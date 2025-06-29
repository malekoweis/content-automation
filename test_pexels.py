from pexels_api import get_pexels_images

# Test the Pexels API with a simple query
query = "nature"
images = get_pexels_images(query)

if isinstance(images, dict) and "error" in images:
    print("Error:", images["message"])
else:
    for image in images:
        print("Image URL:", image["url"])
