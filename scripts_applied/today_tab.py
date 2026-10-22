"""19 Oct: Today tab — track-record banner (replaces bare hit-rate/asymmetry tiles), "Documents with a direction" clickable tile + view,
referee helper on the baseline scoreboard; record the amended-rule H-table run. Run from the repo root:  python today_tab.py ; streamlit run app.py"""
from pathlib import Path
import sys

a = Path("app.py"); s = a.read_text()

# ---- A. referee_numbers on the baseline file, with days / pass flags
old = s[s.index("def referee_numbers():"):s.index("from src.context import context_block, CSS as CTX_CSS")]
new = '''def referee_numbers():
    """Hit-rate, chance bar, asymmetry, horizon, verdict — from the BASELINE backfill scoreboard (PROJECT_MASTER: h=2 primary),
    the same file the Context block reads. Fixed until the engine's method changes and the backfill is re-run."""
    BASE = "48a6c4e879a1_n2617_h2"
    bf = [p for p in PROC.glob("report_scoreboard_backfill_*.json") if BASE in p.name] or \\
         sorted(PROC.glob("report_scoreboard_backfill_*.json"), key=lambda p: p.stat().st_mtime)[-1:]
    if not bf: return None
    j = jload(bf[0]) or {}
    h = j.get("primary_h", 2)
    cell = ((j.get("cells") or {}).get(f"h{h}_primary") or {})
    no = cell.get("nonoverlap") or {}
    return dict(hit=no.get("hit"), q95=cell.get("null_hit_q95") or cell.get("null_q95"), asym=no.get("asym"), n=no.get("n"), h=h,
                days=j.get("n_reports"), pass_hit=cell.get("pass_hit"), pass_asym=cell.get("pass_asym"),
                verdict=cell.get("verdict") or j.get("verdict", "—"), date=pd.Timestamp(bf[0].stat().st_mtime, unit="s").strftime("%d %b %Y"))


'''
if "BASE = \"48a6c4e879a1_n2617_h2\"" in s: print("  referee_numbers: already")
else: s = s.replace(old, new, 1); print("  referee_numbers: baseline file")

# ---- B. documents view (defined after doc_cards)
if "def documents_view(" in s: print("  documents_view: already")
else:
    anchor = "\n\n# ==========================================================================\n# HEADER + TABS\n"
    if anchor not in s: sys.exit("  header anchor not found")
    func = '''

def documents_view(R: dict, day: str):
    """?focus=docs — every document that landed for the day, then how each market's direction was built from them."""
    st.markdown('<a class="rs-back rs-link" href="?" target="_self">← Back to overview</a>', unsafe_allow_html=True)
    docs = R.get("documents", [])
    n_dir = sum(1 for d in docs if any(v is not None and abs(v) > 0.05 for v in (d.get("direction") or {}).values()))
    st.markdown(f'<div class="g rs-banner"><h2>Documents with a direction · {day}</h2>'
                f'<p>{len(docs)} document(s) landed from the five sources we read; {n_dir} carried a usable direction for at least one market. '
                'Each document is read once by the same reader with the same prompt and scored per market from −1 (pushes it down) to +1 (pushes it up), '
                'with how specific, how new and how confident the text is. A market gets a direction only when its documents clear the direction floor '
                'and enough past situations in the same condition with the same kind of document exist to compare against (at least 8 comparable).</p></div>',
                unsafe_allow_html=True)
    st.markdown('<div class="rs-section">What landed</div>', unsafe_allow_html=True)
    doc_cards(docs)
    st.markdown('<div class="rs-section">How each market\\'s direction was built</div>', unsafe_allow_html=True)
    rows = []
    for a_, e in R["assets"].items():
        name = DISPLAY[a_]["name"]
        if e.get("abstain") or not e.get("estimate"):
            rows.append(f"<p class=\\"rs-ctx-p\\"><b>{name}</b> — abstains: {e.get('abstain_reason') or 'no estimate'}.</p>"); continue
        est = e.get("estimate") or {}; nv = e.get("net_view")
        tone = "up" if (nv or 0) > 0 else "down"
        src = SOURCE.get(e.get("dominant_source"), e.get("dominant_source") or "mixed sources")
        rows.append(f"<p class=\\"rs-ctx-p\\"><b>{name}</b> — read <b>{tone}</b> (net {nv:+.2f}) from {e.get('n_docs_today', 0)} document(s), mostly {src}; "
                    f"matched {est.get('n_matched', '—')} past situations, {est.get('ess', 0):.0f} comparable, history weight {est.get('w_shrink', 0):.2f}; "
                    f"documents and history {str(e.get('agreement', '')).lower() or '—'}"
                    + (" — <span style=\\"color:%s\\">two documents point opposite ways; both shown, neither combined</span>" % WARN if e.get("sources_disagree") else "") + ".</p>")
    st.markdown('<div class="g rs-ctx">' + "".join(rows) +
                '<p class="rs-foot">Direction floor and the 8-comparable rule are fixed in the registration (docs/prereg_report_scoreboard.md); nothing here is tuned to the day.</p></div>',
                unsafe_allow_html=True)
'''
    s = s.replace(anchor, func + anchor, 1); print("  documents_view: added")

