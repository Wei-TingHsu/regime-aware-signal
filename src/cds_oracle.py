"""cds_oracle.py -- test CDS-4 (TRACK 3.135): ONE question, on clean data.

The grid of CDS-3 was not more than luck as a whole, but all its strongest cells said the same thing: after a jump in Oracle's CDS spread, Oracle's own share was
weaker the next session. Two doubts: (a) Oracle's share usually falls ON the jump day, and a fall is often followed by another -- the CDS may only mark a bad day;
(b) some 'jumps' were noise of the worked-out spreads. This test removes both:

  - the day's spread uses only trades whose spread is GIVEN in the public file (no worked-out spreads);
  - each jump day is compared with the 10 other days on which Oracle's share moved most nearly the same amount that day WITHOUT a CDS jump.

Question: after a jump of 5% or more in Oracle's CDS, is Oracle's share weaker the next session than after such look-alike days?

    python -m src.cds_oracle test        # the test on the history (free, no download)
    python -m src.cds_oracle forward     # the forward record: every new jump from 27 Nov 2026 on; part of the daily block
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np, pandas as pd

DOCS = Path("docs"); JUMP = np.log(1.05); K = 10; MIN_EVENTS = 15; MINSHIFT = 20; START = pd.Timestamp("2026-11-27"); VERDICT_AT = 20
PX = [Path("data_provenance/selloff_live/prices/ORCL.parquet"), Path("data_provenance/leading/y_ORCL.parquet")]


def _close():
    for f in PX:
        if f.exists():
            d = pd.read_parquet(f); s = d["close"] if "close" in d.columns else d.iloc[:, 0]; s.index = pd.DatetimeIndex(s.index).tz_localize(None) if getattr(s.index, "tz", None) is not None else pd.DatetimeIndex(s.index); return s.dropna()
    raise SystemExit("no Oracle share prices on disk: run the daily check (python -m src.selloff_live daily) first")


def _frame():
    """per session: Oracle's spread of the day from GIVEN spreads only, its change against the last such day (at most 5 sessions back), the share's move that day and the next"""
    from src import cds_public as C
    X = C.trades(); X = X[(X.key == "Oracle") & (X.how == "given")]; sp = X.groupby("day").bp.median(); n = X.groupby("day").size(); px = _close()
    files = sorted(pd.to_datetime([f.stem for f in C.RAW.glob("*.parquet")])); cal = px.index[(px.index >= files[0]) & (px.index <= files[-1])]
    F = pd.DataFrame(index=cal); F["bp"] = sp.reindex(cal); F["trades"] = n.reindex(cal).fillna(0).astype(int); F["prev_bp"] = F.bp.ffill(limit=5).shift(1).where(F.bp.notna()); F["chg"] = np.log(F.bp / F.prev_bp)
    F["same"] = px.pct_change().reindex(cal); F["next"] = (px.shift(-1) / px - 1).reindex(cal); F["jump"] = (F.chg >= JUMP).fillna(False); return F


def _excess(F, ev):
    """for each event day: next-session move minus the average next-session move of the K non-event days whose same-day move is nearest"""
    pool = F[~ev & F.same.notna() & F.next.notna()]; ps = pool.same.to_numpy(); pn = pool.next.to_numpy(); out = []
    for d in F.index[ev & F.same.notna().to_numpy() & F.next.notna().to_numpy()]:
        j = np.argsort(np.abs(ps - F.same[d]))[:K]; out.append((d, F.next[d], pn[j].mean()))
    return pd.DataFrame(out, columns=["day", "next", "alike"]).set_index("day") if out else pd.DataFrame(columns=["next", "alike"])


def cmd_test():
    F = _frame(); ev = F.jump.to_numpy(); E = _excess(F, ev); n = len(E)
    print(f"{len(F)} sessions, {F.index[0]:%Y-%m-%d} to {F.index[-1]:%Y-%m-%d}; days with a GIVEN Oracle spread: {int(F.bp.notna().sum())}; jumps of 5% or more: {int(ev.sum())}, with a next session: {n}")
    if n < MIN_EVENTS:
        verdict = f"TOO FEW to judge (under {MIN_EVENTS} jumps)"; stat = float((E.next - E.alike).mean()) if n else np.nan; p = np.nan; copies = 0
    else:
        stat = float((E.next - E.alike).mean()); sh = range(MINSHIFT, len(F) - MINSHIFT); z = []
        for k in sh:
            e2 = _excess(F, np.roll(ev, k))
            if len(e2) >= MIN_EVENTS // 2: z.append(float((e2.next - e2.alike).mean()))
        z = np.array(z); copies = len(z); p = float((np.sum(np.abs(z) >= abs(stat)) + 1) / (copies + 1)); verdict = "PASSES" if p < 0.05 and stat < 0 else "does not pass"
    raw = float(E.next.mean()) if n else np.nan; alike = float(E.alike.mean()) if n else np.nan; same = float(F.same[E.index].mean()) if n else np.nan; f2 = lambda x: "n/a" if x != x else f"{x * 100:+.2f}%"
    L = ["# Test CDS-4: after a jump in Oracle's CDS, is Oracle's share weaker the next session?", "", f"Registered in TRACK 3.135 before running. One test, limit: chance under 0.05. {len(F)} sessions, {F.index[0]:%Y-%m-%d} to {F.index[-1]:%Y-%m-%d}. "
         f"The day's spread = the middle one of that day's trades whose spread is GIVEN in the public file, done before 16:00 New York ({int(F.bp.notna().sum())} days have one). A jump = 5% or more above the last such day, at most 5 sessions back. "
         f"Each jump day is set against the {K} other days on which Oracle's share moved most nearly the same amount that day without a jump ('look-alike days').", "",
         "| | |", "|---|---|", f"| jumps with a next session | {n} |", f"| Oracle's share ON the jump day, average | {f2(same)} |", f"| Oracle's share the NEXT session, average | {f2(raw)} |", f"| the same after the look-alike days | {f2(alike)} |",
         f"| **difference (jump days minus look-alike days)** | **{f2(stat)}** |", f"| chance (the share of {copies} copies with the jump days slid along the calendar that show a difference at least as large) | {'n/a' if p != p else f'{p:.4f}'} |", f"| **verdict** | **{verdict}** |", "",
         "## Every jump", "", "| day | spread before -> that day, basis points (trades) | share that day | share next session | look-alike days' next session |", "|---|---|---|---|---|"]
    for d, r in E.iterrows(): L.append(f"| {d:%Y-%m-%d} | {F.prev_bp[d]:.0f} -> {F.bp[d]:.0f} ({F.trades[d]}) | {f2(F.same[d])} | {f2(r.next)} | {f2(r.alike)} |")
    L += ["", "What a pass would not mean: the trades are timed when done, not when made public, so it is not yet a rule that can be traded; one market condition; one company. A forward record on new days follows (`python -m src.cds_oracle forward`).",
          "The data: public trade reports under the SEC's Regulation SBSR (DTCC), kept for our own testing, not uploaded (TRACK 3.127)."]
    DOCS.mkdir(exist_ok=True); (DOCS / "cds_oracle.md").write_text("\n".join(L) + "\n")
    print(f"  Oracle's share on the jump day {f2(same)}; the next session {f2(raw)}; after look-alike days {f2(alike)}")
    print(f"VERDICT: {verdict} -- difference {f2(stat)}" + ("" if p != p else f", chance {p:.4f} ({copies} copies; limit 0.05)"))
    print("  every jump: day | spread before -> that day (trades) | share that day | next session | look-alike days' next session")
    for d, r in E.iterrows(): print(f"    {d:%Y-%m-%d} | {F.prev_bp[d]:.0f} -> {F.bp[d]:.0f} ({F.trades[d]}) | {f2(F.same[d])} | {f2(r.next)} | {f2(r.alike)}")
    print("-> docs/cds_oracle.md")


def cmd_forward():
    """every jump on or after START, with its result once the next session is finished. Only counts and averages go into docs/ (the trades themselves are not uploaded)."""
    F = _frame(); ev = F.jump.to_numpy() & (F.index >= START); E = _excess(F, F.jump.to_numpy()); E = E[E.index >= START]; waiting = int(ev.sum()) - len(E); n = len(E); f2 = lambda x: "n/a" if x != x else f"{x * 100:+.2f}%"
    diff = float((E.next - E.alike).mean()) if n else np.nan; worse = int((E.next < E.alike).sum()) if n else 0
    L = ["# CDS-4 forward record: Oracle's share the session after a jump in its CDS", "", f"From {START:%d %b %Y}. A jump = Oracle's CDS spread (given spreads only) 5% or more above its last day with one. Verdict at {VERDICT_AT} jumps with a result (TRACK 3.135). Last day in the files: {F.index[-1]:%Y-%m-%d}.", "",
         "| jumps with a result | waiting for the next session | share weaker than after look-alike days | average difference |", "|---|---|---|---|", f"| {n} of {VERDICT_AT} | {waiting} | {worse} of {n} | {f2(diff)} |", "", "| day | share that day | next session | look-alike days' next session |", "|---|---|---|---|"]
    L += [f"| {d:%Y-%m-%d} | {f2(F.same[d])} | {f2(r.next)} | {f2(r.alike)} |" for d, r in E.iterrows()] or ["| (no jump yet) | | | |"]
    DOCS.mkdir(exist_ok=True); (DOCS / "cds_oracle_forward.md").write_text("\n".join(L) + "\n")
    last = F[F.bp.notna()].tail(1); print(f"  Oracle CDS forward record: {n} of {VERDICT_AT} jumps with a result" + (f", average difference {f2(diff)}" if n else "") + f"; {waiting} waiting. Last given spread: " + (f"{last.index[0]:%d %b}, {last.bp.iloc[0]:.0f} bp" + (f" ({(np.exp(last.chg.iloc[0]) - 1) * 100:+.0f}% against the day before with one" + (" -- A JUMP" if bool(last.jump.iloc[0]) else "") + ")" if last.chg.notna().iloc[0] else "") if len(last) else "none") + " -> docs/cds_oracle_forward.md")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["test", "forward"]); a = ap.parse_args(); cmd_test() if a.cmd == "test" else cmd_forward()
