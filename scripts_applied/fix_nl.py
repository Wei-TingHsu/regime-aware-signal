"""Repair src/history_tables.py line ~174: literal newlines written where '\\n' escapes belong. Run from the repo root: python fix_nl.py"""
from pathlib import Path
p = Path("src/history_tables.py"); s = p.read_text(); NL = chr(10)
broken = f'(DOCS / f"history_{{tid}}.md").write_text("{NL}".join(L) + "{NL}"); print("{NL}".join(L)); print(f"-> docs/history_{{tid}}.md{NL}")'
good = '(DOCS / f"history_{tid}.md").write_text("\\n".join(L) + "\\n"); print("\\n".join(L)); print(f"-> docs/history_{tid}.md\\n")'
if broken in s: p.write_text(s.replace(broken, good, 1)); print("  fixed")
elif good in s: print("  already fine")
else: print("  pattern not found -- paste: sed -n 170,178p src/history_tables.py")
import py_compile; py_compile.compile("src/history_tables.py", doraise=True); print("  compiles")
