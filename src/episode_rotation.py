"""
episode_rotation.py -- Problem 2 STAGE 2: lead-lag WITHIN event-triggered episodes.

This is the conditional merge (PROJECT_STATE, 2026-08-19) implemented:
an event detector segments time into EPISODES; chain logic runs INSIDE them.
The event names the focus SET and the WHEN -- price statistics determine the
sequence and timing within the episode. The unconditional estimand was closed
as a null on 2026-08-21; this engine measures the estimand that test was
structurally blind to.

TRIGGER ARMS (the engine is detector-agnostic)
    --trigger shock    sector-wide shock day: |z| >= Z of the equal-weight
                       chain return vs its trailing 60-session SD.
                       1999-2026 -> the POWERED arm (~60-90 episodes expected).
    --trigger stress   GDELT narrow stress-share z >= Z vs trailing 20-session
                       baseline excluding t (same definition as the Stage 1
                       pre-registration). Needs --gdelt <csv>. ~648 usable
                       sessions -> honest-about-power arm (~25-35 episodes).
    --trigger file     --dates <csv> with a 'date' column: the slot that
                       entity-level GDELT or SEC 8-K plugs into later.

DESIGN (registered before first run)
    * Episode = the EPLEN sessions starting the session AFTER the trigger.
      The trigger day itself is excluded: the gap is conceded (architecture
      doc §3) and, for the shock arm, including the day that defines the
      trigger would be circular.
    * De-clustering gap = EPLEN, so episodes never overlap. A later trigger
      inside a window is ABSORBED (rupture-as-censoring is a v2 refinement;
      the distribution of orders already captures variable order).
    * Residualization: per name, OLS beta on the leave-one-out sector factor,
      fit on the trailing BETA_WIN sessions ending the day BEFORE the trigger,
      frozen through the episode. No look-ahead; no 15-day betas.
    * Window integrity: an episode is kept only if every chain name has a
      return on every one of its EPLEN sessions.

STATISTICS
    [1] Pooled within-episode lead-lag: d_ij(k) at k = 1..LAGS (short lags --
        a 15-day episode cannot support K=10; this is the multi-scale fix),
        pooled across episodes without crossing boundaries. Reported per lag
        and as max over k per pair, Holm-corrected over the 10 pairs.
    [2] Order concentration: per episode, each name's HALF-MAX RESPONSE TIME
        (first session its |cumulative residual| reaches half its own episode
        peak -- parameter-free, always defined); ranking these gives a
        per-episode order. Statistic = mean pairwise Kendall tau-b across
        episode orders. High concentration = a repeatable sequence.

NULL (both statistics)
    Shuffle episodes INDEPENDENTLY PER NAME: each name keeps its real episode
    paths, but they are aligned against other names' paths from different
    episodes. Destroys cross-name within-episode alignment; preserves every
    path shape, each name's distribution, and the episode structure itself.

Run:
    python -m src.episode_rotation --trigger shock
    python -m src.episode_rotation --trigger stress --gdelt <combined_narrow.csv>
    python -m src.episode_rotation --trigger shock --out docs/episode_rotation_shock.md
"""
import argparse
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kendalltau

from src.data_io import load_config, PROCESSED_DIR

CHAIN = ["NVDA", "TSM", "ASML", "MU", "INTC"]


# --------------------------------------------------------------------------- #
# data + triggers
# --------------------------------------------------------------------------- #
def load_panel():
    df = pd.read_parquet(PROCESSED_DIR / "asset_returns.parquet")
    df.index = pd.to_datetime(df.index)
    df = df.sort_index().dropna(how="all")
    if np.nanmedian(np.abs(df.to_numpy())) > 0.5:
        print("  (input looks like PRICES -> converting to returns)")
        df = df.pct_change()
    return df


def load_chain_returns(chain, panel=None):
    df = load_panel() if panel is None else panel
    missing = [c for c in chain if c not in df.columns]
    if missing:
        raise SystemExit(f"missing tickers: {missing}\n"
                         f"available: {sorted(df.columns)}")
    return df[chain].dropna()


