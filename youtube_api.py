from googleapiclient.discovery import build

# Replace with your actual YouTube Data API key
YOUTUBE_API_KEY = "AIzaSyDgEj4dcjaz2oOh7QGzQUxHZIWtlPMwnTo"

def get_youtube_videos(query="nature", max_results=5):
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    request = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=max_results
    )

    response = request.execute()

    videos = []
    for item in response.get("items", []):
        video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
        thumbnail = item['snippet']['thumbnails']['high']['url']
        title = item['snippet']['title']
        
        videos.append({
            "type": "youtube",
            "url": video_url,
            "thumbnailUrl": thumbnail,
            "description": title
        })

    return videos

