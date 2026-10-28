"""T-K3 -- the few-shot chair: style, not reaction.

Every FOMC statement on disk is read on a fixed rubric (the model scores HOW the text is written and WHAT it emphasises;
no market data enters, and the model is told to use nothing it knows about what happened afterwards). The current chair's
n statements are compared with the previous chair's last 8 by energy distance on the standardised rubric, and the p-value
is EXACT: every one of the C(n+8, n) ways of splitting the pooled n+8 statements into 'current' and 'previous' is enumerated.
docs/prereg_liquidity_and_chair.md section 3 (T-K3, prior #79) and the 2026-10-28 amendment (acceptance check on past
transitions, prior #82).

  python -m src.chair_style cost          # what the rubric read costs, counted on disk, before a cent is spent
  python -m src.chair_style selftest      # synthetic: a planted shift is detected; no shift -> nominal rejection
  python -m src.chair_style read          # rubric read of every statement; own cache folder, own prompt version; --limit N
  python -m src.chair_style acceptance    # Yellen->Powell and Bernanke->Yellen, last 8 vs first 8, exact permutation
  python -m src.chair_style test          # the current chair vs the previous chair's last 8
  python -m src.chair_style record        # write the verdicts into the register, the pre-registration and the state record

The read never writes under data_provenance/doc_reads/ -- that folder is the v1 corpus and its hash. Rubric reads live in
data_provenance/doc_reads_style/ and are never pooled with v1 reads.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from itertools import combinations
from math import comb
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.chair_power import CHAIRS, chair_of, _bump_tally, _replace_line  # the same chair boundaries as T-K0..K2

DOCS = Path("data_provenance/docs/fomc_statement")
READS = Path("data_provenance/doc_reads_style")          # NOT doc_reads/: the v1 corpus hash must not move
PROC, DOCSDIR = Path("processed"), Path("docs")
PROMPT_VERSION = "style-v1-2026-10-28"
MODEL_DEFAULT = "claude-sonnet-5"                        # the corpus model; one read condition for the whole rubric corpus
LAST_K = 8                                               # the previous chair's last 8 (registered)
DIMS = ["hawk_dove", "guidance_strength", "balance_sheet", "inflation_vs_labour",
        "hedging_density", "dissents", "length_change", "novelty_vs_prev"]      # the eight registered dimensions
LLM_DIMS = ["hawk_dove", "guidance_strength", "balance_sheet", "balance_sheet_stance",
            "inflation_vs_labour", "hedging_density", "dissents", "novelty_vs_prev"]
IN_RATE, OUT_RATE, SYSTEM_TOK, OUT_TOK = 2.0, 10.0, 520, 220     # $/M in, $/M out (as corpus_status assumes), system prompt, reply
FATAL_MARKERS = ("credit balance is too low", "invalid x-api-key", "authentication_error", "permission_error", "insufficient_quota")

SYSTEM = """You read ONE Federal Reserve FOMC statement and score how it is written and what it emphasises. You are measuring
the text, not the economy: do not predict markets, and use nothing you know about what happened after the statement.
The PREVIOUS statement is given only so that you can judge what is new. Return STRICT JSON, no preamble, no markdown
fences, exactly these keys:
{"hawk_dove": -1..+1 (hawkish positive: the decision and the guidance read together),
 "guidance_strength": 0..1 (how committed the forward guidance is: 0 = none or purely data-dependent,
                            1 = a calendar- or threshold-based commitment),
 "balance_sheet": 0..1 (how much of the statement's substance concerns the balance sheet: purchases, reinvestment,
                        runoff, caps, reserves),
 "balance_sheet_stance": -1..+1 (-1 contracting, 0 holding or silent, +1 expanding),
 "inflation_vs_labour": -1..+1 (-1 the labour market dominates the discussion, +1 inflation dominates),
 "hedging_density": 0..1 (the share of sentences that are conditional, two-sided or qualified),
 "dissents": integer (the number of voters recorded as voting against; 0 if none),
 "novelty_vs_prev": 0..1 (how much of the substance is new relative to the previous statement; 0 = identical),
 "evidence": {"hedging": one quoted clause or "", "balance_sheet": one quoted clause or "",
              "novelty": one quoted clause or ""}}