def trigger_shock(rets, z_thresh, proxy=None, proxy_name="eq-weight chain",
                  sign="both"):
    """Shock day: proxy return beyond z * its trailing 60-session SD.

    sign='both' fires on moves in either direction. That is correct when the
    hypothesised mechanism is SYMMETRIC (e.g. semis leading the capex cycle
    in both directions). It is WRONG when the mechanism is directional: if
    capital rotates one way on a selloff and the reverse on a rally, pooling
    both averages toward zero even when both effects are real.

    sign='down' / 'up' restricts to one direction. Use 'down' for
    flight-to-quality, which by construction only occurs on risk-off.

    For a chain within one asset CLASS the equal-weight mean is a sensible
    proxy. For a cross-asset basket it is NOT -- averaging TLT with SPY mixes
    negatively-correlated series into something with no economic meaning."""
    s = rets.mean(axis=1) if proxy is None else proxy.reindex(rets.index)
    sd = s.rolling(60).std().shift(1)
    z = s / sd
    if sign == "down":
        days = z.index[z <= -z_thresh]
    elif sign == "up":
        days = z.index[z >= z_thresh]
    else:
        days = z.index[np.abs(z) >= z_thresh]
    tag = {"both": f"|z|>={z_thresh}", "down": f"z<=-{z_thresh} (RISK-OFF only)",
           "up": f"z>=+{z_thresh} (risk-on only)"}[sign]
    return days, {"detector": f"{tag} of {proxy_name} vs trailing 60d SD"}


def trigger_stress(gdelt_path, rets_index, z_thresh):
    """GDELT narrow stress-share z-spike -- Stage 1 prereg definition:
    z of share vs trailing 20-session baseline, strictly excluding t."""
    g = pd.read_csv(gdelt_path)
    date_col = next((c for c in g.columns if "date" in c.lower()), g.columns[0])
    stress_col = next((c for c in g.columns if "stress" in c.lower()), None)
    total_col = next((c for c in g.columns
                      if "total" in c.lower() or "doc" in c.lower()), None)
    if stress_col is None or total_col is None:
        raise SystemExit(f"could not identify stress/total columns in "
                         f"{gdelt_path}; found {list(g.columns)}")
    print(f"  gdelt columns: date={date_col!r} stress={stress_col!r} "
          f"total={total_col!r}")

    # YYYYMMDD as an INTEGER is the common BigQuery export shape. Passing it to
    # to_datetime() unformatted makes pandas read it as NANOSECONDS SINCE EPOCH
    # -- every row silently becomes 1970-01-01, nothing matches a session, and
    # the run reports zero triggers rather than raising. Parse explicitly.
    raw_dates = g[date_col]
    if pd.api.types.is_numeric_dtype(raw_dates):
        parsed = pd.to_datetime(raw_dates.astype("Int64").astype(str),
                                format="%Y%m%d", errors="coerce")
    else:
        s = raw_dates.astype(str).str.strip()
        if s.str.fullmatch(r"\d{8}").all():
            parsed = pd.to_datetime(s, format="%Y%m%d", errors="coerce")
        else:
            parsed = pd.to_datetime(s, errors="coerce")
    if parsed.isna().any():
        raise SystemExit(f"{parsed.isna().sum()} unparseable dates in {gdelt_path}")
    if parsed.min().year < 1990:
        raise SystemExit(f"parsed dates start {parsed.min().date()} -- the date "
                         f"column was misread. Check {date_col!r} in {gdelt_path}.")
    g = g.assign(**{date_col: parsed}).set_index(date_col).sort_index()
    print(f"  gdelt coverage: {g.index.min().date()} -> {g.index.max().date()} "
          f"({len(g)} rows)")

    share = g[stress_col] / g[total_col]
    mu = share.rolling(20).mean().shift(1)
    sd = share.rolling(20).std().shift(1)
    z = (share - mu) / sd
    days = z.index[z >= z_thresh]
    on_session = days[days.isin(rets_index)]
    print(f"  z>={z_thresh} on {len(days)} calendar days; {len(on_session)} fall "
          f"on trading sessions ({len(days)-len(on_session)} on weekends/holidays)")
    if len(days) and not len(on_session):
        raise SystemExit("no trigger day matches a trading session -- the GDELT "
                         "dates and the return index do not overlap.")
    return on_session, {"detector": f"narrow stress-share z>={z_thresh} vs trailing "
                                    f"20-session baseline excl. t ({gdelt_path})"}


