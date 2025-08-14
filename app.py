from flask import Flask, jsonify
import json, os, pathlib

app = Flask(__name__, static_url_path="/rendered", static_folder="rendered")

@app.get("/output.json")
def output_raw():
    with open("output.json","r",encoding="utf-8") as f:
        return app.response_class(f.read(), mimetype="application/json")

@app.get("/output_enhanced.json")
def output_enhanced():
    items = json.load(open("output.json","r",encoding="utf-8"))
    manifest_path = pathlib.Path("rendered/manifest.json")
    manifest = []
    if manifest_path.exists():
        try:
            manifest = json.load(open(manifest_path,"r",encoding="utf-8"))
        except Exception:
            manifest = []
    by_src = {m.get("source_url"): f"/rendered/{m.get('file')}" for m in manifest if m.get("source_url") and m.get("file")}
    for it in items:
        it["renderedUrl"] = by_src.get(it.get("url"))
        it["voiceText"]  = it.get("ai_script")
    return jsonify(items)

@app.get("/")
def home():
    return jsonify({"ok": True, "endpoints": ["/output.json", "/output_enhanced.json", "/rendered/..."]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT","5000")))
