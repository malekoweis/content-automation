import os
import subprocess
from datetime import datetime

def push_output():
    try:
        # Setup Git identity
        subprocess.run(["git", "config", "--global", "user.name", "Render Bot"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "render@example.com"], check=True)

        # Get token and set remote URL
        GITHUB_TOKEN = os.environ.get("GH_TOKEN")
        if not GITHUB_TOKEN:
            raise Exception("❌ GH_TOKEN environment variable not set.")

        remote_url = f"https://{GITHUB_TOKEN}@github.com/malekoweis/content-automation.git"

        # Get existing remotes
        result = subprocess.run(["git", "remote"], capture_output=True, text=True, check=True)
        remotes = result.stdout.strip().splitlines()

        if "origin" in remotes:
            subprocess.run(["git", "remote", "set-url", "origin", remote_url], check=True)
        else:
            subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)

        # Debug
        subprocess.run(["git", "remote", "-v"], check=True)

        # Stage and commit output.json
        subprocess
