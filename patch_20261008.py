"""One-shot patch, 8 Oct 2026. Run from the repo root with the venv active. Idempotent."""
from pathlib import Path
import re

def after(path, anchor, text, label):
    p = Path(path); s = p.read_text()
    if text.strip()[:60] in s: print(f"  {label}: already present"); return
    k = s.find(anchor)
    if k < 0: print(f"  {label}: ANCHOR NOT FOUND"); return
    eol = s.index("\n", k) + 1; p.write_text(s[:eol] + text + s[eol:]); print(f"  {label}: written")

# ---- 1. drawdown claim registered as an amendment to T1 (declared contaminated prior)
after("docs/prereg_exposure_dial.md", "| 2026-10-08 | Test A run.",
      "| 2026-10-08 | **Drawdown claim registered for Test B and, retrospectively labelled, for Test A.** Claim: the vol-targeted dial (variant 2) reduces maximum drawdown versus buy-and-hold by ≥ 30% on ≥ 4 of 5 core assets, net at 1×. Null: 10,000 stationary-bootstrap resamples of the paired daily returns, 95% interval on the drawdown ratio. **Prior is contaminated**: it is stated after Test A measured exactly this (SPY −0.83→−0.29, TLT −0.80→−0.57, GLD −0.61→−0.48, UUP −0.26→−0.25, USO −4.08→−1.01). Test A's figures may be cited by T15 as *measured*; the claim becomes *tested* only on Test B's 30-ETF universe, where no figure has been seen | Founder's request; makes the T15 block's figures citable with their status stated |\n",
      "prereg_exposure_dial: drawdown claim")

# ---- 2. oil instrument amendment to the universe
p = Path("docs/prereg_instrument_robustness.md"); s = p.read_text()
row = ("| 2026-10-08 | **Oil column amendment.** `WTI_CONT` (continuous back-adjusted front-month WTI, built from CL=F with the roll on the expiry-day ratio) added to `processed/asset_returns.parquet` beside USO. USO is the one model instrument that is a real compromise (monthly roll drag; part of its −98% in 2020). Every oil result — Problem 1 cross-asset, the referee's USO cell, T1's USO PASS, T13 A2's chain alert — is re-run on both columns and reported side by side; USO stays as the tradeable comparison. The other four pairs were shown consistent on 29 Sep and are not touched | Two-wars review (TRACK §3.14) |\n")
if "WTI_CONT" not in s:
    k = s.find("| — | — | — |")
    s = s.replace("| — | — | — |\n", row, 1) if k >= 0 else s + "\n" + row
    p.write_text(s); print("  prereg_instrument_robustness: oil amendment written")
else:
    print("  prereg_instrument_robustness: already present")

# ---- 3. SOFR futures into the intraday collector
p = Path("src/collect_intraday.py"); s = p.read_text()
old = '           "ZQ=F"]                                                # fed funds front month (phase B surprise)'
new = ('           "ZQ=F",                                                # fed funds front month (phase B surprise)\n'
       '           "SR3=F"]                                               # 3-month SOFR front quarterly -- the contract the Fed\'s surprise series uses since 2023')
if "SR3=F" not in s and old in s:
    p.write_text(s.replace(old, new)); print("  collect_intraday: SOFR futures added")
else:
    print("  collect_intraday: SOFR already present or anchor differs")

# ---- 4. nightly job: blindspot after the report step
p = Path("daily_run.sh"); s = p.read_text()
if "src.blindspot" not in s:
    anchor = "python -m src.report_scoreboard"
    k = s.find(anchor)
    if k >= 0:
        eol = s.index("\n", k) + 1
        s = s[:eol] + "# T13 case A: per-market coverage state and the oil-shock chain alert for the last completed session\npython -m src.blindspot --today || echo \"  blindspot failed -- continuing\"\n" + s[eol:]
        p.write_text(s); print("  daily_run: blindspot step added after the scoreboard")
    else:
        print("  daily_run: scoreboard anchor not found -- add `python -m src.blindspot --today` by hand after step 6c")
else:
    print("  daily_run: blindspot already present")

# ---- 5. app: coverage line + chain alert, reading outputs/blindspot/<day>.json
p = Path("app.py"); s = p.read_text()
if "load_blindspot" not in s:
    s = s.replace('AXIS_OF = {"SPY": "equity"', '''@st.cache_data(show_spinner=False)
def load_blindspot(day: str):
    p = ROOT / "outputs" / "blindspot" / f"{day.replace('-', '')}.json"
    try:
        return json.loads(p.read_text()) if p.exists() else None
    except Exception:
        return None


def coverage_line(a: str, bs) -> str:
    """T13 case A line, per docs/prereg_blindspot.md section 5. Absent on quiet days."""
    if not bs:
        return ""
    st_ = (bs.get("states") or {}).get(a); z = (bs.get("z") or {}).get(a)
    hc = (bs.get("haircut") or {}).get(a, 1.0)
    bits = []
    if st_:
        word = {"A": "the engine's sources carry no document on it (blind)",
                "B": "the engine read it backwards (wrong)",
                "C": "the engine's sources account for it"}[st_]
        bits.append(f"Coverage: this market moved {abs(z):.1f}σ today; {word}.")
    if a == "GLD" and bs.get("chain_alert"):
        ci = bs.get("chain_inputs") or {}
        bits.append(f"<b>Oil-shock chain:</b> oil {ci.get('oil_z', 0):+.1f}σ, 2-year {ci.get('dgs2_5d_bp', 0):+.0f} bp, dollar "
                    f"{ci.get('dxy_5d', 0):+.1%} over five sessions. On the two named precedents (Mar 2022, Mar 2026) gold fell over the "
                    "following months. No direction is issued from this flag.")
    if hc < 0.999:
        bits.append(f"Displayed confidence carries a haircut of {hc:.2f} from recent misreads.")
    return f'<div class="rs-ev">{" ".join(bits)}</div>' if bits else ""


AXIS_OF = {"SPY": "equity"''', 1)
    s = s.replace('        cards = "".join(market_card(a, e, quote(DISPLAY[a]), f"?focus={a}", event_line(a, R, day, fomc_days))\n                        for a, e in R["assets"].items())',
                  '        bs = load_blindspot(day)\n        cards = "".join(market_card(a, e, quote(DISPLAY[a]), f"?focus={a}", event_line(a, R, day, fomc_days) + coverage_line(a, bs))\n                        for a, e in R["assets"].items())', 1)
    p.write_text(s); print("  app.py: coverage line and chain alert added")
else:
    print("  app.py: already patched")

# ---- 6. TRACK: SOFR note under 3.9, and the wrong-prior table in human terms as 18.15 pointer
p = Path("docs/TRACK.md"); s = p.read_text()
if "SR3=F" not in s:
    s = s.replace("| S5 | **collect 1-minute bars on every scheduled event day from now on**",
                  "| S5 | **collect 1-minute bars on every scheduled event day from now on** — incl. ZQ=F and, from 8 Oct, SR3=F (3-month SOFR, the contract the Fed's surprise series uses since 2023), so the engine builds its own surprise measure for every meeting after Dec 2023", 1)
    p.write_text(s); print("  TRACK: SOFR note")
print("patch complete")
