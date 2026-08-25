#!/usr/bin/env python3
"""
patch_edgar_exhibits.py -- fetch the EARNINGS RELEASE, not the SEC cover page.

WHAT THE PILOT READ CAUGHT
    earnings_8k pilot: |dir| eq 0.07, dur 0.00, gold 0.00, specificity 0.20,
    novelty 0.09. Near-contentless across the board.

    Cause: cmd_edgar fetches `primaryDocument`. For an Item 2.02 filing that is
    a one-page form whose entire content is "a press release is attached as
    Exhibit 99.1". The numbers live in EX-99.1, a SEPARATE file in the same
    accession folder, which was never fetched.

    Confirmed from the corpus itself -- the whole of the first document is:
        [8-K items: 2.02,8.01,9.01]
        FORM 8-K / Table of Contents / UNITED STATES / SECURITIES AND EXCHANGE
        COMMISSION / Washington, D.C. 20549 / ... Oracle Corporation / Delaware
        / 001-35992 / 500 Oracle Parkway

    The `len(txt.split()) < 60` guard was written to catch this. Cover-page
    boilerplate runs well past 60 words, so it never fired -- a silent filter
    that passed 307 empty documents through.

    THE READER WAS NOT WRONG. It correctly reported that a cover page contains
    no market-relevant information. The CORPUS was wrong.

WHAT THIS PATCH DOES
    1. fetch_sources.py: after the primary document, read the accession's
       index.json, find EX-99* exhibits, and save THOSE as the document body.
       The primary doc is kept as a header only. Every file records which
       exhibits it came from, so a cover-page-only filing is identifiable in
       the corpus rather than silently counted as an earnings release.
    2. A real substance guard that fires: reject if the body has no digits-and-
       currency pattern typical of a results release. Reported, not silent.
    3. doc_read.py: salvage a JSON object from a reply that carries preamble or
       trailing prose, instead of discarding the document. One retry with a
       stricter instruction before giving up. Failures are listed by name at the
       end so they can be re-run rather than lost.
    4. doc_read.py: --max-words default 6000 -> 20000, and the previous-document
       context is capped separately so --with-prev on FOMC minutes does not
       double an already-large call.

Run from the repo root:
    python patch_edgar_exhibits.py --dry-run
    python patch_edgar_exhibits.py
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

EDITS = []

# --- 1. fetch_sources.py: fetch EX-99 exhibits ----------------------------
EDITS.append((
    "src/fetch_sources.py",
    """            url = ARCH.format(cik=str(int(cik)), acc=acc.replace("-", ""), doc=doc)
            try:
                txt = clean(get(url))
            except Exception:
                continue
            if len(txt.split()) < 60:
                continue                      # cover page only, no substance
            f.write_text(f"[{form} items: {items or 'n/a'}]\\n\\n{txt}")""",
    """            accn = acc.replace("-", "")
            url = ARCH.format(cik=str(int(cik)), acc=accn, doc=doc)
            try:
                txt = clean(get(url))
            except Exception:
                continue

            # THE EARNINGS RELEASE IS IN EX-99, NOT THE PRIMARY DOCUMENT.
            # For Item 2.02 the primary doc is a one-page cover saying "a press
            # release is attached as Exhibit 99.1". Fetch the exhibits.
            ex_txt, ex_names = fetch_exhibits(cik, accn, doc, args)
            if ex_txt:
                body = ex_txt
                src_note = f"exhibits: {', '.join(ex_names)}"
            else:
                body = txt
                src_note = "PRIMARY DOCUMENT ONLY -- no EX-99 found"

            # A substance guard that actually fires. Cover-page boilerplate is
            # long (address, jurisdiction, checkboxes), so a word count cannot
            # separate it from a results release; the presence of reported
            # figures can. Rejections are COUNTED and reported, never silent.
            if not has_figures(body):
                skipped_nosub.append(f"{t} {stamp}")
                continue
            f.write_text(f"[{form} items: {items or 'n/a'}] [{src_note}]"
                         f"\\n\\n{body}")""",
    "fetch_sources.cmd_edgar -- fetch EX-99 exhibits, real substance guard",
))

EDITS.append((
    "src/fetch_sources.py",
    """def cmd_edgar(args):
    \"\"\"8-K filings. Item 2.02 IS the earnings release, so this covers both
    earnings line-items and other material corporate events.\"\"\"""",
    """EX_PAT = __import__("re").compile(r"ex[-_]?99", __import__("re").I)
FIG_PAT = __import__("re").compile(
    r"(\\$\\s?\\d|\\d+\\.\\d+\\s*(billion|million|per share)|per diluted share"
    r"|revenue[s]?\\s+(of|were|increased|decreased)|net income|earnings per share)",
    __import__("re").I)


def has_figures(text):
    \"\"\"Does this look like a results release rather than a cover page?

    A word count cannot tell them apart -- SEC cover-page boilerplate (address,
    state of incorporation, checkbox items) runs to several hundred words. The
    presence of reported FIGURES can. Requires at least three distinct matches
    so a single stray dollar sign in boilerplate does not pass.\"\"\"
    return len(set(m.group(0).lower() for m in FIG_PAT.finditer(text))) >= 3


def fetch_exhibits(cik, accn, primary_doc, args, max_ex=3):
    \"\"\"Return (concatenated EX-99* text, [names]) for one accession.

    The accession index.json lists every file in the filing. EX-99 exhibits are
    where an Item 2.02 press release actually lives. Returns ('', []) when none
    is found, so the caller can fall back to the primary document AND LABEL IT.
    \"\"\"
    import json as _j
    idx = (f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accn}/index.json")
    try:
        items = _j.loads(get(idx))["directory"]["item"]
    except Exception:
        return "", []
    names = [i.get("name", "") for i in items]
    cands = [n for n in names
             if n != primary_doc
             and n.lower().endswith((".htm", ".html", ".txt"))
             and EX_PAT.search(n)]
    # deterministic order: 99-1 style before 99-2, so the release leads
    cands = sorted(cands)[:max_ex]
    parts, got = [], []
    for n in cands:
        try:
            t = clean(get(ARCH.format(cik=str(int(cik)), acc=accn, doc=n)))
        except Exception:
            continue
        if len(t.split()) >= 60:
            parts.append(t); got.append(n)
        __import__("time").sleep(max(args.sleep, 0.11))
    return ("\\n\\n".join(parts), got)


def cmd_edgar(args):
    \"\"\"8-K filings. Item 2.02 IS the earnings release -- but the release TEXT
    is in EX-99, not in the primary document, which is a one-page cover.\"\"\"
    skipped_nosub = []""",
    "fetch_sources -- add fetch_exhibits and a working substance guard",
))

