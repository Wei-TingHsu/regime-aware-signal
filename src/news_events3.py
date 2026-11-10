"""news_events3.py -- N1 v3 (docs/prereg_news_events.md §5, registered 11 Nov): the founder's two explanations for the null, tested.
  (1) "we missed the source that drives the rebound"  -> wider document set: BLS jobs, CPI, PPI, JOLTS, import/export prices; FOMC statements; speeches by the
      Fed Chair and Vice Chairs; window widened to +1..+10 sessions; every event day back to the BLS archive, not only the GDELT era.
  (2) "the read was aimed wrong"                      -> each document is read ONCE, on its own (no GDELT story needed): what its composition implies for
      equities (-1..+1). Contradiction is then mechanical: a fall followed by an equity-supportive document, or a rise followed by a negative one.
  Every fixed number is a grid axis (cutoff, window, horizon, document family), judged against the best the same grid finds on shuffled outcomes.

  python -m src.news_events3 survey          # v3b, no LLM, no network: which event days have documents in the project's own corpus (by source folder)
  python -m src.news_events3 fetch           # BLS archive index -> releases inside any event window (write-once); Fed speeches (Chair / Vice Chair). Needs BLS_CONTACT
  python -m src.news_events3 cost            # documents unread, tokens and US$ counted on disk
  python -m src.news_events3 read [--max-usd 12]   # one read per document, prompt n1-doc-v3, own cache; stops at the cap
  python -m src.news_events3 grid            # reversal(with contradicting doc) - reversal(without), in points: index x direction x cutoff x window x horizon x family
  python -m src.news_events3 size            # does the SIZE of the reversal line up with the contradiction score (rank correlation, permutation p)
Nothing here writes the register.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

from src.sweep import grid, run, write_md
from src.news_events import _returns
from src.news_events2 import _client, _ask, _html_text, RELS, PROC, DOCS

BLS_KINDS = {"empsit": "Employment Situation", "cpi": "Consumer Price Index", "ppi": "Producer Price Index", "jolts": "Job Openings and Labor Turnover", "ximpim": "Import and Export Price Indexes"}
FAMILY = {"all": None, "bls": tuple(BLS_KINDS), "labour": ("empsit", "jolts"), "prices": ("cpi", "ppi", "ximpim"), "fed": ("fomc", "speech")}
WINDOWS, CUTOFFS, HORIZONS, MAXW = [1, 2, 3, 5, 7, 10], [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7], [1, 3, 5, 10], 10
ERAS = [("1994-01-01", "2003-12-31"), ("2004-01-01", "2008-12-31"), ("2009-01-01", "2014-12-31"), ("2015-01-01", "2019-12-31"), ("2020-01-01", "2021-12-31"), ("2022-01-01", "2026-12-31")]
PV3 = "n1-doc-v3-2026-11-11"; READS3 = RELS / "reads3"; MIN_SIDE = 20; IN_RATE, OUT_RATE = 2.0, 10.0; CHARS = 15000
UA = {"User-Agent": f"regime-aware-signal research ({os.environ.get('BLS_CONTACT', 'no contact set')})"}

SYS_DOC = """You are given the text of one US official document: a BLS statistical release, an FOMC statement, or a speech by a Federal Reserve Chair or Vice Chair.
Read its COMPOSITION, not only the headline: which components or arguments carry it. Judge it on its own; do not use anything you know about what markets did
afterwards. Return STRICT JSON, no preamble:
{"headline_surprise_sign": -1, 0 or +1 (vs the expectation the text states, else vs the recent trend it describes; 0 if neither is clear),
 "drivers": [up to five, each {"component": name, "contribution": "large" | "moderate" | "small", "direction": "+" | "-"}],
 "breadth": 0..1 (how broad-based across components or arguments),
 "implication_equities": -1..+1 (what the composition implies for US equities over the next few sessions: +1 clearly supportive, -1 clearly negative, 0 neutral or mixed),
 "implication_rates": -1..+1 (+1 pushes expected policy rates up, -1 down),
 "evidence": one quoted clause that best supports implication_equities}"""


def _get(url: str) -> bytes | None:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r: return r.read()
    except Exception as e:
        print(f"    {url.rsplit('/', 1)[-1][:60]}: {type(e).__name__}: {str(e)[:70]}"); return None


def _events() -> tuple[pd.DataFrame, pd.DatetimeIndex, pd.DataFrame]:
    ev = pd.read_csv(PROC / "news_events.csv", parse_dates=["date"]); r = _returns(); idx = r.index
    ev["pos"] = idx.searchsorted(ev["date"]); return ev, idx, r


def _window_dates(ev: pd.DataFrame, idx: pd.DatetimeIndex) -> set:
    out = set()
    for p in ev["pos"].unique(): out.update(d.date() for d in idx[p + 1: p + 1 + MAXW])
    return out


# ------------------------------------------------------------------------------------------------ survey (v3b)
def cmd_survey():
    ev, idx, _ = _events(); root = Path("data_provenance/docs"); days = sorted(ev["date"].dt.strftime("%Y%m%d").unique()); rows = []
    if not root.exists(): print(f"{root} not found"); return
    names = {}
    for src in sorted(p for p in root.iterdir() if p.is_dir()): names[src.name] = [f.name for f in src.iterdir() if f.is_file()]
    print("corpus folders: " + ", ".join(f"{k} ({len(v):,})" for k, v in names.items()))
    for d in days:
        row = dict(date=d)
        for k, v in names.items(): row[k] = sum(1 for f in v if d in f)
        rows.append(row)
    df = pd.DataFrame(rows); df.to_csv(PROC / "news_corpus_coverage.csv", index=False); src_cols = [c for c in df.columns if c != "date"]
    any_doc = (df[src_cols].sum(axis=1) > 0); yr = df["date"].str[:4].astype(int)
    print(f"{int(any_doc.sum())} of {len(df)} event days have at least one corpus document dated that day ({any_doc.mean():.0%}); from 2020: {any_doc[yr >= 2020].mean():.0%} of {int((yr >= 2020).sum())}")
    print("event days covered, by source: " + ", ".join(f"{c} {int((df[c] > 0).sum())}" for c in src_cols if (df[c] > 0).any()))
    print("-> processed/news_corpus_coverage.csv  (this decides whether a corpus-based cause read, v3b, is worth registering)")


# ------------------------------------------------------------------------------------------------ fetch
def cmd_fetch():
    ev, idx, _ = _events(); want = _window_dates(ev, idx); RELS.mkdir(parents=True, exist_ok=True); n_new = 0
    if "no contact set" in UA["User-Agent"]: print("BLS_CONTACT is not set -- BLS will refuse. In the terminal: export BLS_CONTACT=your@address"); return
    for kind in BLS_KINDS:
        b = _get(f"https://www.bls.gov/bls/news-release/{kind}.htm")
        dates = sorted(set(re.findall(rf"archives/{kind}_(\d{{8}})\.htm", b.decode("utf-8", "ignore")))) if b else []
        hit = [s for s in dates if pd.Timestamp(year=int(s[4:]), month=int(s[:2]), day=int(s[2:4])).date() in want]
        print(f"  {kind}: {len(dates)} archived releases listed, {len(hit)} inside an event window")
        for s in hit:
            p = RELS / f"{kind}_{s}.txt"
            if p.exists(): continue
            bb = _get(f"https://www.bls.gov/news.release/archives/{kind}_{s}.htm")
            if bb and len(bb) > 3000: p.write_text(_html_text(bb)[:60000]); n_new += 1
            time.sleep(0.15)
    b = _get("https://www.federalreserve.gov/json/ne-speeches.json"); n_sp = 0
    if b:
        try: items = json.loads(b.decode("utf-8-sig"))
        except Exception as e: items = []; print(f"    speeches index unreadable: {type(e).__name__}")
        for it in items:
            if not isinstance(it, dict) or "Chair" not in str(it.get("s", "")): continue
            try: d = pd.to_datetime(str(it.get("d", "")).split(" ")[0]).date()
            except Exception: continue
            if d not in want or not it.get("l"): continue
            p = RELS / f"speech_{d:%m%d%Y}_{re.sub(r'[^a-z0-9]+', '', str(it['l']).rsplit('/', 1)[-1].lower())[:24]}.txt"
            if p.exists(): n_sp += 1; continue
            bb = _get("https://www.federalreserve.gov" + str(it["l"]))
            if bb and len(bb) > 3000: p.write_text(f"SPEAKER: {it.get('s')}. TITLE: {it.get('t')}.\n" + _html_text(bb)[:60000]); n_new += 1; n_sp += 1
            time.sleep(0.15)
    print(f"fetched {n_new} new document(s); Chair / Vice Chair speeches inside a window on disk: {n_sp}; total documents on disk: {len(_inventory())}")


def _inventory() -> pd.DataFrame:
    rows = []
    for p in sorted(RELS.glob("*.txt")):
        m = re.match(r"([a-z]+)_(\d{2})(\d{2})(\d{4})", p.stem)
        if m and (m.group(1) in BLS_KINDS or m.group(1) == "speech"): rows.append(dict(kind=m.group(1), date=pd.Timestamp(year=int(m.group(4)), month=int(m.group(2)), day=int(m.group(3))), path=str(p), stem=p.stem))
    fs = Path("data_provenance/docs/fomc_statement")
    if fs.exists():
        for p in sorted(fs.glob("*.txt")):
            if re.fullmatch(r"\d{8}", p.stem): rows.append(dict(kind="fomc", date=pd.to_datetime(p.stem, format="%Y%m%d"), path=str(p), stem=f"fomc_{p.stem}"))
    return pd.DataFrame(rows)


def _in_window(inv: pd.DataFrame) -> pd.DataFrame:
    ev, idx, _ = _events(); want = _window_dates(ev, idx); return inv[inv["date"].dt.date.isin(want)].reset_index(drop=True) if len(inv) else inv


def cmd_cost():
    inv = _in_window(_inventory()); todo = [r for _, r in inv.iterrows() if not (READS3 / f"{r.stem}__{PV3}.json").exists()]
    tok = sum(min(len(Path(r.path).read_text()), CHARS) / 4 + 400 for r in todo); usd = tok / 1e6 * IN_RATE + len(todo) * 300 / 1e6 * OUT_RATE
    print(f"{len(inv)} documents inside an event window ({inv['kind'].value_counts().to_dict() if len(inv) else {}}); {len(todo)} unread under {PV3}; ~{tok:,.0f} input tokens, about US${usd:.2f}. Counted on disk.")


def cmd_read(max_usd: float):
    client = _client(); inv = _in_window(_inventory()); tin = tout = 0; n = 0
    todo = [r for _, r in inv.iterrows() if not (READS3 / f"{r.stem}__{PV3}.json").exists()]; print(f"document read: {len(todo)} of {len(inv)} unread under {PV3}; cap US${max_usd:.2f}")
    for r in todo:
        d, a, b = _ask(client, SYS_DOC, f"DOCUMENT ({r.kind}, {r.date:%Y-%m-%d}):\n{Path(r.path).read_text()[:CHARS]}", r.stem, READS3, PV3); tin += a; tout += b; n += 1
        usd = tin / 1e6 * IN_RATE + tout / 1e6 * OUT_RATE
        if n % 50 == 0: print(f"  {n}/{len(todo)}  ~US${usd:.2f}")
        if usd >= max_usd: print(f"  cap reached at {n} reads (~US${usd:.2f}); rerun to continue with a higher --max-usd"); break
        time.sleep(0.1)
    print(f"done: {n} read(s), ~US${tin / 1e6 * IN_RATE + tout / 1e6 * OUT_RATE:.2f}"); _reads().to_csv(PROC / "news_doc_reads_v3.csv", index=False)


def _reads() -> pd.DataFrame:
    inv = _inventory(); rows = []
    for _, r in inv.iterrows():
        f = READS3 / f"{r.stem}__{PV3}.json"
        if not f.exists(): continue
        d = json.loads(f.read_text())
        try: rows.append(dict(kind=r.kind, date=r.date, stem=r.stem, implication=float(d.get("implication_equities")), rates=float(d.get("implication_rates", 0) or 0), surprise=float(d.get("headline_surprise_sign", 0) or 0), breadth=float(d.get("breadth", 0) or 0)))
        except (TypeError, ValueError): continue
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------------------------ the panel: one row per index-event
def _panel() -> tuple[pd.DataFrame, dict]:
    ev, idx, r = _events(); rd = _reads()
    if rd.empty: raise SystemExit("no v3 document reads on disk -- run `read` first")
    rd["pos"] = idx.searchsorted(rd["date"]); n = len(ev); F = {}
    for h in HORIZONS:
        F[h] = np.array([float(r[c].iloc[p + 1: p + 1 + h].sum()) if p + 1 + h <= len(r) else np.nan for c, p in zip(ev["column"], ev["pos"])])
    C = {}
    for fam, kinds in FAMILY.items():
        sub = rd if kinds is None else rd[rd["kind"].isin(kinds)]; dp = sub["pos"].to_numpy(); imp = sub["implication"].to_numpy()
        for w in WINDOWS:
            v = np.full(n, np.nan)
            for i, (p, sg) in enumerate(zip(ev["pos"].to_numpy(), ev["sign"].to_numpy())):
                m = (dp > p) & (dp <= p + w)
                if m.any(): v[i] = float(np.max(-sg * imp[m]))          # a fall then a supportive document, or a rise then a negative one, scores positive
            C[(fam, w)] = v
    return ev, dict(F=F, C=C, index=ev["index"].to_numpy(), sign=ev["sign"].to_numpy(), date=ev["date"].to_numpy())


def _gap(y, sg, with_mask, grp):
    rev = (np.sign(y) == -sg) & np.isfinite(y); ok = grp & np.isfinite(y); a, b = ok & with_mask, ok & ~with_mask
    if a.sum() < MIN_SIDE or b.sum() < MIN_SIDE: return np.nan, int(a.sum()), int(b.sum())
    return float((rev[a].mean() - rev[b].mean()) * 100), int(a.sum()), int(b.sum())


def cmd_grid():
    ev, P = _panel(); idxs = sorted(set(P["index"])); sws = []; L = ["# N1 v3 — does a contradicting official document in the window raise the reversal rate?", "",
        "Statistic: reversal rate of events WITH a contradicting document in the window minus the rate WITHOUT, in percentage points (each side n ≥ 20). 'Contradicting' = max over documents in the window of (−event sign × the document's equity implication) ≥ cutoff. Null: forward outcomes shuffled among the same index-and-direction events, best cell of the whole grid, 300 draws.", ""]
    def stat(dd, c):
        grp = (P["index"] == c["index"]) & (P["sign"] == c["sign"]); cv = P["C"][(c["family"], c["window"])]; g, na, nb = _gap(dd[c["h"]], c["sign"], np.nan_to_num(cv, nan=-9) >= c["cutoff"], grp); return g, na
    def null_gen(dd, rg):
        out = {h: v.copy() for h, v in dd.items()}
        for ix in idxs:
            for sg in (-1, 1):
                m = np.where((P["index"] == ix) & (P["sign"] == sg))[0]; pm = rg.permutation(m)
                for h in out: out[h][m] = dd[h][pm]
        return out
    for ix in idxs:
        for sg in (-1, 1):
            name = f"{ix} {'fall' if sg < 0 else 'rise'}"; cells = grid(index=[ix], sign=[sg], family=list(FAMILY), cutoff=CUTOFFS, window=WINDOWS, h=HORIZONS)
            sw = run(cells, stat, P["F"], null_gen, n_null=300, seed=sum(map(ord, name)) % 1000, label=f"N1 v3 {name}: reversal gap, with − without", meta=dict(tag=name.replace(" ", "_"))); sws.append(sw)
            valid = int(np.isfinite(sw.surface["stat"]).sum())
            if not valid: print(f"{name}: no cell reaches {MIN_SIDE} events on both sides"); L += [f"## {name}", "", "No cell reaches the minimum on both sides.", ""]; continue
            b = sw.best; grp = (P["index"] == ix) & (P["sign"] == sg); cv = np.nan_to_num(P["C"][(b["family"], b["window"])], nan=-9) >= b["cutoff"]; g, na, nb = _gap(P["F"][b["h"]], sg, cv, grp)
            eras = []
            for a, z in ERAS:
                em = grp & (P["date"] >= np.datetime64(a)) & (P["date"] <= np.datetime64(z)); y = P["F"][b["h"]]; ok = em & np.isfinite(y); w_, wo = ok & cv, ok & ~cv
                if w_.sum() >= 5 and wo.sum() >= 5: rev = np.sign(y) == -sg; eras.append(f"{a[:4]}–{z[:4]}: {(rev[w_].mean() - rev[wo].mean()) * 100:+.0f} (n {int(w_.sum())}/{int(wo.sum())})")
            print(f"{name}: {valid} valid cells; best {b} gap {sw.best_stat:+.1f} pts (n with {na}, without {nb}) vs null q95 {sw.q95:+.1f}, p_family {sw.p_family:.3f}; survivors {len(sw.survivors)}; by era: {'; '.join(eras) or 'too few per era'}")
            L += [f"## {name}", "", f"{valid} valid cells. Best cell `{b}`: gap **{sw.best_stat:+.1f} points** (n with {na}, without {nb}); best-of-grid null 95th percentile {sw.q95:+.1f}; **p_family {sw.p_family:.3f}**; survivors {len(sw.survivors)}.", f"Best cell by era (gap, n with/without): {'; '.join(eras) or 'too few events per era'}.", ""]
            write_md(sw, DOCS / f"news_events_v3_grid_{name.replace(' ', '_')}.md", fmt="{:+.1f}")
    (DOCS / "news_events_v3_grid.md").write_text("\n".join(L) + "\n"); (DOCS / "news_events_v3_grid.json").write_text(json.dumps([s.to_json() for s in sws], indent=1, default=float)); print("-> docs/news_events_v3_grid.md")


def _spearman(a, b):
    ra, rb = pd.Series(a).rank().to_numpy(), pd.Series(b).rank().to_numpy(); return float(np.corrcoef(ra, rb)[0, 1]) if len(a) > 2 and ra.std() > 0 and rb.std() > 0 else np.nan


def cmd_size():
    ev, P = _panel(); rng = np.random.default_rng(0); rows = []
    for ix in sorted(set(P["index"])):
        for sg in (-1, 1):
            grp = (P["index"] == ix) & (P["sign"] == sg)
            for w in (3, 5, 10):
                cv = P["C"][("all", w)]
                for h in HORIZONS:
                    y = -sg * P["F"][h]; ok = grp & np.isfinite(y) & np.isfinite(cv)
                    if ok.sum() < 30: continue
                    rho = _spearman(cv[ok], y[ok]); null = np.array([_spearman(cv[ok], rng.permutation(y[ok])) for _ in range(1000)]); p = float((np.abs(null) >= abs(rho)).mean())
                    big = y[ok] >= np.quantile(y[ok], 0.75); rows.append(dict(index=ix, direction="fall" if sg < 0 else "rise", window=w, h=h, n=int(ok.sum()), rank_corr=rho, p=p, contra_in_big_reversals=float(cv[ok][big].mean()), contra_in_rest=float(cv[ok][~big].mean())))
    tab = pd.DataFrame(rows)
    if tab.empty: print("no cell reaches n >= 30"); return
    print(tab.to_string(index=False, float_format=lambda v: f"{v:+.3f}")); print(f"cells with p < 0.05: {int((tab.p < 0.05).sum())} of {len(tab)} (about {len(tab) * 0.05:.1f} expected by chance)")
    L = ["# N1 v3 — does the SIZE of the reversal line up with the contradiction score?", "", "Reversal return = −event sign × the next h sessions' return (positive = prices went back). rank_corr = Spearman correlation with the strongest contradiction score in the window, among events that had a document in the window; p from 1,000 shuffles. The last two columns: mean contradiction score in the largest quarter of reversals vs the rest.", "",
         "| index | direction | window | h | n | rank corr | p | contra, big reversals | contra, rest |", "|---|---|---|---|---|---|---|---|---|"]
    for _, r_ in tab.iterrows(): L.append(f"| {r_['index']} | {r_['direction']} | {r_['window']} | {r_['h']} | {r_['n']} | {r_['rank_corr']:+.2f} | {r_['p']:.3f} | {r_['contra_in_big_reversals']:+.2f} | {r_['contra_in_rest']:+.2f} |")
    L += ["", f"Cells with p < 0.05: {int((tab.p < 0.05).sum())} of {len(tab)}; about {len(tab) * 0.05:.1f} expected by chance."]
    (DOCS / "news_events_v3_size.md").write_text("\n".join(L) + "\n"); tab.to_json(DOCS / "news_events_v3_size.json", orient="records", indent=1); print("-> docs/news_events_v3_size.md")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["survey", "fetch", "cost", "read", "grid", "size"]); ap.add_argument("--max-usd", type=float, default=12.0); a = ap.parse_args(); DOCS.mkdir(exist_ok=True)
    {"survey": cmd_survey, "fetch": cmd_fetch, "cost": cmd_cost, "read": lambda: cmd_read(a.max_usd), "grid": cmd_grid, "size": cmd_size}[a.cmd]()
