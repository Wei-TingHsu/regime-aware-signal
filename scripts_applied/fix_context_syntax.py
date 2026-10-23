"""Hotfix: an apostrophe inside an f-string expression in src/context.py (Python 3.11 forbids backslashes there). Run from the repo root: python scripts_applied/fix_context_syntax.py"""
from pathlib import Path
import ast
c = Path("src/context.py"); s = c.read_text()
bad = "{ep.get('rule', 'a counter-move of 1.5 × the asset\\'s monthly volatility, floor 8%')}"
if bad in s: s = s.replace(bad, "{ep.get('rule', 'a counter-move of 1.5 × its own monthly volatility, floor 8%')}", 1); c.write_text(s); print("  context.py: apostrophe removed from the f-string expression")
else: print("  pattern not found -- showing line 212:"); print(s.splitlines()[211])
ast.parse(c.read_text()); print("  context.py parses")
for f in ("app.py", "src/why_moved.py", "src/factor_attribution.py", "src/residual_momentum.py", "src/issuer_pool.py"):
    ast.parse(Path(f).read_text()); print(f"  {f} parses")
