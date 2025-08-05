from flask import Flask, send_file
import os

app = Flask(__name__)

@app.route("/output.json")
def get_output():
    file_path = os.path.join(os.path.dirname(__file__), "output.json")
    if os.path.exists(file_path):
        return send_file(file_path, mimetype="application/json")
    else:
        return {"error": "output.json not found"}, 404

@app.route("/")
def home():
    return "Content Automation Backend Running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
