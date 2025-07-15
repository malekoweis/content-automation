def get_tiktok_videos(limit=10):
    # Simulated trending TikTok videos
    videos = []
    for i in range(limit):
        videos.append({
            "type": "tiktok",
            "url": f"https://www.tiktok.com/@user/video/123456789{i}",
            "description": f"Simulated TikTok video {i+1}",
            "thumbnailUrl": f"https://example.com/tiktok_thumb_{i}.jpg"
        })
    return videos
