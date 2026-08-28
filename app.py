"""
app.py -- the product. Three tabs, plain English, no jargon above the fold.

WHAT CHANGED ON 2026-08-27, AND WHY
    The previous version had EIGHT tabs -- "Universe", "Engines", "Document
    layer", "Forward test", "What we got wrong", "Behind the scenes" -- and
    spoke in tier / ESS / w / tau2 / political_other / regime 3. That is an
    evidence terminal for a supervisor. It is not a product: a new user cannot
    tell what to look at first, and a portfolio manager should not have to
    learn five abbreviations to read one screen.

    This version has THREE tabs. Everything a user needs is on the first.
    Technical detail that used to be a tab is now a FOOTNOTE at the bottom of
    the tab it belongs to, marked with an asterisk. Nothing was deleted from
    the record -- the repository still holds every number and every registered
    criterion. It is just no longer the front page.

    Vocabulary is translated once, in PLAIN, and nowhere is a term used on
    screen that has not been translated.

STILL TRUE, AND THE REASON THE PRODUCT LOOKS LIKE THIS
    Every figure is READ from outputs/reports/*.json, written by
    step6_report.py. The app computes nothing except the on-demand asset run.
    Most days, on most assets, the honest answer is "no view", and the product
    says so in those words. A screen that always produced a number would be
    the failure.

Run:
    streamlit run app.py
"""
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
DOCS, PROC = ROOT / "docs", ROOT / "processed"
REPORTS = ROOT / "outputs" / "reports"

st.set_page_config(page_title="Market Conditions Monitor", layout="wide",
                   initial_sidebar_state="collapsed")

# --------------------------------------------------------------------------
# PLAIN. Every term that appears on screen is translated here, once.
# --------------------------------------------------------------------------
SOURCE = {
    "fomc_statement": "Fed policy statement",
    "fomc_minutes": "Fed meeting minutes",
    "earnings_8k": "Company earnings release",
    "political_order": "Executive order",
    "political_other": "Proclamation or notice",
}
ASSET = {"SPY": "US equities", "TLT": "Long-term US Treasuries",
         "GLD": "Gold", "UUP": "US dollar", "USO": "Oil"}
JARGON = {
    "market condition": "Which of four broad market environments today "
                        "resembles, learned from macro data rather than "
                        "assumed.",
    "confidence in that condition": "How sure the model is that today belongs "
                                    "to that environment rather than a "
                                    "neighbouring one. Below 60% we say so.",
    "comparable past days": "How many genuinely similar past situations the "
                            "estimate rests on, after accounting for how "
                            "similar each one is. Fewer than 8 and we decline "
                            "to give a view.",
    "how much history counted": "Between 0 and 1. At 0 the past adds nothing "
                                "beyond the long-run average and we say so.",
}


def jload(p):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return None


def verdict(e):
    """Plain-English verdict for one asset. Returns (headline, colour, detail)."""
    est = e.get("estimate")
    if e["net_view"] is None:
        return "No view", "grey", e.get("abstain_reason") or "nothing published"
    if est is None or e.get("abstain"):
        why = e.get("abstain_reason", "")
        if "ESS" in why or "pool" in why or "precedent" in why:
            plain = "Not enough comparable history to say anything"
        else:
            plain = why or "conditions for a view were not met"
        return "No view", "grey", plain
    pct = est["estimate"]
    tier = est["tier"]
    word = "Clear signal" if tier == 1 else "Weak signal"
    colour = "green" if tier == 1 else "orange"
    return word, colour, f"{pct:+.2%} over the next 3 trading days"


st.markdown("<h1 style='margin-bottom:0'>Market Conditions Monitor</h1>",
            unsafe_allow_html=True)
st.caption("What today's policy and company news implies for five core "
           "markets — and, more often than not, why it implies nothing.")

tabs = st.tabs(["Today", "Look up an asset", "How this works"])

