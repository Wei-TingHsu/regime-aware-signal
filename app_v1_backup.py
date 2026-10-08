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

st.set_page_config(page_title="Regime-Aware Signal", layout="wide",
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


def plain_reason(raw, e=None):
    """Registered wording -> what a user can read. The technical phrasing is
    kept in the footnotes; it does not belong on the card."""
    r = (raw or "").lower()
    if "direction floor" in r or "no document" in r:
        # NOT "no news today". We read five named document sources, not the
        # news. Saying "no news" claims a coverage we do not have and would be
        # false on any day a market moved on something we do not read.
        return ("Nothing we read today spoke to this market — see what we "
                "cover, below")
    if "ess" in r:
        n = None
        if e and e.get("estimate"):
            n = e["estimate"].get("ess")
        return (f"Only {n:.0f} genuinely comparable past situations — we need "
                f"at least 8" if n is not None else
                "Too few genuinely comparable past situations")
    if "pool" in r or "precedent" in r:
        return "Not enough past situations of this kind to compare against"
    if "vetoed" in r:
        return "Today's news was too vague to act on"
    if "not in the price panel" in r:
        return "We do not carry price history for this instrument"
    return raw or "conditions for a view were not met"


def verdict(e):
    """Plain-English verdict for one asset. Returns (headline, colour, detail)."""
    est = e.get("estimate")
    if e["net_view"] is None:
        return "No view", "grey", plain_reason(e.get("abstain_reason"), e)
    if est is None or e.get("abstain"):
        return "No view", "grey", plain_reason(e.get("abstain_reason"), e)
    pct = est["estimate"]
    tier = est["tier"]
    word = "Clear signal" if tier == 1 else "Weak signal"
    colour = "green" if tier == 1 else "orange"
    return word, colour, f"{pct:+.2%} over the next 3 trading days"


st.markdown("<h1 style='margin-bottom:0'>Regime-Aware Signal</h1>",
            unsafe_allow_html=True)
st.caption("A daily read on five core markets, from the policy and company "
           "documents published that day — and, more often than not, an "
           "explicit refusal to call it.")

with st.expander("**How a number on this page is arrived at** — read this first",
                 expanded=False):
    st.markdown("""
Five steps run every trading day. Nothing is hand-adjusted at any of them.

**1 · Where are we?**  Eight macro series — volatility, the dollar, short and
long interest rates, the real yield, the yield curve, the policy rate, money
supply — are reduced to their principal directions of variation, and the day is
assigned to one of **four market conditions**. The four were not chosen by us:
the number came out of stability testing on twenty years of data, and each
condition is described on this page by what is actually inside it, not by a
name we picked.

**2 · What counts as comparable?**  A past day is comparable to today only if
it sat in a similar macro position *and* the documents that landed on it said a
similar thing about the market in question. Both conditions, not either.

**3 · What was published today?**  Every Fed statement, Fed minute, company
earnings release, executive order and proclamation published that day is read
by a language model. It never predicts a price. It classifies: what the
document says, how specific it is, how much of it was already public, and how
confident the reading is.

**4 · Combining several documents into one view.**  When more than one document
lands, each is weighted by how big, how specific, how new and how confidently
read it is — multiplied together, so a vague document contributes almost
nothing regardless of its other scores. If two documents point opposite ways,
**we show both and combine neither**, because the disagreement is more
informative than any average of it.

**5 · What happened last time?**  We find every past situation matching step 2,
weight them by how similar they are and how recent, and report what those
markets did over the following three trading days — blended against the long-run
average in proportion to how much genuinely comparable history exists.

**If fewer than eight past situations are genuinely comparable, we stop at
step 5 and report no number.** That threshold was fixed in writing before any
result was looked at. On most days, for most markets, that is what happens, and
saying so is the product.
    """)

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
                               key="today_signal_only",
                               help="Days where at least one market reached a "
                                    "clear or weak signal.")
        pool = ix[ix.best_tier <= 2] if only else ix
        if not len(pool):
            st.info("No day matches that filter.")
            st.stop()
        dates = list(pool.date)
        day = top[0].selectbox("Date", dates, index=len(dates) - 1,
                               key="today_date")
        R = jload(REPORTS / f"{day.replace('-','')}.json")
        if not R:
            st.warning(f"No report for {day}.")
            st.stop()

        # ---- headline ---------------------------------------------------
        views = [a for a, e in R["assets"].items()
                 if e.get("estimate") and not e.get("abstain")]
        if not views:
            st.info(f"### No view on any market for {day}\n"
                    "Either nothing we read was published, or what was "
                    "published does not resemble enough past situations to "
                    "support a view. That is the system's most common answer.")
        else:
            st.success(f"### {len(views)} of 5 markets have a view for {day}: "
                       + ", ".join(ASSET.get(v, v) for v in views))

        # ---- market condition -------------------------------------------
        g = R["regime"]
        prof = jload(PROC / "regime_profile.json")
        rlab = None
        if prof:
            rlab = prof["regimes"].get(str(g["label"]), {}).get("label")
        # Deliberately NOT st.metric: it clips a long value with an ellipsis
        # and offers no way to widen it, which is what hid the market-condition
        # description in the first build.
        cond_text = rlab if rlab else f"Condition {g['label'] + 1} of 4"
        c = st.columns([3, 1, 1])
        with c[0]:
            st.caption("MARKET CONDITION")
            st.markdown(f"#### {cond_text}")
            st.caption("One of four environments identified from macro data. "
                       "The description is generated from what is inside this "
                       "condition, not chosen.")
        with c[1]:
            st.caption("CONFIDENCE")
            st.markdown(f"#### {g['posterior']:.0%}" if g["posterior"] else "#### —")
        with c[2]:
            st.caption("NEWS TODAY")
            st.markdown(f"#### {len(R['documents'])}")
        if g.get("warning"):
            st.error("The model is **not confident** which market condition "
                     "today belongs to. Treat everything below with extra "
                     "caution.")

        # ---- the five markets -------------------------------------------
        st.write("")
        # One row per market rather than five narrow columns: at 1/5 of the
        # width a two-line reason wraps to five lines and the card stops being
        # scannable. Rows read left to right the way a user reads.
        for a, e in R["assets"].items():
            head, colour, detail = verdict(e)
            row = st.container(border=True)
            with row:
                k = st.columns([2.2, 1.6, 4.2, 4.0])
                k[0].markdown(f"**{ASSET.get(a, a)}**")
                k[1].markdown(f":{colour}[**{head}**]")
                k[2].markdown(detail)
                notes = []
                if e["net_view"] is not None:
                    tone = "positive" if e["net_view"] > 0 else "negative"
                    src = SOURCE.get(e["dominant_source"],
                                     e["dominant_source"] or "")
                    notes.append(f"Today's news reads *{tone}* here, mostly "
                                 f"from a {src.lower()}.")
                if e.get("sources_disagree"):
                    notes.append(":orange[Two items point opposite ways — both "
                                 "shown, neither combined.]")
                if e.get("agreement") == "DISCORDANT":
                    notes.append(":orange[The news and the history disagree.]")
                k[3].markdown("  \n".join(notes) if notes else "")

        # ---- what landed today ------------------------------------------
        st.caption("We read five document types: Federal Reserve statements "
                   "and minutes, company earnings releases, and executive "
                   "orders and proclamations from the Federal Register. We do "
                   "**not** read wire copy, social media or commentary — so a "
                   "quiet day here means our sources were quiet, not that the "
                   "world was.")
        with st.expander("Wider coverage — on the roadmap, and a paid tier"):
            st.markdown("""
Everything above is a **filed decision**. The moment a policy is *threatened*
rather than enacted — a tariff warning, a sanctions signal, a closure of a
shipping lane — is usually where a market moves first, and it is not covered
here today.

Four further sources would close that gap. All are US government works, so free
to obtain and free of the copyright constraint that rules out news text.

| Source | Volume | What it adds |
|---|---|---|
| White House statements and remarks | ~500–1,000/yr | Where threats to act live |
| Federal Reserve speeches and testimony | ~150/yr | We read 8 statements a year and miss ~150 speeches |
| Treasury releases and OFAC sanctions | ~300/yr | Immediate and market-moving |
| USTR press releases | ~200/yr | Trade actions before the Federal Register |

**Not built.** It is costed, scheduled after the current submission, and will be
offered as a subscription tier rather than folded into the base product —
reading intentions rather than only decisions is a materially different service.
            """)
        if R["documents"]:
            st.write("")
            with st.expander(f"The {len(R['documents'])} document(s) behind "
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
                st.dataframe(pd.DataFrame(rows), width='stretch',
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
    st.caption("Enter any listed ticker. We identify which broad market it "
               "belongs to, pull its price history if we do not already hold "
               "it, and ask the same question of that asset's own record. "
               "Tickers outside our core universe take a few seconds to fetch.")
    idx = jload(PROC / "report_index.json")
    if not idx:
        st.warning("No reports generated yet.")
    else:
        ix = pd.DataFrame(idx).sort_values("date")
        c = st.columns([1, 1, 1])
        tk = c[0].text_input("Ticker", value="SMH", key="lookup_tk").strip().upper()
        day = c[1].selectbox("Date", list(ix.date), index=len(ix) - 1,
                             key="lookup_date")
        ax = c[2].selectbox("Market", ["decide for me", "equities", "bonds",
                                       "gold", "dollar", "oil"],
                            key="lookup_axis")
        AXMAP = {"equities": "equity", "bonds": "duration", "gold": "gold",
                 "dollar": "dollar", "oil": "oil"}
        if st.button("Check", key="lookup_go"):
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
                except FileNotFoundError as ex:
                    # Name the file. "File not found" with no path is the least
                    # useful error a demo can give someone evaluating it.
                    st.error(f"**Missing data file:** `{ex.filename or ex}`\n\n"
                             "This tab runs the estimator live, so it needs the "
                             "price panel and the document reads on disk — "
                             "unlike the daily report, which is pre-generated. "
                             "If this is a fresh clone, those files may not be "
                             "committed.")
                    e = None
                except Exception as ex:
                    st.error(f"Could not check {tk}: {type(ex).__name__}: {ex}")
                    e = None
            if e:
                head, colour, detail = verdict(e)
                st.markdown(f"## {tk} — :{colour}[{head}]")
                st.write(detail)
                nice = {"equity": "equities", "duration": "bonds",
                        "gold": "gold", "dollar": "the dollar", "oil": "oil"}
                st.caption(f"{tk} was treated as a **{nice[e['axis']]}** "
                           f"exposure.")
                el = e.get("eligibility")
                if el:
                    q = st.columns(3)
                    q[0].caption("PRICE HISTORY")
                    q[0].markdown(f"**{el['sessions_of_history']:,}** sessions"
                                  f"  \nfrom {el['first_priced']}")
                    q[1].caption("MARKET CONDITIONS SEEN")
                    q[1].markdown(f"**{el['regimes_covered']} of "
                                  f"{el['regimes_total']}**")
                    q[2].caption("PRICES")
                    q[2].markdown(f"{el['price_source']}")
                src = (el or {}).get("price_source", "")
                if ax == "decide for me" and src and src != "project price panel":
                    st.info(f"We have no recorded classification for {tk}, so "
                            f"it was treated as an equity exposure by default. "
                            f"If that is wrong, pick the right market above and "
                            f"run it again — the answer will change.")
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
    st.markdown("#### The four market conditions, and what is in them")
    prof = jload(PROC / "regime_profile.json")
    if prof:
        rows = []
        for r, d in sorted(prof["regimes"].items()):
            rows.append({"Condition": f"{int(r)+1} of {len(prof['regimes'])}",
                         "What it looks like": d["label"],
                         "Share of history": f"{d['share_pct']}%"})
        st.dataframe(pd.DataFrame(rows), width='stretch',
                     hide_index=True)
        st.caption("Each description is the average of the macro series inside "
                   "that condition, against their own long-run averages. It "
                   "describes; it does not validate.")
    else:
        st.caption("Run `python regime_profile.py` to generate the "
                   "descriptions of each condition.")

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
    st.markdown("")
    st.markdown("**On the roadmap.** Four further government sources — White "
                "House statements, Federal Reserve speeches, Treasury and OFAC "
                "releases, and USTR announcements — would let this system read "
                "*intentions* rather than only *decisions*. Costed and "
                "scheduled, not built, and intended as a paid tier.")
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
