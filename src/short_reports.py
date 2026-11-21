"""short_reports.py -- SR-1: do the short-report publishers move the price of the company they write about? (founder, 20 Nov 2026; order of work:
public calls, then short reports, then the sell-off study)

    python -m src.short_reports collect      # each publisher's own list of reports, with the publisher's own date AND time. Free.
    python -m src.short_reports times        # audit BEFORE any test: do these lists carry a real time of day? (the fault of SR-2b is not repeated)
    python -m src.short_reports cost         # what the reading step would cost. Nothing is read.
    python -m src.short_reports extract --max-usd 5     # Claude reads each item: is it a report, on which company, long or short, how serious
    python -m src.short_reports reports      # one row per report and target -> data_provenance/short_reports/reports.csv

Publishers whose own list answers a script (docs/source_probe.md, 20 Nov): Hindenburg Research (archive, to 2017), Grizzly Research (to 2020),
Blue Orca (to 2011), Fuzzy Panda (10 newest), Hunterbrook (20 newest). The others refuse scripts and are not worked around.
All are THIRD PARTIES who may hold a position against (or in) the company: claims unverified. No prices are touched in this file's commands above;
the price test is registered in TRACK before it is added."""
from __future__ import annotations
import argparse, hashlib, json, re, time, urllib.error
from pathlib import Path
import pandas as pd
from src.news_listener import fetch, feed_items

ROOT = Path("data_provenance/short_reports"); RAW = ROOT / "raw"; READS = ROOT / "reads"; PV = "short-v1-2026-11-21"; IN_RATE, OUT_RATE = 2.0, 10.0
PUBLISHERS = {"hindenburg": ("Hindenburg Research", "https://hindenburgresearch.com/feed/", True), "grizzly": ("Grizzly Research", "https://grizzlyreports.com/feed/", True), "blueorca": ("Blue Orca", "https://www.blueorcacapital.com/feed/", True),
              "fuzzypanda": ("Fuzzy Panda", "https://fuzzypandaresearch.com/feed/", False), "hunterbrook": ("Hunterbrook", "https://newsletter.hntrbrk.com/feed", False)}      # slug: (name, feed, pages back with ?paged=N)
SYS = """You are given ONE item from the website of a firm that publishes investment research and may hold a position (often a short position) in the
companies it writes about. Its claims are unverified. Do not judge whether they are true. Return STRICT JSON, no preamble:
{"is_report": true if this item is the firm's own research piece or investigation taking a position on one or more listed companies; false for media
   coverage of the firm, replies to a company's response, legal or personal notes, announcements, translations of an earlier item,
 "targets": [{"company": name, "ticker": the ticker as listed (null if not sure), "exchange": e.g. "NASDAQ", "NYSE", "HKEX", "TSE", "TPEx", "LSE" (null if not sure),
              "yahoo_symbol": the symbol Yahoo Finance uses, e.g. "NVDA", "0700.HK", "6963.T", "3293.TWO" (null if not sure),
              "direction": -1 if the firm is negative / short, 1 if positive / long,
              "first": true if the item presents itself as this firm's first report on this company, false if it follows up an earlier report}],
 "claim": one of "fraud or accounting" | "product or technology" | "regulatory or legal" | "governance or insiders" | "valuation" | "other",
 "severity": 0.0-1.0, how serious the allegation is AS STATED (1.0 = says the company is a fraud or worthless; 0.2 = says it is overvalued),
 "summary": at most 25 words}
If is_report is false, return "targets": []."""


def _load(slug):
    f = RAW / f"{slug}.json"; return json.loads(f.read_text()) if f.exists() else []


