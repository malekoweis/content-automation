import os, json, time, random, pathlib, datetime, requests

BASE_DIR = pathlib.Path(__file__).resolve().parent
OUT = BASE_DIR / "output.json"
HISTORY = BASE_DIR / "history.json"

YT_API_KEY = os.environ.get("YT_API_KEY")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")  # optional
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.environ.get("RAPIDAPI_HOST")      # optional

TARGET = 32
HISTORY_MAX = 800

TOPICS = [
    "ai news", "fitness", "travel", "street food", "football highlights",
    "coding tips", "photography", "gaming clips", "music freestyle",
    "startup ideas", "fashion", "nature", "satisfying", "productivity",
    "unboxing", "android tips", "design inspo"
]

def now_utc():
    return datetime.datetime.utcnow()

def iso_hours_ago(h):
    return (now_utc() - datetime.timedelta(hours=h)).replace(microsecond=0).isoformat("T") + "Z"

def load_history():
    if HISTORY.exists():
        try:
            arr = json.loads(HISTORY.read_text(encoding="utf-8"))
            return list(arr)[-HISTORY_MAX:]
        except Exception:
            return []
    return []

def save_history(hist):
    hist = list(dict.fromkeys(hist))[-HISTORY_MAX:]
    HISTORY.write_text(json.dumps(hist, ensure_ascii=False, indent=2), encoding="utf-8")

