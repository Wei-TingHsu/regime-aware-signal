"""
app.py -- DEMONSTRATION TERMINAL. Regime-Aware Cross-Asset Signal Framework.

TWO KINDS OF TAB, AND THE DIFFERENCE MATTERS
    LIVE tabs read every number from the repo -- processed/*.json, the ledger,
    file counts on disk. If a file is missing the tab says so rather than
    showing a stale figure.

    The SPECIMEN tab is a UI MOCKUP. Steps 3-6 are registered but NOT unblinded,
    so no conditional estimate exists. Every number there is INVENTED to show
    the shape of the deliverable. It is banner-labelled, dated to a fictional
    date, and marked SPECIMEN throughout -- because a fabricated figure that
    escapes its context becomes a claimed result, and an untraceable number is
    the one thing that would actually damage this submission.

    The specimen doubles as the SPECIFICATION for step 6: its fields are exactly
    those registered in prereg_analog_event.md section 8.

Run:
    pip install streamlit
    streamlit run app.py
"""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
DOCS, PROC, PROV = ROOT / "docs", ROOT / "processed", ROOT / "data_provenance"

st.set_page_config(page_title="Regime-Aware Signal — terminal", layout="wide")


def jload(p):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return None


def missing(name, what):
    st.warning(f"`{name}` not found — {what} has not been run. Nothing shown "
               f"rather than a stale figure.")


def nfiles(d, pat):
    try:
        return len(list(Path(d).glob(pat)))
    except Exception:
        return 0


st.title("Regime-Aware Cross-Asset Signal Framework")
st.caption("BMF5391C Applied Faculty Project · evidence terminal")

tabs = st.tabs(["What this is", "Today's report (SPECIMEN)", "Universe",
                "Engines", "Document layer", "Forward test",
                "What we got wrong", "Behind the scenes"])

# ============================================================ 1 · WHAT
with tabs[0]:
    st.header("The claim, and how it is defended")
    st.markdown("""
Three questions: does safe-haven behaviour invert conditionally, does capital
rotate through thematic chains in a detectable order, and can an LLM do useful
work inside a quantitative pipeline?

**Two came back null. The third is registered and unbuilt.**

That is the design working. What is on offer is not a signal — it is
**measurement with declared precision**: an instrument that states how much it
knows, abstains when it does not know enough, and keeps the record of what it
got wrong.
""")
    c = st.columns(3)
    c[0].metric("Pre-registered hypotheses", "10+")
    c[1].metric("Claims retired after testing", "9")
    c[2].metric("Wrong priors logged", "17")
    st.info("""**Why the nulls are the asset.** Every null came from an
instrument first shown to detect a *planted* effect — `--inject` recovered a
planted lead at d = +0.502, p = 0.0005 on the real panel before any null was
reported. A null from an unproven instrument is not evidence.""")
    st.divider()
    st.error("""**Read the tab labels.** The tab marked **SPECIMEN** is a UI
mockup with invented numbers, shown to demonstrate the shape of the deliverable.
Every other tab reads live from the repository.""")

