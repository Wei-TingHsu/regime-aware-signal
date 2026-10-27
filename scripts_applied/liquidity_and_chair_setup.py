"""27 Oct night. (1) Record the flows/positioning run: #61 wrong, tally 62; the SPDR archive endpoint served a PDF (guard added, manual file accepted).
(2) Register T-L (is the liquidity-gold link constant through time?) and T-K (the few-shot chair problem) with criteria and priors, then write the code
for T-L and T-K0/T-K1/T-K2. Nothing is run by this script.
Run from the repo root:  python scripts_applied/liquidity_and_chair_setup.py
then:                    python -m src.liquidity_link run ; python -m src.chair_power run"""
from pathlib import Path
import ast, re
from datetime import datetime

PROC, DOCS = Path("processed"), Path("docs")
TODAY = "2026-10-27"

# ---------------------------------------------------------------- 1. flows.py: do not overwrite a CSV with a PDF; accept a manually downloaded file
fl = Path("src/flows.py"); s = fl.read_text()
if "looks_like_csv" in s: print("  flows.py guard: already")
else:
    old = """    try:
        raw = _get(GLD_URL); f.write_bytes(raw)
    except Exception as e:
        print(f"  GLD archive fetch failed ({type(e).__name__}); using the file on disk if any")
        if not f.exists(): return None
    txt = f.read_text("utf-8", "ignore").splitlines()"""
    new = """    def looks_like_csv(b: bytes) -> bool:
        head = b[:4000]; return (not head.startswith(b"%PDF")) and (not head.lstrip().startswith(b"<")) and (b"Date" in head or b"date" in head)
    try:
        raw = _get(GLD_URL)
        if looks_like_csv(raw): f.write_bytes(raw)
        else: print("  GLD archive endpoint did not serve CSV (PDF/HTML) -- download 'GLD historical data' from spdrgoldshares.com by hand into " + str(f) + " (csv or xlsx)")
    except Exception as e:
        print(f"  GLD archive fetch failed ({type(e).__name__}); using the file on disk if any")
    fx = f.with_suffix(".xlsx")
    if fx.exists():
        try:
            df = pd.read_excel(fx, header=None); hdr = next((i for i in range(min(40, len(df))) if df.iloc[i].astype(str).str.contains("Date").any()), None)
            if hdr is not None:
                df.columns = df.iloc[hdr].astype(str); df = df.iloc[hdr + 1:]
                dcol = next(c for c in df.columns if "Date" in c); tcol = next((c for c in df.columns if "Tonnes" in c), None) or next((c for c in df.columns if "Shares" in c), None)
                if tcol:
                    d = pd.to_datetime(df[dcol], errors="coerce"); v = pd.to_numeric(df[tcol].astype(str).str.replace(",", ""), errors="coerce")
                    s = pd.Series(v.to_numpy(), index=d).dropna(); s = s[~s.index.duplicated()].sort_index(); s.name = str(tcol); return s
        except Exception as e: print(f"  GLD xlsx on disk could not be read ({type(e).__name__})")
    if not f.exists() or not looks_like_csv(f.read_bytes()): print("  GLD archive: no usable CSV on disk"); return None
    txt = f.read_text("utf-8", "ignore").splitlines()"""
    assert old in s, "flows anchor"; s = s.replace(old, new, 1); fl.write_text(s); ast.parse(s); print("  flows.py: CSV guard, xlsx accepted")

# ---------------------------------------------------------------- 2. records of the flows run
p = DOCS / "prereg_factor_attribution.md"; s = p.read_text()
if "| 2026-10-27 | Flows and positioning run (GLD) |" in s: print("  prereg flows result: already")
else:
    s = s.rstrip("\n") + ("\n| 2026-10-27 | Flows and positioning run (GLD) | The SPDR archive endpoint served a PDF, so no ETF-flow series (guard added; a hand-downloaded file is accepted). "
        "CFTC positioning in for gold, silver, WTI (1,939 weeks). **T-A 0.160 on 236 blocks (was 0.177) → FAIL**; T-B: cot_gold 52%, cot_silver 61%, cot_oil 61% — unstable; "
        "the 2026 episode gives cot_gold a 0% share. A weekly series placed as a zero on four sessions in five cannot explain daily moves by construction; the registered cell is kept as run "
        "(no reverting on the outcome — FAIL is FAIL at 0.177 as at 0.160). Registered as candidates for the SPEC_GRID: a weekly, frequency-matched cell; the positioning *level* (z-score) as a state for the crowd hypothesis, not a return factor. | **#61 wrong** (tally 62) |\n")
    p.write_text(s); print("  prereg: flows result recorded, #61 wrong")

m = DOCS / "PROJECT_MASTER.md"; s = m.read_text()
if "tally 62" in s: print("  MASTER tally: already")
else:
    s = s.replace("tally 61 (#40–#43 lever priors", "tally 62 (#40–#43 lever priors", 1)
    s = s.replace("#58–#59 factor attribution R²", "#58–#59 factor attribution R², #61 flows and positioning (T-A 0.177 → 0.160, COT sign shares 52–61%)", 1)
    m.write_text(s); print("  MASTER: tally 62")

