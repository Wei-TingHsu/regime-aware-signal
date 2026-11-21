"""short_reports.py -- SR-1: do the short-report publishers move the price of the company they write about? (founder, 20 Nov 2026; order of work:
public calls, then short reports, then the sell-off study)

    python -m src.short_reports collect      # each publisher's own list of reports, with the publisher's own date AND time. Free.
    python -m src.short_reports times        # audit BEFORE any test: do these lists carry a real time of day? (the fault of SR-2b is not repeated)
    python -m src.short_reports cost         # what the reading step would cost. Nothing is read.
    python -m src.short_reports extract --max-usd 5     # Claude reads each item: is it a report, on which company, long or short, how serious
    python -m src.short_reports reports      # one row per report and target -> data_provenance/short_reports/reports.csv
    python -m src.short_reports test         # the registered price test (TRACK 3.84)
    python -m src.short_reports forward      # forward record of the one lead (TRACK 3.86): run collect, extract, reports first

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


# ------------------------------------------------------------------------------------------------ the price test (registered in TRACK 3.84 before any price)
N_SETS, SEED, COST_BP, MIN_N = 5000, 20261123, 30.0, 30
CC = ["day 0"] + [f"+{k}" for k in range(1, 8)] + ["day 0 to +7"]; CELLS = CC + ["gone before the open", "open to close, day 0", "first tradable point to close +7"]; JUDGED = [c for c in CELLS if c != "gone before the open"]


def _vec(L, j):
    """for day-0 session j (arrays allowed): 9 close-to-close cells, the overnight piece, open->close, and the two versions of 'first tradable point to close +7'"""
    import numpy as np
    cc = np.stack([L["cc"][j + k] for k in range(8)], axis=-1); later = cc[..., 1:].sum(axis=-1)
    return np.concatenate([cc, cc.sum(axis=-1, keepdims=True), np.stack([L["co"][j], L["oc"][j], L["oc"][j] + later, later], axis=-1)], axis=-1)      # 13 numbers


def _pick(v, pre):
    """13 numbers -> the 12 cells for one report: a report out BEFORE the open can be traded from the open; one out DURING the session only from the close"""
    import numpy as np
    out = np.concatenate([v[..., :9], v[..., 9:11], (v[..., 11:12] if pre else v[..., 12:13])], axis=-1)
    if not pre: out[..., 9:11] = np.nan
    return out


def cmd_test():
    import numpy as np
    from src.public_calls import _prices_oc, _legs
    R = pd.read_csv(ROOT / "reports.csv"); R = R[R.us_listed].copy(); n_foreign = int((~pd.read_csv(ROOT / "reports.csv").us_listed).sum())
    px, bad = _prices_oc(sorted(set(R.symbol) | {"SPY"})); G = _legs(px); rng = np.random.default_rng(SEED); rows = []
    ny = pd.to_datetime(R.published, utc=True).dt.tz_convert("America/New_York").dt.tz_localize(None); R["ny"] = ny.values
    for r in R.itertuples():
        if r.symbol not in px: continue
        idx = px[r.symbol].index; d = r.ny.normalize(); hm = r.ny.hour * 60 + r.ny.minute; i0 = int(idx.searchsorted(d + pd.Timedelta(days=1) if hm >= 960 else d))
        if i0 < 2 or i0 + 8 >= len(idx) or (idx[i0] - d).days > 6: continue
        pre = not (idx[i0] == d and 570 <= hm < 960); v = _pick(_vec(G[r.symbol], i0), pre)
        if not np.isfinite(v[:9]).all(): continue
        rows.append(dict(publisher=r.publisher, symbol=r.symbol, direction=r.direction, first=bool(r.first), claim=str(r.claim), severity=r.severity, day0=idx[i0], i0=i0, before_open=bool(pre), title=r.title, **{c: r.direction * float(x) for c, x in zip(CELLS, v)}))
    T = pd.DataFrame(rows).sort_values("day0").reset_index(drop=True)
    if T.empty: print("no report could be priced"); return
    T["cluster"] = [bool(((T.symbol == r.symbol) & (T.direction == r.direction) & (T.publisher != r.publisher) & (T.day0 < r.day0) & (T.day0 >= r.day0 - pd.Timedelta(days=14))).any()) for r in T.itertuples()]
    calls = Path("data_provenance/public_calls/calls.csv"); T["after_investor_call"] = False
    if calls.exists():
        C = pd.read_csv(calls, parse_dates=["first_seen"]); C["d"] = C.first_seen.dt.tz_convert("America/New_York").dt.tz_localize(None)
        T["after_investor_call"] = [bool(((C.ticker == r.symbol) & (C.direction == r.direction) & (C.d < r.day0) & (C.d >= r.day0 - pd.Timedelta(days=14))).any()) for r in T.itertuples()]
    busy = {}
    for tk, g in T.groupby("symbol"):
        b = np.zeros(len(px[tk]), bool)
        for i0 in g.i0: b[max(0, i0 - 20):i0 + 21] = True
        busy[tk] = b
    P = np.full((len(T), N_SETS, len(CELLS)), np.nan)      # every report: the same security and direction on 5,000 other dates
    for r in T.itertuples():
        n = len(px[r.symbol])
        if n < 60: continue
        j = rng.integers(2, n - 9, size=3 * N_SETS); v = _vec(G[r.symbol], j); ok = ~busy[r.symbol][j] & np.isfinite(v).all(axis=1); v = _pick(v[ok][:N_SETS], r.before_open); P[r.Index, :len(v)] = r.direction * v
    def stat(mask, cell):
        k = CELLS.index(cell); x = T.loc[mask, cell].to_numpy(); keep = np.isfinite(x); x = x[keep]
        if len(x) < 8: return dict(n=int(len(x)))
        lo, hi = np.quantile(x, [0.05, 0.95]); mean = float(x.mean()); S = dict(n=int(len(x)), mean=mean, median=float(np.median(x)), trimmed=float(x[(x >= lo) & (x <= hi)].mean()), hit=float((x > 0).mean()), after_cost=mean - COST_BP)
        if len(x) >= MIN_N:
            with np.errstate(all="ignore"): null = np.nanmean(P[np.flatnonzero(mask)[keep]][:, :, k], axis=0)
            S["p"] = float((null >= mean).mean())
        return S
    neg = (T.direction < 0).to_numpy(); first = T["first"].to_numpy(); yr = T.day0.dt.year.to_numpy(); sev = pd.to_numeric(T.severity, errors="coerce").to_numpy(); pubs = sorted(T.publisher.unique()); mid = int(np.median(yr[neg])) if neg.any() else 2020
    main = [("ALL negative reports", neg), ("negative, FIRST report on the company", neg & first), ("negative, follow-up report", neg & ~first)] + [(f"{k}, negative reports", neg & (T.publisher == k).to_numpy()) for k in pubs]
    extra = [("positive reports (the publisher is long)", ~neg), (f"negative, up to {mid}", neg & (yr <= mid)), (f"negative, after {mid}", neg & (yr > mid)), ("negative, out before the open", neg & T.before_open.to_numpy()), ("negative, out during the session", neg & ~T.before_open.to_numpy())] \
            + [(f"negative, severity {lab}", neg & m) for lab, m in (("0.9 or more", sev >= 0.9), ("0.7 or more", sev >= 0.7), ("0.5 or more", sev >= 0.5), ("under 0.7", sev < 0.7), ("under 0.5", sev < 0.5))] \
            + [(f"negative, claim: {k}", neg & (T.claim == k).to_numpy()) for k in sorted(T.claim.unique())] + [(f"{k}, first negative reports", neg & first & (T.publisher == k).to_numpy()) for k in pubs] \
            + [("CLUSTER: a second publisher, same company and direction, within two weeks", T.cluster.to_numpy()), ("CLUSTER: after a well-known investor's call in the same direction, within two weeks", T.after_investor_call.to_numpy())]
    judged_groups = [name for name, m in main if int(m.sum()) >= MIN_N]; bar = 0.05 / max(1, len(judged_groups) * len(JUDGED)); out = dict(bar=bar, reports=int(len(T)), foreign_left_out=n_foreign, no_prices=bad, main={}, extra={})
    def fmt(S, judged):
        if "mean" not in S: return f"n {S['n']}"
        star = "**" if judged and "p" in S and S["p"] < bar else ""; tail = f"; p {S['p']:.4f}" if "p" in S else "; under 30, not judged"
        return f"{star}{S['mean']:+.0f} bp{star} (n {S['n']}; middle {S['median']:+.0f}; without extremes {S['trimmed']:+.0f}; right {S['hit']:.0%}; after cost {S['after_cost']:+.0f}{tail})"
    M = ["# SR-1: short-report publishers -- how the company's share price moved", "",
         f"{len(T)} report-and-company rows priced (US-listed only; {n_foreign} rows on companies listed elsewhere left out of this run; {len(bad)} US symbols have no prices on Yahoo, mostly delisted). Returns in bp (1 bp = 0.01%), minus the S&P 500's same piece, "
         f"IN THE DIRECTION OF THE REPORT: for a negative report a positive number means the share FELL by that much against the market. Day 0 = the session during which, or before whose open, the report came out (the publisher's own clock time). "
         f"'day 0' and '+1' to '+7' are each one session, close to close. 'gone before the open' = previous close to the open of day 0, for reports out before that open (description: not tradable in regular hours). "
         f"'open to close, day 0' = the same reports, from that open to the close. 'first tradable point to close +7' = from the open of day 0 (report out before the open) or from the close of day 0 (report out during the session) to the close of session +7. "
         f"p = how often the same securities on {N_SETS} sets of other dates did as well. Judged groups: {len(judged_groups)}; a cell counts at p < {bar:.5f}. Cost {COST_BP:.0f} bp a round trip is an assumption and does NOT include the fee to borrow the shares for a short sale.", ""]
    for title, groups, key in (("Main groups", main, "main"), ("Splits (description; the bar does not apply)", extra, "extra")):
        M += [f"## {title}", "", "| group | " + " | ".join(CELLS) + " |", "|---|" + "---|" * len(CELLS)]
        for name, mask in groups:
            S = {c: stat(mask, c) for c in CELLS}; out[key][name] = S; M.append(f"| {name} ({int(mask.sum())}) | " + " | ".join(fmt(S[c], key == "main" and c in JUDGED) for c in CELLS) + " |")
            sh = lambda c: (f"{S[c]['mean']:+.0f}" + (f" (p {S[c]['p']:.4f}{' PASS' if key == 'main' and S[c]['p'] < bar else ''})" if "p" in S[c] else "")) if "mean" in S[c] else "n/a"
            print(f"  {name} ({int(mask.sum())}): day 0 {sh('day 0')}; " + "; ".join(f"+{k} {sh(f'+{k}')}" for k in range(1, 8)) + f"; day 0 to +7 {sh('day 0 to +7')} | gone before the open {sh('gone before the open')}; open->close day 0 {sh('open to close, day 0')}; first tradable point to close +7 {sh('first tradable point to close +7')}")
        M.append("")
    Path("docs").mkdir(exist_ok=True); Path("docs/short_reports_test.md").write_text("\n".join(M) + "\n"); Path("docs/short_reports_test.json").write_text(json.dumps(out, indent=1)); T.drop(columns=["i0"]).to_csv(ROOT / "reports_priced.csv", index=False)
    print(f"{len(T)} rows priced; {n_foreign} foreign-listed rows left out; {len(bad)} symbols without prices: {', '.join(bad[:40])}. Judged groups {len(judged_groups)}; bar p < {bar:.5f}. Numbers are in the direction of the report: for a negative report, + means the share fell. -> docs/short_reports_test.md")


# ------------------------------------------------------------------------------------------------ forward record of the one lead of SR-1 (registered in TRACK 3.86)
REGISTERED = "2026-11-21T05:00:00+00:00"      # only reports published after this moment count


def cmd_forward():
    """Lead (found after the fact in SR-1, so a hypothesis): a negative report published DURING the session is followed by a further fall in the next
    session. Counted here on reports published after the registration, from the publishers' own lists (so it does not depend on the listener being on).
    Run after: collect, extract, reports."""
    import numpy as np, yfinance as yf
    from src.public_calls import _legs
    R = pd.read_csv(ROOT / "reports.csv"); R["t"] = pd.to_datetime(R.published, utc=True); R = R[(R.t > pd.Timestamp(REGISTERED)) & (R.direction < 0) & R.us_listed].sort_values("t")
    L = ["# SR-1 forward record: negative short reports published after 21 Nov 2026", "", "Registered lead: a negative report published DURING the New York session -- sell at that session's close, buy back at the next close. "
         "Numbers in bp, minus the S&P 500, + = the share fell. The lead is judged at 30 such reports (TRACK 3.86); until then every look is interim. Reports published before the open are listed too, as the comparison.", ""]
    if R.empty: L.append("No negative report on a US-listed company has been published since the registration."); Path("docs/short_reports_forward.md").write_text("\n".join(L) + "\n"); print("no new negative report on a US-listed company since 21 Nov 2026 -> docs/short_reports_forward.md"); return
    px = {}
    for tk in sorted(set(R.symbol) | {"SPY"}):
        try:
            d = yf.download(tk, start="2026-06-01", interval="1d", progress=False, auto_adjust=True)
            if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
            d = d[["Open", "Close"]].dropna(); d.columns = ["open", "close"]; d.index = pd.DatetimeIndex(d.index).tz_localize(None)
            if len(d) >= 5: px[tk] = d
        except Exception: pass
    if "SPY" not in px: print("prices not reachable now; run again later"); return
    G = _legs(px); rows = []
    for r in R.itertuples():
        ny = r.t.tz_convert("America/New_York").tz_localize(None); d = ny.normalize(); hm = ny.hour * 60 + ny.minute; row = dict(publisher=r.publisher, symbol=r.symbol, published_ny=f"{ny:%Y-%m-%d %H:%M}", severity=r.severity, first=bool(r.first), when="", day0=np.nan, next_session=np.nan, status="no prices")
        if r.symbol in px:
            idx = px[r.symbol].index; i0 = int(idx.searchsorted(d + pd.Timedelta(days=1) if hm >= 960 else d)); row["status"] = "waiting for the session"
            if i0 < len(idx):
                row["when"] = "during the session" if (idx[i0] == d and 570 <= hm < 960) else "before the open"; g = G[r.symbol]; row["status"] = "waiting for the next close"
                if np.isfinite(g["cc"][i0]): row["day0"] = -float(g["cc"][i0])
                if i0 + 1 < len(idx) and np.isfinite(g["cc"][i0 + 1]): row["next_session"] = -float(g["cc"][i0 + 1]); row["status"] = "complete"
        rows.append(row)
    T = pd.DataFrame(rows); T.to_csv(ROOT / "forward.csv", index=False); D = T[(T.when == "during the session") & (T.status == "complete")]; B = T[(T.when == "before the open") & (T.status == "complete")]
    f = lambda x: "" if pd.isna(x) else f"{x:+.0f}"
    L += [f"**Lead so far (interim): {len(D)} of 30 reports published during the session are complete" + (f"; next session: average {D.next_session.mean():+.0f} bp, middle {D.next_session.median():+.0f} bp, the share fell on {(D.next_session > 0).mean():.0%}." if len(D) else ".") + "**",
          f"Comparison, reports published before the open: {len(B)} complete" + (f"; next session average {B.next_session.mean():+.0f} bp." if len(B) else "."), "", "| publisher | company | published (New York) | when | severity | first report | day 0 | next session | status |", "|---|---|---|---|---|---|---|---|---|"]
    L += [f"| {r.publisher} | {r.symbol} | {r.published_ny} | {r.when} | {r.severity} | {'yes' if r.first else 'no'} | {f(r.day0)} | {f(r.next_session)} | {r.status} |" for r in T.itertuples()]
    Path("docs").mkdir(exist_ok=True); Path("docs/short_reports_forward.md").write_text("\n".join(L) + "\n"); print("\n".join(L[4:6])); print(f"{len(T)} negative reports on US-listed companies since 21 Nov 2026 -> docs/short_reports_forward.md")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["collect", "times", "cost", "extract", "reports", "test", "forward"]); ap.add_argument("--max-usd", type=float, default=5.0); a = ap.parse_args()
    {"collect": cmd_collect, "times": cmd_times, "cost": cmd_cost, "extract": lambda: cmd_extract(a.max_usd), "reports": cmd_reports, "test": cmd_test, "forward": cmd_forward}[a.cmd]()
