"""lag_watch.py -- MEASURES how late each news route is, and whether the sources allow more frequent checks. It scores nothing and costs nothing.

    python -m src.lag_watch run --minutes 120      # watch for two hours, then stop by itself and write the report
    python -m src.lag_watch report                 # rebuild the report from what was logged

What it measures (founder, 21 Nov 2026: 'why would there not be a way of shortening this time lag?'):
  1. SEC, the route of the only tested rule. Two free addresses carry a new filing: (a) ONE list of the latest filings of ALL companies, (b) each
     company's own filing list (what the listener uses today: 14 requests per pass). The watch checks (a) every 5 seconds for 8-K and 6-K filings of
     the whole market -- hundreds a day, so two hours give a real sample -- and, for each new filing, checks that company's own list every 5 seconds
     until the filing shows there. Lag = first seen minus the SEC's own acceptance time, for each address.
  2. The feeds the listener already reads (PR Newswire, company newsrooms, research publishers), every 15 seconds: lag = first seen minus the time
     the feed states. Only items published AFTER the watch started are counted.
  3. Refusals (HTTP 403 / 429) at these frequencies. A source that refuses three times in a row is left alone for the rest of the run.
Run it while the US market is open or just closed (filings flow from 06:00 to 22:00 New York time, Monday to Friday). The listener can keep running."""
from __future__ import annotations
import argparse, csv, json, re, time, urllib.error
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
from src.news_listener import fetch, feed_items, FEEDS, RESEARCH, _when

OUT = Path("data_provenance/live/lag_watch.csv"); MD = Path("docs/lag_watch.md"); COLS = ["run", "source", "id", "title", "published", "first_seen", "lag_s", "own_list_seen", "own_list_lag_s", "accepted"]
SEC_LIST = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type={form}&company=&dateb=&owner=include&count=100&output=atom"
SEC_EVERY, FEED_EVERY, MAX_PENDING, GIVE_UP_S = 5, 15, 3, 600


def _now(): return datetime.now(timezone.utc)


