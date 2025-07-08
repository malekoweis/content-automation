import requests

# Replace with your actual API key
PEXELS_API_KEY = "563492ad6f91700001000001abcdef1234567890abcdefabcdef"

def get_pexels_videos(count=5):
    """
    Fetch video URLs from the Pexels API.
    """
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    params = {
        "query": "nature",
        "per_page": count
    }

    response = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params)

    if response.status_code != 200:
        print("❌ Failed to fetch videos from Pexels")
        return []

    data = response.json()
    videos = []

    for video in data.get("videos", []):
        videos.append({
            "type": "pexels",
            "url": video["video_files"][0]["link"],
            "thumbnailUrl": video["image"],
            "description": video.get("user", {}).get("name", "Pexels video")
        })

    return videos