def cmd_collect():
    RAW.mkdir(parents=True, exist_ok=True)
    for slug, (name, url, pages) in PUBLISHERS.items():
        have = {r["id"]: r for r in _load(slug)}; before = len(have); first_id = None; note = ""; run_ids = set()
        for pg in range(1, 121 if pages else 2):
            try: items = feed_items(fetch(url + (f"?paged={pg}" if pg > 1 else ""), timeout=25))
            except urllib.error.HTTPError as e: note = f"stopped at page {pg} (HTTP {e.code})"; break
            except Exception as e: note = f"stopped at page {pg} ({type(e).__name__})"; break
            if not items or (pg > 1 and items[0]["id"] == first_id) or all(it["id"] in run_ids for it in items): note = f"last page {pg - 1}"; break
            run_ids |= {it["id"] for it in items}
            if pg == 1: first_id = items[0]["id"]
            for it in items:
                if it.get("published") is not None: have[it["id"]] = dict(id=it["id"], title=it["title"], link=it["link"], published=it["published"].isoformat(), summary=it["summary"][:6000])
            time.sleep(1.0)
        rows = sorted(have.values(), key=lambda r: r["published"]); (RAW / f"{slug}.json").write_text(json.dumps(rows, indent=1))
        print(f"  {name}: {len(rows)} items" + (f", {rows[0]['published'][:10]} to {rows[-1]['published'][:10]}" if rows else "") + f" ({len(rows) - before} new now; {note or 'one page only'})")
    print(f"done. No cost. -> {RAW}")


