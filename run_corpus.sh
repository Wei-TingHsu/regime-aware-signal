#!/bin/zsh
set -e          # STOP on the first non-zero exit. doc_read exits 1 on a fatal
                # error; without this the script just tries the next source and
                # burns more calls against the same exhausted balance.
cd ~/Projects/regime-aware-signal
source .venv/bin/activate
python -m src.doc_read --source fomc_minutes    --with-prev --out processed/read_minutes.csv
python -m src.doc_read --source earnings_8k                 --out processed/read_8k.csv
python -m src.doc_read --source political_order             --out processed/read_political_order.csv
python -m src.doc_read --source political_other             --out processed/read_political_other.csv
echo "CORPUS READ COMPLETE"
