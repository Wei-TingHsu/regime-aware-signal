"""Fix 1 for src/context.py (16 Oct): print sentence tolerates a missing surprise; referee sentence skipped unless every number is present.
Also prints the scoreboard json's structure so the referee loader can be pointed at the right keys. Run from the repo root: python ctx_fix1.py"""
from pathlib import Path
import json, glob
p = Path("src/context.py"); s = p.read_text()
old = '''        s1.append(f"Today's scheduled release <b>{r['event_type'].split(':')[1]}</b>: {h.get('value')} ({h.get('unit')}), "
                  f"{'above' if (su or 0) > 0 else 'below'} the last print by {abs(su):.1f} {tag('measured')}.")'''
new = '''        surprise = (f", {'above' if su > 0 else 'below'} the last print by {abs(su):.1f}" if isinstance(su, (int, float)) else "")
        s1.append(f"Today's scheduled release <b>{r['event_type'].split(':')[1]}</b>: {h.get('value')} ({h.get('unit')}){surprise} {tag('measured')}.")'''
assert old in s, "print anchor"; s = s.replace(old, new, 1)
old = "    if rf and rf.get(\"hit\") is not None:"
new = "    if rf and all(isinstance(rf.get(k), (int, float)) for k in (\"hit\", \"q95\", \"asym\", \"n\")):"
assert old in s, "referee anchor"; s = s.replace(old, new, 1)
p.write_text(s); print("  context.py: print + referee guards in")

bf = sorted(glob.glob("processed/report_scoreboard_backfill_*.json"))
if bf:
    j = json.load(open(bf[-1])); print(f"\n  scoreboard {bf[-1]} top-level keys: {list(j)[:20]}")
    def walk(o, d=0, pre=""):
        if d > 3: return
        if isinstance(o, dict):
            for k, v in list(o.items())[:12]:
                print(f"  {'  '*d}{pre}{k}: {type(v).__name__}{'' if isinstance(v,(dict,list)) else ' = '+str(v)[:40]}"); walk(v, d + 1)
    walk(j)