# ---------------------------------------------------------------- 3. registration: T-L and T-K
reg = DOCS / "prereg_liquidity_and_chair.md"
if reg.exists(): print("  prereg_liquidity_and_chair.md: already")
else:
    reg.write_text(f"""# Pre-registration — the liquidity–gold link through time (T-L) and the few-shot chair problem (T-K)

*Registered {TODAY} (night, SGT), before any code. Origin: the founder's question of 27 Oct — "we tested whether gold gets sold off when liquidity
drains; was it tested as time-dependent — not there before, there now? I want the logic to hold for all situations — such as a new Fed chair, who will
not announce often enough in his life for a large n; the machine must learn his pattern from a few actions."*

## 1. What is on record (read before registering; nothing re-run)

- **P1, 11 Aug (safe-haven inversion).** Claim: gold decouples from equities under liquidity stress. Liquidity state = 2-component GMM on correlation
  breadth and realised volatility of a basket excluding gold and equities (`src/liquidity_classifier.py`); outcome = 20-session rolling GLD–SPY
  correlation. **NULL, robust:** stress-minus-abundant gap +0.017 (p 0.44); macro-regime gap +0.16, wrong direction. The journal's "if anything gold
  co-moves slightly more in stress — consistent with dash-for-cash selling" is the *sign of a gap that is not distinguishable from zero*, not a finding.
  So "gold is sold when liquidity drains" has never been a registered, passed result here. **The test was pooled over the whole span: one gap, no
  sub-periods, no rolling windows, no change-point. It did not ask whether the relationship changed through time.**
- **T-B, 23 Oct (factor attribution sign stability).** The only time-dependence check on record: 75 walk-forward two-year windows. The rate-based
  proxies flip sign across windows — hike speculation 67%, real 10-yr yield 65% (unstable); dollar 100%, oil 89%, macro lines 83–87% (stable);
  positioning 52–61% (unstable, 27 Oct). Whatever "liquidity" means through yields, gold's response to it is not constant.
- **T9b, 29 Sep (surprise conditioning).** FOMC statement days 2011–2026 (131): gold's reaction to the 2-yr-yield surprise — level 1 INCONCLUSIVE
  (b −0.0054 per bucket, p 0.039), level 3 with the Bauer–Swanson intraday surprises FAIL (b −0.0005/bp, p 0.49). FOMC-by-regime split retired
  (forking paths). No test has ever split FOMC reactions by chair.
- **Not on record:** a direct liquidity quantity (the Fed's balance sheet net of the Treasury's account and reverse repo), a stability test on it, and
  a change-point test on anything.

## 2. T-L — is the liquidity–gold link constant through time?

**Data (free, FRED, as-of Wednesday).** Net liquidity `NL = WALCL/1000 − WTREGEN − RRPONTSYD` (US$ bn: Fed total assets − Treasury General Account −
overnight reverse repo; RRP is daily and is taken as of the Wednesday). `x_t` = weekly Δlog NL. `y_t` = GLD's weekly log return, Thursday-to-Wednesday
(sum of daily log returns from `processed/asset_returns.parquet`). Sample: from GLD's start (Nov 2004) to the latest Wednesday. Contemporaneous.
**This is a description of co-movement, not a trading signal:** the balance sheet is published Thursday for Wednesday.

| test | statistic | criterion |
|---|---|---|
| **T-L1 stability** | β of `y` on `x` in 104-week windows stepped 13 weeks; share of windows with the majority sign | stable if ≥ 80% (the T-B bar) |
| **T-L2 change-point** | Quandt–Andrews sup-F for one break in (α, β) with 15% trimming; null = constant-β model with a circular block bootstrap of its residuals (block 13 weeks, 500 draws) | break if p < 0.05; the break date and β before/after are reported |
| **T-L3 recent-only** | β of the last 104 weeks against the earlier windows' βs | flagged "recent is different" if outside the earlier windows' 5–95% range (descriptive) |
| **T-L4 conditional** | β in the P1 stress weeks vs abundant weeks (`processed/liquidity_states.parquet`, weekly majority) | reported; no criterion (two cells) |
| sub-periods | β, t and n for 2004–08, 2009–14, 2015–19, 2020–21, 2022–26 | reported |

**Prior #76 (Claude, before running).** Pooled β > 0 (more liquidity, higher gold) but small, t < 3. T-L1 share 60–75% → **UNSTABLE**. T-L2 p > 0.05 —
no single break survives the bootstrap; weekly noise swamps it. T-L3: the last window inside the range. In words: the link never held reliably and has
not newly appeared; what looks like "gold sold when liquidity drains" in 2026 is one episode, not a law. The founder's reading (a logic that was absent
before and present now) is the alternative; T-L2 and T-L3 are the tests that would support it.

## 3. T-K — the few-shot chair problem

**The point, stated before any number.** A chair's *actions* (what the statement says, how it changed, whether the press conference softened it) are
measured without noise: one statement gives one exact vector of features. The *market's response* to those actions is measured with noise of about
1% a day on gold against a surprise of a few basis points. Few-shot learning is possible for the first and not for the second: no tenure is long
enough to estimate a chair-specific market coefficient at daily resolution. T-K0 puts a number on that; T-K1 asks whether chairs have ever differed;
T-K2 is the quantity the page should show for the current chair; T-K3 is the few-shot style test on his statements' content.

**Units.** FOMC statement days from `processed/fomc_decisions.csv` up to today (corpus text on disk for 131 statements through 29 Jul 2026; the
16 Sep statement is not yet fetched — a feed gap to close). Chairs by date: Bernanke (to 31 Jan 2014), Yellen (3 Feb 2014 – 3 Feb 2018), Powell
(5 Feb 2018 – 15 May 2026), Warsh (sworn in 22 May 2026; statements 17 Jun, 29 Jul, 16 Sep; the fourth is 28 Oct, 2 pm ET = 29 Oct 02:00 SGT).
Surprise `s` = DGS2(t) − DGS2(t−1) in bp on the statement day (the registered level-1 proxy of T9b). Reaction `y` = GLD's log return on the day.

| test | statistic | criterion / prior |
|---|---|---|
| **T-K0 power (a calculation, not a test)** | pooled β of `y` on `s`, residual σ, var(s); meetings needed to detect a chair-specific difference δ at α 5% and power 80%: n = (2.80 σ)² / (δ² var s), for δ = β/2 and δ = β | **Prior #77:** n > 100 for δ = β/2 — beyond any tenure (8 meetings a year) |
| **T-K1 do chairs differ at all?** | chair × surprise interaction F-test on GLD (Bernanke, Yellen, Powell; ≥ 20 statements each), p from 2,000 permutations of the chair labels; TLT as the cross-check | PASS if p < 0.05 on GLD. **Prior #78: FAIL** (p > 0.2); between-chair variance τ² ≈ 0 |
| **T-K2 the current chair's posterior** | empirical Bayes: τ² from the chairs with n ≥ 20 (method of moments); for the current chair, w = τ² / (τ² + se²), posterior mean = β_pool + w (β̂_chair − β_pool), sd = (1/τ² + 1/se²)^−½ | reported with the shrinkage weight; refreshed after each statement. No criterion — it is what the page shows instead of a per-chair estimate |
| **T-K3 few-shot style (next script, after T-K0/T-K1)** | the LLM reads every statement (and press-conference transcript where on disk) on a fixed rubric: hawkish–dovish score, guidance strength, balance-sheet language, inflation-vs-labour emphasis, hedging density, dissents, length change, novelty vs the previous statement. Energy distance between the current chair's n statements and the previous chair's last 8; exact permutation over all C(n+8, n) arrangements | PASS if p < 0.05 ("his style is distinguishable"). Smallest attainable p: n = 3 → 1/165, n = 4 → 1/495. **Prior #79:** with n = 4 the overall distance does not separate (p > 0.05); balance-sheet language is the single dimension most likely to |

**Standing rule proposed by this registration.** "Learn fast from few" = a strong prior from the pooled history (T-K2) plus content features measured
without market noise (T-K3); never a per-chair market coefficient from n < 30. The page may say "Warsh so far: n statements; style distance from
Powell p = …; gold's reaction assumed at the pooled value until the data can say otherwise (after ~N meetings)".

## 4. Amendments

| date | change | reason |
|---|---|---|
""" + "\n"); print("  prereg_liquidity_and_chair.md: written (#76–#79 stated)")

