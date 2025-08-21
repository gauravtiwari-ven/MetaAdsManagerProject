import os
import time
import requests
from dotenv import load_dotenv

# Load credentials
load_dotenv()
ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
AD_ACCOUNT_ID = os.getenv("FB_AD_ACCOUNT_ID")

# Step 1: Create Campaign
print("🔹 Creating Campaign...")
campaign_url = f"https://graph.facebook.com/v23.0/{AD_ACCOUNT_ID}/campaigns"
campaign_payload = {
    "name": "TestRnFCampGaurav2",
    "objective": "OUTCOME_AWARENESS",
    "status": "PAUSED",
    "buying_type": "RESERVED",
    "special_ad_categories": ["NONE"],
    "access_token": ACCESS_TOKEN
}
campaign_res = requests.post(campaign_url, data=campaign_payload)
print("Campaign Creation Status:", campaign_res.status_code)
print("Campaign Response:", campaign_res.json())

campaign_json = campaign_res.json()
if "id" not in campaign_json:
    exit("❌ Campaign creation failed.")
campaign_id = campaign_json["id"]
print(f"✅ Campaign Created: {campaign_id}")

# Step 2: Create Prediction
print("\n🔹 Creating Reach & Frequency Prediction...")
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

prediction_json = prediction_res.json()
prediction_id = prediction_json.get("id")
if not prediction_id:
    exit("❌ Prediction creation failed.")
print(f"✅ Prediction Created: {prediction_id}")

# Step 3: Check Prediction Status
print("\n🔹 Checking Prediction Status...")
check_url = f"https://graph.facebook.com/v23.0/{prediction_id}"
check_params = {
    "fields": "status",
    "access_token": ACCESS_TOKEN
}
check_res = requests.get(check_url, params=check_params)
check_json = check_res.json()
print("Prediction Status Check Response:", check_json)

if check_json.get("status") != 1:
    exit("❌ Prediction is not ready (status != 1).")
print("✅ Prediction is SUCCESS and ready to reserve.")

# Step 4: Reserve the Prediction
print("\n🔹 Reserving Prediction...")
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
    exit("❌ Reservation failed. Cannot proceed.")
print(f"✅ Reservation successful. Reserved Prediction ID: {reserved_id}")

# Step 5: Create Ad Set
print("\n🔹 Creating Ad Set...")
adset_payload = {
    "name": "TestRnFAdsetGaurav2",
    "campaign_id": campaign_id,
    "billing_event": "IMPRESSIONS",
    "optimization_goal": "REACH",
    "rf_prediction_id": reserved_id,
    "targeting": str({
        "geo_locations": {"countries": ["IN"]},
        "age_min": 18,
        "age_max": 45,
        "publisher_platforms": ["facebook"]
    }).replace("'", '"'),
    "status": "PAUSED",
    "access_token": ACCESS_TOKEN
}

adset_url = f"https://graph.facebook.com/v23.0/{AD_ACCOUNT_ID}/adsets"
adset_res = requests.post(adset_url, data=adset_payload)
print("Ad Set Creation Status:", adset_res.status_code)
print("Ad Set Response:", adset_res.json())

adset_json = adset_res.json()
adset_id = adset_json.get("id")
if adset_id:
    print(f"✅ Adset Created: {adset_id}")
else:
    print("❌ Adset creation failed.")

