import requests
import json

YOUTUBE_API_KEY = "AIzaSyDgEj4dcjaz2oOh7QGzQUxHZIWtlPMwnTo"  # Your API key
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

def fetch_viral_youtube_videos(query="trending", max_results=5):
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "order": "viewCount",
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY
    }
    response = requests.get(YOUTUBE_SEARCH_URL, params=params)
    data = response.json()
    videos = []

    for item in data.get("items", []):
        video = {
            "title": item["snippet"]["title"],
            "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            "channel": item["snippet"]["channelTitle"]
        }
        videos.append(video)

    return videos

if __name__ == "__main__":
    viral_videos = fetch_viral_youtube_videos()
    with open("viral_youtube.json", "w") as f:
        json.dump(viral_videos, f, indent=2)

    print("✅ Viral YouTube videos saved to viral_youtube.json")
