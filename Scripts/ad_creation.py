import os
import json
import tempfile
import base64
from dotenv import load_dotenv
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adimage import AdImage
from facebook_business.adobjects.advideo import AdVideo
from facebook_business.adobjects.ad import Ad
from facebook_business.api import FacebookAdsApi

load_dotenv()

# Load credentials from .env
FB_APP_ID = os.getenv("FB_APP_ID")
FB_APP_SECRET = os.getenv("FB_APP_SECRET")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
FB_AD_ACCOUNT_ID = os.getenv("FB_AD_ACCOUNT_ID")
FB_PAGE_ID = os.getenv("FB_PAGE_ID").replace("pg_", "")

# Initialize API
FacebookAdsApi.init(FB_APP_ID, FB_APP_SECRET, FB_ACCESS_TOKEN)


def get_image_hash(image_path):
    image_path = r"C:\Users\Admin\meta_ads_automation\sampleimage.png"
    """Upload image and get image hash."""
    print("Uploading image and generating hash...")
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
        image = AdAccount(FB_AD_ACCOUNT_ID).create_ad_image(
            fields=[], params={"bytes": encoded}
        )
    print("Image uploaded. Hash:", image["hash"])
    return image["hash"]


def get_video_id(video_path):
    """Upload video and get video ID."""
    print("Uploading video and generating ID...")
    video = AdVideo(parent_id=FB_AD_ACCOUNT_ID)
    video[AdVideo.Field.filepath] = video_path
    video.remote_create()
    video.waitUntilEncodingReady()
    print("Video uploaded. ID:", video.get_id())
    return video.get_id()



def create_ad_creative(creative_type, media_path, ad_name, headline, description, message, link, form_id):
    """Create ad creative for image or video."""
    creative_params = {
        "name": ad_name,
        "object_story_spec": {
            "page_id": FB_PAGE_ID,
        },
    }

    if creative_type.lower() == "image":
        image_hash = get_image_hash(media_path)
        creative_params["object_story_spec"]["link_data"] = {
            "image_hash": image_hash,
            "link": link,
            "message": message,
            "name": headline,
            "description": description,
            "call_to_action": {
                "type": "LEARN_MORE",
                "value": {
                    "link": "https://example.com/shop-now"
                }
            }
        }
    elif creative_type.lower() == "video":
        video_id = get_video_id(media_path)
        creative_params["object_story_spec"]["video_data"] = {
            "video_id": video_id,
            "title": headline,
            "message": message,
            "link_description": description,
            "image_hash": get_image_hash("C:\\Users\\Admin\\meta_ads_automation\\sampleimage.png"),  # Optional thumbnail
            "call_to_action": {
                "type": "LEARN_MORE",
                "value": {"link": "https://example.com/shop-now"}
            }
        }
    else:
        raise ValueError("Invalid creative_type. Must be 'image' or 'video'.")

    print("Creating ad creative with params:", json.dumps(creative_params, indent=2))
    creative = AdAccount(FB_AD_ACCOUNT_ID).create_ad_creative(fields=[], params=creative_params)
    print("Creative ID:", creative["id"])
    return creative["id"]


def create_ad(adset_id, creative_id, ad_name, ad_status="ACTIVE"):
    """Create ad under specified adset."""
    ad_params = {
        "name": ad_name,
        "adset_id": adset_id,
        "creative": {"creative_id": creative_id},
        "status": ad_status.upper()
    }
    print("Creating ad with params:", json.dumps(ad_params, indent=2))
    ad = AdAccount(FB_AD_ACCOUNT_ID).create_ad(fields=[], params=ad_params)
    print("Ad created successfully. ID:", ad["id"])
    return ad["id"]


# Example call for manual run (you can replace with dynamic args or CLI)
if __name__ == "__main__":
    adset_id = "120229463091200477"  
    form_id = ""  # Optional: only needed for Lead Ads; 
    media_path = r"C:\Users\Admin\meta_ads_automation\sampleVideo.mp4"
    creative_type = "video"  
    ad_name = "TestRnFADGauravUP1vid"
    headline = "Upgrade Your Lifestyle Today!"
    description = "Discover top-rated products for your everyday needs."
    message = "🚀 Fast delivery, great prices, and premium quality. Shop now!"
    link = "https://example.com/shop-now"


    creative_id = create_ad_creative(
        creative_type=creative_type,
        media_path=media_path,
        ad_name=ad_name,
        headline=headline,
        description=description,
        message=message,
        link=link,
        form_id=form_id
    )
    ad_id = create_ad(adset_id=adset_id, creative_id=creative_id, ad_name=ad_name)
