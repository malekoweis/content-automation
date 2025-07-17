import requests

YOUTUBE_API_KEY = "AIzaSyDgEj4dcjaz2oOh7QGzQUxHZIWtlPMwnTo"  # Replace with yours
MAX_RESULTS = 10

def fetch_youtube_videos():
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": "viral videos",
        "type": "video",
        "order": "viewCount",
        "maxResults": MAX_RESULTS,
        "key": YOUTUBE_API_KEY
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("YouTube API error:", response.status_code, response.text)
        return []

    data = response.json()
    results = []

    for item in data.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        thumbnail = item["snippet"]["thumbnails"]["high"]["url"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        results.append({
            "type": "youtube",
            "url": video_url,
            "description": title,
            "thumbnailUrl": thumbnail
        })

    return results

