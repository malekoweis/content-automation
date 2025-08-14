import os, io, json, tempfile, subprocess, pathlib, requests
from pydub import AudioSegment
from pydub.generators import Sine
from gtts import gTTS

MIN_VOICE_MS = int(os.getenv("MIN_VOICE_MS","15000"))  # 15s min
MAX_VOICE_MS = int(os.getenv("MAX_VOICE_MS","30000"))  # 30s cap
BG_MUSIC_URL = os.getenv("BG_MUSIC_URL","")
OUT_DIR = pathlib.Path("rendered")
OUT_DIR.mkdir(exist_ok=True)

def sh(cmd, timeout=None):
    subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, timeout=timeout)

def dl(url: str, dest: pathlib.Path) -> bool:
    try:
        if not url: return False
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(dest, "wb") as f:
                for ch in r.iter_content(1024 * 64):
                    if ch: f.write(ch)
        return True
    except Exception:
        return False

def synth_bg(length_ms: int) -> AudioSegment:
    base = Sine(432).to_audio_segment(duration=length_ms).apply_gain(-24)
    overtone = Sine(864).to_audio_segment(duration=length_ms).apply_gain(-32)
    return base.overlay(overtone).fade_in(800).fade_out(1200)

def tts_ar_mp3(text: str, dest: pathlib.Path):
    gTTS(text=text, lang="ar").save(str(dest))

def ffprobe_duration_ms(path: pathlib.Path) -> int:
    try:
        out = subprocess.check_output([
            "ffprobe","-v","error","-select_streams","v:0",
            "-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1", str(path)
        ], stderr=subprocess.STDOUT, text=True).strip()
        sec = float(out)
        return int(sec * 1000)
    except Exception:
        return 16000

def stretch_ffmpeg(in_path: pathlib.Path, out_path: pathlib.Path, factor: float) -> bool:
    if factor <= 0: return False
    f = max(0.5, min(2.0, factor))
    # chain if needed
    filters = []
    remaining = factor
    while remaining < 0.5 or remaining > 2.0:
        step = 0.5 if remaining < 1 else 2.0
        filters.append(f"atempo={step}")
        remaining /= step
    filters.append(f"atempo={remaining}")
    chain = ",".join(filters)
    try:
        sh(["ffmpeg","-y","-i",str(in_path),"-filter:a",chain,str(out_path)])
        return True
    except Exception:
        return False

def fit_to_target(voice: AudioSegment, target_ms: int, tmpdir: pathlib.Path) -> AudioSegment:
    if abs(len(voice) - target_ms) < 800:
        return voice if len(voice) >= target_ms else voice + AudioSegment.silent(duration=target_ms - len(voice))
    factor = target_ms / max(1, len(voice))
    in_path = tmpdir / "v_in.mp3"
    out_path = tmpdir / "v_out.mp3"
    voice.export(in_path, format="mp3")
    if 0.5 <= factor <= 2.0 and stretch_ffmpeg(in_path, out_path, factor):
        try:
            return AudioSegment.from_file(out_path, format="mp3")
        except Exception:
            pass
    # fallback: pad/trim
    return voice + AudioSegment.silent(duration=target_ms - len(voice)) if len(voice) < target_ms else voice[:target_ms]

def mix_audio(voice: AudioSegment, music: AudioSegment) -> AudioSegment:
    voice = voice.normalize()
    music = music.normalize() - 20
    if len(music) < len(voice):
        loops = len(voice) // len(music) + 1
        music = sum([music] * loops)
    music = music[:len(voice)].fade_in(800).fade_out(1200)
    return music.overlay(voice + 4)

def ffmpeg_mux(video_path: pathlib.Path, audio_path: pathlib.Path, out_path: pathlib.Path):
    sh([
        "ffmpeg","-y","-i",str(video_path),"-i",str(audio_path),
        "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","192k",
        "-shortest",str(out_path)
    ])

def process_items(src_json="output.json", limit=5):
    items = json.load(open(src_json,"r",encoding="utf-8"))
    print(f"[TTS] items: {len(items)} (limit={limit})", flush=True)

    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)

        # bg music
        bg_path = tmp / "bg.mp3"
        if dl(BG_MUSIC_URL, bg_path):
            print("[TTS] bg: downloaded", flush=True)
        else:
            print("[TTS] bg: synth", flush=True)
            synth_bg(30000).export(bg_path, format="mp3")
        bg_audio_full = AudioSegment.from_file(bg_path, format="mp3")

        made = 0
        for i, it in enumerate(items):
            if made >= limit: break
            url = (it.get("url") or "").lower()
            if not url.endswith((".mp4",".mov",".m4v",".webm")): continue
            script = (it.get("ai_script") or it.get("ai_caption") or "").strip()
            if not script: continue

            try:
                print(f"[TTS] {made+1}/{limit} download video…", flush=True)
                vid = tmp / f"v{i}.mp4"
                with requests.get(it["url"], stream=True, timeout=60) as r:
                    r.raise_for_status()
                    with open(vid, "wb") as f:
                        for ch in r.iter_content(1024*64):
                            if ch: f.write(ch)

                dur_ms = ffprobe_duration_ms(vid)
                target_ms = max(MIN_VOICE_MS, min(dur_ms, MAX_VOICE_MS))

                print("[TTS] TTS…", flush=True)
                voice_mp3 = tmp / f"voice{i}.mp3"
                tts_ar_mp3(script, voice_mp3)
                voice = AudioSegment.from_file(voice_mp3, format="mp3")
                voice = fit_to_target(voice, target_ms, tmp)

                bg_audio = bg_audio_full[:len(voice)]
                mix = mix_audio(voice, bg_audio)
                mix_path = tmp / f"mix{i}.mp3"
                mix.export(mix_path, format="mp3")

                out = OUT_DIR / f"{i:03d}.mp4"
                print("[TTS] mux…", flush=True)
                ffmpeg_mux(vid, mix_path, out)
                print(f"✅ {out}", flush=True)
                made += 1
            except Exception as e:
                print("skip", i, e, flush=True)

if __name__ == "__main__":
    process_items(limit=int(os.getenv("RENDER_LIMIT","5")))
