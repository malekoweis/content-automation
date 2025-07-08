import os
import subprocess

def push_output_to_github():
    # Step into project directory
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(repo_dir)

    # GitHub remote with personal access token
token = os.getenv("GH_TOKEN")
remote_url = f"https://{token}@github.com/malekoweis/content-automation.git"
    )

    # Add origin if it doesn't exist (Render container has no remotes by default)
    result = subprocess.run(["git", "remote"], capture_output=True, text=True)
    remotes = result.stdout.strip().split("\n")

    if "origin" not in remotes:
        subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)
    else:
        subprocess.run(["git", "remote", "set-url", "origin", remote_url], check=True)

    # Pull to avoid push conflict
    subprocess.run(["git", "pull", "origin", "main", "--rebase"], check=True)

    # Stage the output file
    subprocess.run(["git", "add", "output.json"], check=True)

    # Check if there's anything to commit
    status_result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if not status_result.stdout.strip():
        print("✅ No changes to commit.")
        return

    # Commit and push
    subprocess.run(["git", "commit", "-m", "Update output.json from Render"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
