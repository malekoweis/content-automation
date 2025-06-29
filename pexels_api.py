import requests

API_KEY = "9qhG3xjHIBzHVXN9aYM4qevD2P9N6aDuDWFlUDl3ZMQjgFqLPWcuKQEa"


def get_pexels_images(query, per_page=5):
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": API_KEY}
    params = {"query": query, "per_page": per_page}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()["photos"]
    else:
        return {"error": response.status_code, "message": response.text}
