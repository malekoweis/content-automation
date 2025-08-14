# ai_caption.py
import os
from typing import Optional
from openai import OpenAI

SYSTEM_AR = (
    "أنت كاتب تعليقات قصيرة بالفصحى. اكتب جُملة حكيمة موجزة بنبرة هادئة "
    "وملهمة، مناسبة لفيديوهات تيك توك. اجعلها بين 8 و14 كلمة، بلا هاشتاغات "
    "ولا أسماء مستخدمين، وبلا ترقيم زائد."
)

_client: Optional[OpenAI] = None

def _get_client() -> OpenAI:
    global _client
    if _client is None:
        # OpenAI() will auto-read OPENAI_API_KEY from env
        _client = OpenAI()
    return _client

def ai_caption_for(context_text: str, lang: str = "ar", style: str = "formal") -> Optional[str]:
    """
    Returns a concise Arabic wisdom caption (8–14 words) or None if unavailable.
    """
    client = _get_client()
    model = os.getenv("AI_MODEL", "gpt-4o-mini")
    prompt = (
        f"خلفية مختصرة عن المقطع: {context_text}\n"
        f"اللغة: {'العربية الفصحى' if lang=='ar' else lang}\n"
        f"الأسلوب: {'رسمي هادئ وحكيم' if style=='formal' else style}\n"
        "اكتب تعليقاً واحداً فقط."
    )
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_AR},
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
            max_tokens=60,
        )
        text = (resp.choices[0].message.content or "").strip()
        return " ".join(text.split()) if text else None
    except Exception:
        return None
