import os
import requests
from dotenv import load_dotenv

# Load .env credentials
load_dotenv()
ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")

def get_region_key(region_name):
    url = "https://graph.facebook.com/v23.0/search"
    params = {
        "type": "adgeolocation",
        "location_types": '["region"]',
        "q": region_name,
        "country_code": "IN",
        "access_token": ACCESS_TOKEN
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("❌ API Request Failed:", response.status_code, response.text)
        return

    data = response.json()
    results = data.get("data", [])
    if not results:
        print(f"❌ No matching region found for: {region_name}")
        return

    print(f"✅ Found regions for '{region_name}':\n")
    for region in results:
        print(f"Name: {region['name']} | Key: {region['key']} | Country: {region['country_code']}")

# Example usage
region_input = "Maharashtra"  # Replace with desired region name
get_region_key(region_input)
