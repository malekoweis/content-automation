#!/usr/bin/env bash
set -euo pipefail
ROOT="$(pwd)"
bk() { [ -f "$1" ] && cp -n "$1" "$1.bak.$(date +%s)" || true; }

echo "[1/7] Writing files…"
mkdir -p logs
bk app.py; cat > app.py << "PY"
import os, json, subprocess, threading, time, pathlib
from flask import Flask, jsonify, send_file, request
from flask_cors import CORS

BASE_DIR = pathlib.Path(__file__).resolve().parent
OUTPUT_PATH = BASE_DIR / "output.json"
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def _read_json_safe(path: pathlib.Path):
    if not path.exists():
        return None, "output.json not found"
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data, None
    except Exception as e:
        return None, f"Invalid JSON: {e}"

@app.get("/")
def index():
    return jsonify({
        "service": "content-automation-backend",
        "status": "ok",
        "endpoints": ["/health", "/output.json", "/version", "/run (POST)", "/push (POST)"]
    })

@app.get("/health")
def health():
    data, err = _read_json_safe(OUTPUT_PATH)
    return jsonify({
        "ok": True,
        "has_output_json": OUTPUT_PATH.exists(),
        "json_valid": err is None,
        "error": err
    })

@app.get("/output.json")
def get_output():
    if not OUTPUT_PATH.exists():
        return jsonify({"error": "output.json not found"}), 404
    return send_file(str(OUTPUT_PATH), mimetype="application/json")

@app.get("/version")
def version():
    commit = os.environ.get("RENDER_GIT_COMMIT") or os.environ.get("GIT_COMMIT", "")
    try:
        rev = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
        commit = commit or rev
    except Exception:
        pass
    return jsonify({"commit": commit or "unknown"})

def _tail(path: pathlib.Path, n: int = 4000) -> str:
    try:
        t = path.read_text(encoding="utf-8", errors="ignore")
        return t[-n:]
    except Exception:
        return ""

def _run_script(cmd, log_name, timeout_sec=900):
    log_file = LOGS_DIR / log_name
    start = time.time()
    with log_file.open("w", encoding="utf-8") as lf:
        try:
            proc = subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT, env={**os.environ})
            while proc.poll() is None:
                if time.time() - start > timeout_sec:
                    proc.kill()
                    lf.write("\n\n[ERROR] Process timeout — killed.\n")
                    return False, _tail(log_file)
                time.sleep(0.5)
            return proc.returncode == 0, _tail(log_file)
        except Exception as e:
            lf.write(f"\n\n[ERROR] Exception: {e}\n")
            return False, _tail(log_file)

@app.post("/run")
def run_pipeline():
    ok, log_tail = _run_script(["python", "main.py"], "run_main.log", 900)
    status = 200 if ok else 500
    data, err = _read_json_safe(OUTPUT_PATH)
    return jsonify({
        "ok": ok,
        "log_tail": log_tail,
        "has_output_json": OUTPUT_PATH.exists(),
        "json_valid": err is None,
        "error": err
    }), status

@app.post("/push")
def push_to_github():
    ok, log_tail = _run_script(["python", "push_to_github.py"], "push_to_github.log", 300)
    return (jsonify({"ok": ok, "log_tail": log_tail}), 200 if ok else 500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
PY

bk Procfile; cat > Procfile << "P"
web: gunicorn app:app --workers 2 --threads 4 --timeout 120
P

bk requirements.txt; cat > requirements.txt << "R"
Flask==3.0.3
gunicorn==22.0.0
flask-cors==4.0.1
python-dotenv==1.0.1
requests==2.32.3
urllib3==2.2.2
charset-normalizer==3.3.2
idna==3.7
certifi==2024.7.4
openai>=1.35.7
google-api-python-client==2.132.0
pytz==2024.1
GitPython==3.1.43
R

bk render.yaml; cat > render.yaml << "Y"
services:
  - type: web
    name: content-automation-backend
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app --workers 2 --threads 4 --timeout 120
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.9
      - key: GH_TOKEN
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: YT_API_KEY
        sync: false
      - key: RAPIDAPI_KEY
        sync: false
      - key: GIT_AUTHOR_NAME
        value: automation-bot
      - key: GIT_AUTHOR_EMAIL
        value: bot@example.com
Y

bk push_to_github.py; cat > push_to_github.py << "G"
import os, subprocess, pathlib, sys

BASE_DIR = pathlib.Path(__file__).resolve().parent
REPO_URL = os.environ.get("GIT_REMOTE_URL", "https://github.com/malekoweis/content-automation.git")
GH_TOKEN = os.environ.get("GH_TOKEN")

def run(cmd, check=True):
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, cwd=str(BASE_DIR), check=check)