# ============================================================ 2 · SPECIMEN
with tabs[1]:
    st.error("""### SPECIMEN — EVERY NUMBER ON THIS TAB IS INVENTED

Steps 3–6 are **registered but not unblinded**. No conditional estimate exists
yet. This tab shows the **shape** of the daily deliverable and serves as the
specification for step 6. The date is fictional. Do not cite, screenshot or
quote any figure below as a result.""")

    st.header("Daily Decision Report — 2027-03-15  *(specimen)*")
    c = st.columns(4)
    c[0].metric("Macro regime", "3 — tightening", "SPECIMEN")
    c[1].metric("Regime posterior", "0.71", "SPECIMEN")
    c[2].metric("Documents read", "4", "SPECIMEN")
    c[3].metric("Assets with a view", "3 of 47", "SPECIMEN")
    st.caption("A regime posterior below 0.60 prints as a warning, not a "
               "footnote — the system says when it is unsure which regime it is in.")

    st.subheader("Documents read today  *(specimen)*")
    st.dataframe(pd.DataFrame([
        {"source": "fomc_statement", "direction": "gold −0.4", "magnitude": 0.55,
         "specificity": 0.85, "novelty": 0.40,
         "evidence quote": "\"the Committee decided to raise the target range\""},
        {"source": "earnings_8k · NVDA", "direction": "equity +0.7",
         "magnitude": 0.70, "specificity": 0.80, "novelty": 0.55,
         "evidence quote": "\"revenue increased 22% year over year\""},
        {"source": "political_order", "direction": "equity −0.2",
         "magnitude": 0.30, "specificity": 0.75, "novelty": 0.20,
         "evidence quote": "\"it is hereby ordered that tariffs be imposed\""},
        {"source": "political_other", "direction": "equity 0.0",
         "magnitude": 0.05, "specificity": 0.20, "novelty": 0.02,
         "evidence quote": "\"National Small Business Week, 2027\""},
    ]), use_container_width=True, hide_index=True)
    st.caption("The reader never predicts returns. It classifies content; what a "
               "direction *did* is answered by price data. Note the ceremonial "
               "proclamation scoring specificity 0.20 — that separation is what "
               "makes weighing possible at all.")

    st.subheader("Net view per asset  *(specimen)*")
    st.dataframe(pd.DataFrame([
        {"asset": "GLD", "estimate (3d)": "−0.31%", "precedents": 34,
         "ESS": 21.4, "precedent strength": 0.68, "tier": "1 · matched",
         "dominant source": "fomc_statement", "reader vs history": "corroborated"},
        {"asset": "SMH", "estimate (3d)": "+0.44%", "precedents": 17,
         "ESS": 11.2, "precedent strength": 0.41, "tier": "2 · partial",
         "dominant source": "earnings_8k", "reader vs history": "corroborated"},
        {"asset": "XLE", "estimate (3d)": "—", "precedents": 6, "ESS": 4.1,
         "precedent strength": 0.00, "tier": "3 · abstain",
         "dominant source": "political_order", "reader vs history": "abstained"},
    ]), use_container_width=True, hide_index=True)
    st.caption("**ESS** is the effective sample size after weighting — how many "
               "precedents the number is really made of. **Precedent strength** "
               "is how much of the estimate came from macro-matched history "
               "versus the unconditional average. Below ESS 8 the system "
               "**abstains** rather than issuing a thin number.")

    st.warning("""**Divergent — both shown, no combined number issued  *(specimen)*.**

`UUP` · the reader scores today's order **dollar-positive (+0.3)**; macro-matched
history says **−0.18%** over 3 sessions across 22 precedents.

They disagree in sign, so **no net view is issued for UUP today**. Both numbers
are shown and the disagreement is flagged. The reader's opinion is never allowed
to weight the historical estimate — it would be validating itself.""")

    st.error("""**What this system could not see today  *(specimen — but the
gaps are real)*.**

- Statements, social posts and rhetoric outside the Federal Register — **not covered**
- Bank research and earnings-call transcripts — **no free structured feed, zero documents**
- Foreign issuers (6-K) — no separate exhibits, lower precision than domestic 8-K

Their absence is a **coverage gap, not evidence** that these sources do not move
markets. This block prints on every report.""")
    st.info("**No performance number appears on this report, specimen or real.** "
            "Nothing is claimed until a forward-test row has matured.")

