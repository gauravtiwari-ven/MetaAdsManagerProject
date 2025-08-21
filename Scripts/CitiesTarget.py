import requests
from urllib.parse import quote
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()
ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")

# Ask user for city name
city_name = input("Enter city name: ").strip()

# Build the URL for Facebook geo lookup
url = f"https://graph.facebook.com/v19.0/search?type=adgeolocation&location_types=['city']&q={quote(city_name)}&access_token={ACCESS_TOKEN}"

# Make the request
res = requests.get(url)
data = res.json()

# Extract and format the output
if "data" in data and len(data["data"]) > 0:
    city_data = data["data"][0]  # First matched city
    city_key = city_data["key"]
    print("\nCopy this snippet into your geo_locations:")
    print(f'''
"cities": [
  {{
    "key": "{city_key}",
    "radius": 25,
    "distance_unit": "kilometer"
  }}
]
''')
else:
    print("❌ No city found with that name.")
