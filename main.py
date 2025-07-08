import json
from finalize_output import finalize_output
from pixel_tracker import track_pixels
from pexels_api import get_pexels_videos
from youtube_api import get_youtube_videos
from tiktok_api import get_tiktok_videos
import push_to_github

def main():
    print("Getting images from Pexels...")
    pexels_videos = get_pexels_videos()

    print("Getting videos from YouTube...")
    youtube_videos = get_youtube_videos()

    print("Getting videos from TikTok...")
    tiktok_videos = get_tiktok_videos()

    print("Tracking Pixel Events...")
    all_videos = pexels_videos + youtube_videos + tiktok_videos
    tracked_videos = track_pixels(all_videos)

    print("✅ Results saved to output.json")
    finalize_output(tracked_videos)

    print("🔄 Attempting to push output.json to GitHub...")
    push_to_github.push_output()

    print("✅ Script finished.")

if __name__ == "__main__":
    main()
