import json
import os
import subprocess
import datetime
from youtube_api import get_youtube_videos
from tiktok_api import get_tiktok_videos
from pexels_api import get_pexels_images
from pixel_tracker import track_pixel_events

def main():
    print("Getting images from Pexels...")
    pexels_images = get_pexels_images()

    print("Getting videos from YouTube...")
    youtube_videos = get_youtube_videos()

    print("Getting videos from TikTok...")
    tiktok_videos = get_tiktok_videos()

    print("Tracking Pixel Events...")
    pixel_events = track_pixel_events()

    combined_results = []

    for video in youtube_videos:
        video["type"] = "youtube"
        combined_results.append(video)

    for video in tiktok_videos:
        video["type"] = "tiktok"
        combined_results.append(video)

    for image in pexels_images:
        image["type"] = "pexels"
        combined_results.append(image)

    for event in pixel_events:
        event["type"] = "pixel"
        combined_results.append(event)

    print("✅ Tracking Pixel Events...")

    # Write to output.json
    with open("output.json", "w") as f:
        json.dump(combined_results, f, indent=2)

    print(f"✅ Results saved to output.json")
    print(f"✅ output.json written successfully with {len(combined_results)} items")

    # Push to GitHub
    print("🔄 Attempting to push output.json to GitHub...")

    github_token = os.environ.get("GH_TOKEN")
    if not github_token:
        print("❌ General error: ❌ GH_TOKEN environment variable not set.")
        return

    repo_url = f"https://{github_token}@github.com/malekoweis/content-automation.git"
    timestamp = datetime.datetime.now().isoformat(timespec='seconds')
    commit_message = f"Update output.json - {timestamp}"

    try:
        subprocess.run(["git", "config", "user.email", "automation@render.com"], check=True)
        subprocess.run(["git", "config", "user.name", "Render Automation"], check=True)
        subprocess.run(["git", "remote", "set-url", "origin", repo_url], check=True)
        subprocess.run(["git", "add", "output.json"], check=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("✅ output.json pushed to GitHub successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git push failed: {e}")

    print("✅ Script finished.")

if __name__ == "__main__":
    main()
