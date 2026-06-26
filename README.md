# Regime-Aware Cross-Asset Signal Framework

NUS BMF5391C Experiential Project — Hsu Wei-Ting (E1616086), supervised by Dr Lee Yen Teik.

A hybrid regime-and-flow detection framework for cross-asset signal extraction, combining
classical multi-factor analysis with an LLM-driven scenario layer. Investigates three
empirical questions in asset pricing: conditional safe-haven behaviour, capital rotation
within thematic chains, and the appropriate role of LLMs in financial pipelines.

## Project structure

- `config/` — single-source-of-truth configuration (config.yaml)
- `raw/` — untouched API pulls (gitignored, regenerable)
- `processed/` — cleaned, aligned data panels (gitignored, regenerable)
- `outputs/` — fitted models, diagnostics, figures (gitignored, regenerable)
- `src/` — pipeline modules
- `notebooks/` — exploratory analysis and diagnostics
- `docs/` — methodology, LLM playbook, factor dictionary
- `hypotheses/` — pre-registered hypotheses for the quant engine to test

## Setup

1. Clone the repo.
2. `python3 -m venv .venv && source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. Create `.env` with `FRED_API_KEY=<your key>` (request one at fred.stlouisfed.org).
5. `python src/download_data.py` (forthcoming) builds the raw cache.

## Reproducibility

All randomness is seeded from `config.yaml::project.random_seed`. The `raw/` directory
is write-once; the pipeline regenerates `processed/` and `outputs/` deterministically.