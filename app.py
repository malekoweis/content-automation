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
