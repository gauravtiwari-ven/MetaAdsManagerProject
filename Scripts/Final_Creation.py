import os
import time
import base64
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.reachfrequencyprediction import ReachFrequencyPrediction
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.adimage import AdImage
from facebook_business.adobjects.advideo import AdVideo

# Load credentials from .env
load_dotenv()
app_id = os.getenv("FB_APP_ID")
app_secret = os.getenv("FB_APP_SECRET")
access_token = os.getenv("FB_ACCESS_TOKEN")
ad_account_id = os.getenv("FB_AD_ACCOUNT_ID")
page_id = os.getenv("FB_PAGE_ID")

# Ensure ad account ID has 'act_' prefix
if ad_account_id and not ad_account_id.startswith("act_"):
    ad_account_id = f"act_{ad_account_id}"
if page_id and page_id.startswith("pg_"):
    page_id = page_id.replace("pg_", "")

# Initialize the Facebook API
FacebookAdsApi.init(app_id, app_secret, access_token)
account = AdAccount(ad_account_id)

# Function to upload image and return hash
def get_image_hash(image_path):
    print("Uploading image and generating hash...")
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
        image = account.create_ad_image(fields=[], params={"bytes": encoded})
    image_hash = image.get("hash")
    print(f"Image uploaded. Hash: {image_hash}")
    return image_hash

# Function to upload video and return video ID
def get_video_id(video_path):
    print("Uploading video and generating ID...")
    video = AdVideo(parent_id=ad_account_id)
    video[AdVideo.Field.filepath] = video_path
    video.remote_create()
    video.waitUntilEncodingReady()
    vid_id = video.get_id()
    print(f"Video uploaded. ID: {vid_id}")
    return vid_id

# Function to create ad creative (image or video)
def create_ad_creative(creative_type, media_path, ad_name, headline, description, message, link):
    creative_params = {
        "name": ad_name,
        "object_story_spec": {
            "page_id": page_id
        }
    }
    if creative_type.lower() == "image":
        # Create image creative
        image_hash = get_image_hash(media_path)
        creative_params["object_story_spec"]["link_data"] = {
            "image_hash": image_hash,
            "link": link,
            "message": message,
            "name": headline,
            "description": description,
            "call_to_action": {
                "type": "LEARN_MORE",
                "value": {"link": link}
            }
        }
    elif creative_type.lower() == "video":
        # Create video creative
        video_id = get_video_id(media_path)
        # Optionally, upload an image for thumbnail if needed
        thumbnail_hash = get_image_hash(r"C:\Users\Admin\meta_ads_automation\sampleimage.png")
        creative_params["object_story_spec"]["video_data"] = {
            "video_id": video_id,
            "title": headline,
            "message": message,
            "link_description": description,
            "image_hash": thumbnail_hash,
            "call_to_action": {
                "type": "LEARN_MORE",
                "value": {"link": link}
            }
        }
    else:
        raise ValueError("Invalid creative_type. Must be 'image' or 'video'.")

    print("Creating ad creative...")
    creative = account.create_ad_creative(fields=[], params=creative_params)
    creative_id = creative.get("id")
    print(f"✅ Creative Created: {creative_id}")
    return creative_id

# Function to create an ad in specified ad set
def create_ad(adset_id, creative_id, ad_name, ad_status="ACTIVE"):
    ad_params = {
        "name": ad_name,
        "adset_id": adset_id,
        "creative": {"creative_id": creative_id},
        "status": ad_status.upper()
    }
    print("Creating ad...")
    ad = account.create_ad(fields=[], params=ad_params)
    ad_id = ad.get("id")
    print(f"✅ Ad Created: {ad_id}")
    return ad_id

# Step 1: Create Campaign
print("\n🔹 Creating Campaign...")
campaign_params = {
    Campaign.Field.name: "GauravFinalVideoCamp",
    Campaign.Field.objective: "OUTCOME_AWARENESS",
    Campaign.Field.status: "PAUSED",
    Campaign.Field.buying_type: "RESERVED",
    Campaign.Field.special_ad_categories: ["NONE"]
}
campaign = account.create_campaign(fields=[], params=campaign_params)
campaign_id = campaign.get("id")
if not campaign_id:
    exit("❌ Campaign creation failed.")
print(f"✅ Campaign Created: {campaign_id}")

# Step 2: Create Reach & Frequency Prediction
print("\n🔹 Creating Reach & Frequency Prediction...")
start_time = int(time.time()) + 3600  # Start in 1 hour
end_time = start_time + (3 * 24 * 60 * 60)  # 3 days
prediction_params = {
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
    "frequency_cap": 2,
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
prediction_id = prediction.get("id")
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
reserved_id = reserve.get("id")
if not reserved_id:
    exit("❌ Reservation failed.")
print(f"✅ Reservation successful. Reserved Prediction ID: {reserved_id}")

# Step 6: Create Ad Set
print("\n🔹 Creating Ad Set...")
adset_params = {
    AdSet.Field.name: "GauravFinalVideoAdSet",
    AdSet.Field.campaign_id: campaign_id,
    AdSet.Field.billing_event: "IMPRESSIONS",
    AdSet.Field.optimization_goal: "REACH",
    AdSet.Field.rf_prediction_id: reserved_id,
    AdSet.Field.targeting: prediction_params["target_spec"],
    AdSet.Field.status: "PAUSED"
}
adset = account.create_ad_set(fields=[], params=adset_params)
adset_id = adset.get("id")
if not adset_id:
    exit("❌ Ad Set creation failed.")
print(f"✅ Ad Set Created: {adset_id}")

# Step 7: Create Ad Creative (Image or Video)
creative_type = "Video"  # Change to "image" if using an image
ad_name = "GauravFinalAdVideo"
headline = "Upgrade Your Lifestyle Today!"
description = "Discover top-rated products for your everyday needs."
message = "🚀 Fast delivery, great prices, and premium quality. Shop now!"
link = "https://example.com/shop-now"
image_path = r"C:\Users\Admin\meta_ads_automation\sampleimage.png"
video_path = r"C:\Users\Admin\meta_ads_automation\sampleVideo.mp4"

if creative_type.lower() == "image":
    creative_id = create_ad_creative(creative_type, image_path, ad_name, headline, description, message, link)
else:
    creative_id = create_ad_creative(creative_type, video_path, ad_name, headline, description, message, link)

# Step 8: Create Ad
print("\n🔹 Creating Ad...")
ad_id = create_ad(adset_id, creative_id, ad_name, ad_status="ACTIVE")

# Summary of all created IDs
print("\n✅ All entities created successfully!")
print(f"✅ Campaign ID: {campaign_id}")
print(f"✅ Prediction ID: {prediction_id}")
print(f"✅ Reserved Prediction ID: {reserved_id}")
print(f"✅ Ad Set ID: {adset_id}")
print(f"✅ Creative ID: {creative_id}")
print(f"✅ Ad ID: {ad_id}")