# ---------------------------------------------------------------- 4. src/liquidity_link.py
ll = Path("src/liquidity_link.py")
if ll.exists(): print("  liquidity_link.py: already")
else:
    ll.write_text(r'''"""T-L: is the liquidity-gold link constant through time? Weekly Fed net liquidity (WALCL - TGA - RRP, FRED) against GLD's weekly return.
Stability (sign share across 104-week windows), change-point (sup-F, block-bootstrap null), recent-vs-history, conditional on the P1 liquidity state.
docs/prereg_liquidity_and_chair.md section 2.   python -m src.liquidity_link run"""
from __future__ import annotations
import json, os, sys, urllib.request, urllib.parse
from datetime import datetime
from pathlib import Path
import numpy as np, pandas as pd

PROC, DOCS, DP = Path("processed"), Path("docs"), Path("data_provenance") / "liquidity"
FRED = "https://api.stlouisfed.org/fred/series/observations"
WIN, STEP, TRIM, BLOCK, NDRAW, SEED, STABLE = 104, 13, 0.15, 13, 500, 0, 0.80
PERIODS = [("2004-08", 2004, 2008), ("2009-14", 2009, 2014), ("2015-19", 2015, 2019), ("2020-21", 2020, 2021), ("2022-26", 2022, 2026)]


def fred_key() -> str:
    env = Path(".env")
    if env.exists():
        for ln in env.read_text().splitlines():
            if ln.startswith("FRED_API_KEY="): return ln.split("=", 1)[1].strip().strip('"').strip("'")
    return os.environ.get("FRED_API_KEY", "")


def fred(sid: str, start: str = "2000-01-01", refresh: bool = True) -> pd.Series | None:
    """One FRED series, cached as data_provenance/liquidity/<id>.csv (the file on disk is the record)."""
    DP.mkdir(parents=True, exist_ok=True); f = DP / f"{sid}.csv"
    if refresh or not f.exists():
        try:
            q = urllib.parse.urlencode(dict(series_id=sid, api_key=fred_key(), file_type="json", observation_start=start))
            j = json.loads(urllib.request.urlopen(f"{FRED}?{q}", timeout=60).read())
            pd.DataFrame(j["observations"])[["date", "value"]].to_csv(f, index=False)
        except Exception as e:
            print(f"  FRED {sid}: fetch failed ({type(e).__name__}: {e})" + ("; using the cached file" if f.exists() else ""))
            if not f.exists(): return None
    df = pd.read_csv(f); s = pd.Series(pd.to_numeric(df["value"], errors="coerce").to_numpy(), index=pd.to_datetime(df["date"])).dropna(); s.name = sid
    return s


def net_liquidity() -> pd.DataFrame | None:
    w, t, r = fred("WALCL"), fred("WTREGEN"), fred("RRPONTSYD")
    if w is None or t is None: return None
    nl = (w / 1000.0).to_frame("walcl").join(t.rename("tga"), how="inner")
    nl["rrp"] = (r.reindex(nl.index, method="ffill") if r is not None else 0.0); nl["rrp"] = nl["rrp"].fillna(0.0)
    nl["NL"] = nl["walcl"] - nl["tga"] - nl["rrp"]; return nl


def weekly_pair(asset: str = "GLD") -> tuple[pd.Series, pd.Series, pd.DataFrame]:
    nl = net_liquidity()
    if nl is None: raise SystemExit("  no net-liquidity series (FRED key or network)")
    r = pd.read_parquet(PROC / "asset_returns.parquet"); r.index = pd.to_datetime(r.index); y = r[asset].resample("W-WED").sum(min_count=1)
    x = np.log(nl["NL"]).diff(); x.index = pd.to_datetime(x.index)
    df = pd.concat([x.rename("x"), y.rename("y")], axis=1).dropna(); df = df[df.index >= "2004-11-24"]
    return df["x"], df["y"], nl


def ols(x: np.ndarray, y: np.ndarray):
    n = len(x); xm, ym = x.mean(), y.mean(); sxx = ((x - xm) ** 2).sum(); b = ((x - xm) * (y - ym)).sum() / sxx; a = ym - b * xm
    e = y - a - b * x; s2 = (e @ e) / max(n - 2, 1); se = float(np.sqrt(s2 / sxx)); return float(a), float(b), se, e


def _rss_prefix(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """RSS of the simple regression on the first i points, i = 0..n (NaN where i < 2)."""
    cx, cy, cxx, cxy, cyy = [np.concatenate([[0.0], np.cumsum(v)]) for v in (x, y, x * x, x * y, y * y)]
    i = np.arange(len(x) + 1, dtype=float)
    with np.errstate(invalid="ignore", divide="ignore"):
        sxx = cxx - cx * cx / i; sxy = cxy - cx * cy / i; syy = cyy - cy * cy / i; rss = syy - sxy * sxy / sxx
    rss[:2] = np.nan; return rss


def sup_f(x: np.ndarray, y: np.ndarray, trim: float = TRIM) -> tuple[float, int]:
    """Quandt-Andrews sup-F for one break in (alpha, beta), trimming `trim` at both ends. Returns (sup F, break index = first point of the second segment)."""
    n = len(x); k = 2; R1 = _rss_prefix(x, y); R2 = _rss_prefix(x[::-1], y[::-1])[::-1]   # R2[i] = RSS of points i..n-1
    rss0 = R1[n]; lo, hi = int(np.floor(n * trim)), int(np.ceil(n * (1 - trim))); idx = np.arange(lo, hi)
    F = ((rss0 - R1[idx] - R2[idx]) / k) / ((R1[idx] + R2[idx]) / (n - 2 * k)); j = int(np.nanargmax(F)); return float(F[j]), int(idx[j])


def block_bootstrap_p(x: np.ndarray, y: np.ndarray, F_obs: float, n_draw: int = NDRAW, block: int = BLOCK, seed: int = SEED) -> tuple[float, np.ndarray]:
    """Null of a constant (alpha, beta): regenerate y from the pooled fit with circular block-bootstrapped residuals; sup-F each draw."""
    a, b, _, e = ols(x, y); n = len(x); rng = np.random.default_rng(seed); out = np.empty(n_draw); nb = int(np.ceil(n / block))
    for d in range(n_draw):
        starts = rng.integers(0, n, nb); idx = (starts[:, None] + np.arange(block)[None, :]).ravel()[:n] % n
        out[d] = sup_f(x, a + b * x + e[idx])[0]
    return float((out >= F_obs).mean()), out


def run(asset: str = "GLD"):
    x, y, nl = weekly_pair(asset); X, Y = x.to_numpy(), y.to_numpy(); n = len(X); dates = x.index
    a, b, se, e = ols(X, Y); t_pool = b / se
    # T-L1 stability
    rows = []
    for s0 in range(0, n - WIN + 1, STEP):
        _, bw, sew, _ = ols(X[s0:s0 + WIN], Y[s0:s0 + WIN]); rows.append(dict(start=dates[s0], end=dates[s0 + WIN - 1], beta=bw, t=bw / sew))
    W = pd.DataFrame(rows); pos = float((W.beta > 0).mean()); share = max(pos, 1 - pos); maj = "+" if pos >= 0.5 else "-"
    # T-L2 change-point
    F_obs, j = sup_f(X, Y); p_break, null = block_bootstrap_p(X, Y, F_obs); bdate = dates[j]
    _, b1, se1, _ = ols(X[:j], Y[:j]); _, b2, se2, _ = ols(X[j:], Y[j:])
    # T-L3 recent vs history
    _, b_last, se_last, _ = ols(X[-WIN:], Y[-WIN:]); earlier = W[W.end < dates[-WIN]].beta; lo5, hi95 = (np.percentile(earlier, 5), np.percentile(earlier, 95)) if len(earlier) >= 5 else (np.nan, np.nan)
    recent_diff = bool(len(earlier) >= 5 and (b_last < lo5 or b_last > hi95))
    # sub-periods
    per = []
    for lab, y0, y1 in PERIODS:
        m = (dates.year >= y0) & (dates.year <= y1)
        if m.sum() >= 30: _, bp, sep, _ = ols(X[m], Y[m]); per.append(dict(period=lab, n=int(m.sum()), beta=bp, t=bp / sep))
    # T-L4 conditional on the P1 liquidity state
    cond = None; fs = PROC / "liquidity_states.parquet"
    if fs.exists():
        try:
            L = pd.read_parquet(fs); L.index = pd.to_datetime(L.index)
            col = next((c for c in L.columns if "stress" in c.lower()), None)
            if col is not None:
                st = L[col].astype(float).resample("W-WED").mean().reindex(dates); m1 = (st > 0.5).to_numpy(); m0 = (st <= 0.5).to_numpy()
                if m1.sum() >= 30 and m0.sum() >= 30:
                    _, bs, ses, _ = ols(X[m1], Y[m1]); _, ba, sea, _ = ols(X[m0], Y[m0]); cond = dict(col=col, n_stress=int(m1.sum()), beta_stress=bs, t_stress=bs / ses, n_abundant=int(m0.sum()), beta_abundant=ba, t_abundant=ba / sea)
            else: cond = dict(note=f"no stress column in liquidity_states.parquet (columns {list(L.columns)[:6]})")
        except Exception as ex: cond = dict(note=f"liquidity_states.parquet not usable ({type(ex).__name__})")
    v1 = "STABLE" if share >= STABLE else "UNSTABLE"; v2 = "BREAK" if p_break < 0.05 else "no break"
    L = [f"# T-L — the liquidity–gold link through time ({asset})", "",
         f"*{datetime.now():%Y-%m-%d %H:%M}. {n} weeks, {dates[0].date()} → {dates[-1].date()}; x = weekly Δlog(Fed assets − TGA − RRP), y = {asset} weekly log return, Thursday-to-Wednesday; contemporaneous, not a trading signal. prereg_liquidity_and_chair §2.*", "",
         f"**Pooled:** β = {b:+.3f} (t {t_pool:+.2f}) — a 1% weekly rise in net liquidity goes with {b:+.3f}% on {asset} the same week.", "",
         f"**T-L1 stability:** {len(W)} windows of {WIN} weeks; majority sign {maj}, share {share:.0%} → **{v1}** (bar {STABLE:.0%}).", "",
         f"**T-L2 change-point:** sup-F {F_obs:.2f} at {bdate.date()}; bootstrap null median {np.median(null):.2f}, 95th {np.percentile(null, 95):.2f}; **p = {p_break:.3f} → {v2}**. β before {b1:+.3f} (t {b1 / se1:+.2f}), after {b2:+.3f} (t {b2 / se2:+.2f}).", "",
         f"**T-L3 recent-only:** last {WIN} weeks β = {b_last:+.3f} (t {b_last / se_last:+.2f}); earlier windows' 5–95% range {lo5:+.3f} to {hi95:+.3f} → " + ("**recent is different** (outside the range)" if recent_diff else "inside the range — nothing new"), ""]
    if cond and "beta_stress" in cond:
        L += [f"**T-L4 conditional (P1 state '{cond['col']}'):** stress weeks β = {cond['beta_stress']:+.3f} (t {cond['t_stress']:+.2f}, n {cond['n_stress']}); abundant weeks β = {cond['beta_abundant']:+.3f} (t {cond['t_abundant']:+.2f}, n {cond['n_abundant']}).", ""]
    elif cond: L += [f"T-L4: {cond['note']}", ""]
    L += ["| period | n weeks | β | t |", "|---|---|---|---|"] + [f"| {q['period']} | {q['n']} | {q['beta']:+.3f} | {q['t']:+.2f} |" for q in per]
    L += ["", "| window start | end | β | t |", "|---|---|---|---|"] + [f"| {q.start.date()} | {q.end.date()} | {q.beta:+.3f} | {q.t:+.2f} |" for q in W.itertuples()]
    out = DOCS / f"liquidity_link_{asset}.md"; out.write_text("\n".join(L) + "\n"); print("\n".join(L[:14])); print(f"-> {out}")
    J = json.loads((PROC / "liquidity_link.json").read_text()) if (PROC / "liquidity_link.json").exists() else {}
    J[asset] = dict(run=datetime.now().strftime("%Y-%m-%d %H:%M"), n=n, start=str(dates[0].date()), end=str(dates[-1].date()), beta=b, t=t_pool, TL1=dict(windows=len(W), share=share, majority=maj, verdict=v1),
                    TL2=dict(supF=F_obs, date=str(bdate.date()), p=p_break, beta_before=b1, beta_after=b2, verdict=v2), TL3=dict(beta_last=b_last, lo5=float(lo5), hi95=float(hi95), recent_is_different=recent_diff),
                    TL4=cond, periods=per, nl_latest=dict(date=str(nl.index[-1].date()), NL_bn=float(nl["NL"].iloc[-1]), walcl_bn=float(nl["walcl"].iloc[-1]), tga_bn=float(nl["tga"].iloc[-1]), rrp_bn=float(nl["rrp"].iloc[-1])))
    (PROC / "liquidity_link.json").write_text(json.dumps(J, indent=1, default=float))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "run": run(sys.argv[2] if len(sys.argv) > 2 else "GLD")
    elif cmd == "levels":
        nl = net_liquidity(); print(nl.tail(8).round(0)) if nl is not None else print("  none")
'''); ast.parse(ll.read_text()); print("  src/liquidity_link.py: written, parses")

