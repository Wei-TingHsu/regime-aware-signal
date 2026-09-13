"""
doc_read.py -- PROBLEM 3, STEP 2 GENERALISED: read ANY information source into
ONE comparable schema.

WHY ONE SCHEMA MATTERS MORE THAN ANY SINGLE SOURCE
    Step 5 of the design is "weigh which force dominates when several land the
    same day". That is impossible unless every source is measured on the SAME
    scale. A hawkish FOMC statement and an NVDA earnings beat and a Trump tariff
    post have to produce commensurable numbers or there is nothing to weigh.

    So: source-specific PROMPTS, one common OUTPUT.

INGESTION IS A DROP FOLDER, NOT A SCRAPER
    Sources differ enormously in how they are obtained -- Fed pages parse
    cleanly, EDGAR has an API, conference transcripts are downloaded by hand,
    media summaries are copy-pasted. Rather than a scraper per source, every
    source lands as dated text in:

        data_provenance/docs/<source_type>/<YYYYMMDD>[_<id>].txt

    Anything in that layout is readable, whether a script fetched it or a human
    saved it. Manual collection builds HISTORY; automation handles LIVE.

THE LIVE-VS-BACKTEST ASYMMETRY, recorded because it decides what is usable
    A source collectable only going forward can NEVER enter step 3, which asks
    "what did this kind of news do in macro-similar history". No history, no
    conditioning. Such a source can enter the live system only as an
    unvalidated input, and must be labelled that way in any output shown to a
    customer.

COMMON SCHEMA (every source, every document)
    direction     dict, -1..+1 per asset class: equity, duration, gold, dollar,
                  oil. Sign = which way this news pushes that asset.
    magnitude     0..1, how big a move this warrants relative to typical news
                  of its type. NOT a return forecast.
    horizon_days  over how many sessions the effect would plausibly play out.
    specificity   0..1. Concrete, verifiable, immediately actionable (a rate
                  decision, a reported EPS) = high. Vague intention, aspiration
                  or rhetoric = low. This is what separates a signed executive
                  order from a social-media threat, and it is the field that
                  makes political sources usable at all.
    novelty       0..1, how much is NOT already expected/priced by the time of
                  release, judged from the text alone.
    confidence    0..1, the model's confidence in its own read.
    evidence      up to 3 verbatim quotes under 15 words each.

    Source-specific extras (stance for Fed, surprise_direction for earnings,
    etc.) are kept alongside but are NOT used for cross-source weighing.

THE MODEL NEVER PREDICTS RETURNS
    It reads content and classifies it. What a given direction/magnitude
    actually DID is answered by the data in step 3, conditioned on the macro
    state -- not by the model's recollection of history. This is also the main
    defence against outcome leakage on documents the model has seen before.

Run:
    python -m src.doc_read --source fomc_statement
    python -m src.doc_read --all
    python -m src.doc_read --list                     # what is in the drop folder
"""
import argparse
import json
import os
import re
import time
from pathlib import Path

import pandas as pd

DOCS = Path("data_provenance/docs")
READS = Path("data_provenance/doc_reads")
PROMPT_VERSION = "v1-2026-08-23"

COMMON = """Return STRICT JSON, no preamble, no markdown fences, exactly:
{"direction": {"equity": float, "duration": float, "gold": float,
               "dollar": float, "oil": float},
 "magnitude": float, "horizon_days": int, "specificity": float,
 "novelty": float, "confidence": float, "evidence": [string], "extra": {}}

direction    -1..+1 per asset class. Sign only: which way does this news PUSH
             that asset. "duration" means long-dated government bonds (price,
             so falling yields = positive). 0.0 if the news says nothing about it.
magnitude    0..1, size relative to TYPICAL news of this same type. A routine
             release is ~0.2; a genuine regime break is ~0.9. NOT a return.
horizon_days over how many trading sessions would this plausibly play out.
specificity  0..1. Concrete, verifiable, already decided = high. Aspiration,
             intention, rhetoric or threat = low.
novelty      0..1. How much of this was NOT already expected before release,
             judged from the text alone.
confidence   0..1, your confidence in this read.
evidence     up to 3 verbatim quotes from the document, each under 15 words.
extra        source-specific fields as instructed below; {} if none.

You are NOT forecasting markets. Do not reason about what any asset actually
did. Do not use recollection of subsequent events. Judge only this text."""

