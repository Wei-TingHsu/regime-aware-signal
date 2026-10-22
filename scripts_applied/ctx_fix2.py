"""Fix 2 for src/context.py (16 Oct): referee reads the h=2 baseline scoreboard by name (not the newest by mtime), uses its own keys and verdict,
adds the market's own breakdown; chain-forward line shows 0 before the file exists. Run from the repo root: python ctx_fix2.py"""
from pathlib import Path
p = Path("src/context.py"); s = p.read_text()

old = s[s.index("def referee():"):s.index("def forward_counts():")]
new = '''BASELINE = "48a6c4e879a1_n2617_h2"


def referee(asset=None):
    """The current baseline scoreboard (PROJECT_MASTER: h=2 primary). Falls back to the newest file only if the baseline is absent."""
    fs = [p for p in PROC.glob("report_scoreboard_backfill_*.json") if BASELINE in p.name] or \\
         sorted(PROC.glob("report_scoreboard_backfill_*.json"), key=lambda p: p.stat().st_mtime)[-1:]
    if not fs: return None
    j = _j(fs[0]) or {}; h = j.get("primary_h", 2); cell = ((j.get("cells") or {}).get(f"h{h}_primary") or {}); no = cell.get("nonoverlap") or {}
    mine = ((j.get("breakdowns") or {}).get("asset") or {}).get(asset) if asset else None
    return dict(hit=no.get("hit"), q95=cell.get("null_hit_q95"), asym=no.get("asym"), n=no.get("n"), h=h, days=j.get("n_reports"),
                verdict=cell.get("verdict") or j.get("verdict"), pass_hit=cell.get("pass_hit"), pass_asym=cell.get("pass_asym"), mine=mine, tag=j.get("backfill_tag"))


'''
s = s.replace(old, new, 1)

old = s[s.index("    rf = referee()"):s.index("    if s2: P.append(")]
new = '''    rf = referee(asset if asset in MODEL else None)
    if rf and all(isinstance(rf.get(k), (int, float)) for k in ("hit", "q95", "asym", "n")):
        bar = "clears" if rf["pass_hit"] else "does not clear"
        s2.append(f"The engine's own {rf['h']}-session direction calls, all five markets, {rf['days']:,} report days: hit-rate {rf['hit']:.1%}, which {bar} the "
                  f"chance bar of {rf['q95']:.1%} (what shuffled history produces 95% of the time); asymmetry {rf['asym']:.2f} (a right call's gain against a "
                  f"wrong call's loss; 1.0 = even; the test needs 1.20), {rf['n']} non-overlapping calls; scoreboard verdict {rf['verdict']} "
                  f"{tag('tested: ' + str(rf['verdict']))}.")
        m = rf.get("mine")
        if m and isinstance(m.get("hit"), (int, float)):
            s2.append(f"For {name} alone: {m['n']} calls, hit-rate {m['hit']:.0%}, asymmetry {m['asym']:.2f} — a breakdown, not a tested cell "
                      f"(the criterion was set for the pooled calls) {tag('measured')}.")
'''
s = s.replace(old, new, 1)

old = '''    if "chain" in fc: s4.append(f"Chain alarm → gold: {fc['chain'][0]} firing(s) logged forward since 13 Oct 2026, {fc['chain'][1]} matured; the rule needs ten {tag('running')}.")'''
new = '''    ch = fc.get("chain", (0, 0))
    s4.append(f"Chain alarm → gold: {ch[0]} firing(s) logged forward since 16 Oct 2026, {ch[1]} matured (a firing matures when 60 sessions of gold prices exist after it); "
              f"with the five historical cases the rule needs five more before it can be tested {tag('running')}.")'''
assert old in s, "chain anchor"; s = s.replace(old, new, 1)
p.write_text(s); print("  context.py: referee -> baseline h2 + per-market breakdown; chain line always shown")
print("done -- python -m src.context selftest ; python -m src.context show GLD | head -30")
