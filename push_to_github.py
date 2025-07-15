import os
import subprocess
from datetime import datetime

def push_output():
    try:
        # Step 1: Setup Git identity for Render
        subprocess.run(["git", "config", "--global", "user.name", "Render Bot"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "render@example.com"], check=True)

        # Step 2: Fetch GitHub token from environment
        GITHUB_TOKEN = os.environ.get("GH_TOKEN")
        if not GITHUB_TOKEN:
            raise Exception("❌ GH_TOKEN environment variable not set.")

        # Step 3: Set remote origin (overwrite if already exists)
        remote_url = f"https://{GITHUB_TOKEN}@github.com/malekoweis/content-automation.git"
        subprocess.run(["git", "remote", "remove", "origin"], check=False)
        subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)

        # Optional Debug: show remotes and branches
        subprocess.run(["git", "remote", "-v"], check=True)
        subprocess.run(["git", "branch", "-vv"], check=True)

        # Step 4: Stage and commit output.json with timestamp
        subprocess.run(["git", "add", "output.json"], check=True)
        commit_message = f"Update output.json - {datetime.now().isoformat()}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        # Step 5: Push changes
        subprocess.run(["git", "push", "origin", "main", "--force"], check=True)
        print("✅ output.json pushed to GitHub successfully.")

    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")
    except Exception as e:
        print(f"❌ General error: {e}")

# Trigger it
if __name__ == "__main__":
    push_output()