PROFILES = {
    "fomc_statement": ("You classify the policy stance of a Federal Reserve FOMC "
                       "statement.",
                       '"extra": {"stance": -1..+1 hawkish positive, '
                       '"guidance": -1..+1}'),
    "fomc_minutes": ("You classify FOMC meeting minutes. Minutes reveal the "
                     "DISPERSION of views and the conditions attached to future "
                     "action; weigh those over the headline decision, which was "
                     "already public three weeks earlier.",
                     '"extra": {"stance": -1..+1, "dispersion": 0..1}'),
    "earnings_8k": ("You classify a company earnings release (SEC 8-K Item 2.02 "
                    "or equivalent). Weigh GUIDANCE over reported results: the "
                    "quarter is history, the outlook is not.",
                    '"extra": {"surprise": -1..+1, "guidance_change": -1..+1, '
                    '"ticker": string}'),
    "political_order": (
        "You classify a United States presidential EXECUTIVE ORDER, "
        "PRESIDENTIAL ORDER or PRESIDENTIAL DETERMINATION as published in the "
        "Federal Register. Separate what has been DECIDED from what has been "
        "merely SAID or planned, and judge the text on its own terms.",
        '"extra": {"actor": string, "is_decided": true/false, '
        '"sectors": [string]}'),
    "political_other": (
        "You classify a United States presidential PROCLAMATION, NOTICE or "
        "MEMORANDUM as published in the Federal Register. Separate what has "
        "been DECIDED from what has been merely SAID or planned, and judge the "
        "text on its own terms. Note that this document class spans a wide "
        "range: some are administrative or commemorative, others carry "
        "operative trade or emergency measures. Judge each document by its own "
        "content, not by its class.",
        '"extra": {"actor": string, "is_decided": true/false, '
        '"sectors": [string]}'),
    "political_order": (
        "You classify a United States presidential EXECUTIVE ORDER, "
        "PRESIDENTIAL ORDER or PRESIDENTIAL DETERMINATION as published in the "
        "Federal Register. Separate what has been DECIDED from what has been "
        "merely SAID or planned, and judge the text on its own terms.",
        '"extra": {"actor": string, "is_decided": true/false, '
        '"sectors": [string]}'),
    "political_other": (
        "You classify a United States presidential PROCLAMATION, NOTICE or "
        "MEMORANDUM as published in the Federal Register. Separate what has "
        "been DECIDED from what has been merely SAID or planned, and judge the "
        "text on its own terms. Note that this document class spans a wide "
        "range: some are administrative or commemorative, others carry "
        "operative trade or emergency measures. Judge each document by its own "
        "content, not by its class.",
        '"extra": {"actor": string, "is_decided": true/false, '
        '"sectors": [string]}'),
    "political": ("You classify a political or policy communication (executive "
                  "statement, social post, official remarks). CRITICAL: separate "
                  "what has been DECIDED from what has been merely SAID. A signed "
                  "order and a threat to act are not the same event; the "
                  "difference belongs in `specificity`, and a low-specificity "
                  "item should carry low magnitude even if the language is "
                  "forceful.",
                  '"extra": {"actor": string, "is_decided": true/false, '
                  '"sectors": [string]}'),
    "bank_research": ("You classify a published summary of investment-bank "
                      "research or a strategist view. This is opinion, not fact: "
                      "keep `novelty` low unless it contains information not "
                      "already public.",
                      '"extra": {"institution": string, "conviction": 0..1}'),
    "transcript": ("You classify an executive appearance -- fireside chat, "
                   "conference, interview. Weigh forward-looking commitments and "
                   "changes in tone over restated known facts.",
                   '"extra": {"speaker": string, "company": string}'),
}


# Errors that will NEVER succeed on retry. Retrying these burned 897 pointless
# calls on 2026-08-25 after the API balance ran out mid-run, and produced a log
# that looked like a completed pass.
FATAL_MARKERS = (
    "credit balance is too low",
    "invalid x-api-key",
    "authentication_error",
    "permission_error",
    "insufficient_quota",
)


def is_fatal(exc):
    """Is this error permanent for the whole run, not just this document?

    Deliberately matches on the MESSAGE rather than the exception class: the
    SDK raises BadRequestError for both a malformed request (per-document, worth
    retrying) and an exhausted balance (fatal). The class cannot tell them
    apart; the message can."""
    s = f"{type(exc).__name__}: {exc}".lower()
    return any(m in s for m in FATAL_MARKERS)


def parse_name(p):
    m = re.match(r"(\d{8})(?:_(.+))?$", p.stem)
    if not m:
        return None, None
    return pd.to_datetime(m.group(1), format="%Y%m%d"), (m.group(2) or "")