def choose_topic():
    # rotate topic hourly so it changes naturally
    random.seed(int(time.time() // 3600))
    return random.choice(TOPICS)

def fetch_youtube_recent(topic, max_results=20):
    if not YT_API_KEY:
        print("YouTube: missing YT_API_KEY; skipping", flush=True)
        return []
    print(f"▶️ YouTube: topic='{topic}'", flush=True)
    base = "https://www.googleapis.com/youtube/v3/search"
    attempts = [
        {"publishedAfter": iso_hours_ago(24), "label": "last24h"},
        {"publishedAfter": iso_hours_ago(72), "label": "last72h"},
        {"publishedAfter": None,             "label": "latest"},
    ]
    for attempt in attempts:
        params = {
            "key": YT_API_KEY,
            "q": topic,
            "part": "snippet",
            "type": "video",
            "maxResults": max_results,
            "order": "date",
            "safeSearch": "none",
        }
        if attempt["publishedAfter"]:
            params["publishedAfter"] = attempt["publishedAfter"]
        try:
            r = requests.get(base, params=params, timeout=20)
            r.raise_for_status()
            data = r.json()
            items = []
            for it in data.get("items", []):
                vid = it.get("id", {}).get("videoId")
                sn = it.get("snippet", {})
                if not vid:
                    continue
                thumb = (sn.get("thumbnails", {}).get("medium", {}) or sn.get("thumbnails", {}).get("default", {})).get("url")
                items.append({
                    "type": "youtube",
                    "url": f"https://www.youtube.com/watch?v={vid}",
                    "description": sn.get("title"),
                    "thumbnailUrl": thumb
                })
            print(f"✅ YouTube({attempt['label']}): {len(items)}", flush=True)
            if items:
                return items
        except Exception as e:
            print(f"⚠️ YouTube error ({attempt['label']}): {e}", flush=True)
    return []

def fetch_pexels_videos(topic, max_results=12):
    if not PEXELS_API_KEY:
        print("Pexels: missing PEXELS_API_KEY; skipping", flush=True)
        return []
    page = random.randint(1, 50)  # rotate page to vary results
    print(f"📸 Pexels: topic='{topic}', page={page}", flush=True)
    headers = {"Authorization": PEXELS_API_KEY}
    url = "https://api.pexels.com/videos/search"
    params = {"query": topic, "per_page": max_results, "page": page}
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
        print(f"✅ Pexels: {len(items)}", flush=True)
        return items
    except Exception as e:
        print(f"⚠️ Pexels error: {e}", flush=True)
        return []

def fetch_tiktok_trending():
    if not RAPIDAPI_KEY:
        print("TikTok: missing RAPIDAPI_KEY; skipping", flush=True)
        return []
    # Hosts & paths to try (first uses RAPIDAPI_HOST if provided)
    host_candidates = []
    if RAPIDAPI_HOST:
        host_candidates.append(RAPIDAPI_HOST.strip())
    host_candidates += ["tiktok-scraper7.p.rapidapi.com", "tiktok-scraper2.p.rapidapi.com", "tiktok-video-no-watermark2.p.rapidapi.com"]
    host_candidates = list(dict.fromkeys(host_candidates))  # dedupe, keep order

    # Common paths used by different providers
    path_candidates = ["/feed/trending", "/trending", "/trending/feed"]

    region = random.choice(["US","GB","DE","FR","JP","IN","BR","CA"])
    count = random.randint(8, 18)

    for host in host_candidates:
        for path in path_candidates:
            try:
                url = f"https://{host}{path}"
                headers = {"X-RapidAPI-Key": RAPIDAPI_KEY, "X-RapidAPI-Host": host}
                params = {"region": region, "count": count}
                print(f"🎵 TikTok: host={host} path={path} region={region} count={count}", flush=True)
                r = requests.get(url, headers=headers, params=params, timeout=20)
                if r.status_code == 404:
                    print("   -> 404 on this host/path, trying next…", flush=True)
                    continue
                r.raise_for_status()
                data = r.json()
                # Normalize a few common shapes
                raw = data.get("data") or data.get("aweme_list") or data.get("results") or data.get("itemList") or []
                items = []
                for it in raw:
                    play = it.get("play") or it.get("video", {}).get("play_addr", {}).get("url_list", [None])[0]
                    desc = it.get("title") or it.get("desc") or "TikTok video"
                    thumb = it.get("origin_cover") or it.get("video", {}).get("origin_cover", {}).get("url_list", [None])[0]
                    if not play:
                        continue
                    items.append({"type": "tiktok", "url": play, "description": desc, "thumbnailUrl": thumb})
                print(f"✅ TikTok via {host}{path}: {len(items)}", flush=True)
                if items:
                    return items
            except Exception as e:
                print(f"⚠️ TikTok error via {host}{path}: {e}", flush=True)
                continue
    return []
    # Prefer explicit host, else try common ones
    hosts = []
    if RAPIDAPI_HOST:
        hosts.append((RAPIDAPI_HOST, "/feed/trending"))
    hosts += [
        ("tiktok-scraper7.p.rapidapi.com", "/feed/trending"),
        ("tiktok-scraper2.p.rapidapi.com", "/trending"),
    ]
    region = random.choice(["US","GB","DE","FR","JP","IN","BR","CA"])
    count = random.randint(8, 18)

    for host, path in hosts:
        try:
            url = f"https://{host}{path}"
            headers = {"X-RapidAPI-Key": RAPIDAPI_KEY, "X-RapidAPI-Host": host}
            params = {"region": region, "count": count}
            print(f"🎵 TikTok: host={host} region={region} count={count}", flush=True)
            r = requests.get(url, headers=headers, params=params, timeout=20)
            r.raise_for_status()
            data = r.json()
            # Normalize common response shapes
            raw = data.get("data") or data.get("aweme_list") or data.get("results") or data.get("itemList") or []
            items = []
            for it in raw:
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
            print(f"✅ TikTok via {host}: {len(items)}", flush=True)
            if items:
                return items
        except Exception as e:
            print(f"⚠️ TikTok error via {host}: {e}", flush=True)
            continue
    return []
    region = random.choice(["US","GB","DE","FR","JP","IN","BR","CA"])
    count = random.randint(8, 18)
    print(f"🎵 TikTok: region={region} count={count}", flush=True)
    url = "https://tiktok-scraper7.p.rapidapi.com/feed/trending"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "tiktok-scraper7.p.rapidapi.com",
    }
    params = {"region": region, "count": count}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        raw = data.get("data") or data.get("aweme_list") or []
        items = []
        for it in raw:
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
        print(f"✅ TikTok: {len(items)}", flush=True)
        return items
    except Exception as e:
        print(f"⚠️ TikTok error: {e}", flush=True)
        return []

def write_output(items):
    random.shuffle(items)
    OUT.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"💾 Saved output.json with {len(items)} items.", flush=True)

