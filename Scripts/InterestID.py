import os
import time
import requests
from dotenv import load_dotenv

# Load token from .env file
load_dotenv()
ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")

# Get user input for number of interests
while True:
    try:
        interest_count = int(input("Enter number of interests to generate (1-100): "))
        if 1 <= interest_count <= 100:
            break
        print("Please enter a number between 1 and 100")
    except ValueError:
        print("Please enter a valid number")

# List of interest keywords to search
keywords = [
    "fashion", "fitness", "technology", "travel", "food", "music", "movies", "shopping",
    "education", "business", "finance", "sports", "health", "beauty", "marketing",
    "automotive", "photography", "gaming", "yoga", "design", "lifestyle", "art", "home",
    "parenting", "entertainment", "wellness", "luxury", "gadgets", "nature", "news",
    "coding", "medicine", "startup", "entrepreneur", "finance", "investment", "architecture",
    "engineering", "productivity", "relationships","selfcare", "pets", "DIY", "career", "psychology", 
    "space", "environment", "sustainability", "culture", "finance tips", "crypto", "stocks"
]

def search_valid_interests(keyword, limit=2):
    url = "https://graph.facebook.com/v19.0/search"
    params = {
        "type": "adinterest",
        "q": keyword,
        "limit": limit,
        "access_token": ACCESS_TOKEN
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            print(f"⚠️ Error for '{keyword}':", response.json())
            return []
    except Exception as e:
        print(f"❌ Exception for '{keyword}':", e)
        return []

valid_interests = []
for kw in keywords:
    interests = search_valid_interests(kw)
    for interest in interests:
        valid_interests.append({
            "id": interest["id"],
            "name": interest["name"]
        })
    if len(valid_interests) >= interest_count:
        break
    time.sleep(0.3)  # gentle rate limiting

# Limit to requested count
valid_interests = valid_interests[:interest_count]

# Output the valid interests
print(f"\n✅ Total Valid Interests Collected: {len(valid_interests)}\n")
for i, interest in enumerate(valid_interests, 1):
    print(f"{i:2d}. {interest['name']} — ID: {interest['id']}")
