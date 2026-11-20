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
    python -m src.public_calls test          # daily prices from Yahoo (free) -> docs/public_calls_test.md
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


def _read_batch(client, model, parse, slug, heads, tok):
    """one batch -> list of calls (numbered within this batch). If the answer is not valid JSON the batch is read again in two halves (down to 10 headlines)."""
    body = f"Investor: {INVESTORS[slug][1]}\n\n" + "\n".join(f"{i}. [{str(h['published'])[:10]}; {h['source']}] {h['title']}" for i, h in enumerate(heads))
    r = client.messages.create(model=model, max_tokens=8000, system=SYS, messages=[{"role": "user", "content": body}]); t = "".join(x.text for x in r.content if x.type == "text"); tok[0] += r.usage.input_tokens; tok[1] += r.usage.output_tokens
    try:
        d = parse(t); return [c for c in (d.get("calls") or []) if isinstance(c, dict) and str(c.get("i", "")).lstrip("-").isdigit() and 0 <= int(c["i"]) < len(heads)]
    except Exception:
        if len(heads) <= 10: raise RuntimeError(f"answer not readable (stop: {r.stop_reason}); it began: {t[:70]!r}")
        h = len(heads) // 2; left = _read_batch(client, model, parse, slug, heads[:h], tok); right = _read_batch(client, model, parse, slug, heads[h:], tok)
        return left + [dict(c, i=int(c["i"]) + h) for c in right]


def cmd_extract(max_usd: float):
    from src.news_events2 import _client, _parse, MODEL
    client = _client(); READS.mkdir(parents=True, exist_ok=True); tok = [0, 0]; n = 0; bad = 0; cost = lambda: tok[0] / 1e6 * IN_RATE + tok[1] / 1e6 * OUT_RATE
    for slug, m, k, heads in _batches():
        out = READS / f"{slug}_{m}_{k}__{PV}.json"
        if out.exists(): continue
        try:
            calls = [dict(c, **{"published": heads[int(c["i"])]["published"], "title": heads[int(c["i"])]["title"], "source": heads[int(c["i"])]["source"], "link": heads[int(c["i"])]["link"]}) for c in _read_batch(client, MODEL, _parse, slug, heads, tok)]
            out.write_text(json.dumps(dict(slug=slug, month=m, model=MODEL, prompt_version=PV, n_headlines=len(heads), calls=calls), indent=1)); n += 1
        except Exception as e: bad += 1; print(f"  {slug} {m} batch {k}: {type(e).__name__}: {str(e)[:160]}")
        if n and n % 50 == 0: print(f"  {n} batches, about US${cost():.2f}")
        if cost() >= max_usd: print(f"  cap US${max_usd:.2f} reached after {n} batches; run again to continue"); break
    left = sum(1 for b in _batches() if not (READS / f"{b[0]}_{b[1]}_{b[2]}__{PV}.json").exists())
    print(f"done: {n} batches read now, {bad} failed now, {left} still unread in total, about US${cost():.2f} -> {READS}")


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


# ------------------------------------------------------------------------------------------------ the test (registered in TRACK 3.76 before any price)
INDEX_ETF = {"SPY", "QQQ", "DIA", "IWM", "VOO", "IVV"}; N_PLACEBO, SEED, BAR = 200, 20261120, 0.05 / 8; CELLS = ["day 0"] + [f"+{k}" for k in range(1, 8)] + ["day 0 to +7"]


def _prices(tickers):
    import yfinance as yf
    PX = ROOT / "prices"; PX.mkdir(parents=True, exist_ok=True); out = {}; bad = []
    for t in tickers:
        f = PX / f"{t}.parquet"
        if f.exists(): out[t] = pd.read_parquet(f)["close"]; continue
        try:
            d = yf.download(t, start="2017-06-01", interval="1d", progress=False, auto_adjust=True); c = d["Close"]; c = c.iloc[:, 0] if isinstance(c, pd.DataFrame) else c; c = c.dropna()
            if len(c) < 60: bad.append(t); continue
            c.index = pd.DatetimeIndex(c.index).tz_localize(None); c.to_frame("close").to_parquet(f); out[t] = c
        except Exception: bad.append(t)
    return out, bad


