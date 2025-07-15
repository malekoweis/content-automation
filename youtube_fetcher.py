import os
import requests

# Replace with your YouTube Data API key or environment variable if preferred
YOUTUBE_API_KEY = "AIzaSyCH8g6GrLZt8bqCg0vHk-LsDLa_zEzTQHU"

def get_youtube_videos(limit=10):
    search_url = "https://www.googleapis.com/youtube/v3/search"
    video_url = "https://www.googleapis.com/youtube/v3/videos"

    # Step 1: Search for popular videos (can be customized)
    search_params = {
        "part": "snippet",
        "q": "viral trending",
        "type": "video",
        "maxResults": limit,
        "key": YOUTUBE_API_KEY
    }

    search_response = requests.get(search_url, params=search_params)
    search_results = search_response.json()

    video_ids = [item["id"]["videoId"] for item in search_results.get("items", [])]

    if not video_ids:
        return []

    # Step 2: Get statistics and metadata
    stats_params = {
        "part": "snippet,statistics",
        "id": ",".join(video_ids),
        "key": YOUTUBE_API_KEY
    }

    stats_response = requests.get(video_url, params=stats_params)
    stats_results = stats_response.json()

    videos = []

    for item in stats_results.get("items", []):
        video_id = item["id"]
        snippet = item["snippet"]
        stats = item.get("statistics", {})

        view_count = int(stats.get("viewCount", 0))
        if view_count < 10000:  # Optional: filter low-view videos
            continue

        videos.append({
            "type": "youtube",
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "description": snippet.get("title", "No Title"),
            "thumbnailUrl": snippet.get("thumbnails", {}).get("high", {}).get("url", "")
        })

    return videos
