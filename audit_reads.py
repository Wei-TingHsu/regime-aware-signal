"""
audit_reads.py -- do the documents that MUST carry signal actually carry it?
Every source, every check, from cached reads on disk. No API calls.

WHY THIS EXISTS
    On 2026-08-25 the political_other aggregate -- 816 documents, |direction|
    below 0.005 on every asset class -- was read as "the reader correctly finds
    nothing in ceremonial documents". That interpretation was made without
    checking whether the documents that would falsify it existed. They do:
    Section 232 tariffs are imposed by PROCLAMATION, which is this class.

    The error generalises. An aggregate statistic for a source says nothing
    about whether the reader saw the documents that matter. For every source
    there are document types that MUST produce a read with direction,
    magnitude and novelty if the reader is working at all. This finds those
    documents by their text and reports what the reader assigned them.

WHAT EACH SECTION TESTS

    A  TIMING ORDER. Novelty should fall with publication lag: an FOMC
       statement IS the event; an 8-K accompanies the release; a Federal
       Register document lands days after the announcement that moved the
       price. If novelty does not fall in that order, the novelty field is not
       measuring what it claims.

    B  SIGNAL CLASSES vs BASELINE. Per source, keyword-matched document classes
       that should carry signal, against the rest of the source. Matched
       documents reading like unmatched ones means the reader is not
       distinguishing operative content from routine content.

    C  SIGN CONSISTENCY. Where the expected sign is knowable from the text:
       "raise the target range" -> duration NEGATIVE (duration is bond PRICE
       per the schema). "lower the target range" -> duration POSITIVE. A
       reader that gets these backwards is unusable regardless of aggregates.
       Gold and equity under tariffs are deliberately NOT signed -- the sign is
       genuinely ambiguous (risk-off vs dollar strength).

    D  WITHIN-READER CONSISTENCY. The reader's own fields should agree with each
       other. is_decided=True should have higher specificity than False.
       extra.stance (hawkish +) should anti-correlate with dir_duration.
       extra.surprise should correlate with dir_equity. Disagreement here needs
       no external truth to be a defect.

    E  LANDMARK DOCUMENTS. Named events the reader must have seen as large:
       the 2020-03-15 emergency cut, the 2022-06 75bp hike, the 2025 tariff
       orders, and so on. Matched by date window AND keyword. A landmark read
       as routine is a defect with a name attached.

    F  FIELD POPULATION. Are the source-specific extras actually filled?
       An earnings read with no ticker, a political read with no is_decided,
       cannot be used by step 5.

    G  FLAT-TAIL CHECK. Per source: how many documents carry any direction, and
       what the top of the distribution looks like. A source with a handful of
       operative documents and a long flat tail is plausible. A source where
       NOTHING was read as directional is not.

WHAT THIS IS NOT
    Keyword matching is crude. Every match list over- and under-includes.
    Nothing here is a registered test and nothing here changes a result. It
    tells you WHERE TO LOOK and what the reader said when it got there. A
    flagged line is a question, not a verdict.

Run from the repo root:
    python audit_reads.py
Writes docs/read_audit_results.md.
"""
import json
import re
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

DOCS = Path("data_provenance/docs")
READS = Path("data_provenance/doc_reads")
OUT_MD = Path("docs/read_audit_results.md")
PROMPT_VERSION = "v1-2026-08-23"
SOURCES = ["fomc_statement", "fomc_minutes", "earnings_8k",
           "political_order", "political_other"]
ASSET = {"equity": "dir_eq", "duration": "dir_dur", "gold": "dir_gold",
         "dollar": "dir_usd", "oil": "dir_oil"}

