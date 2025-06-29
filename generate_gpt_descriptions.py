import openai
import json
import time

# Set your actual OpenAI API key
openai.api_key = "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"

def generate_gpt_description(alt_text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an assistant that writes vivid, creative content descriptions for media."},
                {"role": "user", "content": f"Describe this image for a media catalog: {alt_text}"}
            ],
            temperature=0.7,
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Load existing output.json
with open("output.json", "r") as file:
    data = json.load(file)

# Enhance Pexels image descriptions
for item in data.get("pexels_images", []):
    alt_text = item.get("alt", "An image.")
    description = generate_gpt_description(alt_text)
    item["gpt_description"] = description
    time.sleep(1)  # To avoid hitting rate limits

# Save updated JSON
with open("output.json", "w") as file:
    json.dump(data, file, indent=4)

print("✅ GPT descriptions added to output.json")
