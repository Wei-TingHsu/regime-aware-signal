"""
A4 reader-consistency run on the scheduled-release texts (prereg_prints_and_attribution §A4, §A2b).

The prompt is read from docs/data_print_profile.md -- the file the founder reviewed IS the prompt. The section between the
first and second '---' lines is the system prompt; the JSON block inside it is the schema the reader must return.

  python -m src.read_prints --dry-run           print the assembled system prompt and the user body for the first release
  python -m src.read_prints --run [--model M]   read every text in data_provenance/docs/data_print/ not yet read; write-once
  python -m src.read_prints --score             compare with ALFRED first prints and the §A2b statuses -> docs/a4_reader_consistency.md

Write-once: data_provenance/doc_reads_prints/<YYYYMMDD>_empsit__<PROMPT_VERSION>.json. Re-reading needs --force and is a
registered act, not a convenience.
"""
import argparse, json, os, re, sys, time
from pathlib import Path
import pandas as pd

PROMPT_FILE = Path("docs/data_print_profile.md")
PROMPT_VERSION = "v1-2026-10-11"
TEXT_DIR = Path("data_provenance/docs/data_print")
OUT_DIR = Path("data_provenance/doc_reads_prints")
CAL = Path("data_provenance/event_calendar.csv")
PRINTS = Path("processed/prints.csv")
REPORT = Path("docs/a4_reader_consistency.md")
# what §A2b says the reader must return on the three calibration months; 'supported' anywhere here = reader used own knowledge
EXPECTED_STATUS = {"20260702": "contradicted", "20260807": "contradicted", "20260904": "contradicted"}
# 20260807 corrected 11 Oct: the text says "Retail trade lost 19,000 jobs in July" and retail is a calendar industry with
# expected sign +, so the rule gives contradicted; the registered "undetermined" came from a grep, not a read (#44).


def load_prompt():
    s = PROMPT_FILE.read_text()
    parts = s.split("\n---\n")
    if len(parts) < 3:
        sys.exit("data_print_profile.md: expected the prompt between the first and second '---' lines")
    system = parts[1].strip()
    m = re.search(r"```json\n(.*?)\n```", system, re.S)
    if not m:
        sys.exit("data_print_profile.md: no ```json schema block inside the prompt section")
    return system, m.group(1)


def calendar_for(ref_month):
    if not CAL.exists():
        return []
    c = pd.read_csv(CAL, dtype=str)
    rows = c[c.ref_month == ref_month]
    return [{"event": r.event, "expected_sign": int(r.expected_sign), "industries": r.industries.split(";"),
             "status_at_registration": r.status} for r in rows.itertuples()]


def ref_month_of(release_date):
    # the Employment Situation released in month M describes month M-1
    d = pd.Timestamp(release_date)
    return (d.replace(day=1) - pd.Timedelta(days=1)).strftime("%Y-%m")   # fixed 11 Oct: MonthBegin rolled to the same month


def body_for(text, cal, prev):
    b = ""
    if prev:
        keep = {k: prev.get(k) for k in ("headline", "special_factors", "calendar_factors", "transitory_share")}
        b += "PREVIOUS RELEASE'S READ:\n" + json.dumps(keep, ensure_ascii=False) + "\n\n"
    b += "CALENDAR ENTRIES FOR THIS REFERENCE MONTH (may be empty):\n" + json.dumps(cal, ensure_ascii=False) + "\n\n"
    b += "RELEASE TEXT:\n" + text
    return b


def texts():
    fs = sorted(TEXT_DIR.glob("*_empsit.txt"))
    return [(f.stem[:8], f) for f in fs]


def out_path(stamp):
    return OUT_DIR / f"{stamp}_empsit__{PROMPT_VERSION}.json"


def run(model, force, sleep, dates=()):
    from anthropic import Anthropic
    from src.doc_read import is_fatal
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("set ANTHROPIC_API_KEY (set -a; source .env; set +a)")
    system, _ = load_prompt()
    client = Anthropic()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    prev = None; n_read = n_skip = 0; tok_in = tok_out = 0
    for stamp, f in texts():
        op = out_path(stamp)
        redo = force and stamp in dates
        if op.exists() and not redo:
            prev = json.load(open(op))["read"]; n_skip += 1
            print(f"  {stamp}: exists -- write-once"); continue
        rel = f"{stamp[:4]}-{stamp[4:6]}-{stamp[6:]}"
        cal = calendar_for(ref_month_of(rel))
        body = body_for(f.read_text(), cal, prev)
        r = None; attempts = 0
        while attempts < 3:
            attempts += 1
            try:
                r = client.messages.create(model=model, max_tokens=4000, system=system,
                                           messages=[{"role": "user", "content": body}])
            except Exception as e:
                if is_fatal(e):
                    sys.exit(f"READ ABORTED (fatal): {type(e).__name__}: {e}")
                print(f"  {stamp}: error on attempt {attempts}: {type(e).__name__}: {e}"); r = None; continue
            if r.stop_reason != "max_tokens":
                break
            print(f"  {stamp}: attempt {attempts} hit max_tokens (likely a whitespace loop), retrying")
        if r is None:
            print(f"  {stamp}: no reply after {attempts} attempts, skipped"); continue
        t = "".join(b.text for b in r.content if b.type == "text").strip()
        t = re.sub(r"^```(?:json)?|```$", "", t, flags=re.M).strip()
        i, j = t.find("{"), t.rfind("}")
        try:
            read = json.loads(t[i:j + 1])
        except Exception:
            raw = OUT_DIR / f"{stamp}_empsit__{PROMPT_VERSION}.RAW.txt"
            raw.write_text(f"stop_reason={r.stop_reason} in={r.usage.input_tokens} out={r.usage.output_tokens}\n\n{t}")
            print(f"  {stamp}: reply was not JSON (stop_reason={r.stop_reason}); raw saved -> {raw.name}"); continue
        rec = {"release_date": rel, "ref_month": ref_month_of(rel), "source_file": str(f), "prompt_file": str(PROMPT_FILE),
               "prompt_version": PROMPT_VERSION, "model": model, "calendar_given": cal,
               "usage": {"input": r.usage.input_tokens, "output": r.usage.output_tokens}, "attempts": attempts,
               "read_at": pd.Timestamp.utcnow().isoformat(), "read": read,
               "reread_of": "previous read of this date superseded (recorded in CURRENT_STATE)" if redo else None}
        op.write_text(json.dumps(rec, ensure_ascii=False, indent=1))
        tok_in += r.usage.input_tokens; tok_out += r.usage.output_tokens
        prev = read; n_read += 1
        print(f"  {stamp}: headline_value={read.get('headline_value')} special={len(read.get('special_factors') or [])} "
              f"calendar={[c.get('status') for c in (read.get('calendar_factors') or [])]}")
        time.sleep(sleep)
    print(f"read {n_read}, skipped {n_skip}; tokens in {tok_in} out {tok_out}")


