import os
import subprocess

def push_output_to_github():
    repo_dir = os.getcwd()
    os.chdir(repo_dir)

    # Git configuration
    subprocess.run(["git", "config", "user.name", "render-bot"], check=True)
    subprocess.run(["git", "config", "user.email", "render@bot.com"], check=True)

    # Stage output.json
    subprocess.run(["git", "add", "output.json"], check=True)

    # Skip commit if no changes
    result = subprocess.run(["git", "diff", "--cached", "--quiet"])
    if result.returncode == 0:
        print("✅ No changes to commit.")
        return

    # Commit and push using token
    subprocess.run(["git", "commit", "-m", "Update output.json from Render"], check=True)

    token = os.environ.get("GH_TOKEN")
    if not token:
        raise Exception("❌ GH_TOKEN is not set in environment.")

    remote_url = f"https://{token}@github.com/malekoweis/content-automation.git"
    subprocess.run(["git", "remote", "set-url", "origin", remote_url], check=True)

    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("✅ output.json pushed to GitHub successfully.")

if __name__ == "__main__":
    push_output_to_github()
