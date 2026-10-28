"""Route the Federal Register backlog into the two folders the report reads, and price the read before it is run.

docs/prereg_political_backfill.md (registered 2026-10-28, before this ran). The 26 Aug re-fetch put every presidential
document since 2011 into data_provenance/docs/political/ -- including the 1,697 the corpus had already read from the typed
folders -- and the report reads only political_order/ (executive orders, presidential orders, determinations) and
political_other/ (proclamations, notices, memoranda). Nothing in political/ has ever reached a report or the backfill.

  python -m src.political_route            # dry run: what would be copied, by type and year, and what the read would cost
  python -m src.political_route --apply    # copy the text files (never move, never delete; existing files are never touched)
  python -m src.political_route --cap 40   # exit 2 if the measured estimate exceeds the cap (the runner's guard)

Type comes from the filename the fetcher wrote: YYYYMMDD_<type><number>.txt. Reads are NOT copied from the nightly
`political` profile's cache: that profile carries a different role text, so its 47 reads would be a different read
condition under the same prompt version. Those documents are re-read under the typed profiles (about US$0.25).
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

DOCS = Path("data_provenance/docs")
SRC = DOCS / "political"
ORDER, OTHER = DOCS / "political_order", DOCS / "political_other"
TO_ORDER = {"exec", "pres", "dete"}            # executive order, presidential order, determination  -> political_order
TO_OTHER = {"proc", "noti", "memo"}            # proclamation, notice, memorandum                       -> political_other
IN_RATE, OUT_RATE, OUT_TOK, SYSTEM_TOK = 2.0, 10.0, 290, 400   # as corpus_status / measure_unread assume


def type_of(stem: str) -> str:
    m = re.match(r"\d{8}_([a-z]+)", stem)
    return m.group(1) if m else "?"


def ratio() -> float:
    """Tokens per word, calibrated as measure_unread does: observed tokens per document over observed words."""
    try:
        from src.corpus_status import MEASURED_TOKENS_PER_DOC as T
        rs = []
        for s in ("political_order", "political_other"):
            files = sorted((DOCS / s).glob("*.txt"))[:300]
            if files and s in T:
                mw = sum(len(f.read_text(errors="ignore").split()) for f in files) / len(files)
                if mw > 0:
                    rs.append(T[s] / mw)
        if rs:
            r = sum(rs) / len(rs)
            if 0.8 < r < 4:
                return r
    except Exception:
        pass
    return 1.5


def plan() -> tuple[list[tuple[Path, Path]], Counter, Counter, list[str]]:
    have = {p.name for p in ORDER.glob("*.txt")} | {p.name for p in OTHER.glob("*.txt")}
    moves, by_type, by_year, odd = [], Counter(), Counter(), []
    for p in sorted(SRC.glob("*.txt")):
        if p.name in have:
            continue
        t = type_of(p.stem)
        if t in TO_ORDER:
            dst = ORDER / p.name
        elif t in TO_OTHER:
            dst = OTHER / p.name
        else:
            dst = OTHER / p.name; odd.append(p.name)
        moves.append((p, dst)); by_type[t] += 1; by_year[p.name[:4]] += 1
    return moves, by_type, by_year, odd


def estimate(moves) -> tuple[float, int]:
    r = ratio()
    words = sum(len(p.read_text(errors="ignore").split()) for p, _ in moves)
    tin = words * r + SYSTEM_TOK * len(moves)
    usd = tin / 1e6 * IN_RATE + len(moves) * OUT_TOK / 1e6 * OUT_RATE
    return usd, words


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--cap", type=float, help="US$; exit 2 if the measured estimate is above it")
    a = ap.parse_args()
    moves, by_type, by_year, odd = plan()
    print(f"backlog in {SRC}: {len(list(SRC.glob('*.txt')))} files; already in the typed folders: skipped; to copy: {len(moves)}")
    print("  by type: " + ", ".join(f"{k} {v}" for k, v in sorted(by_type.items(), key=lambda kv: -kv[1])))
    print("  by year: " + ", ".join(f"{k} {v}" for k, v in sorted(by_year.items())))
    if odd:
        print(f"  {len(odd)} file(s) with an unrecognised type code go to political_other and are listed: {', '.join(odd[:8])}{' ...' if len(odd) > 8 else ''}")
    usd, words = estimate(moves)
    print(f"  measured: {words:,} words in the files themselves, tokens/word {ratio():.2f} calibrated -> about US${usd:.2f} "
          f"to read at {IN_RATE}/{OUT_RATE} $/M (output {OUT_TOK} tok/doc). Counted on disk, not a corpus average.")
    if a.cap is not None and usd > a.cap:
        print(f"  ABOVE THE CAP of US${a.cap:.0f}: nothing copied, nothing read. Raise CAP_USD deliberately or read a subset.")
        sys.exit(2)
    if not a.apply:
        print("  dry run -- nothing copied (add --apply)")
        return
    n = 0
    for p, dst in moves:
        if not dst.exists():
            shutil.copy2(p, dst); n += 1
    print(f"  copied {n} file(s) into political_order/ and political_other/; political/ untouched")


if __name__ == "__main__":
    main()
