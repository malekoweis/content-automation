import json
import openai
import time

# ✅ Insert your real OpenAI key here
openai.api_key = "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"

def describe_with_gpt(prompt):
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

def main():
    with open("output.json", "r") as f:
        data = json.load(f)

    for image in data.get("pexels_images", []):
        print(f"Processing image ID {image['id']}...")
        if "gpt_description" not in image or "Error" in image["gpt_description"]:
            image["gpt_description"] = describe_with_gpt(f"Describe this image: {image['alt']}")
        if image.get("category", "") == "Uncategorized":
            image["category"] = describe_with_gpt(f"What category best fits this image? Description: {image['alt']}")
        if image.get("niche", "") == "unknown":
            image["niche"] = describe_with_gpt(f"What niche does this content fit in? Description: {image['alt']}")
        time.sleep(1)

    for video in data.get("youtube_videos", []) + data.get("tiktok_videos", []):
        print(f"Processing video: {video['url']}...")
        if "gpt_description" not in video or "Error" in video["gpt_description"] or "Skipped" in video["gpt_description"]:
            video["gpt_description"] = describe_with_gpt(f"Generate a content description for this video URL: {video['url']}")
        if video.get("category", "") == "Uncategorized":
            video["category"] = describe_with_gpt(f"What category best fits this video? URL: {video['url']}")
        if video.get("niche", "") == "unknown":
            video["niche"] = describe_with_gpt(f"What niche does this video fit in? URL: {video['url']}")
        time.sleep(1)

    with open("output.json", "w") as f:
        json.dump(data, f, indent=2)

    print("✅ output.json updated.")

if __name__ == "__main__":
    main()