EDITS.append((
    "src/fetch_sources.py",
    """    print(f"\\n8-K: {total} documents -> {out}/")
    print("  Item 2.02 = results of operations (the earnings release itself).")""",
    """    print(f"\\n8-K: {total} documents -> {out}/")
    if skipped_nosub:
        print(f"  {len(skipped_nosub)} filing(s) REJECTED as cover-page-only "
              f"(no reported figures found):")
        print("    " + ", ".join(skipped_nosub[:12])
              + (" ..." if len(skipped_nosub) > 12 else ""))
        print("  These are counted, not silently dropped. A high count means the"
              " exhibit fetch is failing, not that the filings are empty.")
    print("  Item 2.02 = results of operations. The release TEXT comes from")
    print("  EX-99 exhibits; the primary document is a cover page and carries")
    print("  no figures. Each file records which exhibits it was built from.")""",
    "fetch_sources -- report cover-page rejections",
))

# --- 2. doc_read.py: salvage JSON instead of discarding -------------------
EDITS.append((
    "src/doc_read.py",
    """    t = "".join(b.text for b in r.content if b.type == "text").strip()
    t = re.sub(r"^```(?:json)?|```$", "", t, flags=re.M).strip()
    return json.loads(t), r.usage.input_tokens, r.usage.output_tokens""",
    """    t = "".join(b.text for b in r.content if b.type == "text").strip()
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
        raise""",
    "doc_read.call -- salvage a JSON object from a reply with preamble",
))

EDITS.append((
    "src/doc_read.py",
    """            try:
                data, a, b = call(client, args.model, src, texts[i], prev)
                tin += a; tout += b
            except Exception as e:
                print(f"    {f.stem}  FAILED: {type(e).__name__}: {e}")
                failed += 1
                continue""",
    """            try:
                data, a, b = call(client, args.model, src, texts[i], prev)
                tin += a; tout += b
            except Exception as e:
                # ONE retry with a stricter instruction before giving up. A
                # transient formatting slip should not cost a document.
                try:
                    data, a, b = call(client, args.model, src,
                                      texts[i] + "\\n\\n[REMINDER: reply with "
                                      "the JSON object ONLY. No preamble, no "
                                      "explanation, no markdown fences.]", prev)
                    tin += a; tout += b
                    print(f"    {f.stem}  recovered on retry")
                except Exception as e2:
                    print(f"    {f.stem}  FAILED: {type(e2).__name__}: {e2}")
                    failed += 1
                    failed_names.append(f"{src}/{f.stem}")
                    continue""",
    "doc_read.main -- one retry before losing a document",
))

EDITS.append((
    "src/doc_read.py",
    """    sources = sorted(PROFILES) if args.all else [args.source]
    rows, tin, tout, failed = [], 0, 0, 0""",
    """    sources = sorted(PROFILES) if args.all else [args.source]
    rows, tin, tout, failed = [], 0, 0, 0
    failed_names = []""",
    "doc_read.main -- track failed document names",
))

