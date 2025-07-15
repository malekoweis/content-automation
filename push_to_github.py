kimport os
import subprocess
from datetime import datetime

def push_output():
    try:
        subprocess.run(["git", "config", "--global", "user.name", "Render Bot"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "render@example.com"], check=True)

        GITHUB_TOKEN = os.environ.get("GH_TOKEN")
        if not GITHUB_TOKEN:
            raise Exception("❌ GH_TOKEN environment variable not set.")
        
        remote_url = f"https://{GITHUB_TOKEN}@github.com/malekoweis/content-automation.git"

        # Check if 'origin' exists
        result = subprocess.run(["git", "remote"], capture_output=True, text=True, check=True)
        remotes = result.stdout.strip().splitlines()

        if "origin" in remotes:
            subprocess.run(["git", "remote", "set-url", "origin", remote_url], check=True)
        else:
            subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)

        subprocess.run(["git", "remote", "-v"], check=True)

        subprocess.run(["git", "add", "output.json"], check=True)
        commit_message = f"Update output.json - {datetime.now().isoformat()}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push", "origin", "main", "--force"], check=True)

        print("✅ output.json pushed to GitHub successfully.")

    except subprocess.CalledProcessError as e:
        print(f"❌ Git push failed: {e}")
    except Exception as e:
        print(f"❌ General error: {e}")

if __name__ == "__main__":
    push_output()

