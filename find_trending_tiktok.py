import requests
import json
from bs4 import BeautifulSoup

def fetch_trending_tiktok_sounds(max_results=10):
    url = "https://www.tiktok.com/music"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    trending = []
    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        if "/music/" in href and len(trending) < max_results:
            title = tag.text.strip()
            sound_url = f"https://www.tiktok.com{href}"
            trending.append({"title": title, "url": sound_url})

    return trending

if __name__ == "__main__":
    trending_sounds = fetch_trending_tiktok_sounds()
    with open("trending_tiktok_sounds.json", "w") as f:
        json.dump(trending_sounds, f, indent=2)

    print("✅ Trending TikTok sounds saved to trending_tiktok_sounds.json")
