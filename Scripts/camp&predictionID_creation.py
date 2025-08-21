import os
import time
import requests
from dotenv import load_dotenv

# Load credentials
load_dotenv()
ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
AD_ACCOUNT_ID = os.getenv("FB_AD_ACCOUNT_ID")

# Create Campaign
campaign_url = f"https://graph.facebook.com/v23.0/{AD_ACCOUNT_ID}/campaigns"
campaign_payload = {
    "name": "TestRnFCampGaurav1",
    "objective": "OUTCOME_AWARENESS",
    "status": "PAUSED",
    "buying_type": "RESERVED",
    "special_ad_categories": ["NONE"],  
    "access_token": ACCESS_TOKEN
}
campaign_res = requests.post(campaign_url, data=campaign_payload)
print("Campaign Creation Status:", campaign_res.status_code)
print("Campaign Response:", campaign_res.json())

if "id" not in campaign_res.json():
    exit("Campaign creation failed")

campaign_id = campaign_res.json()["id"]

# Prediction setup
start_time = int(time.time()) + 3600
end_time = start_time + (3 * 24 * 60 * 60)

prediction_url = f"https://graph.facebook.com/v23.0/{AD_ACCOUNT_ID}/reachfrequencypredictions"
prediction_payload = {
    "campaign_id": campaign_id,
    "reach": 100000,
    "frequency_cap": 2,
    "start_time": start_time,
    "end_time": end_time,
    "objective": "REACH",
    "buying_type": "RESERVED",
    "prediction_mode": 1,
    "budget": 15000000,
    "target_spec": {
        "geo_locations": {"countries": ["IN"]},
        "age_min": 18,
        "age_max": 45,
        "publisher_platforms": ["facebook"]
    },
    "access_token": ACCESS_TOKEN
}
prediction_res = requests.post(prediction_url, json=prediction_payload)
print("Prediction Status:", prediction_res.status_code)
print("Prediction Response:", prediction_res.json())
