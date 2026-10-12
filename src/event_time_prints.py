"""
08:30 event-time reader for scheduled releases (TRACK §3.19; prereg_event_time amendment 2026-10-13).

Per release day, one row per release: the headline number as received (API), the surprise (market-implied from S5's
fed-funds bars 08:25->08:35 when present, else the naive prior from processed/prints.csv, labelled), the 08:25->08:45
reaction on the five shown instruments, the release text where the agency serves scripts (BEA, Census), and a
`data_print` read of that text with the A4-passed prompt. BLS and DOL text is 403 to scripts: those rows carry
text_status=unfetchable and can be completed by hand with `paste --date --name --file`.

  selftest                       no network: window maths, calendar parsing, ledger append on a temp copy
  calendar                       FRED release dates (ids 50 empsit, 10 cpi, 46 ppi, 180 claims, 53 gdp, 54 pce, 9 retail)
                                 -> processed/release_calendar.csv (past year + scheduled future dates)
  dry-run --date D --name N      past release: number from the API, reaction from stored S5 parquet, text if fetchable,
                                 writes outputs/event_time/<D>_<N>.json (write-once) and a ledger row with dry_run=True
  live                           used by prints_run.sh: exits unless today is a release day and the clock is 08:10-08:28 ET;
                                 waits for 08:30, polls the number, waits for delayed bars, records the reaction
  settle --date D                fills rest_of_session (08:45 -> 16:00) from S5 parquet for that day's rows, once
  paste --date D --name N --file F   attach a hand-fetched release text and read it (BLS/DOL rows)
"""
from __future__ import annotations
import argparse, csv, glob, json, os, re, sys, time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
ET = ZoneInfo("America/New_York")
OUT = Path("outputs/event_time"); LEDGER = Path("processed/event_time_ledger.csv")
CAL = Path("processed/release_calendar.csv"); PRINTS = Path("processed/prints.csv")
INTRA = Path("data_provenance/intraday"); TEXTS = Path("data_provenance/docs/data_print")
READS = Path("data_provenance/doc_reads_prints")
SHOWN = {"ES=F": "S&P 500 (futures)", "^TNX": "10-year yield", "GC=F": "gold", "DX-Y.NYB": "DXY", "CL=F": "WTI"}   # ES=F: ^GSPC has no 08:30 bars
FOLDER = {"^GSPC": "GSPC", "ES=F": "ES_F", "^TNX": "TNX", "GC=F": "GC_F", "DX-Y.NYB": "DX-Y_NYB", "CL=F": "CL_F", "ZQ=F": "ZQ_F"}
# name -> (FRED release id, agency, number source, series, how the headline is formed, text route)
RELEASES = {
    "empsit": (50, "BLS", "bls", "CES0000000001", "diff", "unfetchable"),
    "cpi":    (10, "BLS", "bls", "CUSR0000SA0",  "pct",  "unfetchable"),
    "ppi":    (46, "BLS", "bls", "WPSFD4",       "pct",  "unfetchable"),
    "claims": (180, "DOL", "fred", "ICSA",       "level", "unfetchable"),
    "gdp":    (53, "BEA", "fred", "A191RL1Q225SBEA", "level", "bea:gross-domestic-product"),
    "pce":    (54, "BEA", "fred", "PCEPI",       "pct",  "bea:personal-income-and-outlays"),
    "retail": (9, "Census", "fred", "RSAFS",     "pct",  "census:https://www.census.gov/retail/marts/www/marts_current.pdf"),
}
W_PRE, W_POST, W_SURP = (8, 25), (8, 45), (8, 35)


def log(msg): print(f"[{datetime.now(ET):%H:%M:%S ET}] {msg}", flush=True)


# ---------------------------------------------------------------- calendar
def _fred_release_dates(rid, api_key, start, end):
    import urllib.request
    url = (f"https://api.stlouisfed.org/fred/release/dates?release_id={rid}&api_key={api_key}&file_type=json"
           f"&include_release_dates_with_no_data=true&realtime_start={start}&realtime_end={end}&limit=1000")
    with urllib.request.urlopen(url, timeout=30) as r:
        j = json.loads(r.read().decode())
    return sorted({d["date"] for d in j.get("release_dates", [])})


