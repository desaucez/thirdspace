#take the coordinates from script 2, and find real venues using the Places API. 

import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def get_nearby_venues(lat, lng, radius=1000):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": "establishment",
        "key": API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()

    venues = []
    for place in data["results"]:
        venue = {
            "name": place["name"],
            "address": place.get("vicinity", "No address available"),
            "rating": place.get("rating", "No rating"),
            "types":place["types"]
        }
        venues.append(venue)

    return venues

def display_venues(venues):
    print(f"\nFound {len(venues)} venues nearby:\n")
    for i, venue in enumerate(venues, 1):
        print(f"{i}. {venue['name']}")
        print(f"   Address: {venue['address']}")
        print(f"   Rating: {venue['rating']}")
        print(f"   Types: {', '.join(venue['types'][:3])}")
        print()

# Using the fairest meeting point from script2
lat = 1.3554727
lng = 103.841858025

venues = get_nearby_venues(lat, lng)
display_venues(venues)