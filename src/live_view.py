"""live_view.py -- what the 'Event signals' page shows, computed from the live listener's log (data_provenance/live/events.jsonl).
No Streamlit here, so it can be checked on its own. The rules shown are the registered forward rules; swap RULES when a later test crowns another."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import pandas as pd

LIVE = Path("data_provenance/live"); LOG = LIVE / "events.jsonl"; SEEN = LIVE / "seen.json"; OUT = LIVE / "outcomes.csv"; NY = ZoneInfo("America/New_York")
RULES = [      # the rule line shown on the page. To change the rule in force, change this list (and register the change in TRACK first).
    dict(id="FA-4", kind="results", score="own_stock", threshold=0.7, enter_min=1, hold_min=60, instrument="the company's own stock",
         text="Results release: when the own-stock score is 0.7 or more in size, trade the company's own stock in the direction of the score. Enter 1 minute after the release, hold 60 minutes.",
         evidence="Past releases 2020-2026, thresholds fitted on earlier years only: +1.42% per trade on 140 trades, before cost. Measured cost on Interactive Brokers for a US$10,000 trade: 0.21% median, 0.29% average per round trip. Scores of 0.8 or more after cost: +1.04% on 132 trades, right on 60%."),
    dict(id="FA-1", kind="fed", score="implication_equities", threshold=0.0, enter_min=1, hold_min=60, instrument="the Nasdaq-100 future",
         text="Fed statement: trade the Nasdaq-100 future in the direction of the statement's score. Enter 1 minute after the release, hold 60 minutes.",
         evidence="Statement days 2010-2026: +0.30% on average, right on 74% of 101 days, before a cost of about 0.02%."),
]
STATUS = "Candidate rules under forward test. Not confirmed signals, not investment advice."


def _ts(x):
    t = pd.to_datetime(x, utc=True, errors="coerce", format="ISO8601"); return None if pd.isna(t) else t


def load(now=None) -> dict:
    now = now or datetime.now(timezone.utc); rows = []
    if LOG.exists():
        for line in LOG.read_text().splitlines():
            try: rows.append(json.loads(line))
            except Exception: continue
    scored, other = {}, []
    for r in rows:
        seen = _ts(r.get("seen")); pub = _ts(r.get("published"))
        if seen is None: continue
        rel = min(pub, seen) if pub is not None else seen; kind = str(r.get("kind", "")); d = r.get("read") if isinstance(r.get("read"), dict) else None
        base = dict(ticker=r.get("ticker"), kind=kind, title=str(r.get("title", ""))[:140], source=str(r.get("source", "")), release=rel, seen=seen, lag_s=r.get("lag_published_s"), score_s=r.get("score_s"), drill=bool(r.get("drill")), rescored=bool(r.get("rescored")), read=d, link=r.get("link", ""))
        if d is None or r.get("empty") or "(again)" in kind or kind == "other": other.append(base); continue
        if kind == "results" and (d.get("facts") or {}).get("revenue") in (None, "", "null") and not any(d.get(k) for k in ("own_stock", "market", "results_vs_prior_guidance")): other.append(base); continue
        scored[(base["ticker"], kind, rel.astimezone(NY).strftime("%Y-%m-%d"), r.get("id") if kind in ("event", "research") else "")] = base      # a rescored row replaces the live one
    S = sorted(scored.values(), key=lambda b: b["seen"], reverse=True)
    for b in S: b["action"] = action(b, now)
    beat = (now - datetime.fromtimestamp(SEEN.stat().st_mtime, timezone.utc)).total_seconds() if SEEN.exists() else None
    return dict(now=now, scored=S, other=sorted(other, key=lambda b: b["seen"], reverse=True), heartbeat_s=beat, record=record())


def action(b: dict, now) -> dict:
    """what the rule in force says about one scored item, and whether its window is still open"""
    rule = next((r for r in RULES if r["kind"] == b["kind"]), None)
    if rule is None or b["drill"]: return dict(rule=None, text=("alert only: a third party's report, claims unverified; no tested rule" if b["kind"] == "research" else "logged only (no rule for this kind of news)") if rule is None else "drill, not a live item", state="none")
    try: s = float((b["read"] or {}).get(rule["score"]) or 0)
    except Exception: s = 0.0
    if abs(s) < rule["threshold"] or s == 0: return dict(rule=rule["id"], text=f"no trade: score {s:+.2f} is under {rule['threshold']}" if rule["threshold"] else "no trade: score is 0", state="none", score=s)
    rel = b["release"]; t_in = (rel.floor("min") + pd.Timedelta(minutes=(1 if (rel.second or rel.microsecond) else 0) + rule["enter_min"])); t_out = t_in + pd.Timedelta(minutes=rule["hold_min"]); side = "BUY" if s > 0 else "SELL"
    state = "before entry" if now < t_in else ("OPEN" if now < t_out else "closed"); left = max(0, round((t_out - now).total_seconds() / 60)) if state != "closed" else 0
    note = " (scored after the fact: no live trade was possible)" if b["rescored"] else ""
    return dict(rule=rule["id"], side=side, score=s, enter=t_in, exit=t_out, state=state, minutes_left=left, text=f"{side} {rule['instrument'] if b['kind'] == 'fed' else b['ticker']}: enter {t_in.astimezone(NY):%H:%M}, exit {t_out.astimezone(NY):%H:%M} New York{note}")


def record() -> pd.DataFrame:
    if not OUT.exists(): return pd.DataFrame()
    T = pd.read_csv(OUT); T["gross_bp"] = pd.to_numeric(T.get("gross_bp"), errors="coerce"); g = T.dropna(subset=["gross_bp"]).groupby("rule")["gross_bp"]
    return pd.DataFrame(dict(trades=g.size(), average_pct=(g.mean() / 100).round(2), right_on=(g.apply(lambda x: (x > 0).mean()) * 100).round(0))).reset_index() if len(T.dropna(subset=["gross_bp"])) else pd.DataFrame()


def table(items: list, tz: str) -> pd.DataFrame:
    Z = ZoneInfo(tz); rows = []
    for b in items:
        d = b["read"] or {}; fx = d.get("facts") or {}
        rows.append({"Released (New York)": b["release"].astimezone(NY).strftime("%d %b %H:%M:%S"), "Local time": b["release"].astimezone(Z).strftime("%d %b %H:%M"), "Company": b["ticker"], "Type": ("third-party report" if b["kind"] == "research" else b["kind"]) + (" (drill)" if b["drill"] else "") + (" (rescored)" if b["rescored"] else ""),
                     "Own stock": d.get("own_stock"), "Market": d.get("market") if b["kind"] != "fed" else d.get("implication_equities"), "AI demand": d.get("ai_demand"), "Vs prior guidance": d.get("results_vs_prior_guidance"), "New guidance": d.get("guidance_change"), "Material": d.get("material"), "Uncertainty": d.get("uncertainty"),
                     "Rule says": b.get("action", {}).get("text", ""), "Window": b.get("action", {}).get("state", ""), "Revenue": str(fx.get("revenue") or "")[:48], "Guidance": str(fx.get("guidance_next") or "")[:90],
                     "Other companies named": ", ".join(f"{x.get('company')} {float(x.get('direction') or 0):+.1f}" for x in (d.get("affected") or []) if isinstance(x, dict))[:80], "Headline": b["title"], "Source": b["source"], "Seen after release (s)": b["lag_s"], "Scored after seen (s)": b["score_s"]})
    return pd.DataFrame(rows)
