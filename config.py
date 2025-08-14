import os

USE_AI = os.getenv("USE_AI", "true").lower() == "true"
AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini")
AI_MAX_CALLS = int(os.getenv("AI_MAX_CALLS", "50"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LANG = os.getenv("AI_CAPTION_LANG", "ar")  # 'ar' Formal Standard Arabic
STYLE = os.getenv("AI_CAPTION_STYLE", "formal")