def trigger_file(path, rets_index):
    d = pd.read_csv(path)
    col = next((c for c in d.columns if "date" in c.lower()), d.columns[0])
    days = pd.DatetimeIndex(pd.to_datetime(d[col])).sort_values()
    days = days[days.isin(rets_index)]
    return days, {"detector": f"user-supplied dates ({path})"}


def decluster(days, sessions, gap):
    """Keep the first trigger of any cluster; absorb triggers within `gap`
    SESSIONS of a kept one. Non-overlap by construction when gap >= eplen."""
    pos = {d: i for i, d in enumerate(sessions)}
    kept, last = [], -10**9
    for d in days:
        i = pos.get(d)
        if i is None:
            continue
        if i - last >= gap:
            kept.append(d)
            last = i
    return kept


# --------------------------------------------------------------------------- #
# episodes
# --------------------------------------------------------------------------- #
def build_episodes(rets, triggers, eplen, beta_win, min_beta_obs, chain,
                   mode="loo", factor=None):
    """Returns tensor (E, eplen, N) of episode paths + meta.

    mode:
      'loo'    each name residualized on the equal-weight mean of the OTHERS.
               Correct when all names share ONE dominant factor (e.g. five
               semiconductors sharing a sector beta).
      'market' each name residualized on an EXPLICIT factor series (e.g. SPY).
               Correct for sector ETFs, which share market beta but where the
               leave-one-out mean of a handful of sectors is a poor proxy for it.
      'none'   raw returns, no residualization. Correct for CROSS-ASSET baskets:
               there is no shared factor to remove, and the rotation itself IS
               the raw flow (money out of bonds into equities = TLT down, SPY
               up). Residualizing would strip out the phenomenon.
    Betas are fit on the trailing beta_win sessions ending the day BEFORE the
    trigger and frozen through the episode -- no look-ahead, no 15-day betas."""
    sessions = rets.index
    pos = {d: i for i, d in enumerate(sessions)}
    R = rets.to_numpy()
    F = None if factor is None else factor.reindex(sessions).to_numpy()
    N = len(chain)
    paths, meta, dropped = [], [], {"short_data": 0, "short_beta": 0, "nan": 0}

    for t in triggers:
        i = pos[t]
        s, e = i + 1, i + 1 + eplen             # episode = sessions AFTER trigger
        if e > len(sessions):
            dropped["short_data"] += 1
            continue
        b0 = max(0, i - beta_win)
        if i - b0 < min_beta_obs:
            dropped["short_beta"] += 1
            continue
        seg = R[s:e]
        if np.isnan(seg).any() or np.isnan(R[b0:i]).any():
            dropped["nan"] += 1
            continue
        if mode == "market":
            if F is None:
                raise SystemExit("mode='market' needs a factor series")
            if np.isnan(F[b0:i]).any() or np.isnan(F[s:e]).any():
                dropped["nan"] += 1
                continue

        if mode == "none":
            resid = seg.copy()
        else:
            resid = np.empty((eplen, N))
            for n in range(N):
                if mode == "market":
                    f_fit, f_ep = F[b0:i], F[s:e]
                else:
                    others = [m for m in range(N) if m != n]
                    f_fit = R[b0:i, others].mean(axis=1)
                    f_ep = seg[:, others].mean(axis=1)
                A = np.vstack([f_fit, np.ones_like(f_fit)]).T
                beta, *_ = np.linalg.lstsq(A, R[b0:i, n], rcond=None)
                resid[:, n] = seg[:, n] - (beta[0] * f_ep + beta[1])
        paths.append(resid)
        meta.append(dict(trigger=t.date(), entry=sessions[s].date()))
    return np.array(paths), meta, dropped


