import os
import requests
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()
ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
AD_ACCOUNT_ID = os.getenv("FB_AD_ACCOUNT_ID")  # Should include 'act_'

# Input
campaign_id = input("Enter Campaign ID: ").strip()
prediction_id = input("Enter Reach & Frequency Prediction ID: ").strip()

# Step 1: Check prediction status
check_url = f"https://graph.facebook.com/v23.0/{prediction_id}"
check_params = {
    "fields": "status",
    "access_token": ACCESS_TOKEN
}
check_res = requests.get(check_url, params=check_params)
check_json = check_res.json()

print("Prediction Status Check Response:", check_json)
status = check_json.get("status")

if status != 1:
    print("❌ Prediction is not ready (status is not SUCCESS).")
    exit()
else:
    print("✅ Prediction is SUCCESS and ready to reserve.")

# Step 2: Reserve the prediction
reserve_url = f"https://graph.facebook.com/v23.0/{AD_ACCOUNT_ID}/reachfrequencypredictions"
reserve_payload = {
    "action": "reserve",
    "rf_prediction_id": prediction_id,
    "access_token": ACCESS_TOKEN
}
reserve_res = requests.post(reserve_url, data=reserve_payload)
reserve_json = reserve_res.json()

print("Reserve Response:", reserve_res.status_code, reserve_json)

reserved_id = reserve_json.get("id")
if not reserved_id:
    print("❌ Reservation failed. Cannot proceed to create ad set.")
    exit()
else:
    print(f"✅ Reservation successful. Reserved Prediction ID: {reserved_id}")

# Step 3: Create Ad Set using the reserved ID
adset_payload = {
    "name": "TestRnFAdsetGaurav",
    "campaign_id": campaign_id,
    "billing_event": "IMPRESSIONS",
    "optimization_goal": "REACH",
    "rf_prediction_id": reserved_id,
    "targeting": str({
        "geo_locations": {"countries": ["IN"]},
        "age_min": 18,
        "age_max": 45,
        "publisher_platforms": ["facebook"]
    }).replace("'", '"'),  # ensure JSON-encoded string
    "status": "PAUSED",
    "access_token": ACCESS_TOKEN
}

adset_url = f"https://graph.facebook.com/v23.0/{AD_ACCOUNT_ID}/adsets"
adset_res = requests.post(adset_url, data=adset_payload)
print("Ad Set Creation Status:", adset_res.status_code)
print("Ad Set Response:", adset_res.json())