Score only what is in the text. If a field cannot be judged from the text, use 0 and say so in evidence."""


# ----------------------------------------------------------------------------------------------- the texts and the cache
def statements() -> list[tuple[Path, pd.Timestamp]]:
    out = []
    for p in sorted(DOCS.glob("*.txt")):
        m = re.match(r"(\d{8})", p.stem)
        if m:
            out.append((p, pd.to_datetime(m.group(1), format="%Y%m%d")))
    return out


def cache_path(stem: str) -> Path:
    return READS / f"fomc_statement__{stem}__{PROMPT_VERSION}.json"


def dissents_from_text(t: str) -> int | None:
    """Two formats: 'Voting against the action were A; and B.' (to 2026) and 'by a 9 - 3 vote' (the 2026 preamble)."""
    m = re.search(r"by a\s+(\d+)\s*[–\-]\s*(\d+)\s+vote", t)
    if m:
        return int(m.group(2))
    m = re.search(r"Voting against (?:this|the) action (?:was|were)\s+([^.]*)\.", t)
    if not m:
        return 0 if re.search(r"Voting for (?:this|the) (?:FOMC )?(?:monetary policy )?action", t) else None
    names = re.split(r";\s*|,\s*and\s+|\s+and\s+", m.group(1))
    return max(1, len([x for x in names if re.search(r"[A-Z][a-z]+", x)]))


def is_fatal(exc) -> bool:
    s = f"{type(exc).__name__}: {exc}".lower()
    return any(m in s for m in FATAL_MARKERS)


def tokens_per_word() -> float:
    """Calibrate on the v1 reads of the same texts where the API's own token count is on file; else the measured corpus ratio."""
    try:
        from src.corpus_status import MEASURED_TOKENS_PER_DOC as T
        s = T.get("fomc_statement") if isinstance(T, dict) else None
        if s:
            words = np.median([len(p.read_text().split()) for p, _ in statements()])
            r = float(s) / float(words)
            if 0.8 < r < 4:
                return r
    except Exception:
        pass
    return 1.45


def cost() -> dict:
    st = statements()
    r = tokens_per_word()
    words = [len(p.read_text().split()) for p, _ in st]
    prev = [0] + words[:-1]
    unread = [i for i, (p, _) in enumerate(st) if not cache_path(p.stem).exists()]
    tin = sum((words[i] + prev[i]) * r + SYSTEM_TOK for i in unread)
    tout = len(unread) * OUT_TOK
    usd = tin / 1e6 * IN_RATE + tout / 1e6 * OUT_RATE
    print(f"statements on disk {len(st)}, unread under {PROMPT_VERSION}: {len(unread)}")
    print(f"tokens/word {r:.2f} (calibrated); input ~{tin:,.0f} tok, output ~{tout:,.0f} tok -> about US${usd:.2f} "
          f"at {IN_RATE}/{OUT_RATE} $/M. A number counted on disk, not a corpus average.")
    return dict(n=len(st), unread=len(unread), usd=usd)


# ----------------------------------------------------------------------------------------------- the read
def call(client, model, text, prev):
    body = f"PREVIOUS STATEMENT:\n{prev}\n\nSTATEMENT:\n{text}" if prev else f"STATEMENT:\n{text}"
    r = client.messages.create(model=model, max_tokens=900, system=SYSTEM, messages=[{"role": "user", "content": body}])
    t = "".join(b.text for b in r.content if b.type == "text").strip()
    t = re.sub(r"^```(?:json)?|```$", "", t, flags=re.M).strip()
    try:
        return json.loads(t), r.usage.input_tokens, r.usage.output_tokens
    except json.JSONDecodeError:
        i, j = t.find("{"), t.rfind("}")
        if i != -1 and j > i:
            return json.loads(t[i:j + 1]), r.usage.input_tokens, r.usage.output_tokens
        raise


