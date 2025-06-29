import json
import openai
import random
from pexels_api import get_pexels_images
from youtube_api import search_youtube_videos
from tiktok_api import search_tiktok_videos
from pixel_tracker import track_pixel_events

# Set OpenAI API Key
openai.api_key = "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"

def generate_description(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a creative assistant that describes visual media."},
                {"role": "user", "content": f"Describe this in an engaging, vivid way: {text}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    query = "nature"

    print("\nGetting images from Pexels...")
    images = get_pexels_images(query)
    for img in images:
        print(f"Pexels Image URL: {img['url']}")
        img['gpt_description'] = generate_description(img.get('alt', ''))

    print("\nGetting videos from YouTube...")
    youtube_videos = search_youtube_videos(query)
    for vid in youtube_videos:
        print(f"YouTube Video URL: {vid['url']}")
        vid['gpt_description'] = generate_description(f"YouTube video: {vid['url']}")

    print("\nGetting videos from TikTok...")
    tiktok_videos = search_tiktok_videos(query)
    for vid in tiktok_videos:
        print(f"TikTok Video URL: {vid['url']}")
        vid['gpt_description'] = generate_description(f"TikTok video: {vid['url']}")

    print("\nTracking Pixel Events...")
    import io
    import sys
    old_stdout = sys.stdout
    sys.stdout = mystdout = io.StringIO()
    track_pixel_events()
    sys.stdout = old_stdout
    pixel_logs = mystdout.getvalue().strip().split('\n')

    output = {
        "pexels_images": images,
        "youtube_videos": youtube_videos,
        "tiktok_videos": tiktok_videos,
        "pixel_events": pixel_logs
    }

    with open("output.json", "w") as f:
        json.dump(output, f, indent=4)

    print("\n\u2705 Results saved to output.json")

if __name__ == "__main__":
    main()
