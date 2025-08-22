import os
import time
import base64
import json
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.reachfrequencyprediction import ReachFrequencyPrediction
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.advideo import AdVideo
from config import Config_Data
import pandas as pd
from date_time_stripper import Stripper
import time
from datetime import datetime

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
# Ensure page ID doesn't have 'pg_' prefix for API calls
if page_id and page_id.startswith("pg_"):
    page_id = page_id.replace("pg_", "")

# Initialize the Facebook API
FacebookAdsApi.init(app_id, app_secret, access_token)
account = AdAccount(ad_account_id)

###################################################### HELPER METHODS ###############################################

# Function to upload image and return hash
def get_image_hash(image_path):
    print("🖼️  Uploading image and generating hash...")
    print("⏳ Please wait...")
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
        image = account.create_ad_image(fields=[], params={"bytes": encoded})
    image_hash = image.get("hash")
    print(f"✅ Image uploaded successfully. Hash: {image_hash}")
    return image_hash


# Function to upload video and return video ID
def get_video_id(video_path):
    print("🎬 Uploading video and generating ID...")
    print("⏳ Please wait, this may take a few moments...")
    video = AdVideo(parent_id=ad_account_id)
    video[AdVideo.Field.filepath] = video_path
    video.remote_create()
    print("🔄 Video is being processed and encoded...")
    video.waitUntilEncodingReady()
    vid_id = video.get_id()
    print(f"✅ Video uploaded successfully. ID: {vid_id}")
    return vid_id


# Function to create ad creative (image or video)
def create_ad_creative(creative_type, media_path, ad_name, headline, description, message, link, call_to_action):
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
                "type": call_to_action.strip().upper(),
                "value": {"link": link}
            }
        }
    elif creative_type.lower() == "video":
        # Create video creative
        video_id = get_video_id(media_path)
        # Optionally, upload an image for thumbnail if needed
        thumbnail_hash = get_image_hash(r"sampleimage.png")
        creative_params["object_story_spec"]["video_data"] = {
            "video_id": video_id,
            "title": headline,
            "message": message,
            "link_description": description,
            "image_hash": thumbnail_hash,
            "call_to_action": {
                "type": call_to_action.strip().upper(),
                "value": {"link": link}
            }
        }
    else:
        raise ValueError("Invalid creative_type. Must be 'image' or 'video'.")

    print("🎨 Creating ad creative...")
    print("⏳ Please wait while we set up your creative...")
    creative = account.create_ad_creative(fields=[], params=creative_params)
    creative_id = creative.get("id")
    print(f"✅ Creative Created Successfully: {creative_id}")
    return creative_id


# Function to create an ad in specified ad set
def create_ad(adset_id, creative_id, ad_name, ad_status="ACTIVE"):
    ad_params = {
        "name": ad_name,
        "adset_id": adset_id,
        "creative": {"creative_id": creative_id},
        "status": ad_status.upper()
    }
    print("📢 Creating ad...")
    print("⏳ Please wait while we create your ad...")
    ad = account.create_ad(fields=[], params=ad_params)
    ad_id = ad.get("id")
    print(f"✅ Ad Created Successfully: {ad_id}")
    return ad_id

##FIltering campaign columns
camp_cols = Config_Data.campaign_columns

#READ THE INPUT FILE - AND CREATE A DATAFRAME
df = pd.read_csv("MedullaPOCFILE.csv")
final_df = df.copy()

# Initialize columns that will be added later to avoid pandas warnings
final_df['campaign_logs'] = ''
final_df['campaign_id'] = ''
final_df['adset_logs'] = ''
final_df['adset_id'] = ''
final_df['prediction_id'] = ''
final_df['ad_logs'] = ''
final_df['ad_id'] = ''

####################################### COMPLETE CAMPAIGN FLOW #####################################
camp_df = df[camp_cols].drop_duplicates()

# Check if there are any valid campaigns to process
if camp_df.empty:
    print("No campaigns detected in the data.")
    exit()