# ---------------------------------------------------------------- 5. src/chair_power.py
cp = Path("src/chair_power.py")
if cp.exists(): print("  chair_power.py: already")
else:
    cp.write_text(r'''"""T-K0/T-K1/T-K2: the few-shot chair problem. Statement-day reaction of GLD (and TLT) to the 2-yr-yield surprise, by chair; power of a per-chair
coefficient; chair x surprise interaction with a permutation null; empirical-Bayes posterior for the current chair.
docs/prereg_liquidity_and_chair.md section 3.   python -m src.chair_power run"""
from __future__ import annotations
import json, sys
from datetime import datetime
from math import comb
from pathlib import Path
import numpy as np, pandas as pd

PROC, DOCS = Path("processed"), Path("docs")
CHAIRS = [("Bernanke", "2006-02-01", "2014-01-31"), ("Yellen", "2014-02-03", "2018-02-03"), ("Powell", "2018-02-05", "2026-05-15"), ("Warsh", "2026-05-22", "2099-12-31")]
MIN_N, NPERM, SEED, Z = 20, 2000, 0, 1.96 + 0.84   # alpha 5% two-sided, power 80%


def chair_of(d: pd.Timestamp) -> str:
    for name, a, b in CHAIRS:
        if pd.Timestamp(a) <= d <= pd.Timestamp(b): return name
    return "other"


def table() -> pd.DataFrame:
    dates = pd.to_datetime(pd.read_csv(PROC / "fomc_decisions.csv")["date"]); dates = dates[dates <= pd.Timestamp.today().normalize()]
    r = pd.read_parquet(PROC / "asset_returns.parquet"); r.index = pd.to_datetime(r.index)
    m = pd.read_parquet(PROC / "macro_panel.parquet"); m.index = pd.to_datetime(m.index); s = (m["DGS2"].diff() * 100).reindex(r.index)
    rows = [dict(date=d, chair=chair_of(d), s=s.get(d, np.nan), gld=r["GLD"].get(d, np.nan), tlt=(r["TLT"].get(d, np.nan) if "TLT" in r.columns else np.nan)) for d in dates]
    df = pd.DataFrame(rows).dropna(subset=["s", "gld"]); return df


def ols(x, y):
    n = len(x); xm, ym = x.mean(), y.mean(); sxx = ((x - xm) ** 2).sum(); b = ((x - xm) * (y - ym)).sum() / sxx if sxx > 0 else np.nan; a = ym - b * xm
    e = y - a - b * x; s2 = (e @ e) / max(n - 2, 1); return float(a), float(b), float(np.sqrt(s2 / sxx)) if sxx > 0 else np.nan, e


def interaction_F(df: pd.DataFrame, col: str, labels: np.ndarray) -> float:
    """F for chair x surprise slopes (full: own intercept and slope per chair) against a common slope with own intercepts."""
    y = df[col].to_numpy(); s = df["s"].to_numpy(); groups = sorted(set(labels)); n = len(y)
    D = np.column_stack([(labels == g).astype(float) for g in groups]); Xr = np.column_stack([D, s]); Xf = np.column_stack([D, D * s[:, None]])
    def rss(X): c, *_ = np.linalg.lstsq(X, y, rcond=None); e = y - X @ c; return float(e @ e)
    rf, rr = rss(Xf), rss(Xr); kf, kr = Xf.shape[1], Xr.shape[1]; return ((rr - rf) / (kf - kr)) / (rf / max(n - kf, 1))


def run():
    df = table(); n = len(df); a, b, se, e = ols(df.s.to_numpy(), df.gld.to_numpy()); sigma = float(e.std(ddof=2)); var_s = float(df.s.var())
    per = []
    for name, _, _ in CHAIRS:
        g = df[df.chair == name]
        if len(g) >= 3: _, bc, sec, _ = ols(g.s.to_numpy(), g.gld.to_numpy()); per.append(dict(chair=name, n=int(len(g)), beta=bc, se=sec, mean_s=float(g.s.mean()), sd_s=float(g.s.std()), mean_gld=float(g.gld.mean())))
        else: per.append(dict(chair=name, n=int(len(g)), beta=np.nan, se=np.nan, mean_s=float(g.s.mean()) if len(g) else np.nan, sd_s=np.nan, mean_gld=float(g.gld.mean()) if len(g) else np.nan))
    P = pd.DataFrame(per); big = P[P.n >= MIN_N]
    tau2 = float(max(0.0, big.beta.var(ddof=1) - (big.se ** 2).mean())) if len(big) >= 2 else 0.0
    # T-K0 power: meetings needed to detect delta
    need = {f"delta = beta/{k}": (Z ** 2) * sigma ** 2 / ((abs(b) / k) ** 2 * var_s) if b != 0 else np.nan for k in (2, 1)}
    # T-K1 interaction among the chairs with n >= MIN_N
    sub = df[df.chair.isin(big.chair)].reset_index(drop=True); lab = sub.chair.to_numpy(); rng = np.random.default_rng(SEED)
    F_obs = interaction_F(sub, "gld", lab); null = np.array([interaction_F(sub, "gld", rng.permutation(lab)) for _ in range(NPERM)]); p_gld = float((null >= F_obs).mean())
    p_tlt = np.nan; F_tlt = np.nan
    if sub.tlt.notna().sum() == len(sub):
        F_tlt = interaction_F(sub, "tlt", lab); null_t = np.array([interaction_F(sub, "tlt", rng.permutation(lab)) for _ in range(NPERM)]); p_tlt = float((null_t >= F_tlt).mean())
    # T-K2 posterior for the current chair
    cur = P.iloc[-1]; post = None
    if np.isfinite(cur.se):
        w = tau2 / (tau2 + cur.se ** 2) if tau2 > 0 else 0.0; mean = b + w * (cur.beta - b); sd = (1 / tau2 + 1 / cur.se ** 2) ** -0.5 if tau2 > 0 else 0.0
        post = dict(chair=cur.chair, n=int(cur.n), beta_hat=float(cur.beta), se=float(cur.se), weight_on_own=float(w), posterior_mean=float(mean), posterior_sd=float(sd))
    min_p = {k: 1 / comb(k + 8, k) for k in (3, 4, 5, 6, 8)}
    v1 = "PASS — chairs differ" if p_gld < 0.05 else "FAIL — no detectable chair difference"
    L = [f"# T-K — the few-shot chair problem (GLD on the 2-yr surprise, statement days)", "",
         f"*{datetime.now():%Y-%m-%d %H:%M}. {n} statement days {df.date.min().date()} → {df.date.max().date()}; s = ΔDGS2 bp on the day, y = GLD log return on the day (%). prereg_liquidity_and_chair §3.*", "",
         f"**Pooled:** β = {b * 100:+.4f}% per bp (se {se * 100:.4f}), residual σ = {sigma * 100:.2f}% a day, sd of the surprise {np.sqrt(var_s):.1f} bp.", "",
         "| chair | statements | mean surprise (bp) | sd (bp) | mean GLD day (%) | β (% per bp) | se |", "|---|---|---|---|---|---|---|"]
    for q in P.itertuples(): L.append(f"| {q.chair} | {q.n} | {q.mean_s:+.1f} | {q.sd_s:.1f} | {q.mean_gld * 100:+.2f} | {q.beta * 100:+.4f} | {q.se * 100:.4f} |" if np.isfinite(q.beta) else f"| {q.chair} | {q.n} | {q.mean_s:+.1f} | — | {q.mean_gld * 100:+.2f} | — | — |")
    L += ["", f"**T-K0 power:** meetings needed to detect a chair-specific difference at α 5%, power 80% — " + "; ".join(f"{k}: **{v:,.0f}**" for k, v in need.items()) + f". A tenure is 8 meetings a year.", "",
          f"**T-K1 chairs differ?** interaction F = {F_obs:.2f} among {', '.join(big.chair)}; permutation p = **{p_gld:.3f}** → **{v1}**; between-chair τ = {np.sqrt(tau2) * 100:.4f}% per bp" + (f"; TLT cross-check F = {F_tlt:.2f}, p = {p_tlt:.3f}" if np.isfinite(p_tlt) else "") + ".", ""]
    if post: L += [f"**T-K2 {post['chair']} so far ({post['n']} statements):** own estimate {post['beta_hat'] * 100:+.4f}% per bp (se {post['se'] * 100:.4f}); weight the data earns against the pooled prior {post['weight_on_own']:.0%}; posterior {post['posterior_mean'] * 100:+.4f}% ± {post['posterior_sd'] * 100:.4f}. The page quotes the posterior, not the own estimate.", ""]
    L += ["**T-K3 (not run):** smallest attainable exact-permutation p for n statements against the previous chair's last 8 — " + ", ".join(f"n = {k}: {v:.4f}" for k, v in min_p.items()) + "."]
    out = DOCS / "chair_power.md"; out.write_text("\n".join(L) + "\n"); print("\n".join(L)); print(f"-> {out}")
    J = dict(run=datetime.now().strftime("%Y-%m-%d %H:%M"), n=n, beta=b, se=se, sigma=sigma, var_s=var_s, chairs=per, tau2=tau2, need=need, TK1=dict(F=F_obs, p=p_gld, F_tlt=F_tlt, p_tlt=p_tlt, verdict=v1), TK2=post, min_p=min_p)
    (PROC / "chair_power.json").write_text(json.dumps(J, indent=1, default=float))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "run": run()
    elif cmd == "table": print(table().tail(12))
'''); ast.parse(cp.read_text()); print("  src/chair_power.py: written, parses")

