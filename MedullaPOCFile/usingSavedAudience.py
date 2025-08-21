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
# Removed SavedAudience import - we'll use account.get_saved_audiences instead
from config import Config_Data
import pandas as pd
from date_time_stripper import Stripper
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

# Get the saved audience ID for logging purposes and to derive exclusions
saved_audience_id = "120230031807900477"

# Log what audiences we're working with and fetch Saved Audience targeting
print(f"🎯 Saved Audience ID (for reference): {saved_audience_id}")
sa_targeting = {}
try:
    sa = next((s for s in account.get_saved_audiences(fields=['id','name','targeting'], params={'limit': 500}) if str(s.get('id')) == str(saved_audience_id)), None)
    if sa:
        print(f"🎯 Saved Audience Name: {sa.get('name')} ({saved_audience_id})")
        sa_targeting = sa.get('targeting') or {}
    else:
        print("⚠️ Saved Audience not found in account")
except Exception as e:
    print(f"⚠️ Could not fetch Saved Audience details: {e}")

# Build exclusions from the Saved Audience targeting
def _to_plain(value):
    if isinstance(value, dict):
        return {k: _to_plain(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_plain(v) for v in value]
    return value

sa_targeting = _to_plain(sa_targeting)

# Flatten Saved Audience flexible_spec into direct keys suitable for `exclusions`
aggregated_exclusions = {}
saved_excluded_geo = None
saved_included_geo = None

def _extend_agg(key, items):
    if not items:
        return
    existing = aggregated_exclusions.get(key, [])
    # Deduplicate by id where available
    seen = {str(x.get('id')) for x in existing if isinstance(x, dict) and x.get('id')}
    for it in items:
        if isinstance(it, dict) and it.get('id'):
            if str(it['id']) not in seen:
                existing.append({"id": str(it['id'])})
                seen.add(str(it['id']))
        else:
            if it not in existing:
                existing.append(it)
    aggregated_exclusions[key] = existing

if isinstance(sa_targeting, dict):
    flex = sa_targeting.get('flexible_spec') or []
    if isinstance(flex, list):
        for group in flex:
            if not isinstance(group, dict):
                continue
            for k in [
                'interests','behaviors','life_events','industries','income',
                'family_statuses','home_ownership','user_device','user_os',
                'wireless_carrier','user_adclusters'
            ]:
                if group.get(k):
                    _extend_agg(k, group.get(k))
    # Some saved audiences may have direct top-level lists too
    for k in [
        'interests','behaviors','life_events','industries','income',
        'family_statuses','home_ownership','user_device','user_os',
        'wireless_carrier','user_adclusters'
    ]:
        if sa_targeting.get(k):
            _extend_agg(k, sa_targeting.get(k))
    # If the saved audience itself defines an exclusions block, merge it as well
    if isinstance(sa_targeting.get('exclusions'), dict):
        for k in [
            'interests','behaviors','life_events','industries','income',
            'family_statuses','home_ownership','user_device','user_os',
            'wireless_carrier','user_adclusters'
        ]:
            if sa_targeting['exclusions'].get(k):
                _extend_agg(k, sa_targeting['exclusions'].get(k))

    # Geo: capture both included and excluded pieces from Saved Audience
    if sa_targeting.get('geo_locations'):
        saved_included_geo = sa_targeting.get('geo_locations')
    if sa_targeting.get('excluded_geo_locations'):
        saved_excluded_geo = sa_targeting.get('excluded_geo_locations')

saved_exclusions = aggregated_exclusions if aggregated_exclusions else None

if saved_exclusions:
    print("🧩 Applying Saved Audience exclusions (interests/behaviors/etc.)")
if saved_excluded_geo:
    print("🧭 Applying Saved Audience excluded_geo_locations")
if saved_included_geo:
    inc_regions = len(saved_included_geo.get('regions') or []) if isinstance(saved_included_geo, dict) else 0
    inc_cities = len(saved_included_geo.get('cities') or []) if isinstance(saved_included_geo, dict) else 0
    print(f"🗺️ Saved Audience included geo (will be used as exclusions): regions={inc_regions}, cities={inc_cities}")

# Note: We will not use excluded_custom_audiences; we'll derive exclusions from the Saved Audience targeting

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

# Filtering campaign columns
camp_cols = Config_Data.campaign_columns

# READ THE INPUT FILE - AND CREATE A DATAFRAME
df = pd.read_csv("MedullaPOCFILE.csv")
final_df = df.copy()

# Initialize result columns to avoid pandas SettingWithCopy warnings
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
    # Skip empty or invalid campaign rows
    if camp_row.isnull().all():
        print("No further campaigns detected.")
        break
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
            if start_time_str is None or stop_time_str is None:
                print(f"Skipping row with invalid dates: start_date={adset_row['start_date']}, end_date={adset_row['end_date']}")
                continue
                
            # Handle datetime strings with or without timezone info
            try:
                start_dt = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S%z")
                stop_dt = datetime.strptime(stop_time_str, "%Y-%m-%dT%H:%M:%S%z")
            except ValueError:
                start_dt = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S")
                stop_dt = datetime.strptime(stop_time_str, "%Y-%m-%dT%H:%M:%S")
        except (ValueError, TypeError) as e:
            print(f"Date parsing error: {e}")
            continue

        # Build exclusions for geo using: included geo (as negatives) + explicit excluded geo from Saved Audience
        combined_excluded_geo = None
        if saved_included_geo or saved_excluded_geo:
            # Only exclude regions and cities to avoid excluding entire country 'IN'
            combined_excluded_geo = {"regions": [], "cities": []}
            if isinstance(saved_excluded_geo, dict):
                combined_excluded_geo["regions"].extend(saved_excluded_geo.get("regions", []) or [])
                combined_excluded_geo["cities"].extend(saved_excluded_geo.get("cities", []) or [])
            if isinstance(saved_included_geo, dict):
                # Treat included regions/cities from Saved Audience as exclusions for our ad set
                combined_excluded_geo["regions"].extend(saved_included_geo.get("regions", []) or [])
                combined_excluded_geo["cities"].extend(saved_included_geo.get("cities", []) or [])
            # Deduplicate regions/cities (dicts)
            def _dedupe_places(items):
                seen = set()
                result = []
                for it in items:
                    if not isinstance(it, dict):
                        continue
                    key = (str(it.get("name", "")).lower(), str(it.get("country", "")).upper())
                    if key not in seen:
                        seen.add(key)
                        result.append({k: v for k, v in it.items() if v is not None})
                return result
            combined_excluded_geo["regions"] = _dedupe_places(combined_excluded_geo["regions"])
            combined_excluded_geo["cities"] = _dedupe_places(combined_excluded_geo["cities"])
            print(f"🧭 Excluded locations (Saved Audience derived) → regions: {len(combined_excluded_geo['regions'])}, cities: {len(combined_excluded_geo['cities'])}")

        prediction_params = {
            "campaign_id": adset_row['campaign_id'],
            "objective": adset_row['objective'],
            "optimization_goal": "REACH",
            "start_time": int(start_dt.timestamp()),
            "end_time": int(stop_dt.timestamp()),
            "budget": int(adset_row['adset_budget_amount']),
            "buying_type": adset_row['buy_type'],
            "frequency_cap": int(adset_row['frequency_cap']),
            "interval_frequency_cap_reset_period": 96,  # 96 hours = 4 days
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
                            {"id": "6003348604581"}, {"id": "6003396051089"}, {"id": "6003384248805"},
                            {"id": "6003277229371"}, {"id": "6003985771306"}, {"id": "6003164535634"},
                            {"id": "6004160395895"}, {"id": "6003211401886"}, {"id": "6003266061909"},
                            {"id": "6009248606271"}, {"id": "6003020834693"}, {"id": "6003029869785"},
                            {"id": "6003139266461"}, {"id": "6003161475030"}, {"id": "6003263791114"},
                            {"id": "6003346592981"}, {"id": "6003327060545"}, {"id": "6003270811593"},
                            {"id": "6003402305839"}, {"id": "6003248297213"}, {"id": "6003130044117"},
                            {"id": "6003143720966"}, {"id": "6003269553527"}, {"id": "6003540150873"},
                            {"id": "6003258544357"}, {"id": "6003382102565"}, {"id": "6002867432822"},
                            {"id": "6003088846792"}, {"id": "6003279598823"}, {"id": "6003403706343"},
                            {"id": "6003304550260"}, {"id": "6003641420907"}, {"id": "6003109198633"},
                            {"id": "6003057392644"}, {"id": "6004922412789"}, {"id": "6003306084421"},
                            {"id": "6004920030448"}, {"id": "6003649983713"}, {"id": "6002920953955"},
                            {"id": "6003502352425"}, {"id": "6003392552125"}, {"id": "6002989694968"},
                            {"id": "6003594228273"}
                        ]
                    },
                    {
                        "interests": [
                            {"id": "6003456388203"}, {"id": "6003418314031"}, {"id": "6003526234370"},
                            {"id": "6003188355978"}, {"id": "6003372784175"}
                        ]
                    }
                ],
                # Apply exclusions derived from Saved Audience targeting (not using excluded_custom_audiences)
                **({"exclusions": saved_exclusions} if saved_exclusions else {}),
                **({"excluded_geo_locations": combined_excluded_geo} if combined_excluded_geo else {}),
                "geo_locations": {
                    "countries": ["IN"],
                    "location_types": ["home", "recent"]
                },
                "brand_safety_content_filter_levels": ["FACEBOOK_RELAXED"],
                "publisher_platforms": eval(adset_row['publisher_platforms']) if adset_row.get('publisher_platforms') else ["facebook"],
                "facebook_positions": eval(adset_row['facebook_positions']) if adset_row.get('facebook_positions') else ["feed"],
                "device_platforms": ["mobile", "desktop"] if adset_row["device"].strip().upper() == "ALL" else [adset_row["device"].strip().lower()],
                "audience_network_positions": ["classic"]
            }
        }
    
        prediction_id = None
        try:
            prediction = account.create_reach_frequency_prediction(fields=[], params=prediction_params)
            prediction_id = prediction.get("id")
            print(f"✅ Prediction Created: {prediction_id}")
        except Exception as e:
            print(f"❌ Reach Creation Failed: {e}")
            print(f"Campaign ID: {adset_row['campaign_id']}, Adset: {adset_row['adset_name']}")
            prediction_id = False

        if not prediction_id:
            continue

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

        # Step 5: Reserve the Prediction if successful
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

        # Save the prediction ID
        final_df.loc[(final_df['campaign_id'] == adset_row['campaign_id']) & (final_df['adset_name'] == adset_row['adset_name']), 'prediction_id'] = prediction_id

        # Prepare targeting for ad set creation; mirror prediction targeting
        adset_targeting = prediction_params["target_spec"].copy()
        adset_targeting.pop('exclusions', None)
        # Re-apply exclusions derived from Saved Audience for prediction-only fields
        if saved_exclusions:
            # Note: R&F ad sets ignore detailed targeting exclusions at creation time
            adset_targeting['exclusions'] = saved_exclusions
        if combined_excluded_geo:
            # For ad set, place excluded geo under geo_locations for UI to display
            geo = adset_targeting.get('geo_locations') or {}
            geo['excluded_geo_locations'] = combined_excluded_geo
            adset_targeting['geo_locations'] = geo
        
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

        # CONFIRMATION STEP: Fetch ad set details from Meta API to verify exclusions were applied
        print(f"\n🔍 CONFIRMATION: Fetching ad set details from Meta API to verify exclusions...")
        try:
            # Fetch the created ad set with targeting details
            adset_obj = AdSet(adset_id)
            adset_details = adset_obj.api_get(fields=[
                'id', 'name', 'targeting', 'status'
            ])
            
            print(f"📋 Ad Set Details Retrieved:")
            print(f"   ID: {adset_details.get('id')}")
            print(f"   Name: {adset_details.get('name')}")
            print(f"   Status: {adset_details.get('status')}")
            
            # Check targeting structure
            targeting = adset_details.get('targeting', {})
            if targeting:
                print(f"   📍 Geo Locations: {targeting.get('geo_locations', 'Not set')}")
                if targeting.get('geo_locations', {}).get('excluded_geo_locations'):
                    excluded_geo = targeting['geo_locations']['excluded_geo_locations']
                    print(f"   🚫 Excluded Geo Locations: {excluded_geo}")
                else:
                    print(f"   🚫 Excluded Geo Locations: None found")
                
                if targeting.get('exclusions'):
                    exclusions = targeting['exclusions']
                    print(f"   🚫 Detailed Targeting Exclusions: {exclusions}")
                else:
                    print(f"   🚫 Detailed Targeting Exclusions: None found")
            else:
                print(f"   📍 Targeting: Not set or empty")
                
        except Exception as e:
            print(f"⚠️ Could not fetch ad set details for confirmation: {e}")

        # Step 6: Process all ads for this adset
        ad_columns = Config_Data.ad_columns
        adset_ads = final_df[(final_df['campaign_name'] == cname) & (final_df['adset_name'] == adset_row['adset_name'])][ad_columns].drop_duplicates()
        
        if adset_ads.empty:
            print("No ads detected for this adset.")
            continue
        
        for ad_idx, ad_row in adset_ads.iterrows():
            if ad_row.isnull().all():
                print("No further ads detected for this adset.")
                break
            print(f"\n--- Processing Ad: {ad_row['ad_name']} ---")
            ad_row['adset_id'] = adset_id

            if not adset_id:
                print("Adset creation failed; skipping ad creation.")
                ad_id = False
                ad_logs = 'ADSET_CREATION_FAILED'
                final_df.loc[final_df['ad_name'] == ad_row['ad_name'], 'ad_logs'] = ad_logs
                final_df.loc[final_df['ad_name'] == ad_row['ad_name'], 'ad_id'] = ad_id
                continue
            
            # Step 7: Create Ad Creative and Ad
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

                # Create Ad
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

# Save results to CSV
final_df.to_csv('finaloutput.csv', index=False)
