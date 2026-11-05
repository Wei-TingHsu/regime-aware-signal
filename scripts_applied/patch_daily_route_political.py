"""patch_daily_route_political.py (v2) -- the nightly job: route new Federal Register documents into the folders the report reads,
and stop reading them under the retired `political` profile.

FOUND 28 Oct 2026: the nightly fetch writes presidential documents to data_provenance/docs/political/, step 4 reads them under
the `political` profile (a different role text from the typed profiles), and step 6 reads only read_political_order.csv and
read_political_other.csv. Since 27 Aug every new document was read (47, cents) and none reached a report; the 47 orphan reads
broke the gate's CSV-vs-cache check on 28 Oct. After the backlog routing, new arrivals would go on doing the same.

v1 looked for a standalone `doc_read --source political` line; the nightly reads its sources in a loop:
    for SRC in fomc_statement fomc_minutes earnings_8k political_order political_other political; do
so v2 removes the word `political` from that list (the typed sources stay) and inserts the routing call before step 4.
Anchors verified (exactly one match each) or nothing changes. Dry run by default:
    python scripts_applied/patch_daily_route_political.py
    python scripts_applied/patch_daily_route_political.py --write
Backup: daily_run.sh.bak_20261028. Protocol of wrong prior #19: verify, apply, check (zsh -n), revert on failure.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

P = Path("daily_run.sh")
STEP4 = re.compile(r'^step\s+"4/7.*$', re.M)
LOOP = re.compile(r'^(\s*for SRC in [^\n;]*?\bpolitical_other)\s+political(\s*;\s*do\s*)$', re.M)
STANDALONE = re.compile(r'^(\s*python -m src\.doc_read\b[^\n]*--source political(?!_)[^\n]*)$', re.M)
INSERT = ('# 28 Oct: new Federal Register documents are routed into the typed folders the report reads (TRACK 3.1 / prereg_political_backfill);\n'
          '# the `political` profile is retired from the read loop below -- it fed no report and its orphan reads broke the gate on 28 Oct.\n'
          'python -m src.political_route --apply || echo "  political routing failed -- continuing"\n')


def main():
    s = P.read_text()
    a = STEP4.findall(s); b = LOOP.findall(s); c = STANDALONE.findall(s)
    print(f"anchor 1 (step 4/7 line): {len(a)} match(es): {a[:2]}")
    print(f"anchor 2a (for-loop list ending in 'political_other political; do'): {len(b)} match(es)")
    print(f"anchor 2b (standalone doc_read --source political line): {len(c)} match(es)")
    if len(a) != 1 or (len(b) + len(c)) != 1:
        print("the step-4 block as it stands:"); m = re.search(r'^step\s+"4/7.*?(?=^step\s+"5/7)', s, re.M | re.S); print(m.group(0) if m else "(not found)")
        sys.exit("anchors not unique -- nothing changed; adjust the patterns to the block printed above")
    if "--write" not in sys.argv:
        print("dry run: anchors verified; add --write to apply"); return
    bak = P.with_name("daily_run.sh.bak_20261028"); shutil.copy2(P, bak)
    m = STEP4.search(s); s2 = s[:m.start()] + INSERT + s[m.start():]
    if b:
        s2 = LOOP.sub(lambda mm: mm.group(1) + mm.group(2), s2, count=1)
    else:
        s2 = STANDALONE.sub(lambda mm: "# 28 Oct retired (fed no report; orphan reads broke the gate): " + mm.group(1).strip(), s2, count=1)
    P.write_text(s2)
    r = subprocess.run(["zsh", "-n", str(P)], capture_output=True, text=True)
    if r.returncode != 0:
        shutil.copy2(bak, P); sys.exit(f"zsh -n FAILED, reverted: {r.stderr}")
    print(f"applied; {P} parses (zsh -n); backup at {bak.name}. Check tomorrow's log for 'political routing' before step 4 and no 'political:' read line.")


if __name__ == "__main__":
    main()
