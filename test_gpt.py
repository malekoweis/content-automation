from openai import OpenAI
from openai.types.chat import ChatCompletionMessage
import os

# ✅ Insert your real API key here
client = OpenAI(api_key="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")

try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # ✅ Use this if gpt-4 isn’t enabled
        messages=[
            {"role": "user", "content": "Say hello from test_gpt.py"}
        ],
        temperature=0.7,
    )

    print("✅ API working. Response:")
    print(response.choices[0].message.content)

except Exception as e:
    print("❌ Error:", e)
