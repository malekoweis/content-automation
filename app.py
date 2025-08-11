import os, json, time, subprocess, pathlib
from flask import Flask, jsonify, send_file
from flask_cors import CORS

BASE_DIR = pathlib.Path(__file__).resolve().parent
OUTPUT_PATH = BASE_DIR / "output.json"

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
        rev = subprocess.check_output(["git","rev-parse","--short","HEAD"]).decode().strip()
        commit = commit or rev
    except Exception:
        pass
    return jsonify({"commit": commit or "unknown"})

if __name__ == "__main__":
    # Render provides $PORT; bind to it so the service starts
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
