import os
import subprocess
from datetime import datetime

def push_output():
    try:
        # Setup Git identity
        subprocess.run(["git", "config", "--global", "user.name", "Render Bot"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "render@example.com"], check=True)

        # Ensure remote is set correctly (replace if needed)
        GITHUB_TOKEN = os.environ.get("GH_TOKEN")
        if not GITHUB_TOKEN:
            raise Exception("❌ GH_TOKEN environment variable not set.")
        
        remote_url = f"https://{GITHUB_TOKEN}@github.com/malekoweis/content-automation.git"
        subprocess.run(["git", "remote", "remove", "origin"], check=False)
        subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)

        # Debugging: Show current Git config
        subprocess.run(["git", "remote", "-v"], check=True)
        subprocess.run(["git", "branch", "-vv"], check=True)

        # Add and commit changes with timestamp
        subprocess.run(["git", "add", "output.json"], check=True)
        commit_message = f"Update output.json - {datetime.now().isoformat()}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        # Force push to GitHub
        subprocess.run(["git", "push", "origin", "main", "--force"], check=True)
        print("✅ output.json pushed to GitHub successfully.")

    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")
    except Exception as e:
        print(f"❌ General error: {e}")
