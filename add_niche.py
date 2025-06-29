import json
import openai
import os

openai.api_key = "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"

def detect_niche(description):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": f"What is the most likely niche for this content: '{description}'? Respond with one word like travel, tech, health, food, finance, etc."
            }]
        )
        return response.choices[0].message.content.strip().lower()
    except Exception as e:
        return f"Error: {str(e)}"

with open("output.json", "r") as f:
    data = json.load(f)

for section in ["pexels_images", "youtube_videos", "tiktok_videos"]:
    for item in data.get(section, []):
        desc = item.get("gpt_description", "")
        if desc and not desc.startswith("Error") and not desc.startswith("Skipped"):
            item["niche"] = detect_niche(desc)
        else:
            item["niche"] = "unknown"

with open("output.json", "w") as f:
    json.dump(data, f, indent=2)

print("✅ Niche detection complete and saved to output.json")