def read(limit: int | None, model: str, sleep: float):
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("set ANTHROPIC_API_KEY")
    from anthropic import Anthropic
    client = Anthropic()
    READS.mkdir(parents=True, exist_ok=True)
    st = statements()
    texts = [p.read_text() for p, _ in st]
    todo = [i for i, (p, _) in enumerate(st) if not cache_path(p.stem).exists()]
    if limit:
        todo = todo[:limit]
    print(f"rubric read: {len(todo)} of {len(st)} statements unread under {PROMPT_VERSION}, model {model}")
    tin = tout = 0
    for k, i in enumerate(todo):
        p, dt = st[i]
        prev = texts[i - 1] if i > 0 else None
        data = None
        for attempt in range(2):
            try:
                data, a, b = call(client, model, texts[i], prev)
                tin += a; tout += b
                break
            except Exception as e:
                if is_fatal(e):
                    print("!" * 70)
                    print(f"FATAL -- {type(e).__name__}: {e}")
                    print(f"{len(todo) - k} statement(s) NOT READ. Cached reads are kept. Nothing retried.")
                    print("!" * 70)
                    raise SystemExit(1)
                if attempt == 0:
                    time.sleep(3); continue
                print(f"    {p.stem}  FAILED: {type(e).__name__}: {e}")
        if data is None:
            continue
        rx = dissents_from_text(texts[i])
        if rx is not None and int(data.get("dissents", 0)) != rx:
            print(f"    {p.stem}: dissents read {data.get('dissents')} vs text {rx} (text pattern kept beside, model value used)")
        data.update(source="fomc_statement", date=dt.strftime("%Y-%m-%d"), prompt_version=PROMPT_VERSION, model=model,
                    words=len(texts[i].split()), prev_words=(len(texts[i - 1].split()) if i > 0 else None),
                    dissents_text=rx, chair=chair_of(dt), read_at=datetime.now().strftime("%Y-%m-%d %H:%M"))
        out = cache_path(p.stem); tmp = out.with_suffix(f".{os.getpid()}.tmp")
        tmp.write_text(json.dumps(data, indent=2)); os.replace(tmp, out)
        if (k + 1) % 20 == 0:
            print(f"  {k + 1}/{len(todo)}  in {tin:,} out {tout:,} tokens  ~US${tin / 1e6 * IN_RATE + tout / 1e6 * OUT_RATE:.2f}")
        time.sleep(sleep)
    print(f"done: in {tin:,} out {tout:,} tokens, ~US${tin / 1e6 * IN_RATE + tout / 1e6 * OUT_RATE:.2f}")


# ----------------------------------------------------------------------------------------------- features and the test
def frame() -> pd.DataFrame:
    rows = []
    for f in sorted(READS.glob(f"fomc_statement__*__{PROMPT_VERSION}.json")):
        d = json.loads(f.read_text())
        row = {k: float(d.get(k, 0) or 0) for k in LLM_DIMS}
        row["length_change"] = float(np.log(d["words"] / d["prev_words"])) if d.get("prev_words") else 0.0
        row["words"] = d.get("words"); row["date"] = pd.Timestamp(d["date"]); row["chair"] = d.get("chair") or chair_of(row["date"])
        rows.append(row)
    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    return df


def zscore(df: pd.DataFrame, dims=DIMS) -> np.ndarray:
    X = df[dims].to_numpy(float)
    mu, sd = X.mean(0), X.std(0, ddof=1)
    sd = np.where(sd > 0, sd, 1.0)
    return (X - mu) / sd


def _md(A, B):
    return np.sqrt(((A[:, None, :] - B[None, :, :]) ** 2).sum(-1)).mean()


def energy(X, Y) -> float:
    return float(2 * _md(X, Y) - _md(X, X) - _md(Y, Y))


def exact_p(Z: np.ndarray, n_cur: int) -> tuple[float, float, int]:
    """Z: the pooled rows, the first n_cur being the current group. Enumerates every C(N, n_cur) split."""
    N = len(Z); obs = energy(Z[:n_cur], Z[n_cur:]); cnt = tot = 0
    for S in combinations(range(N), n_cur):
        mask = np.zeros(N, bool); mask[list(S)] = True
        tot += 1
        if energy(Z[mask], Z[~mask]) >= obs - 1e-12:
            cnt += 1
    return obs, cnt / tot, tot