# ---------------------------------------------------------------- 6. MASTER register rows 51-52, CURRENT_STATE, TRACK
s = m.read_text()
if "| 51 | Liquidity–gold link through time (T-L)" in s: print("  MASTER rows 51-52: already")
else:
    i = s.find("\n| 50 |"); j = s.find("\n", i + 1)
    if i > 0 and j > i:
        rows = ("\n| 51 | Liquidity–gold link through time (T-L): GLD's weekly return on weekly Δlog Fed net liquidity (assets − TGA − RRP) — sign stable across 104-week windows (≥ 80%); one break by sup-F against a block-bootstrap null (p < 0.05); the last two years vs the earlier windows' range | registered 27 Oct, not run; prior #76: unstable, no break, nothing new | — |"
                "\n| 52 | Few-shot chair (T-K): meetings needed for a per-chair gold reaction (T-K0); chair × surprise interaction 2011–2026, permutation p < 0.05 on GLD (T-K1); empirical-Bayes posterior for the current chair (T-K2); style distance on LLM-read rubric scores by exact permutation, p < 0.05 (T-K3) | registered 27 Oct, not run; priors #77 n > 100, #78 FAIL, #79 n = 4 does not separate | — |")
        s = s[:j] + rows + s[j:]; m.write_text(s); print("  MASTER: rows 51-52 registered")
    else: print("  MASTER: row 50 anchor not found — rows 51-52 not inserted")