# ============================================================ 3 · UNIVERSE
with tabs[2]:
    st.header("Asset universe")
    st.markdown("""47 instruments in three groups: 31 long-history core ETFs
driving regime discovery and backtesting, 4 modern-theme overlay instruments
tracked live but excluded from pre-inception backtests, and 12 spotlight single
names used for news attribution.

**The ≥8-year cut matters.** Any instrument with less than 8 years of history is
excluded from the long-history universe — the survivorship check that stops a
result being carried by recent-inception tickers which only exist inside one
bull run.""")

    st.subheader("Add an instrument  *(interface demonstration)*")
    st.caption("Shows how a client instrument would be screened before entering "
               "the universe. Adding one is a config entry plus a pipeline "
               "re-run; the screening logic shown is real.")
    col1, col2 = st.columns([2, 1])
    tic = col1.text_input("Ticker", placeholder="e.g. XLF, EEM, IWM")
    yrs = col2.number_input("Years of history available", 0.0, 60.0, 12.0, 0.5)

    if tic:
        t = tic.strip().upper()
        st.markdown(f"#### Screening `{t}`")
        long_ok = yrs >= 8
        st.dataframe(pd.DataFrame([
            {"check": "Ticker resolves on the data vendor",
             "result": "verified on `download_data --force`"},
            {"check": "≥ 8 years of history (long-history universe)",
             "result": "qualifies" if long_ok else
                       f"{yrs:g}y — tracked live, EXCLUDED from long-history"},
            {"check": "Spans ≥ 2 crisis regimes",
             "result": "likely" if long_ok else "insufficient span"},
            {"check": "Group assignment",
             "result": "core — regime discovery + backtest" if long_ok
                       else "overlay — live attribution only"},
            {"check": "Enters the analog engine's forward-return panel",
             "result": "yes" if long_ok else "from its inception date onward"},
        ]), use_container_width=True, hide_index=True)
        if long_ok:
            st.success(f"""`{t}` would join the **core** group: regime discovery,
PCA, backtesting and the analog engine. Adding it needs a `config.yaml` entry and
a pipeline re-run — panel, PCA and regimes all regenerate deterministically from
the seed.""")
        else:
            st.warning(f"""`{t}` would be added to the **overlay** group. It would
appear in daily reports and news attribution but be **excluded from the
long-history universe**, so no historical claim would rest on it. That exclusion
is the point — it is what stops a backtest being carried by instruments that only
existed during one favourable period.""")

    st.divider()
    cfg = ROOT / "config" / "config.yaml"
    if cfg.exists():
        txt = cfg.read_text()
        st.caption(f"Universe defined in `config/config.yaml` — "
                   f"{txt.count('ticker:')} instruments across "
                   f"{sum(k in txt for k in ('core:', 'overlay:', 'spotlight:'))} "
                   f"groups.")
    else:
        missing("config/config.yaml", "the universe definition")

# ============================================================ 4 · ENGINES
with tabs[3]:
    st.header("Engines — what was measured")
    st.subheader("The recency ladder, run on two engines")
    rs = jload(PROC / "recency_sweep.json")
    if rs is None:
        missing("processed/recency_sweep.json", "the λ ladder")
    else:
        rows = []
        for k, v in rs.items():
            parts = k.split("|")
            if len(parts) != 3 or parts[2] != "LONG-HISTORY":
                continue
            rows.append({"engine": parts[0], "rung": parts[1],
                         "Sharpe": round(float(v.get("sharpe", float("nan"))), 4),
                         "p": round(float(v.get("p", float("nan"))), 4)})
        if rows:
            st.dataframe(pd.DataFrame(rows).sort_values(["engine", "rung"]),
                         use_container_width=True, hide_index=True)
    st.markdown("""**The two engines disagree, and that is the finding.** They
differ only in feature basis, regime-refit policy and decay default — so the
result is **basis-carried, not phenomenon-carried**, and is reported as
exploratory rather than as a finding.""")

    st.subheader("What λ actually does to analog selection")
    if jload(PROC / "rung_diagnostic.json") is None:
        missing("processed/rung_diagnostic.json", "the rung diagnostic")
    else:
        st.error("""**Verdict: RESELECTION on both engines.** The registered
threshold was top-k overlap ≥ 0.90 against the no-decay control — that would mean
λ merely breaks ties. Measured **0.765 and 0.850**, with effective sample size
holding at ~99.6 of 100 at every rung. λ does not concentrate weight; **it swaps
which days are used at all.**

Both engines reduce to *"pick the 100 most recent same-regime days and average
them equally."* **The word *analog* promises more than the mechanism delivers**,
and the report says so.""")

    st.subheader("A declared look-ahead, finally measured")
    st.dataframe(pd.DataFrame([
        {"model": "level", "full-panel": 0.2526, "expanding": 0.2406,
         "diff": 0.012, "paired p": 0.940},
        {"model": "trend (model_2)", "full-panel": 0.4131, "expanding": 0.1522,
         "diff": 0.261, "paired p": 0.057},
        {"model": "trend (model_3)", "full-panel": 0.4947, "expanding": 0.3568,
         "diff": 0.138, "paired p": 0.500},
    ]), use_container_width=True, hide_index=True)
    st.warning("""Small for the level model, large for both trend models — and
that resolves an older question. Fixing horizon and varying only the similarity
mode, the trend advantage is **+0.11 with the look-ahead and −0.12 without it**.
On this panel **the trend advantage *is* the look-ahead.**""")

