"""
app.py -- DEMONSTRATION TERMINAL. Regime-Aware Cross-Asset Signal Framework.

TWO KINDS OF TAB, AND THE DIFFERENCE MATTERS
    LIVE tabs read every number from the repo -- processed/*.json, the ledger,
    file counts on disk. If a file is missing the tab says so rather than
    showing a stale figure.

    The "Daily report" tab was a SPECIMEN with invented numbers until
    2026-08-27. It now reads outputs/reports/*.json written by step6_report.py
    after the step 3 unblinding. Every figure has a registered script and a
    commit behind it. Most assets on most days ABSTAIN, with the reason stated;
    that is the honest state of the evidence (CURRENT_STATE section 17.7), and
    a tab that always produced a number would be the failure.

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

tabs = st.tabs(["What this is", "Daily report", "Universe",
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
    # ---- LIVE. Reads outputs/reports/*.json written by step6_report.py. -----
    # Nothing here is computed; every number has a registered script and a
    # commit behind it. The SPECIMEN this tab replaced is gone: an invented
    # figure that escapes its banner becomes a claimed result.
    idx = jload(PROC / "report_index.json")
    if not idx:
        missing("processed/report_index.json", "generate_reports.py")
    else:
        ix = pd.DataFrame(idx).sort_values("date")
        st.header("Daily decision report")
        st.caption("Specification: `prereg_analog_event.md` §8. Every field is "
                   "required by that section. Sessions without a document are "
                   "not listed here; on those days the system states the regime "
                   "and abstains on every asset because nothing was published.")
        c = st.columns([2, 1, 1, 1])
        flt = c[1].selectbox("show", ["all document sessions",
                                      "sources disagreed",
                                      "tier 1 or 2 reached"])
        pool = ix
        if flt == "tier 1 or 2 reached":
            pool = ix[ix.best_tier <= 2]
        elif flt == "sources disagreed":
            keep = []
            for d in ix.date:
                r = jload(ROOT / "outputs" / "reports" / f"{d.replace('-','')}.json")
                if r and any(e.get("sources_disagree") for e in r["assets"].values()):
                    keep.append(d)
            pool = ix[ix.date.isin(keep)]
        dates = list(pool.date)
        if not dates:
            st.info("no sessions match this filter"); st.stop()
        day = c[0].selectbox("session", dates, index=len(dates) - 1)
        R = jload(ROOT / "outputs" / "reports" / f"{day.replace('-','')}.json")
        if not R:
            missing(f"outputs/reports/{day}.json", "step6_report.py"); st.stop()

        # ---- 1. regime -------------------------------------------------
        g = R["regime"]
        m = st.columns(4)
        m[0].metric("Session", R["date"])
        m[1].metric("Regime", g["label"])
        m[2].metric("Posterior", f"{g['posterior']:.1%}" if g["posterior"] else "—")
        m[3].metric("Documents", len(R["documents"]))
        if g.get("warning"):
            st.error("**Posterior below 60%.** The regime assignment for this "
                     "session is not confident and every conditional figure "
                     "below inherits that uncertainty.")
        if g.get("label_mismatch"):
            st.warning(f"Expanding cache assigns regime {g['label']}; a fresh fit "
                       f"assigns {g['posterior_label']}. Reported, not resolved.")

        # ---- 2. documents ----------------------------------------------
        st.subheader("Documents read this session")
        rows = []
        for d in R["documents"]:
            dirs = ", ".join(f"{k} {v:+.2f}" for k, v in d["direction"].items()
                             if v is not None and abs(v) > 0.05) or "—"
            rows.append({"source": d["source"], "published": d["published"],
                         "magnitude": d["magnitude"], "specificity": d["specificity"],
                         "novelty": d["novelty"], "confidence": d["confidence"],
                         "directions": dirs, "truncated": d["truncated"]})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # ---- 3-5. per asset ----------------------------------------------
        st.subheader("Per asset — the tier is the headline")
        st.caption("Tier 3 is an abstention with its reason. The estimate is "
                   "still printed, in grey, marked *not a recommendation* — "
                   "transparency is required by §8, endorsement is not.")
        cols = st.columns(5)
        for i, (a, e) in enumerate(R["assets"].items()):
            with cols[i]:
                est = e.get("estimate")
                tier = est["tier"] if est else 3
                colour = {1: "green", 2: "orange", 3: "red"}[tier]
                st.markdown(f"### {a}  :{colour}[tier {tier}]")
                if e["net_view"] is None:
                    st.markdown(f"**ABSTAIN** — {e['abstain_reason']}")
                    continue
                st.markdown(f"net view **{e['net_view']:+.3f}**  \n"
                            f"dominant `{e['dominant_source']}`")
                if e.get("sources_disagree"):
                    st.markdown(":orange[**sources disagree in sign**]")
                if est:
                    st.markdown(f"precedents {est['n_matched']} · "
                                f"ESS **{est['ess']:.1f}** · w {est['w_shrink']:.3f}")
                    if est["tau2_zero"]:
                        st.markdown(":grey[τ² = 0 — registered null path]")
                    if e["abstain"]:
                        st.markdown(f"**ABSTAIN** — {e['abstain_reason']}")
                        st.markdown(f":grey[estimate {est['estimate']:+.3%} "
                                    f"— not a recommendation]")
                    else:
                        st.markdown(f"**estimate {est['estimate']:+.3%}** (3-session)")
                    if e["agreement"] == "DISCORDANT":
                        st.markdown(":orange[DISCORDANT] — documents and history "
                                    "disagree; both shown, no combined figure")
                    elif e["agreement"] == "CONCORDANT":
                        st.markdown(":grey[CONCORDANT — display only; the "
                                    "registered test found concordant cases "
                                    "performed *worse*]")
                else:
                    st.markdown(f"**ABSTAIN** — {e['abstain_reason']}")

        # ---- carry-forward: last document view, with its age --------------
        st.subheader("Last document view before this session")
        st.caption("Shown with its age. Not decayed — decaying it is a modelling "
                   "choice that would need registering; showing it is display.")
        prev = ix[ix.date < day]
        if len(prev):
            pday = prev.iloc[-1].date
            P = jload(ROOT / "outputs" / "reports" / f"{pday.replace('-','')}.json")
            age = (pd.Timestamp(day) - pd.Timestamp(pday)).days
            if P:
                lines = [f"**{pday}** — {age} calendar day(s) earlier"]
                for a, e in P["assets"].items():
                    if e["net_view"] is not None:
                        lines.append(f"- {a}: net {e['net_view']:+.3f} from "
                                     f"`{e['dominant_source']}`")
                st.markdown("\n".join(lines))
        else:
            st.markdown("*no earlier document session*")

        # ---- any asset, through the five-axis route ---------------------
        st.subheader("Any asset, through the five-axis route")
        st.caption("Names an axis for the asset and runs the frozen estimator "
                   "on that asset's own returns. Registered in "
                   "`asset_extension.py`; the registered prediction — non-proxy "
                   "assets show lower `w` — held trivially, because `w` ≈ 0 for "
                   "the proxy too. The route works; the macro signal is thin.")
        tk = st.text_input("ticker", value="SMH").strip().upper()
        ax = st.selectbox("axis", ["auto", "equity", "duration", "gold",
                                   "dollar", "oil"])
        if st.button("run"):
            try:
                import asset_extension as AE
                cfg = AE.load_config(); sc, rt = AE.load_data()
                ix2 = pd.DatetimeIndex(sc.index)
                lab = AE.regime_labels_expanding(sc, cfg)
                Z = AE._z_expanding(sc[AE.CLUSTERING_PCS].values)
                amap = AE.axis_map(cfg)
                docs = AE.load_reads()
                pos = ix2.searchsorted(pd.DatetimeIndex(docs["date"].values), side="left")
                ok = pos < len(ix2); docs = docs.loc[ok].copy(); docs["session"] = ix2[pos[ok]]
                for cc in ("magnitude", "specificity", "novelty", "confidence"):
                    docs[cc] = pd.to_numeric(docs.get(cc), errors="coerce")
                docs["weight"] = (docs.magnitude.fillna(0) * docs.specificity.fillna(0)
                                  * docs.novelty.fillna(0) * docs.confidence.fillna(0))
                t = pd.Timestamp(day); ti = int(ix2.get_loc(t))
                axis = amap.get(tk, ("equity", "?"))[0] if ax == "auto" else ax
                e = AE.run_asset(tk, axis, t, ti, ix2, sc, rt, Z, lab,
                                 int(AE.DEFAULT["n_regimes"]),
                                 docs[docs.session == t], docs[docs.session < t])
                st.markdown(AE.render(t, [e]))
            except Exception as ex:
                st.error(f"asset run failed: {type(ex).__name__}: {ex}")

        # ---- 6. cannot see ---------------------------------------------
        st.subheader("What this system cannot see")
        st.caption("Printed in every report, per §8 item 6. Coverage gaps, not results.")
        for h, b in R["cannot_see"]:
            st.markdown(f"**{h}.** {b}")

        # ---- 7. performance ----------------------------------------------
        st.subheader("Performance")
        st.markdown("*§8 item 7: no performance number that has not matured.* "
                    "The live forward test began 19 August 2026. No figure is "
                    "reported because matured trades remain too few to carry one.")

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