# --------------------------------------------------------------------------
# B: keyword classes per source. "expect" is what a working reader must show
# on matched documents RELATIVE to the source baseline. Signs are only
# asserted where the text makes them unambiguous.
# --------------------------------------------------------------------------
CLASSES = {
    "fomc_statement": [
        ("rate HIKE",  r"raise the target range|increase the target range|raise the federal funds", "dur<0, mag>base"),
        ("rate CUT",   r"lower the target range|reduce the target range|decrease the target range", "dur>0, mag>base"),
        ("emergency / intermeeting", r"intermeeting|unscheduled|emergency", "mag>>base, novelty>>base"),
        ("QE / asset purchases start", r"begin purchas|will purchase|increase its holdings|expand its holdings", "dur>0, mag>base"),
        ("taper / runoff", r"reduce the pace|reducing the pace|balance sheet.{0,40}reduc|runoff|roll ?off", "dur<0"),
        ("forward guidance strengthened", r"for an extended period|at least through|until.{0,60}(inflation|employment)", "spec>base"),
    ],
    "fomc_minutes": [
        ("taper / runoff discussed", r"taper|reduce the pace|balance sheet.{0,60}(reduc|normali)|runoff", "dur<0, dispersion>base"),
        ("dissent recorded", r"voting against|dissent", "dispersion>base"),
        ("emergency context", r"intermeeting|unscheduled|videoconference", "mag>base"),
        ("hawkish tilt language", r"(several|many|most|a number of) participants.{0,80}(sooner|faster|more rapid|earlier)", "dur<0"),
        ("dovish tilt language", r"(several|many|most|a number of) participants.{0,80}(patien|gradual|slower|later)", "dur>0"),
    ],
    "earnings_8k": [
        ("guidance RAISED", r"rais(e|es|ed|ing) (its |our |full[- ]year |fiscal |annual )?(guidance|outlook)|guidance.{0,40}(above|exceed)", "eq>0, mag>base, guidance_change>0"),
        ("guidance LOWERED / withdrawn", r"lower(s|ed|ing)? (its |our |full[- ]year )?(guidance|outlook)|withdraw.{0,20}guidance|below.{0,40}guidance", "eq<0, mag>base, guidance_change<0"),
        ("record revenue", r"record (quarterly |annual |fiscal )?revenue", "eq>0"),
        ("net loss", r"net loss", "eq<=base"),
        ("restructuring / impairment", r"restructuring|impairment|write[- ]?down", "eq<=base"),
        ("buyback / dividend raise", r"(share|stock) repurchase|buyback|(increase|raise).{0,30}dividend", "eq>0"),
    ],
    "political_order": [
        ("TARIFF / trade action", r"\btariff|ad valorem|section 232|section 301|reciprocal trade|IEEPA|international emergency economic powers", "spec>base, |dir|>base"),
        ("SANCTIONS / blocking", r"blocking property|sanction|asset(s)? (of|are) blocked", "spec>base, |dir|>base"),
        ("export controls / semiconductors", r"export control|advanced computing|semiconductor|entity list", "|dir|>base"),
        ("energy / drilling / pipelines", r"drilling|pipeline|oil and gas|energy dominance|offshore", "oil != 0"),
        ("national emergency declared", r"declar(e|es|ing).{0,30}national emergency", "spec>base, mag>base"),
        ("ceremonial / administrative", r"advisory (council|committee|board)|establish(es|ing)? (the|a).{0,40}(council|commission|task force)|flag", "spec<base, |dir|~0"),
    ],
    "political_other": [
        ("Section 232 PROCLAMATION", r"section 232|trade expansion act|adjusting imports", "spec>base, |dir|>base  <-- THE TARIFF CASE"),
        ("Section 201 safeguard", r"section 201|safeguard|trade act of 1974", "spec>base, |dir|>base"),
        ("any tariff / duty language", r"\btariff|ad valorem|\bduties\b|\bquota\b", "|dir|>base"),
        ("national emergency (notice / continuation)", r"national emergency", "spec>base"),
        ("commemorative", r"(day|week|month) of|national.{0,30}(day|week|month)|proclaim.{0,60}(day|week|month)|in witness whereof", "spec<base, |dir|~0"),
    ],
}

