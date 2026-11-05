"""sweep.py -- one engine for the founder's rule of 28 Oct: every fixed number in a test is a grid variable, the whole surface is
published, and the strongest cell is judged against the strongest cell the same search finds on data with no relationship.

The second half is what makes the first half usable. A wider grid finds a better best cell on noise by construction, so the
best cell's own p-value says nothing; the number that carries information is where the best cell sits in the distribution of
"best cell over the same grid" on null data (time-shifted or block-permuted). That is the best-of-sweep null the register has
used since T-A/T-G (23 Oct); this module makes it the default for every test, and lets an era axis sit in the grid so that
"the era in which the pattern is strongest" is searched and judged the same way.

    from src.sweep import grid, run, write_md
    cells = grid(h=[5, 7, 10, 13, 15, 20, 30], thr=[-0.04, -0.05, ..., -0.10])
    res = run(cells, stat=my_stat, data=my_data, null_gen=shift_null, n_null=200, seed=0, label="T-L5b grid")
    write_md(res, Path("docs/sweep_TL5b.md"))

  stat(data, cell) -> float            the statistic of one cell (larger = stronger); NaN when the cell is empty (n too small)
  null_gen(data, rng) -> data'         one draw of the null: the same data with the relationship destroyed (helpers below)
  res.surface                          a DataFrame: one row per cell, its statistic and n
  res.best, res.best_stat              the strongest cell and its statistic
  res.null_max                         the n_null values of max-over-grid on null draws
  res.p_family                         share of null draws whose best cell is at least as strong as the real best cell
  res.q95                              the 95th percentile of null_max -- the bar a cell must clear to "survive the sweep"
  res.survivors                        cells whose statistic clears q95 (reported; promotion still needs a forward test)
  res.local_p                          per cell: share of null draws in which THAT cell was at least as strong (descriptive)

Standing rule (prereg_factor_attribution §4, 23 Oct): the registered cell's verdict stands as recorded; a sweep survivor is promoted
to a forward test by dated amendment. Nothing here writes the register.

Null generators provided
  shift_null(data, rng, key, min_shift)   circular time-shift of data[key] (a Series/array aligned with the rest); destroys
                                          the contemporaneous link, keeps each series' own autocorrelation
  block_perm_null(data, rng, key, block)  permute data[key] in contiguous blocks
  date_null(...)                          for event tests: see era_liquidity.py -- random start dates drawn from the same pool
"""
from __future__ import annotations

import itertools
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd


def grid(**axes) -> list[dict]:
    """Every combination of the axes, as dicts. grid(h=[5, 10], thr=[-0.05]) -> [{'h': 5, 'thr': -0.05}, {'h': 10, 'thr': -0.05}]."""
    keys = list(axes)
    return [dict(zip(keys, vals)) for vals in itertools.product(*[list(axes[k]) for k in keys])]


@dataclass
class SweepResult:
    label: str
    surface: pd.DataFrame
    best: dict
    best_stat: float
    null_max: np.ndarray
    p_family: float
    q95: float
    survivors: list
    local_p: pd.Series
    n_null: int
    meta: dict = field(default_factory=dict)

    def to_json(self) -> dict:
        return dict(label=self.label, best=self.best, best_stat=self.best_stat, p_family=self.p_family, q95=self.q95, n_null=self.n_null,
                    survivors=self.survivors, null_max_quantiles={q: float(np.nanquantile(self.null_max, q)) for q in (0.5, 0.9, 0.95, 0.99)} if len(self.null_max) else {},
                    surface=json.loads(self.surface.to_json(orient="records")), meta=self.meta)


def _eval(cells, stat, data):
    out = []
    for c in cells:
        v = stat(data, c)
        if isinstance(v, tuple):          # (statistic, n) is accepted
            v, n = v
        else:
            n = np.nan
        out.append((v, n))
    return out


