import os
import subprocess

def push_output_to_github():
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(repo_dir, 'output.json')

    os.chdir(repo_dir)

    if not os.path.exists(output_file):
        print("❌ output.json not found.")
        return

    # ✅ Add user config so Git can commit in Render
    subprocess.run(["git", "config", "--global", "user.name", "AutoBot"], check=True)
    subprocess.run(["git", "config", "--global", "user.email", "autobot@render.com"], check=True)

    try:
        subprocess.run(["git", "add", "output.json"], check=True)
        subprocess.run(["git", "commit", "-m", "Update output.json from Render"], check=True)
    except subprocess.CalledProcessError:
        print("ℹ️ Nothing to commit.")
        return

    # ✅ Set remote if missing
    result = subprocess.run(["git", "remote"], capture_output=True, text=True)
    remotes = result.stdout.strip().split('\n')
    if "origin" not in remotes:
        remote_url = f"https://{os.getenv('GH_TOKEN')}@github.com/malekoweis/content-automation.git"
        subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)

    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("✅ Git push successful")

if __name__ == "__main__":
    push_output_to_github()