def _adj(px, spy):
    """for every security: its daily move minus the S&P 500's, in bp (a call on an index itself: the raw move). Computed once."""
    return {t: ((c.pct_change() if t in INDEX_ETF else c.pct_change() - spy.reindex(c.index).pct_change()) * 1e4).to_numpy(float) for t, c in px.items()}


def _path(A, t, i0):
    """day 0 and sessions +1..+7, and their sum; None when prices are missing"""
    import numpy as np
    a = A[t]
    if i0 < 1 or i0 + 7 >= len(a): return None
    v = a[i0:i0 + 8]; return None if not np.isfinite(v).all() else list(v) + [float(v.sum())]


def cmd_test():
    import numpy as np
    C = pd.read_csv(ROOT / "calls.csv", parse_dates=["first_seen"]); px, bad = _prices(sorted(set(C.ticker) | {"SPY"})); spy = px["SPY"]; A = _adj(px, spy); rng = np.random.default_rng(SEED); rows = []
    ny = C.first_seen.dt.tz_convert("America/New_York"); C["day"] = (ny.dt.normalize() + pd.to_timedelta((ny.dt.hour >= 16).astype(int), unit="D")).dt.tz_localize(None)
    for r in C.itertuples():
        if r.ticker not in px: continue
        c = px[r.ticker]; i0 = int(c.index.searchsorted(r.day))      # the first session on or after the call's day
        if i0 >= len(c) or (c.index[i0] - r.day).days > 5: continue
        v = _path(A, r.ticker, i0)
        if v is not None: rows.append(dict(investor=r.investor, ticker=r.ticker, direction=r.direction, day0=c.index[i0], i0=i0, new=bool(r.reported_as_new), kind=r.kind, headlines=r.headlines, **{k: r.direction * x for k, x in zip(CELLS, v)}))
    T = pd.DataFrame(rows).sort_values("day0").reset_index(drop=True)
    if T.empty: print("no call could be priced"); return
    T["cluster"] = [bool(((T.ticker == r.ticker) & (T.direction == r.direction) & (T.investor != r.investor) & (T.day0 < r.day0) & (T.day0 >= r.day0 - pd.Timedelta(days=14))).any()) for r in T.itertuples()]
    busy = {t: set(i for i0 in g.i0 for i in range(i0 - 20, i0 + 21)) for t, g in T.groupby("ticker")}
    def placebo(g):      # the same securities and directions on other dates, 200 times
        P = np.full((N_PLACEBO, len(CELLS)), np.nan)
        for k in range(N_PLACEBO):
            acc = []
            for r in g.itertuples():
                n = len(A[r.ticker]); v = None
                for _ in range(6):
                    j = int(rng.integers(1, n - 8))
                    if j in busy[r.ticker]: continue
                    v = _path(A, r.ticker, j)
                    if v is not None: break
                if v is not None: acc.append([r.direction * x for x in v])
            if acc: P[k] = np.mean(acc, axis=0)
        return P
    groups = [(k, g) for k, g in T.groupby("investor")] + [("ALL INVESTORS", T), ("negative calls only", T[T.direction < 0]), ("positive calls only", T[T.direction > 0]), ("reported as that day's news", T[T.new]), ("single calls", T[~T.cluster]), ("CLUSTERS: a second investor, same direction, within two weeks", T[T.cluster])]
    L = ["# SR-2: public calls by well-known investors -- how the security moved", "", f"{len(C)} calls extracted, {len(T)} priced ({len(bad)} securities without prices on Yahoo). Return = the security's daily move minus the S&P 500's (a call on an index itself: the raw move), in the direction of the call, in bp (1 bp = 0.01%). Day 0 = the first session whose close comes after the first headline. Each of +1 to +7 is that one session alone. p = how often the same securities on other dates did as well (200 sets). A group counts at p < {BAR:.4f}; it needs 30 calls.", "",
         "| group | calls | " + " | ".join(CELLS) + " |", "|---|---|" + "---|" * len(CELLS)]; out = {}
    for name, g in groups:
        if len(g) < 30: L.append(f"| {name} | {len(g)} (under 30: not judged) | " + " | ".join("" for _ in CELLS) + " |"); print(f"  {name}: {len(g)} calls -- under 30, not judged"); out[name] = dict(n=int(len(g))); continue
        P = placebo(g); cells = []; res = {}
        for j, c in enumerate(CELLS):
            m = float(g[c].mean()); pv = float((P[:, j] >= m).mean()); hit = float((g[c] > 0).mean()); res[c] = dict(mean=m, p=pv, hit=hit); cells.append(f"{'**' if pv < BAR else ''}{m:+.0f} bp, {hit:.0%}, p {pv:.3f}{'**' if pv < BAR else ''}")
        L.append(f"| {name} | {len(g)} | " + " | ".join(cells) + " |"); out[name] = dict(n=int(len(g)), cells=res)
        print(f"  {name} ({len(g)} calls): day 0 {res['day 0']['mean']:+.0f} bp (p {res['day 0']['p']:.3f}); +1 {res['+1']['mean']:+.0f}; +2 {res['+2']['mean']:+.0f}; +3 {res['+3']['mean']:+.0f}; +4 {res['+4']['mean']:+.0f}; +5 {res['+5']['mean']:+.0f}; +6 {res['+6']['mean']:+.0f}; +7 {res['+7']['mean']:+.0f}; day 0 to +7 {res['day 0 to +7']['mean']:+.0f} bp (p {res['day 0 to +7']['p']:.3f}, right on {res['day 0 to +7']['hit']:.0%})")
    L += ["", "Each cell: average move in the direction of the call, share of calls where the move went the call's way, and p. Bold = passes the bar.", "", "Most-called securities: " + ", ".join(f"{k} {v}" for k, v in T.ticker.value_counts().head(15).items()) + "."]
    Path("docs").mkdir(exist_ok=True); Path("docs/public_calls_test.md").write_text("\n".join(L) + "\n"); Path("docs/public_calls_test.json").write_text(json.dumps(out, indent=1)); T.drop(columns=["i0"]).to_csv(ROOT / "calls_priced.csv", index=False); print("-> docs/public_calls_test.md")


