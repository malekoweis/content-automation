from typing import Optional
from openai import OpenAI
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Set OPENAI_API_KEY")
MODEL = os.getenv("AI_MODEL", "gpt-4o-mini")

client = OpenAI(api_key=OPENAI_API_KEY)

SYS_CAPTION_AR = (
    "أنت كاتب تعليقات قصيرة بالفصحى. اكتب جُملة حكيمة موجزة بنبرة هادئة "
    "وملهمة، مناسبة لفيديوهات تيك توك. بين 8 و14 كلمة. دون هاشتاغات أو رموز."
)

SYS_SCRIPT_AR = (
    "أنت كاتب نصوص قصيرة ملهمة بالفصحى لنص صوتي. اكتب فقرة من جملتين إلى ثلاث "
    "جمل بنبرة هادئة وعميقة ومباشرة، بين 35 و60 كلمة، بدون هاشتاغات أو رموز "
    "تعبيرية أو تعداد نقطي. اجعل الأسلوب مناسباً لفيديو مدته 15 ثانية."
)

def _chat(system: str, user: str) -> Optional[str]:
    try:
        r = client.chat.completions.create(
            model=MODEL,
            messages=[{"role":"system","content":system},
                      {"role":"user","content":user}],
            temperature=0.7,
            max_tokens=220,
        )
        txt = (r.choices[0].message.content or "").strip()
        return " ".join(txt.split()) if txt else None
    except Exception:
        return None

def ai_caption_for(context_text: str) -> Optional[str]:
    return _chat(SYS_CAPTION_AR, f"خلفية المقطع: {context_text}\nأعطني تعليقاً واحداً فقط.")

def ai_script_for(context_text: str) -> Optional[str]:
    return _chat(SYS_SCRIPT_AR, f"خلفية المقطع: {context_text}\nأعطني فقرة واحدة فقط.")
