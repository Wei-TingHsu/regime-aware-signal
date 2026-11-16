"""wire_history.py -- step 2 of the agenda: can the PAST release times be collected from PR Newswire's company pages? (The other two wires refuse
scripts from this machine, docs/wire_probe.md.) Read-only probe: for each company it tries a few candidate page addresses, counts the items that carry a
clock time, counts the results releases among them, and checks whether older pages can be reached. Writes docs/wire_history_probe.md. No cost, no key.

The page addresses are CANDIDATES (Claude's guesses at how PR Newswire names each company's page); the probe shows which are real.

    python -m src.wire_history probe
"""
from __future__ import annotations
import re, time, urllib.request, urllib.error
from pathlib import Path

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
BASE = "https://www.prnewswire.com/news/{slug}/?page={page}&pagesize=100"
SLUGS = {"META": ["meta", "meta-platforms,-inc.", "facebook"], "ORCL": ["oracle", "oracle-corporation"], "AVGO": ["broadcom-inc.", "broadcom", "broadcom-limited"], "MSFT": ["microsoft-corp.", "microsoft", "microsoft-corporation"],
         "INTC": ["intel-corporation", "intel"], "MU": ["micron-technology,-inc.", "micron-technology", "micron"], "AMZN": ["amazon.com,-inc.", "amazon", "amazon.com"], "NVDA": ["nvidia", "nvidia-corporation"],
         "AMD": ["amd", "advanced-micro-devices"], "CRWD": ["crowdstrike", "crowdstrike-holdings,-inc."], "SNDK": ["sandisk", "sandisk-corporation"], "GOOG": ["alphabet-inc.", "google", "alphabet"], "TSM": ["tsmc", "taiwan-semiconductor-manufacturing-company"], "SKHY": ["sk-hynix", "sk-hynix-inc."]}
RX_ITEM = r"<small[^>]*>\s*([A-Z][a-z]{2}\s+\d{1,2},\s+\d{4},\s+\d{1,2}:\d{2}\s+ET)\s*</small>\s*(.*?)\s*</h3>"
RX_RESULTS = r"\b(reports?|announces?|posts?|delivers?)\b.*\b(quarter(ly)?|results|earnings)\b"; RX_NOT = r"\b(to (report|announce|host|release|webcast|present)|sets? (date|conference)|conference call|date for|schedules?|will (report|announce|host))\b"


def get(url):
    r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"}), timeout=25); return r.status, r.read(3_000_000).decode("utf-8", "ignore")


def items(html: str) -> list:
    return [(re.sub(r"\s+", " ", t), re.sub(r"<[^>]+>", "", re.sub(r"\s+", " ", title)).strip()) for t, title in re.findall(RX_ITEM, html, flags=re.S)]


def probe():
    L = ["# PR Newswire company pages: can past release times be collected?", "", "| company | page that answered | items with a clock time (page 1) | results releases among them | newest | oldest on page 1 | page 2 reachable | oldest on page 5 |", "|---|---|---|---|---|---|---|---|"]; sample = None
    for tk, slugs in SLUGS.items():
        found = None
        for slug in slugs:
            try: status, html = get(BASE.format(slug=slug, page=1))
            except urllib.error.HTTPError as e: print(f"  {tk:5} /news/{slug}/: HTTP {e.code}"); time.sleep(0.5); continue
            except Exception as e: print(f"  {tk:5} /news/{slug}/: {type(e).__name__}: {str(e)[:60]}"); time.sleep(0.5); continue
            it = items(html); time.sleep(0.5)
            if not it: print(f"  {tk:5} /news/{slug}/: HTTP {status}, {len(html) // 1000} KB, but no dated items in the layout the probe expects"); sample = sample or html; continue
            found = (slug, it); break
        if not found: L.append(f"| {tk} | none of {', '.join(slugs)} | | | | | | |"); continue
        slug, it = found; res = [x for x in it if re.search(RX_RESULTS, x[1], re.I) and not re.search(RX_NOT, x[1], re.I)]; p2 = p5 = ""
        try:
            _, h2 = get(BASE.format(slug=slug, page=2)); i2 = items(h2); p2 = f"yes, {len(i2)} items, oldest {i2[-1][0]}" if i2 and i2[0] != it[0] else ("no (same as page 1)" if i2 else "no items"); time.sleep(0.5)
            _, h5 = get(BASE.format(slug=slug, page=5)); i5 = items(h5); p5 = i5[-1][0] if i5 and i5[0] != it[0] else "not reachable"
        except Exception as e: p2 = p2 or f"{type(e).__name__}"
        print(f"  {tk:5} /news/{slug}/: {len(it)} dated items, {len(res)} results releases; newest {it[0][0]}; oldest on page 1 {it[-1][0]}; page 2: {p2}; page 5 oldest: {p5}")
        for x in res[:2]: print(f"          e.g. {x[0]} | {x[1][:90]}")
        L.append(f"| {tk} | /news/{slug}/ | {len(it)} | {len(res)}" + (f" (e.g. {res[0][0]}: {res[0][1][:60]})" if res else "") + f" | {it[0][0]} | {it[-1][0]} | {p2} | {p5} |"); time.sleep(0.5)
    if sample:
        m = re.search(r"\d{1,2}:\d{2}\s+ET", sample); a = max(0, (m.start() if m else 3000) - 500); print("\nA page answered but its layout was not recognised. A piece of it, for Claude to adjust the probe:\n" + re.sub(r"\s+", " ", sample[a:a + 1100]))
    Path("docs").mkdir(exist_ok=True); Path("docs/wire_history_probe.md").write_text("\n".join(L) + "\n"); print("-> docs/wire_history_probe.md")


if __name__ == "__main__": probe()