# ------------------------------------------------------------------------------------------------ SR-2b: the parts a user could have traded (registered in TRACK 3.78 before running)
N_F, SEED_F, COST_BP = 2000, 20261121, 30.0; LEGS = ["gone before the open", "open to close, day 0", "close day 0 to close +1", "open day 0 to close +1"]; JUDGED = LEGS[1:]


def _prices_oc(tickers):
    import yfinance as yf
    PX = ROOT / "prices_oc"; PX.mkdir(parents=True, exist_ok=True); out = {}; bad = []
    for t in tickers:
        f = PX / f"{t}.parquet"
        if f.exists(): out[t] = pd.read_parquet(f); continue
        try:
            d = yf.download(t, start="2017-06-01", interval="1d", progress=False, auto_adjust=True)
            if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
            d = d[["Open", "Close"]].dropna(); d.columns = ["open", "close"]
            if len(d) < 60: bad.append(t); continue
            d.index = pd.DatetimeIndex(d.index).tz_localize(None); d.to_parquet(f); out[t] = d
        except Exception: bad.append(t)
    return out, bad


def _legs(px):
    """per security, per session i, in bp and minus the S&P 500's same piece (an index itself: raw):
    co = previous close -> open; oc = open -> close; cc = previous close -> close"""
    spy = px["SPY"]; out = {}
    for t, d in px.items():
        s = spy.reindex(d.index); raw = t in INDEX_ETF
        f = lambda a, b, sa, sb: ((a / b - 1) - (0 if raw else (sa / sb - 1))).to_numpy(float) * 1e4
        out[t] = dict(co=f(d.open, d.close.shift(1), s.open, s.close.shift(1)), oc=f(d.close, d.open, s.close, s.open), cc=f(d.close, d.close.shift(1), s.close, s.close.shift(1)))
    return out


