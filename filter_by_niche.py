import json

TARGET_NICHES = ["tech", "travel"]  # ✅ Edit this list to filter by different niches

with open("output.json", "r") as f:
    data = json.load(f)

filtered = {
    "pexels_images": [],
    "youtube_videos": [],
    "tiktok_videos": []
}

for section in filtered:
    for item in data.get(section, []):
        if item.get("niche", "") in TARGET_NICHES:
            filtered[section].append(item)

with open("filtered_output.json", "w") as f:
    json.dump(filtered, f, indent=2)

print("✅ Filtered content saved to filtered_output.json")
