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

# Initialize API
FacebookAdsApi.init(app_id, app_secret, access_token, api_version="v23.0")
if not ad_account_id.startswith("act_"):
    ad_account_id = f"act_{ad_account_id}"
account = AdAccount(ad_account_id)

# Step 1: Create Campaign
print("\n🔹 Creating RESERVED Campaign...")
campaign_params = {
    Campaign.Field.name: "TestRnFCampaignGauravVideoFixed",
    Campaign.Field.objective: "OUTCOME_AWARENESS",
    Campaign.Field.status: "PAUSED",
    Campaign.Field.buying_type: "RESERVED",
    Campaign.Field.special_ad_categories: []  # Fixed: empty array instead of ["NONE"]
}

try:
    campaign = account.create_campaign(fields=[], params=campaign_params)
    campaign_id = campaign["id"]
    print(f"✅ Campaign Created: {campaign_id}")
except Exception as e:
    print(f"❌ Campaign creation failed: {e}")
    exit(1)

# Step 2: Create R&F Prediction with VALID placements for RESERVED
print("\n🔹 Creating Reach & Frequency Prediction...")
start_time = int(time.time()) + 7200  # Start in 2 hours
end_time = start_time + (7 * 24 * 60 * 60)  # 7 days duration

prediction_params = {
    "campaign_id": campaign_id,
    "objective": "OUTCOME_AWARENESS", 
    "optimization_goal": "REACH",
    "start_time": start_time,
    "end_time": end_time,
    "budget": 5000000,
    "buying_type": "RESERVED",
    "interval_frequency_cap_reset_period": 24,
    "prediction_mode": 1,
    "frequency_cap": 2,
    "reach": 50000,
    "destination_id": page_id,
    "creative_types": ["VIDEO"],
    "creative_spec": {
        "page_id": page_id
    },
    "target_spec": {  
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
            "countries": ["IN"],
            "location_types": ["home", "recent"]
        },
        "brand_safety_content_filter_levels": ["FACEBOOK_RELAXED", "AN_RELAXED"],
        "publisher_platforms": ["facebook", "audience_network"],
        "facebook_positions": ["feed"],
        "audience_network_positions": ["classic"],
        "device_platforms": ["mobile", "desktop"]
    }
}

try:
    prediction = account.create_reach_frequency_prediction(fields=[], params=prediction_params)
    prediction_id = prediction["id"]
    print(f"✅ Prediction Created: {prediction_id}")
except Exception as e:
    print(f"❌ Prediction creation failed: {e}")
    print("This usually means invalid placements or targeting for RESERVED campaigns")
    exit(1)

# Step 3: Poll prediction status with better error handling
print("\n🔹 Checking Prediction Status...")
max_attempts = 20
for attempt in range(max_attempts):
    try:
        status_response = ReachFrequencyPrediction(prediction_id).api_get(fields=["status"])
        status = status_response["status"]
        print(f"Attempt {attempt+1}: Prediction Status = {status}")
        
        if status == 1:  # SUCCESS
            print("✅ Prediction is ready and successful!")
            break
        elif status == 2:  # PENDING
            print("⏳ Prediction still processing...")
        elif status == 3:  # FAIL - Cannot reach audience
            print("❌ FAILED: Cannot reach audience - reach too broad or budget too high")
            print("💡 Try: Reduce budget, increase reach target, or broaden targeting")
            exit(1)
        elif status in [4, 5, 6, 7, 8, 9, 10, 11]:  # Various failure codes
            print(f"❌ Prediction failed with status {status}")
            print("Check targeting parameters, budget, duration, or placements")
            exit(1)
        else:
            print(f"⚠️ Unknown status: {status}")
            
        time.sleep(30)  # Wait 30 seconds before next check
        
    except Exception as e:
        print(f"Error checking status: {e}")
        time.sleep(30)
else:
    print("❌ Prediction timed out after maximum attempts")
    exit(1)

# Step 4: Reserve the prediction
print("\n🔹 Reserving Prediction...")
try:
    reserve_response = account.create_reach_frequency_prediction(fields=[], params={
        "action": "reserve",
        "rf_prediction_id": prediction_id
    })
    reserved_id = reserve_response["id"]
    print(f"✅ Reserved: {reserved_id}")
except Exception as e:
    print(f"❌ Reservation failed: {e}")
    exit(1)

# Step 5: Create Ad Set with matching targeting
print("\n🔹 Creating Ad Set...")
adset_params = {
    AdSet.Field.name: "TestAdSetGauravVideoRnFFixed",
    AdSet.Field.campaign_id: campaign_id,
    AdSet.Field.billing_event: "IMPRESSIONS",
    AdSet.Field.optimization_goal: "REACH",
    AdSet.Field.rf_prediction_id: reserved_id,
    # MUST match the prediction targeting exactly
    AdSet.Field.targeting: prediction_params["target_spec"],
    AdSet.Field.status: "PAUSED",
    AdSet.Field.start_time: start_time,
    AdSet.Field.end_time: end_time
}

try:
    adset = account.create_ad_set(fields=[], params=adset_params)
    print(f"✅ Ad Set Created: {adset['id']}")
    print("\n🎉 SUCCESS! Campaign, Prediction, and Ad Set created successfully!")
    print(f"Campaign ID: {campaign_id}")
    print(f"Prediction ID: {prediction_id}")
    print(f"Reserved ID: {reserved_id}")
    print(f"Ad Set ID: {adset['id']}")
except Exception as e:
    print(f"❌ Ad Set creation failed: {e}")
