#seperate useful venues like parks and cafes, malls etc from places like govt offices and schools

import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

VENUE_CATEGORIES = {
    "cafe": ["cafe", "bakery", "coffee"],
    "food": ["restaurant", "food", "bar", "meal_takeaway"],
    "park": ["park", "natural_feature"],
    "activity": ["movie_theater", "bowling_alley", "amusement_park", "gym", "shopping_mall"],
    "culture": ["museum", "art_gallery", "library"]
}

FREE_TYPES = {"park", "natural_feature", "library"}

def categorise_venue(types): 
    for category, keywords in VENUE_CATEGORIES.items():
        for keyword in keywords:
            if keyword in types:
                return category
            
    return None

def is_free(types):
    for t in types:
        if t in FREE_TYPES:
            return True
    return False

def get_nearby_venues(lat, lng, radius=1000):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "key": API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
 
    venues = []
    for place in data["results"]:
        venue = {
            "name": place["name"],
            "address": place.get("vicinity", "No address available"),
            "rating": place.get("rating", 0),
            "types": place["types"],
        }
        venues.append(venue)

    return venues

def filter_and_categorise(venues):
    filtered= []

    for venue in venues:
        category = categorise_venue(venue["types"])
        if category is None:
            continue

        venue["category"] = category
        venue["is_free"] = is_free(venue["types"])
        filtered.append(venue)

    filtered.sort(key=lambda x: x["rating"], reverse=True)
    return filtered

def display_filtered_venues(venues):
    if not venues:
        print("No relevant venues found")
        return
    
    print(f"\nFound {len(venues)} relevant venues: \n")

    for category in VENUE_CATEGORIES.keys():
        category_venues = [v for v in venues if v["category"] == category]
        if not category_venues:
            continue

        print(f"--- {category.upper()} ---")
        for venue in category_venues:
            free_label = "FREE" if venue["is_free"] else "PAID"
            print(f"  {venue['name']}")
            print(f"  Address: {venue['address']}")
            print(f"  Rating: {venue['rating']} | {free_label}")
            print()

lat = 1.3554727
lng = 103.841858025

venues = get_nearby_venues(lat, lng)
filtered = filter_and_categorise(venues)
display_filtered_venues(filtered)