EDITS.append((
    "src/doc_read.py",
    """    print(f"\\nread {len(df)} docs, {failed} failed | "
          f"tokens {tin:,} in / {tout:,} out")""",
    """    print(f"\\nread {len(df)} docs, {failed} failed | "
          f"tokens {tin:,} in / {tout:,} out")
    if failed_names:
        print("\\nFAILED, re-runnable (cached reads are skipped, so a re-run "
              "only retries these):")
        for fn in failed_names:
            print(f"    {fn}")""",
    "doc_read.main -- list failed documents by name so they can be re-run",
))

# --- 3. doc_read.py: word caps --------------------------------------------
EDITS.append((
    "src/doc_read.py",
    """    ap.add_argument("--max-words", type=int, default=6000)""",
    """    ap.add_argument("--max-words", type=int, default=20000,
                    help="skip documents longer than this. Raised from 6000 on "
                         "2026-08-24: the cap was dropping 105 of 125 FOMC "
                         "minutes (84%%) and 13 political documents. FOMC "
                         "minutes typically run 10-15k words, so a 6k cap "
                         "excluded the source almost entirely.")
    ap.add_argument("--max-prev-words", type=int, default=3000,
                    help="cap on the PREVIOUS document passed by --with-prev. "
                         "Without this, raising --max-words doubles the cost of "
                         "every minutes call; the previous document is context "
                         "for detecting change, and its opening is enough.")""",
    "doc_read -- raise the word cap and cap the --with-prev context separately",
))

EDITS.append((
    "src/doc_read.py",
    """            prev = texts[i - 1] if (args.with_prev and i > 0) else None""",
    '''            prev = texts[i - 1] if (args.with_prev and i > 0) else None
            if prev is not None:
                pw = prev.split()
                if len(pw) > args.max_prev_words:
                    prev = (" ".join(pw[:args.max_prev_words])
                            + "\\n\\n[previous document truncated for context]\\n")''',
    "doc_read -- truncate the --with-prev context to max_prev_words",
))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    print("=" * 74)
    print("PHASE 1 -- verifying anchors (nothing written)")
    print("=" * 74)
    failures = []
    for path, anchor, _r, label in EDITS:
        p = ROOT / path
        if not p.exists():
            failures.append(f"MISSING FILE: {path}")
            print(f"  FAIL  {path}: not found"); continue
        n = p.read_text().count(anchor)
        if n == 0:
            failures.append(f"ANCHOR NOT FOUND in {path} [{label}]")
            print(f"  FAIL  {path}: anchor not found -- {label}")
            print(f"        sought: {anchor[:70]!r}")
        elif n > 1:
            failures.append(f"ANCHOR NOT UNIQUE ({n}x) in {path} [{label}]")
            print(f"  FAIL  {path}: anchor x{n} -- {label}")
        else:
            print(f"  ok    {path}: {label}")

    if failures:
        print("\n" + "=" * 74)
        print(f"ABORTED -- {len(failures)} failure(s). NO FILE WAS MODIFIED.")
        print("=" * 74)
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)

    print(f"\nall {len(EDITS)} anchors verified, unique.")
    if args.dry_run:
        print("\n--dry-run: nothing written.")
        return

    print("\n" + "=" * 74)
    print("PHASE 2 -- applying")
    print("=" * 74)
    touched = {}
    for path, anchor, repl, label in EDITS:
        text = touched.get(path, (ROOT / path).read_text())
        assert text.count(anchor) == 1, f"anchor lost mid-run: {path} [{label}]"
        touched[path] = text.replace(anchor, repl)
        print(f"  applied  {path}: {label}")
    for path, text in touched.items():
        (ROOT / path).write_text(text)
        print(f"  written  {path}")

    print("\n" + "=" * 74)
    print("""NEXT -- re-fetch the 8-K corpus, then check ONE file before spending
on the full read:

  # the existing 307 files are cover pages; move them aside, do not delete
  mv data_provenance/docs/earnings_8k data_provenance/docs/earnings_8k_coverpages

  python -m src.fetch_sources edgar --limit 25          # small, to verify

  # this MUST now show revenue / EPS / per-share figures, not an address block
  head -c 900 "$(ls data_provenance/docs/earnings_8k/*.txt | head -1)"

  # then a 20-doc pilot re-read; specificity and |dir| must rise sharply
  python -m src.doc_read --source earnings_8k --limit 20 \\
      --out processed/pilot_8k_v2.csv

Only if |dir| and specificity move should the full corpus read be started.
""")
    print("=" * 74)


if __name__ == "__main__":
    main()