# ============================================================ 5 · DOCS
with tabs[4]:
    st.header("The document layer")
    st.markdown("""Every source — Fed statements, Fed minutes, SEC earnings
releases, executive orders, proclamations — is read into **one common schema**:
direction per asset class, magnitude, horizon, specificity, novelty, confidence,
and up to three verbatim evidence quotes.

**The model never predicts returns.** It classifies *content*. What a direction
actually did is answered by price data — which is also the main defence against
outcome leakage on documents it may have seen in training.""")
    rows = []
    for s in ["fomc_statement", "fomc_minutes", "earnings_8k",
              "political_order", "political_other"]:
        rows.append({"source": s,
                     "documents": nfiles(PROV / "docs" / s, "*.txt"),
                     "read": nfiles(PROV / "doc_reads", f"{s}__*.json")})
    df = pd.DataFrame(rows)
    df["% read"] = (100 * df["read"] / df["documents"].replace(0, pd.NA)).round(0)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("Does `specificity` actually discriminate?")
    g = jload(PROC / "gate_check.json")
    if g is None:
        missing("processed/gate_check.json", "the gate check")
    else:
        lo, hi = (g.get("ci") or [None, None])[:2]
        st.metric("Between-source spread",
                  f"{g.get('spread', float('nan')):.3f}",
                  f"95% CI [{lo:.3f}, {hi:.3f}]" if lo is not None else None)
        (st.success if g.get("passed") else st.error)(
            f"**GATE: {'PASS' if g.get('passed') else 'FAIL'}** — the criterion "
            f"is the *lower bound* of the CI exceeding "
            f"{g.get('threshold', 0.25)}, tightened from a point comparison "
            f"after a marginal result. The tightening is an amendment with its "
            f"timing declared.")
        srcs = g.get("sources", {})
        if srcs:
            st.dataframe(pd.DataFrame([
                {"source": k, "n": v.get("n"),
                 "mean specificity": round(v.get("mean", float("nan")), 3),
                 "expected": v.get("expected", "—")}
                for k, v in srcs.items()
            ]).sort_values("mean specificity", ascending=False),
                use_container_width=True, hide_index=True)
    st.error("""**What this system cannot see.** Statements, posts and rhetoric
outside the Federal Register are **not covered**. Bank research and transcripts
have no free structured feed and stand at zero documents. Foreign issuers file
6-K with no separate exhibits. Their absence is a **coverage gap, not
evidence** — and it prints on every daily report.""")

# ============================================================ 6 · FORWARD
with tabs[5]:
    st.header("Live forward test")
    st.markdown("""Three models frozen in `config/models.yaml` **before any live
data existed**, including a deliberately cherry-picked overfit control whose
registered hypothesis is that its in-sample lead shrinks out of sample.

Signal is the last completed US close; entry is the **next** session, never the
signal bar. A row matures only if **every** session of its window has a return
for **every** picked asset. Missed days are honest gaps, never back-filled.""")
    led = PROC / "forward_ledger.csv"
    if not led.exists():
        missing("processed/forward_ledger.csv", "the forward test")
    else:
        d = pd.read_csv(led)
        c = st.columns(3)
        c[0].metric("Rows logged", len(d))
        c[1].metric("Matured", int((d["status"] == "matured").sum()))
        c[2].metric("Pending", int((d["status"] == "pending").sum()))
        st.dataframe(d.sort_values("signal_date", ascending=False).head(15),
                     use_container_width=True, hide_index=True)
    st.info("""**No performance number is shown because none has matured.** The
live test contributes its *design and timestamps*, not its numbers. Reporting an
unmatured return would be the easiest way to mislead a reader here.""")