def compare(df: pd.DataFrame, Z: np.ndarray, cur_idx: list[int], prev_idx: list[int], label: str, dims=DIMS) -> dict:
    sub = np.vstack([Z[cur_idx], Z[prev_idx]]); n = len(cur_idx)
    obs, p, tot = exact_p(sub, n)
    per = {}
    for j, dname in enumerate(dims):
        o, pj, _ = exact_p(sub[:, [j]], n)
        per[dname] = dict(E=o, p=pj, mean_cur=float(df.loc[cur_idx, dname].mean()), mean_prev=float(df.loc[prev_idx, dname].mean()))
    rank = sorted(per, key=lambda k: per[k]["p"])
    print(f"{label}: n_cur {n} vs n_prev {len(prev_idx)}; energy {obs:.3f}; exact p = {p:.4f} over {tot:,} arrangements "
          f"(floor {1 / tot:.4f}); {'separates' if p < 0.05 else 'does not separate'} at 0.05; per-dimension order: " + ", ".join(f"{k} {per[k]['p']:.3f}" for k in rank))
    return dict(label=label, n_cur=n, n_prev=len(prev_idx), E=obs, p=p, arrangements=tot, floor=1 / tot, per_dim=per, dim_rank=rank,
                cur_dates=[str(d.date()) for d in df.loc[cur_idx, "date"]], prev_dates=[str(d.date()) for d in df.loc[prev_idx, "date"]])


def acceptance() -> dict:
    df = frame(); Z = zscore(df)
    out = {}
    for a, b in (("Bernanke", "Yellen"), ("Yellen", "Powell")):
        ia = list(df.index[df.chair == a][-LAST_K:]); ib = list(df.index[df.chair == b][:LAST_K])
        if len(ia) < LAST_K or len(ib) < LAST_K:
            print(f"{a}->{b}: too few statements read ({len(ia)}, {len(ib)})"); continue
        out[f"{a}->{b}"] = compare(df, Z, ib, ia, f"{a}->{b}: {b}'s first {LAST_K} vs {a}'s last {LAST_K}")
    sep = {k: v["p"] < 0.05 for k, v in out.items()}
    power = any(sep.values())
    yp, by = sep.get("Yellen->Powell"), sep.get("Bernanke->Yellen")
    right82 = (yp is True) and (by is False)
    verdict = "INSTRUMENT OK (at least one past transition separates)" if power else "UNINFORMATIVE (no past transition separates: a Warsh null means nothing)"
    print(f"acceptance: {verdict}; prior #82 (Yellen->Powell separates, Bernanke->Yellen does not): {'right' if right82 else 'wrong'}")
    J = _load(); J.update(acceptance=out, acceptance_verdict=verdict, instrument_ok=power, right82=right82, run=datetime.now().strftime("%Y-%m-%d %H:%M"))
    _save(J); return J


def test() -> dict:
    df = frame(); Z = zscore(df)
    names = [c[0] for c in CHAIRS if (df.chair == c[0]).any()]
    cur, prev = names[-1], names[-2]
    ic = list(df.index[df.chair == cur]); ip = list(df.index[df.chair == prev][-LAST_K:])
    res = compare(df, Z, ic, ip, f"{cur} ({len(ic)} statements) vs {prev}'s last {LAST_K}")
    means = df.groupby("chair")[DIMS + ["words"]].mean().round(3)
    J = _load(); J.update(test=res, chair=cur, previous=prev, n=len(ic), chair_means=json.loads(means.to_json(orient="index")),
                          run=datetime.now().strftime("%Y-%m-%d %H:%M"), n_read=int(len(df)))
    _save(J); _write_md(J); return J


def _load() -> dict:
    p = PROC / "chair_style.json"
    return json.loads(p.read_text()) if p.exists() else {}


def _save(J: dict):
    (PROC / "chair_style.json").write_text(json.dumps(J, indent=1, default=float))


