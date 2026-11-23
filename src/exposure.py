"""exposure.py -- the EXPOSURE reading (code EX-1). Founder, 22 Nov 2026: a research release about a product market (TrendForce: 'NAND prices set to fall in
2027') must be linked to companies by what each company SELLS and BUYS, read from its own annual report -- not by whether the release names the company, and
not by asking the founder. Then the release's numbers are carried into the company's income statement and free cash flow, and that size is the score.

The chain, each step on disk:
  1. PROFILE   Claude reads each company's annual report (business description, segment and product notes) -> which product markets it sells into or buys
               from, and what share of revenue or cost each is. One profile per company per fiscal year, so a release is only ever linked with the profile
               that was public BEFORE it (no hindsight).
  2. RELEASE   Claude reads each research release -> which product market, which quantity (price, volume, market size, capital spending), which direction,
               how many per cent, over what period, and whether it raises or lowers the publisher's earlier view.
  3. LINK      arithmetic, no Claude: expected change in the company's operating profit and free cash flow = share of revenue (or cost) in that market
               x the release's change, using the company's reported revenue, margins and cash flow. The score is that change as a share of revenue.
  4. TEST      registered separately before it runs: does the score tell the stock's move after the release?

THIS FILE, so far: the free steps and the cost count. Nothing is read by Claude until the founder has seen the cost.
    python -m src.exposure filings     # free: the annual reports of the basket's technology companies from the SEC -> data_provenance/exposure/filings
    python -m src.exposure texts       # free: the full text of the TrendForce releases -> data_provenance/trendforce/text
    python -m src.exposure cost        # counts what steps 1 and 2 would cost; reads nothing
"""
from __future__ import annotations
import argparse, html, json, os, re, time
from pathlib import Path
import pandas as pd

ROOT = Path("data_provenance/exposure"); FIL = ROOT / "filings"; TF = Path("data_provenance/trendforce"); TXT = TF / "text"; DOCS = Path("docs"); PV = "EX1-v1"; FIRST_YEAR = 2007; CAP = 90_000
SECTORS = ("semiconductors", "computers and equipment"); ANNUAL = ("10-K", "10-K405", "20-F", "40-F")
MARKETS = ["NAND flash", "DRAM", "high-bandwidth memory (HBM)", "enterprise solid-state drives", "hard disk drives", "foundry wafers, leading edge", "foundry wafers, mature nodes", "AI accelerators and AI servers", "general servers",
           "PCs and notebooks", "smartphones", "networking and optical parts", "semiconductor equipment", "displays and panels", "cloud capital spending", "automotive chips", "other"]
SYS_PROFILE = """You are given parts of one listed company's ANNUAL REPORT (its business description and its notes on segments and products). Build a profile of what
the company sells and what it buys, for linking outside research about PRODUCT MARKETS to this company's income statement. Use ONLY what the text says; do
not use anything you know from elsewhere, and nothing from after the report's date.
Product markets (use these names exactly): """ + "; ".join(MARKETS) + """.
Reply with JSON only:
{"fiscal_year_end": "YYYY-MM-DD or empty", "revenue_usd_millions": number or null,
 "sells": [{"market": one of the names, "product_in_report": the report's own words for it, "share_of_revenue_pct": number or null,
            "share_is": "stated in the report" | "computed from stated figures" | "estimated from the description", "evidence": a quote of at most 25 words}],
 "buys":  [{"market": one of the names, "what": the report's own words, "share_of_cost_pct": number or null, "share_is": same choices, "evidence": quote of at most 25 words}],
 "priced_by_market": true if the report says its selling prices follow market or contract prices for the product (commodity-like), else false,
 "note": at most 40 words on anything that limits this profile}
Rules: list a market only if the report supports it. Shares in "sells" should add up to about 100 when the report allows; use "other" for the rest. If the
report gives no figure, estimate only when the description clearly supports it and say so in share_is; otherwise null."""
SYS_RELEASE = """You are given one press release from a market-research firm. Extract what it says about PRODUCT MARKETS, for linking to companies' income statements.
The firm is a third party; do not judge whether it is right, and do not use anything you know about what happened afterwards.
Product markets (use these names exactly): """ + "; ".join(MARKETS) + """.
Reply with JSON only:
{"statements": [{"market": one of the names, "quantity": "price" | "volume" | "market revenue" | "capital spending" | "supply" | "demand",
                 "direction": "up" | "down" | "flat", "change_pct": number or null (negative for down; the midpoint if a range is given),
                 "period": the period the change refers to, in the release's words, "kind": "forecast" | "report of what already happened",
                 "against_its_earlier_view": "raised" | "lowered" | "first statement" | "unchanged" | "not said", "evidence": quote of at most 25 words}],
 "companies_named": [names exactly as written], "summary": at most 30 words}
Rules: one statement per market and quantity; take the most forward-looking figure when several periods are given, and say which period. No statement
without a quote from the release."""