# --------------------------------------------------------------------------
# E: landmark documents. Date = the ANNOUNCEMENT date; Federal Register
# publication lags it, so the window is generous. Matched by window AND
# keyword. If a landmark is absent that is a COVERAGE finding, not a reader one.
# --------------------------------------------------------------------------
LANDMARKS = [
    ("fomc_statement",  "2008-12-16", 3,  r"0 to 1/4|zero", "ZIRP -- dur>0, mag high, novelty high"),
    ("fomc_statement",  "2020-03-15", 3,  r"1/4|emergency|coronavirus", "COVID emergency cut -- dur>0, mag >>, novelty >>"),
    ("fomc_statement",  "2015-12-16", 3,  r"raise|1/4 to 1/2", "first hike of the cycle -- dur<0, novelty LOW (telegraphed)"),
    ("fomc_statement",  "2022-06-15", 3,  r"3/4|1-1/2 to 1-3/4", "75bp hike -- dur<0, mag high"),
    ("fomc_statement",  "2013-12-18", 3,  r"reduce the pace|modest", "taper begins -- dur<0"),
    ("fomc_minutes",    "2013-05-22", 3,  r"taper|reduce the pace|purchases", "taper-tantrum minutes -- dur<0, dispersion high"),
    ("fomc_minutes",    "2022-01-05", 3,  r"balance sheet|runoff", "Jan-22 minutes, runoff shock -- dur<0, novelty > base"),
    ("political_order", "2025-02-01", 10, r"tariff|Canada|Mexico|China|IEEPA", "IEEPA tariffs CA/MX/CN -- spec high, |dir| > 0"),
    ("political_order", "2025-04-02", 10, r"reciprocal|tariff|ad valorem", "reciprocal tariffs -- spec high, mag high, |dir| > 0"),
    ("political_other", "2018-03-08", 10, r"steel|aluminum|section 232", "232 steel/aluminum -- spec high, |dir| > 0"),
    ("political_other", "2025-03-26", 10, r"automobile|section 232", "232 autos -- spec high, |dir| > 0"),
    ("political_other", "2025-02-10", 10, r"steel|aluminum|section 232", "232 steel/aluminum restored -- spec high, |dir| > 0"),
    ("earnings_8k",     "2023-05-24", 3,  r"NVIDIA|NVDA", "NVDA FQ1-24, guidance +50% -- eq>0, mag high, novelty high"),
]


# ==========================================================================
def parse_date(stem):
    m = re.match(r"(\d{8})", stem)
    return datetime.strptime(m.group(1), "%Y%m%d") if m else None


