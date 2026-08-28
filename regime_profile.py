"""
regime_profile.py -- what is actually true inside each regime?

WHAT THIS IS, AND WHAT IT IS NOT
    It is DESCRIPTION. For each regime, the mean of every macro series in the
    panel, against that series' own full-panel mean. "Regime 2 has average VIX
    28 against a panel average of 17" is arithmetic on the clustering inputs.
    It cannot be wrong, only uninformative.

    It is NOT the claim that collapsed in CURRENT_STATE §15. That claim was
    regime-EVENT alignment -- that the regimes line up with external news
    events -- and it failed at p 0.32 on the extended panel. Describing a
    cluster by the variables that formed it is a different operation from
    validating it against something outside itself, and this file does only
    the first.

WHY IT MATTERS FOR THE PRODUCT
    "Market condition 3 of 4" tells a user nothing. "Elevated volatility,
    strong dollar, falling real yields" tells them where they are. The label
    is generated from the numbers, not chosen, so it cannot drift from what
    the regime actually contains.

HOW THE LABEL IS BUILT
    Each series is scored as its regime mean minus the panel mean, in panel
    standard deviations. Any series beyond +/-0.5 sd contributes a phrase; the
    two largest absolute deviations are used, in plain words. If nothing clears
    0.5 sd the regime is described as "close to typical", which is itself
    informative -- one regime usually is.

    The threshold 0.5 and the two-phrase cap are display choices, stated here,
    and they change no number anywhere in the pipeline.

Run:  python regime_profile.py
"""
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from src.analog_event import load_data, regime_labels_expanding
from src.data_io import load_config, PROCESSED_DIR

REPO = PROCESSED_DIR.parent
OUT_JSON = PROCESSED_DIR / "regime_profile.json"
OUT_MD = REPO / "docs" / "regime_profile.md"
SD = 0.5

# series -> (plain name, phrase when high, phrase when low)
PLAIN = {
    "VIXCLS": ("equity volatility", "elevated volatility", "calm markets"),
    "DTWEXBGS": ("the dollar", "a strong dollar", "a weak dollar"),
    "DGS10": ("10-year yield", "high long-term rates", "low long-term rates"),
    "DFII10": ("10-year real yield", "high real rates", "low or negative real rates"),
    "DGS2": ("2-year yield", "high short-term rates", "low short-term rates"),
    "T10Y2Y": ("the yield curve", "a steep curve", "a flat or inverted curve"),
    "EFFR": ("the policy rate", "a high policy rate", "a low policy rate"),
    "M2SL": ("money supply", "rapid money growth", "slow money growth"),
}


def find_macro(scores):
    """The raw macro panel, tried in the usual places. Falls back to whatever
    non-PC columns sit alongside the scores."""
    for name in ("macro_panel.parquet", "macro.parquet",
                 "processed_macro.parquet", "panel.parquet"):
        p = PROCESSED_DIR / name
        if p.exists():
            try:
                df = pd.read_parquet(p)
                cols = [c for c in df.columns if c in PLAIN]
                if cols:
                    return df[cols]
            except Exception:
                pass
    cols = [c for c in scores.columns if c in PLAIN]
    return scores[cols] if cols else None


def main():
    cfg = load_config()
    scores, _ = load_data()
    labels = regime_labels_expanding(scores, cfg)
    macro = find_macro(scores)
    if macro is None or macro.empty:
        raise SystemExit(
            "No raw macro series found. Looked for VIXCLS, DTWEXBGS, DGS10, "
            "DFII10, DGS2, T10Y2Y, EFFR, M2SL in processed/*.parquet and in "
            "the scores frame. Point find_macro() at the panel file.")

    macro = macro.loc[macro.index.intersection(scores.index)]
    lab = pd.Series(labels, index=scores.index).loc[macro.index]
    mu, sd = macro.mean(), macro.std()

    print("=" * 78)
    print("REGIME PROFILES -- description, not validation")
    print("=" * 78)
    print(f"  series used: {', '.join(macro.columns)}")
    print(f"  panel {len(macro)} sessions")

    out = {}
    for r in sorted(set(int(x) for x in lab if x >= 0)):
        sel = macro[lab == r]
        z = ((sel.mean() - mu) / sd).sort_values(key=abs, ascending=False)
        phrases = []
        for s, v in z.items():
            if abs(v) < SD or len(phrases) >= 2:
                continue
            nice, hi, lo = PLAIN[s]
            phrases.append(hi if v > 0 else lo)
        label = ", ".join(phrases).capitalize() if phrases else "Close to typical"
        share = 100 * len(sel) / len(macro)
        out[str(r)] = dict(label=label, sessions=int(len(sel)),
                           share_pct=round(share, 1),
                           z={k: round(float(v), 2) for k, v in z.items()},
                           means={k: round(float(v), 3)
                                  for k, v in sel.mean().items()})
        print(f"\n  Regime {r}  ({len(sel)} sessions, {share:.0f}% of the panel)")
        print(f"     LABEL: {label}")
        for s, v in z.items():
            nice = PLAIN[s][0]
            flag = "  <--" if abs(v) >= SD else ""
            print(f"       {nice:22} {sel[s].mean():9.2f}  "
                  f"({v:+.2f} sd vs panel){flag}")

    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    OUT_JSON.write_text(json.dumps(dict(run=ts, sd_threshold=SD,
                                        regimes=out), indent=2))
    L = ["# What each market condition actually contains", "",
         f"*Run {ts}. Description, not validation.*", "",
         "Each regime is described by the mean of every macro series inside it, "
         "against that series' own full-panel mean, in panel standard "
         "deviations. This is arithmetic on the variables that formed the "
         "clusters — it cannot be wrong, only uninformative. It is a different "
         "operation from the regime–event alignment claim that collapsed in "
         "`CURRENT_STATE` §15, which tested the regimes against something "
         "outside themselves and failed.", "",
         "| condition | label | sessions | share | strongest deviations |",
         "|---|---|---|---|---|"]
    for r, d in out.items():
        top = ", ".join(f"{PLAIN[k][0]} {v:+.2f}sd"
                        for k, v in list(d["z"].items())[:3])
        L.append(f"| {int(r)+1} of {len(out)} | **{d['label']}** | "
                 f"{d['sessions']} | {d['share_pct']}% | {top} |")
    L += ["", f"A series contributes a phrase when its regime mean sits more "
              f"than {SD} panel standard deviations from the panel mean; the "
              f"two largest contribute. Both are display choices and change no "
              f"number in the pipeline.", ""]
    OUT_MD.write_text("\n".join(L) + "\n")
    print(f"\n  -> {OUT_JSON}\n  -> {OUT_MD}")


if __name__ == "__main__":
    main()
