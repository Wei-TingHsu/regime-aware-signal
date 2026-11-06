"""news_events2.py -- N1 stage 2 (docs/prereg_news_events.md §2): the cause read, the release-composition read, the tables, the learner.

  python -m src.news_events2 read [--limit N]        # S1: each event-day digest -> cause class, confidence, reason (LLM; own cache data_provenance/news_reads/,
                                                     #     prompt version n1-cause-v1; never pooled with the corpus reads); cost printed as it goes
  python -m src.news_events2 releases                # S2a: BLS Employment Situation and CPI releases in sessions +1..+5 after each event, fetched from the BLS
                                                     #     archive (bls.gov/news.release/archives/{empsit|cpi}_MMDDYYYY.htm) write-once; FOMC statements from the corpus
  python -m src.news_events2 read_releases           # S2b: each release in a window -> surprise sign, driving components, contradiction score vs the event's cause
  python -m src.news_events2 tables                  # S3: reversal rate by index x direction x cause class, with / without a contradicting release; H-table standard
  python -m src.news_events2 learn                   # S4: walk-forward ridge vs the plain rule 'buy the session after a >= 4% fall'; best-of-search null
  python -m src.news_events2 all
Nothing here writes the register. Needs ANTHROPIC_API_KEY for the two read steps.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.request
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from src.sweep import grid, run, write_md
from src.news_events import DIG, _returns, UA

PROC, DOCS = Path("processed"), Path("docs")
READS = Path("data_provenance/news_reads"); RELS = Path("data_provenance/releases"); PV = "n1-cause-v1-2026-11-06"; PV_REL = "n1-release-v1-2026-11-06"
MODEL = "claude-sonnet-5"; COST = 0.0010; MIN_N = 30
CLASSES = ["macro_release", "central_bank", "earnings_guidance", "geopolitics", "election_regulation", "credit_liquidity", "health", "no_identifiable_news_positioning"]
FATAL = ("credit balance is too low", "invalid x-api-key", "authentication_error", "permission_error", "insufficient_quota")

SYS_CAUSE = f"""You are given a one-page digest of what the GDELT event database recorded on one trading day (actors, event types, tone, source-URL slugs) and the
market moves of that session. Classify the most likely CAUSE of the market move. Use only the digest; do not use anything you know about what happened on
that date from memory -- if the digest does not support a cause, say so with the class no_identifiable_news_positioning. Return STRICT JSON, no preamble:
{{"cause": one of {CLASSES}, "confidence": 0..1 (how clearly the digest supports it), "secondary": one of the classes or null, "reason": one sentence quoting the digest items that support the class,
 "story": one sentence stating the narrative the market would be trading (e.g. 'growth fears', 'rate-hike fears', 'AI demand doubts'), "story_direction_for_equities": -1 or +1}}"""

SYS_REL = """You are given the text of a US statistical release (BLS Employment Situation or CPI) and the cause story of a large market move 1-5 sessions earlier.
Read the COMPOSITION of the release, not only the headline. Return STRICT JSON, no preamble:
{"headline_surprise_sign": -1, 0 or +1 (the release vs the stated expectation if the text gives one, else vs the recent trend it describes),
 "drivers": [up to five components that drove the headline, each {"component": name, "contribution": "large" | "moderate" | "small", "direction": "+" | "-"}],
 "breadth": 0..1 (how broad-based the change is across components),
 "contradiction": -1..+1 (-1 = the composition CONFIRMS the market's story, +1 = it CONTRADICTS it, 0 = unrelated),
 "evidence": one quoted clause supporting the contradiction score}"""


def is_fatal(e) -> bool:
    s = f"{type(e).__name__}: {e}".lower(); return any(m in s for m in FATAL)


def _client():
    if not os.environ.get("ANTHROPIC_API_KEY"): raise SystemExit("set ANTHROPIC_API_KEY")
    from anthropic import Anthropic; return Anthropic()


def _parse(t: str) -> dict:
    t = re.sub(r"^```(?:json)?|```$", "", t.strip(), flags=re.M).strip(); i, j = t.find("{"), t.rfind("}")
    if i != -1 and j > i: t = t[i:j + 1]
    try: return json.loads(t)
    except json.JSONDecodeError: return json.loads(t, strict=False)


def _ask(client, system: str, body: str, stem: str, folder: Path, pv: str) -> tuple[dict | None, int, int]:
    out = folder / f"{stem}__{pv}.json"
    if out.exists(): return json.loads(out.read_text()), 0, 0
    try:
        r = client.messages.create(model=MODEL, max_tokens=700, system=system, messages=[{"role": "user", "content": body}])
        t = "".join(b.text for b in r.content if b.type == "text")
        try: d = _parse(t)
        except json.JSONDecodeError:
            r2 = client.messages.create(model=MODEL, max_tokens=700, system=system, messages=[{"role": "user", "content": body}, {"role": "assistant", "content": t or "(empty)"}, {"role": "user", "content": "That was not valid JSON. Reply with the JSON object only."}])
            t2 = "".join(b.text for b in r2.content if b.type == "text")
            try: d = _parse(t2)
            except json.JSONDecodeError: (folder / f"{stem}__{pv}.failed.txt").write_text(t + "\n----\n" + t2); return None, r.usage.input_tokens + r2.usage.input_tokens, r.usage.output_tokens + r2.usage.output_tokens
        d["_model"] = MODEL; d["_prompt_version"] = pv; d["_read_at"] = datetime.now().strftime("%Y-%m-%d %H:%M"); tmp = out.with_suffix(".tmp"); tmp.write_text(json.dumps(d, indent=1)); os.replace(tmp, out)
        return d, r.usage.input_tokens, r.usage.output_tokens
    except Exception as e:
        if is_fatal(e): print("!" * 60 + f"\nFATAL -- {type(e).__name__}: {e}\nnothing retried; cached reads kept\n" + "!" * 60); raise SystemExit(1)
        print(f"    {stem}: {type(e).__name__}: {str(e)[:100]}"); return None, 0, 0


# ------------------------------------------------------------------------------------------------ S1
def cmd_read(limit: int | None):
    client = _client(); READS.mkdir(parents=True, exist_ok=True); files = sorted(DIG.glob("*.txt"))
    todo = [p for p in files if not (READS / f"{p.stem}__{PV}.json").exists()]; todo = todo[-limit:] if limit else todo
    print(f"cause read: {len(todo)} of {len(files)} digests unread under {PV}"); tin = tout = 0
    for k, p in enumerate(todo):
        d, a, b = _ask(client, SYS_CAUSE, p.read_text(), p.stem, READS, PV); tin += a; tout += b
        if (k + 1) % 25 == 0: print(f"  {k + 1}/{len(todo)}  ~US${tin / 1e6 * 2 + tout / 1e6 * 10:.2f}")
        time.sleep(0.2)
    print(f"done: ~US${tin / 1e6 * 2 + tout / 1e6 * 10:.2f}")
    rows = [dict(date=f.name[:8], **{k: v for k, v in json.loads(f.read_text()).items() if not k.startswith("_")}) for f in sorted(READS.glob(f"*__{PV}.json"))]
    df = pd.DataFrame(rows); df.to_csv(PROC / "news_causes.csv", index=False)
    if len(df): print(df["cause"].value_counts().to_string()); print(f"mean confidence {df['confidence'].astype(float).mean():.2f}; share no-identifiable-news {(df['cause'] == 'no_identifiable_news_positioning').mean():.0%}")


# ------------------------------------------------------------------------------------------------ S2a
def _get(url: str) -> bytes | None:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r: return r.read()
    except Exception: return None


def _html_text(b: bytes) -> str:
    t = b.decode("utf-8", "ignore"); t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S); t = re.sub(r"<[^>]+>", " ", t); t = re.sub(r"&nbsp;|&#160;", " ", t); return re.sub(r"\s+", " ", t).strip()


def cmd_releases():
    ev = pd.read_csv(PROC / "news_events.csv", parse_dates=["date"]); r = _returns(); idx = r.index; RELS.mkdir(parents=True, exist_ok=True); rows = []; fetched = 0
    days = sorted(ev["date"].unique())
    for d in days:
        pos = idx.searchsorted(pd.Timestamp(d)); window = idx[pos + 1: pos + 6]
        for w in window:
            for kind in ("empsit", "cpi"):
                stem = f"{kind}_{w:%m%d%Y}"; p = RELS / f"{stem}.txt"
                if not p.exists():
                    b = _get(f"https://www.bls.gov/news.release/archives/{stem}.htm")
                    if b and len(b) > 5000 and ("Employment Situation" in b.decode("utf-8", "ignore") or "Consumer Price Index" in b.decode("utf-8", "ignore")):
                        p.write_text(_html_text(b)[:60000]); fetched += 1
                    else: continue
                rows.append(dict(event_date=pd.Timestamp(d).date(), release_date=w.date(), kind=kind, sessions_after=int(idx.get_loc(w) - pos), file=str(p)))
            fs = Path("data_provenance/docs/fomc_statement") / f"{w:%Y%m%d}.txt"
            if fs.exists(): rows.append(dict(event_date=pd.Timestamp(d).date(), release_date=w.date(), kind="fomc", sessions_after=int(idx.get_loc(w) - pos), file=str(fs)))
        time.sleep(0.05)
    df = pd.DataFrame(rows); df.to_csv(PROC / "news_releases_in_window.csv", index=False)
    print(f"{fetched} release(s) fetched; {len(df)} event-release pairs in the +1..+5 window ({df['kind'].value_counts().to_dict() if len(df) else {}}); "
          f"{ev['date'].nunique() - df['event_date'].nunique() if len(df) else ev['date'].nunique()} event days with no release in the window")


# ------------------------------------------------------------------------------------------------ S2b
def cmd_read_releases():
    client = _client(); pairs = pd.read_csv(PROC / "news_releases_in_window.csv"); causes = pd.read_csv(PROC / "news_causes.csv", dtype={"date": str}).set_index("date")
    RELS.mkdir(parents=True, exist_ok=True); rows = []; tin = tout = 0
    for _, p in pairs.iterrows():
        ed = pd.Timestamp(p.event_date).strftime("%Y%m%d"); c = causes.loc[ed] if ed in causes.index else None
        story = (f"{c['story']} (equities {'down' if int(c['story_direction_for_equities']) < 0 else 'up'}; cause {c['cause']})" if c is not None else "unknown")
        text = Path(p.file).read_text()[:40000]; stem = f"{Path(p.file).stem}__for_{ed}"
        d, a, b = _ask(client, SYS_REL, f"MARKET MOVE {p.event_date}, STORY: {story}\n\nRELEASE ({p.kind}, {p.release_date}):\n{text}", stem, RELS / "reads", PV_REL); tin += a; tout += b
        if d: rows.append(dict(event_date=p.event_date, release_date=p.release_date, kind=p.kind, sessions_after=p.sessions_after, **{k: v for k, v in d.items() if not k.startswith("_") and k != "drivers"}, drivers=json.dumps(d.get("drivers"))))
    pd.DataFrame(rows).to_csv(PROC / "news_release_reads.csv", index=False); print(f"{len(rows)} release reads, ~US${tin / 1e6 * 2 + tout / 1e6 * 10:.2f} -> processed/news_release_reads.csv")


# ------------------------------------------------------------------------------------------------ S3 / S4
def _frame() -> pd.DataFrame:
    ev = pd.read_csv(PROC / "news_events.csv", parse_dates=["date"]); causes = pd.read_csv(PROC / "news_causes.csv", dtype={"date": str}); causes["date"] = pd.to_datetime(causes["date"], format="%Y%m%d")
    ev = ev.merge(causes[["date", "cause", "confidence", "story_direction_for_equities"]], on="date", how="left"); r = _returns(); idx = r.index
    rel = pd.read_csv(PROC / "news_release_reads.csv", parse_dates=["event_date"]) if (PROC / "news_release_reads.csv").exists() else None
    for h in (1, 3, 5):
        f = []
        for _, e in ev.iterrows():
            col = e["column"]; pos = idx.searchsorted(e["date"]); s = r[col]; f.append(float(s.iloc[pos + 1: pos + 1 + h].sum()) if pos + 1 + h <= len(s) else np.nan)
        ev[f"f{h}"] = f
    ev["contra"] = 0.0
    if rel is not None and len(rel):
        m = rel.groupby("event_date")["contradiction"].max(); ev["contra"] = ev["date"].map(m).fillna(0.0).astype(float); ev["has_release"] = ev["date"].isin(rel["event_date"])
    else: ev["has_release"] = False
    ev["cause"] = ev["cause"].fillna("unread"); return ev


def cmd_tables():
    ev = _frame(); r = _returns(); rows = []
    for (ix, sg), g in ev.groupby(["index", "sign"]):
        col = g["column"].iloc[0]; s = r[col].dropna()
        for h in (1, 3, 5):
            base_series = s.rolling(h).sum().shift(-h).dropna(); base = float((np.sign(base_series) == -sg).mean())
            for cls, gg in list(g.groupby("cause")) + [("ALL", g)] + [("with contradicting release", g[g.contra > 0.3]), ("without", g[~(g.contra > 0.3)])]:
                v = gg[f"f{h}"].dropna(); n = len(v)
                if n == 0: continue
                rev = float((np.sign(v) == -sg).mean()); gap = (rev - base) * 100
                if n >= MIN_N:
                    rng = np.random.default_rng(0); pool = base_series.to_numpy(); null = np.array([(np.sign(rng.choice(pool, n, replace=False)) == -sg).mean() for _ in range(1000)]); p = float((np.abs(null - base) >= abs(rev - base)).mean())
                    verdict = "PASS" if (abs(gap) >= 10 and p < 0.05) else "FAIL"
                else: p, verdict = np.nan, "measured (n < 30)"
                rows.append(dict(index=ix, direction="fall" if sg < 0 else "rise", h=h, cause=cls, n=n, reversal=rev, base=base, gap=gap, p=p, verdict=verdict))
    tab = pd.DataFrame(rows); out = DOCS / "news_events_tables.md"
    L = ["# N1 — reversal after ≥ 4% moves, by cause class", "", "Reversal = the next h sessions' return has the opposite sign to the event; base = how often that sign occurs over any h sessions. H-table standard: n ≥ 30, |gap| ≥ 10 points, random-date p < 0.05.", ""]
    for (ix, dr), g in tab.groupby(["index", "direction"]):
        L += [f"## {ix} — {dr}", "", "| cause | h | n | reversal | base | gap | p | verdict |", "|---|---|---|---|---|---|---|---|"]
        for _, r_ in g.sort_values(["cause", "h"]).iterrows(): L.append(f"| {r_['cause']} | {r_['h']} | {r_['n']} | {r_['reversal']:.0%} | {r_['base']:.0%} | {r_['gap']:+.0f} | {('%.3f' % r_['p']) if np.isfinite(r_['p']) else '·'} | {r_['verdict']} |")
        L.append("")
    out.write_text("\n".join(L) + "\n"); out.with_suffix(".json").write_text(tab.to_json(orient="records", indent=1)); print(tab[(tab.cause == "ALL")].to_string(index=False)); print(f"-> {out}")


def cmd_learn():
    ev = _frame().dropna(subset=["f5"]).sort_values("date").reset_index(drop=True); r = _returns()
    vix = None
    try:
        m = pd.read_parquet(PROC / "macro_panel.parquet"); m.index = pd.to_datetime(m.index); vix = m["VIXCLS"].reindex(ev["date"]).ffill().to_numpy() if "VIXCLS" in m.columns else None
    except Exception: pass
    X = pd.get_dummies(ev["cause"].astype(str)).astype(float); X["move"] = ev["move"]; X["sign"] = ev["sign"]; X["conf"] = ev["confidence"].fillna(0); X["contra"] = ev["contra"]; X["has_rel"] = ev["has_release"].astype(float)
    trend = [float(r[c].iloc[max(0, r.index.searchsorted(d) - 20): r.index.searchsorted(d)].sum()) for c, d in zip(ev["column"], ev["date"])]; X["trend20"] = trend
    if vix is not None: X["vix"] = np.nan_to_num(vix, nan=np.nanmean(vix))
    X["const"] = 1.0; Xn = X.to_numpy(float); n = len(ev)
    def stat(dd, c):
        y = np.asarray(dd["y"]); pnl = []
        for s in range(max(60, int(n * 0.4)), n, 25):
            tr = np.arange(max(0, s - c["train"]), s); te = np.arange(s, min(s + 25, n))
            b = np.linalg.solve(Xn[tr].T @ Xn[tr] + c["ridge"] * np.eye(Xn.shape[1]), Xn[tr].T @ y[tr]); pred = Xn[te] @ b; pnl.extend((np.sign(pred) * y[te] - COST).tolist())
        pnl = np.array(pnl)
        if len(pnl) < 40 or pnl.std(ddof=1) == 0: return np.nan, len(pnl)
        return float(pnl.mean() / pnl.std(ddof=1) * np.sqrt(252 / c["h"])), len(pnl)
    sws = []
    for h in (1, 3, 5):
        y = ev[f"f{h}"].to_numpy(float); cells = grid(train=[100, 200, 400], ridge=[1.0, 10.0, 100.0], h=[h])
        sw = run(cells, stat, dict(y=y), lambda dd, rg: dict(y=np.asarray(dd["y"])[rg.permutation(len(dd["y"]))]), n_null=200, seed=h, label=f"N1 learner → {h}-session return after the event", meta=dict(tag=f"h{h}", rows="train", cols="ridge")); sws.append(sw)
        plain = ev[ev.sign < 0][f"f{h}"].to_numpy(float) - COST; plain_sh = float(plain.mean() / plain.std(ddof=1) * np.sqrt(252 / h)) if len(plain) > 10 else np.nan
        print(f"h={h}: learner best {sw.best} Sharpe {sw.best_stat:+.2f} vs null q95 {sw.q95:+.2f}, p_family {sw.p_family:.3f}; plain 'buy after a fall' Sharpe {plain_sh:+.2f} (n {len(plain)})")
        write_md(sw, DOCS / f"news_events_learn_h{h}.md", axis_rows="train", axis_cols="ridge", fmt="{:+.2f}", note=f"Plain rule 'long the session after a ≥ 4% fall', {h} sessions: Sharpe {plain_sh:+.2f} on n {len(plain)}.")
    (DOCS / "news_events_learn.json").write_text(json.dumps([s.to_json() for s in sws], indent=1, default=float))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["read", "releases", "read_releases", "tables", "learn", "all"]); ap.add_argument("--limit", type=int); a = ap.parse_args(); DOCS.mkdir(exist_ok=True)
    for c in (["read", "releases", "read_releases", "tables", "learn"] if a.cmd == "all" else [a.cmd]):
        {"read": lambda: cmd_read(a.limit), "releases": cmd_releases, "read_releases": cmd_read_releases, "tables": cmd_tables, "learn": cmd_learn}[c]()
