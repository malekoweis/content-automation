#!/usr/bin/env bash
set -euo pipefail
echo "[1/6] Ensure pip…"
sudo apt update >/dev/null 2>&1 || true
sudo apt install -y python3-pip >/dev/null 2>&1 || true

echo "[2/6] Write backend files…"
mkdir -p logs
# (re)write files exactly as before
cat > app.py << "PY"
import os, json, subprocess, time, pathlib
from flask import Flask, jsonify, send_file
from flask_cors import CORS
BASE_DIR = pathlib.Path(__file__).resolve().parent
OUTPUT_PATH = BASE_DIR / "output.json"
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
def _read_json_safe(path: pathlib.Path):
    if not path.exists(): return None, "output.json not found"
    try:
        with path.open("r", encoding="utf-8") as f: return json.load(f), None
    except Exception as e: return None, f"Invalid JSON: {e}"
@app.get("/")
def index():
    return jsonify({"service":"content-automation-backend","status":"ok",
                    "endpoints":["/health","/output.json","/version","/run (POST)","/push (POST)"]})
@app.get("/health")
def health():
    data, err = _read_json_safe(OUTPUT_PATH)
    return jsonify({"ok": True, "has_output_json": OUTPUT_PATH.exists(),
                    "json_valid": err is None, "error": err})
@app.get("/output.json")
def get_output():
    if not OUTPUT_PATH.exists(): return jsonify({"error":"output.json not found"}), 404
    return send_file(str(OUTPUT_PATH), mimetype="application/json")
@app.get("/version")
def version():
    commit = os.environ.get("RENDER_GIT_COMMIT") or os.environ.get("GIT_COMMIT", "")
    try:
        import subprocess
        rev = subprocess.check_output(["git","rev-parse","--short","HEAD"]).decode().strip()
        commit = commit or rev
    except Exception: pass
    return jsonify({"commit": commit or "unknown"})
def _tail(path: pathlib.Path, n: int = 4000) -> str:
    try: return path.read_text(encoding="utf-8", errors="ignore")[-n:]
    except Exception: return ""
def _run(cmd, log_name, timeout_sec=900):
    log = LOGS_DIR / log_name; start = time.time()
    with log.open("w", encoding="utf-8") as lf:
        try:
            p = subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT, env={**os.environ})
            while p.poll() is None:
                if time.time()-start>timeout_sec:
                    p.kill(); lf.write("\n\n[ERROR] Timeout — killed.\n"); return False, _tail(log)
                time.sleep(0.5)
            return p.returncode==0, _tail(log)
        except Exception as e:
            lf.write(f"\n\n[ERROR] {e}\n"); return False, _tail(log)
@app.post("/run")
def run_pipeline():
    ok, tail = _run(["python3","main.py"], "run_main.log", 900)
    data, err = _read_json_safe(OUTPUT_PATH)
    return jsonify({"ok":ok,"log_tail":tail,"has_output_json":OUTPUT_PATH.exists(),"json_valid":err is None,"error":err}), (200 if ok else 500)
@app.post("/push")
def push_to_github():
    ok, tail = _run(["python3","push_to_github.py"], "push_to_github.log", 300)
    return jsonify({"ok":ok,"log_tail":tail}), (200 if ok else 500)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT","5000")))
PY
cat > Procfile << "P"
web: gunicorn app:app --workers 2 --threads 4 --timeout 120
P
cat > requirements.txt << "R"
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
cat > render.yaml << "Y"
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
cat > push_to_github.py << "G"
import os, subprocess, pathlib, sys
BASE_DIR = pathlib.Path(__file__).resolve().parent
REPO_URL = os.environ.get("GIT_REMOTE_URL","https://github.com/malekoweis/content-automation.git")
GH_TOKEN = os.environ.get("GH_TOKEN")
def run(cmd, check=True): print("+"," ".join(cmd), flush=True); return subprocess.run(cmd, cwd=str(BASE_DIR), check=check)
def ensure_remote():
    run(["git","init"]); rem = subprocess.check_output(["git","remote"], cwd=str(BASE_DIR)).decode().split()
    if "origin" not in rem:
        url = REPO_URL
        if GH_TOKEN and url.startswith("https://"): url = url.replace("https://", f"https://{GH_TOKEN}@")
        run(["git","remote","add","origin",url], check=False)
    elif GH_TOKEN:
        url = REPO_URL.replace("https://", f"https://{GH_TOKEN}@")
        run(["git","remote","set-url","origin",url], check=False)
def set_identity():
    run(["git","config","user.name",os.environ.get("GIT_AUTHOR_NAME","automation-bot")], check=False)
    run(["git","config","user.email",os.environ.get("GIT_AUTHOR_EMAIL","bot@example.com")], check=False)
def main():
    if not GH_TOKEN: print("ERROR: GH_TOKEN not set", file=sys.stderr); sys.exit(1)
    ensure_remote(); set_identity()
    run(["git","add","-A"], check=False)
    st = subprocess.check_output(["git","status","--porcelain"], cwd=str(BASE_DIR)).decode().strip()
    if st: run(["git","commit","-m","Automated update"], check=False)
    br = subprocess.check_output(["git","branch","--list"], cwd=str(BASE_DIR])).decode()
    run(["git","checkout","-B","main"], check=False) if "main" not in br else run(["git","checkout","main"], check=False)
    run(["git","pull","origin","main","--rebase"], check=False)
    run(["git","push","origin","main"], check=False)
    print("Push complete.")
if __name__=="__main__": main()
G
echo ".venv/
__pycache__/
logs/
.env
*.pyc" > .gitignore

echo "[3/6] Install deps (user site)…"
python3 -m pip install --user --upgrade pip || true
python3 -m pip install --user -r requirements.txt || python3 -m pip install --user --break-system-packages -r requirements.txt

# expose user site executables (gunicorn) for this session
export PATH="$HOME/.local/bin:$PATH"

echo "[4/6] Sanity JSON + smoke run…"
python3 - << "T"
import pathlib; p=pathlib.Path("output.json")
if not p.exists(): p.write_text("[]", encoding="utf-8")
print("output.json OK")
T
( nohup python3 app.py >/dev/null 2>&1 & echo $! > .flask_pid )
sleep 5 || true
kill $(cat .flask_pid) 2>/dev/null || true
rm -f .flask_pid

echo "[5/6] Commit + ensure origin…"
git rebase --abort >/dev/null 2>&1 || true
git reset --hard
git add -A
git commit -m "Flask backend (no-venv): endpoints, CORS, Procfile, blueprint" || true
git remote -v | grep -q "^origin" || git remote add origin https://github.com/malekoweis/content-automation.git

echo "[6/6] Push…"
git push -u origin main || true
echo "Done. Deploy on Render with start command:"
echo "  gunicorn app:app --workers 2 --threads 4 --timeout 120"
echo "Add env vars: GH_TOKEN, OPENAI_API_KEY, YT_API_KEY, RAPIDAPI_KEY."
