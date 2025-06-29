import json
import os
import openai

openai.api_key = "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"

def gpt_describe_and_categorize(text):
    try:
        prompt = f"""Given the following content description, categorize it broadly.
Description: "{text}"
Return format: 
{{
  "description": "...",
  "category": "..." 
}}

Categories to choose from: ["Nature", "Travel", "Tutorial", "Tech", "Art", "Entertainment", "News", "Product", "Fashion", "Other"]
"""
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content
        parsed = json.loads(content)
        return parsed["description"], parsed["category"]
    except Exception as e:
        return f"Error: {str(e)}", "Uncategorized"

def update_descriptions_and_categories(media_list):
    for item in media_list:
        desc = item.get("gpt_description", "")
        if not desc or "Skipped" in desc or "Error" in desc:
            item["category"] = "Uncategorized"
            continue
        gpt_text, category = gpt_describe_and_categorize(desc)
        item["gpt_description"] = gpt_text
        item["category"] = category
    return media_list

with open("output.json", "r") as f:
    data = json.load(f)

if "youtube_videos" in data:
    data["youtube_videos"] = update_descriptions_and_categories(data["youtube_videos"])

if "pexels_images" in data:
    data["pexels_images"] = update_descriptions_and_categories(data["pexels_images"])

if "tiktok_videos" in data:
    data["tiktok_videos"] = update_descriptions_and_categories(data["tiktok_videos"])

with open("output.json", "w") as f:
    json.dump(data, f, indent=4)

print("✅ GPT descriptions and categories updated in output.json")
