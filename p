import requests

PEXELS_API_KEY = "9qhG3xjHIBzHVXN9aYM4qevD2P9N6aDuDWFlUDl3ZMQjgFqLPWcuKQEa"  # ✅ Your updated key

def get_pexels_images(query="nature", max_results=10):
    url = f"https://api.pexels.com/videos/search?query={query}&per_page={max_results}"
    headers = {
        "Authorization": PEXELS_API_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        results = []
        for video in data.get("videos", []):
            video_url = video.get("video_files", [{}])[0].get("link", "")
            thumbnail_url = video.get("image", "")
            photographer = video.get("user", {}).get("name", "Unknown")

            if video_url:
                results.append({
                    "type": "pexels",
                    "url": video_url,
                    "description": photographer,
                    "thumbnailUrl": thumbnail_url
                })

        print(f"✅ Pexels videos fetched: {len(results)}")
        return results

    except Exception as e:
        print(f"❌ Error fetching Pexels videos: {e}")
        return []
