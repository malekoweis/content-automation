### ✅ FULL INTEGRATION PIPELINE (READY TO COPY & RUN)

# ─────────────────────────────────────────
# 1. Create output_collector.py
# ─────────────────────────────────────────

# Create this file inside the project root directory
# File: output_collector.py

import json
from datetime import datetime

def save_output(data, filename="output.json"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record = {
        "timestamp": timestamp,
        "pexels": data.get("pexels", []),
        "youtube": data.get("youtube", []),
        "tiktok": data.get("tiktok", []),
        "pixel_events": data.get("pixel_events", [])
    }

    try:
        with open(filename, "a") as f:
            f.write(json.dumps(record, indent=2) + "\n")
        print(f"[✓] Output saved to {filename}")
    except Exception as e:
        print(f"[!] Failed to save output: {e}")


# ─────────────────────────────────────────
# 2. Update main.py to collect all results
# ─────────────────────────────────────────

# Replace your entire main.py with the following:

from pexels_api import get_pexels_images
from youtube_api import search_youtube_videos
from tiktok_api import search_tiktok_videos
from pixel_tracker import track_pixel_events
from output_collector import save_output

if __name__ == "__main__":
    print("\nGetting images from Pexels...")
    images = get_pexels_images("nature")
    for img in images:
        print(f"Pexels Image URL: {img['url']}")

    print("\nGetting videos from YouTube...")
    videos = search_youtube_videos("nature")
    for vid in videos:
        print(f"YouTube Video URL: {vid['url']}")

    print("\nGetting videos from TikTok...")
    tiktok_links = search_tiktok_videos("nature")
    for tiktok in tiktok_links:
        print(f"TikTok Video URL: {tiktok['url']}")

    print("\nTracking Pixel Events...")
    events = track_pixel_events()

    data = {
        "pexels": images,
        "youtube": videos,
        "tiktok": tiktok_links,
        "pixel_events": events
    }

    save_output(data)


# ─────────────────────────────────────────
# 3. To run the whole system:
# ─────────────────────────────────────────

# Inside your virtualenv, run:
#
#     source venv/bin/activate
#     python main.py
#     cat output.json

# Done. This setup will generate one output.json file with timestamps
# and full API results every time it runs.
# Perfect for future automation, logs, or dashboard integration.