# ==========================================================================
with tabs[0]:
    idx = jload(PROC / "report_index.json")
    if not idx:
        st.warning("No reports have been generated yet. Run "
                   "`python generate_reports.py --docs-only`.")
    else:
        ix = pd.DataFrame(idx).sort_values("date")
        top = st.columns([2, 1, 3])
        only = top[1].checkbox("Only days with a signal", value=False,
                               help="Days where at least one market reached a "
                                    "clear or weak signal.")
        pool = ix[ix.best_tier <= 2] if only else ix
        if not len(pool):
            st.info("No day matches that filter.")
            st.stop()
        dates = list(pool.date)
        day = top[0].selectbox("Date", dates, index=len(dates) - 1)
        R = jload(REPORTS / f"{day.replace('-','')}.json")
        if not R:
            st.warning(f"No report for {day}.")
            st.stop()

        # ---- headline ---------------------------------------------------
        views = [a for a, e in R["assets"].items()
                 if e.get("estimate") and not e.get("abstain")]
        if not views:
            st.info(f"### No view on any market for {day}\n"
                    "The news that landed does not resemble enough past "
                    "situations to support a view. That is the system's most "
                    "common answer.")
        else:
            st.success(f"### {len(views)} of 5 markets have a view for {day}: "
                       + ", ".join(ASSET.get(v, v) for v in views))

        # ---- market condition -------------------------------------------
        g = R["regime"]
        c = st.columns(3)
        c[0].metric("Market condition", f"{g['label'] + 1} of 4")
        c[1].metric("Confidence in that condition",
                    f"{g['posterior']:.0%}" if g["posterior"] else "—")
        c[2].metric("News items today", len(R["documents"]))
        if g.get("warning"):
            st.error("The model is **not confident** which market condition "
                     "today belongs to. Treat everything below with extra "
                     "caution.")

        # ---- the five markets -------------------------------------------
        st.write("")
        cols = st.columns(5)
        for i, (a, e) in enumerate(R["assets"].items()):
            head, colour, detail = verdict(e)
            with cols[i]:
                st.markdown(f"**{ASSET.get(a, a)}**")
                st.markdown(f":{colour}[**{head}**]")
                st.caption(detail)
                if e["net_view"] is not None:
                    tone = "positive" if e["net_view"] > 0 else "negative"
                    st.caption(f"Today's news reads *{tone}* for this market, "
                               f"mostly from a "
                               f"{SOURCE.get(e['dominant_source'], e['dominant_source']).lower()}.")
                if e.get("sources_disagree"):
                    st.caption(":orange[Two news items point opposite ways. We "
                               "show both and combine neither.]")
                if e.get("agreement") == "DISCORDANT":
                    st.caption(":orange[The news and the history disagree.]")

        # ---- what landed today ------------------------------------------
        if R["documents"]:
            st.write("")
            with st.expander(f"The {len(R['documents'])} news item(s) behind "
                             f"this, in detail"):
                rows = []
                for d in R["documents"]:
                    dirs = ", ".join(
                        f"{ASSET.get(k, k)} {'up' if v > 0 else 'down'}"
                        for k, v in d["direction"].items()
                        if v is not None and abs(v) > 0.05) or "no clear read"
                    rows.append({"Type": SOURCE.get(d["source"], d["source"]),
                                 "Published": d["published"],
                                 "Reads as": dirs,
                                 "How specific": f"{d['specificity']:.0%}"
                                 if d["specificity"] else "—",
                                 "How new": f"{d['novelty']:.0%}"
                                 if d["novelty"] else "—"})
                st.dataframe(pd.DataFrame(rows), use_container_width=True,
                             hide_index=True)

        # ---- carry-forward ------------------------------------------------
        prev = ix[ix.date < day]
        if len(prev):
            pday = prev.iloc[-1].date
            P = jload(REPORTS / f"{pday.replace('-','')}.json")
            age = (pd.Timestamp(day) - pd.Timestamp(pday)).days
            if P:
                lines = [f"- **{ASSET.get(a, a)}**: news read "
                         f"{'positive' if e['net_view'] > 0 else 'negative'}"
                         for a, e in P["assets"].items()
                         if e["net_view"] is not None]
                if lines:
                    with st.expander(f"What the last news day said "
                                     f"({pday}, {age} day(s) before)"):
                        st.markdown("\n".join(lines))
                        st.caption("Shown as it was, not faded with age. "
                                   "Whether older news should count for less "
                                   "is a modelling question we have not "
                                   "answered, so we do not pretend to.")

        # ---- footnotes ----------------------------------------------------
        st.write("")
        st.divider()
        st.caption("**\\* Notes on the above.**")
        n = []
        for a, e in R["assets"].items():
            est = e.get("estimate")
            if est:
                n.append(f"*{ASSET.get(a, a)}*: {est['n_matched']} past "
                         f"situations matched, of which "
                         f"{est['ess']:.0f} counted as genuinely comparable; "
                         f"history weight {est['w_shrink']:.2f}.")
        if n:
            st.caption("  \n".join(n))
        st.caption("\\* *A view is withheld unless at least 8 past situations "
                   "are genuinely comparable. This threshold was fixed in "
                   "advance, in writing, before any result was seen.*")
        st.caption("\\* *Where the news and the history disagree, both are "
                   "shown and no combined number is produced. Combining them "
                   "would hide the disagreement, which is the most useful "
                   "thing on the screen.*")
        st.caption("\\* *We tested whether agreement between news and history "
                   "predicts better outcomes. It does not — cases where they "
                   "disagreed performed better. So agreement is displayed and "
                   "changes no number.*")