def run(cells: list[dict], stat: Callable, data, null_gen: Callable | None, n_null: int = 200, seed: int = 0, label: str = "",
        min_cells_valid: int = 1, meta: dict | None = None) -> SweepResult:
    vals = _eval(cells, stat, data)
    surface = pd.DataFrame(cells); surface["stat"] = [v for v, _ in vals]; surface["n"] = [n for _, n in vals]
    valid = surface["stat"].notna()
    if valid.sum() < min_cells_valid:
        raise ValueError(f"{label}: no valid cell (every cell NaN -- too few observations everywhere)")
    i_best = int(surface.loc[valid, "stat"].idxmax()); best = {k: cells[i_best][k] for k in cells[i_best]}; best_stat = float(surface.loc[i_best, "stat"])
    null_max = np.full(n_null, np.nan); hits = np.zeros(len(cells))
    if null_gen is not None and n_null > 0:
        rng = np.random.default_rng(seed)
        for k in range(n_null):
            d2 = null_gen(data, rng)
            v2 = np.array([v for v, _ in _eval(cells, stat, d2)], float)
            null_max[k] = np.nanmax(v2) if np.isfinite(v2).any() else np.nan
            hits += np.where(np.isfinite(v2) & valid.to_numpy(), v2 >= surface["stat"].to_numpy() - 1e-12, False)
        ok = np.isfinite(null_max)
        p_family = float((null_max[ok] >= best_stat - 1e-12).mean()) if ok.any() else np.nan
        q95 = float(np.nanquantile(null_max[ok], 0.95)) if ok.any() else np.nan
        local_p = pd.Series(hits / max(ok.sum(), 1), index=surface.index)
    else:
        p_family, q95, local_p = np.nan, np.nan, pd.Series(np.nan, index=surface.index)
    surface["local_p"] = local_p
    survivors = [dict(cells[i]) | {"stat": float(surface.loc[i, "stat"])} for i in surface.index if valid[i] and np.isfinite(q95) and surface.loc[i, "stat"] > q95]
    return SweepResult(label, surface, best, best_stat, null_max, p_family, q95, survivors, local_p, n_null, meta or {})


# ------------------------------------------------------------------------------------------------------------ null generators
def shift_null(key: str, min_shift: int = 60):
    """Circular shift of data[key] by a random offset >= min_shift. data is a dict of aligned arrays/Series (same length)."""
    def gen(data: dict, rng: np.random.Generator) -> dict:
        x = np.asarray(data[key]); n = len(x)
        s = int(rng.integers(min_shift, n - min_shift)) if n > 2 * min_shift else int(rng.integers(1, n))
        d = dict(data); d[key] = np.roll(x, s)
        if isinstance(data[key], pd.Series):
            d[key] = pd.Series(d[key], index=data[key].index)
        return d
    return gen


def block_perm_null(key: str, block: int = 20):
    """Permute data[key] in contiguous blocks (keeps within-block dependence)."""
    def gen(data: dict, rng: np.random.Generator) -> dict:
        x = np.asarray(data[key]); n = len(x)
        starts = np.arange(0, n, block); order = rng.permutation(len(starts))
        idx = np.concatenate([np.arange(starts[j], min(starts[j] + block, n)) for j in order])
        d = dict(data); d[key] = x[idx]
        if isinstance(data[key], pd.Series):
            d[key] = pd.Series(d[key], index=data[key].index)
        return d
    return gen