# ---- C. dispatch
old = '    if focus_param in R["assets"]:\n        detail_dashboard(focus_param, R, day, reg)\n'
if 'focus_param == "docs"' in s: print("  dispatch: already")
elif old not in s: sys.exit("  dispatch anchor not found")
else: s = s.replace(old, '    if focus_param == "docs":\n        documents_view(R, day)\n    elif focus_param in R["assets"]:\n        detail_dashboard(focus_param, R, day, reg)\n', 1); print("  dispatch: docs view")

# ---- D. tile: Markets with a view -> Documents with a direction (clickable)
old = '''  <div class="g rs-tile"><div class="rs-k">Markets with a view</div><div class="rs-v">{len(views)} <span style="color:{INK3};font-weight:500">of 5</span></div>
    <div class="rs-s">a view needs at least 8 comparable past situations</div></div>
</div>""", unsafe_allow_html=True)'''
new = '''  <a class="rs-link" href="?focus=docs" target="_self"><div class="g rs-tile rs-hover"><div class="rs-k">Documents with a direction</div><div class="rs-v">{n_dir} <span style="color:{INK3};font-weight:500">of {len(R['documents'])}</span></div>
    <div class="rs-s">click to see each document and how every market's direction was built · {len(views)} of 5 markets have a view</div></div></a>
</div>""", unsafe_allow_html=True)'''
if "Documents with a direction</div>" in s: print("  tile: already")
elif old not in s: sys.exit("  tile anchor not found")
else:
    s = s.replace(old, new, 1)
    old2 = '        st.markdown(f"""\n<div class="rs-tiles">\n  <div class="g rs-tile"><div class="rs-k">Market condition</div>'
    if old2 not in s: sys.exit("  tiles start anchor not found")
    s = s.replace(old2, '        n_dir = sum(1 for d in R["documents"] if any(v is not None and abs(v) > 0.05 for v in (d.get("direction") or {}).values()))\n' + old2, 1)
    print("  tile: Documents with a direction (clickable)")

# ---- E. hit-rate / asymmetry tiles -> track-record banner
start = s.find("        rf = referee_numbers()\n        if rf:\n            hit = ")
end = s.find("        st.markdown(regime_strip_html(reg, T, prof), unsafe_allow_html=True)")
if "Track record, in one breath" in s: print("  banner: already")
elif start < 0 or end < 0: sys.exit("  banner anchors not found")
else:
    banner = '''        rf = referee_numbers()
        if rf and all(isinstance(rf.get(k), (int, float)) for k in ("hit", "q95", "n")):
            days = f"{rf['days']:,}" if isinstance(rf.get("days"), int) else "the scored"
            if rf.get("pass_hit"):
                verdict_line = ("<b>The calls cleared the chance bar on how often they were right, but not the test on how much a right call pays "
                                "against a wrong one</b> — scoreboard verdict " + str(rf["verdict"]) + ".")
            else:
                verdict_line = "<b>So far this engine has not shown it beats a coin</b> — scoreboard verdict " + str(rf["verdict"]) + "."
            st.markdown(f'<div class="g rs-banner"><h2>Track record, in one breath</h2>'
                        f'<p>Over <b>{days}</b> scored days the engine\\'s direction calls were right <b>{rf["hit"]:.0%}</b> of the time. '
                        f'Chance alone would have reached up to {rf["q95"]:.0%}. {verdict_line} Read the Up/Down pills as the engine\\'s reading, not as advice.</p>'
                        '<p><b>What you can rely on here:</b> the market condition, the oil-shock alarm and the history tables are counts of what actually '
                        'happened — not predictions — and every sentence in the context blocks carries a tag: <i>measured</i>, <i>tested</i> (with its verdict), '
                        '<i>hypothesis</i>, or <i>running</i>. The full scoreboard, including the size test (asymmetry), is on “The record”.</p></div>',
                        unsafe_allow_html=True)
'''
    s = s[:start] + banner + s[end:]; print("  banner: replaces hit-rate / asymmetry tiles")
