"""
Report-level scoreboard -- scores the DECISION REPORT, not the price models.

Registered: docs/prereg_report_scoreboard.md (97dd490, amendments 0734c76).
Built:      2026-09-14, against the seven acceptance tests in prereg §12,
            on synthetic ledgers only. No real report is scored until all
            seven pass (`--selftest`).

Two ledgers, one scorer:
  forward   processed/report_ledger.csv   append-only; a matured row is never edited
  backfill  (step 7, not here)            same scorer over outputs/reports_backfill/<hash>/

Unit of observation: (report date t, asset a, horizon h).
Call            sign(assets[a].net_view) -- horizon-free.
Primary return  log close(t) -> close(t+h), NYSE sessions (the estimand).
Tradeable       log open(t+1) -> close(t+1+h) (what a reader could do).
Exclusions      abstain / sources_disagree / net_view == 0 / no document
                -> counted in COVERAGE, never in hit-rate. A realised return
                of exactly 0 counts as a MISS.
Non-overlap     every h-th report date per asset, first date fixed. Only
                non-overlap rows enter any test.
Minimum         no figure printed for a cell with < 30 non-overlap rows.
Null            within asset, permute calls across report dates in contiguous
                blocks of PRIMARY_H rows; returns stay in place; 10,000 draws.
Criterion       pooled, h*=3, non-overlap, >= 30 rows: hit-rate above the
                null's 95th percentile AND asymmetry > 1 with 95% block-bootstrap
                lower bound > 1. One of two = INCONCLUSIVE.

Usage:
  python -m src.report_scoreboard --selftest            # prereg §12, writes docs/report_scoreboard_selftest.md
  python -m src.report_scoreboard                       # update ledger from outputs/reports, score, write md/json
  python -m src.report_scoreboard --reports-dir outputs/reports_backfill/<hash> --ledger /tmp/x.csv --tag backfill_<hash>
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

# ---- registered constants (prereg §2, §3, §5, §6) ----------------------------
HORIZONS = (2, 3, 5, 20)   # 2 added 2026-10-09; 3 kept so the old primary stays reported
PRIMARY_H = 2              # h* 3 -> 2 on 2026-10-09 (amendment)
MIN_ROWS = 30
N_PERM = 10_000
N_BOOT = 2_000          # bootstrap draws for the asymmetry interval (declared here; prereg gives the level, 95%, not the draw count)
ALPHA = 0.05
BLOCK = PRIMARY_H       # block length, in report dates, for the permutation null and the bootstrap
WRITE_ONCE_FROM = "20260911"   # first session under the write-once rule (step6_report.WRITE_ONCE_FROM)

REPORT_DIR = Path("outputs/reports")
LEDGER = Path("processed/report_ledger.csv")
OUT_JSON = Path("processed/report_scoreboard.json")
OUT_MD = Path("docs/report_scoreboard.md")
SELFTEST_MD = Path("docs/report_scoreboard_selftest.md")

EXCL_NO_DOC = "no_document"
EXCL_ABSTAIN = "abstain"
EXCL_DIVERGE = "divergence"
EXCL_ZERO = "zero_direction"
CALL = "call"

LEDGER_COLS = ["date", "asset", "h", "kind", "call", "net_view", "tier", "ess", "w",
               "dominant_source", "agreement", "regime", "n_docs", "estimate_horizon",
               "ret_primary", "ret_tradeable", "status", "logged_at", "matured_at"]


# =============================================================================
# 1. reports -> per-(date, asset) rows
# =============================================================================
def load_reports(report_dir: Path, since: str = WRITE_ONCE_FROM) -> list[dict]:
    out = []
    for p in sorted(Path(report_dir).glob("*.json")):
        if p.stem < since:
            continue
        try:
            out.append(json.loads(p.read_text()))
        except Exception as e:  # a corrupt report is reported, not scored
            print(f"  {p.name}: unreadable ({type(e).__name__}), skipped")
    return out


def classify(e: dict) -> str:
    """One exclusion label or CALL, per the prereg §1 rules, in this order."""
    if e.get("n_docs_today", 0) == 0:
        return EXCL_NO_DOC
    if e.get("abstain"):
        return EXCL_ABSTAIN
    if e.get("sources_disagree"):
        return EXCL_DIVERGE
    nv = e.get("net_view")
    if nv is None or float(nv) == 0.0:
        return EXCL_ZERO
    return CALL


def rows_from_reports(reports: list[dict]) -> pd.DataFrame:
    rows = []
    for R in reports:
        d = pd.Timestamp(R["date"])
        reg = R.get("regime", {}) or {}
        for asset, e in (R.get("assets") or {}).items():
            est = e.get("estimate") or {}
            kind = classify(e)
            nv = e.get("net_view")
            rows.append(dict(
                date=d, asset=asset, kind=kind,
                call=(np.sign(float(nv)) if kind == CALL else np.nan),
                net_view=(float(nv) if nv is not None else np.nan),
                tier=est.get("tier", np.nan), ess=est.get("ess", np.nan),
                w=est.get("w_shrink", est.get("w", np.nan)),
                dominant_source=e.get("dominant_source"),
                agreement=e.get("agreement"),
                regime=reg.get("label", np.nan),
                n_docs=e.get("n_docs_today", 0),
                estimate_horizon=est.get("horizon", R.get("estimate_horizon_sessions", np.nan)),
            ))
    if not rows:
        return pd.DataFrame(columns=[c for c in LEDGER_COLS if c not in ("h", "ret_primary", "ret_tradeable", "status", "logged_at", "matured_at")])
    return pd.DataFrame(rows)


# =============================================================================
# 2. realised returns
# =============================================================================
def realise(calls: pd.DataFrame, closes: pd.DataFrame, opens: pd.DataFrame | None,
            sessions: pd.DatetimeIndex, horizons=HORIZONS) -> pd.DataFrame:
    """Expand (date, asset) rows to (date, asset, h) with both entry conventions.

    closes / opens: index = sessions (a superset is fine), columns = assets.
    A row whose exit session has not completed (not in `closes.index` with a
    value) stays pending with NaN returns.
    """
    sessions = pd.DatetimeIndex(sessions).sort_values()
    pos = {d: i for i, d in enumerate(sessions)}
    out = []
    for _, r in calls.iterrows():
        d = pd.Timestamp(r["date"])
        for h in horizons:
            rp = rt = np.nan
            status = "pending"
            if d in pos:
                i = pos[d]
                j = i + h                       # exit for primary: close of t+h
                if j < len(sessions):
                    a = r["asset"]
                    c0 = closes.at[d, a] if (d in closes.index and a in closes.columns) else np.nan
                    c1 = closes.at[sessions[j], a] if (sessions[j] in closes.index and a in closes.columns) else np.nan
                    if np.isfinite(c0) and np.isfinite(c1) and c0 > 0 and c1 > 0:
                        rp = float(np.log(c1 / c0))
                        status = "matured"
                    if opens is not None and i + 1 + h < len(sessions):
                        e_d, x_d = sessions[i + 1], sessions[i + 1 + h]
                        o0 = opens.at[e_d, a] if (e_d in opens.index and a in opens.columns) else np.nan
                        c2 = closes.at[x_d, a] if (x_d in closes.index and a in closes.columns) else np.nan
                        if np.isfinite(o0) and np.isfinite(c2) and o0 > 0 and c2 > 0:
                            rt = float(np.log(c2 / o0))
            row = dict(r)
            row.update(h=h, ret_primary=rp, ret_tradeable=rt, status=status)
            out.append(row)
    df = pd.DataFrame(out)
    for c in LEDGER_COLS:
        if c not in df.columns:
            df[c] = np.nan
    for c in ("logged_at", "matured_at"):       # text columns; an all-NaN float
        df[c] = df[c].astype(object)            # column refuses a string later
    return df[LEDGER_COLS]


# =============================================================================
# 3. sampling, metrics, null, bootstrap
# =============================================================================
def nonoverlap_dates(dates, h: int) -> list:
    """Every h-th report date, first date fixed, over the SORTED UNIQUE dates."""
    u = sorted(set(pd.to_datetime(d) for d in dates))
    return u[::h]


def nonoverlap(df: pd.DataFrame, h: int) -> pd.DataFrame:
    """Per asset, keep every h-th report date (first fixed)."""
    keep = []
    for a, g in df.groupby("asset", sort=False):
        sel = set(nonoverlap_dates(g["date"], h))
        keep.append(g[g["date"].isin(sel)])
    return pd.concat(keep) if keep else df.iloc[0:0]


def metrics(call: np.ndarray, ret: np.ndarray) -> dict:
    """Hit-rate, asymmetry, mean signed return, profit factor. Zero return = miss."""
    call = np.asarray(call, float); ret = np.asarray(ret, float)
    ok = np.isfinite(call) & np.isfinite(ret)
    call, ret = call[ok], ret[ok]
    n = len(call)
    if n == 0:
        return dict(n=0, hit=np.nan, asym=np.nan, mean_signed=np.nan, pf=np.nan, n_hits=0, n_misses=0, no_misses=False)
    hit = (np.sign(call) == np.sign(ret)) & (ret != 0)
    m_h = np.abs(ret[hit]).mean() if hit.any() else np.nan
    m_m = np.abs(ret[~hit]).mean() if (~hit).any() else np.nan
    asym = (m_h / m_m) if (hit.any() and (~hit).any() and m_m > 0) else np.nan
    signed = call * ret
    gains = signed[signed > 0].sum(); losses = -signed[signed < 0].sum()
    pf = (gains / losses) if losses > 0 else np.nan
    return dict(n=int(n), hit=float(hit.mean()), asym=(float(asym) if np.isfinite(asym) else np.nan),
                mean_signed=float(signed.mean()), pf=(float(pf) if np.isfinite(pf) else np.nan),
                n_hits=int(hit.sum()), n_misses=int((~hit).sum()), no_misses=bool(hit.all()))


def _block_perm(x: np.ndarray, block: int, rng: np.random.Generator) -> np.ndarray:
    """Permute x in contiguous blocks of `block` (last block may be short)."""
    n = len(x)
    if block <= 1 or n <= block:
        return x[rng.permutation(n)]
    idx = np.arange(n)
    blocks = [idx[i:i + block] for i in range(0, n, block)]
    order = rng.permutation(len(blocks))
    return x[np.concatenate([blocks[k] for k in order])]


def null_distribution(df: pd.DataFrame, ret_col: str, block: int = BLOCK,
                      n_perm: int = N_PERM, seed: int = 0) -> dict:
    """Within-asset block permutation of CALLS across report dates; returns fixed.

    Returns the null draws of pooled hit-rate and asymmetry.
    """
    rng = np.random.default_rng(seed)
    groups = []
    for a, g in df.groupby("asset", sort=False):
        g = g.sort_values("date")
        c = g["call"].to_numpy(float); r = g[ret_col].to_numpy(float)
        ok = np.isfinite(c) & np.isfinite(r)
        if ok.sum():
            groups.append((c[ok], r[ok]))
    if not groups:
        return dict(hit=np.array([]), asym=np.array([]))
    hits = np.empty(n_perm); asyms = np.empty(n_perm)
    for k in range(n_perm):
        cs = np.concatenate([_block_perm(c, block, rng) for c, _ in groups])
        rs = np.concatenate([r for _, r in groups])
        m = metrics(cs, rs)
        hits[k] = m["hit"]; asyms[k] = m["asym"]
    return dict(hit=hits, asym=asyms)


def block_bootstrap_asym(df: pd.DataFrame, ret_col: str, block: int = BLOCK,
                         n_boot: int = N_BOOT, seed: int = 1) -> tuple[float, float]:
    """95% interval for asymmetry by block bootstrap of rows (per asset, sorted by date)."""
    rng = np.random.default_rng(seed)
    groups = []
    for a, g in df.groupby("asset", sort=False):
        g = g.sort_values("date")
        c = g["call"].to_numpy(float); r = g[ret_col].to_numpy(float)
        ok = np.isfinite(c) & np.isfinite(r)
        if ok.sum():
            groups.append((c[ok], r[ok]))
    if not groups:
        return (np.nan, np.nan)
    vals = []
    for _ in range(n_boot):
        cs, rs = [], []
        for c, r in groups:
            n = len(c); nb = int(np.ceil(n / block))
            starts = rng.integers(0, max(1, n - block + 1), size=nb)
            idx = np.concatenate([np.arange(s, min(s + block, n)) for s in starts])[:n]
            cs.append(c[idx]); rs.append(r[idx])
        vals.append(metrics(np.concatenate(cs), np.concatenate(rs))["asym"])
    vals = np.array(vals, float); vals = vals[np.isfinite(vals)]
    if len(vals) == 0:
        return (np.nan, np.nan)
    return (float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5)))


# =============================================================================
# 4. coverage and scoring
# =============================================================================
def coverage(rows: pd.DataFrame) -> dict:
    """Counts, reported BEFORE any metric (prereg §4)."""
    if rows.empty:
        return dict(report_dates=0, dates_with_docs=0, dates_with_call=0, by_asset={}, by_kind={})
    r1 = rows[rows["h"] == rows["h"].min()] if "h" in rows.columns else rows   # one row per (date, asset)
    by_kind = r1["kind"].value_counts().to_dict()
    by_asset = {}
    for a, g in r1.groupby("asset"):
        d = g["kind"].value_counts().to_dict()
        d["tier_counts"] = g.loc[g["kind"] == CALL, "tier"].dropna().astype(int).value_counts().sort_index().to_dict()
        by_asset[a] = d
    dates = r1.groupby("date")
    return dict(report_dates=int(r1["date"].nunique()),
                dates_with_docs=int((dates["n_docs"].max() > 0).sum()),
                dates_with_call=int((dates["kind"].apply(lambda s: (s == CALL).any())).sum()),
                by_kind={k: int(v) for k, v in by_kind.items()},
                by_asset=by_asset)


def score_cell(df: pd.DataFrame, ret_col: str, h: int, do_null: bool, n_perm: int, seed: int) -> dict:
    """One (horizon, ret_col) cell. Naive and non-overlap; test only on non-overlap, >= MIN_ROWS."""
    calls = df[(df["h"] == h) & (df["kind"] == CALL) & (df["status"] == "matured")]
    calls = calls[np.isfinite(calls[ret_col].to_numpy(float))]
    naive = metrics(calls["call"], calls[ret_col])
    no = nonoverlap(calls, h)
    non = metrics(no["call"], no[ret_col])
    cell = dict(h=h, ret=ret_col, naive=naive, nonoverlap=non, too_few=(non["n"] < MIN_ROWS))
    if cell["too_few"]:
        cell["note"] = f"too few to report ({non['n']} non-overlap rows; minimum {MIN_ROWS})"
        cell["nonoverlap"] = dict(n=non["n"])           # NO number printed below the minimum (§3.2)
        cell["naive"] = dict(n=naive["n"])
        return cell
    if do_null:
        nd = null_distribution(no, ret_col, block=BLOCK, n_perm=n_perm, seed=seed)
        p_hit = float((nd["hit"] >= non["hit"]).mean()) if len(nd["hit"]) else np.nan
        q95 = float(np.percentile(nd["hit"], 95)) if len(nd["hit"]) else np.nan
        lo, hi = block_bootstrap_asym(no, ret_col, seed=seed + 1)
        pass_hit = bool(non["hit"] > q95)
        pass_asym = bool(np.isfinite(non["asym"]) and non["asym"] > 1.0 and np.isfinite(lo) and lo > 1.0)
        cell.update(null_hit_q95=q95, p_hit=p_hit, asym_ci=(lo, hi),
                    pass_hit=pass_hit, pass_asym=pass_asym,
                    verdict=("PASS" if (pass_hit and pass_asym) else
                             "INCONCLUSIVE" if (pass_hit or pass_asym) else "FAIL"),
                    n_perm=n_perm, n_boot=N_BOOT, block=BLOCK)
    return cell


def breakdowns(df: pd.DataFrame, ret_col: str, h: int) -> dict:
    """Reported in full, tested in none (§6)."""
    calls = df[(df["h"] == h) & (df["kind"] == CALL) & (df["status"] == "matured")]
    out = {}
    for key in ("asset", "tier", "dominant_source", "regime"):
        if key not in calls.columns:
            continue
        d = {}
        for k, g in calls.groupby(key, dropna=True):
            no = nonoverlap(g, h)
            m = metrics(no["call"], no[ret_col])
            d[str(k)] = (dict(n=m["n"], note="too few") if m["n"] < MIN_ROWS
                         else dict(n=m["n"], hit=m["hit"], asym=m["asym"], mean_signed=m["mean_signed"]))
        out[key] = d
    return out


def score(df: pd.DataFrame, do_null: bool = True, n_perm: int = N_PERM, seed: int = 0) -> dict:
    res = dict(run=datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %z"),
               prereg="docs/prereg_report_scoreboard.md", primary_h=PRIMARY_H, horizons=list(HORIZONS),
               min_rows=MIN_ROWS, coverage=coverage(df), cells={}, breakdowns={})
    for h in HORIZONS:
        for ret_col in ("ret_primary", "ret_tradeable"):
            key = f"h{h}_{ret_col.split('_')[1]}"
            is_primary = (h == PRIMARY_H and ret_col == "ret_primary")
            res["cells"][key] = score_cell(df, ret_col, h, do_null and is_primary, n_perm, seed)
            res["cells"][key]["primary"] = is_primary
            if not is_primary and do_null:
                # secondary cells: numbers, no test, per §6
                res["cells"][key]["note_secondary"] = "reported, not tested"
    res["breakdowns"] = breakdowns(df, "ret_primary", PRIMARY_H)
    pc = res["cells"][f"h{PRIMARY_H}_primary"]
    res["verdict"] = pc.get("verdict", "too few to report")
    # tier expectation (§6.1): reported, not tested
    tb = res["breakdowns"].get("tier", {})
    if "1" in tb and "3" in tb and "hit" in tb["1"] and "hit" in tb["3"]:
        res["tier_expectation"] = ("holds" if tb["1"]["hit"] >= tb["3"]["hit"]
                                   else "REVERSED -- tiers are not grading; report, do not move thresholds")
    return res


# =============================================================================
# 5. rendering
# =============================================================================
def _f(x, pct=False, d=3):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "—"
    return f"{100*x:.1f}%" if pct else f"{x:.{d}f}"


def render_md(res: dict, tag: str = "forward") -> str:
    L = [f"# Report-level scoreboard — {tag}", "",
         f"*Generated {res['run']}. Registered in `{res['prereg']}`. Primary horizon h*={res['primary_h']}; "
         f"minimum {res['min_rows']} non-overlap rows before any figure is printed. Only the primary cell is tested; "
         f"every other cell and every breakdown is reported, not tested.*", "",
         "## Coverage — before any metric", ""]
    c = res["coverage"]
    L += [f"- report dates scored: **{c['report_dates']}**",
          f"- dates with ≥1 document: {c['dates_with_docs']}",
          f"- dates with ≥1 net view (a call): {c['dates_with_call']}",
          "- per (date, asset): " + ", ".join(f"{k} {v}" for k, v in sorted(c["by_kind"].items())) if c["by_kind"] else "- no rows", ""]
    if c["by_asset"]:
        L += ["| asset | call | no_document | abstain | divergence | zero_direction | tiers (1/2/3) |", "|---|---|---|---|---|---|---|"]
        for a, d in sorted(c["by_asset"].items()):
            t = d.get("tier_counts", {})
            L.append(f"| {a} | {d.get(CALL,0)} | {d.get(EXCL_NO_DOC,0)} | {d.get(EXCL_ABSTAIN,0)} | {d.get(EXCL_DIVERGE,0)} | {d.get(EXCL_ZERO,0)} | {t.get(1,0)}/{t.get(2,0)}/{t.get(3,0)} |")
        L.append("")
    L += [f"## Verdict (primary cell, h*={res['primary_h']}, close-to-close, non-overlap)", "",
          f"**{res['verdict']}**", ""]
    if "tier_expectation" in res:
        L += [f"Tier expectation (§6.1): {res['tier_expectation']}", ""]
    L += ["## Cells", "", "| cell | rows (naive / non-overlap) | hit-rate (naive / non-overlap) | asymmetry | mean signed | null q95 | p | asym 95% CI | verdict |",
          "|---|---|---|---|---|---|---|---|---|"]
    for key, cell in res["cells"].items():
        nv, no = cell["naive"], cell["nonoverlap"]
        star = " **(primary)**" if cell.get("primary") else ""
        if cell.get("too_few"):
            L.append(f"| {key}{star} | {nv['n']} / {no['n']} | too few to report | — | — | — | — | — | — |")
            continue
        L.append(f"| {key}{star} | {nv['n']} / {no['n']} | {_f(nv['hit'],True)} / {_f(no['hit'],True)} | "
                 f"{_f(no['asym'])}{' (no misses)' if no.get('no_misses') else ''} | {_f(no['mean_signed']*100, d=4)}% | "
                 f"{_f(cell.get('null_hit_q95'),True)} | {_f(cell.get('p_hit'),d=4)} | "
                 f"{('[' + _f(cell['asym_ci'][0]) + ', ' + _f(cell['asym_ci'][1]) + ']') if 'asym_ci' in cell else '—'} | "
                 f"{cell.get('verdict', cell.get('note_secondary','—'))} |")
    L.append("")
    if res["breakdowns"]:
        L += [f"## Breakdowns at h*={res['primary_h']} (close-to-close, non-overlap) — reported, not tested", ""]
        for key, d in res["breakdowns"].items():
            L += [f"### by {key}", "", "| value | n | hit-rate | asymmetry | mean signed |", "|---|---|---|---|---|"]
            for k, m in sorted(d.items()):
                if "hit" in m:
                    L.append(f"| {k} | {m['n']} | {_f(m['hit'],True)} | {_f(m['asym'])} | {_f(m['mean_signed']*100, d=4)}% |")
                else:
                    L.append(f"| {k} | {m['n']} | too few | — | — |")
            L.append("")
    return "\n".join(L)


# =============================================================================
# 6. real run: ledger maintenance (append-only) and price sources
# =============================================================================
def _refuse(t):
    raise RuntimeError(f"report_scoreboard does not fetch prices; {t} is not in the raw cache")


def load_prices_real(assets: list[str]):
    """closes from the processed returns panel (exact same estimand as the estimator);
    opens (and matching closes) from the raw yfinance cache for the tradeable column."""
    from src.analog_event import load_data
    _, rets = load_data()
    rets = rets[[a for a in assets if a in rets.columns]]
    closes = np.exp(rets.fillna(0).cumsum())          # price index whose log-diffs are rets exactly
    closes[rets.isna()] = np.nan
    sessions = pd.DatetimeIndex(rets.index)
    opens = None; closes_raw = None
    try:
        from src.data_io import cached_fetch
        o, c = {}, {}
        for a in assets:
            df = cached_fetch(source="yfinance", key=a, fetch_fn=lambda a=a: _refuse(a), force_refresh=False)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            adj = df["Adj Close"] if "Adj Close" in df.columns else df["Close"]
            ratio = (adj / df["Close"]).replace([np.inf, -np.inf], np.nan)
            o[a] = (df["Open"] * ratio); c[a] = adj
        opens = pd.DataFrame(o); closes_raw = pd.DataFrame(c)
        opens.index = pd.to_datetime(opens.index).tz_localize(None) if getattr(opens.index, "tz", None) is not None else pd.to_datetime(opens.index)
        closes_raw.index = opens.index
        opens = opens.reindex(sessions); closes_raw = closes_raw.reindex(sessions)
    except Exception as e:
        print(f"  WARNING: tradeable column unavailable -- opens could not be loaded from the raw cache "
              f"({type(e).__name__}: {str(e)[:100]}). Primary column unaffected.")
    return closes, opens, closes_raw, sessions


def update_ledger(report_dir: Path, ledger_path: Path) -> pd.DataFrame:
    """Append rows for new reports; mature pending rows; NEVER edit a matured row."""
    reports = load_reports(report_dir)
    new = rows_from_reports(reports)
    assets = sorted(new["asset"].unique()) if not new.empty else []
    old = pd.read_csv(ledger_path, parse_dates=["date"]) if ledger_path.exists() else pd.DataFrame(columns=LEDGER_COLS)
    for c in ("logged_at", "matured_at"):
        if c in old.columns:
            old[c] = old[c].astype(object)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    if new.empty and old.empty:
        return old
    if not assets:
        assets = sorted(old["asset"].unique())
    closes, opens, closes_raw, sessions = load_prices_real(assets)

    # rows not yet in the ledger
    have = set(zip(pd.to_datetime(old["date"]), old["asset"])) if not old.empty else set()
    add = new[[(d, a) not in have for d, a in zip(new["date"], new["asset"])]]
    fresh = realise(add, closes, None, sessions) if not add.empty else pd.DataFrame(columns=LEDGER_COLS)
    if not fresh.empty:
        fresh["logged_at"] = now
        # tradeable from raw prices, separately, so a raw-cache problem never touches the primary column
        if opens is not None:
            tr = realise(add, closes_raw, opens, sessions)
            fresh["ret_tradeable"] = tr["ret_tradeable"].to_numpy()
        fresh.loc[fresh["status"] == "matured", "matured_at"] = now
        fresh.loc[fresh["status"] != "matured", "ret_primary"] = np.nan   # pending rows carry no number

    # mature pending rows in the old ledger (only pending; matured rows are frozen)
    if not old.empty:
        pend = old["status"] != "matured"
        if pend.any():
            sub = old[pend].drop(columns=["h", "ret_primary", "ret_tradeable", "status", "logged_at", "matured_at"]).drop_duplicates(["date", "asset"])
            rp = realise(sub, closes, None, sessions).set_index(["date", "asset", "h"])
            rt = realise(sub, closes_raw, opens, sessions).set_index(["date", "asset", "h"]) if opens is not None else None
            for i in old[pend].index:
                k = (pd.Timestamp(old.at[i, "date"]), old.at[i, "asset"], int(old.at[i, "h"]))
                if k in rp.index and rp.at[k, "status"] == "matured":
                    old.at[i, "ret_primary"] = rp.at[k, "ret_primary"]
                    old.at[i, "ret_tradeable"] = (rt.at[k, "ret_tradeable"] if rt is not None and k in rt.index else np.nan)
                    old.at[i, "status"] = "matured"; old.at[i, "matured_at"] = now

    ledger = pd.concat([old, fresh], ignore_index=True) if not fresh.empty else old
    ledger = ledger[LEDGER_COLS]
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger.to_csv(ledger_path, index=False)
    n_new = len(fresh); n_mat = int((ledger["status"] == "matured").sum())
    print(f"  ledger: {len(ledger)} rows (+{n_new} new), {n_mat} matured, {len(ledger) - n_mat} pending -> {ledger_path}")
    return ledger


# =============================================================================
# 7. acceptance tests (prereg §12) -- synthetic ledgers only
# =============================================================================
def _synthetic(n_dates=300, assets=("A", "B", "C", "D", "E"), seed=0, h=PRIMARY_H,
               calls_from="random", ret_ar=0.0, call_runs=1):
    """Build a synthetic (date, asset, h) ledger in the real schema."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2020-01-01", periods=n_dates + 30)
    rows = []
    for a in assets:
        # returns: AR(1) with coefficient ret_ar, so T7 can make them persistent
        e = rng.normal(0, 0.01, size=len(dates)); r = np.empty(len(dates)); r[0] = e[0]
        for i in range(1, len(dates)):
            r[i] = ret_ar * r[i - 1] + e[i]
        if call_runs > 1:
            base = rng.choice([-1.0, 1.0], size=int(np.ceil(n_dates / call_runs)))
            c = np.repeat(base, call_runs)[:n_dates]
        else:
            c = rng.choice([-1.0, 1.0], size=n_dates)
        for i in range(n_dates):
            ret = float(r[i + 1:i + 1 + h].sum())            # close(t) -> close(t+h) in log terms
            call = (np.sign(ret) if calls_from == "perfect" else c[i])
            if calls_from == "perfect" and call == 0:
                call = 1.0
            rows.append(dict(date=dates[i], asset=a, h=h, kind=CALL, call=call, net_view=call * 0.5,
                             tier=int(rng.integers(1, 4)), ess=20.0, w=0.5, dominant_source="s", agreement="x",
                             regime=int(rng.integers(0, 4)), n_docs=1, estimate_horizon=h,
                             ret_primary=ret, ret_tradeable=ret, status="matured", logged_at="t", matured_at="t"))
    return pd.DataFrame(rows)[LEDGER_COLS]