for camp_idx, camp_row in camp_df.iterrows():
    # Check if the row contains NaN values (empty data)
    if camp_row.isnull().all():
        print("No further campaigns detected.")
        break
    
    # Check if essential campaign fields are NaN
    if pd.isna(camp_row['campaign_name']) or pd.isna(camp_row['objective']) or pd.isna(camp_row['buy_type']):
        print("\n🔹 No further campaigns detected.")
        break
    
    print(f"\n{'='*60}")
    print(f"Processing Campaign: {camp_row['campaign_name']}")
    print(f"{'='*60}")
    
    # Step 1: Create Campaign
    print("\n🔹 Creating Campaign...")
    cname = camp_row['campaign_name']
    campaign_params = {
        Campaign.Field.name: cname,
        Campaign.Field.objective: camp_row['objective'],
        Campaign.Field.status: "PAUSED",
        Campaign.Field.buying_type: camp_row['buy_type'],
        Campaign.Field.special_ad_categories: ["NONE"]
    }
    
    try:
        campaign = account.create_campaign(fields=[], params=campaign_params)
        campaign_id = campaign.get("id")
        camp_logs = 'NO ERROR'
        print(f"✅ Campaign Created: {campaign_id}")
    except Exception as e:
        campaign_id = ''
        camp_logs = e
        print(f"❌ Campaign Creation Failed: {e}")
        continue  # Skip to next campaign if this one fails

    final_df.loc[(final_df['campaign_name'] == cname), 'campaign_logs'] = camp_logs
    final_df.loc[(final_df['campaign_name'] == cname), 'campaign_id'] = campaign_id
    
    # Step 2: Process all adsets for this campaign
    adset_cols = Config_Data.adset_columns
    campaign_adsets = final_df[(final_df['campaign_name'] == cname)][adset_cols].drop_duplicates()
    
    for adset_idx, adset_row in campaign_adsets.iterrows():
        print(f"\n--- Processing Adset: {adset_row['adset_name']} ---")
        
        # Update the adset row with the campaign_id
        adset_row['campaign_id'] = campaign_id

    ############################# Create Reach & Frequency Prediction #################################

        print("\n🔹 Creating Reach & Frequency Prediction...")
        
        # Use Stripper class for date handling
        try:
            start_time_str, stop_time_str = Stripper(adset_row['start_date'], adset_row['end_date']).get_formatted_dates()
            
            # Check if dates are valid
            if start_time_str is None or stop_time_str is None:
                print(f"Skipping row with invalid dates: start_date={adset_row['start_date']}, end_date={adset_row['end_date']}")
                continue
                
            # Handle datetime strings with or without timezone info
            try:
                start_dt = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S%z")
                stop_dt = datetime.strptime(stop_time_str, "%Y-%m-%dT%H:%M:%S%z")
            except ValueError:
                # If timezone info is missing, parse without it
                start_dt = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S")
                stop_dt = datetime.strptime(stop_time_str, "%Y-%m-%dT%H:%M:%S")
        except (ValueError, TypeError) as e:
            print(f"Date parsing error: {e}")
            continue

        prediction_params = {
            "campaign_id": adset_row['campaign_id'],
            "objective": adset_row['objective'],
            "optimization_goal": "REACH",
            "start_time": int(start_dt.timestamp()),
            "end_time": int(stop_dt.timestamp()),
           # "stop_time": stop_int,
            "budget": int(adset_row['adset_budget_amount']),
            "buying_type": adset_row['buy_type'],
            "frequency_cap": int(adset_row['frequency_cap']),
            "interval_frequency_cap_reset_period":168,
            "prediction_mode": int(adset_row['prediction_mode']),
            "destination_id": adset_row['fbpage'].replace("pg_", "") if adset_row['fbpage'] and adset_row['fbpage'].startswith("pg_") else adset_row['fbpage'],
            "story_event_type": 128,
            "creative_spec": {"page_id": adset_row['fbpage'].replace("pg_", "") if adset_row['fbpage'] and adset_row['fbpage'].startswith("pg_") else adset_row['fbpage']},
        "target_spec": {
            "age_max": int(adset_row['age_max']),
            "age_min": int(adset_row['age_min']),
            "flexible_spec": [
                {
                    "interests": [
                        {"id": "6003384248805"}, {"id": "6003369782940"}, {"id": "6003456388203"},
                        {"id": "6003348604581"}, {"id": "6003263791114"}, {"id": "6003188355978"},
                        {"id": "6003372784175"}, {"id": "6003526234370"}
                     ],
                    "behaviors": [
                        {"id": "6071631541183"}, {"id": "6002714895372"}
                    ]
                },
                {
                    "interests":[{"id": "6003242077675"},{"id": "6003103108917"}]
                }
            ],
            "geo_locations": {
                "countries": ["IN"],
                "location_types": ["home", "recent"]
            },
            "brand_safety_content_filter_levels": ["FACEBOOK_RELAXED"],#, "AN_RELAXED"
            "publisher_platforms": eval(adset_row['publisher_platforms']) if adset_row.get('publisher_platforms') else ["facebook"],
            "facebook_positions": eval(adset_row['facebook_positions']) if adset_row.get('facebook_positions') else ["feed"],
            "device_platforms": ["mobile", "desktop"] if adset_row["device"].strip().upper() == "ALL" else [adset_row["device"].strip().lower()],
            "audience_network_positions": ["classic"]
        }
    }

        # Initialize prediction_id to None
        prediction_id = None
        
        try:
            prediction = account.create_reach_frequency_prediction(fields=[], params=prediction_params)
            prediction_id = prediction.get("id")
            print(f"✅ Prediction Created: {prediction_id}")
        except Exception as e:
            print(f'❌ Reach Creation Failed: {e}')
            print(f"Campaign ID: {adset_row['campaign_id']}, Adset: {adset_row['adset_name']}")
            prediction_id = False

    if prediction_id:
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
            elif status == 2:
                time.sleep(10)
                print("⏳ Prediction is still processing...")
            else:
                print(f"❌ Prediction Failed with status: {status}")
                break

        # Step 5: Reserve the Prediction only if status is 1 (success)
        if status == 1:
            print("\n🔹 Reserving Prediction...")
            try:
                reserve = account.create_reach_frequency_prediction(fields=[], params={
                    "action": "reserve",
                    "rf_prediction_id": prediction_id
                })
                reserved_id = reserve.get("id")
                if reserved_id:
                    print(f"✅ Reservation successful. Reserved Prediction ID: {reserved_id}")
                else:
                    print("❌ Reservation failed - no ID returned")
                    continue
            except Exception as e:
                print(f"❌ Reservation failed: {e}")
                continue
        else:
            print(f"❌ Cannot reserve prediction - status is {status}")
            continue

        # Only create ad set if prediction was successful
        final_df.loc[(final_df['campaign_id'] == adset_row['campaign_id']) & (final_df['adset_name'] == adset_row['adset_name']), 'prediction_id'] = prediction_id

        # Create targeting spec for ad set with excluded locations
        adset_targeting = prediction_params["target_spec"].copy()
        adset_targeting["geo_locations"] = {
            "countries": ["IN"],
            "location_types": ["home", "recent"],
            "excluded_geo_locations": {
                "regions": [{"name": state.strip(), "country": "IN"} for state in eval(adset_row.get("exclude_states", "[]"))] if adset_row.get("exclude_states") and adset_row.get("exclude_states") != "[]" else [],
                "cities": [{"name": city.strip(), "country": "IN"} for city in eval(adset_row.get("exclude_cities", "[]"))] if adset_row.get("exclude_cities") and adset_row.get("exclude_cities") != "[]" else []
            }            
        }
        
        adset_params = {
            AdSet.Field.name: adset_row['adset_name'],
            AdSet.Field.campaign_id: adset_row['campaign_id'],
            AdSet.Field.billing_event: "IMPRESSIONS",
            AdSet.Field.optimization_goal: "REACH",
            AdSet.Field.rf_prediction_id: reserved_id,
            AdSet.Field.targeting: adset_targeting,
            AdSet.Field.status: "PAUSED"
        }
        try:
            print("\n🔹 Creating Ad Set...")
            adset = account.create_ad_set(fields=[], params=adset_params)
            adset_id = adset.get("id")
            adset_logs = 'NO ERROR'
            print(f"✅ Ad Set Created: {adset_id}")
        except Exception as e:
            adset_id = False
            adset_logs = e
            print(f"❌ Ad Set Creation Failed: {e}")

        final_df.loc[(final_df['campaign_id'] == adset_row['campaign_id']) & (final_df['adset_name'] == adset_row['adset_name']), 'adset_logs'] = adset_logs
        final_df.loc[(final_df['campaign_id'] == adset_row['campaign_id']) & (final_df['adset_name'] == adset_row['adset_name']), 'adset_id'] = adset_id
        
        print(f"✅ Ad Set ID {adset_id} assigned to adset {adset_row['adset_name']}")
        
        # Step 3: Process all ads for this adset
        ad_columns = Config_Data.ad_columns
        adset_ads = final_df[(final_df['campaign_name'] == cname) & (final_df['adset_name'] == adset_row['adset_name'])][ad_columns].drop_duplicates()
        
        # Check if there are any ads to process
        if adset_ads.empty:
            print("No ads detected for this adset.")
            continue
            
        for ad_idx, ad_row in adset_ads.iterrows():
            # Check if the row is empty (all values are NaN)
            if ad_row.isnull().all():
                print("No further ads detected for this adset.")
                break 
            print(f"\n--- Processing Ad: {ad_row['ad_name']} ---")
            
            # Update the ad row with the adset_id
            ad_row['adset_id'] = adset_id
            
            # Step 4: Create Ad Creative (Image or Video)
            creative_type = ad_row['ad_format']
            ad_name = ad_row['ad_name']
            headline = ad_row['headline']
            description = ad_row['description']
            message = ad_row['primary_text']
            link = ad_row['link']  
            image_path = r"sampleimage.png"
            video_path = r"sampleVideo.mp4"

            try:
                print(f"\n🎯 Starting ad creation process for: {ad_name}")
                print("=" * 50)
                
                if creative_type.lower() == "image":
                    print("📸 Creating image-based ad creative...")
                    creative_id = create_ad_creative(creative_type, image_path, ad_name, headline, description, message, link, ad_row['call_to_action'])
                else:
                    print("🎬 Creating video-based ad creative...")
                    creative_id = create_ad_creative(creative_type, video_path, ad_name, headline, description, message, link, ad_row['call_to_action'])

                # Step 5: Create Ad
                print("\n📢 Finalizing ad creation...")
                ad_id = create_ad(ad_row['adset_id'], creative_id, ad_name, ad_status="ACTIVE")
                ad_logs = 'NO ERROR'
                
                print(f"\n🎉 Ad Creation Complete!")
                print("=" * 50)
                print(f"✅ Campaign ID: {campaign_id}")
                print(f"✅ Prediction ID: {prediction_id}")
                print(f"✅ Reserved Prediction ID: {reserved_id}")
                print(f"✅ Ad Set ID: {adset_id}")
                print(f"✅ Creative ID: {creative_id}")
                print(f"✅ Ad ID: {ad_id}")
                print("=" * 50)
                
            except Exception as e:
                ad_id = False
                ad_logs = e
                print(f"❌ Ad Creation Failed: {e}")

            final_df.loc[final_df['ad_name'] == ad_row['ad_name'], 'ad_logs'] = ad_logs
            final_df.loc[final_df['ad_name'] == ad_row['ad_name'], 'ad_id'] = ad_id




final_df.to_csv('finaloutput.csv')
