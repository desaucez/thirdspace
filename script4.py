#seperate useful venues like parks and cafes, malls etc from places like govt offices and schools

import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

#dictionary that maps own category names to google's type tags
VENUE_CATEGORIES = {
    "cafe": ["cafe", "bakery", "coffee", "tea"],
    "food": ["restaurant", "food", "bar", "meal_takeaway", "meal_delivery", "hawker", "food_court"],
    "park": ["park", "natural_feature", "campground", "beach"],
    "activity": ["movie_theater", "bowling_alley", "amusement_park", "gym", "shopping_mall", "stadium", "zoo", "aquarium", "night_club"],
    "culture": ["museum", "art_gallery", "library", "tourist_attraction", "place_of_worship"]
}
#list of places google type tags that are considered free
FREE_TYPES = {"park", "natural_feature", "library"}
#function to that takes the venues list of types, and figures out which categoriues it belongs to. loops through each category in VENUE_CATEGORIES, and checks if any of the google type tags for that category are in the venue's types. if finds a match, returns the category name. if no match found after checking all categories, returns None
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
#main filtering function. loops thru every venue, calls categorise_venue to see if relevant. if None, hits continue. skips that venue and moves on to the next. if valid category, adds two new keys to the dictionary, category and is_free. after the loop, filtered.sort sorts list from hgihest to lowest. lambda x is a small inline fucntion that sorts.(claude helped with this) 
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
#displays the result grouped by catgeory. 
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
if __name__ == "__main__":
    lat = 1.3554727
    lng = 103.841858025
    venues = get_nearby_venues(lat, lng)
    filtered = filter_and_categorise(venues)
    display_filtered_venues(filtered)