# ------------------------------------------------------------------------------------------------------------ output
def write_md(res: SweepResult, path: Path, axis_rows: str | None = None, axis_cols: str | None = None, fmt: str = "{:+.3f}", note: str = ""):
    """A surface table (two axes pivoted when named; otherwise the flat list), the best cell, the family p and the survivors."""
    L = [f"# Sweep — {res.label}", "",
         f"Best cell: `{res.best}` with statistic {fmt.format(res.best_stat)}; best-of-grid null over {res.n_null} draws: 95th percentile {fmt.format(res.q95) if np.isfinite(res.q95) else 'n/a'}, "
         f"**p_family = {res.p_family:.3f}**" if np.isfinite(res.p_family) else f"Best cell: `{res.best}` with statistic {fmt.format(res.best_stat)} (no null run)", ""]
    if note:
        L += [note, ""]
    s = res.surface
    if axis_rows and axis_cols and axis_rows in s.columns and axis_cols in s.columns:
        other = [c for c in s.columns if c not in (axis_rows, axis_cols, "stat", "n", "local_p")]
        groups = [((), s)] if not other else list(s.groupby(other))
        for key, g in groups:
            if other:
                L += ["### " + ", ".join(f"{k} = {v}" for k, v in zip(other, key if isinstance(key, tuple) else (key,))), ""]
            piv = g.pivot(index=axis_rows, columns=axis_cols, values="stat")
            L += ["| " + axis_rows + " \\ " + axis_cols + " | " + " | ".join(str(c) for c in piv.columns) + " |", "|---|" + "---|" * len(piv.columns)]
            for r, row in piv.iterrows():
                L.append(f"| {r} | " + " | ".join((fmt.format(v) if np.isfinite(v) else "·") + ("**" if (np.isfinite(v) and np.isfinite(res.q95) and v > res.q95) else "") for v in row) + " |")
            L.append("")
        L += ["Bold-marked (**) cells clear the best-of-sweep null's 95th percentile. Per-cell n and local p in the JSON.", ""]
    else:
        L += ["| " + " | ".join(c for c in s.columns) + " |", "|---|" * len(s.columns)]
        for _, row in s.iterrows():
            L.append("| " + " | ".join((fmt.format(v) if isinstance(v, float) and np.isfinite(v) else ("·" if isinstance(v, float) else str(v))) for v in row) + " |")
        L.append("")
    L += [f"Survivors (statistic above the null's 95th percentile): {len(res.survivors)}" + (" — " + "; ".join(str({k: v for k, v in c.items() if k != 'stat'}) + f" {fmt.format(c['stat'])}" for c in res.survivors[:12]) if res.survivors else ""), "",
          "The registered cell's verdict stands as recorded; a survivor is promoted to a forward test by dated amendment, never by this table."]
    path.write_text("\n".join(L) + "\n")
    path.with_suffix(".json").write_text(json.dumps(res.to_json(), indent=1, default=float))


# ------------------------------------------------------------------------------------------------------------ selftest
def selftest(seed: int = 0) -> bool:
    """Planted relationship in one cell of a 7 x 7 grid must be found with p_family < 0.05; pure noise must give p_family >= 0.05 most of the time."""
    rng = np.random.default_rng(seed); n = 1500
    x = rng.standard_normal(n); e = rng.standard_normal(n)
    y = np.zeros(n); y[10:] = 0.25 * x[:-10]; y += e        # y depends on x lagged 10
    data = dict(x=x, y=y)
    def stat(d, c):
        xx, yy = np.asarray(d["x"]), np.asarray(d["y"]); L = c["lag"]
        a, b = (xx[:-L], yy[L:]) if L > 0 else (xx, yy)
        if c["half"] == "first": a, b = a[: len(a) // 2], b[: len(b) // 2]
        elif c["half"] == "second": a, b = a[len(a) // 2:], b[len(b) // 2:]
        return float(np.corrcoef(a, b)[0, 1]), len(a)
    cells = grid(lag=[0, 2, 5, 8, 10, 12, 15], half=["all", "first", "second"])
    res = run(cells, stat, data, shift_null("x", 60), n_null=150, seed=1, label="selftest planted")
    ok1 = res.best["lag"] == 10 and res.p_family < 0.05
    y0 = rng.standard_normal(n)
    res0 = run(cells, stat, dict(x=x, y=y0), shift_null("x", 60), n_null=150, seed=2, label="selftest noise")
    ok2 = res0.p_family >= 0.05
    print(f"selftest planted: best {res.best}, stat {res.best_stat:+.3f}, q95 {res.q95:+.3f}, p_family {res.p_family:.3f} -> {'PASS' if ok1 else 'FAIL'}")
    print(f"selftest noise:   best {res0.best}, stat {res0.best_stat:+.3f}, q95 {res0.q95:+.3f}, p_family {res0.p_family:.3f} -> {'PASS' if ok2 else 'FAIL'} (the best noise cell looks 'significant' on its own; the family p says it is not)")
    return ok1 and ok2


if __name__ == "__main__":
    import sys
    sys.exit(0 if selftest() else 1)
