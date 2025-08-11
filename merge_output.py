import json
import os

output_raw = []

# Load YouTube
if os.path.exists("youtube_output.json"):
    with open("youtube_output.json", "r") as f:
        try:
            data = json.load(f)
            output_raw.extend(data)
            print(f"✅ Loaded {len(data)} YouTube videos")
        except Exception as e:
            print(f"❌ Failed to load youtube_output.json: {e}")

# Load TikTok
if os.path.exists("tiktok_output.json"):
    with open("tiktok_output.json", "r") as f:
        try:
            data = json.load(f)
            output_raw.extend(data)
            print(f"✅ Loaded {len(data)} TikTok videos")
        except Exception as e:
            print(f"❌ Failed to load tiktok_output.json: {e}")

# Save to output_raw.json
try:
    with open("output_raw.json", "w") as f:
        json.dump(output_raw, f, indent=2)
    print(f"\n✅ Merged {len(output_raw)} items into output_raw.json successfully.")
except Exception as e:
    print(f"❌ Failed to write output_raw.json: {e}")
