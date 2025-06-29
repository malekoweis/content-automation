import os
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, TextClip

INPUT_FOLDER = "processed_media"
OUTPUT_FOLDER = "final_ready"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def is_video(file):
    return file.lower().endswith(('.mp4', '.mov', '.webm'))

def is_image(file):
    return file.lower().endswith(('.jpg', '.jpeg', '.png'))

def format_video(input_path, output_path):
    clip = VideoFileClip(input_path).subclip(0, min(60, VideoFileClip(input_path).duration))
    clip = clip.resize(height=1280)  # 720x1280 format
    clip = clip.set_position("center")

    # Optional watermark
    watermark = TextClip("via AI Engine", fontsize=40, color='white')
    watermark = watermark.set_position(("center", "bottom")).set_duration(clip.duration)

    final = CompositeVideoClip([clip, watermark])
    final.write_videofile(output_path, codec="libx264", audio_codec="aac")

def format_image(input_path, output_path):
    clip = ImageClip(input_path).set_duration(10).resize(height=1280)
    watermark = TextClip("via AI Engine", fontsize=40, color='white')
    watermark = watermark.set_position(("center", "bottom")).set_duration(clip.duration)
    final = CompositeVideoClip([clip, watermark])
    final.write_videofile(output_path, fps=24, codec="libx264")

def process_all():
    for filename in os.listdir(INPUT_FOLDER):
        input_path = os.path.join(INPUT_FOLDER, filename)
        output_path = os.path.join(OUTPUT_FOLDER, f"formatted_{filename}.mp4")

        try:
            if is_video(filename):
                print(f"Processing video: {filename}")
                format_video(input_path, output_path)
            elif is_image(filename):
                print(f"Processing image: {filename}")
                format_image(input_path, output_path)
            else:
                print(f"Skipping unsupported file: {filename}")
        except Exception as e:
            print(f"Failed to process {filename}: {e}")

if __name__ == "__main__":
    process_all()
