"""public_calls.py -- test SR-2 (TRACK 3.74, 3.76): when a well-known investor makes a public call on a stock, how does the stock move on the day and on
each of the next seven sessions, and does it move more when two or more of them call the same way within two weeks ("sensational fear")?

Stage B, steps in this file (no price is touched here):
    collect   dated news headlines about each investor, month by month, from Google News' free search feed (no key, no cost)
    cost      how many headlines there are and what reading them with Claude would cost. Reads nothing.
    extract   Claude reads the headlines in batches and lists the calls: who, which stock, which direction, new or a re-telling
    calls     merges re-tellings into one call per (investor, stock, direction) and writes data_provenance/public_calls/calls.csv

    python -m src.public_calls collect [--start 2018-01]
    python -m src.public_calls cost
    python -m src.public_calls extract --max-usd 15
    python -m src.public_calls calls
"""
from __future__ import annotations
import argparse, json, re, time, urllib.parse, urllib.request
from pathlib import Path
import pandas as pd
from src.news_listener import feed_items, UA

ROOT = Path("data_provenance/public_calls"); RAW = ROOT / "raw"; READS = ROOT / "reads"; PV = "calls-v1-2026-11-20"; BATCH = 40; IN_RATE, OUT_RATE = 2.0, 10.0
INVESTORS = {"burry": ('"Michael Burry" OR "Scion Asset Management"', "Michael Burry"), "buffett": ('"Warren Buffett" OR "Berkshire Hathaway"', "Warren Buffett"), "soros": ('"George Soros" OR "Soros Fund Management"', "George Soros"),
             "ackman": ('"Bill Ackman" OR "Pershing Square"', "Bill Ackman"), "dalio": ('"Ray Dalio" OR "Bridgewater Associates"', "Ray Dalio"), "wood": ('"Cathie Wood" OR "ARK Invest"', "Cathie Wood"), "icahn": ('"Carl Icahn" OR "Icahn Enterprises"', "Carl Icahn")}
GNEWS = "https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
RX_KEEP = r"short|bet|stake|buy|bought|sell|sold|dump|trim|exit|position|\bputs?\b|\bcalls?\b|warn|bubble|13f|disclos|\badds?\b|boost|\bcuts?\b|load|bear|bull|stock|shares|invest"
SYS = """You are given numbered news headlines (with date and publisher) about one well-known investor. List every headline that reports a CALL: the
investor (or the fund they run) taking, holding, adding to, cutting or closing a position in, or publicly stating a view on, ONE specific listed company,
exchange-traded fund or share index. Skip headlines about the market in general with no named security, about the investor's life, politics or
philanthropy, and opinion pieces that only mention the investor. Return STRICT JSON, no preamble:
{"calls": [{"i": the headline's number, "ticker": the US ticker of the security (use SPY for the S&P 500, QQQ for the Nasdaq-100; null if you are not sure of the ticker),
  "company": its name, "direction": 1 if the call is positive for the security (buys, adds, long, praises) or -1 if negative (shorts, buys puts, sells, exits, warns),
  "kind": "statement" | "position disclosed in a filing" | "position reported by the media",
  "new": true if the headline reports the call as news of that day, false if it re-tells an older call or discusses it afterwards}]}
One headline can give several entries when it names several securities. If no headline reports a call, return {"calls": []}."""


def _months(start: str):
    m = pd.Period(start, "M"); end = pd.Timestamp.now().to_period("M")
    while m <= end: yield m; m += 1