def inject_lead(T, i, j, lag, strength, rng):
    """AUDIT: plant a known lead of `strength` from name i to name j at `lag`
    sessions, inside the REAL episode tensor. If the engine cannot recover a
    planted lead on the user's own data, its nulls are not trustworthy."""
    out = T.copy()
    out[:, lag:, j] = ((1 - strength) * T[:, lag:, j]
                       + strength * T[:, :-lag, i])
    return out


# --------------------------------------------------------------------------- #
# statistics
# --------------------------------------------------------------------------- #
def pooled_lead(T, k):
    """d_ij(k) pooled across episodes, never crossing an episode boundary.
    T: (E, L, N). Returns (N, N) matrix of corr(x_i[t], x_j[t+k]) - reverse."""
    E, L, N = T.shape
    X = T[:, :-k, :].reshape(E * (L - k), N)    # within-episode t
    Y = T[:, k:, :].reshape(E * (L - k), N)     # within-episode t+k
    Xc, Yc = X - X.mean(0), Y - Y.mean(0)
    sX, sY = X.std(0, ddof=1), Y.std(0, ddof=1)
    C = (Xc.T @ Yc / (len(X) - 1)) / np.outer(sX, sY)
    return C - C.T


def half_max_times(T):
    """(E, N) half-max response times: first session |cum resid| reaches half
    its own episode max. Parameter-free; always defined."""
    cum = np.abs(np.cumsum(T, axis=1))          # (E, L, N)
    half = 0.5 * cum.max(axis=1, keepdims=True)
    return (cum >= half).argmax(axis=1)         # first True along L


def _sign_matrix(times):
    """(E, N) response times -> (E, P) sign of each item-pair ordering."""
    E, N = times.shape
    cols = [np.sign(times[:, j] - times[:, i])
            for i, j in combinations(range(N), 2)]
    return np.stack(cols, axis=1).astype(float)


def order_concentration(times):
    """Mean pairwise Kendall tau-b across the E per-episode time-rankings.

    EXACT vectorized tau-b, not an approximation. For rankings of N items,
    tau_b(a,b) = (C - D) / sqrt(n_a * n_b), where C - D is the inner product
    of the two sign vectors over the N(N-1)/2 item pairs and n_a is a's count
    of non-tied item pairs. One (E x P) sign matrix and one E x E matrix
    product replace C(E,2) scipy calls -- the original implementation was
    O(E^2) scipy calls PER NULL ITERATION, which at E=203 and 2000 iterations
    is ~41 million calls (~an hour). This is ~2 seconds and bit-identical.
    Verified against scipy at runtime by order_selftest()."""
    S = _sign_matrix(times)
    nz = (S != 0).sum(axis=1).astype(float)       # non-tied item pairs per episode
    P = S @ S.T                                    # (C - D) for every episode pair
    denom = np.sqrt(np.outer(nz, nz))
    with np.errstate(invalid="ignore", divide="ignore"):
        tau = np.where(denom > 0, P / denom, np.nan)
    iu = np.triu_indices(len(times), k=1)
    return float(np.nanmean(tau[iu]))


def order_selftest(times, n_check=40):
    """Verify the vectorized tau-b against scipy on real data. Fails loud."""
    sub = times[:n_check]
    S = _sign_matrix(sub)
    nz = (S != 0).sum(axis=1).astype(float)
    P = S @ S.T
    for a, b in combinations(range(len(sub)), 2):
        ref, _ = kendalltau(sub[a], sub[b])
        d = np.sqrt(nz[a] * nz[b])
        mine = P[a, b] / d if d > 0 else np.nan
        if np.isnan(ref) != np.isnan(mine) or \
           (not np.isnan(ref) and abs(ref - mine) > 1e-12):
            raise SystemExit(f"SELF-TEST FAILED: vectorized tau-b {mine} != "
                             f"scipy {ref} on episode pair ({a},{b}). "
                             f"Refusing to report numbers.")
    print(f"  self-test OK: vectorized tau-b matches scipy on "
          f"{n_check*(n_check-1)//2} episode pairs")


