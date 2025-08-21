import os
import time
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.reachfrequencyprediction import ReachFrequencyPrediction
from facebook_business.adobjects.adset import AdSet

# Load credentials from .env
load_dotenv()
app_id = os.getenv("FB_APP_ID")
app_secret = os.getenv("FB_APP_SECRET")
access_token = os.getenv("FB_ACCESS_TOKEN")
ad_account_id = os.getenv("FB_AD_ACCOUNT_ID")
page_id = os.getenv("FB_PAGE_ID")

# Initialize the Facebook API
FacebookAdsApi.init(app_id, app_secret, access_token)

# Ensure ad account ID has 'act_' prefix
if ad_account_id and not ad_account_id.startswith("act_"):
    ad_account_id = f"act_{ad_account_id}"
account = AdAccount(ad_account_id)

# Step 1: Create Campaign
print("\n🔹 Creating Campaign...")
campaign_params = {
    Campaign.Field.name: "GauravTestCampaignUP",
    Campaign.Field.objective: "OUTCOME_AWARENESS",
    Campaign.Field.status: "PAUSED",
    Campaign.Field.buying_type: "RESERVED",
    Campaign.Field.special_ad_categories: ["NONE"]
}
campaign = account.create_campaign(fields=[], params=campaign_params)
campaign_id = campaign.get('id')
print("Campaign Creation Status: 200")
print("Campaign Response:", dict(campaign))
if not campaign_id:
    exit("❌ Campaign creation failed.")
print(f"✅ Campaign Created: {campaign_id}")

# Step 2: Create Reach & Frequency Prediction
print("\n🔹 Creating Reach & Frequency Prediction...")
start_time = int(time.time()) + 3600  # Start in 1 hour
end_time = start_time + (3 * 24 * 60 * 60)  # Run for 3 days
prediction_params = {
    "campaign_id": campaign_id,
    "objective": "OUTCOME_AWARENESS",
    "optimization_goal": "REACH",
    "start_time": start_time,
    "end_time": end_time,
    "stop_time": end_time,
    "budget": 150000,
    "buying_type": "RESERVED",
    "interval_frequency_cap_reset_period": 24,
    "prediction_mode": 1,
    "frequency_cap": 3,
    "destination_id": page_id,
    "story_event_type": 128,
    "creative_spec": {"page_id": page_id},
    "target_spec": {
        "age_max": 55,
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
    }
}
prediction = account.create_reach_frequency_prediction(fields=[], params=prediction_params)
prediction_id = prediction.get('id')
print("Prediction Status: 200")
print("Prediction Response:", dict(prediction))
if not prediction_id:
    exit("❌ Prediction creation failed.")
print(f"✅ Prediction Created: {prediction_id}")

# Step 3: Poll for Prediction Status
print("\n🔹 Checking Prediction Status...")
prediction_obj = ReachFrequencyPrediction(prediction_id)
status = None
for attempt in range(6):
    prediction_obj = prediction_obj.api_get(fields=[ReachFrequencyPrediction.Field.status])
    status = prediction_obj.get(ReachFrequencyPrediction.Field.status)
    print(f"Attempt {attempt + 1}: Prediction Status = {status}")
    if status == 1:
        print("✅ Prediction is SUCCESS and ready to reserve.")
        break
    elif status in [2, 17]:
        exit("❌ Prediction failed or is invalid.")
    time.sleep(15)
if status != 1:
    exit("❌ Prediction is not ready after multiple attempts.")

# Step 4: Verify the Region
print("\n🔹 Verifying Region from Prediction...")
verify_obj = ReachFrequencyPrediction(prediction_id)
verify = verify_obj.api_get(fields=['target_spec'])
if 'target_spec' in verify:
    regions = verify['target_spec'].get("geo_locations", {}).get("regions", [])
    print("✅ Targeted Regions:")
    for region in regions:
        print(f"  - Region Name: {region.get('name')} | Region Key: {region.get('key')}")
else:
    print("❌ Could not fetch targeted region.")

# Step 5: Reserve the Prediction
print("\n🔹 Reserving Prediction...")
reserve = account.create_reach_frequency_prediction(fields=[], params={
    "action": "reserve",
    "rf_prediction_id": prediction_id
})
print("Reserve Response:", dict(reserve))
reserved_id = reserve.get('id')
if not reserved_id:
    exit("❌ Reservation failed. Cannot proceed.")
print(f"✅ Reservation successful. Reserved Prediction ID: {reserved_id}")

# Step 6: Create Ad Set
print("\n🔹 Creating Ad Set...")
adset_params = {
    AdSet.Field.name: "GauravTestAdSetUP",
    AdSet.Field.campaign_id: campaign_id,
    AdSet.Field.billing_event: "IMPRESSIONS",
    AdSet.Field.optimization_goal: "REACH",
    AdSet.Field.rf_prediction_id: reserved_id,
    AdSet.Field.targeting: prediction_params["target_spec"],
    AdSet.Field.status: "PAUSED"
}
adset = account.create_ad_set(fields=[], params=adset_params)
print("Ad Set Creation Status: 200")
print("Ad Set Response:", dict(adset))
if not adset:
    exit("❌ Ad Set creation failed.")