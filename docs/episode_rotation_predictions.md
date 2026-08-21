# Predictions before first episode_rotation run (2026-08-21)

EPLEN: primary 15, decided on definitional grounds (architecture doc horizon
"multi-week", committed 2026-08-19, before any episode data was seen).
Sensitivity ladder {10, 15, 20} declared now; ALL rungs reported regardless of
outcome; no rung may be promoted to primary after results are seen.

Shock arm (primary): ~60-90 episodes expected; order concentration tau
+0.05..+0.15 with p 0.05-0.30 (suggestive, not clearing 0.05); 0-1 pairs after
Holm. Stress arm: <20 episodes, all null, underpowered by construction.

Reading rule, fixed in advance: the SHOCK arm is the verdict on the
episode-local hypothesis; the stress arm is the GDELT integration test. Future
detectors (FOMC decisions, FOMC minutes, chain earnings, 8-K) cross-validate
via --trigger file with no engine changes.

Engine verified on synthetic data before first real run: planted 1-day lead
detected at d=0.93, destroyed by the per-name episode-shuffle null to 0.09;
identical episode orders give tau=1.00, random orders -0.02.
