import os
import json
import requests
from urllib.parse import urlparse

OUTPUT_FOLDER = "processed_media"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def download_file(url, output_dir):
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            filename = os.path.basename(urlparse(url).path)
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Downloaded: {url}")
        else:
            print(f"Failed to download {url}: HTTP {response.status_code}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

def process_json(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Pexels images
    for item in data.get("pexels_images", []):
        src = item.get("src", {})
        original_url = src.get("original")
        if original_url:
            download_file(original_url, OUTPUT_FOLDER)

    # YouTube videos (placeholder URLs or thumbnails)
    for item in data.get("youtube_videos", []):
        url = item.get("url")
        if url:
            download_file(url, OUTPUT_FOLDER)

    # TikTok videos (placeholder or for pixel tracking test)
    for item in data.get("tiktok_videos", []):
        url = item.get("url")
        if url:
            download_file(url, OUTPUT_FOLDER)

if __name__ == "__main__":
    process_json("filtered_output_fixed.json")