a.write_text(s)

# ---- F. record the amended-rule H run
p = Path("docs/prereg_history_tables.md"); t = p.read_text()
if "| 2026-10-19 | H1–H5 under §4 amendment |" in t: print("  prereg §5 amended run: already")
else:
    p.write_text(t.rstrip("\n") + "\n| 2026-10-19 | H1–H5 under §4 amendment | Rerun at 5 and 20 sessions, gap floor 10 pts, p < 0.0083: **no PASS in any of the 72 cells**. "
        "H1 FAIL ×12 (both horizons, split), H4dn FAIL ×12, H5 FAIL ×12, H4up FAIL SPY/TLT/WTI ×2 + INCONCLUSIVE GLD/UUP/USO, H3 INCONCLUSIVE ×24 (21/15 events). "
        "All six event tables close as measured-only; they stay on the app with their tags. | **#54 right** |\n")
    print("  prereg §5 amended run: appended")
tr = Path("docs/TRACK.md"); t = tr.read_text()
old = "(16 Oct report had been written over an all-NaN row).\n"
if "no PASS in 72 cells" in t: print("  TRACK: already")
elif old in t: tr.write_text(t.replace(old, old + "**Amended rerun 19 Oct: no PASS in 72 cells** (#54 right); the six event tables are closed as measured-only. Remaining under 3.25: "
                                    "H2 (after the reader's first month), H6, H7, and the dollar-series data item.\n", 1)); print("  TRACK: amended run noted")
else: print("  TRACK anchor not found -- add by hand")
m = Path("docs/PROJECT_MASTER.md"); t = m.read_text()
old = "| H0 measured; H1, H4, H5 FAIL on every testable cell (#50, #52, #53 right); H3 at 3% gave 6/3 events (#51 wrong), amended to 2% |"
if "no PASS in 72 cells" in t: print("  MASTER: already")
elif old in t: m.write_text(t.replace(old, "| H0 measured; H1, H4, H5 FAIL on every testable cell (#50, #52, #53 right); H3 6/3 → 21/15 events at 2% (#51 wrong), INCONCLUSIVE; "
                                   "horizon amendment (5 s, 10 pts, p < 0.05/6): no PASS in 72 cells (#54 right). Event tables closed as measured-only |", 1)); print("  MASTER row 45: final")
else: print("  MASTER row 45 anchor not found -- add by hand")
c = Path("docs/CURRENT_STATE_2026-08-23.md"); t = c.read_text()
old = "Not lowered again.\n"
if "72 cells" in t: print("  CURRENT_STATE: already")
elif old in t: c.write_text(t.replace(old, old + "Founder's horizon amendment (5 sessions beside 20, 10-point floor, per-table Bonferroni) run the same afternoon: no PASS in 72 cells; "
                                   "prior #54 right. The Today tab was rewritten the same day: a plain-words track-record banner replaces the bare hit-rate/asymmetry tiles, "
                                   "and \"Documents with a direction\" is a clickable count opening each document and how every market's direction was built.\n", 1)); print("  CURRENT_STATE: noted")
else: print("  CURRENT_STATE anchor not found -- add by hand")
print("done -- streamlit run app.py")
