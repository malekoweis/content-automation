import os, json, time, random, pathlib, datetime, requests

BASE_DIR = pathlib.Path(__file__).resolve().parent
OUT = BASE_DIR / "output.json"
HISTORY = BASE_DIR / "history.json"

YT_API_KEY = os.environ.get("YT_API_KEY")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")  # optional
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")      # optional

TARGET = 32
HISTORY_MAX = 500

TOPICS = [
    "ai news", "fitness", "travel", "street food", "football highlights",
    "coding tips", "photography", "gaming clips", "music freestyle",
    "startup ideas", "fashion", "nature", "satisfying", "productivity",
]

def now_utc():
    return datetime.datetime.utcnow()

def iso_24h_ago():
    return (now_utc() - datetime.timedelta(hours=24)).replace(microsecond=0).isoformat("T") + "Z"

def load_history():
    if HISTORY.exists():
        try:
            return set(json.loads(HISTORY.read_text(encoding="utf-8")))
        except Exception:
            return set()
    return set()

def save_history(urls:set):
    # cap history size
    arr = list(urls)
    if len(arr) > HISTORY_MAX:
        arr = arr[-HISTORY_MAX:]
    HISTORY.write_text(json.dumps(arr, ensure_ascii=False, indent=2), encoding="utf-8")

def choose_topic():
    # deterministic per run (helps debugging) but still rotates
    random.seed(int(time.time() // 3600))
    return random.choice(TOPICS)

def fetch_youtube_recent(topic, max_results=20):
    if not YT_API_KEY:
        return []
    print(f"▶️ Getting videos from YouTube… topic='{topic}'", flush=True)
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": YT_API_KEY,
        "q": topic,
        "part": "snippet",
        "type": "video",
        "maxResults": max_results,
        "order": "date",
        "publishedAfter": iso_24h_ago(),
        # "regionCode": "US",  # optionally set
        # "relevanceLanguage": "en",
        "safeSearch": "none",
    }
    try:
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        items = []
        for it in data.get("items", []):
            vid = it.get("id", {}).get("videoId")
            sn = it.get("snippet", {})
            if not vid:
                continue
            items.append({
                "type": "youtube",
                "url": f"https://www.youtube.com/watch?v={vid}",
                "description": sn.get("title"),
                "thumbnailUrl": (sn.get("thumbnails", {}).get("medium", {}) or sn.get("thumbnails", {}).get("default", {})).get("url")
            })
        print(f"✅ YouTube videos: {len(items)}", flush=True)
        return items
    except Exception as e:
        print(f"⚠️ YouTube fetch error: {e}", flush=True)
        return []

def fetch_pexels_videos(topic, max_results=12):
    if not PEXELS_API_KEY:
        return []
    print(f"📸 Getting videos from Pexels… topic='{topic}'", flush=True)
    headers = {"Authorization": PEXELS_API_KEY}
    url = "https://api.pexels.com/videos/search"
    params = {"query": topic, "per_page": max_results}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        items = []
        for v in data.get("videos", []):
            files = v.get("video_files", [])
            files.sort(key=lambda f: f.get("width", 0), reverse=True)
            link = files[0]["link"] if files else None
            if not link:
                continue
            items.append({
                "type": "pexels",
                "url": link,
                "description": v.get("user", {}).get("name") or topic,
                "thumbnailUrl": v.get("image"),
            })
        print(f"✅ Pexels videos: {len(items)}", flush=True)
        return items
    except Exception as e:
        print(f"⚠️ Pexels fetch error: {e}", flush=True)
        return []

def fetch_tiktok_trending(max_results=12):
    if not RAPIDAPI_KEY:
        return []
    print("🎵 Getting videos from TikTok (RapidAPI)…", flush=True)
    # NOTE: RapidAPI hosts vary; this one is commonly available. Adjust if your plan uses a different host.
    url = "https://tiktok-scraper7.p.rapidapi.com/feed/trending"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "tiktok-scraper7.p.rapidapi.com",
    }
    params = {"region": "US", "count": max_results}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        items = []
        for it in (data.get("data") or data.get("aweme_list") or []):
            # best effort to normalize fields across providers
            play = it.get("play") or it.get("video", {}).get("play_addr", {}).get("url_list", [None])[0]
            desc = it.get("title") or it.get("desc") or "TikTok video"
            thumb = it.get("origin_cover") or it.get("video", {}).get("origin_cover", {}).get("url_list", [None])[0]
            if not play:
                continue
            items.append({
                "type": "tiktok",
                "url": play,
                "description": desc,
                "thumbnailUrl": thumb
            })
        print(f"✅ TikTok videos: {len(items)}", flush=True)
        return items
    except Exception as e:
        print(f"⚠️ TikTok fetch error: {e}", flush=True)
        return []

def write_output(items):
    random.shuffle(items)
    OUT.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"💾 Saved output.json with {len(items)} items.", flush=True)

def main():
    topic = choose_topic()
    all_items = []

    # Fetch from providers (each is optional/safe)
    all_items += fetch_pexels_videos(topic, max_results=12)
    all_items += fetch_youtube_recent(topic, max_results=16)
    all_items += fetch_tiktok_trending(max_results=16)

    # Dedupe by URL
    seen = set()
    uniq = []
    for it in all_items:
        u = it.get("url")
        if not u or u in seen:
            continue
        seen.add(u)
        uniq.append(it)

    # Against run history: prefer items not served recently
    history = load_history()
    fresh = [it for it in uniq if it["url"] not in history]

    # If we don't have enough, fill from the rest
    result = fresh[:TARGET]
    if len(result) < TARGET:
        for it in uniq:
            if it["url"] in {x["url"] for x in result}:
                continue
            result.append(it)
            if len(result) >= TARGET:
                break

    # Persist history
    new_history = list(history) + [it["url"] for it in result]
    save_history(set(new_history))

    # Final write
    write_output(result)

    # (Optional) also print a short GitHub upload note if you have a separate uploader
    print("✅ Script finished.", flush=True)

if __name__ == "__main__":
    main()