# ==========================================================================
with tabs[1]:
    st.subheader("Look up any asset")
    st.caption("Enter a ticker. We identify which broad market it belongs to, "
               "then ask the same question of that asset's own price history.")
    idx = jload(PROC / "report_index.json")
    if not idx:
        st.warning("No reports generated yet.")
    else:
        ix = pd.DataFrame(idx).sort_values("date")
        c = st.columns([1, 1, 1])
        tk = c[0].text_input("Ticker", value="SMH").strip().upper()
        day = c[1].selectbox("Date", list(ix.date), index=len(ix) - 1)
        ax = c[2].selectbox("Market", ["decide for me", "equities", "bonds",
                                       "gold", "dollar", "oil"])
        AXMAP = {"equities": "equity", "bonds": "duration", "gold": "gold",
                 "dollar": "dollar", "oil": "oil"}
        if st.button("Check"):
            with st.spinner("Checking history…"):
                try:
                    import asset_extension as AE
                    cfg = AE.load_config(); sc, rt = AE.load_data()
                    ii = pd.DatetimeIndex(sc.index)
                    lab = AE.regime_labels_expanding(sc, cfg)
                    Z = AE._z_expanding(sc[AE.CLUSTERING_PCS].values)
                    amap = AE.axis_map(cfg)
                    docs = AE.load_reads()
                    pos = ii.searchsorted(pd.DatetimeIndex(docs["date"].values),
                                          side="left")
                    ok = pos < len(ii)
                    docs = docs.loc[ok].copy(); docs["session"] = ii[pos[ok]]
                    for cc in ("magnitude", "specificity", "novelty",
                               "confidence"):
                        docs[cc] = pd.to_numeric(docs.get(cc), errors="coerce")
                    docs["weight"] = (docs.magnitude.fillna(0)
                                      * docs.specificity.fillna(0)
                                      * docs.novelty.fillna(0)
                                      * docs.confidence.fillna(0))
                    t = pd.Timestamp(day); ti = int(ii.get_loc(t))
                    axis = (amap.get(tk, ("equity", "?"))[0]
                            if ax == "decide for me" else AXMAP[ax])
                    e = AE.run_asset(tk, axis, t, ti, ii, sc, rt, Z, lab,
                                     int(AE.DEFAULT["n_regimes"]),
                                     docs[docs.session == t],
                                     docs[docs.session < t])
                except Exception as ex:
                    st.error(f"Could not check {tk}: {type(ex).__name__}")
                    e = None
            if e:
                head, colour, detail = verdict(e)
                st.markdown(f"## {tk} — :{colour}[{head}]")
                st.write(detail)
                nice = {"equity": "equities", "duration": "bonds",
                        "gold": "gold", "dollar": "the dollar", "oil": "oil"}
                st.caption(f"{tk} was treated as a **{nice[e['axis']]}** "
                           f"exposure.")
                est = e.get("estimate")
                if est:
                    st.caption(f"\\* {est['n_matched']} past situations "
                               f"matched, {est['ess']:.0f} genuinely "
                               f"comparable, history weight "
                               f"{est['w_shrink']:.2f}.")
                if not e.get("is_proxy"):
                    st.caption(f"\\* *The news we read describes "
                               f"{nice[e['axis']]} broadly. It says nothing "
                               f"specific to {tk}'s own industry, so treat "
                               f"this as a market-level read, not a "
                               f"company-level one.*")

# ==========================================================================
with tabs[2]:
    st.subheader("How this works")
    st.markdown("""
Every trading day we read the policy and company documents published that day —
Federal Reserve statements and minutes, company earnings releases, executive
orders and proclamations. A language model classifies each one: what it says,
how specific it is, how much of it was already public.

We separately identify which of **four broad market environments** today
resembles, using macro data alone.

Then we ask one question: **when documents like today's landed in environments
like today's, what happened next?** If enough genuinely comparable situations
exist, we report what they did. If they do not, we say so and give no number.

That last part is the product. Most days, for most markets, the honest answer
is that there is no usable precedent — and a tool that produced a number anyway
would be worse than useless.
    """)
    st.divider()
    st.markdown("#### What this cannot see")
    R0 = None
    ixx = jload(PROC / "report_index.json")
    if ixx:
        R0 = jload(REPORTS / f"{ixx[-1]['date'].replace('-','')}.json")
    if R0:
        for h, b in R0["cannot_see"]:
            plain = (b.replace("`transcript`", "earnings call transcripts")
                      .replace("`bank_research`", "sell-side research")
                      .replace("**", ""))
            st.markdown(f"- **{h}.** {plain}")
    st.divider()
    st.caption("**\\* Method notes, for readers who want them.**")
    st.caption("\\* *Every threshold in this system — how comparable a past "
               "situation must be, how many are enough, what counts as a "
               "signal — was written down and committed to version control "
               "before any result was looked at. Where a test failed, the "
               "failure is recorded rather than the test rerun.*")
    st.caption("\\* *Two headline hypotheses were tested and rejected: gold "
               "does not reliably decouple from equities under stress on this "
               "data, and sector rotation has no stable running order. Both "
               "are published rather than buried.*")
    st.caption("\\* *No live performance figure is shown anywhere in this "
               "tool. The forward test began on 19 August 2026 and too few "
               "positions have run their course to report anything honestly.*")
    st.caption("\\* *Full methodology, every registered test and every "
               "correction is in the project repository.*")
