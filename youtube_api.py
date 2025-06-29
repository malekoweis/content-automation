import requests

API_KEY = "AIzaSyDgEj4dcjaz2oOh7QGzQUxHZIWtlPMwnTo"  # your YouTube API key

def search_youtube_videos(query, max_results=5):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": API_KEY
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        videos = []
        for item in response.json().get("items", []):
            video_id = item["id"]["videoId"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            videos.append({"url": video_url})
        return videos
    else:
        return {"error": response.status_code, "message": response.text}
