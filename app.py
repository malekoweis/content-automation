import os, json, subprocess, time, pathlib, threading
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
            return json.load(f), None
    except Exception as e:
        return None, f"Invalid JSON: {e}"

def _tail(path: pathlib.Path, n: int = 4000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[-n:]
    except Exception:
        return ""

def _run_script(cmd, log_name, timeout_sec=900):
    log_file = LOGS_DIR / log_name
    start = time.time()
    with log_file.open("w", encoding="utf-8") as lf:
        try:
            proc = subprocess.Popen(
                cmd, cwd=str(BASE_DIR),
                stdout=lf, stderr=subprocess.STDOUT,
                env={**os.environ}
            )
            while proc.poll() is None:
                if time.time() - start > timeout_sec:
                    proc.kill()
                    lf.write("\n\n[ERROR] Process timeout — killed.\n")
                    return False, _tail(log_file)
                time.sleep(0.5)
            return (proc.returncode == 0), _tail(log_file)
        except Exception as e:
            lf.write(f"\n\n[ERROR] Exception: {e}\n")
            return False, _tail(log_file)

RUN_STATE = {
    "running": False,
    "started_at": None,
    "finished_at": None,
    "ok": None,
    "log_tail": "",
    "error": None
}
STATE_LOCK = threading.Lock()

def _bg_run_pipeline():
    with STATE_LOCK:
        RUN_STATE.update({
            "running": True, "started_at": time.time(),
            "finished_at": None, "ok": None, "log_tail": "", "error": None
        })
    ok, log_tail = _run_script(["python", "main.py"], "run_main.log", 900)
    _, err = _read_json_safe(OUTPUT_PATH)
    with STATE_LOCK:
        RUN_STATE.update({
            "running": False, "finished_at": time.time(),
            "ok": ok, "log_tail": log_tail, "error": err
        })

@app.route("/run", methods=["POST"])
def run_pipeline():
    with STATE_LOCK:
        if RUN_STATE["running"]:
            # 200 JSON so jq always parses
            return jsonify({"ok": True, "started": False, "running": True, "message": "already running"}), 200
        threading.Thread(target=_bg_run_pipeline, daemon=True).start()
        RUN_STATE["running"] = True
        RUN_STATE["started_at"] = time.time()
    # 200 JSON, not 202, to avoid proxies stripping the body
    return jsonify({"ok": True, "started": True, "running": True}), 200

@app.route("/run/status", methods=["GET"])

def run_status():
    with STATE_LOCK:
        st = dict(RUN_STATE)
    data, err = _read_json_safe(OUTPUT_PATH)
    st.update({
        "has_output_json": OUTPUT_PATH.exists(),
        "json_valid": err is None,
        "error": err,
        "items": (len(data) if isinstance(data, list) else None)
    })
    if st.get("ok") is None and st.get("json_valid"):
        st["ok"] = True
    return jsonify(st)

@app.route("/push", methods=["POST"])
def push_to_github():
    ok, log_tail = _run_script(["python", "push_to_github.py"], "push_to_github.log", 300)
    return jsonify({"ok": ok, "log_tail": log_tail}), (200 if ok else 500)

@app.get("/")
def index():
    return jsonify({
        "service": "content-automation-backend",
        "status": "ok",
        "endpoints": ["/health", "/output.json", "/version", "/run (POST)", "/run/status", "/push (POST)"]
    })

@app.get("/health")
def health():
    _, err = _read_json_safe(OUTPUT_PATH)
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
    resp = send_file(str(OUTPUT_PATH), mimetype="application/json")
    resp.headers["Cache-Control"] = "no-store, no-cache, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

@app.get("/version")
def version():
    commit = os.environ.get("RENDER_GIT_COMMIT") or os.environ.get("GIT_COMMIT", "")
    try:
        rev = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(BASE_DIR)).decode().strip()
        commit = commit or rev
    except Exception:
        pass
    return jsonify({"commit": commit or "unknown"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))


@app.get("/run/log")
def run_log():
    return jsonify({"log_tail": _tail(LOGS_DIR / "run_main.log", 5000)})


@app.post("/admin/clear_history")
def clear_history():
    import os, pathlib
    token = os.environ.get("ADMIN_TOKEN")
    if token and request.headers.get("X-Admin-Token") != token:
        return jsonify({"ok": False, "error": "forbidden"}), 403
    hist = BASE_DIR / "history.json"
    deleted = False
    if hist.exists():
        hist.unlink()
        deleted = True
    return jsonify({"ok": True, "deleted": deleted})