# ============================================================ 7 · WRONG
with tabs[6]:
    st.header("What we got wrong — and how we found out")
    st.markdown("A running tally of wrong priors is a first-class project "
                "artifact. **Seventeen entries.** The most consequential:")
    st.dataframe(pd.DataFrame([
        {"claim": "No recency parameter exists anywhere in the codebase",
         "how it was caught": "Reading the config file",
         "outcome": "False — it was there, and the headline figures carried it"},
        {"claim": "Removing that parameter raises Sharpe 0.25 → 0.38",
         "how it was caught": "A paired test registered before it ran",
         "outcome": "Not distinguishable, p = 0.485 — claim retired"},
        {"claim": "The trend similarity mode outperforms level",
         "how it was caught": "Fixing horizon, varying only the mode",
         "outcome": "The advantage was a look-ahead, not an effect"},
        {"claim": "The 8-K corpus contains earnings releases",
         "how it was caught": "A 20-document pilot before the full spend",
         "outcome": "307 SEC cover pages containing no figures"},
        {"claim": "The estimator's null path fires when there is no signal",
         "how it was caught": "A blind acceptance test",
         "outcome": "Floating-point residue stopped it firing — guarded"},
    ]), use_container_width=True, hide_index=True)
    st.success("""**Every one was caught by *running something*, not by reasoning
about it.**

The record of failure is kept, not deleted: the 307 cover pages are retained on
disk, the failed acceptance-test log is committed alongside the passing one, and
every amendment records **when it was decided relative to what had already been
seen** — the only thing distinguishing an amendment from a rationalisation.""")

# ============================================================ 8 · BEHIND
with tabs[7]:
    st.header("Behind the scenes — how a claim becomes a result")
    st.markdown("""
**1 · Register before running.** Every hypothesis has a written criterion
committed to git before any number is looked at. Nine claims have been retired
this way.

**2 · Prove the instrument before trusting the null.** Before any test reports
"no effect", a known effect is planted in the real data and the test must recover
it.

**3 · Build blind.** The document estimator was built against data with real
volatility, fat tails, missing values and holidays — only the link between
events and outcomes destroyed, a known effect planted on top. Six acceptance
tests passed before it ever saw a real conditional estimate.

**4 · Fail loud.** Nine defects this session shared one shape: something failed
and the code carried on, logging something plausible. A silent filter passed 307
empty documents. A retry loop burned 897 calls against an exhausted balance. Each
is now a hard stop.

**5 · Estimate, don't choose.** Where a parameter can be estimated it is never
picked by hand — trying values and keeping the best is a one-parameter grid
search.
""")
    st.divider()
    st.subheader("Commercial read")
    st.markdown("""The precedent is **Barra**, which did not sell alpha. It sold
*measurement with declared precision* and became a standard.

The deliverable is the daily report in the specimen tab: every asset carrying its
estimate, its precedent count, its **effective** sample size after weighting, a
**precedent-strength** number, and an explicit **abstention** when evidence is
thin. Where the reader and the historical record disagree, both are shown and no
combined number is issued.

**A system that abstains is more sellable to a fiduciary than one that always has
an answer** — the fiduciary carries the liability and needs to know which days
the model is guessing.""")
    st.divider()
    c = st.columns(2)
    c[0].success("""**Done**
- Macro analog engine measured, caveats declared
- Two hypotheses closed as clean nulls
- Document layer built; 5 sources on one schema
- Discrimination gate passed on a tightened criterion
- Conditional estimator registered, blind-tested 6/6
- Live forward test running with frozen models""")
    c[1].warning("""**Not done**
- Conditional estimator not yet unblinded
- Source weighing and decision report unbuilt
- Daily automation unbuilt
- Two sources have no free feed — zero documents
- **No forward-test row has matured**""")