def _four(L, j):
    """the four pieces for a call whose day 0 is session j (arrays allowed)"""
    import numpy as np
    return np.stack([L["co"][j], L["oc"][j], L["cc"][j + 1], L["oc"][j] + L["cc"][j + 1]], axis=-1)


def cmd_follow():
    import numpy as np
    C = pd.read_csv(ROOT / "calls.csv", parse_dates=["first_seen"]); px, bad = _prices_oc(sorted(set(C.ticker) | {"SPY"})); G = _legs(px); rng = np.random.default_rng(SEED_F); rows = []
    ny = C.first_seen.dt.tz_convert("America/New_York"); C["day"] = (ny.dt.normalize() + pd.to_timedelta((ny.dt.hour >= 16).astype(int), unit="D")).dt.tz_localize(None); C["ny"] = ny.dt.tz_localize(None)
    for r in C.itertuples():
        if r.ticker not in px: continue
        idx = px[r.ticker].index; i0 = int(idx.searchsorted(r.day))
        if i0 < 2 or i0 + 2 >= len(idx) or (idx[i0] - r.day).days > 5: continue
        v = _four(G[r.ticker], i0)
        if not np.isfinite(v).all(): continue
        pre = r.ny < idx[i0] + pd.Timedelta(hours=9, minutes=30)      # the first headline was out before that session opened
        rows.append(dict(investor=r.investor, ticker=r.ticker, direction=r.direction, day0=idx[i0], i0=i0, before_open=bool(pre), kind=str(r.kind), new=bool(r.reported_as_new), **{k: r.direction * float(x) for k, x in zip(LEGS, v)}))
    T = pd.DataFrame(rows).sort_values("day0").reset_index(drop=True)
    if T.empty: print("no call could be priced"); return
    busy = {}
    for t, g in T.groupby("ticker"):
        b = np.zeros(len(px[t]), bool)
        for i0 in g.i0: b[max(0, i0 - 20):i0 + 21] = True
        busy[t] = b
    P = np.full((len(T), N_F, 4), np.nan)      # for every call: the same security and direction on 2,000 other dates
    for r in T.itertuples():
        L = G[r.ticker]; n = len(px[r.ticker]); j = rng.integers(2, n - 2, size=6 * N_F); v = _four(L, j); ok = ~busy[r.ticker][j] & np.isfinite(v).all(axis=1); v = v[ok][:N_F]; P[r.Index, :len(v)] = r.direction * v
    def stat(mask, leg):
        k = LEGS.index(leg); m = mask & (T.before_open.to_numpy() if k in (0, 1, 3) else True); x = T.loc[m, leg].to_numpy()
        if len(x) < 30: return dict(n=int(len(x)))
        lo, hi = np.quantile(x, [0.05, 0.95]); null = np.nanmean(P[m][:, :, k], axis=0); mean = float(x.mean())
        return dict(n=int(len(x)), mean=mean, median=float(np.median(x)), trimmed=float(x[(x >= lo) & (x <= hi)].mean()), hit=float((x > 0).mean()), after_cost=mean - COST_BP, p=float((null >= mean).mean()))
    yr = T.day0.dt.year.to_numpy(); pos = (T.direction > 0).to_numpy(); one = np.ones(len(T), bool)
    main = [("ALL INVESTORS", one), ("positive calls", pos), ("negative calls", ~pos)] + [(k, (T.investor == k).to_numpy()) for k in sorted(T.investor.unique())]
    extra = [("positive calls, 2018 to 2021", pos & (yr <= 2021)), ("positive calls, 2022 to 2026", pos & (yr >= 2022)), ("positive, said in a statement", pos & (T.kind == "statement").to_numpy()), ("positive, position disclosed in a filing", pos & (T.kind == "position disclosed in a filing").to_numpy()), ("positive, position reported by the media", pos & (T.kind == "position reported by the media").to_numpy()),
             ("positive, reported as that day's news", pos & T.new.to_numpy()), ("positive, without the 5 most-called securities", pos & ~T.ticker.isin(list(T.ticker.value_counts().head(5).index)).to_numpy())] + [(f"{k}, positive calls", pos & (T.investor == k).to_numpy()) for k in sorted(T.investor.unique())]
    bar = 0.05 / (len(main) * len(JUDGED)); out = dict(bar=bar, calls=int(len(T)), before_open=int(T.before_open.sum()), main={}, extra={})
    fmt = lambda s: f"under 30 ({s['n']})" if "mean" not in s else f"{'**' if s['p'] < bar else ''}{s['mean']:+.0f} bp{'**' if s['p'] < bar else ''} (n {s['n']}; middle call {s['median']:+.0f}; without the 5% largest and smallest {s['trimmed']:+.0f}; right {s['hit']:.0%}; after {COST_BP:.0f} bp cost {s['after_cost']:+.0f}; p {s['p']:.4f})"
    M = ["# SR-2b: public calls by well-known investors -- the parts a user could have traded", "",
         f"{len(T)} calls priced; for {int(T.before_open.sum())} the first headline was out before the session opened (the others appeared during the session). Returns in bp, minus the S&P 500's same piece, in the direction of the call. "
         f"'gone before the open' = previous close to the open of day 0: already in the price when a user could first trade (description, not judged). 'open to close, day 0' = buy at that open, sell at that close (only calls out before the open). "
         f"'close day 0 to close +1' = buy at the close of day 0, sell at the next close (all calls). 'open day 0 to close +1' = both. p = how often the same securities on {N_F} sets of other dates did as well. "
         f"A main cell counts at p < {bar:.4f} (0.05 / {len(main)} groups / {len(JUDGED)} pieces). Cost: {COST_BP:.0f} bp a round trip (the average measured on IBKR for the AI-chain list, docs/ai_chain_costs.md; an assumption for these securities).", ""]
    for title, groups, key in (("Main groups (judged)", main, "main"), ("Splits (description; the bar does not apply)", extra, "extra")):
        M += [f"## {title}", "", "| group | " + " | ".join(LEGS) + " |", "|---|" + "---|" * len(LEGS)]
        for name, mask in groups:
            S = {leg: stat(mask, leg) for leg in LEGS}; out[key][name] = S; M.append(f"| {name} | " + " | ".join(fmt(S[leg]) if (key == "main" and leg in JUDGED) else fmt(S[leg]).replace("**", "") for leg in LEGS) + " |")
            short = lambda s: f"n {s['n']} under 30" if "mean" not in s else f"{s['mean']:+.0f} bp, middle {s['median']:+.0f}, trimmed {s['trimmed']:+.0f}, right {s['hit']:.0%}, p {s['p']:.4f}{' PASS' if key == 'main' and s['p'] < bar else ''}"
            print(f"  {name}: open->close day 0 [{short(S[LEGS[1]])}] | close day 0->close +1 [{short(S[LEGS[2]])}] | gone before the open {S[LEGS[0]].get('mean', float('nan')):+.0f} bp")
        M.append("")
    Path("docs").mkdir(exist_ok=True); Path("docs/public_calls_follow.md").write_text("\n".join(M) + "\n"); Path("docs/public_calls_follow.json").write_text(json.dumps(out, indent=1)); T.drop(columns=["i0"]).to_csv(ROOT / "calls_legs.csv", index=False)
    print(f"bar for the main groups: p < {bar:.4f}. -> docs/public_calls_follow.md")


