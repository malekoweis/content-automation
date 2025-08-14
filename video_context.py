import os, tempfile, pathlib, subprocess
from typing import List, Optional, Tuple
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Set OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def _run(cmd: list, timeout: int = 90):
    subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, timeout=timeout)

def extract_frames_and_audio(video_url: str, seconds: int = 12, frames: int = 3) -> Tuple[List[bytes], Optional[bytes]]:
    """
    Stream just the first `seconds` from URL. Try fast copy, fallback to re-encode.
    Returns (list_of_jpegs, mp3_bytes_or_None). Never throws.
    """
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        head = tmp / "head.mp4"

        # 1) Try fast copy
        try:
            _run(["ffmpeg","-y","-ss","0","-t",str(seconds),"-i",video_url,"-c","copy",str(head)], timeout=90)
        except Exception:
            # 2) Fallback: re-encode (more robust)
            try:
                _run(["ffmpeg","-y","-ss","0","-t",str(seconds),"-i",video_url,"-c:v","libx264","-an",str(head)], timeout=120)
            except Exception:
                return [], None

        # Extract frames
        try:
            fps = max(0.2, frames / max(1, seconds))
            _run(["ffmpeg","-y","-i",str(head),"-vf",f"fps={fps}","-q:v","2",str(tmp/"frame_%02d.jpg")], timeout=60)
            jpgs = [p.read_bytes() for p in sorted(tmp.glob("frame_*.jpg"))[:frames]]
        except Exception:
            jpgs = []

        # Extract audio (optional)
        mp3 = None
        try:
            aout = tmp / "audio.mp3"
            _run(["ffmpeg","-y","-i",str(head),"-vn","-ac","1","-ar","16000","-b:a","64k",str(aout)], timeout=60)
            if aout.exists() and aout.stat().st_size > 1024:
                mp3 = aout.read_bytes()
        except Exception:
            mp3 = None

        return jpgs, mp3

def b64_data_url(jpeg_bytes: bytes) -> str:
    import base64
    return "data:image/jpeg;base64," + base64.b64encode(jpeg_bytes).decode("utf-8")

def transcribe_whisper(mp3_bytes: bytes) -> Optional[str]:
    try:
        from io import BytesIO
        bio = BytesIO(mp3_bytes); bio.name = "audio.mp3"
        r = client.audio.transcriptions.create(model="whisper-1", file=bio, response_format="text", temperature=0)
        text = (r or "").strip()
        return text if text else None
    except Exception:
        return None

def build_grounded_context(video_url: str, fallback_desc: str = "") -> str:
    """
    Safe: if any step fails, returns fallback_desc.
    """
    try:
        frames, mp3 = extract_frames_and_audio(video_url, seconds=12, frames=3)
    except Exception:
        frames, mp3 = [], None

    transcript = None
    if mp3:
        try:
            transcript = transcribe_whisper(mp3)
        except Exception:
            transcript = None

    messages = [
        {"role":"system","content":
         "حلّل الصور بدقة دون افتراضات. صف ما يظهر فعلاً: الأشخاص/الأشياء/الحركة/المكان/المزاج. "
         "اكتب وصفاً قصيراً بالعربية (سطران كحد أقصى) مع إبراز المغزى. تجنب الأسماء التجارية."}
    ]

    parts: list = []
    if frames:
        parts.append({"type":"text","text":"هذه لقطات من الفيديو:"})
        for jb in frames:
            parts.append({"type":"input_image","image_url":{"url": b64_data_url(jb)}})
    if transcript:
        parts.append({"type":"text","text": f"تفريغ صوتي مختصر: {transcript}"})
    if fallback_desc:
        parts.append({"type":"text","text": f"وصف المصدر: {fallback_desc[:220]}"} )
    if not parts:
        return fallback_desc or ""

    try:
        r = client.chat.completions.create(
            model=os.getenv("AI_MODEL","gpt-4o-mini"),
            messages=[{"role":"user","content": parts}],
            temperature=0.4,
            max_tokens=180
        )
        txt = (r.choices[0].message.content or "").strip()
        return " ".join(txt.split()) if txt else (fallback_desc or "")
    except Exception:
        return fallback_desc or ""