def cmd_collect(start: str):
    RAW.mkdir(parents=True, exist_ok=True); n_new = fails = 0
    for slug, (q, name) in INVESTORS.items():
        got = 0
        for m in _months(start):
            f = RAW / f"{slug}_{m}.json"
            if f.exists() and m < pd.Timestamp.now().to_period("M"): got += len(json.loads(f.read_text())); continue
            query = f"({q}) after:{m.start_time:%Y-%m-%d} before:{(m + 1).start_time:%Y-%m-%d}"
            for attempt in range(3):
                try:
                    body = urllib.request.urlopen(urllib.request.Request(GNEWS.format(q=urllib.parse.quote(query)), headers={"User-Agent": UA}), timeout=25).read(4_000_000); it = feed_items(body); srcs = re.findall(r"<source[^>]*>([^<]+)</source>", body.decode("utf-8", "ignore"))
                    rows = [dict(title=x["title"], published=str(x["published"]), link=x["link"], source=srcs[k] if k < len(srcs) else "") for k, x in enumerate(it) if x["published"] is not None and m.start_time.tz_localize("UTC") - pd.Timedelta(days=1) <= x["published"] <= (m + 1).start_time.tz_localize("UTC") + pd.Timedelta(days=1)]
                    f.write_text(json.dumps(rows)); got += len(rows); n_new += 1; break
                except Exception as e:
                    if attempt == 2: fails += 1; print(f"  {name} {m}: {type(e).__name__}: {str(e)[:70]}")
                    time.sleep(8 * (attempt + 1))
            time.sleep(1.2)
        print(f"  {name}: {got} dated headlines from {start}")
    print(f"done: {n_new} months fetched now, {fails} failed (run again to retry them). No cost. -> {RAW}")


def _batches():
    """(slug, month, k, [headlines]) -- headlines that pass the word filter, oldest first, without exact repeats of a title"""
    for f in sorted(RAW.glob("*.json")):
        slug, m = f.stem.rsplit("_", 1); rows = json.loads(f.read_text()); seen = set(); keep = []
        for r in sorted(rows, key=lambda r: r["published"]):
            t = re.sub(r"\s+-\s+[^-]+$", "", r["title"]).strip(); key = t.lower()
            if key in seen or not re.search(RX_KEEP, t, re.I): continue
            seen.add(key); keep.append(dict(r, title=t))
        for k in range(0, len(keep), BATCH): yield slug, m, k // BATCH, keep[k:k + BATCH]


def cmd_cost():
    B = list(_batches()); todo = [b for b in B if not (READS / f"{b[0]}_{b[1]}_{b[2]}__{PV}.json").exists()]; heads = sum(len(b[3]) for b in B)
    usd = sum((len(SYS) + sum(len(h["title"]) + 40 for h in b[3])) / 3.5 / 1e6 * IN_RATE + (150 + 45 * len(b[3]) * 0.35) / 1e6 * OUT_RATE for b in todo)
    per = pd.Series([b[0] for b in B for _ in b[3]]).value_counts() if B else pd.Series(dtype=int)
    print(f"{heads} headlines pass the word filter, in {len(B)} batches of up to {BATCH}; {len(todo)} batches still to read: about US${usd:.2f}. By investor: " + ", ".join(f"{INVESTORS[k][1]} {v}" for k, v in per.items()) + ". Nothing was read.")


