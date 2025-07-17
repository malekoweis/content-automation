import json
from pexels_api import get_pexels_images
from youtube_fetcher import fetch_youtube_videos  # ✅ FIXED: correct function
from tiktok_fetcher import get_tiktok_videos
from pixel_tracker import track_pixel_events
from push_to_github import push_output

def main():
    print("📸 Getting images from Pexels...")
    pexels_images = get_pexels_images()
    print(f"✅ Pexels images: {len(pexels_images)}")

    print("▶️ Getting videos from YouTube...")
    youtube_videos = fetch_youtube_videos()
    print(f"✅ YouTube videos: {len(youtube_videos)}")

    print("🎵 Getting videos from TikTok...")
    tiktok_videos = get_tiktok_videos()
    print(f"✅ TikTok videos: {len(tiktok_videos)}")

    print("📍 Tracking Pixel Events...")
    pixel_events = track_pixel_events()
    print(f"✅ Pixel events: {len(pixel_events)}")

    # Merge all content
    all_content = pexels_images + youtube_videos + tiktok_videos + pixel_events

    # Save to output.json
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(all_content, f, ensure_ascii=False, indent=2)

    print(f"💾 Saved output.json with {len(all_content)} items.")

    # Push to GitHub
    print("🚀 Uploading to GitHub...")
    push_output()
    print("✅ Script finished.")

if __name__ == "__main__":
    main()
