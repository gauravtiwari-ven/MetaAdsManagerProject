import os
import time
import requests
from dotenv import load_dotenv

# Load .env values
load_dotenv()

ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
AD_ACCOUNT_ID = os.getenv("FB_AD_ACCOUNT_ID")
CAMPAIGN_ID = input("Enter existing Campaign ID: ").strip()

# Timing
start_time = int(time.time()) + 3600
end_time = start_time + (3 * 24 * 60 * 60)

# Build prediction payload
payload = {
    "campaign_id": CAMPAIGN_ID,
    "frequency_cap": 2,
    "start_time": start_time,
    "end_time": end_time,
    "objective": "REACH",
    "buying_type": "RESERVED",
    "prediction_mode": 1,
    "budget": 10000,
    "access_token": ACCESS_TOKEN,
    "target_spec": {
        "geo_locations": {"countries": ["IN"]},
        "age_min": 18,
        "age_max": 45,

        "publisher_platforms": ["facebook"],
        "flexible_spec": [
            {
                "interests": [{"id": 6003349442621}]  # Technology
            },
            {
                "behaviors": [{"id": 6002714895372}]  # Engaged Shoppers
            }
        ]
    },
    "frequency_control_spec": [
        {
            "event": "IMPRESSION",
            "interval_days": 7,
            "max_frequency": 2
        }
    ]
}

# payload = {
#     "campaign_id": CAMPAIGN_ID,
#     "frequency_cap": 2,
#     "start_time": start_time,
#     "end_time": end_time,
#     "objective": "REACH",
#     "buying_type": "RESERVED",
#     "prediction_mode": 1,
#     "budget": 10000,
#     "access_token": ACCESS_TOKEN,
#     "target_spec": {
#         "geo_locations": {"countries": ["IN"]},
#         "age_min": 18,
#         "age_max": 45,
#         "publisher_platforms": ["facebook"],

#         "interests": [{"id": 6003349442621}],      # Technology
#         "behaviors": [{"id": 6002714895372}],      # Engaged Shoppers
#     },
#     "frequency_control_spec": [
#         {
#             "event": "IMPRESSION",
#             "interval_days": 7,
#             "max_frequency": 2
#         }
#     ]
# }

# Make API call
url = f"https://graph.facebook.com/v23.0/{AD_ACCOUNT_ID}/reachfrequencypredictions"
response = requests.post(url, json=payload)

# Output
print("Status Code:", response.status_code)
print("Response PredictionID:", response.json())
