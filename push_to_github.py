import os
import base64
import requests
from datetime import datetime

def push_output():
    try:
        GITHUB_TOKEN = os.environ.get("GH_TOKEN")
        if not GITHUB_TOKEN:
            raise Exception("❌ GH_TOKEN environment variable not set.")

        repo = "malekoweis/content-automation"
        path = "output.json"
        branch = "main"

        # Read output.json and encode it
        with open("output.json", "rb") as f:
            content = base64.b64encode(f.read()).decode("utf-8")

        url = f"https://api.github.com/repos/{repo}/contents/{path}"
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        }

        # Check if output.json already exists
        response = requests.get(url, headers=headers)
        sha = response.json().get("sha") if response.status_code == 200 else None

        data = {
            "message": f"Auto-update output.json - {datetime.now().isoformat()}",
            "content": content,
            "branch": branch
        }

        if sha:
            data["sha"] = sha  # Needed to overwrite

        # Upload via GitHub API
        put_response = requests.put(url, headers=headers, json=data)
        if put_response.status_code in [200, 201]:
            print("✅ output.json uploaded to GitHub via API.")
        else:
            print(f"❌ GitHub upload failed: {put_response.status_code} {put_response.text}")

    except Exception as e:
        print(f"❌ General error: {e}")

if __name__ == "__main__":
    push_output()
