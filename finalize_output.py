import json

# Load original data
with open("filtered_output_fixed.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Build flat list
flat_output = []

# Extract YouTube
for video in data.get("youtube_videos", []):
    flat_output.append({
        "url": video["url"],
        "type": "youtube",
        "thumbnailUrl": video.get("thumbnailUrl", "")
    })

# Extract TikTok
for video in data.get("tiktok_videos", []):
    flat_output.append({
        "url": video["url"],
        "type": "tiktok",
        "thumbnailUrl": video.get("thumbnailUrl", "")
    })

# Extract Pexels
for image in data.get("pexels_images", []):
    flat_output.append({
        "url": image.get("url", ""),
        "type": "pexels",
        "thumbnailUrl": image.get("src", {}).get("medium", "")
    })

# Write to final output
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(flat_output, f, indent=2)

print("✅ output.json written successfully with", len(flat_output), "items")
