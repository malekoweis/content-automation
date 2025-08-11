#!/usr/bin/env bash
set -euxo pipefail
python -V
python -m pip install --upgrade pip
# Install from your repo's requirements
python -m pip install --no-cache-dir -r requirements.txt
# Belt & suspenders: ensure gunicorn is present even if the step above is ignored
python -m pip install --no-cache-dir gunicorn==22.0.0
# Prove it's installed
python -m pip show gunicorn
python - << 'PY'
import importlib
import sys
try:
    importlib.import_module("gunicorn")
    print("gunicorn import OK")
except Exception as e:
    print("gunicorn import FAILED:", e, file=sys.stderr); sys.exit(1)
PY
