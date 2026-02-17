import os
import requests

MAPBOX_FORWARD_URL = "https://api.mapbox.com/search/geocode/v6/forward"

def geocode_address(address, city):
    """
    return (lat, lng) o retorna None si no encuentra nada.
    """
    token = os.getenv("MAPBOX_ACCESS_TOKEN")
    if not token:
        raise Exception("MAPBOX_ACCESS_TOKEN missing in .env")

    query = f"{address}, {city}"

    params = {
        "q": query,
        "limit": 1,
        "access_token": token
    }

    res = requests.get(MAPBOX_FORWARD_URL, params=params, timeout=10)

    if res.status_code != 200:
        raise Exception(f"Mapbox error {res.status_code}: {res.text}")

    data = res.json()
    features = data.get("features", [])

    if not features:
        return None

    # Mapbox RETURN [lng, lat]
    lng, lat = features[0]["geometry"]["coordinates"]
    print("Mapbox coords:", lat, lng)

    return (lat, lng)