def selftest(n_perm_fast=300, reps=200) -> str:
    out = []; ok_all = True

    def rec(name, ok, detail):
        nonlocal ok_all
        ok_all &= ok
        out.append(f"| {name} | {'PASS' if ok else 'FAIL'} | {detail} |")
        print(f"  {name}: {'PASS' if ok else 'FAIL'} -- {detail}")

    # T1 planted-perfect
    df = _synthetic(calls_from="perfect", seed=1)
    res = score(df, do_null=True, n_perm=n_perm_fast, seed=1)
    cell = res["cells"][f"h{PRIMARY_H}_primary"]
    rec("T1 planted-perfect",
        cell["nonoverlap"]["hit"] == 1.0 and cell["nonoverlap"]["no_misses"] and cell["p_hit"] < 0.001,
        f"hit {cell['nonoverlap']['hit']:.3f}, no_misses={cell['nonoverlap']['no_misses']}, p {cell['p_hit']:.4f} ({n_perm_fast} draws)")

    # T2 planted-shuffled: rejection rate at alpha=0.05 in [0.02, 0.08]
    rej = 0
    for k in range(reps):
        d = _synthetic(n_dates=120, seed=100 + k)
        c = score(d, do_null=True, n_perm=n_perm_fast, seed=100 + k)["cells"][f"h{PRIMARY_H}_primary"]
        rej += int(c["p_hit"] < ALPHA)
    rate = rej / reps
    rec("T2 planted-shuffled", 0.02 <= rate <= 0.08, f"rejection rate {rate:.3f} over {reps} reps ({n_perm_fast} draws each)")

    # T3 min-count: 29 non-overlap rows -> too few; 30 -> printed
    def _cell_with(n_no):
        d = _synthetic(n_dates=n_no * PRIMARY_H, assets=("A",), seed=7)   # exactly n_no non-overlap rows
        return score(d, do_null=False)["cells"][f"h{PRIMARY_H}_primary"]
    c29, c30 = _cell_with(29), _cell_with(30)
    rec("T3 min-count", c29["too_few"] and ("hit" not in c29["nonoverlap"]) and (not c30["too_few"]) and ("hit" in c30["nonoverlap"]),
        f"29 -> {c29.get('note','printed')}; 30 -> n={c30['nonoverlap']['n']}, hit printed")

    # T4 non-overlap sampler: 20 dates, every PRIMARY_H-th from the first (h=2 -> ten rows at dates 1,3,...,19; h=3 -> seven at 1,4,...,19)
    dates = pd.bdate_range("2021-01-01", periods=20)
    sel = nonoverlap_dates(dates, PRIMARY_H)
    hand = [dates[i] for i in range(0, 20, PRIMARY_H)]   # re-specified 2026-10-09: follows the registered horizon (was the h=3 list by hand)
    rec("T4 non-overlap sampler", sel == hand, f"selected {len(sel)} rows; positions {[dates.get_loc(d)+1 for d in sel]}")

    # T5 exclusions
    d = _synthetic(n_dates=40, assets=("A",), seed=3)
    d.loc[0, "kind"] = EXCL_ABSTAIN; d.loc[1, "kind"] = EXCL_DIVERGE; d.loc[2, "kind"] = EXCL_ZERO; d.loc[3, "kind"] = EXCL_NO_DOC
    d.loc[4, "ret_primary"] = 0.0                       # zero return: stays a call, counts as a MISS
    d.loc[[0, 1, 2, 3], "call"] = np.nan
    r = score(d, do_null=False)
    cov = r["coverage"]["by_kind"]; cell = r["cells"][f"h{PRIMARY_H}_primary"]
    m = metrics(d.loc[4:, "call"], d.loc[4:, "ret_primary"])
    rec("T5 exclusions",
        cov.get(EXCL_ABSTAIN) == 1 and cov.get(EXCL_DIVERGE) == 1 and cov.get(EXCL_ZERO) == 1 and cov.get(EXCL_NO_DOC) == 1
        and cell["naive"]["n"] == 36 and m["n_misses"] >= 1,
        f"coverage {cov}; naive rows {cell['naive']['n']} of 40; zero-return row scored as miss")

    # T6 two entries: constructed OHLC with overnight gap g on t+1
    sessions = pd.bdate_range("2022-01-03", periods=10)
    close = np.array([100, 101, 102, 103, 104, 105, 106, 107, 108, 109], float)
    opn = close.copy(); g = 0.02
    opn[1] = close[0] * np.exp(g)                        # open(t+1) = close(t) * e^g
    closes = pd.DataFrame({"A": close}, index=sessions); opens = pd.DataFrame({"A": opn}, index=sessions)
    calls = pd.DataFrame([dict(date=sessions[0], asset="A", kind=CALL, call=1.0, net_view=0.5, tier=1, ess=1, w=1,
                               dominant_source="s", agreement="x", regime=0, n_docs=1, estimate_horizon=3)])
    led = realise(calls, closes, opens, sessions, horizons=(3,))
    rp, rt = led.at[0, "ret_primary"], led.at[0, "ret_tradeable"]
    # primary = log(c3/c0); tradeable = log(c4/o1) = log(c4/c0) - g  =>  rp - rt = g - log(c4/c3)
    expect = g - np.log(close[4] / close[3])
    rec("T6 two entries", abs((rp - rt) - expect) < 1e-9, f"rp-rt = {rp-rt:.9f}, expected {expect:.9f}")

    # T7 block null widens vs free null when calls AND returns are persistent
    d = _synthetic(n_dates=240, seed=11, ret_ar=0.8, call_runs=5)
    calls7 = d[d["h"] == PRIMARY_H]                      # naive rows (overlapping), where persistence lives
    nb = null_distribution(calls7, "ret_primary", block=BLOCK, n_perm=n_perm_fast, seed=5)["hit"].std()
    nf = null_distribution(calls7, "ret_primary", block=1, n_perm=n_perm_fast, seed=5)["hit"].std()
    rec("T7 block null does something", nb >= nf, f"null sd block={nb:.4f} vs free={nf:.4f}")

    hdr = ["# Report scoreboard — acceptance tests (prereg §12)", "",
           f"*Run {datetime.now(timezone.utc).astimezone():%Y-%m-%d %H:%M %z}. Synthetic ledgers only; no real report used. "
           f"Fast settings: {n_perm_fast} permutation draws per test, {reps} replications for T2.*", "",
           "| test | result | detail |", "|---|---|---|"]
    md = "\n".join(hdr + out + ["", f"**{'ALL SEVEN PASS' if ok_all else 'NOT ALL PASSING -- record the failure in prereg §11 before any repair'}**", ""])
    SELFTEST_MD.parent.mkdir(parents=True, exist_ok=True)
    SELFTEST_MD.write_text(md)
    print(f"\n  -> {SELFTEST_MD}")
    return md


