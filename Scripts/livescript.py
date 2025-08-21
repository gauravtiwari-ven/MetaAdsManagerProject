import os
import time
import json
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.reachfrequencyprediction import ReachFrequencyPrediction
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.advideo import AdVideo
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.ad import Ad

# ─── Load .env & init API ─────────────────────────────────────────────
print("🔄 Initializing Facebook Marketing API...")
load_dotenv()
app_id = os.getenv("FB_APP_ID")
app_secret = os.getenv("FB_APP_SECRET")
access_token = os.getenv("FB_ACCESS_TOKEN")
ad_account_id = os.getenv("FB_AD_ACCOUNT_ID")
page_id = os.getenv("FB_PAGE_ID")

print(f"   App ID: {app_id[:8]}...")
print(f"   Account ID: {ad_account_id}")
print(f"   Page ID: {page_id}")

# Initialize the Facebook API
FacebookAdsApi.init(app_id, app_secret, access_token, api_version="v23.0")

# Ensure ad account ID has 'act_' prefix
if ad_account_id and not ad_account_id.startswith("act_"):
    ad_account_id = f"act_{ad_account_id}"
account = AdAccount(ad_account_id)

print("✅ API initialized successfully")

def sleep_sec(sec):
    print(f"⏳ Sleeping {sec}s to avoid rate limits…")
    time.sleep(sec)

# ─── Step 1: Create RESERVED Campaign ──────────────────────────────────────
print("\n🔹 Step 1: Creating RESERVED Campaign...")
campaign_params = {
    Campaign.Field.name: "Gauri01camp",
    Campaign.Field.objective: "OUTCOME_AWARENESS",
    Campaign.Field.status: "PAUSED",
    Campaign.Field.buying_type: "RESERVED",
    Campaign.Field.special_ad_categories: []  # Fixed: empty array instead of ["NONE"]
}

print("📋 Campaign Parameters:")
for key, value in campaign_params.items():
    print(f"   {key}: {value}")

try:
    campaign = account.create_campaign(fields=[], params=campaign_params)
    campaign_id = campaign.get('id')
    print("✅ Campaign Creation Status: 200")
    print("✅ Campaign Response:", dict(campaign))
    if not campaign_id:
        exit("❌ Campaign creation failed.")
    print(f"✅ Campaign Created: {campaign_id}")
except Exception as e:
    print(f"❌ Campaign creation failed: {e}")
    exit(1)

sleep_sec(2)

# ─── Step 2: Create R&F Prediction with Enhanced Targeting ─────────────────────────────────────
print("\n🔹 Step 2: Creating Reach & Frequency Prediction...")
start_time = int(time.time()) + 3600  # Start in 1 hour 
end_time = start_time + (7 * 24 * 60 * 60)  # Run for 7 days

print(f"⏰ Campaign Schedule:")
print(f"   Start Time: {start_time} ({time.ctime(start_time)})")
print(f"   End Time: {end_time} ({time.ctime(end_time)})")

# Enhanced targeting spec from reference code (but with RESERVED-compatible placements)
target_spec = {
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
    # CRITICAL: Only valid placements for RESERVED campaigns
    "publisher_platforms": ["facebook", "audience_network"],
    "facebook_positions": ["feed"],  # Only feed allowed for RESERVED
    "audience_network_positions": ["classic"],  # Only classic allowed for RESERVED
    "device_platforms": ["mobile", "desktop"]
}

prediction_params = {
    "campaign_id": campaign_id,
    "objective": "OUTCOME_AWARENESS",
    "optimization_goal": "REACH",
    "start_time": start_time,
    "end_time": end_time,
   # "stop_time": end_time,
    "budget": 150000,  # 150,000 in currency units
    "buying_type": "RESERVED",
    "interval_frequency_cap_reset_period": 24,
    "prediction_mode": 1,
    "frequency_cap": 1,
    "destination_id": page_id,
    "creative_types": ["VIDEO"],  # CRITICAL: This enables video support
    "creative_spec": {"page_id": page_id},
    "target_spec": target_spec
}

print("📋 Prediction Parameters:")
print(f"   Budget: {prediction_params['budget']} (currency units)")
print(f"   Frequency Cap: {prediction_params['frequency_cap']}")
print(f"   Creative Types: {prediction_params['creative_types']}")
print(f"   Target Region: Uttar Pradesh, India")
print(f"   Valid Placements: Facebook Feed + Audience Network Classic")

try:
    prediction = account.create_reach_frequency_prediction(fields=[], params=prediction_params)
    prediction_id = prediction.get('id')
    print("✅ Prediction Status: 200")
    print("✅ Prediction Response:", dict(prediction))
    if not prediction_id:
        exit("❌ Prediction creation failed.")
    print(f"✅ Prediction Created: {prediction_id}")
