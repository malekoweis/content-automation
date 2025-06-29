import random

def track_pixel_events():
    # Simulate tracking pixel events
    events = [
        {"event": "PageView", "timestamp": "2025-06-16T12:00:00Z"},
        {"event": "ViewContent", "timestamp": "2025-06-16T12:05:00Z"},
        {"event": "AddToCart", "timestamp": "2025-06-16T12:10:00Z"},
        {"event": "Purchase", "timestamp": "2025-06-16T12:15:00Z"},
    ]
    for event in events:
        print(f"Tracked Event: {event['event']} at {event['timestamp']}")

if __name__ == "__main__":
    track_pixel_events()