# ------------------------------------------------------------------------------------------------ SR-2c: only what comes after the headline for certain (registered in TRACK 3.80 before running)
SAFE = ["overnight into +1", "open to close, +1", "open +1 to close +2"]; SEED_S = 20261122


def _three(L, j):
    import numpy as np
    return np.stack([L["co"][j + 1], L["oc"][j + 1], L["oc"][j + 1] + L["cc"][j + 2]], axis=-1)


def cmd_safe():
    """93% of the headlines carry a date but no real time of day (the feed stamps them midnight Pacific). So the only pieces that are after the headline for
    certain start at the OPEN of the session after the headline's date. Day 0 here = the first session on or after the headline's Pacific date."""
    import numpy as np
    C = pd.read_csv(ROOT / "calls.csv", parse_dates=["first_seen"]); px, bad = _prices_oc(sorted(set(C.ticker) | {"SPY"})); G = _legs(px); rng = np.random.default_rng(SEED_S); rows = []
    t = C.first_seen; C["date_only"] = (t.dt.minute == 0) & (t.dt.second == 0) & t.dt.hour.isin([7, 8]); C["day"] = t.dt.tz_convert("America/Los_Angeles").dt.normalize().dt.tz_localize(None)
    for r in C.itertuples():
        if r.ticker not in px: continue
        idx = px[r.ticker].index; i0 = int(idx.searchsorted(r.day))
        if i0 < 2 or i0 + 3 >= len(idx) or (idx[i0] - r.day).days > 5: continue
        v = _three(G[r.ticker], i0)
        if not np.isfinite(v).all(): continue
        k = str(r.kind).replace("reported by media", "reported by the media")
        rows.append(dict(investor=r.investor, ticker=r.ticker, direction=r.direction, day0=idx[i0], i0=i0, kind=k, date_only=bool(r.date_only), **{n: r.direction * float(x) for n, x in zip(SAFE, v)}))
    T = pd.DataFrame(rows).sort_values("day0").reset_index(drop=True)
    if T.empty: print("no call could be priced"); return
    busy = {}
    for tk, g in T.groupby("ticker"):
        b = np.zeros(len(px[tk]), bool)
        for i0 in g.i0: b[max(0, i0 - 20):i0 + 21] = True
        busy[tk] = b
    P = np.full((len(T), N_F, 3), np.nan)
    for r in T.itertuples():
        n = len(px[r.ticker]); j = rng.integers(2, n - 3, size=6 * N_F); v = _three(G[r.ticker], j); ok = ~busy[r.ticker][j] & np.isfinite(v).all(axis=1); v = v[ok][:N_F]; P[r.Index, :len(v)] = r.direction * v
    def stat(mask, leg):
        k = SAFE.index(leg); x = T.loc[mask, leg].to_numpy()
        if len(x) < 30: return dict(n=int(len(x)))
        lo, hi = np.quantile(x, [0.05, 0.95]); null = np.nanmean(P[mask][:, :, k], axis=0); mean = float(x.mean())
        return dict(n=int(len(x)), mean=mean, median=float(np.median(x)), trimmed=float(x[(x >= lo) & (x <= hi)].mean()), hit=float((x > 0).mean()), after_cost=mean - COST_BP, p=float((null >= mean).mean()))
    yr = T.day0.dt.year.to_numpy(); pos = (T.direction > 0).to_numpy(); one = np.ones(len(T), bool); inv = sorted(T.investor.unique())
    main = [("ALL INVESTORS", one), ("positive calls", pos), ("negative calls", ~pos)] + [(k, (T.investor == k).to_numpy()) for k in inv]
    extra = [("positive calls, 2018 to 2021", pos & (yr <= 2021)), ("positive calls, 2022 to 2026", pos & (yr >= 2022))] + [(f"positive, {k}", pos & (T.kind == k).to_numpy()) for k in ("statement", "position disclosed in a filing", "position reported by the media")] + [(f"negative, {k}", ~pos & (T.kind == k).to_numpy()) for k in ("statement", "position disclosed in a filing", "position reported by the media")] \
            + [(f"{k}, positive calls", pos & (T.investor == k).to_numpy()) for k in inv] + [(f"{k}, 2018 to 2021", (T.investor == k).to_numpy() & (yr <= 2021)) for k in inv] + [(f"{k}, 2022 to 2026", (T.investor == k).to_numpy() & (yr >= 2022)) for k in inv]
    judged = SAFE[1:]; bar = 0.05 / (len(main) * len(judged)); out = dict(bar=bar, calls=int(len(T)), date_only=int(T.date_only.sum()), main={}, extra={})
    fmt = lambda s, b: f"under 30 ({s['n']})" if "mean" not in s else f"{'**' if b and s['p'] < bar else ''}{s['mean']:+.0f} bp{'**' if b and s['p'] < bar else ''} (n {s['n']}; middle call {s['median']:+.0f}; without the 5% largest and smallest {s['trimmed']:+.0f}; right {s['hit']:.0%}; after {COST_BP:.0f} bp cost {s['after_cost']:+.0f}; p {s['p']:.4f})"
    M = ["# SR-2c: public calls by well-known investors -- only what comes after the headline for certain", "",
         f"{len(T)} calls priced; {int(T.date_only.sum())} of them ({T.date_only.mean():.0%}) carry a date but no real time of day. Day 0 = the first session on or after the headline's date. Returns in bp, minus the S&P 500's same piece, in the direction of the call. "
         f"'overnight into +1' = close of day 0 to the open of +1 (description: a headline that came out after the close shows up here, before a user can trade). 'open to close, +1' = buy at the open of the next session, sell at its close. 'open +1 to close +2' = hold one session longer. "
         f"p = how often the same securities on {N_F} sets of other dates did as well. A main cell counts at p < {bar:.4f} (0.05 / {len(main)} groups / {len(judged)} pieces). Cost {COST_BP:.0f} bp a round trip (assumption).", ""]
    for title, groups, key in (("Main groups (judged)", main, "main"), ("Splits (description; the bar does not apply)", extra, "extra")):
        M += [f"## {title}", "", "| group | " + " | ".join(SAFE) + " |", "|---|" + "---|" * len(SAFE)]
        for name, mask in groups:
            S = {leg: stat(mask, leg) for leg in SAFE}; out[key][name] = S; M.append(f"| {name} | " + " | ".join(fmt(S[leg], key == "main" and leg in judged) for leg in SAFE) + " |")
            short = lambda s: f"n {s['n']} under 30" if "mean" not in s else f"{s['mean']:+.0f} bp, middle {s['median']:+.0f}, trimmed {s['trimmed']:+.0f}, right {s['hit']:.0%}, after cost {s['after_cost']:+.0f}, p {s['p']:.4f}{' PASS' if key == 'main' and s['p'] < bar else ''}"
            print(f"  {name}: overnight into +1 {S[SAFE[0]].get('mean', float('nan')):+.0f} bp | open->close +1 [{short(S[SAFE[1]])}] | open +1->close +2 [{short(S[SAFE[2]])}]")
        M.append("")
    Path("docs").mkdir(exist_ok=True); Path("docs/public_calls_safe.md").write_text("\n".join(M) + "\n"); Path("docs/public_calls_safe.json").write_text(json.dumps(out, indent=1)); T.drop(columns=["i0"]).to_csv(ROOT / "calls_safe.csv", index=False)
    print(f"{int(T.date_only.sum())} of {len(T)} calls have a date but no time of day. Bar for the main groups: p < {bar:.4f}. -> docs/public_calls_safe.md")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["collect", "cost", "extract", "calls", "test", "follow", "safe"]); ap.add_argument("--start", default="2018-01"); ap.add_argument("--max-usd", type=float, default=15.0); a = ap.parse_args()
    {"collect": lambda: cmd_collect(a.start), "cost": cmd_cost, "extract": lambda: cmd_extract(a.max_usd), "calls": cmd_calls, "test": cmd_test, "follow": cmd_follow, "safe": cmd_safe}[a.cmd]()