def main():
    topic = choose_topic()
    print(f"🧭 RUN TOPIC: {topic}", flush=True)

    # gather
    all_items = []
    all_items += fetch_pexels_videos(topic, max_results=14)
    all_items += fetch_youtube_recent(topic, max_results=18)
    # Prefer explicit by-URL flow for scraper7; fallback to trending finder if configured

    tt_by_url = fetch_tiktok_by_urls()

    all_items += tt_by_url

    if not tt_by_url:

        try:

            all_items += fetch_tiktok_trending()

        except NameError:

            print("TikTok trending fetcher not available; only by-URL mode is supported.", flush=True)
# dedupe by URL
    seen = set()
    uniq = []
    for it in all_items:
        u = it.get("url")
        if not u or u in seen:
            continue
        seen.add(u)
        uniq.append(it)

    # history-based rotation
    history = load_history()
    hist_set = set(history)
    fresh = [it for it in uniq if it["url"] not in hist_set]

    result = []
    result.extend(fresh[:TARGET])
    if len(result) < TARGET:
        for it in uniq:
            if len(result) >= TARGET:
                break
            if it["url"] in {x["url"] for x in result}:
                continue
            result.append(it)

    # update history
    new_hist = history + [it["url"] for it in result]
    save_history(new_hist)

    # write
    write_output(result)
    print("✅ Script finished.", flush=True)

if __name__ == "__main__":
    main()


def fetch_tiktok_by_urls():
    """
    Uses the 'tiktok-scraper7' style endpoint:
      GET https://{host}/?url=<tiktok video url>&hd=1
    Reads list of video page URLs from TIKTOK_VIDEO_URLS (comma or newline separated).
    Returns normalized items [{type,url,description,thumbnailUrl}, ...].
    """
    if not RAPIDAPI_KEY:
        print("TikTok by URLs: missing RAPIDAPI_KEY; skipping", flush=True)
        return []
    if not TIKTOK_VIDEO_URLS:
        print("TikTok by URLs: TIKTOK_VIDEO_URLS not set; skipping", flush=True)
        return []

    host = (RAPIDAPI_HOST or "tiktok-scraper7.p.rapidapi.com").strip()
    base = f"https://{host}/"

    # split on comma/newline and strip
    raw_urls = [u.strip() for u in TIKTOK_VIDEO_URLS.replace("\\n", ",").split(",")]
    urls = [u for u in raw_urls if u.startswith("http")]

    out = []
    for u in urls:
        try:
            params = {"url": u, "hd": "1"}
            headers = {
                "X-RapidAPI-Key": RAPIDAPI_KEY,
                "X-RapidAPI-Host": host,
            }
            print(f"🎵 TikTok by-url: host={host} url={u}", flush=True)
            r = requests.get(base, headers=headers, params=params, timeout=20)
            r.raise_for_status()
            data = r.json()

            # Many providers return a 'data' object with play/nowm/url, title, cover
            d = data.get("data") if isinstance(data, dict) else None
            play = None
            thumb = None
            title = None
            if isinstance(d, dict):
                play = d.get("play") or d.get("hdplay") or d.get("nowm") or d.get("url")
                thumb = d.get("cover") or d.get("origin_cover")
                title = d.get("title") or d.get("desc") or "TikTok video"
            # fallback shapes
            if not play and isinstance(data, dict):
                play = data.get("url") or data.get("nowm")
                thumb = thumb or data.get("cover") or data.get("thumbnail")
                title = title or data.get("title") or data.get("desc")

            if not play:
                print("   -> no playable URL found in response, skipping", flush=True)
                continue

            out.append({
                "type": "tiktok",
                "url": play,
                "description": title or u,
                "thumbnailUrl": thumb
            })
        except Exception as e:
            print(f"⚠️ TikTok by-url error for {u}: {e}", flush=True)
            continue

    print(f"✅ TikTok by URLs: {len(out)}", flush=True)
    return out