def ensure_remote():
    run(["git", "init"])
    remotes = subprocess.check_output(["git", "remote"], cwd=str(BASE_DIR)).decode().split()
    if "origin" not in remotes:
        url = REPO_URL
        if GH_TOKEN and url.startswith("https://"):
            url = url.replace("https://", f"https://{GH_TOKEN}@")
        run(["git", "remote", "add", "origin", url], check=False)
    else:
        if GH_TOKEN:
            url = REPO_URL.replace("https://", f"https://{GH_TOKEN}@")
            run(["git", "remote", "set-url", "origin", url], check=False)

def set_identity():
    user = os.environ.get("GIT_AUTHOR_NAME", "automation-bot")
    email = os.environ.get("GIT_AUTHOR_EMAIL", "bot@example.com")
    run(["git", "config", "user.name", user], check=False)
    run(["git", "config", "user.email", email], check=False)

def main():
    if not GH_TOKEN:
        print("ERROR: GH_TOKEN env var is not set.", file=sys.stderr)
        sys.exit(1)

    ensure_remote()
    set_identity()

    run(["git", "add", "-A"], check=False)
    status = subprocess.check_output(["git", "status", "--porcelain"], cwd=str(BASE_DIR)).decode().strip()
    if status:
        run(["git", "commit", "-m", "Automated update"], check=False)
    else:
        print("No changes to commit.")

    branches = subprocess.check_output(["git", "branch", "--list"], cwd=str(BASE_DIR)).decode()
    if "main" not in branches:
        run(["git", "checkout", "-B", "main"], check=False)
    else:
        run(["git", "checkout", "main"], check=False)

    run(["git", "pull", "origin", "main", "--rebase"], check=False)
    run(["git", "push", "origin", "main"], check=False)
    print("Push complete.")

if __name__ == "__main__":
    main()
G

bk .gitignore; cat > .gitignore << "I"
.venv/
__pycache__/
logs/
.env
*.pyc
I

echo "[2/7] Creating venv + installing deps…"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "[3/7] Quick local sanity check…"
python - << "T"
import json, os, pathlib
p = pathlib.Path("output.json")
if not p.exists():
    p.write_text("[]", encoding="utf-8")
print("output.json exists and is basic JSON.")
T

echo "[4/7] Smoke-run Flask (5s) to verify…"
( nohup python app.py >/dev/null 2>&1 & echo $! > .flask_pid )
sleep 5 || true
kill $(cat .flask_pid) 2>/dev/null || true
rm -f .flask_pid

echo "[5/7] Ensure git remote + commit…"
git rebase --abort >/dev/null 2>&1 || true
git reset --hard
git add -A
git commit -m "Flask backend: stable endpoints, CORS, Procfile, render blueprint" || true

echo "[6/7] Set origin if missing…"
if ! git remote | grep -q "^origin$"; then
  git remote add origin https://github.com/malekoweis/content-automation.git
fi

echo "[7/7] Push…"
git push -u origin main || true

echo "Done. Files are ready. Deploy on Render with start command:"
echo "  gunicorn app:app --workers 2 --threads 4 --timeout 120"
echo "Remember to add env vars on Render: GH_TOKEN, OPENAI_API_KEY, YT_API_KEY, RAPIDAPI_KEY."
