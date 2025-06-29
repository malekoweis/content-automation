import json
import re
import requests

# === CONFIG ===
input_file = "filtered_output.json"
output_file = "filtered_output_fixed.json"
api_key = "AIzaSyDgEj4dcjaz2oOh7QGzQUxHZIWtlPMwnTo"

# === FUNCTION TO EXTRACT VIDEO ID ===
def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([\w-]+)", url)
    return match.group(1) if match else None

# === FETCH VIDEO TITLE FROM YOUTUBE ===
def fetch_youtube_title(video_id):
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])
        if items:
            return items[0]["snippet"]["title"]
    except Exception as e:
        print(f"Error fetching title for {video_id}: {e}")
    return "No title available"

# === LOAD JSON ===
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# === PROCESS YOUTUBE VIDEOS ===
for video in data.get("youtube_videos", []):
    video_id = extract_video_id(video.get("url", ""))
    title = fetch_youtube_title(video_id) if video_id else "Unknown Video"
    video["description"] = title
    # Remove the original gpt_description if present
    video.pop("gpt_description", None)

# === FIX PEXELS & TIKTOK TOO (if needed) ===
for group in ["pexels_images", "tiktok_videos"]:
    for item in data.get(group, []):
        if "gpt_description" in item:
            item["description"] = item.pop("gpt_description")

# === SAVE FIXED FILE ===
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"✅ Fixed file saved to: {output_file}")
