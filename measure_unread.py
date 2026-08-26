"""
measure_unread.py -- what will the rest of the corpus read ACTUALLY cost?

WHY THIS EXISTS
    corpus_status.py prices unread documents with a per-source AVERAGE token
    count. That average has now been wrong once already (earnings_8k, priced at
    the corpus mean when the unread remainder was entirely over-cap documents),
    and the run has just exhausted a topped-up balance far faster than the
    corrected estimate predicted. An average that has been wrong once should
    not be trusted to price the retry.

    So this counts. No averages, no assumptions about which documents are left:
    it finds every unread file, reads its actual length, applies the truncation
    cap the reader will apply, and calibrates tokens-per-word against the
    OBSERVED token counts already recorded in corpus_status.TOK rather than
    guessing a ratio.

Run from the repo root:
    python measure_unread.py
"""
from pathlib import Path
import statistics

DOCS = Path("data_provenance/docs")
READS = Path("data_provenance/doc_reads")
PROMPT_VERSION = "v1-2026-08-23"
MAX_WORDS = 20000          # doc_read.py --max-words default
SYSTEM_OVERHEAD = 400      # system prompt + schema, per call, approximate
OUT_TOK = 290              # observed output tokens per document
IN_RATE, OUT_RATE = 2.0, 10.0   # $/M as assumed by corpus_status

# Observed input tokens per document, from the read logs (corpus_status.TOK).
OBSERVED = {"fomc_statement": 1400, "fomc_minutes": 22097, "earnings_8k": 8421,
            "political_order": 3551, "political_other": 2037}

SOURCES = ["fomc_statement", "fomc_minutes", "earnings_8k",
           "political_order", "political_other"]


def words_of(p):
    try:
        return len(p.read_text(errors="ignore").split())
    except OSError:
        return 0


def main():
    read_words, unread_words = {}, {}
    for s in SOURCES:
        d = DOCS / s
        if not d.exists():
            continue
        rw, uw = [], []
        for p in sorted(d.glob("*.txt")):
            cache = READS / f"{s}__{p.stem}__{PROMPT_VERSION}.json"
            (rw if cache.exists() else uw).append(min(words_of(p), MAX_WORDS))
        read_words[s], unread_words[s] = rw, uw

    # --- calibrate tokens per word, per source, from documents ALREADY READ ---
    # OBSERVED[s] is the mean input tokens actually billed for that source. The
    # mean post-truncation word count of the same documents is measurable here.
    # Their ratio is this corpus's real tokens-per-word, including the system
    # prompt -- not a textbook 1.3 that was never checked against these files.
    print("=" * 74)
    print("TOKENS PER WORD -- calibrated from documents already read")
    print("=" * 74)
    print(f"  {'source':18} {'n read':>7} {'mean words':>11} "
          f"{'obs tokens':>11} {'tok/word':>9}")
    ratios = []
    for s in SOURCES:
        rw = read_words.get(s, [])
        if not rw or s not in OBSERVED:
            continue
        mw = statistics.mean(rw)
        r = (OBSERVED[s] - SYSTEM_OVERHEAD) / mw if mw else float("nan")
        ratios.append(r)
        print(f"  {s:18} {len(rw):7d} {mw:11.0f} {OBSERVED[s]:11d} {r:9.2f}")
    ratio = statistics.median(ratios) if ratios else 1.35
    print(f"\n  median tokens/word across sources: {ratio:.2f}")
    print("  (a ratio far from ~1.3-1.6 means OBSERVED is itself unreliable --")
    print("   say so rather than pricing the retry with it)")

    # --- price the unread, from their real lengths -------------------------
    print("\n" + "=" * 74)
    print("UNREAD DOCUMENTS -- counted and measured, not averaged")
    print("=" * 74)
    print(f"  {'source':18} {'unread':>7} {'mean w':>8} {'med w':>8} "
          f"{'max w':>8} {'at cap':>7} {'$ in':>8}")
    total_in = total_out = 0.0
    total_unread = 0
    for s in SOURCES:
        uw = unread_words.get(s, [])
        if not uw:
            continue
        toks = [w * ratio + SYSTEM_OVERHEAD for w in uw]
        cin = sum(toks) / 1e6 * IN_RATE
        cout = len(uw) * OUT_TOK / 1e6 * OUT_RATE
        at_cap = sum(1 for w in uw if w >= MAX_WORDS)
        total_in += cin
        total_out += cout
        total_unread += len(uw)
        print(f"  {s:18} {len(uw):7d} {statistics.mean(uw):8.0f} "
              f"{statistics.median(uw):8.0f} {max(uw):8d} {at_cap:7d} "
              f"{cin:8.2f}")

    print(f"\n  unread total: {total_unread}")
    print(f"  input  ${total_in:6.2f}")
    print(f"  output ${total_out:6.2f}")
    print(f"  TOTAL  ${total_in + total_out:6.2f}   "
          f"(corpus_status currently says ~$15.94)")
    print("=" * 74)
    print("\n  If this differs materially from corpus_status, corpus_status is")
    print("  the one to fix -- it prices by source average, and an average is")
    print("  wrong whenever the unread remainder is not a random sample of the")
    print("  source. That has now happened once already (earnings_8k).")
    print("\n  NOTE: rates are corpus_status's assumed $2/M in, $10/M out. If")
    print("  the console shows a different actual spend for this session, the")
    print("  RATES are wrong, not the token counts -- check the model's real")
    print("  pricing before re-launching.")


if __name__ == "__main__":
    main()