def _write_md(J: dict):
    L = [f"# T-K3 — chair style on the rubric (exact permutation) — run {J.get('run')}", "",
         f"Rubric reads: {J.get('n_read')} statements under `{PROMPT_VERSION}`, own cache folder, never pooled with v1.", ""]
    if "acceptance" in J:
        L += ["## Acceptance check (registered 28 Oct 2026, prior #82)", "", "| transition | n | energy | exact p | arrangements | separates | dimensions by p |", "|---|---|---|---|---|---|---|"]
        for k, v in J["acceptance"].items():
            dims_txt = ", ".join(f"{d} {v['per_dim'][d]['p']:.3f}" for d in v["dim_rank"][:4])
            L.append(f"| {k} | {v['n_cur']} vs {v['n_prev']} | {v['E']:.3f} | {v['p']:.4f} | {v['arrangements']:,} | {'yes' if v['p'] < 0.05 else 'no'} | {dims_txt} |")
        L += ["", f"Verdict: {J['acceptance_verdict']}. Prior #82: {'right' if J.get('right82') else 'wrong'}.", ""]
    if "test" in J:
        t = J["test"]
        L += [f"## {J['chair']} vs {J['previous']}'s last {LAST_K} (T-K3, prior #79)", "",
              f"n = {t['n_cur']}; energy {t['E']:.3f}; exact p = {t['p']:.4f} over {t['arrangements']:,} arrangements (floor {t['floor']:.4f}); "
              f"{'separates' if t['p'] < 0.05 else 'does not separate'} at 0.05.", "",
              "| dimension | exact p | mean current | mean previous |", "|---|---|---|---|"]
        for d in t["dim_rank"]:
            v = t["per_dim"][d]; L.append(f"| {d} | {v['p']:.4f} | {v['mean_cur']:+.3f} | {v['mean_prev']:+.3f} |")
        L += ["", "Per-dimension p-values are descriptive (eight dimensions; a single one at 0.05 is not a finding).", ""]
    if "chair_means" in J:
        L += ["## Rubric means by chair", "", "| chair | " + " | ".join(DIMS + ["words"]) + " |", "|---|" + "---|" * (len(DIMS) + 1)]
        for c, row in J["chair_means"].items():
            L.append(f"| {c} | " + " | ".join(f"{row[d]:+.2f}" if d != "words" else f"{row[d]:.0f}" for d in DIMS + ["words"]) + " |")
    (DOCSDIR / "chair_style.md").write_text("\n".join(L) + "\n")
    print("  -> docs/chair_style.md, processed/chair_style.json")


# ----------------------------------------------------------------------------------------------- selftest (synthetic)
def selftest(reps=200, seed=0) -> bool:
    rng = np.random.default_rng(seed); d = len(DIMS); n, k = 4, LAST_K
    hits = 0
    for _ in range(reps):
        X = rng.standard_normal((n, d)); X[:, 2] += 3.5           # a planted shift of 3.5 sd on one dimension
        Y = rng.standard_normal((k, d)); _, p, _ = exact_p(np.vstack([X, Y]), n); hits += p <= 0.05
    power = hits / reps
    rej = 0
    for _ in range(reps):
        X = rng.standard_normal((n, d)); Y = rng.standard_normal((k, d)); _, p, _ = exact_p(np.vstack([X, Y]), n); rej += p <= 0.05
    size = rej / reps
    # the test is exact, so at n = 4 vs 8 the p-value takes only multiples of 1/495; the size test allows that granularity
    ok_power, ok_size = power >= 0.90, 0.02 <= size <= 0.08
    print(f"selftest: planted 3.5-sd shift on one of {d} dimensions, n {n} vs {k}: detected in {power:.0%} of {reps} (need >= 90%) -> {'PASS' if ok_power else 'FAIL'}")
    print(f"selftest: no shift: rejected at 0.05 in {size:.1%} of {reps} (need 2-8%) -> {'PASS' if ok_size else 'FAIL'}")
    s = "PASS" if ok_power and ok_size else "FAIL"
    (DOCSDIR / "chair_style_selftest.md").write_text(
        f"# chair_style selftest — {datetime.now():%Y-%m-%d %H:%M}\n\nPlanted 3.5-sd shift on one of {d} dimensions, n {n} vs {k}: "
        f"detected in {power:.0%} of {reps} (need ≥ 90%).  No shift: rejected at 0.05 in {size:.1%} of {reps} (need 2–8%).  **{s}**\n")
    return ok_power and ok_size


