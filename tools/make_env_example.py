"""Regenerate .env.example from the variable NAMES the code reads. Values are never written.
Run after adding any new environment variable:  python tools/make_env_example.py
"""
import re, glob
from pathlib import Path
pat = re.compile(r'(?:environ(?:\.get)?\(?\[?|getenv\()\s*["\']([A-Z][A-Z0-9_]+)["\']')
names = set()
for f in glob.glob("*.py") + glob.glob("src/*.py") + glob.glob("tools/*.py") + glob.glob("*.sh"):
    names |= set(pat.findall(Path(f).read_text(errors="ignore")))
for f in glob.glob("*.sh"):
    names |= set(re.findall(r'export\s+([A-Z][A-Z0-9_]+)=', Path(f).read_text(errors="ignore")))
names -= {"HOME", "PATH", "USER", "PWD", "SHELL", "TERM", "LANG"}
where = {"ANTHROPIC_API_KEY": "console.anthropic.com -> API keys (document reader)",
         "FRED_API_KEY": "fred.stlouisfed.org -> My Account -> API Keys (macro panel)",
         "SEC_CONTACT": "not a secret -- the contact email EDGAR requires in the User-Agent header, e.g. Name your@email",
         "GOOGLE_APPLICATION_CREDENTIALS": "console.cloud.google.com -> service-account JSON path (BigQuery/GDELT)"}
out = ["# .env.example -- variable NAMES only. Copy to .env and fill in on a new machine.",
       "# .env is git-ignored and is never committed. See docs/TRACK.md section 7.",
       "# Regenerate: python tools/make_env_example.py", ""]
for n in sorted(names):
    out += [f"# {where.get(n, 'issued by the provider named in the code that reads it')}",
            f"{n}=enter_your_key_here", ""]
Path(".env.example").write_text("\n".join(out))
print("variables found:", sorted(names) or "NONE")
