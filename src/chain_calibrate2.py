"""
Oil-shock chain, calibration round 2 (8 Oct). Thresholds read off the stage-1 list:
the two war-starts are separated from demand-driven oil rallies by the DOLLAR leg (>= +0.9%
over 5 sessions alongside oil >= +8%) and by RATES confirming within 5 sessions.

Candidates:
  W1: oil5 >= 8% & dxy5 >= 0.9%                                  (two-leg, day one)
  W2: W1 & DGS2 +10bp within 5 sessions after                    (three-leg, confirmed)
  W3: W2 & gold NOT above oil/4 over the same 5 sessions          (haven leg absent -- 2026 only, by construction)

For each: every firing since 2006 with what gold did after, and whether the two war-starts are in.
Writes docs/chain_calibration_round2.md.
"""
from datetime import datetime
from pathlib import Path
import numpy as np, pandas as pd

WARS = {"Ukraine 2022-03-01": ("2022-02-24", "2022-03-15"), "Iran 2026-03-03": ("2026-02-28", "2026-03-20")}


def main():
    rets = pd.read_parquet("processed/asset_returns.parquet"); rets.index = pd.to_datetime(rets.index); rets = rets.loc["2006-01-01":]
    from src.data_io import cached_fetch
    def fred(k):
        d = cached_fetch(source="fred", key=k, fetch_fn=lambda: (_ for _ in ()).throw(RuntimeError()), force_refresh=False)
        s = d.iloc[:, 0] if isinstance(d, pd.DataFrame) else d; s = pd.to_numeric(s, errors="coerce"); s.index = pd.to_datetime(s.index)
        return s.reindex(rets.index).ffill()
    dgs2, dxy = fred("DGS2"), fred("DTWEXBGS")
    o5 = rets["USO"].rolling(5).sum(); g5 = rets["GLD"].rolling(5).sum()
    dx5 = dxy / dxy.shift(5) - 1; d2_5 = (dgs2 - dgs2.shift(5)) * 100
    w1 = (o5 >= 0.08) & (dx5 >= 0.009)
    # rates confirm: DGS2 5-session change >= +10bp on any of the next 0..5 sessions
    conf = pd.Series([bool((d2_5.iloc[i:i + 6] >= 10).any()) for i in range(len(rets))], index=rets.index)
    w2 = w1 & conf
    w3 = w2 & (g5 < o5 / 4)
    L = ["# Oil-shock chain — calibration round 2", "", f"*Run {datetime.now():%Y-%m-%d %H:%M}. Thresholds read off the stage-1 list of 8 Oct: the war-starts are "
         "the entries where the dollar surged with oil. Nothing here is registered until the founder approves a rule; A2 is then re-run on it.*", ""]
    summary = []
    for name, mask in (("W1: oil ≥ +8%/5s & dollar ≥ +0.9%/5s", w1), ("W2: W1 & 2-year ≥ +10bp/5s within 5 sessions", w2), ("W3: W2 & gold lagging oil (haven absent)", w3)):
        starts = mask & ~mask.shift(1, fill_value=False); dates = list(starts[starts].index)
        L += [f"## {name}", "", "| fires | oil 5s | dollar 5s | 2-year 5s at fire | gold +20s | gold +60s | in a war window |", "|---|---|---|---|---|---|---|"]
        hits = {w: False for w in WARS}; outside = 0
        for d in dates:
            i = rets.index.get_loc(d)
            g20 = rets["GLD"].iloc[i + 1:i + 21].sum() if i + 21 < len(rets) else np.nan
            g60 = rets["GLD"].iloc[i + 1:i + 61].sum() if i + 61 < len(rets) else np.nan
            inw = [w for w, (a, b) in WARS.items() if pd.Timestamp(a) <= d <= pd.Timestamp(b)]
            for w in inw: hits[w] = True
            if not inw and not (pd.Timestamp("2026-03-20") < d):   # 2026 re-escalations after the start window are the same war; shown, not counted as false
                outside += 1
            tag = inw[0] if inw else ("same war, re-escalation" if d > pd.Timestamp("2026-03-20") else "—")
            L.append(f"| {d:%Y-%m-%d} | {o5.loc[d]:+.1%} | {dx5.loc[d]:+.2%} | {d2_5.loc[d]:+.0f} bp | {g20:+.1%} | {g60:+.1%} | {tag} |")
        both = all(hits.values())
        summary.append((name, both, outside, len(dates)))
        L.append("")
    L += ["## Summary", "", "| rule | both war-starts in | firings outside (excl. 2026 re-escalations) | total firings 2006–2026 | strict fit |", "|---|---|---|---|---|"]
    for name, both, out, n in summary:
        L.append(f"| {name} | {'yes' if both else 'NO'} | {out} | {n} | {'**yes**' if both and out == 0 else 'no'} |")
    out = Path("docs/chain_calibration_round2.md"); out.write_text("\n".join(L) + "\n"); print("\n".join(L)); print(f"\n  -> {out}")


if __name__ == "__main__":
    main()
