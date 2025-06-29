API_KEY = "9qhG3xjHIBzHVXN9aYM4qevD2P9N6aDuDWFlUDl3ZMQjgFqLPWcuKQEa"  # your TikTok API key

def search_tiktok_videos(query, max_results=5):
    # Simulated result for now (since TikTok API is not officially public)
    videos = [
        {"url": f"https://www.tiktok.com/@user/video/{i}"} for i in range(1, max_results + 1)
    ]
    return videos
