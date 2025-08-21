import os
import time
import requests
from dotenv import load_dotenv

# Load credentials
load_dotenv()
ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
AD_ACCOUNT_ID = os.getenv("FB_AD_ACCOUNT_ID")
FB_PAGE_ID = os.getenv("FB_PAGE_ID").replace("pg_", "")

# Step 1: Create Campaign
print("\n🔹 Creating Campaign...")
campaign_url = f"https://graph.facebook.com/v23.0/{AD_ACCOUNT_ID}/campaigns"
campaign_payload = {
    "name": "TestRnFCampGauravUP1",
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

# Step 2: Create Reach & Frequency Prediction
print("\n🔹 Creating Reach & Frequency Prediction...")
start_time = int(time.time()) + 3600  # Start in 1 hour
end_time = start_time + (3 * 24 * 60 * 60)  # Run for 3 days

prediction_url = f"https://graph.facebook.com/v23.0/{AD_ACCOUNT_ID}/reachfrequencypredictions"

prediction_payload = {
    "campaign_id": campaign_id,
    "objective": "OUTCOME_AWARENESS",
    "optimization_goal": "REACH",
    "start_time": start_time,
    "end_time": end_time,
    "stop_time": end_time,
    "budget": 1500000,
    "buying_type": "RESERVED",
    "interval_frequency_cap_reset_period": 24,
    "prediction_mode": 1,
    "frequency_cap": 3,
    "destination_id": FB_PAGE_ID,
    "story_event_type": 128,
    "creative_spec": {
        "page_id": "FB_PAGE_ID"
    },
    "target_spec": {
        "age_max": 35,
        "age_min": 18,
        "flexible_spec": [
            {
                "interests": [
                    {"id": "6003780008652"}, {"id": "6003346592981"}, {"id": "6003456388203"},
                    {"id": "6003348604581"}, {"id": "6003263791114"}, {"id": "6003188355978"},
                    {"id": "6003372784175"}, {"id": "6003526234370"}, {"id": "6003103108917"},
                    {"id": "6003242077675"}, {"id": "6004030160948"}, {"id": "6003242238524"},
                    {"id": "6002867432822"}, {"id": "6003142505790"}, {"id": "6003348453981"},
                    {"id": "6002866906422"}, {"id": "6002921098355"}, {"id": "6003402305839"},
                    {"id": "6003483619198"}, {"id": "6003343520028"}, {"id": "6003068366382"},
                    {"id": "6007828099136"}
                ],
                "behaviors": [
                    {"id": "6071631541183"}, {"id": "6002714895372"},
                    {"id": "6004386044572"}, {"id": "6004382299972"}
                ]
            }
        ],
        "geo_locations": {
            "regions": [
                {
                    "key": "1754",
                    "name": "Uttar Pradesh",
                    "country": "IN"
                }
            ],
            "location_types": ["home", "recent"]
        },
        "brand_safety_content_filter_levels": ["FACEBOOK_RELAXED", "AN_RELAXED"],
        "publisher_platforms": ["facebook", "audience_network"],
        "facebook_positions": [
            "feed", "instream_video", "video_feeds", "marketplace", "story",
            "facebook_reels_overlay", "search", "facebook_reels"
        ],
        "device_platforms": ["mobile", "desktop"],
        "audience_network_positions": ["classic"]
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

# Step 3: Poll for Prediction Status
print("\n🔹 Checking Prediction Status...")
check_url = f"https://graph.facebook.com/v23.0/{prediction_id}"
check_params = {
    "fields": "status",
    "access_token": ACCESS_TOKEN
}

status = None
for attempt in range(15):
    check_res = requests.get(check_url, params=check_params)
    check_json = check_res.json()
    status = check_json.get("status")
    print(f"Attempt {attempt + 1}: Prediction Status = {status}")
    
    if status == 1:
        print("✅ Prediction is SUCCESS and ready to reserve.")
        break
    elif status in [2, 17]:
        exit("❌ Prediction failed or is invalid.")
    
    time.sleep(40)

if status != 1:
    exit("❌ Prediction is not ready after multiple attempts.")

# Step 4 : Verify the region
print("\n🔹 Verifying Region from Prediction...")
verify_url = f"https://graph.facebook.com/v23.0/{prediction_id}"
verify_params = {
    "fields": "target_spec",
    "access_token": ACCESS_TOKEN
}
verify_res = requests.get(verify_url, params=verify_params)
verify_json = verify_res.json()

if "target_spec" in verify_json:
    regions = verify_json["target_spec"].get("geo_locations", {}).get("regions", [])
    print("✅ Targeted Regions:")
    for region in regions:
        print(f"  - Region Name: {region.get('name')} | Region Key: {region.get('key')}")
else:
    print("❌ Could not fetch targeted region.")

# Step 5: Reserve the Prediction
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

# Step 6: Create Ad Set
print("\n🔹 Creating Ad Set...")
adset_url = f"https://graph.facebook.com/v23.0/{AD_ACCOUNT_ID}/adsets"
adset_payload = {
    "name": "TestRnFAdsetGauravUP1",
    "campaign_id": campaign_id,
    "billing_event": "IMPRESSIONS",
    "optimization_goal": "REACH",
    "rf_prediction_id": reserved_id,
   # "targeting": prediction_payload["target_spec"],
    "status": "PAUSED",
    "access_token": ACCESS_TOKEN
}

adset_res = requests.post(adset_url, json=adset_payload)
print("Ad Set Creation Status:", adset_res.status_code)
print("Ad Set Response:", adset_res.json())
