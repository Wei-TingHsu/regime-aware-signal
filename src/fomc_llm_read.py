"""
fomc_llm_read.py -- PROBLEM 3, STEP 2: read what the Fed said.

    fetch_fomc_dates -> WHEN        (done)
    fomc_corpus      -> WHAT text   (done)
    fomc_llm_read    -> STANCE      <-- this file
    (next) analog-conditioned effect: what did THIS stance do to each asset in
           the historical periods that resemble TODAY, weighted by similarity
           and recency

THE CENTRAL DESIGN DECISION: THE MODEL DOES NOT PREDICT RETURNS
    It would be easy, and wrong, to ask "what will gold do after this statement".
    Two reasons not to:

    1. OUTCOME LEAKAGE. The model has read market history. Shown a 2020 statement
       it may recall what gold actually did, and the pipeline would look
       predictive while doing nothing but remembering. Asking instead "is this
       hawkish relative to the previous statement" is a reading-comprehension
       task about the text in front of it.
    2. SEPARATION OF CONCERNS. Text -> STANCE is a language job. STANCE -> asset
       direction is an empirical job, and it must be answered by the historical
       data CONDITIONED ON THE CURRENT MACRO STATE -- which is the whole point of
       the design. Letting the LLM shortcut straight to a direction would destroy
       the conditioning that makes this different from a generic sentiment score.

    So: the model outputs stance and evidence. Direction comes from data, later.

STATEMENTS ARE READ AS DELTAS
    Practitioners read FOMC statements by diffing them against the previous one --
    the words that CHANGED carry the signal. Each statement is therefore sent with
    its immediate predecessor in context, and the model is asked for both the
    absolute stance and the SHIFT.

OUTPUT (one JSON per statement, plus a combined CSV)
    stance          -1 (very dovish) .. +1 (very hawkish), absolute reading
    shift           -1 .. +1, change vs the PREVIOUS statement (0 = no change)
    inflation       -1 .. +1, concern about inflation
    labor           -1 .. +1, -1 = deteriorating, +1 = strong/tight
    growth          -1 .. +1
    guidance        -1 .. +1, forward guidance direction
    uncertainty      0 .. 1, hedging / conditionality in the language
    confidence       0 .. 1, the model's confidence in its own read
    evidence        up to 3 short quotes it keyed on (<15 words each)
    changed_phrases what changed vs the previous statement

REPRODUCIBILITY
    Prompt version stamped into every record. Re-reading with a different prompt
    writes a different version rather than overwriting, so reads stay comparable
    across prompt revisions. (temperature is not passed: anthropic SDK 1.x
    removed it from Messages.create. Reads are therefore not bit-deterministic --
    the stored JSON is the record of what was actually read.)

Run:
    export ANTHROPIC_API_KEY=...
    python -m src.fomc_llm_read --limit 3          # inspect before spending
    python -m src.fomc_llm_read                    # full corpus
    python -m src.fomc_llm_read --out processed/fomc_stance.csv
"""
import argparse
import json
import os
import re
import time
from pathlib import Path

import pandas as pd

CORPUS = Path("data_provenance/fomc")
READS = Path("data_provenance/fomc_reads")
PROMPT_VERSION = "v1-2026-08-23"

SYSTEM = """You classify the POLICY STANCE of Federal Reserve FOMC statements.

You are NOT forecasting markets. Do not reason about what any asset will do. Do
not use any recollection of what happened after this statement. Judge ONLY the
language in the text provided, relative to the previous statement given.

Return STRICT JSON, no preamble, no markdown fences, exactly these keys:
{"stance": float, "shift": float, "inflation": float, "labor": float,
 "growth": float, "guidance": float, "uncertainty": float, "confidence": float,
 "evidence": [string], "changed_phrases": [string]}

Scales:
  stance   -1 very dovish .. 0 neutral .. +1 very hawkish (absolute reading)
  shift    -1 much more dovish than the previous statement .. +1 much more
           hawkish. 0 means materially unchanged. Most consecutive statements
           differ only slightly; do not inflate this.
  inflation -1 inflation concern receding .. +1 elevated concern
  labor    -1 deteriorating .. +1 strong or tight
  growth   -1 weakening .. +1 strengthening
  guidance -1 signalling easing ahead .. +1 signalling tightening ahead
  uncertainty 0 confident and direct .. 1 heavily hedged and conditional
  confidence  0 .. 1, YOUR confidence in this read

evidence: up to 3 quotes, each UNDER 15 WORDS, drawn verbatim from the CURRENT
statement, that drove your scores.
changed_phrases: up to 3 short notes on what changed versus the previous
statement. Empty list if there is no previous statement."""