def _strip(h: str) -> str:
    h = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", h); h = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</tr>|</h\d>", "\n", h); h = html.unescape(re.sub(r"<[^>]+>", " ", h)); return re.sub(r"[ \t\xa0]+", " ", re.sub(r"\n\s*\n+", "\n", h)).strip()


def _sections(t: str) -> str:
    """the business description (the longest stretch from an 'Item 1 / Item 4' heading to the next item) and short windows around product and segment tables"""
    low = t.lower(); best = (0, 0)
    for a_rx, b_rx in ((r"item\s+1\s*[\.\:\-–—]?\s*business", r"item\s+1a\s*[\.\:\-–—]?\s*risk|item\s+2\s*[\.\:\-–—]?\s*properties"), (r"item\s+4\s*[\.\:\-–—]?\s*information on the company", r"item\s+4a|item\s+5\s*[\.\:\-–—]?\s*operating")):
        ends = [m.start() for m in re.finditer(b_rx, low)]
        for m in re.finditer(a_rx, low):
            e = next((x for x in ends if x > m.end() + 2000), None)
            if e and e - m.start() > best[1] - best[0]: best = (m.start(), e)
    body = t[best[0]:best[1]][:60_000] if best[1] else t[:60_000]; wins = []; used = 0
    for m in re.finditer(r"(revenues?|net sales) by (product|technology|segment|end market|business|platform|geograph)|disaggregat\w+ of revenue|by product line|reportable segments?", low):
        if m.start() < best[1] or (wins and m.start() < wins[-1][1]): continue
        wins.append((max(0, m.start() - 400), m.start() + 3200)); used += 3600
        if used > CAP - len(body): break
    return (body + "\n\n[NOTES ON SEGMENTS AND PRODUCTS]\n" + "\n...\n".join(t[a:b] for a, b in wins))[:CAP]


def _companies() -> pd.DataFrame:
    from src.selloff_study import CHAIN, _stocks
    from src.selloff_inputs import sector_of
    meta = Path("data_provenance/selloff/sec/companies.csv"); M = pd.read_csv(meta, dtype=str) if meta.exists() else pd.DataFrame(columns=["ticker", "cik", "sic", "name"])
    M["sector"] = M.sic.map(sector_of) if len(M) else []; pick = M[M.ticker.isin(CHAIN) | M.sector.isin(SECTORS)].copy(); miss = [t for t in CHAIN if t not in set(pick.ticker)]
    if miss: print(f"  AI-chain stocks with no SEC record on disk (they file elsewhere or were not found): {miss}")
    return pick[pick.ticker.isin(_stocks())].sort_values("ticker")


def cmd_filings():
    import src.ai_earnings as A
    FS = A._sec(); C = _companies(); FIL.mkdir(parents=True, exist_ok=True); idx = ROOT / "filings.csv"; old = pd.read_csv(idx, dtype=str) if idx.exists() else pd.DataFrame(columns=["ticker", "form", "filed", "period", "accession", "chars"]); rows = old.to_dict("records"); have = set(old.accession); new = 0; bad = []
    print(f"  {len(C)} companies: {', '.join(C.ticker)}")
    for r in C.itertuples():
        try:
            sub = json.loads(FS.get(FS.SUBS.format(cik=r.cik))); time.sleep(0.15); parts = [sub["filings"]["recent"]]
            for f in sub["filings"].get("files", []): parts.append(json.loads(FS.get("https://data.sec.gov/submissions/" + f["name"]))); time.sleep(0.15)
            for p in parts:
                for form, acc, doc, filed, per in zip(p["form"], p["accessionNumber"], p["primaryDocument"], p["filingDate"], p["reportDate"]):
                    if form not in ANNUAL or filed[:4] < str(FIRST_YEAR) or acc in have or not doc: continue
                    raw = FS.get(f"https://www.sec.gov/Archives/edgar/data/{int(r.cik)}/{acc.replace('-', '')}/{doc}"); time.sleep(0.15); raw = raw.decode("utf-8", "ignore") if isinstance(raw, (bytes, bytearray)) else raw
                    t = _sections(_strip(raw)); (FIL / f"{r.ticker}_{filed}.txt").write_text(t); rows.append(dict(ticker=r.ticker, form=form, filed=filed, period=per, accession=acc, chars=len(t))); have.add(acc); new += 1
        except Exception as e: bad.append(f"{r.ticker} ({type(e).__name__})")
        pd.DataFrame(rows).to_csv(idx, index=False)
    R = pd.DataFrame(rows); 
    if not len(R): print("  no annual report found -- tell Claude"); return
    R["chars"] = R.chars.astype(int); short = R[R.chars < 8000]
    print(f"{len(R)} annual reports on disk ({new} new now), {R.filed.min()[:4]} to {R.filed.max()[:4]}, {R.ticker.nunique()} companies; failed: {bad or 'none'}. Reports where under 8,000 characters could be cut out (the business section was not found): {len(short)}" + (f" -- {', '.join(short.ticker + ' ' + short.filed.str[:4])[:300]}" if len(short) else "") + f". No cost. -> {FIL}")
    print("  per company: " + ", ".join(f"{t} {len(g)}" for t, g in R.groupby("ticker")))


