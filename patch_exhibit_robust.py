#!/usr/bin/env python3
"""
patch_exhibit_robust.py -- recover NVDA, TSLA, INTC. Stop guessing filenames.

WHAT FAILED
    First exhibit patch: NVDA 0/25 saved, INTC 2/25, TSLA 4/25, 91 filings
    rejected as cover-page-only. The exhibit fetch found nothing and fell back
    to the primary document, which has no figures, so has_figures() rejected it.

    Root cause: fetch_exhibits matched filenames against `ex[-_]?99` and accepted
    only .htm/.html/.txt. That is a guess about naming conventions, and issuers
    do not share one. TSLA files exhibits as PDF. Some issuers name the release
    with no "ex99" substring at all.

    Losing NVDA is not acceptable: it is a spotlight name AND the announcer in
    the cross-firm spillover finding, the mechanism that fixed the entry
    convention for the whole project.

THE FIX -- stop pattern-matching, start testing content
    1. Try the EX_PAT names first (fast path, usually right).
    2. If that yields nothing, fall back to scanning EVERY non-primary document
       in the accession and keeping any that passes has_figures(). A results
       release is identified by CONTAINING REPORTED FIGURES, which is what we
       actually care about -- not by what someone named the file.
    3. PDFs are accepted when pdftotext or pypdf is available; when a PDF is the
       only candidate and neither is installed, that is REPORTED, not silent.
    4. When nothing is found, print the accession's actual filenames. The next
       failure of this kind then names itself instead of vanishing into a count.

    Cost: the fallback fetches more files per accession, so it is capped and
    only runs when the fast path fails.

Run from the repo root:
    python patch_exhibit_robust.py --dry-run
    python patch_exhibit_robust.py
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

EDITS = [(
    "src/fetch_sources.py",
    '''def fetch_exhibits(cik, accn, primary_doc, args, max_ex=3):
    """Return (concatenated EX-99* text, [names]) for one accession.

    The accession index.json lists every file in the filing. EX-99 exhibits are
    where an Item 2.02 press release actually lives. Returns ('', []) when none
    is found, so the caller can fall back to the primary document AND LABEL IT.
    """
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
    return ("\\n\\n".join(parts), got)''',
    '''def _pdf_text(raw_bytes):
    """Extract text from a PDF exhibit. Returns '' when no extractor is
    available -- the caller REPORTS that rather than silently skipping."""
    try:
        import io
        from pypdf import PdfReader
        return "\\n".join((p.extract_text() or "")
                          for p in PdfReader(io.BytesIO(raw_bytes)).pages)
    except Exception:
        return ""


def _fetch_one(cik, accn, name, args):
    """Fetch one document from an accession. Handles htm/txt and pdf."""
    url = ARCH.format(cik=str(int(cik)), acc=accn, doc=name)
    if name.lower().endswith(".pdf"):
        try:
            import urllib.request
            req = urllib.request.Request(
                url, headers={"User-Agent": __import__("os").environ.get(
                    "SEC_CONTACT", "research contact@example.com")})
            with urllib.request.urlopen(req, timeout=30) as r:
                txt = _pdf_text(r.read())
            return txt, ("" if txt else "pdf-no-extractor")
        except Exception as e:
            return "", f"pdf-fetch-failed:{type(e).__name__}"
    try:
        return clean(get(url)), ""
    except Exception as e:
        return "", f"fetch-failed:{type(e).__name__}"


def fetch_exhibits(cik, accn, primary_doc, args, max_ex=3, max_scan=8,
                   ticker=""):
    """Return (release text, [names]) for one accession.

    TWO PASSES. The first matches EX_PAT filenames -- fast and usually right.
    The second, used ONLY when the first yields nothing, scans every other
    document in the accession and keeps whatever CONTAINS REPORTED FIGURES.

    The second pass exists because the first is a guess about naming
    conventions and issuers do not share one: NVDA saved 0 of 25 and TSLA 4 of
    25 under filename matching alone. A results release is identified by its
    CONTENT, not by what someone called the file.

    When both passes fail, the accession's actual filenames are printed, so the
    next failure of this kind names itself instead of vanishing into a count.
    """
    import json as _j
    idx = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accn}/index.json"
    try:
        items = _j.loads(get(idx))["directory"]["item"]
    except Exception as e:
        if args.verbose_exhibits:
            print(f"      {ticker} {accn}: index.json FAILED "
                  f"({type(e).__name__})")
        return "", []
    names = [i.get("name", "") for i in items if i.get("name")]
    doc_ext = (".htm", ".html", ".txt", ".pdf")
    others = [n for n in names
              if n != primary_doc and n.lower().endswith(doc_ext)]

    def _try(cands, need_figures):
        parts, got, notes = [], [], []
        for n in cands:
            t, note = _fetch_one(cik, accn, n, args)
            if note:
                notes.append(f"{n}:{note}")
            __import__("time").sleep(max(args.sleep, 0.11))
            if len(t.split()) < 60:
                continue
            if need_figures and not has_figures(t):
                continue
            parts.append(t); got.append(n)
            if len(got) >= max_ex:
                break
        return "\\n\\n".join(parts), got, notes

    # PASS 1 -- filename match, no content requirement (fast path)
    p1 = sorted([n for n in others if EX_PAT.search(n)])[:max_ex]
    txt, got, notes = _try(p1, need_figures=False)
    if txt and has_figures(txt):
        return txt, got

    # PASS 2 -- content scan. Naming failed us; test what is actually inside.
    rest = [n for n in others if n not in p1][:max_scan]
    txt2, got2, notes2 = _try(rest, need_figures=True)
    if txt2:
        return txt2, got2

    if args.verbose_exhibits:
        print(f"      {ticker} {accn}: no release found among "
              f"{len(others)} document(s): {', '.join(others[:10])}"
              + (" ..." if len(others) > 10 else ""))
        if notes + notes2:
            print(f"        notes: {'; '.join((notes + notes2)[:6])}")
    return "", []''',
    "fetch_sources.fetch_exhibits -- content-scan fallback, PDF support, loud diagnostic",
), (
    "src/fetch_sources.py",
    """            ex_txt, ex_names = fetch_exhibits(cik, accn, doc, args)""",
    """            ex_txt, ex_names = fetch_exhibits(cik, accn, doc, args, ticker=t)""",
    "fetch_sources.cmd_edgar -- pass the ticker through for diagnostics",
), (
    "src/fetch_sources.py",
    '''    e.add_argument("--items", default="2.02",''',
    '''    e.add_argument("--verbose-exhibits", action="store_true", default=True,
                   help="print the accession's actual filenames when no "
                        "earnings release is found. ON by default: a silent "
                        "rejection count is how 307 cover pages entered the "
                        "corpus unnoticed.")
    e.add_argument("--items", default="2.02",''',
    "fetch_sources -- add --verbose-exhibits, defaulting ON",
)]


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
    print("""VERIFY ON THE FAILING TICKERS FIRST -- do not re-fetch everything yet:

  pip install pypdf          # TSLA files exhibits as PDF

  python -m src.fetch_sources edgar --tickers NVDA,TSLA,INTC --limit 8

  Expect NVDA to save close to 8 of 8. If it still saves 0, the diagnostic now
  PRINTS the accession's actual filenames -- paste those and the pattern can be
  fixed against reality instead of guessed at again.

  head -c 700 "$(ls -t data_provenance/docs/earnings_8k/*NVDA* | head -1)"

Only once NVDA saves should the full fetch run:

  python -m src.fetch_sources edgar --limit 400
""")
    print("=" * 74)


if __name__ == "__main__":
    main()
