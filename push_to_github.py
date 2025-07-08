import subprocess
import os

def push_output_to_github():
    try:
        print("🔄 Attempting to push output.json to GitHub...")

        # Set Git user if not already set
        subprocess.run(["git", "config", "--global", "user.email", "render@render.com"], check=True)
        subprocess.run(["git", "config", "--global", "user.name", "Render Deploy"], check=True)

        # Check if remote "origin" exists
        remotes = subprocess.run(["git", "remote"], capture_output=True, text=True)
        if "origin" not in remotes.stdout:
            remote_url = os.getenv("GIT_REMOTE_URL")
            if not remote_url:
                raise ValueError("❌ GIT_REMOTE_URL environment variable not set")
            subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)

        # Add and commit output.json
        subprocess.run(["git", "add", "output.json"], check=True)
        subprocess.run(["git", "commit", "--allow-empty", "-m", "Force push output.json from Render"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)

        print("✅ output.json pushed to GitHub successfully.")

    except Exception as e:
        print(f"❌ Failed to push to GitHub: {e}")