def call(client, model, profile, text, prev=None):
    role, extra = PROFILES[profile]
    system = f"{role}\n\n{COMMON}\n\nFor this source type, extra must be:\n{extra}"
    body = f"DOCUMENT:\n{text}"
    if prev:
        body = f"PREVIOUS DOCUMENT OF THE SAME TYPE:\n{prev}\n\n{body}"
    r = client.messages.create(model=model, max_tokens=1400, system=system,
                               messages=[{"role": "user", "content": body}])
    t = "".join(b.text for b in r.content if b.type == "text").strip()
    t = re.sub(r"^```(?:json)?|```$", "", t, flags=re.M).strip()
    try:
        return json.loads(t), r.usage.input_tokens, r.usage.output_tokens
    except json.JSONDecodeError:
        # Salvage: the reply carried preamble or trailing prose. Take the
        # outermost {...} rather than discarding a document that cost a full
        # call. A 4,399-word FOMC minutes doc -- well under the word cap -- was
        # lost this way in the 2026-08-24 pilot.
        i, j = t.find("{"), t.rfind("}")
        if i != -1 and j > i:
            try:
                return (json.loads(t[i:j + 1]), r.usage.input_tokens,
                        r.usage.output_tokens)
            except json.JSONDecodeError:
                pass
        raise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=sorted(PROFILES))
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--repair-cache", action="store_true",
                    help="scan every cached read, report and DELETE any that "
                         "will not parse, then exit. Deleted entries are simply "
                         "re-read on the next run at the cost of one API call "
                         "each.")
    ap.add_argument("--model", default="claude-sonnet-5")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--unread-only", action="store_true",
                    help="drop documents already in the read cache BEFORE "
                         "applying --limit, so the cap is spent on new reads")
    ap.add_argument("--since",
                    help="YYYYMMDD; drop documents dated before this BEFORE "
                         "--unread-only and --limit. Keeps deferred backfill "
                         "sets out of the nightly cap.")
    ap.add_argument("--max-words", type=int, default=20000,
                    help="skip documents longer than this. Raised from 6000 on "
                         "2026-08-24: the cap was dropping 105 of 125 FOMC "
                         "minutes (84%%) and 13 political documents. FOMC "
                         "minutes typically run 10-15k words, so a 6k cap "
                         "excluded the source almost entirely.")
    ap.add_argument("--max-prev-words", type=int, default=3000,
                    help="cap on the PREVIOUS document passed by --with-prev. "
                         "Without this, raising --max-words doubles the cost of "
                         "every minutes call; the previous document is context "
                         "for detecting change, and its opening is enough.")
    ap.add_argument("--with-prev", action="store_true",
                    help="pass the previous document of the same type as "
                         "context (deltas matter for Fed statements)")
    ap.add_argument("--sleep", type=float, default=0.3)
    ap.add_argument("--out", default="processed/doc_reads.csv")
    args = ap.parse_args()

    if args.repair_cache:
        files = sorted(READS.glob("*.json")) if READS.exists() else []
        bad = []
        for p in files:
            try:
                json.loads(p.read_text())
            except Exception as e:
                bad.append((p, type(e).__name__))
        print(f"cache scan: {len(files)} entries, {len(bad)} unparseable")
        for p, e in bad:
            print(f"  DELETE {p.name}  ({e})")
            try:
                p.unlink()
            except OSError as e2:
                print(f"    could not delete: {e2}")
        # stray temp files from an interrupted atomic write
        tmps = sorted(READS.glob("*.tmp")) if READS.exists() else []
        for p in tmps:
            print(f"  DELETE {p.name}  (stray temp)")
            try:
                p.unlink()
            except OSError:
                pass
        print(f"\n{len(bad)} deleted, {len(tmps)} temp file(s) removed. "
              f"They will be re-read at one API call each.")
        return

    DOCS.mkdir(parents=True, exist_ok=True)
    if args.list or not (args.source or args.all):
        print(f"drop folder: {DOCS}/<source_type>/<YYYYMMDD>[_<id>].txt\n")
        print("recognised source types:")
        for k, (role, _) in PROFILES.items():
            d = DOCS / k
            n = len(list(d.glob("*.txt"))) if d.exists() else 0
            print(f"  {k:16} {n:5d} docs   {role.split('.')[0][:52]}")
        print("\nAnything dropped into that layout is readable -- fetched by a "
              "script or saved by hand.")
        if not (args.source or args.all):
            return

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("set ANTHROPIC_API_KEY")
    from anthropic import Anthropic
    client = Anthropic()
    READS.mkdir(parents=True, exist_ok=True)

    sources = sorted(PROFILES) if args.all else [args.source]
    rows, tin, tout, failed = [], 0, 0, 0
    failed_names = []
    for src in sources:
        d = DOCS / src
        if not d.exists():
            continue
        files = sorted(d.glob("*.txt"))
        pairs = [(f, *parse_name(f)) for f in files]
        pairs = [(f, dt, i) for f, dt, i in pairs if dt is not None]
        bad = len(files) - len(pairs)
        if bad:
            print(f"  {src}: {bad} file(s) skipped -- name must be "
                  f"YYYYMMDD[_id].txt")
        pairs.sort(key=lambda x: x[1])
        if args.since:
            n0 = len(pairs)
            pairs = [t for t in pairs if t[0].stem[:8] >= args.since]
            print(f"  {src}: --since {args.since}: "
                  f"{n0 - len(pairs)} older doc(s) left for a dedicated run")
        texts = [f.read_text() for f, _, _ in pairs]
        # TRUNCATE, DO NOT SKIP (2026-08-25, prereg_analog_event section 11).
        # Skipping dropped 189 of 834 earnings documents -- 23% -- all 6-K
        # complete submissions where the whole filing is one file because
        # foreign issuers file no separate EX-99. An earnings release's figures
        # sit near the TOP; the tail is exhibits and signature pages.
        # The truncation is RECORDED, not silent.
        orig_words = {i: len(t.split()) for i, t in enumerate(texts)}
        long_ = [i for i in range(len(texts)) if orig_words[i] > args.max_words]
        for i in long_:
            texts[i] = (" ".join(texts[i].split()[:args.max_words])
                        + f"\n\n[DOCUMENT TRUNCATED at {args.max_words} words "
                          f"of {orig_words[i]}. The remainder is not shown. "
                          f"Judge only what is above.]\n")
        if long_:
            print(f"  {src}: {len(long_)} doc(s) over {args.max_words} words, "
                  f"TRUNCATED and read (was: skipped)")
        use = list(range(len(pairs)))
        if args.unread_only:
            use = [i for i in use
                   if not (READS / f"{src}__{pairs[i][0].stem}__"
                                   f"{PROMPT_VERSION}.json").exists()]
            print(f"  {src}: {len(use)} unread of {len(pairs)}")
        if args.limit:
            use = use[:args.limit]
        if not use:
            continue
        print(f"\n{src}: reading {len(use)} of {len(pairs)} docs")
        for k, i in enumerate(use):
            f, dt, did = pairs[i]
            out_f = READS / f"{src}__{f.stem}__{PROMPT_VERSION}.json"
            if out_f.exists():
                # SELF-HEALING. A cache file that will not parse is deleted and
                # the document re-read. A concurrent double-launch on
                # 2026-08-25 spliced two JSON objects into one file, and the
                # unguarded json.loads() below aborted the whole run on a CACHE
                # READ -- before any API call -- blocking that source until the
                # file was found by hand. A corrupt entry should cost one call,
                # not a source.
                try:
                    rows.append(json.loads(out_f.read_text()))
                    continue
                except (json.JSONDecodeError, OSError) as ce:
                    print(f"    {f.stem}  CORRUPT CACHE ({type(ce).__name__}), "
                          f"deleting and re-reading: {out_f.name}")
                    try:
                        out_f.unlink()
                    except OSError:
                        pass
            prev = texts[i - 1] if (args.with_prev and i > 0) else None
            if prev is not None:
                pw = prev.split()
                if len(pw) > args.max_prev_words:
                    prev = (" ".join(pw[:args.max_prev_words])
                            + "\n\n[previous document truncated for context]\n")
            try:
                data, a, b = call(client, args.model, src, texts[i], prev)
                tin += a; tout += b
            except Exception as e:
                if is_fatal(e):
                    remaining = len(use) - k
                    print("\n" + "!" * 70)
                    print("FATAL -- ABORTING THE WHOLE RUN, NOT JUST THIS DOC")
                    print(f"  {type(e).__name__}: {e}")
                    print(f"\n  {src}: {k} read this session, "
                          f"{remaining} NOT READ.")
                    print("  This error is permanent for the run. Retrying it "
                          "is pointless and")
                    print("  continuing past it produces a log that looks like "
                          "a completed pass --")
                    print("  which is exactly what happened on 2026-08-25: 897 "
                          "documents failed")
                    print("  this way over four hours.")
                    print("\n  Everything read so far IS CACHED. Fix the cause, "
                          "re-run the same")
                    print("  command, and only the unread documents are billed.")
                    print("!" * 70)
                    raise SystemExit(1)
                # ONE retry with a stricter instruction before giving up. A
                # transient formatting slip should not cost a document.
                try:
                    data, a, b = call(client, args.model, src,
                                      texts[i] + "\n\n[REMINDER: reply with "
                                      "the JSON object ONLY. No preamble, no "
                                      "explanation, no markdown fences.]", prev)
                    tin += a; tout += b
                    print(f"    {f.stem}  recovered on retry")
                except Exception as e2:
                    if is_fatal(e2):
                        print("\n" + "!" * 70)
                        print("FATAL ON RETRY -- ABORTING THE WHOLE RUN")
                        print(f"  {type(e2).__name__}: {e2}")
                        print(f"  {src}: {k} read this session, "
                              f"{len(use) - k} NOT READ. Cached reads are kept.")
                        print("!" * 70)
                        raise SystemExit(1)
                    print(f"    {f.stem}  FAILED: {type(e2).__name__}: {e2}")
                    failed += 1
                    failed_names.append(f"{src}/{f.stem}")
                    continue
            data.update(source=src, date=dt.strftime("%Y-%m-%d"), doc_id=did,
                        prompt_version=PROMPT_VERSION, model=args.model,
                        truncated=bool(i in long_),
                        orig_words=int(orig_words[i]),
                        max_words=int(args.max_words))
            # ATOMIC WRITE. os.replace() is atomic on POSIX, so two writers
            # can only produce a whole file from one or a whole file from the
            # other -- never a splice. A plain write_text() here is what let a
            # double-launched run corrupt the cache on 2026-08-25.
            tmp_f = out_f.with_suffix(f".{os.getpid()}.tmp")
            tmp_f.write_text(json.dumps(data, indent=2))
            os.replace(tmp_f, out_f)
            rows.append(data)
            if (k + 1) % 20 == 0:
                print(f"    {k+1}/{len(use)} ...")
            time.sleep(args.sleep)

    if not rows:
        print("\nnothing read")
        return
    flat = []
    for r in rows:
        d = r.get("direction", {}) or {}
        # NOTE: column names are prefixed dir_* deliberately. A column called
        # "eq" collides with pandas' DataFrame.eq() method, so g.eq returns the
        # bound method rather than the column -- an AttributeError at best and
        # silently wrong at worst.
        flat.append(dict(date=r.get("date"), source=r.get("source"),
                         doc_id=r.get("doc_id", ""),
                         # Read condition, carried into the CSV so any
                         # cross-source comparison can show whether it is also a
                         # cross-prompt or cross-model comparison. Without these
                         # two columns that mixture is invisible.
                         prompt_version=r.get("prompt_version", ""),
                         model=r.get("model", ""),
                         truncated=r.get("truncated", False),
                         orig_words=r.get("orig_words", None),
                         dir_eq=d.get("equity"), dir_dur=d.get("duration"),
                         dir_gold=d.get("gold"), dir_usd=d.get("dollar"),
                         dir_oil=d.get("oil"),
                         magnitude=r.get("magnitude"),
                         horizon_days=r.get("horizon_days"),
                         specificity=r.get("specificity"),
                         novelty=r.get("novelty"),
                         confidence=r.get("confidence")))
    df = pd.DataFrame(flat).sort_values(["date", "source"])
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)

    print(f"\nread {len(df)} docs, {failed} failed | "
          f"tokens {tin:,} in / {tout:,} out")
    if failed_names:
        print("\nFAILED, re-runnable (cached reads are skipped, so a re-run "
              "only retries these):")
        for fn in failed_names:
            print(f"    {fn}")
    print("\nby source:")
    for s, g in df.groupby("source"):
        print(f"  {s:16} n={len(g):4d}  |dir| mean "
              f"eq {g['dir_eq'].abs().mean():.2f} "
              f"dur {g['dir_dur'].abs().mean():.2f} "
              f"gold {g['dir_gold'].abs().mean():.2f} | specificity "
              f"{g['specificity'].mean():.2f} | "
              f"novelty {g['novelty'].mean():.2f}")
    print(f"\n-> {out}   full reads in {READS}/")
    print("\nCHECK BEFORE USE: specificity should SEPARATE sources -- decided")
    print("policy and reported earnings high, rhetoric and opinion low. If every")
    print("source scores alike, the field is not discriminating and step 5 has")
    print("nothing to weigh with.")


if __name__ == "__main__":
    main()
