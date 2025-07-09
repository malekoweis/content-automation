import requests

# ⚠️ Your actual Pexels API key — REPLACE THIS with a secure value for production
PEXELS_API_KEY = "563492ad6f91700001000001e5cbdcc99ce54b3e9458d1b0c0735083"

def get_pexels_videos(query="nature", per_page=5):
    url = "https://api.pexels.com/videos/search"
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    params = {
        "query": query,
        "per_page": per_page
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        results = []
        for video in data.get("videos", []):
            results.append({
                "type": "Pexels",
                "url": video["video_files"][0]["link"],
                "thumbnailUrl": video.get("image", ""),
                "description": video.get("user", {}).get("name", "Pexels Video")
            })

        return results

    except Exception as e:
        print(f"❌ Failed to fetch videos from Pexels: {e}")
        return []