def call(client, model, prev, cur):
    prev_block = prev if prev else "(none - this is the first statement in the corpus)"
    msg = (f"PREVIOUS STATEMENT:\n{prev_block}\n\n"
           f"CURRENT STATEMENT:\n{cur}\n\n"
           f"Classify the CURRENT statement. JSON only.")
    r = client.messages.create(
        model=model, max_tokens=1200,
        system=SYSTEM, messages=[{"role": "user", "content": msg}])
    txt = "".join(b.text for b in r.content if b.type == "text").strip()
    txt = re.sub(r"^```(?:json)?|```$", "", txt, flags=re.M).strip()
    return json.loads(txt), r.usage.input_tokens, r.usage.output_tokens


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="claude-sonnet-5")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--max-words", type=int, default=1200,
                    help="skip files longer than this: likely untrimmed page "
                         "furniture rather than statement text")
    ap.add_argument("--sleep", type=float, default=0.3)
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--out", default="processed/fomc_stance.csv")
    args = ap.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("set ANTHROPIC_API_KEY first")
    try:
        from anthropic import Anthropic
    except ImportError:
        raise SystemExit("pip install anthropic")
    client = Anthropic()

    files = sorted(CORPUS.glob("*.txt"))
    if not files:
        raise SystemExit(f"no corpus at {CORPUS}/ -- run fomc_corpus first")
    READS.mkdir(parents=True, exist_ok=True)

    texts = {f.stem: f.read_text() for f in files}
    stems = sorted(texts)
    long_ones = [s for s in stems if len(texts[s].split()) > args.max_words]
    if long_ones:
        print(f"SKIPPING {len(long_ones)} file(s) over {args.max_words} words "
              f"(likely untrimmed): {', '.join(long_ones[:6])}"
              + (" ..." if len(long_ones) > 6 else ""))
        print("  Fix the trimmer and re-read them rather than feeding furniture "
              "to the model.\n")
    usable = [s for s in stems if s not in long_ones]
    todo = usable if args.limit is None else usable[:args.limit]

    print(f"reading {len(todo)} of {len(stems)} statements | model {args.model} "
          f"| prompt {PROMPT_VERSION}")
    rows, tin, tout, failed = [], 0, 0, 0
    for i, stem in enumerate(todo):
        out_f = READS / f"{stem}_{PROMPT_VERSION}.json"
        if out_f.exists() and not args.refresh:
            rows.append(json.loads(out_f.read_text()))
            continue
        j = usable.index(stem)
        prev = texts[usable[j - 1]] if j > 0 else None
        try:
            data, a, b = call(client, args.model, prev, texts[stem])
            tin += a; tout += b
        except Exception as e:
            print(f"  {stem}  FAILED: {type(e).__name__}: {e}")
            failed += 1
            continue
        data["date"] = pd.to_datetime(stem, format="%Y%m%d").strftime("%Y-%m-%d")
        data["prompt_version"] = PROMPT_VERSION
        data["model"] = args.model
        out_f.write_text(json.dumps(data, indent=2))
        rows.append(data)
        if (i + 1) % 10 == 0:
            print(f"  {i+1}/{len(todo)} ...")
        time.sleep(args.sleep)

    if not rows:
        raise SystemExit("nothing read")
    df = pd.DataFrame(rows).sort_values("date")
    keep = ["date", "stance", "shift", "inflation", "labor", "growth",
            "guidance", "uncertainty", "confidence", "prompt_version", "model"]
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    df[[c for c in keep if c in df]].to_csv(out, index=False)

    print(f"\nread {len(df)} statements, {failed} failed")
    print(f"tokens: {tin:,} in / {tout:,} out")
    print(f"\nstance  mean {df['stance'].mean():+.2f}  "
          f"range {df['stance'].min():+.2f}..{df['stance'].max():+.2f}")
    print(f"shift   mean {df['shift'].mean():+.2f}  "
          f"|shift|>0.3 on {(df['shift'].abs() > 0.3).sum()} statements")
    print(f"confidence median {df['confidence'].median():.2f}")
    print(f"\n-> {out}   full reads with evidence in {READS}/")
    print("\nSANITY CHECK BEFORE USING THIS: open 3-4 JSON reads from dates whose")
    print("policy you know (e.g. 2015-12 first hike, 2020-03 emergency cuts,")
    print("2022-06 75bp) and confirm the stance sign matches. A reader that gets")
    print("those wrong will not be rescued by any downstream statistics.")


if __name__ == "__main__":
    main()
