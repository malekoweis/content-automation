#!/usr/bin/env bash
set -euxo pipefail
python -V
python -m pip install --upgrade pip
# Install your deps with the SAME interpreter Render will use
python -m pip install --no-cache-dir -r requirements.txt
# Belt & suspenders: force-install gunicorn and prove it’s there
python -m pip install --no-cache-dir gunicorn==22.0.0
python -m pip show gunicorn
python - << 'PY'
import importlib, sys
try:
    importlib.import_module("gunicorn")
    print("gunicorn import OK")
except Exception as e:
    print("gunicorn import FAILED:", e, file=sys.stderr); sys.exit(1)
PY
