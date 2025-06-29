import json
import os

INPUT_FILE = "output.json"
FINAL_FILE = "final_output.json"

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Input file not found: {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        new_data = json.load(f)

    if os.path.exists(FINAL_FILE):
        with open(FINAL_FILE, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = {}
    else:
        existing_data = {}

    for section in ["pexels_images", "youtube_videos", "tiktok_videos", "pixel_events"]:
        new_items = new_data.get(section, [])
        if section not in existing_data:
            existing_data[section] = []

        # Merge while avoiding duplicates
        if isinstance(new_items, list) and isinstance(existing_data[section], list):
            if section == "pixel_events":
                # Items are strings, not dicts
                existing_set = set(existing_data[section])
                for item in new_items:
                    if item not in existing_set:
                        existing_data[section].append(item)
            else:
                # Items are dicts with "id" or "url"
                existing_ids = {
                    str(item.get("id") or item.get("url"))
                    for item in existing_data[section]
                    if isinstance(item, dict)
                }
                for item in new_items:
                    if isinstance(item, dict):
                        identifier = str(item.get("id") or item.get("url"))
                        if identifier not in existing_ids:
                            existing_data[section].append(item)
        else:
            existing_data[section] = new_items

    with open(FINAL_FILE, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Finalized data written to: {FINAL_FILE}")

if __name__ == "__main__":
    main()