def cmd_times():
    """Before any test: is the time of day real? A list that stamps every item at midnight or on the hour gives a DATE only."""
    L = ["# SR-1: do the publishers' lists carry a real time of day?", "", "Times are the publisher's own (the feed's pubDate), shown in New York time. 'On the exact minute' = seconds are 00; 'on the exact hour' = minutes and seconds are 00; "
         "many of either means the time is typed or rounded, not a real clock. Session = 09:30 to 16:00 New York, Monday to Friday.", "", "| publisher | items | from | to | exactly midnight | on the exact hour | seconds not 00 | before the open | during the session | after the close | weekend |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for slug, (name, _, _) in PUBLISHERS.items():
        R = _load(slug)
        if not R: L.append(f"| {name} | 0 | | | | | | | | | |"); print(f"  {name}: nothing collected"); continue
        t = pd.to_datetime([r["published"] for r in R], utc=True); ny = t.tz_convert("America/New_York"); hm = ny.hour * 60 + ny.minute; wk = ny.dayofweek >= 5
        mid = ((t.hour == 0) & (t.minute == 0) & (t.second == 0)) | ((ny.hour == 0) & (ny.minute == 0) & (ny.second == 0)); onh = (t.minute == 0) & (t.second == 0); sec = t.second != 0
        pre = ~wk & (hm < 570); dur = ~wk & (hm >= 570) & (hm < 960); aft = ~wk & (hm >= 960); p = lambda m: f"{m.mean():.0%}"
        L.append(f"| {name} | {len(R)} | {ny.min():%Y-%m-%d} | {ny.max():%Y-%m-%d} | {p(mid)} | {p(onh)} | {p(sec)} | {p(pre)} | {p(dur)} | {p(aft)} | {p(wk)} |")
        print(f"  {name}: {len(R)} items, {ny.min():%Y-%m-%d} to {ny.max():%Y-%m-%d}; exactly midnight {p(mid)}; on the exact hour {p(onh)}; seconds not 00 {p(sec)}; before the open {p(pre)}, during the session {p(dur)}, after the close {p(aft)}, weekend {p(wk)}")
    Path("docs").mkdir(exist_ok=True); Path("docs/short_reports_times.md").write_text("\n".join(L) + "\n"); print("-> docs/short_reports_times.md")


def _key(slug, r): return READS / f"{slug}_{hashlib.sha1(r['id'].encode()).hexdigest()[:12]}__{PV}.json"


def _body(name, r): return f"Firm: {name}\nPublished: {r['published'][:16]}\nTitle: {r['title']}\n\nText (beginning):\n{r['summary'][:3000]}"


def cmd_cost():
    n = todo = chars = 0
    for slug, (name, _, _) in PUBLISHERS.items():
        for r in _load(slug):
            n += 1
            if not _key(slug, r).exists(): todo += 1; chars += len(SYS) + len(_body(name, r))
    tin = chars / 3.6; lo = tin / 1e6 * IN_RATE + todo * 150 / 1e6 * OUT_RATE; hi = tin / 1e6 * IN_RATE + todo * 900 / 1e6 * OUT_RATE
    print(f"{n} items collected; {todo} still to read. Cost of reading them: between about US${lo:.2f} and US${hi:.2f} (the answer's length is the unknown; the last estimate of this kind was half the true figure, so the upper number assumes long answers). Nothing was read.")


def cmd_extract(max_usd: float):
    from src.news_events2 import _client, _parse, MODEL
    client = _client(); READS.mkdir(parents=True, exist_ok=True); tin = tout = n = bad = 0; cost = lambda: tin / 1e6 * IN_RATE + tout / 1e6 * OUT_RATE; stop = False
    for slug, (name, _, _) in PUBLISHERS.items():
        for r in _load(slug):
            out = _key(slug, r)
            if out.exists(): continue
            try:
                a = client.messages.create(model=MODEL, max_tokens=1500, system=SYS, messages=[{"role": "user", "content": _body(name, r)}]); t = "".join(b.text for b in a.content if b.type == "text"); tin += a.usage.input_tokens; tout += a.usage.output_tokens
                d = _parse(t); out.write_text(json.dumps(dict(slug=slug, publisher=name, id=r["id"], title=r["title"], link=r["link"], published=r["published"], model=MODEL, prompt_version=PV, read=d), indent=1)); n += 1
            except Exception as e: bad += 1; print(f"  {name}: {r['title'][:60]}: {type(e).__name__}: {str(e)[:90]}")
            if n and n % 50 == 0: print(f"  {n} items read, about US${cost():.2f}")
            if cost() >= max_usd: print(f"  cap US${max_usd:.2f} reached after {n} items; run again to continue"); stop = True; break
        if stop: break
    left = sum(1 for slug in PUBLISHERS for r in _load(slug) if not _key(slug, r).exists())
    print(f"done: {n} items read now, {bad} failed now, {left} still unread, about US${cost():.2f} -> {READS}")


def cmd_reports():
    rows = []; items = 0; not_report = 0
    for f in sorted(READS.glob(f"*__{PV}.json")):
        d = json.loads(f.read_text()); r = d.get("read") or {}; items += 1
        if not r.get("is_report"): not_report += 1; continue
        for x in (r.get("targets") or []):
            if not isinstance(x, dict): continue
            try: dr = int(x.get("direction") or 0)
            except Exception: dr = 0
            sym = str(x.get("yahoo_symbol") or x.get("ticker") or "").upper().strip()
            if dr not in (1, -1) or not re.fullmatch(r"[A-Z0-9][A-Z0-9.\-]{0,9}", sym): continue
            try: sev = float(r.get("severity"))
            except Exception: sev = None
            rows.append(dict(publisher=d["publisher"], published=d["published"], symbol=sym, company=x.get("company"), exchange=x.get("exchange"), direction=dr, first=bool(x.get("first")), claim=r.get("claim"), severity=sev, title=d["title"], link=d["link"], summary=r.get("summary")))
    if not rows: print("no report extracted yet"); return
    R = pd.DataFrame(rows).sort_values("published"); R["us_listed"] = ~R.symbol.str.contains(r"\.", regex=True); ROOT.mkdir(parents=True, exist_ok=True); R.to_csv(ROOT / "reports.csv", index=False)
    print(f"{items} items read; {not_report} are not reports; {len(R)} report-and-company rows ({(R.direction < 0).sum()} negative, {(R.direction > 0).sum()} positive; {R['first'].sum()} first reports; {R.us_listed.sum()} on US-listed companies), {R.symbol.nunique()} companies, {R.published.min()[:7]} to {R.published.max()[:7]}")
    print("by publisher (rows; first reports; negative): " + ", ".join(f"{k} {len(g)}; {int(g['first'].sum())}; {(g.direction < 0).sum()}" for k, g in R.groupby("publisher"))); print(f"-> {ROOT / 'reports.csv'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["collect", "times", "cost", "extract", "reports"]); ap.add_argument("--max-usd", type=float, default=5.0); a = ap.parse_args()
    {"collect": cmd_collect, "times": cmd_times, "cost": cmd_cost, "extract": lambda: cmd_extract(a.max_usd), "reports": cmd_reports}[a.cmd]()
