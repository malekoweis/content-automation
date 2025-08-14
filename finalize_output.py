import json, os
from typing import List, Dict, Any
from ai_text import ai_caption_for, ai_script_for
from video_context import build_grounded_context

USE_AI = (os.getenv("USE_AI","true").lower() == "true")
AI_MAX_CALLS = int(os.getenv("AI_MAX_CALLS","50"))
MAX_AI_ITEMS = int(os.getenv("MAX_AI_ITEMS","12"))
INPUT_JSON = os.getenv("INPUT_JSON","output.json")
OUTPUT_JSON = os.getenv("OUTPUT_JSON","output.json")

def load_items(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    items: List[Dict[str, Any]] = []
    for key in ("youtube_videos","tiktok_videos","pexels_videos","pexels_images","videos","items"):
        if key in data and isinstance(data[key], list):
            items.extend(data[key])
    return items

def normalize_type(it: Dict[str, Any]) -> None:
    t = (it.get("type") or "").lower()
    if "youtube" in t: it["type"] = "youtube"
    elif "tiktok" in t: it["type"] = "tiktok"
    else: it["type"] = "pexels"

def attach_ai(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not USE_AI: return items
    calls = 0
    count = min(MAX_AI_ITEMS, len(items))
    print(f"[AI] processing up to {count} items; max calls {AI_MAX_CALLS}", flush=True)

    for idx, it in enumerate(items[:count], start=1):
        if calls >= AI_MAX_CALLS: break
        desc = it.get("gpt_description") or it.get("description") or ""
        url  = it.get("url","")

        try:
            ctx = build_grounded_context(url, fallback_desc=desc)
        except Exception as e:
            print(f"[AI] ctx failed for item {idx}: {e}; using fallback", flush=True)
            ctx = desc

        if not it.get("ai_script") and calls < AI_MAX_CALLS:
            sc = ai_script_for(ctx)  # 35–60 words
            if sc:
                it["ai_script"] = sc
                calls += 1
                print(f"[AI] {idx}/{count} script ✔ (calls={calls})", flush=True)

        if not it.get("ai_caption") and calls < AI_MAX_CALLS:
            cp = ai_caption_for(ctx)  # 8–14 words
            if cp:
                it["ai_caption"] = cp
                calls += 1
                print(f"[AI] {idx}/{count} caption ✔ (calls={calls})", flush=True)

    print(f"[AI] done (calls used={calls})", flush=True)
    return items

def main():
    items = load_items(INPUT_JSON)
    for it in items: normalize_type(it)
    items = attach_ai(items)
    out = []
    for it in items:
        out.append({
            "type": it.get("type"),
            "url": it.get("url"),
            "description": it.get("description") or it.get("gpt_description") or "",
            "thumbnailUrl": it.get("thumbnailUrl"),
            "ai_caption": it.get("ai_caption"),
            "ai_script": it.get("ai_script"),
        })
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("[AI] wrote", OUTPUT_JSON, flush=True)

if __name__ == "__main__":
    main()