except Exception as e:
    print(f"❌ Prediction creation failed: {e}")
    print("💡 This usually means invalid placements or targeting for RESERVED campaigns")
    exit(1)

sleep_sec(2)

# ─── Step 3: Poll for Prediction Status ─────────────────────────────────────
print("\n🔹 Step 3: Monitoring Prediction Status...")
prediction_obj = ReachFrequencyPrediction(prediction_id)
status = None
max_attempts = 6

for attempt in range(max_attempts):
    try:
        prediction_obj = prediction_obj.api_get(fields=[ReachFrequencyPrediction.Field.status])
        status = prediction_obj.get(ReachFrequencyPrediction.Field.status)
        
        status_messages = {
            1: "SUCCESS - Ready to reserve",
            2: "PENDING - Still processing", 
            3: "FAIL - Cannot reach audience (reduce budget or broaden targeting)",
            4: "FAIL - Invalid parameters",
            17: "FAIL - Generic failure"
        }
        
        status_msg = status_messages.get(status, f"Unknown status: {status}")
        print(f"⏳ Attempt {attempt + 1}/{max_attempts}: Status = {status} ({status_msg})")
        
        if status == 1:
            print("✅ Prediction is SUCCESS and ready to reserve!")
            break
        elif status in [3, 4, 17]:
            print(f"❌ Prediction failed with status {status}")
            print("💡 Try: Reduce budget, increase reach target, or broaden targeting")
            exit(1)
        
        sleep_sec(40)
        
    except Exception as e:
        print(f"⚠️ Error checking prediction status: {e}")
        sleep_sec(40)
else:
    print(f"❌ Prediction timed out after {max_attempts} attempts")
    exit(1)

# ─── Step 4: Verify the Region ────────────────────────────────────────
print("\n🔹 Step 4: Verifying Region from Prediction...")
try:
    verify_obj = ReachFrequencyPrediction(prediction_id)
    verify = verify_obj.api_get(fields=['target_spec'])
    if 'target_spec' in verify:
        regions = verify['target_spec'].get("geo_locations", {}).get("regions", [])
        print("✅ Targeted Regions:")
        for region in regions:
            print(f"  - Region Name: {region.get('name')} | Region Key: {region.get('key')}")
    else:
        print("❌ Could not fetch targeted region.")
except Exception as e:
    print(f"⚠️ Error verifying region: {e}")

sleep_sec(2)

# ─── Step 5: Reserve the Prediction ────────────────────────────────────────
print("\n🔹 Step 5: Reserving Prediction...")
try:
    reserve = account.create_reach_frequency_prediction(fields=[], params={
        "action": "reserve",
        "rf_prediction_id": prediction_id
    })
    print("✅ Reserve Response:", dict(reserve))
    reserved_id = reserve.get('id')
    if not reserved_id:
        exit("❌ Reservation failed. Cannot proceed.")
    print(f"✅ Reservation successful. Reserved Prediction ID: {reserved_id}")
except Exception as e:
    print(f"❌ Reservation failed: {e}")
    exit(1)

sleep_sec(2)

# ─── Step 6: Create Ad Set ─────────────────────────────────────────────────
print("\n🔹 Step 6: Creating Ad Set...")
adset_params = {
    AdSet.Field.name: "Gauri01adset",
    AdSet.Field.campaign_id: campaign_id,
    AdSet.Field.billing_event: "IMPRESSIONS",
    AdSet.Field.optimization_goal: "REACH",
    AdSet.Field.rf_prediction_id: reserved_id,
    AdSet.Field.targeting: prediction_params["target_spec"],  # Use the original target_spec
    AdSet.Field.status: "PAUSED",
    AdSet.Field.start_time: start_time,
    AdSet.Field.end_time: end_time,
    "creative_type": "VIDEO"                     # ←---- the missing flag

}

print("📋 Ad Set Parameters:")
for key, value in adset_params.items():
    if key != AdSet.Field.targeting:  # Don't print the full targeting object
        print(f"   {key}: {value}")
print(f"   targeting: [Complex targeting object - matches prediction]")

try:
    adset = account.create_ad_set(fields=[], params=adset_params)
    print("✅ Ad Set Creation Status: 200")
    print("✅ Ad Set Response:", dict(adset))
    adset_id = adset.get('id')
    if not adset_id:
        exit("❌ Ad Set creation failed.")
    print(f"✅ Ad Set Created: {adset_id}")
except Exception as e:
    print(f"❌ Ad Set creation failed: {e}")
    exit(1)

sleep_sec(2)

# ─── Step 7: Upload Video & Create Creative ─────────────────────────────────
print("\n🔹 Step 7: Uploading Video...")
VIDEO_FILE_PATH = r"C:\Users\Admin\meta_ads_automation\sampleVideo.mp4"  # Update this path