cs = DOCS / "CURRENT_STATE_2026-08-23.md"; s = cs.read_text()
if "### 18.39" in s: print("  CURRENT_STATE 18.39: already")
else:
    cs.write_text(s.rstrip("\n") + """

### 18.39 Flows run; the liquidity question; the few-shot chair (27 Oct)

Flows and positioning (amendment #61) ran: the SPDR archive endpoint served a PDF, so there is no ETF-flow series yet; CFTC positioning for gold,
silver and WTI is in. T-A fell from 0.177 to 0.160 (FAIL either way) and the three positioning factors are sign-unstable (52–61%): a weekly series
placed as zeros on four sessions in five cannot explain daily moves. #61 wrong, tally 62. The founder asked whether "gold is sold when liquidity
drains" was ever tested as time-dependent. It was not: P1 (11 Aug) was one pooled gap, NULL, and its "dash-for-cash" line is the sign of a gap not
distinguishable from zero; T-B is the only time-dependence check and shows the rate proxies flipping sign across windows. T-L registers the direct
test (Fed net liquidity, weekly; stability, change-point, recent-vs-history). He also asked how a new chair's pattern can be learned from a few
announcements. T-K registers the answer: a chair's actions are measured without noise and can be learned from few (T-K3, exact permutation); the
market's reaction to them cannot be estimated per chair within a tenure (T-K0 power), so the page carries the pooled coefficient shrunk toward the
chair (T-K2). Priors #76–#79 on file; code written for T-L and T-K0–K2; nothing run.
"""); print("  CURRENT_STATE 18.39: appended")
tr = DOCS / "TRACK.md"; s = tr.read_text()
if "3.35" in s and "liquidity–gold link" in s: print("  TRACK 3.35: already")
else:
    tr.write_text(s.rstrip("\n") + """

### 3.35 The liquidity–gold link through time (T-L) and the few-shot chair (T-K) — registered 27 Oct

Origin: the founder's question (27 Oct). Record: `docs/prereg_liquidity_and_chair.md`; code `src/liquidity_link.py`, `src/chair_power.py`; T-K3
(LLM rubric reads of every statement, exact permutation) follows T-K0/T-K1. Open: the 16 Sep 2026 FOMC statement is not in the corpus (feed gap);
the SPDR ETF-flow archive must be downloaded by hand.
"""); print("  TRACK 3.35: appended")
for f in ("src/flows.py", "src/liquidity_link.py", "src/chair_power.py", "src/factor_attribution.py", "src/why_moved.py", "src/context.py", "app.py"):
    ast.parse(Path(f).read_text())
print("  all modules parse")
print("done -- python -m src.liquidity_link run ; python -m src.chair_power run")