# ----------------------------------------------------------------------------------------------- record
def record():
    """Write T-K3 into the pre-registration (section 5), MASTER row 52 and CURRENT_STATE; replaces rows written earlier."""
    J = _load()
    if "test" not in J:
        raise SystemExit("run `test` first")
    t = J["test"]; stamp = datetime.now().strftime("%Y-%m-%d")
    acc = J.get("acceptance", {})
    acc_txt = "; ".join(f"{k} p {v['p']:.3f}" for k, v in acc.items()) or "not run"
    sep = t["p"] < 0.05
    top = t["dim_rank"][0]
    verdict_txt = "PASS — his statements are distinguishable from the previous chair's on the rubric" if sep else "FAIL — not distinguishable at this n"
    res = (f"T-K3 ({J['chair']} n = {t['n_cur']} vs {J['previous']}'s last {LAST_K}, exact permutation over {t['arrangements']:,} arrangements, floor {t['floor']:.4f}): "
           f"energy {t['E']:.2f}, p {t['p']:.4f} → {verdict_txt}; "
           f"strongest dimension {top} (p {t['per_dim'][top]['p']:.3f}; balance_sheet ranked {t['dim_rank'].index('balance_sheet') + 1} of {len(DIMS)}). "
           f"Acceptance on past transitions: {acc_txt} → {J.get('acceptance_verdict', 'not run')}")
    n4 = t["n_cur"] >= 4
    p79 = ("**#79 " + ("wrong" if sep else "right") + "**" + ("" if n4 else " (judged at n = " + str(t["n_cur"]) + "; re-judged at n = 4)"))
    p82 = "**#82 right**" if J.get("right82") else ("**#82 wrong**" if acc else "#82 not yet judged")
    pri = f"{p79}; {p82}"
    p = DOCSDIR / "prereg_liquidity_and_chair.md"; s = p.read_text()
    row = f"| {stamp} | T-K3 chair style (rubric, exact permutation) | {res}. docs/chair_style.md | {pri} |"
    s, done = _replace_line(s, r"^\| \d{4}-\d{2}-\d{2} \| T-K3 chair style \(rubric.*$", row)
    if not done:
        s = s.rstrip("\n") + "\n" + row + "\n"
    p.write_text(s); print("  prereg: T-K3 row " + ("replaced" if done else "added"))
    m = DOCSDIR / "PROJECT_MASTER.md"; s = m.read_text(); txt = f"{res} ({pri.replace('**', '')})."
    lines = s.split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith("| 52 |"):
            if "T-K3 next |" in ln:
                lines[i] = ln.replace("T-K3 next |", txt + " |", 1)
            else:
                lines[i] = re.sub(r"T-K3 \(.*?\)\. \|$", lambda _: txt + " |", ln, count=1) if re.search(r"T-K3 \(.*?\)\. \|$", ln) else ln
    s2 = "\n".join(lines)
    wrong = (sep and "#79" in pri and "wrong" in p79) or ("#82 wrong" in p82)
    if wrong:
        for note in (["#79 chair style separates at n = " + str(t["n_cur"])] if (sep and n4) else []) + (["#82 past transitions"] if "#82 wrong" in p82 else []):
            s2 = _bump_tally(s2, note)
    m.write_text(s2); print("  MASTER: row 52 " + ("updated" if s2 != s else "unchanged (anchor not found)"))
    cs = DOCSDIR / "CURRENT_STATE_2026-08-23.md"; s = cs.read_text(); line = f"T-K3 result ({datetime.now():%d %b}): {res}. {pri.replace('**', '')}."
    s, done = _replace_line(s, r"^T-K3 result \(.*$", line)
    if not done:
        s = s.rstrip("\n") + "\n\n" + line + "\n"
    cs.write_text(s); print("  CURRENT_STATE: T-K3 line " + ("replaced" if done else "added"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["cost", "selftest", "read", "acceptance", "test", "record"])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--model", default=MODEL_DEFAULT)
    ap.add_argument("--sleep", type=float, default=0.3)
    a = ap.parse_args()
    if a.cmd == "cost": cost()
    elif a.cmd == "selftest": sys.exit(0 if selftest() else 1)
    elif a.cmd == "read": read(a.limit, a.model, a.sleep)
    elif a.cmd == "acceptance": acceptance()
    elif a.cmd == "test": test()
    elif a.cmd == "record": record()
