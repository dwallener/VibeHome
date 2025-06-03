import http.client
import json
import time

# ZIP → (lat, lon)
ZIP_LAT_LON = {
    "33130": (25.7683, -80.2058),
    "33131": (25.7634, -80.1897),
    "33127": (25.8135, -80.2027),
    "33137": (25.8161, -80.1903),
    "33129": (25.7510, -80.2106),
    "33133": (25.7311, -80.2441),
    "33134": (25.7505, -80.2784),
    "33149": (25.6926, -80.1625),
    "33139": (25.7828, -80.1341),
    "33141": (25.8531, -80.1326),
    "33154": (25.8872, -80.1260),
    "33165": (25.7343, -80.3611),
    "33176": (25.6584, -80.3615),
    "33156": (25.6612, -80.3046),
    "33157": (25.6059, -80.3486),
    "33189": (25.5707, -80.3576),
    "33138": (25.8558, -80.1812),
    "33172": (25.7884, -80.3690),
    "33175": (25.7330, -80.4076),
    "33135": (25.7688, -80.2363),
    "33142": (25.8131, -80.2411),
    "33147": (25.8517, -80.2374),
    "33054": (25.9100, -80.2543),
    "33012": (25.8655, -80.3007),
    "33150": (25.8473, -80.2006),
    "33161": (25.8870, -80.1813),
    "33109": (25.7587, -80.1358),
    "33160": (25.9330, -80.1248)
}

# Short list for debugging
# ZIP_LAT_LON = {
#    "33139": (25.7828, -80.1341),
#}

API_HOST = "realtor16.p.rapidapi.com"
API_KEY = "435f273a6amsh3973eab886359cap108895jsn5ef05f7d2f9b"

headers = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': API_HOST
}

conn = http.client.HTTPSConnection(API_HOST)

all_listings = []

for zip_code, (lat, lon) in ZIP_LAT_LON.items():
    print(f"🔍 Fetching ZIP {zip_code} at ({lat}, {lon})")

    path = f"/search/forsale/coordinates?latitude={lat}&longitude={lon}&radius=2"

    try:
        conn.request("GET", path, headers=headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        json_data = json.loads(data)
        # print(json.dumps(json_data, indent=2))  # See full structure

        # Immediately after `json_data = json.loads(data)`
        # Print keys to guide debugging
        print("Top-level keys:", list(json_data.keys()))

        # Try the expected path first
        results = json_data.get("data", {}).get("home_search", {}).get("results", [])

        # Fallback 1: look for a direct "results" field
        if not results:
            results = json_data.get("results", [])

        # Fallback 2: try deeper paths if known
        if not results and "data" in json_data:
            for key in json_data["data"]:
                sub = json_data["data"][key]
                if isinstance(sub, dict) and "results" in sub:
                    results = sub["results"]
                    break

        # print(f"✅ Found {len(results)} listings")

        #results = json_data.get("data", {}).get("home_search", {}).get("results", [])
        results = json_data.get("properties", [])
        if not results:
            results = json_data.get("data", {}).get("home_search", {}).get("results", [])

        if not results:
            print(f"⚠️ No listings found for {zip_code}")
            continue

        for item in results:
            listing = {
                "zip": zip_code,
                "price": item.get("price") or item.get("list_price"),
                "beds": item.get("beds") or item.get("description", {}).get("beds"),
                "baths": item.get("baths") or item.get("description", {}).get("baths"),
                "sqft": item.get("sqft") or item.get("description", {}).get("sqft"),
                "address": item.get("address", {}).get("line") or item.get("location", {}).get("address", {}).get("line"),
                "city": item.get("address", {}).get("city") or item.get("location", {}).get("address", {}).get("city"),
                "description": item.get("description", {}).get("text") or "",
                #"image_url": (
                #    (item.get("photo") or {}).get("href")
                #    or (item.get("primary_photo") or {}).get("href")
                #)
                #sAnd this "image_urls": [photo.get("href") for photo in item.get("photos", []) if photo.get("href")]
                # hack to get bigger images
                "image_urls": [
                    photo.get("href").replace("s.jpg", "l.jpg")
                    for photo in item.get("photos", [])
                    if photo.get("href")
                ]
            }
            all_listings.append(listing)

    except Exception as e:
        print(f"❌ Error on ZIP {zip_code}: {e}")

    time.sleep(2)

# Save to file
with open("listings_by_coordinates.json", "w") as f:
    json.dump(all_listings, f, indent=2)

print(f"✅ Saved {len(all_listings)} listings to listings_by_coordinates.json")
