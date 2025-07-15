import json
from pexels_api import get_pexels_images
from youtube_fetcher import get_youtube_videos
from tiktok_fetcher import get_tiktok_videos
from pixel_tracker import track_pixel_events
from push_to_github import push_output

def main():
    print("Getting images from Pexels...")
    pexels_images = get_pexels_images()

    print("Getting videos from YouTube...")
    youtube_videos = get_youtube_videos()

    print("Getting videos from TikTok...")
    tiktok_videos = get_tiktok_videos()

    print("Tracking Pixel Events...")
    pixel_events = track_pixel_events()
    print("✅ Tracking Pixel Events...")

    # Merge all content
    all_content = pexels_images + youtube_videos + tiktok_videos + pixel_events

    # Save to output.json
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(all_content, f, ensure_ascii=False, indent=2)

    print(f"✅ Results saved to output.json")
    print(f"✅ output.json written successfully with {len(all_content)} items")

    # Upload using GitHub API
    print("🔄 Attempting to push output.json to GitHub...")
    push_output()
    print("✅ Script finished.")

if __name__ == "__main__":
    main()
