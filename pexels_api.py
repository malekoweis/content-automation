import requests

# Active Pexels API key (hardcoded for Render use)
PEXELS_API_KEY = "9qhG3xjHIBzHVXN9aYM4qevD2P9N6aDuDWFlUDl3ZMQjgFqLPWcuKQEa"

def get_pexels_images(limit=10):
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    url = f"https://api.pexels.com/videos/popular?per_page={limit}"

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"❌ Failed to fetch Pexels videos: {response.status_code} {response.text}")

    data = response.json()
    results = []

    for video in data.get("videos", []):
        video_files = video.get("video_files", [])
        video_url = video_files[0]["link"] if video_files else ""

        results.append({
            "type": "pexels",
            "url": video_url,
            "description": video.get("user", {}).get("name", "Pexels Creator"),
            "thumbnailUrl": video.get("image", "")
        })

    return results
