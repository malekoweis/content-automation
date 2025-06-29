import os
import subprocess

repo_url = "https://github.com/malekoweis/content-automation.git"
token = os.environ.get("GH_TOKEN")
if not token:
    raise Exception("GitHub token not found in environment variable 'GH_TOKEN'")

# Configure Git
subprocess.run(["git", "config", "--global", "user.name", "AutoBot"], check=True)
subprocess.run(["git", "config", "--global", "user.email", "autobot@render.com"], check=True)

# Clone, copy, commit, and push
subprocess.run(["git", "clone", f"https://malekoweis:{token}@github.com/malekoweis/content-automation.git"], check=True)
os.chdir("content-automation")
subprocess.run(["cp", "../output.json", "."], check=True)
subprocess.run(["git", "add", "output.json"], check=True)
subprocess.run(["git", "commit", "-m", "Update output.json from Render"], check=True)
subprocess.run(["git", "push"], check=True)
