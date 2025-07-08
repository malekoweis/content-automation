import subprocess
import os

def push_output_to_github():
    try:
        print("🔄 Attempting to push output.json to GitHub...")

        # Set Git user if not set
        subprocess.run(["git", "config", "--global", "user.email", "render@render.com"], check=True)
        subprocess.run(["git", "config", "--global", "user.name", "Render Deploy"], check=True)

        # Check if remote "origin" exists
        remotes = subprocess.run(["git", "remote"], capture_output=True, text=True)
        if "origin" not in remotes.stdout:
            remote_url = os.getenv("GIT_REMOTE_URL_