def _write(rows):
    OUT.parent.mkdir(parents=True, exist_ok=True); new = not OUT.exists()
    with OUT.open("a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        if new: w.writeheader()
        for r in rows: w.writerow({k: r.get(k, "") for k in COLS})


def cmd_run(minutes: float):
    run = _now().strftime("%Y-%m-%dT%H:%MZ"); t0 = _now(); t_end = time.time() + minutes * 60
    feeds = [dict(name=f["name"], url=f["url"]) for f in FEEDS if f.get("kind") != "fed"] + [dict(name=r["name"], url=u) for r in RESEARCH for u in r["urls"][:1]]
    S = [dict(name=f"SEC: one list for all companies ({form})", url=SEC_LIST.format(form=form), sec=True, every=SEC_EVERY) for form in ("8-K", "6-K")] + [dict(f, sec=False, every=FEED_EVERY) for f in feeds]
    for s in S: s.update(seen=None, last=0.0, ok=0, refused=0, failed=0, streak=0, off=False)
    pending = {}; timed = set(); done = 0; nxt = time.time() + 300; own = dict(ok=0, refused=0, failed=0); n_new = 0
    print(f"watching {len(S)} addresses for {minutes:.0f} minutes: the SEC lists every {SEC_EVERY} s, the feeds every {FEED_EVERY} s. Nothing is scored; no cost. It stops by itself.")
    try:
        while time.time() < t_end:
            for s in S:
                if s["off"] or time.time() - s["last"] < s["every"]: continue
                s["last"] = time.time()
                try: items = feed_items(fetch(s["url"], timeout=15)); s["ok"] += 1; s["streak"] = 0
                except urllib.error.HTTPError as e:
                    if e.code in (403, 429): s["refused"] += 1; s["streak"] += 1
                    else: s["failed"] += 1
                    if s["streak"] >= 3: s["off"] = True; print(f"  {s['name']}: refused three times in a row (HTTP {e.code}) -- left alone for the rest of this run")
                    continue
                except SystemExit: raise
                except Exception: s["failed"] += 1; continue
                now = _now(); ids = {it["id"] for it in items}
                if s["seen"] is None: s["seen"] = ids; continue      # first look: memorise only
                rows = []
                for it in items:
                    if it["id"] in s["seen"]: continue
                    pub = it.get("published")
                    if pub is None or pub < t0: continue      # published before the watch began: its lag would only measure when we started
                    row = dict(run=run, source=s["name"], id=it["id"], title=it["title"][:120], published=pub.isoformat(), first_seen=now.isoformat(), lag_s=round((now - pub).total_seconds(), 1)); n_new += 1
                    if s["sec"]:
                        acc = re.search(r"accession-number=([\d-]+)", it["id"]); cik = re.search(r"\((\d{10})\)", it["title"])
                        if acc and cik:
                            if acc.group(1) in pending or acc.group(1) in timed: n_new -= 1; continue      # the same filing listed twice (filer and subject)
                            timed.add(acc.group(1))
                            if len(pending) < 40: pending[acc.group(1)] = dict(cik=cik.group(1), row=row, until=time.time() + GIVE_UP_S, last=0.0); continue      # written when the company's own list shows it
                    rows.append(row)
                s["seen"] |= ids
                if rows: _write(rows)
            for acc, p in sorted(pending.items(), key=lambda kv: kv[1]["last"])[:MAX_PENDING]:      # the same filing on the company's own list
                if time.time() - p["last"] < SEC_EVERY: continue
                p["last"] = time.time(); found = None
                try:
                    r = json.loads(fetch(f"https://data.sec.gov/submissions/CIK{p['cik']}.json", timeout=15))["filings"]["recent"]; own["ok"] += 1
                    if acc in r.get("accessionNumber", [])[:40]: found = _when(str(r["acceptanceDateTime"][r["accessionNumber"].index(acc)]))
                except urllib.error.HTTPError as e: own["refused" if e.code in (403, 429) else "failed"] += 1
                except SystemExit: raise
                except Exception: own["failed"] += 1
                if found is not None or time.time() > p["until"]:
                    now = _now(); row = p["row"]
                    if found is not None: row.update(own_list_seen=now.isoformat(), accepted=found.isoformat(), own_list_lag_s=round((now - found).total_seconds(), 1), lag_s=round((datetime.fromisoformat(row["first_seen"]) - found).total_seconds(), 1))
                    _write([row]); pending.pop(acc); done += 1
                time.sleep(0.15)
            if time.time() >= nxt: nxt += 300; print(f"  {(_now() - t0).total_seconds() / 60:.0f} min: {n_new} new items timed, {done} filings timed on both SEC addresses, {len(pending)} waiting")
            time.sleep(0.5)
    except KeyboardInterrupt: print("stopped by hand")
    if pending: _write([p["row"] for p in pending.values()])
    stats = dict(run=run, minutes=round((_now() - t0).total_seconds() / 60, 1), sources=[dict(name=s["name"], every_s=s["every"], answered=s["ok"], refused=s["refused"], failed=s["failed"], left_alone=s["off"]) for s in S], own_list=own)
    P = OUT.with_name("lag_watch_runs.jsonl"); P.parent.mkdir(parents=True, exist_ok=True)
    with P.open("a") as fh: fh.write(json.dumps(stats) + "\n")
    cmd_report()


def _row(name, x):
    x = pd.to_numeric(x, errors="coerce").dropna()
    if not len(x): return f"| {name} | 0 | | | | |"
    return f"| {name} | {len(x)} | {x.min():.0f} s | {x.median():.0f} s | {x.quantile(0.9):.0f} s | {x.max():.0f} s |"


def cmd_report():
    if not OUT.exists(): print("nothing logged yet"); return
    T = pd.read_csv(OUT); R = [json.loads(l) for l in OUT.with_name("lag_watch_runs.jsonl").read_text().splitlines()] if OUT.with_name("lag_watch_runs.jsonl").exists() else []
    L = ["# Lag watch: how late each news route is", "", f"{len(T)} new items timed over {len(R)} run(s), {sum(r['minutes'] for r in R):.0f} minutes in total. Lag = the moment this machine first saw the item minus the time the source states "
         "(for SEC filings: minus the SEC's own acceptance time). Only items published after a run began are counted. Nothing was scored.", "", "## SEC: the same filings on the two free addresses", "",
         "| address | filings | fastest | middle | nine in ten within | slowest |", "|---|---|---|---|---|---|"]
    S = T[T.source.str.startswith("SEC") & T.own_list_lag_s.notna()]
    L += [_row("one list for all companies (checked every 5 s)", S.lag_s), _row("the company's own list (what the listener uses; here checked every 5 s)", S.own_list_lag_s)]
    if len(S):
        d = S.own_list_lag_s - S.lag_s; L += ["", f"On the same {len(S)} filings the single list was first on {(d > 0).mean():.0%}; the middle gap is {d.median():+.0f} s (positive = the single list is earlier). " + f"{int(T[T.source.str.startswith('SEC')].own_list_lag_s.isna().sum())} filings never showed on the company's own list within {GIVE_UP_S // 60} minutes or were still waiting at the end."]
    L += ["", "## The feeds the listener reads", "", "| source | new items | fastest | middle | nine in ten within | slowest |", "|---|---|---|---|---|---|"] + [_row(k, g.lag_s) for k, g in T[~T.source.str.startswith("SEC")].groupby("source")]
    L += ["", "A feed's stated time is often the planned release minute, so a lag of under a minute can be the feed's own rounding.", "", "## Did any source refuse the more frequent checks?", "", "| run | source | checked every | answered | refused (403/429) | other failures | left alone |", "|---|---|---|---|---|---|---|"]
    for r in R:
        L += [f"| {r['run']} | {s['name']} | {s['every_s']} s | {s['answered']} | {s['refused']} | {s['failed']} | {'yes' if s['left_alone'] else 'no'} |" for s in r["sources"]] + [f"| {r['run']} | SEC: a company's own list | 5 s | {r['own_list']['ok']} | {r['own_list']['refused']} | {r['own_list']['failed']} | no |"]
    MD.parent.mkdir(exist_ok=True); MD.write_text("\n".join(L) + "\n"); print("\n".join(l for l in L if l.startswith("| ") and "---" not in l)[:6000]); print(f"-> {MD}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["run", "report"]); ap.add_argument("--minutes", type=float, default=120.0); a = ap.parse_args()
    cmd_run(a.minutes) if a.cmd == "run" else cmd_report()
