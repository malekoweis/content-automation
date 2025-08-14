import json
import os
from typing import List, Dict, Any

from config import USE_AI, AI_MAX_CALLS, LANG, STYLE
from ai_caption import ai_caption_for

INPUT_JSON = os.getenv("INPUT_JSON", "output.json")        # source merged data
OUTPUT_JSON = os.getenv("OUTPUT_JSON", "output.json")      # overwrite by default

def load_items(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Accept either a flat list or a dict with sections
    if isinstance(data, list):
        return data
    items: List[Dict[str, Any]] = []
    for key in ("youtube_videos", "tiktok_videos", "pexels_videos", "pexels_images", "videos", "items"):
        if key in data and isinstance(data[key], list):
            items.extend(data[key])
    return items

def summarize_for_prompt(item: Dict[str, Any]) -> str:
    t = item.get("type", "")
    desc = item.get("gpt_description") or item.get("description") or ""
    url = item.get("url", "")
    brief = desc[:220]
    topic_hint = {
        "youtube": "لقطات ملهمة أو مشهد قصصي",
        "tiktok": "لقطة قصيرة وحيوية",
        "pexels": "مقطع بصري هادئ وجمالي",
        "pexels_image": "صورة ملهمة",
    }.get(t, "مقطع بصري")
    return f"{topic_hint}. الوصف: {brief}. الرابط للاستئناس فقط: {url}"

def attach_ai_captions(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not USE_AI:
        return items

    calls = 0
    for it in items:
        if calls >= AI_MAX_CALLS:
            break
        if not it.get("ai_caption"):
            ctx = summarize_for_prompt(it)
            cap = ai_caption_for(ctx, lang=LANG, style=STYLE)
            if cap:
                it["ai_caption"] = cap
                calls += 1
    return items

def normalize_type(it: Dict[str, Any]) -> None:
    # unify types into: 'youtube' | 'tiktok' | 'pexels'
    t = (it.get("type") or "").lower()
    if "youtube" in t:
        it["type"] = "youtube"
    elif "tiktok" in t:
        it["type"] = "tiktok"
    else:
        it["type"] = "pexels"

def main():
    items = load_items(INPUT_JSON)
    for it in items:
        normalize_type(it)
    items = attach_ai_captions(items)

    # ensure minimal fields
    cleaned = []
    for it in items:
        cleaned.append({
            "type": it.get("type"),
            "url": it.get("url"),
            "description": it.get("description") or it.get("gpt_description") or "",
            "thumbnailUrl": it.get("thumbnailUrl"),
            "ai_caption": it.get("ai_caption"),
        })

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
