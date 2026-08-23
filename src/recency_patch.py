"""
recency_patch.py -- add the RECENCY KERNEL to analog_core, opt-in.

WHAT THIS RESTORES
    The 2026-08-18 design session LOCKED a two-axis analog weight:

        w_t = exp(-lambda*(T-t)) * exp(-||z_t - z_now||^2 / (2 sigma^2))
              \\_______________/   \\____________________________________/
               recency kernel              similarity kernel

    described as "similarity-dominant (tight sigma so only true analogs get
    weight; gentle recency decay breaks ties among them)". `analog_core._kw()`
    implements ONLY the similarity half. There is no lambda anywhere in the
    codebase; a 2008 analog and a 2024 analog at equal macro distance receive
    equal weight. The gap was found 2026-08-23, five days after the design was
    locked.

WHY IT IS OPT-IN AND NOT A GLOBAL CHANGE
    `config/models.yaml` is FROZEN pre-registration for the live forward test
    (ce18d34, 2026-08-17). Changing the weighting that model_1/2/3 use would
    silently alter a running pre-registered experiment. So:

      * `half_life_years` defaults to None  -> exp(0) = 1 -> IDENTICAL to
        current behaviour, bit for bit. Existing frozen models are untouched.
      * A model that wants recency weighting must declare `half_life_years` in
        its own spec. New entries only; never edit an existing one.

    lambda is derived from a HALF-LIFE, not set directly, because a half-life is
    something you can hold an economic opinion about ("analogs older than a
    decade are worth half as much") while a raw decay constant is not.

        lambda = ln(2) / half_life_years,  age measured in YEARS = sessions/252

PRE-REGISTRATION REQUIREMENT
    half_life_years is a free hyperparameter, and the project has a Sharpe of
    0.25-0.51 already on the table. Tuning it against that number is exactly how
    backtests get flattered. Before running the sweep, write down the half-life
    you believe on economic grounds and why; report every rung of the declared
    ladder regardless of outcome. Any improvement found by search is EXPLORATORY
    on data already seen.

Run:
    python -m src.recency_patch          # applies the patch, verifies invariance
"""
import re
from pathlib import Path

TARGET = Path("src/analog_core.py")

NEW_KW = '''def _kw(dist, spec, age_years=None):
    """Analog weight = similarity kernel x recency kernel.

    similarity: gaussian exp(-d^2/2s^2) or exponential exp(-d/s)
    recency:    exp(-lambda * age_years), lambda = ln(2)/half_life_years

    age_years is None, or spec has no half_life_years -> recency term is 1.0,
    which reproduces the pre-2026-08-23 behaviour EXACTLY. The frozen models in
    models.yaml carry no half_life_years and are therefore unaffected."""
    if spec["kernel"] == "exp":
        sim = np.exp(-dist / spec["sigma"])
    else:
        sim = np.exp(-(dist ** 2) / (2 * spec["sigma"] ** 2))
    hl = spec.get("half_life_years")
    if hl is None or age_years is None:
        return sim
    lam = np.log(2.0) / float(hl)
    return sim * np.exp(-lam * np.asarray(age_years, dtype=float))
'''


def main():
    if not TARGET.exists():
        raise SystemExit(f"{TARGET} not found -- run from the repo root")
    src = TARGET.read_text()
    if "half_life_years" in src:
        print("already patched -- nothing to do")
        return

    # 1. replace _kw
    m = re.search(r"def _kw\(dist, spec\):.*?(?=\ndef )", src, flags=re.S)
    if not m:
        raise SystemExit("could not locate _kw -- inspect analog_core.py by hand")
    src = src[:m.start()] + NEW_KW + "\n" + src[m.end():]

    # 2. default spec key (None = off)
    src = src.replace("topk=100, nbasket=5, min_analogs=20, min_cov=10)",
                      "topk=100, nbasket=5, min_analogs=20, min_cov=10,\n"
                      "               half_life_years=None)")

    # 3. pass age at every call site. Indentation differs between backtest()
    #    (8 spaces) and current_picks() (4), so match on the pattern rather than
    #    a fixed literal. cand are integer positions in the session index and
    #    pos is the as-of row, so age = (pos - cand) sessions -> /252 = years.
    pat = re.compile(
        r"^(?P<i>[ \t]*)dist = np\.linalg\.norm\(X\[cand\] - x_now, axis=1\)\n"
        r"(?P=i)w = _kw\(dist, spec\)", flags=re.M)
    n = len(pat.findall(src))
    if n < 2:
        raise SystemExit(f"expected >=2 weighting call sites, found {n} -- "
                         f"inspect analog_core.py by hand")
    src = pat.sub(lambda m: (f"{m.group('i')}dist = np.linalg.norm(X[cand] - x_now, axis=1)\n"
                             f"{m.group('i')}age = (pos - cand) / 252.0"
                             f"          # sessions -> years\n"
                             f"{m.group('i')}w = _kw(dist, spec, age)"), src)

    # 4. docstring
    src = src.replace(
        "    topk        number of nearest analogs to weight",
        "    half_life_years  recency half-life in YEARS. None (default) = no\n"
        "                decay, identical to pre-2026-08-23 behaviour. Restores\n"
        "                the 2026-08-18 locked design w = exp(-lam*age) * sim,\n"
        "                lam = ln(2)/half_life. OPT-IN: frozen models omit it.\n"
        "    topk        number of nearest analogs to weight")

    TARGET.write_text(src)
    print(f"patched {TARGET}: {n} call site(s) now pass analog age")

    # ---- invariance check: default spec must reproduce old weights exactly ---
    import importlib
    import numpy as np
    import src.analog_core as ac
    importlib.reload(ac)
    rng = np.random.default_rng(0)
    d = rng.random(500) * 3
    for kern in ("gaussian", "exp"):
        spec = dict(ac.DEFAULT); spec["kernel"] = kern
        old = (np.exp(-d / spec["sigma"]) if kern == "exp"
               else np.exp(-(d ** 2) / (2 * spec["sigma"] ** 2)))
        assert np.allclose(ac._kw(d, spec), old, atol=0, rtol=0), kern
        assert np.allclose(ac._kw(d, spec, np.full(500, 12.0)), old), kern + "+age"
    print("INVARIANCE OK: with half_life_years=None the weights are bit-identical")
    print("               to the previous implementation, with or without age.")

    spec = dict(ac.DEFAULT); spec["half_life_years"] = 10.0
    w0 = ac._kw(np.zeros(1), spec, np.array([0.0]))[0]
    w10 = ac._kw(np.zeros(1), spec, np.array([10.0]))[0]
    w20 = ac._kw(np.zeros(1), spec, np.array([20.0]))[0]
    print(f"DECAY OK: half_life=10y -> weight at 0y {w0:.3f}, "
          f"10y {w10:.3f}, 20y {w20:.3f}  (halves per decade)")
    assert abs(w10 / w0 - 0.5) < 1e-9 and abs(w20 / w0 - 0.25) < 1e-9
    print("\nNEXT: declare the half-life you believe BEFORE sweeping. Add new")
    print("entries to models.yaml -- never edit model_1/2/3, they are frozen.")


if __name__ == "__main__":
    main()