def cmd_extract(max_usd: float):
    from src.news_events2 import _client, _parse, MODEL
    client = _client(); READS.mkdir(parents=True, exist_ok=True); tin = tout = 0; n = 0; cost = lambda: tin / 1e6 * IN_RATE + tout / 1e6 * OUT_RATE
    for slug, m, k, heads in _batches():
        out = READS / f"{slug}_{m}_{k}__{PV}.json"
        if out.exists(): continue
        body = f"Investor: {INVESTORS[slug][1]}\n\n" + "\n".join(f"{i}. [{str(h['published'])[:10]}; {h['source']}] {h['title']}" for i, h in enumerate(heads))
        try:
            r = client.messages.create(model=MODEL, max_tokens=3000, system=SYS, messages=[{"role": "user", "content": body}]); t = "".join(b.text for b in r.content if b.type == "text"); tin += r.usage.input_tokens; tout += r.usage.output_tokens
            d = _parse(t); calls = [dict(c, **{"published": heads[int(c["i"])]["published"], "title": heads[int(c["i"])]["title"], "source": heads[int(c["i"])]["source"], "link": heads[int(c["i"])]["link"]}) for c in (d.get("calls") or []) if isinstance(c, dict) and str(c.get("i", "")).lstrip("-").isdigit() and 0 <= int(c["i"]) < len(heads)]
            out.write_text(json.dumps(dict(slug=slug, month=m, model=MODEL, prompt_version=PV, n_headlines=len(heads), calls=calls), indent=1)); n += 1
        except Exception as e: print(f"  {slug} {m} batch {k}: {type(e).__name__}: {str(e)[:90]}")
        if n and n % 50 == 0: print(f"  {n} batches, about US${cost():.2f}")
        if cost() >= max_usd: print(f"  cap US${max_usd:.2f} reached after {n} batches; run again to continue"); break
    print(f"done: {n} batches read now, about US${cost():.2f} -> {READS}")


def cmd_calls():
    rows = []
    for f in sorted(READS.glob(f"*__{PV}.json")):
        d = json.loads(f.read_text())
        for c in d["calls"]:
            tk = str(c.get("ticker") or "").upper().strip().replace("$", "")
            try: dr = int(c.get("direction") or 0)
            except Exception: dr = 0
            if not re.fullmatch(r"[A-Z][A-Z.\-]{0,5}", tk) or dr not in (1, -1): continue
            rows.append(dict(investor=INVESTORS[d["slug"]][1], ticker=tk, company=c.get("company"), direction=dr, kind=c.get("kind"), new=bool(c.get("new")), published=pd.to_datetime(c["published"], utc=True), source=c.get("source"), title=c.get("title")))
    H = pd.DataFrame(rows)
    if H.empty: print("no calls extracted yet"); return
    H = H.sort_values("published"); out = []
    for (inv, tk, dr), g in H.groupby(["investor", "ticker", "direction"]):
        start = None; grp = []
        for r in g.itertuples():      # a headline within 10 days of the previous one about the same call is the same call re-told
            if start is None or (r.published - grp[-1].published).days > 10:
                if grp: out.append(_one(inv, tk, dr, grp))
                grp = []; start = r.published
            grp.append(r)
        if grp: out.append(_one(inv, tk, dr, grp))
    C = pd.DataFrame(out).sort_values("first_seen"); ROOT.mkdir(parents=True, exist_ok=True); C.to_csv(ROOT / "calls.csv", index=False); H.to_csv(ROOT / "call_headlines.csv", index=False)
    print(f"{len(H)} headlines reporting a call -> {len(C)} separate calls ({(C.direction < 0).sum()} negative, {(C.direction > 0).sum()} positive), {C.ticker.nunique()} securities, {C.first_seen.min():%Y-%m} to {C.first_seen.max():%Y-%m}")
    print("by investor (calls; negative): " + ", ".join(f"{k} {len(g)}; {(g.direction < 0).sum()}" for k, g in C.groupby("investor"))); print("most-called: " + ", ".join(f"{k} {v}" for k, v in C.ticker.value_counts().head(12).items())); print(f"-> {ROOT / 'calls.csv'}")


def _one(inv, tk, dr, grp):
    first = grp[0]; return dict(investor=inv, ticker=tk, direction=dr, first_seen=first.published, headlines=len(grp), publishers=len({x.source for x in grp}), reported_as_new=any(x.new for x in grp[:3]), kind=first.kind, first_title=first.title, first_source=first.source)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["collect", "cost", "extract", "calls"]); ap.add_argument("--start", default="2018-01"); ap.add_argument("--max-usd", type=float, default=15.0); a = ap.parse_args()
    {"collect": lambda: cmd_collect(a.start), "cost": cmd_cost, "extract": lambda: cmd_extract(a.max_usd), "calls": cmd_calls}[a.cmd]()
