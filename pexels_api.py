# pexels_api.py

import requests

# ✅ Your provided Pexels API key
PEXELS_API_KEY = "9qhG3xjHIBzHVXN9aYM4qevD2P9N6aDuDWFlUDl3ZMQjgFqLPWcuKQEa"

def get_pexels_videos():
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    url = "https://api.pexels.com/videos/search?query=nature&per_page=5"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        videos = []
        for video in data.get("videos", []):
            videos.append({
                "type": "Pexels",
                "url": video["video_files"][0]["link"],
                "thumbnailUrl": video["image"],
                "description": video.get("url", "")
            })

        return videos

    except Exception as e:
        print(f"❌ Failed to fetch videos from Pexels: {e}")
        return []