def score():
    pr = pd.read_csv(PRINTS, parse_dates=["date"])
    pr = pr[pr["name"] == "empsit"].sort_values(["date", "obs"]).copy()
    pr = pr.drop_duplicates("date", keep="last")        # 16 Dec 2025 carried Oct + Nov; the headline is the later month
    pr.index = pr["date"].dt.strftime("%Y%m%d")
    rows = []; ok = 0; n = 0; wc_ok = True
    for stamp, f in texts():
        op = out_path(stamp)
        if not op.exists():
            rows.append((stamp, "not read", "", "", "", "")); continue
        rec = json.load(open(op)); rd = rec["read"]; n += 1
        alfred = float(pr.loc[stamp, "actual_first_print"]) if stamp in pr.index else float("nan")
        hv = rd.get("headline_value")
        match = (hv is not None) and pd.notna(alfred) and abs(float(hv) - alfred) <= 1.0
        ok += bool(match)
        sf = rd.get("special_factors") or []
        cf = rd.get("calendar_factors") or []
        st = ";".join(str(c.get("status")) for c in cf) if cf else "-"
        wc = ""
        if stamp in EXPECTED_STATUS:
            got = {c.get("status") for c in cf}
            wc = f"expected {EXPECTED_STATUS[stamp]}; got {sorted(got) or ['none']}"
            if "supported" in got or EXPECTED_STATUS[stamp] not in got:
                wc_ok = False
        rows.append((stamp, f"{hv}", f"{alfred:g}", "yes" if match else "NO",
                     "; ".join(str(x.get("factor"))[:60] for x in sf) or "(none)", st + (" | " + wc if wc else "")))
    verdict = "PASS" if (n and ok >= n - 1 and wc_ok) else ("INCOMPLETE" if n < len(texts()) else "FAIL")
    L = [f"# A4 — reader consistency on {n} Employment Situation releases (prompt {PROMPT_VERSION})", "",
         f"*Scored {pd.Timestamp.utcnow():%Y-%m-%d}. Criterion (prereg §A4 + §A2b): headline_value equals ALFRED's first print "
         f"within ±1 on ≥ {max(n-1,0)} of {n}; special_factors empty where a human finds none named (column 5 is for that "
         f"check — the founder reads it); on the three World Cup months the calendar statuses are contradicted / contradicted / "
         f"contradicted (July corrected 11 Oct, #44) and never 'supported'.*", "",
         f"**headline_value matches: {ok} / {n}.  World Cup statuses as registered: {'yes' if wc_ok else 'NO'}.  Verdict: {verdict}**", "",
         "| release | reader headline_value | ALFRED first print | match | special_factors named (reader) | calendar statuses |",
         "|---|---|---|---|---|---|"]
    L += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    L += ["", "Population: the 20 releases on file (7 Feb 2025 → 2 Oct 2026). One read each except 4 Sep 2026, read three times: "
          "first with no calendar entry (reference-month bug), then a whitespace loop at the token cap, then good — the "
          "last is the one scored (CURRENT_STATE 18.24). What this does not "
          "measure: whether the reader's directions are right (that is the backfill's job), or anything before 2025."]
    REPORT.write_text("\n".join(L) + "\n")
    print("\n".join(L[:6])); print(f"-> {REPORT}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--score", action="store_true")
    ap.add_argument("--model", default="claude-sonnet-5")
    ap.add_argument("--force", action="store_true", help="re-read existing files -- only those named in --dates")
    ap.add_argument("--dates", nargs="*", default=[], help="YYYYMMDD stamps that --force may re-read")
    ap.add_argument("--sleep", type=float, default=0.5)
    a = ap.parse_args()
    if a.dry_run:
        system, schema = load_prompt()
        stamp, f = texts()[-1]
        rel = f"{stamp[:4]}-{stamp[4:6]}-{stamp[6:]}"
        print("=== SYSTEM PROMPT ===\n" + system + "\n\n=== USER BODY (first 1200 chars) ===\n"
              + body_for(f.read_text(), calendar_for(ref_month_of(rel)), None)[:1200])
        print(f"\n[{len(texts())} texts on file; ~{sum(len(t.read_text()) for _, t in texts())//4} input tokens total]")
    if a.force and not a.dates: sys.exit("--force needs --dates <YYYYMMDD ...>: re-reads are scoped and recorded")
    if a.run: run(a.model, a.force, a.sleep, set(a.dates))
    if a.score: score()
    if not (a.dry_run or a.run or a.score): ap.print_help()


if __name__ == "__main__":
    main()