# =============================================================================
# 8. entry point
# =============================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--reports-dir", default=str(REPORT_DIR))
    ap.add_argument("--ledger", default=str(LEDGER))
    ap.add_argument("--out-json", default=str(OUT_JSON))
    ap.add_argument("--out-md", default=str(OUT_MD))
    ap.add_argument("--tag", default="forward")
    ap.add_argument("--n-perm", type=int, default=N_PERM)
    a = ap.parse_args()

    print("=" * 72); print("REPORT SCOREBOARD -- scores the decision report (prereg_report_scoreboard.md)"); print("=" * 72)
    if a.selftest:
        selftest(); return

    ledger = update_ledger(Path(a.reports_dir), Path(a.ledger))
    if ledger.empty:
        # Still write the artefact: an empty scoreboard that says so is the
        # correct daily output while reports are deferred (reads paused).
        ledger = pd.DataFrame(columns=LEDGER_COLS)
        print("  no reports on disk since WRITE_ONCE_FROM -- scoreboard written with zero coverage.")
    res = score(ledger, do_null=True, n_perm=a.n_perm)
    Path(a.out_json).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out_json).write_text(json.dumps(res, indent=2, default=str))
    Path(a.out_md).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out_md).write_text(render_md(res, tag=a.tag))
    print(f"  verdict: {res['verdict']}")
    print(f"  -> {a.out_md}\n  -> {a.out_json}")


if __name__ == "__main__":
    main()