def load():
    """One row per cached read, with the document text attached."""
    rows = []
    for src in SOURCES:
        d = DOCS / src
        if not d.exists():
            continue
        for p in sorted(d.glob("*.txt")):
            c = READS / f"{src}__{p.stem}__{PROMPT_VERSION}.json"
            if not c.exists():
                continue
            try:
                r = json.loads(c.read_text())
                text = p.read_text(errors="ignore")
            except Exception:
                continue
            dd = r.get("direction") or {}
            ex = r.get("extra") or {}
            row = dict(source=src, stem=p.stem, date=parse_date(p.stem),
                       text=text, words=len(text.split()),
                       specificity=r.get("specificity"), novelty=r.get("novelty"),
                       magnitude=r.get("magnitude"), confidence=r.get("confidence"),
                       horizon=r.get("horizon_days"),
                       n_evidence=len([e for e in (r.get("evidence") or [])
                                       if isinstance(e, str) and e.strip()]),
                       truncated=bool(r.get("truncated", False)))
            for k, col in ASSET.items():
                v = dd.get(k)
                row[col] = float(v) if isinstance(v, (int, float)) else np.nan
            for k in ("stance", "guidance", "dispersion", "surprise",
                      "guidance_change", "ticker", "is_decided", "actor"):
                row["x_" + k] = ex.get(k)
            rows.append(row)
    df = pd.DataFrame(rows)
    for c in ("specificity", "novelty", "magnitude", "confidence"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["absdir_max"] = df[list(ASSET.values())].abs().max(axis=1)
    df["absdir_mean"] = df[list(ASSET.values())].abs().mean(axis=1)
    return df


L = []   # markdown lines


def out(s=""):
    print(s)
    L.append(s)


def fmt(v, w=6):
    return f"{v:{w}.3f}" if isinstance(v, (int, float)) and not np.isnan(v) else " " * (w - 1) + "-"


# ==========================================================================
def section_A(df):
    out("\n## A. TIMING ORDER — does novelty fall with publication lag?")
    out()
    out("Expected: fomc_statement > earnings_8k > political_order ≈ political_other.")
    out("The statement IS the event; the 8-K accompanies the release; a Federal")
    out("Register document lands days after the announcement that moved the price.")
    out()
    out("| source | n | novelty mean | novelty p90 | specificity | max\\|dir\\| mean |")
    out("|---|---|---|---|---|---|")
    g = df.groupby("source")
    rank = {}
    for s in SOURCES:
        if s not in g.groups:
            continue
        x = g.get_group(s)
        rank[s] = x["novelty"].mean()
        out(f"| {s} | {len(x)} | {fmt(x['novelty'].mean())} | "
            f"{fmt(x['novelty'].quantile(.9))} | {fmt(x['specificity'].mean())} | "
            f"{fmt(x['absdir_max'].mean())} |")
    order = [s for s, _ in sorted(rank.items(), key=lambda kv: -kv[1])]
    out()
    out(f"Observed novelty order: {' > '.join(order)}")
    exp = ["fomc_statement", "earnings_8k", "fomc_minutes", "political_order", "political_other"]
    ok = [s for s in exp if s in rank]
    if order[:1] == ok[:1] and order[-1] == ok[-1]:
        out("Consistent with the timing hypothesis at both ends. A low political")
        out("novelty is then what the schema predicts, not a reader defect.")
    else:
        out("**NOT the expected order.** The novelty field may not be measuring")
        out("publication lag. Look at the landmark section before trusting it.")


def section_B(df):
    out("\n## B. SIGNAL CLASSES vs SOURCE BASELINE")
    out()
    out("Matched = documents whose TEXT contains the class keywords. Baseline =")
    out("the rest of the source. A matched class that reads like its baseline")
    out("means the reader is not separating operative from routine content.")
    for src, classes in CLASSES.items():
        x = df[df.source == src]
        if x.empty:
            out(f"\n### {src} — no cached reads")
            continue
        out(f"\n### {src}  (n={len(x)})")
        out()
        out("| class | n | spec | novelty | mag | eq | dur | gold | usd | oil | max\\|dir\\| | expect |")
        out("|---|---|---|---|---|---|---|---|---|---|---|---|")
        base = x
        out(f"| *baseline (all)* | {len(base)} | {fmt(base.specificity.mean())} | "
            f"{fmt(base.novelty.mean())} | {fmt(base.magnitude.mean())} | "
            + " | ".join(fmt(base[c].mean()) for c in ASSET.values())
            + f" | {fmt(base.absdir_max.mean())} | — |")
        for name, pat, expect in classes:
            m = x.text.str.contains(pat, case=False, regex=True, na=False)
            hit = x[m]
            if hit.empty:
                out(f"| {name} | 0 | | | | | | | | | | {expect} — **NO MATCHES** |")
                continue
            flag = ""
            # flag when matched |dir| is no higher than baseline on a class
            # that should carry signal
            if ">base" in expect and "|dir|" in expect and \
                    hit.absdir_max.mean() <= base.absdir_max.mean() + 0.02:
                flag = " **<-- FLAT vs baseline**"
            if "spec>base" in expect and hit.specificity.mean() <= base.specificity.mean():
                flag += " **<-- spec not above baseline**"
            out(f"| {name} | {len(hit)} | {fmt(hit.specificity.mean())} | "
                f"{fmt(hit.novelty.mean())} | {fmt(hit.magnitude.mean())} | "
                + " | ".join(fmt(hit[c].mean()) for c in ASSET.values())
                + f" | {fmt(hit.absdir_max.mean())} | {expect}{flag} |")


def section_C(df):
    out("\n## C. SIGN CONSISTENCY — where the text fixes the sign")
    out()
    out("Duration = bond PRICE in the schema, so a hike must read dur < 0 and a")
    out("cut dur > 0. This is the one place the sign is not a judgement call.")
    out()
    x = df[df.source == "fomc_statement"]
    hike = x[x.text.str.contains(r"raise the target range|increase the target range", case=False, regex=True, na=False)]
    cut = x[x.text.str.contains(r"lower the target range|reduce the target range|decrease the target range", case=False, regex=True, na=False)]
    out("| class | n | dur mean | dur>0 | dur<0 | dur=0 | stance mean | verdict |")
    out("|---|---|---|---|---|---|---|---|")
    for name, h, want in (("HIKE", hike, -1), ("CUT", cut, +1)):
        if h.empty:
            out(f"| {name} | 0 | | | | | | no matches |")
            continue
        d = h.dir_dur.dropna()
        pos, neg, zero = (d > 0.05).sum(), (d < -0.05).sum(), (d.abs() <= 0.05).sum()
        st = pd.to_numeric(h.x_stance, errors="coerce").mean()
        wrong = pos if want < 0 else neg
        right = neg if want < 0 else pos
        verdict = ("OK" if right > 2 * max(wrong, 1) else
                   "**MIXED**" if right > wrong else "**BACKWARDS**")
        if zero > right:
            verdict += " — **mostly ZERO on a decision that moves rates**"
        out(f"| {name} (want dur{'<' if want<0 else '>'}0) | {len(h)} | {fmt(d.mean())} | "
            f"{pos} | {neg} | {zero} | {fmt(st)} | {verdict} |")

    # earnings: surprise vs equity direction
    e = df[df.source == "earnings_8k"].copy()
    e["sur"] = pd.to_numeric(e.x_surprise, errors="coerce")
    e["gc"] = pd.to_numeric(e.x_guidance_change, errors="coerce")
    out()
    out("Earnings — the reader's own `extra.surprise` and `extra.guidance_change`")
    out("against its own `dir_equity`. These are the same read; they should agree.")
    out()
    out("| pair | n | corr | agree sign | disagree | either zero |")
    out("|---|---|---|---|---|---|")
    for lab, col in (("surprise vs dir_eq", "sur"), ("guidance_change vs dir_eq", "gc")):
        v = e[[col, "dir_eq"]].dropna()
        if len(v) < 5:
            out(f"| {lab} | {len(v)} | | | | |")
            continue
        nz = v[(v[col].abs() > 0.05) & (v.dir_eq.abs() > 0.05)]
        agree = (np.sign(nz[col]) == np.sign(nz.dir_eq)).sum()
        corr = v[col].corr(v.dir_eq)
        flag = " **<-- reader disagrees with itself**" if len(nz) and agree < 0.8 * len(nz) else ""
        out(f"| {lab} | {len(v)} | {fmt(corr)} | {agree} | {len(nz)-agree} | {len(v)-len(nz)} |{flag}")


def section_D(df):
    out("\n## D. WITHIN-READER CONSISTENCY")
    out()
    out("`is_decided` and `specificity` are both the reader's judgement of the same")
    out("thing. If decided documents are not more specific, the field is noise.")
    out()
    out("| source | is_decided | n | specificity | novelty | max\\|dir\\| |")
    out("|---|---|---|---|---|---|")
    for src in ("political_order", "political_other"):
        x = df[df.source == src]
        for val in (True, False):
            h = x[x.x_is_decided == val]
            if h.empty:
                out(f"| {src} | {val} | 0 | | | |")
                continue
            out(f"| {src} | {val} | {len(h)} | {fmt(h.specificity.mean())} | "
                f"{fmt(h.novelty.mean())} | {fmt(h.absdir_max.mean())} |")
        t, f_ = x[x.x_is_decided == True], x[x.x_is_decided == False]
        if len(t) and len(f_) and t.specificity.mean() <= f_.specificity.mean() + 0.05:
            out(f"| | | | **{src}: decided ≈ not decided on specificity — INCONSISTENT** | | |")

    out()
    out("FOMC — `extra.stance` (hawkish +) against `dir_duration` (price). Hawkish")
    out("should mean duration DOWN, so the correlation should be NEGATIVE.")
    out()
    for src in ("fomc_statement", "fomc_minutes"):
        x = df[df.source == src].copy()
        x["st"] = pd.to_numeric(x.x_stance, errors="coerce")
        v = x[["st", "dir_dur"]].dropna()
        if len(v) < 5:
            out(f"- {src}: n={len(v)}, too few")
            continue
        c = v.st.corr(v.dir_dur)
        verdict = "OK (negative)" if c < -0.2 else ("**NEAR ZERO — stance and duration decoupled**" if abs(c) <= 0.2 else "**POSITIVE — sign convention backwards somewhere**")
        out(f"- {src}: n={len(v)}, corr(stance, dir_dur) = {c:+.3f} → {verdict}")


def section_E(df):
    out("\n## E. LANDMARK DOCUMENTS")
    out()
    out("Named events the reader must have seen as large. Window around the")
    out("ANNOUNCEMENT date, since Federal Register publication lags it. Absent =")
    out("a COVERAGE finding. Present but routine = a READER finding.")
    out()
    out("| source | window | expectation | found | stem | spec | novelty | mag | eq | dur | gold | usd |")
    out("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for src, dt, win, kw, expect in LANDMARKS:
        d0 = datetime.strptime(dt, "%Y-%m-%d")
        x = df[(df.source == src) & df.date.notna()]
        x = x[(x.date >= d0 - timedelta(days=1)) & (x.date <= d0 + timedelta(days=win))]
        x = x[x.text.str.contains(kw, case=False, regex=True, na=False)]
        if x.empty:
            out(f"| {src} | {dt} +{win}d | {expect} | **ABSENT** | | | | | | | | |")
            continue
        r = x.sort_values("absdir_max", ascending=False).iloc[0]
        flag = ""
        if r.absdir_max < 0.15:
            flag = " **<-- read as routine**"
        out(f"| {src} | {dt} +{win}d | {expect} | {len(x)} | {r.stem} | "
            f"{fmt(r.specificity)} | {fmt(r.novelty)} | {fmt(r.magnitude)} | "
            f"{fmt(r.dir_eq)} | {fmt(r.dir_dur)} | {fmt(r.dir_gold)} | {fmt(r.dir_usd)} |{flag}")
    out()
    out("Dates in this table are from memory and should be checked against the")
    out("documents themselves. A miss may be my date, not the corpus.")


def section_F(df):
    out("\n## F. FIELD POPULATION — can step 5 use these reads?")
    out()
    out("| source | n | evidence≥1 | ticker | surprise | guidance_change | stance | is_decided | dispersion |")
    out("|---|---|---|---|---|---|---|---|---|")
    for src in SOURCES:
        x = df[df.source == src]
        if x.empty:
            continue
        def pct(col):
            if col not in x:
                return "—"
            v = x[col]
            filled = v.notna() & (v.astype(str).str.strip() != "") & (v.astype(str) != "None")
            return f"{100*filled.mean():.0f}%"
        out(f"| {src} | {len(x)} | {100*(x.n_evidence>=1).mean():.0f}% | "
            f"{pct('x_ticker')} | {pct('x_surprise')} | {pct('x_guidance_change')} | "
            f"{pct('x_stance')} | {pct('x_is_decided')} | {pct('x_dispersion')} |")
    out()
    out("Fields the source's prompt asks for should be near 100%. A field the")
    out("prompt does not ask for is expected to be blank and is not a defect.")
    tr = df[df.truncated]
    if len(tr):
        nt = df[(df.source == "earnings_8k") & ~df.truncated]
        out()
        out(f"Truncated 8-Ks (n={len(tr)}) vs whole (n={len(nt)}): specificity "
            f"{fmt(tr.specificity.mean())} vs {fmt(nt.specificity.mean())}, "
            f"confidence {fmt(tr.confidence.mean())} vs {fmt(nt.confidence.mean())}, "
            f"evidence≥1 {100*(tr.n_evidence>=1).mean():.0f}% vs "
            f"{100*(nt.n_evidence>=1).mean():.0f}%, ticker filled "
            f"{100*tr.x_ticker.notna().mean():.0f}% vs {100*nt.x_ticker.notna().mean():.0f}%.")
        out("(Confounded with document type — 6-K complete submissions vs EX-99 — as")
        out("assess_8k.py states. Reported, not adjusted for.)")


def section_G(df):
    out("\n## G. FLAT-TAIL CHECK — did ANYTHING in each source read as directional?")
    out()
    out("| source | n | any\\|dir\\|>0.05 | >0.3 | top-5 max\\|dir\\| | top-5 stems |")
    out("|---|---|---|---|---|---|")
    for src in SOURCES:
        x = df[df.source == src]
        if x.empty:
            continue
        top = x.sort_values("absdir_max", ascending=False).head(5)
        flag = ""
        if (x.absdir_max > 0.05).sum() < 0.02 * len(x):
            flag = " **<-- essentially nothing directional in the whole source**"
        out(f"| {src} | {len(x)} | {(x.absdir_max>0.05).sum()} | {(x.absdir_max>0.3).sum()} | "
            + ", ".join(f"{v:.2f}" for v in top.absdir_max)
            + " | " + ", ".join(top.stem) + f" |{flag}")


def main():
    df = load()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    out(f"# Document-read audit — every source, from cached reads")
    out(f"\n*Run {ts}. {len(df)} cached reads. No API calls. Nothing here is a*")
    out("*registered test; a flagged line is a question, not a verdict.*")
    out()
    out("Origin: the political_other aggregate (|dir| < 0.005 across 816 documents)")
    out("was interpreted as \"nothing here moves markets\" without checking whether")
    out("the documents that would falsify that — Section 232 tariff proclamations —")
    out("were present and what the reader assigned them. This applies the same")
    out("question to every source.")
    section_A(df)
    section_B(df)
    section_C(df)
    section_D(df)
    section_E(df)
    section_F(df)
    section_G(df)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(L) + "\n")
    print(f"\n-> {OUT_MD}")


if __name__ == "__main__":
    main()