def cmd_texts(limit: int | None):
    from src.news_listener import fetch
    R = pd.read_csv(TF / "releases.csv", dtype=str); TXT.mkdir(parents=True, exist_ok=True); n = bad = 0; todo = [r for r in R.itertuples() if not (TXT / f"{r.id}.txt").exists()][:limit]
    for k, r in enumerate(todo):
        try:
            t = _strip(fetch(r.url).decode("utf-8", "ignore")); i = t.find(r.title[:40]); j = min([x for x in (t.find("Previous Article"), t.find("Next Article"), t.find("Related Articles"), t.find("Subject\n")) if x > i > -1] or [len(t)]); t = t[max(0, i):j][:12_000]
            if len(t) < 300: bad += 1; continue
            (TXT / f"{r.id}.txt").write_text(t); n += 1
        except Exception: bad += 1
        if (k + 1) % 100 == 0: print(f"  {k + 1} of {len(todo)}")
        time.sleep(0.5)
    have = [f for f in TXT.glob("*.txt")]; sizes = [f.stat().st_size for f in have]
    print(f"{len(have)} of {len(R)} releases have their text on disk ({n} fetched now, {bad} failed or too short -- run again to retry); typical length {int(pd.Series(sizes).median()) if sizes else 0} characters. No cost. -> {TXT}")


def cmd_cost():
    from src.short_reports import IN_RATE, OUT_RATE
    F = pd.read_csv(ROOT / "filings.csv") if (ROOT / "filings.csv").exists() else pd.DataFrame(columns=["chars"]); T = [f.stat().st_size for f in TXT.glob("*.txt")] if TXT.exists() else []
    def rng(chars, n, sys, out_lo, out_hi): tin = (chars + n * len(sys)) / 3.6; return tin / 1e6 * IN_RATE + n * out_lo / 1e6 * OUT_RATE, tin / 1e6 * IN_RATE + n * out_hi / 1e6 * OUT_RATE
    a = rng(float(F.chars.sum()), len(F), SYS_PROFILE, 500, 1500); b = rng(float(sum(T)), len(T), SYS_RELEASE, 250, 800)
    L = [f"Step 1, company profiles: {len(F)} annual reports of {F.ticker.nunique() if len(F) else 0} companies, {F.chars.sum() / 1e6:.1f} million characters -> between about US${a[0]:.0f} and US${a[1]:.0f}.",
         f"Step 2, releases: {len(T)} TrendForce releases, {sum(T) / 1e6:.1f} million characters -> between about US${b[0]:.0f} and US${b[1]:.0f}.",
         f"Both: between about US${a[0] + b[0]:.0f} and US${a[1] + b[1]:.0f}. Step 3 (the link to the income statement) is arithmetic and costs nothing.",
         "Cheaper first step, if wanted: only the annual reports of the last 8 years and the releases since 2018 (the period the stocks of the list have prices and funds for): about " + (f"US${(a[0] * (F.filed.astype(str).str[:4].astype(int) >= 2018).mean() + b[0] * 0.55):.0f} to US${(a[1] * (F.filed.astype(str).str[:4].astype(int) >= 2018).mean() + b[1] * 0.55):.0f}." if len(F) else "n/a.")]
    print("\n".join(L)); print("Nothing was read by Claude. (Earlier estimates of this kind were up to half the true figure; the upper numbers assume long answers.)")
    DOCS.mkdir(exist_ok=True); (DOCS / "exposure_cost.md").write_text("# Exposure reading (EX-1): what the two reading steps would cost\n\n" + "\n\n".join(L) + f"\n\nPrompt version {PV}. Nothing was read.\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["filings", "texts", "cost"]); ap.add_argument("--limit", type=int, default=None); a = ap.parse_args()
    if a.cmd == "filings":
        if not os.environ.get("SEC_CONTACT"): raise SystemExit("SEC_CONTACT is not set (the SEC asks every script to say who is calling)")
        cmd_filings()
    elif a.cmd == "texts": cmd_texts(a.limit)
    else: cmd_cost()