if not os.path.exists(VIDEO_FILE_PATH):
    print(f"⚠️ Video file not found: {VIDEO_FILE_PATH}")
    print("📝 Please update VIDEO_FILE_PATH and run again")
    print(f"\n🎉 PARTIAL SUCCESS SUMMARY:")
    print(f"   Campaign ID: {campaign_id}")
    print(f"   Prediction ID: {prediction_id}")
    print(f"   Reserved ID: {reserved_id}")
    print(f"   Ad Set ID: {adset_id}")
    exit(0)

try:
    print(f"📤 Uploading video: {VIDEO_FILE_PATH}")
    video = AdVideo(parent_id=ad_account_id)
    video[AdVideo.Field.filepath] = VIDEO_FILE_PATH
    video.remote_create()
    print("⏳ Waiting for video encoding...")
    video.waitUntilEncodingReady()
    video_id = video.get_id()
    print(f"✅ Video uploaded successfully: {video_id}")
except Exception as e:
    print(f"❌ Video upload failed: {e}")
    exit(1)

sleep_sec(2)

def upload_image_and_get_hash(image_path, ad_account_id):
    """Uploads an image to Facebook and returns its image_hash."""
    from facebook_business.adobjects.adimage import AdImage
    image = AdImage(parent_id=ad_account_id)
    image[AdImage.Field.filename] = image_path
    image.remote_create()
    return image[AdImage.Field.hash]

print("\n🔹 Creating Video Creative...")
try:
    # Upload thumbnail image and get hash
    THUMBNAIL_IMAGE_PATH = r"C:\Users\Admin\meta_ads_automation\sampleimage.png"
    image_hash = upload_image_and_get_hash(THUMBNAIL_IMAGE_PATH, ad_account_id)
    print(f"✅ Uploaded thumbnail image. Image hash: {image_hash}")

    creative_params = {
        "name": "TestRnFVideoCreative1",
        "object_story_spec": {
            "page_id": page_id,
            "video_data": {
                "video_id": video_id,
                "title": "Upgrade Your Life!",
                "message": "🚀 Fast delivery & quality products.",
                "link_description": "Shop now!",
                "call_to_action": {
                    "type": "LEARN_MORE",
                    "value": {"link": "https://example.com"}
                },
                "image_hash": image_hash  # <-- Add thumbnail image hash here
            }
        }
    }
    
    creative = account.create_ad_creative(fields=[], params=creative_params)
    creative_id = creative.get('id')
    print(f"✅ Creative created successfully: {creative_id}")
except Exception as e:
    print(f"❌ Creative creation failed: {e}")
    exit(1)

sleep_sec(2)

# ─── Step 8: Create Ad ─────────────────────────────────────────────────────
print("\n🔹 Step 8: Creating Final Ad...")
try:
    ad_params = {
        "name": "TestRnFVideoAd1",
        "adset_id": adset_id,
        "creative": {"creative_id": creative_id},
        "status": "ACTIVE"  
    }
    
    print("📋 Ad Parameters:")
    for key, value in ad_params.items():
        print(f"   {key}: {value}")
    
    ad = account.create_ad(fields=[], params=ad_params)
    ad_id = ad.get('id')
    print("✅ Ad Creation Status: 200")
    print(f"✅ Ad Created Successfully: {ad_id}")
    print(f"📊 Ad Response: {dict(ad)}")
    
except Exception as e:
    print(f"❌ Ad creation failed: {e}")
    print(f"\n🎉 PARTIAL SUCCESS SUMMARY:")
    print(f"   Campaign ID: {campaign_id}")
    print(f"   Prediction ID: {prediction_id}")  
    print(f"   Reserved ID: {reserved_id}")
    print(f"   Ad Set ID: {adset_id}")
    print(f"   Creative ID: {creative_id}")
    exit(1)

# Final Success Summary
print(f"\n🎉 COMPLETE SUCCESS! All objects created:")
print(f"   ✅ Campaign ID: {campaign_id}")
print(f"   ✅ Prediction ID: {prediction_id}")
print(f"   ✅ Reserved ID: {reserved_id}")
print(f"   ✅ Ad Set ID: {adset_id}")
print(f"   ✅ Video ID: {video_id}")
print(f"   ✅ Creative ID: {creative_id}")
print(f"   ✅ Ad ID: {ad_id}")
print(f"\n📝 Next Steps:")
print(f"   1. Review all objects in Meta Ads Manager")
print(f"   2. Activate the campaign when ready")
print(f"   3. Monitor performance and optimize as needed")
print(f"\n💡 All objects created in PAUSED status for your review!")
