"""
stress_axis.py -- data-driven identification of the risk-stress principal
component, so no script hard-codes a PC index.

Refitting the macro PCA on a different span renumbers and re-signs the
components. The macro stress regime was historically picked via 'PC2', but on
the 2006+ refit the VIX-loaded axis moved to PC3. This helper finds the stress
axis by economic meaning: the PC whose score is most correlated (in magnitude)
with VIX, oriented so higher = more stress.

    from src.stress_axis import find_stress_axis, stress_scores, stress_regime_id
"""
import numpy as np
import pandas as pd


def find_stress_axis(scores: pd.DataFrame, vix: pd.Series):
    """(column_name, sign, corr) of the PC most correlated with VIX.
    sign is +1/-1 so that sign*score increases with VIX (stress-up)."""
    common = scores.index.intersection(vix.dropna().index)
    if len(common) < 30:
        raise ValueError(f"too few overlapping days ({len(common)}) to locate the stress axis")
    S = scores.loc[common]
    v = vix.loc[common]
    corrs = {c: S[c].corr(v) for c in S.columns}
    col = max(corrs, key=lambda c: abs(corrs[c]))
    r = corrs[col]
    sign = 1.0 if r >= 0 else -1.0
    return col, sign, r


def stress_scores(scores: pd.DataFrame, vix: pd.Series) -> pd.Series:
    """1-D stress score (higher = more stress), oriented via VIX."""
    col, sign, _ = find_stress_axis(scores, vix)
    return sign * scores[col]


def stress_regime_id(labels, scores, panel_path="processed/macro_panel.parquet"):
    """Regime id whose mean stress-axis score is highest.

    Stress axis = the PC most correlated with VIX (data-driven), so this is
    robust to PCA renumbering. Replaces the old 'highest mean PC2' rule.
    Loads VIX from the macro panel to identify the axis.
    """
    panel = pd.read_parquet(panel_path)
    panel.index = pd.to_datetime(panel.index)
    vixcol = "VIXCLS" if "VIXCLS" in panel.columns else ("vix" if "vix" in panel.columns else None)
    if vixcol is None:
        raise SystemExit(f"no VIX column in panel: {list(panel.columns)}")
    col, sign, _ = find_stress_axis(scores, panel[vixcol])
    axis = sign * scores[col]
    means = {r: axis[labels == r].mean() for r in labels.unique()}
    return max(means, key=means.get)


def describe(scores: pd.DataFrame, vix: pd.Series) -> str:
    col, sign, r = find_stress_axis(scores, vix)
    orient = "as-is" if sign > 0 else "sign-flipped"
    return f"stress axis = {col} ({orient}), corr with VIX = {r:+.3f}"


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", default="processed/macro_pca_scores.parquet")
    ap.add_argument("--panel", default="processed/macro_panel.parquet")
    args = ap.parse_args()
    scores = pd.read_parquet(args.scores); scores.index = pd.to_datetime(scores.index)
    panel = pd.read_parquet(args.panel); panel.index = pd.to_datetime(panel.index)
    vixcol = "VIXCLS" if "VIXCLS" in panel.columns else ("vix" if "vix" in panel.columns else None)
    if vixcol is None:
        raise SystemExit(f"no VIX column in panel: {list(panel.columns)}")
    print("=" * 60)
    print("STRESS-AXIS IDENTIFICATION (data-driven)")
    print("=" * 60)
    print(f"scores columns: {list(scores.columns)}")
    common = scores.index.intersection(panel[vixcol].dropna().index)
    for c in scores.columns:
        print(f"  corr({c}, VIX) = {scores.loc[common, c].corr(panel.loc[common, vixcol]):+.3f}")
    print("-" * 60)
    print("  " + describe(scores, panel[vixcol]))
    print("=" * 60)
