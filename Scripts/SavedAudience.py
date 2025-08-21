#!/usr/bin/env python3
"""
Create a Saved Audience (SAVED_AUDIENCE) in the Ad Account using a full targeting spec.
Put your FB_ACCESS_TOKEN and FB_AD_ACCOUNT_ID in environment variables (or load via dotenv).
"""

import os
import json
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.customaudience import CustomAudience

# Optional: uncomment if you keep credentials in a .env file
load_dotenv()

ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
AD_ACCOUNT_ID = os.getenv("FB_AD_ACCOUNT_ID")  # either '12345' or 'act_12345'

if not ACCESS_TOKEN or not AD_ACCOUNT_ID:
    raise SystemExit("Please set FB_ACCESS_TOKEN and FB_AD_ACCOUNT_ID environment variables")

# Ensure ad account id has act_ prefix
if not AD_ACCOUNT_ID.startswith("act_"):
    AD_ACCOUNT_ID = f"act_{AD_ACCOUNT_ID}"

# Init SDK
FacebookAdsApi.init(access_token=ACCESS_TOKEN)

# ----------------------------
# Targeting Spec (from your payload)
# ----------------------------
target_spec = {
    "age_min": 25,
    "age_max": 55,
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
    "exclusions": {
        "interests": [
            {"id": "6003023855850"}, {"id": "6003232518610"}, {"id": "6003737012891"},
            {"id": "6003349442621"}, {"id": "6003396473977"}
        ]
    },
    "geo_locations": {
        "countries": ["IN"],
        "location_types": ["home", "recent"]
    },
    # Note: excluded_geo_locations sometimes requires keys/IDs; using names may work,
    # but if API rejects them you'll need to replace with the targeting-search keys.
    "excluded_geo_locations": {
        "regions": [
            {"name": "Bihar", "country": "IN"},
            {"name": "Rajasthan", "country": "IN"}
        ],
        "cities": [
            {"name": "Mumbai", "country": "IN"},
            {"name": "Dehra Dun", "country": "IN"}
        ]
    },
    "brand_safety_content_filter_levels": ["FACEBOOK_RELAXED"],
    "publisher_platforms": ["facebook"],           # keep only facebook if you don't want AN
    "facebook_positions": ["feed"],
    "device_platforms": ["mobile", "desktop"],
    "audience_network_positions": ["classic"]
}

# ----------------------------
# Saved audience params and create call
# ----------------------------
audience_name = "Medulla Saved Audience - Full Spec"
audience_description = "Saved audience created from given targeting spec (includes exclusions & excluded locations)."

params = {
    CustomAudience.Field.name: audience_name,
    CustomAudience.Field.subtype: CustomAudience.Subtype.saved_audience,
    CustomAudience.Field.description: audience_description,
    CustomAudience.Field.account_id: AD_ACCOUNT_ID.replace("act_", ""),
    CustomAudience.Field.targeting: target_spec,
}

try:
    acct = AdAccount(AD_ACCOUNT_ID)
    saved_audience = acct.create_custom_audience(fields=[], params=params)
    audience_id = saved_audience.get("id") or saved_audience.get(CustomAudience.Field.id)
    print("✅ Saved Audience created successfully.")
    print("Audience ID:", audience_id)
    print("Full response:", json.dumps(saved_audience, indent=2))
except Exception as e:
    print("❌ Failed to create saved audience:")
    print(type(e), e)
    # Print more details if SDK returned a dict-like error
    try:
        import traceback
        traceback.print_exc()
    except:
        pass