def cmd_calendar(a):
    key = os.environ.get("FRED_API_KEY") or sys.exit("set FRED_API_KEY")
    today = pd.Timestamp.today().normalize()
    start, end = (today - pd.Timedelta(days=400)).strftime("%Y-%m-%d"), (today + pd.Timedelta(days=400)).strftime("%Y-%m-%d")
    rows = []
    for name, (rid, agency, *_r) in RELEASES.items():
        try:
            ds = _fred_release_dates(rid, key, start, end)
        except Exception as e:
            print(f"  {name}: FRED release dates failed: {type(e).__name__}: {e}"); continue
        rows += [(d, name, agency, rid) for d in ds]
        fut = [d for d in ds if d >= today.strftime("%Y-%m-%d")]
        print(f"  {name:7} {len(ds)} dates, next: {fut[:3]}")
    df = pd.DataFrame(rows, columns=["date", "name", "agency", "release_id"]).sort_values(["date", "name"])
    CAL.parent.mkdir(exist_ok=True); df.to_csv(CAL, index=False); print(f"  -> {CAL} ({len(df)} rows)")


def releases_on(day: str) -> list[str]:
    if not CAL.exists(): return []
    c = pd.read_csv(CAL, dtype=str); return sorted(set(c[c.date == day].name))


# ---------------------------------------------------------------- the number
def _bls_latest(series):
    import urllib.request
    body = json.dumps({"seriesid": [series], "startyear": str(datetime.now().year - 1), "endyear": str(datetime.now().year)}).encode()
    req = urllib.request.Request("https://api.bls.gov/publicAPI/v2/timeseries/data/", data=body, headers={"Content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        j = json.loads(r.read().decode())
    data = j["Results"]["series"][0]["data"]
    obs = sorted(((d["year"], d["period"], float(d["value"])) for d in data if d["period"].startswith("M")), key=lambda x: (x[0], x[1]))
    return [(f"{y}-{p[1:]}", v) for y, p, v in obs]


def _fred_latest(series):
    from fredapi import Fred
    s = Fred(api_key=os.environ["FRED_API_KEY"]).get_series(series).dropna()
    return [(d.strftime("%Y-%m-%d"), float(v)) for d, v in s.iloc[-24:].items()]


def headline(name):
    rid, agency, src, series, how, _t = RELEASES[name]
    obs = _bls_latest(series) if src == "bls" else _fred_latest(series)
    if len(obs) < 2: return None
    (p0, v0), (p1, v1) = obs[-2], obs[-1]
    if how == "diff": val, unit = v1 - v0, "thousands, change"
    elif how == "pct": val, unit = (v1 / v0 - 1) * 100, "percent, m/m"
    else: val, unit = v1, "level"
    return dict(period=p1, value=round(val, 3), unit=unit, raw_latest=v1, raw_prior=v0, source=src, series=series,
                received_at_et=datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S"))


def naive_prior(name, day):
    if not PRINTS.exists(): return None
    p = pd.read_csv(PRINTS, parse_dates=["date"]); p = p[(p["name"] == name) & (p["date"] < pd.Timestamp(day))]
    if p.empty: return None
    r = p.sort_values("date").iloc[-1]; return dict(expected=float(r["actual_first_print"]), source="naive_prior", from_release=str(r["date"].date()))


# ---------------------------------------------------------------- bars
def _bars(tk, day):
    f = INTRA / FOLDER.get(tk, tk.replace("^", "").replace("=", "_").replace(".", "_")) / f"{day.replace('-', '')}.parquet"
    if not f.exists(): return None
    d = pd.read_parquet(f); idx = pd.DatetimeIndex(d.index)
    d.index = idx.tz_convert(ET) if idx.tz is not None else idx.tz_localize("UTC").tz_convert(ET)
    return d


def _at(d, hh, mm, side="last_before"):
    """Close of the last bar at or before hh:mm (or first at/after)."""
    t = d.index[0].replace(hour=hh, minute=mm, second=0, microsecond=0)
    sub = d[d.index <= t] if side == "last_before" else d[d.index >= t]
    if sub.empty: return None
    return float((sub.iloc[-1] if side == "last_before" else sub.iloc[0])["Close"])


def window_change(d, tk, a, b):
    x, y = _at(d, *a), _at(d, *b)
    if x is None or y is None: return None
    return (y - x) if tk == "^TNX" else (y / x - 1)


def reaction(day, live=False):
    out = {}
    for tk, name in SHOWN.items():
        d = None
        if live:
            try:
                import yfinance as yf
                d = yf.Ticker(tk).history(period="1d", interval="1m", auto_adjust=False)
                if not d.empty:
                    idx = pd.DatetimeIndex(d.index); d.index = idx.tz_convert(ET) if idx.tz is not None else idx.tz_localize("UTC").tz_convert(ET)
            except Exception as e:
                out[name] = dict(ticker=tk, error=f"{type(e).__name__}: {e}"); continue
        else:
            d = _bars(tk, day)
        if d is None or d.empty: out[name] = dict(ticker=tk, error="no bars"); continue
        ch = window_change(d, tk, W_PRE, W_POST)
        out[name] = dict(ticker=tk, window="08:25 -> 08:45 ET", change=ch)
    return out


def market_surprise(day, live=False):
    """Sign and size of the fed-funds move 08:25->08:35: price down = rates up = hawkish surprise."""
    d = None
    if live:
        try:
            import yfinance as yf
            d = yf.Ticker("ZQ=F").history(period="1d", interval="1m", auto_adjust=False)
            idx = pd.DatetimeIndex(d.index); d.index = idx.tz_convert(ET) if idx.tz is not None else idx.tz_localize("UTC").tz_convert(ET)
        except Exception: d = None
    else:
        d = _bars("ZQ=F", day)
    if d is None or d.empty: return None
    ch = window_change(d, "ZQ=F", W_PRE, W_SURP)
    if ch is None: return None
    return dict(source="market_implied_ZQ", window="08:25 -> 08:35 ET", zq_change=ch, rates_direction=("up" if ch < 0 else "down" if ch > 0 else "flat"))


# ---------------------------------------------------------------- text
def fetch_text(name, day):
    route = RELEASES[name][5]
    if route == "unfetchable": return None, "unfetchable (403 to scripts; use paste)"
    import urllib.request
    try:
        if route.startswith("census:"):
            url = route.split(":", 1)[1]
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30) as r: raw = r.read()
            from pypdf import PdfReader; import io
            txt = "\n".join((pg.extract_text() or "") for pg in PdfReader(io.BytesIO(raw)).pages)
        else:
            slug = route.split(":", 1)[1]
            with urllib.request.urlopen(urllib.request.Request("https://www.bea.gov/news/current-releases", headers={"User-Agent": "Mozilla/5.0"}), timeout=30) as r: page = r.read().decode("utf-8", "ignore")
            m = re.search(rf'href="(/news/\d{{4}}/{slug}[^"]*)"', page)
            if not m: return None, "BEA: release link not found on current-releases page"
            with urllib.request.urlopen(urllib.request.Request("https://www.bea.gov" + m.group(1), headers={"User-Agent": "Mozilla/5.0"}), timeout=30) as r: html = r.read().decode("utf-8", "ignore")
            txt = re.sub(r"<[^>]+>", " ", html); txt = re.sub(r"\s+", " ", txt)
        TEXTS.mkdir(parents=True, exist_ok=True)
        f = TEXTS / f"{day.replace('-', '')}_{name}.txt"
        if not f.exists(): f.write_text(txt)
        return f, "fetched"
    except Exception as e:
        return None, f"fetch failed: {type(e).__name__}: {e}"


def read_text(name, day, f):
    """One data_print read with the A4 prompt (src.read_prints.load_prompt); write-once JSON beside the empsit reads."""
    from src.read_prints import load_prompt, body_for, calendar_for, ref_month_of, PROMPT_VERSION
    from src.doc_read import is_fatal
    from anthropic import Anthropic
    op = READS / f"{day.replace('-', '')}_{name}__{PROMPT_VERSION}.json"
    if op.exists(): return json.load(open(op))["read"]
    if not os.environ.get("ANTHROPIC_API_KEY"): log("no ANTHROPIC_API_KEY; text saved, not read"); return None
    system, _ = load_prompt(); cal = calendar_for(ref_month_of(day))
    try:
        r = Anthropic().messages.create(model="claude-sonnet-5", max_tokens=4000, system=system,
                                        messages=[{"role": "user", "content": body_for(f.read_text()[:60000], cal, None)}])
    except Exception as e:
        if is_fatal(e): log(f"READ ABORTED (fatal): {e}")
        else: log(f"read error: {e}")
        return None
    t = "".join(b.text for b in r.content if b.type == "text").strip(); i, j = t.find("{"), t.rfind("}")
    try: read = json.loads(t[i:j + 1])
    except Exception: log("reply not JSON"); return None
    READS.mkdir(parents=True, exist_ok=True)
    op.write_text(json.dumps(dict(release_date=day, name=name, prompt_version=PROMPT_VERSION, model="claude-sonnet-5",
                                  calendar_given=cal, usage=dict(input=r.usage.input_tokens, output=r.usage.output_tokens),
                                  read_at=datetime.now(ET).isoformat(), read=read), ensure_ascii=False, indent=1))
    return read


# ---------------------------------------------------------------- event record
def write_event(day, name, dry, head, surprise, prior, react, text_status, read):
    OUT.mkdir(parents=True, exist_ok=True)
    f = OUT / f"{day.replace('-', '')}_{name}.json"
    if f.exists(): log(f"event file exists, not rewritten: {f.name}"); return f
    exp = None; surp = None; src = None
    if prior: exp, src = prior["expected"], prior["source"]
    if head and exp is not None: surp = head["value"] - exp
    rec = dict(date=day, event_type=f"print:{name}", agency=RELEASES[name][1], dry_run=dry,
               recorded_at_et=datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S"), headline=head,
               expectation=dict(naive=prior, market=surprise), surprise_vs_naive=surp, surprise_source=src,
               reaction=react, text_status=text_status,
               read=(None if read is None else {k: read.get(k) for k in ("headline_value", "special_factors", "calendar_factors", "transitory_share", "underlying_direction", "confidence")}),
               rest_of_session=None)
    f.write_text(json.dumps(rec, indent=2, ensure_ascii=False))
    new = not LEDGER.exists()
    hdr = ["date", "read_at_et", "dry_run", "stance", "dir_equity", "dir_duration", "dir_gold", "dir_dollar", "dir_oil", "magnitude", "specificity", "novelty", "confidence", "event_type"]
    ud = (read or {}).get("underlying_direction") or {}
    with LEDGER.open("a", newline="") as h:
        w = csv.writer(h)
        if new: w.writerow(hdr)
        w.writerow([day, rec["recorded_at_et"], dry, (surp if surp is not None else ""), ud.get("equity", ""), ud.get("duration", ""), ud.get("gold", ""), ud.get("dollar", ""), ud.get("oil", ""),
                    "", (read or {}).get("specificity", ""), "", (read or {}).get("confidence", ""), f"print:{name}"])
    log(f"event written: {f.name}; headline {head and head['value']} ({head and head['unit']}); surprise vs naive {surp}; "
        f"reaction " + ", ".join(f"{k} {v.get('change'):+.4f}" for k, v in react.items() if v.get("change") is not None))
    return f


def run_one(day, name, dry, live):
    head = None
    try: head = headline(name)
    except Exception as e: log(f"{name}: number fetch failed: {type(e).__name__}: {e}")
    prior = naive_prior(name, day); surprise = market_surprise(day, live=live)
    react = reaction(day, live=live)
    f, status = fetch_text(name, day)
    read = read_text(name, day, f) if f is not None else None
    return write_event(day, name, dry, head, surprise, prior, react, status, read)


def cmd_dry(a):
    for name in ([a.name] if a.name else releases_on(a.date)):
        if name not in RELEASES: sys.exit(f"unknown release {name}")
        run_one(a.date, name, dry=True, live=False)


def cmd_live(a):
    day = datetime.now(ET).strftime("%Y-%m-%d"); names = releases_on(day)
    if not names: log(f"{day}: no scheduled release in {CAL}; nothing to do"); return
    now = datetime.now(ET)
    if not (8 <= now.hour <= 8 and 10 <= now.minute <= 28) and not a.no_wait:
        log(f"{now:%H:%M} ET is outside the 08:10-08:28 start window; nothing to do"); return
    log(f"release day: {names}; waiting for 08:30:30 ET")
    if not a.no_wait:
        target = now.replace(hour=8, minute=30, second=30)
        while datetime.now(ET) < target: time.sleep(5)
    heads = {}
    deadline = time.time() + 20 * 60
    for name in names:
        known = naive_prior(name, day)
        while time.time() < deadline:
            try:
                h = headline(name)
                if h and (known is None or h["period"] > (known.get("from_release") or "")): heads[name] = h; break
            except Exception as e: log(f"{name}: poll error {type(e).__name__}")
            time.sleep(15)
        log(f"{name}: number {'received' if name in heads else 'NOT received in 20 min'}")
    if not a.no_wait:
        log("waiting until 09:05 ET for the delayed 1-minute bars");
        target = datetime.now(ET).replace(hour=9, minute=5, second=0)
        while datetime.now(ET) < target: time.sleep(10)
    for name in names:
        prior = naive_prior(name, day); surprise = market_surprise(day, live=True); react = reaction(day, live=True)
        f, status = fetch_text(name, day); read = read_text(name, day, f) if f is not None else None
        write_event(day, name, False, heads.get(name), surprise, prior, react, status, read)
    log("done")


def cmd_settle(a):
    for f in sorted(OUT.glob(f"{a.date.replace('-', '')}_*.json")):
        rec = json.loads(f.read_text())
        if rec.get("rest_of_session") is not None: continue
        out = {}
        for tk, name in SHOWN.items():
            d = _bars(tk, a.date)
            if d is None: continue
            ch = window_change(d, tk, W_POST, (16, 0)); out[name] = dict(ticker=tk, window="08:45 -> 16:00 ET", change=ch)
        rec["rest_of_session"] = out; f.write_text(json.dumps(rec, indent=2, ensure_ascii=False))
        log(f"{f.name}: rest of session " + ", ".join(f"{k} {v['change']:+.4f}" for k, v in out.items() if v.get("change") is not None))


def cmd_paste(a):
    f = TEXTS / f"{a.date.replace('-', '')}_{a.name}.txt"
    if not f.exists(): f.write_text(Path(a.file).read_text())
    read = read_text(a.name, a.date, f)
    ef = OUT / f"{a.date.replace('-', '')}_{a.name}.json"
    if ef.exists() and read is not None:
        rec = json.loads(ef.read_text()); rec["text_status"] = "pasted by founder"; rec["read"] = {k: read.get(k) for k in ("headline_value", "special_factors", "calendar_factors", "transitory_share", "underlying_direction", "confidence")}
        ef.write_text(json.dumps(rec, indent=2, ensure_ascii=False)); log(f"{ef.name}: read attached")


def cmd_selftest(a):
    import tempfile, shutil
    # 1. window maths on a synthetic day
    idx = pd.date_range("2026-10-02 08:00", "2026-10-02 16:00", freq="1min", tz=ET)
    px = pd.Series(100.0, index=idx); px[idx >= idx[0].replace(hour=8, minute=30)] = 101.0; px[idx >= idx[0].replace(hour=12)] = 102.0
    d = pd.DataFrame({"Close": px})
    assert abs(window_change(d, "^GSPC", W_PRE, W_POST) - 0.01) < 1e-9, "reaction window"
    assert abs(window_change(d, "^GSPC", W_POST, (16, 0)) - (102 / 101 - 1)) < 1e-9, "rest of session"
    assert abs(window_change(d, "^TNX", W_PRE, W_POST) - 1.0) < 1e-9, "yield difference"
    print("  T1 window maths: PASS")
    # 2. calendar lookup on a temp calendar
    tmp = Path(tempfile.mkdtemp()); bak = CAL
    try:
        globals()["CAL"] = tmp / "cal.csv"; pd.DataFrame([("2026-10-02", "empsit", "BLS", 50), ("2026-10-02", "unrate", "BLS", 50)], columns=["date", "name", "agency", "release_id"]).to_csv(CAL, index=False)
        assert releases_on("2026-10-02") == ["empsit", "unrate"] and releases_on("2026-10-03") == []
        print("  T2 calendar lookup: PASS")
    finally:
        globals()["CAL"] = bak; shutil.rmtree(tmp)
    # 3. ledger append on a temp copy (no real write)
    tmp = Path(tempfile.mkdtemp()); bak_l, bak_o = LEDGER, OUT
    try:
        globals()["LEDGER"] = tmp / "ledger.csv"; globals()["OUT"] = tmp / "out"
        write_event("2026-10-02", "empsit", True, dict(value=29.0, unit="thousands, change"), None, dict(expected=162.0, source="naive_prior", from_release="2026-09-04"),
                    {"S&P 500": dict(ticker="^GSPC", change=0.004)}, "unfetchable", None)
        r = list(csv.reader(LEDGER.open())); assert r[0][-1] == "event_type" and r[1][-1] == "print:empsit" and r[1][3] == "-133.0"
        print("  T3 ledger row: PASS")
    finally:
        globals()["LEDGER"] = bak_l; globals()["OUT"] = bak_o; shutil.rmtree(tmp)
    # 4. headline arithmetic
    assert RELEASES["empsit"][4] == "diff" and RELEASES["cpi"][4] == "pct"
    print("  T4 headline rules: PASS"); print("selftest: 4/4")


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest"); sub.add_parser("calendar")
    d = sub.add_parser("dry-run"); d.add_argument("--date", required=True); d.add_argument("--name")
    l = sub.add_parser("live"); l.add_argument("--no-wait", action="store_true")
    s_ = sub.add_parser("settle"); s_.add_argument("--date", required=True)
    p = sub.add_parser("paste"); p.add_argument("--date", required=True); p.add_argument("--name", required=True); p.add_argument("--file", required=True)
    a = ap.parse_args()
    {"selftest": cmd_selftest, "calendar": cmd_calendar, "dry-run": cmd_dry, "live": cmd_live, "settle": cmd_settle, "paste": cmd_paste}[a.cmd](a)


if __name__ == "__main__":
    main()
