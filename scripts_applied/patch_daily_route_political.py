"""patch_daily_route_political.py -- the nightly job: route new Federal Register documents into the folders the report reads,
and stop reading them under the retired `political` profile.

FOUND 28 Oct 2026: the nightly fetch writes presidential documents to data_provenance/docs/political/, step 4 reads them under
the `political` profile (a different role text from the typed profiles), and step 6 reads only read_political_order.csv and
read_political_other.csv. So since 27 Aug every new document was read (47 of them, cents) and none reached a report, and the
47 orphan reads broke the gate's CSV-vs-cache coverage check on 28 Oct. After the backlog routing, new arrivals would go on
doing the same from tonight.

The patch (anchors verified, exactly one match each, else nothing changes):
  1. before the line that starts step 4, insert:   python -m src.political_route --apply || echo "..."
     (copies new political/ files into political_order/ and political_other/ by type; existing files never touched)
  2. the doc_read line whose source is `political` (not political_order / political_other) is commented out with a dated note.
Dry run by default:
    python scripts_applied/patch_daily_route_political.py
    python scripts_applied/patch_daily_route_political.py --write
Backup: daily_run.sh.bak_20261028. Protocol of wrong prior #19: verify, apply, check, revert on failure.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

P = Path("daily_run.sh")
STEP4 = re.compile(r'^step\s+"4/7.*$', re.M)
POLITICAL_READ = re.compile(r'^(\s*python -m src\.doc_read\b[^\n]*--source political(?!_)[^\n]*)$', re.M)
INSERT = ('# 28 Oct: new Federal Register documents are routed into the typed folders the report reads (TRACK 3.1 / prereg_political_backfill);\n'
          '# the `political` profile read below is retired -- it fed no report and its orphan reads broke the gate on 28 Oct.\n'
          'python -m src.political_route --apply || echo "  political routing failed -- continuing"\n')


def main():
    s = P.read_text()
    a, b = STEP4.findall(s), POLITICAL_READ.findall(s)
    print(f"anchor 1 (step 4/7 line): {len(a)} match(es): {a[:2]}")
    print(f"anchor 2 (doc_read --source political line): {len(b)} match(es): {[x.strip()[:90] for x in b[:2]]}")
    if len(a) != 1 or len(b) != 1:
        sys.exit("anchors not unique -- nothing changed; read daily_run.sh around step 4 and adjust the patterns")
    if "--write" not in sys.argv:
        print("dry run: anchors verified; add --write to apply"); return
    bak = P.with_name("daily_run.sh.bak_20261028"); shutil.copy2(P, bak)
    m = STEP4.search(s)
    s2 = s[:m.start()] + INSERT + s[m.start():]
    s2 = POLITICAL_READ.sub(lambda mm: "# 28 Oct retired (fed no report; orphan reads broke the gate): " + mm.group(1).strip(), s2, count=1)
    P.write_text(s2)
    r = subprocess.run(["zsh", "-n", str(P)], capture_output=True, text=True)
    if r.returncode != 0:
        shutil.copy2(bak, P); sys.exit(f"zsh -n FAILED, reverted: {r.stderr}")
    print(f"applied; {P} parses (zsh -n); backup at {bak.name}. Verify tomorrow's log for 'political routing' before step 4.")


if __name__ == "__main__":
    main()
