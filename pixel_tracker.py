import json
import random
import time

def track_pixels(data):
    """
    Simulate pixel tracking by adding a tracking_id and timestamp to each item.
    """
    for item in data:
        item['tracking'] = {
            "tracking_id": f"pxl_{random.randint(100000, 999999)}",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    print(f"✅ Tracking Pixel Events...")
    return data
