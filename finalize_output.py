import json

def finalize_output(data):
    """
    Finalizes the content by saving the data to output.json
    in a nicely formatted way.
    """
    try:
        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ output.json written successfully with {len(data)} items")
    except Exception as e:
        print(f"❌ Failed to write output.json: {e}")