def shuffle_names(T, rng):
    """Independent episode-shuffle per name: name n's paths come from a
    permuted episode order. Kills cross-name within-episode alignment only."""
    E, L, N = T.shape
    out = np.empty_like(T)
    for n in range(N):
        out[:, :, n] = T[rng.permutation(E), :, n]
    return out


def holm(pvals):
    p = np.asarray(pvals, float)
    idx = np.argsort(p)
    adj, running = np.empty(len(p)), 0.0
    for rank, i in enumerate(idx):
        running = max(running, (len(p) - rank) * p[i])
        adj[i] = min(1.0, running)
    return adj


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trigger", choices=["shock", "stress", "file"],
                    required=True)
    ap.add_argument("--gdelt", type=str, help="csv for --trigger stress")
    ap.add_argument("--dates", type=str, help="csv for --trigger file")
    ap.add_argument("--z", type=float, default=None,
                    help="threshold; default 2.0 (shock) / 1.5 (stress)")
    ap.add_argument("--eplen", type=int, default=15)
    ap.add_argument("--lags", type=int, default=3)
    ap.add_argument("--beta-win", type=int, default=250)
    ap.add_argument("--min-beta-obs", type=int, default=120)
    ap.add_argument("--iters", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--chain", type=str, default=",".join(CHAIN))
    ap.add_argument("--residualize", choices=["loo", "market", "none"],
                    default="loo",
                    help="loo: leave-one-out mean (one shared sector factor). "
                         "market: explicit --factor (sector ETFs). "
                         "none: raw returns (CROSS-ASSET; the flow is the signal)")
    ap.add_argument("--factor", type=str, default="SPY",
                    help="factor ticker for --residualize market")
    ap.add_argument("--shock-on", type=str, default=None,
                    help="ticker the shock detector runs on; default is the "
                         "eq-weight chain (wrong for cross-asset baskets)")
    ap.add_argument("--shock-sign", choices=["both", "down", "up"],
                    default="both",
                    help="direction of the shock trigger. 'down' for "
                         "flight-to-quality (directional mechanism); 'both' "
                         "when the mechanism is symmetric")
    ap.add_argument("--inject", type=str, default=None,
                    help="AUDIT: 'NVDA,TSM,1,0.5' plants a lead of the given "
                         "strength at the given lag in the REAL episodes")
    ap.add_argument("--out", type=str, default=None)
    args = ap.parse_args()

    cfg = load_config()
    seed = args.seed if args.seed is not None else int(cfg["project"]["random_seed"])
    rng = np.random.default_rng(seed)
    chain = [c.strip() for c in args.chain.split(",")]
    z = args.z if args.z is not None else (2.0 if args.trigger == "shock" else 1.5)
    log = []

    def say(s=""):
        print(s)
        log.append(s)

    panel = load_panel()
    rets = load_chain_returns(chain, panel)

    factor = None
    if args.residualize == "market":
        if args.factor not in panel.columns:
            raise SystemExit(f"--factor {args.factor} not in panel; "
                             f"available: {sorted(panel.columns)}")
        factor = panel[args.factor]

    if args.trigger == "shock":
        if args.shock_on:
            if args.shock_on not in panel.columns:
                raise SystemExit(f"--shock-on {args.shock_on} not in panel")
            raw, info = trigger_shock(rets, z, panel[args.shock_on],
                                      args.shock_on, args.shock_sign)
        else:
            raw, info = trigger_shock(rets, z, sign=args.shock_sign)
    elif args.trigger == "stress":
        if not args.gdelt:
            raise SystemExit("--trigger stress needs --gdelt <csv>")
        raw, info = trigger_stress(args.gdelt, rets.index, z)
    else:
        if not args.dates:
            raise SystemExit("--trigger file needs --dates <csv>")
        raw, info = trigger_file(args.dates, rets.index)

    kept = decluster(raw, rets.index, gap=args.eplen)
    T, meta, dropped = build_episodes(rets, kept, args.eplen, args.beta_win,
                                      args.min_beta_obs, chain,
                                      mode=args.residualize, factor=factor)

    injected = None
    if args.inject and len(T):
        a, b, lg, stg = args.inject.split(",")
        ia, ib = chain.index(a.strip()), chain.index(b.strip())
        T = inject_lead(T, ia, ib, int(lg), float(stg), rng)
        injected = f"{a.strip()} -> {b.strip()} at lag {lg}, strength {stg}"

    say("=" * 78)
    say("EPISODE-CONDITIONAL ROTATION -- Problem 2 Stage 2 (the conditional merge)")
    say("=" * 78)
    say(f"chain:     {', '.join(chain)}")
    say(f"window:    {rets.index[0].date()} -> {rets.index[-1].date()} "
        f"({len(rets)} sessions)")
    say(f"detector:  {info['detector']}")
    say(f"episode:   {args.eplen} sessions after trigger (trigger day EXCLUDED; "
        f"gap conceded)")
    rmode = {"loo": "leave-one-out sector mean",
             "market": f"explicit factor ({args.factor})",
             "none": "NONE -- raw returns (cross-asset: the flow is the signal)"}
    say(f"residual:  {rmode[args.residualize]}")
    say(f"beta:      trailing {args.beta_win} sessions frozen at trigger "
        f"(min {args.min_beta_obs})")
    if injected:
        say(f"** INJECTION AUDIT ACTIVE: planted {injected}. A working engine "
            f"MUST detect this. **")
    say(f"triggers:  {len(raw)} raw -> {len(kept)} after de-clustering "
        f"(gap {args.eplen}) -> {len(T)} episodes kept "
        f"(dropped: {dropped})")
    say(f"iters {args.iters} | seed {seed} | lags 1..{args.lags}")

    if len(T) < 4:
        say(f"\nONLY {len(T)} EPISODE(S) SURVIVED. No statistic can be computed. "
            f"Check the detector: raw triggers were {len(raw)}, de-clustered "
            f"{len(kept)}, kept {len(T)}. If raw is 0 the detector fired on "
            f"nothing; if kept collapsed, inspect the drop reasons above.")
        if args.out:
            pth = Path(args.out)
            pth.parent.mkdir(parents=True, exist_ok=True)
            pth.write_text(f"# Episode-conditional rotation -- {args.trigger} arm\n\n"
                           "```\n" + "\n".join(log) + "\n```\n")
            print(f"\n  written -> {pth}")
        return
    if len(T) < 10:
        say(f"\nFEWER THAN 10 EPISODES ({len(T)}). No statistic below carries "
            f"meaningful power; results are reported for the record only.")

    pairs = list(combinations(range(len(chain)), 2))

    # ---- [1] pooled within-episode lead-lag -------------------------------
    say(f"\n[1] POOLED WITHIN-EPISODE LEAD-LAG (k = 1..{args.lags})")
    D_k = [pooled_lead(T, k) for k in range(1, args.lags + 1)]
    obs_max = np.array([max(abs(D_k[k - 1][i, j]) for k in range(1, args.lags + 1))
                        for i, j in pairs])
    obs_sgn = np.array([D_k[int(np.argmax([abs(D_k[k][i, j])
                        for k in range(args.lags)]))][i, j] for i, j in pairs])

    null_max = np.empty((args.iters, len(pairs)))
    for t in range(args.iters):
        Ts = shuffle_names(T, rng)
        Dn = [pooled_lead(Ts, k) for k in range(1, args.lags + 1)]
        null_max[t] = [max(abs(Dn[k][i, j]) for k in range(args.lags))
                       for i, j in pairs]
    p_pair = [(np.sum(null_max[:, c] >= obs_max[c]) + 1) / (args.iters + 1)
              for c in range(len(pairs))]
    p_adj = holm(p_pair)

    say("      pair            max|d|   signed    p      p(Holm)")
    for c, (i, j) in enumerate(pairs):
        star = " *" if p_adj[c] < 0.05 else ""
        say(f"      {chain[i]:>5} -> {chain[j]:<5} {obs_max[c]:.4f}  "
            f"{obs_sgn[c]:+.4f}  {p_pair[c]:.4f}  {p_adj[c]:.4f}{star}")
    n_sig = int(np.sum(p_adj < 0.05))
    say(f"    {n_sig} of {len(pairs)} pairs significant after Holm.")
    say("    per-lag pooled profile (d_ij, upper triangle):")
    for k in range(1, args.lags + 1):
        vals = ", ".join(f"{chain[i]}->{chain[j]} {D_k[k-1][i,j]:+.3f}"
                         for i, j in pairs)
        say(f"      k={k}: {vals}")

    # ---- [2] order concentration ------------------------------------------
    say(f"\n[2] ORDER CONCENTRATION across {len(T)} episodes")
    times = half_max_times(T)
    order_selftest(times, n_check=min(40, len(times)))
    obs_conc = order_concentration(times)
    null_conc = np.empty(args.iters)
    for t in range(args.iters):
        null_conc[t] = order_concentration(half_max_times(shuffle_names(T, rng)))
    p_conc = (np.sum(null_conc >= obs_conc) + 1) / (args.iters + 1)
    say(f"    mean pairwise Kendall tau-b of per-episode orders = {obs_conc:+.4f}")
    say(f"    null: mean {null_conc.mean():+.4f}, SD {null_conc.std(ddof=1):.4f}")
    say(f"    p(concentration >= observed) = {p_conc:.4f}")
    say("    High concentration = the same sequence recurs across episodes,")
    say("    whatever that sequence is. This is the statistic the unconditional")
    say("    test was structurally unable to compute.")

    first = np.array(chain)[times.argmin(axis=1)]
    counts = pd.Series(first).value_counts()
    say("    first-mover counts (earliest half-max response per episode):")
    for nm, ct in counts.items():
        say(f"      {nm:5} {ct:3d}  ({ct/len(T):.0%})")

    # ---- reading ----------------------------------------------------------
    say("\n" + "=" * 78)
    say("READING")
    say(f"  Within-episode lead-lag [1]: {n_sig}/{len(pairs)} pairs after Holm.")
    say(f"  Order concentration     [2]: tau {obs_conc:+.3f}, p = {p_conc:.4f}.")
    say("")
    if p_conc < 0.05:
        say("  ORDER CONCENTRATION CLEARS ITS NULL at this rung. This is the")
        say("  primary statistic. CONFIRM ACROSS THE DECLARED EPLEN LADDER")
        say("  {10, 15, 20} before treating it as a result -- a single rung is")
        say("  one cell of a multi-rung grid, not a finding.")
    elif n_sig > 0:
        say(f"  {n_sig} pair(s) survive Holm WITHIN this rung, but order")
        say("  concentration does not clear its null. Holm was applied within")
        say("  the rung, NOT across the {10,15,20} ladder: 30 pair-tests total,")
        say("  so ~1.5 false positives are expected at alpha=0.05. Treat a lone")
        say("  pair as noise unless it holds with a consistent sign at adjacent")
        say("  rungs. NOT a detection.")
    else:
        say("  No episode-local structure under this detector. Scope: this arm's")
        say("  trigger and this chain. If the POWERED (shock) arm is null, the")
        say("  episode-local hypothesis loses its main support; a stress-arm")
        say("  null alone is underpowered and inconclusive by itself.")
    say("=" * 78)

    if args.out:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"# Episode-conditional rotation -- {args.trigger} arm\n\n"
                     "```\n" + "\n".join(log) + "\n```\n")
        print(f"\n  written -> {p}")


if __name__ == "__main__":
    main()
