#combined all scripts for one single end to end flow. used claude to compile and refactor the code. 

import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
#added a few more categories because results are inconsistnent. same amendment for script4. 
VENUE_CATEGORIES = {
    "cafe": ["cafe", "bakery", "coffee", "tea"],
    "food": ["restaurant", "food", "bar", "meal_takeaway", "meal_delivery", "hawker", "food_court"],
    "park": ["park", "natural_feature", "campground", "beach"],
    "activity": ["movie_theater", "bowling_alley", "amusement_park", "gym", "shopping_mall", "stadium", "zoo", "aquarium", "night_club"],
    "culture": ["museum", "art_gallery", "library", "tourist_attraction", "place_of_worship"]
}

FREE_TYPES = {"park", "natural_feature", "library"}

def get_coordinates(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": API_KEY}
    response = requests.get(url, params=params) 
    data = response.json()
    location = data["results"][0]["geometry"]["location"]
    return location["lat"], location["lng"]

def get_geometric_midpoint(coordinates):
    avg_lat = sum(lat for lat, lng in coordinates) / len(coordinates)
    avg_lng = sum(lng for lat, lng in coordinates) / len(coordinates)
    return avg_lat, avg_lng

def get_commute_time_seconds(origin, destination_lat, destination_lng):
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": origin,
        "destinations": f"{destination_lat},{destination_lng}",
        "mode": "transit",
        "key": API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    element = data["rows"][0]["elements"][0]
    if element["status"] == "OK":
        return element["duration"]["value"]
    else:
        return None
    
def generate_candidates(midpoint_lat, midpoint_lng, radius=0.02, grid_size=3):
    candidates = []
    step = radius / grid_size
    for i in range(-grid_size, grid_size + 1):
        for j in range(-grid_size, grid_size + 1):
            lat = midpoint_lat + i * step
            lng = midpoint_lng + j * step
            candidates.append((lat, lng))
    return candidates

def find_fairest_meetup_point(addresses):
    coordinates = [get_coordinates(addr) for addr in addresses]
    midpoint = get_geometric_midpoint(coordinates)
    candidates = generate_candidates(midpoint[0], midpoint[1])

    best_candidate = None
    best_variance = float("inf")

    for candidate in candidates:
        times = []
        for address in addresses:
            time = get_commute_time_seconds(address, candidate[0], candidate[1])
            if time is not None:
                times.append(time)

        if len(times) == len(addresses):
            avg = sum(times) / len(times)
            variance = sum((t - avg) ** 2 for t in times) / len(times)
            if variance < best_variance:
                best_variance = variance
                best_candidate = candidate

    return best_candidate, best_variance

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
            "rating": place.get("rating", 0),
            "types": place["types"]
        }
        venues.append(venue)
    return venues

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

def filter_and_categorise(venues):
    filtered = []
    for venue in venues:
        category = categorise_venue(venue["types"])
        if category is None:
            continue
        venue["category"] = category
        venue["is_free"] = is_free(venue["types"])
        filtered.append(venue)
    filtered.sort(key=lambda x: x["rating"], reverse=True)
    return filtered

def display_results(addresses, best_point, variance, venues):
    print("\n=== THIRDSPACE RESULTS ===\n")
    print("Addresses entered:")
    for addr in addresses:
        print(f"  - {addr}")
    print(f"\nFairest meeting point: {best_point[0]:.4f}, {best_point[1]:.4f}")
    print(f"Commute time variance: {variance:.2f} seconds squared")
    print(f"\nVenue suggestions nearby:\n")

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

def run(addresses):
    print("Finding fairest meeting point...")
    best_point, variance = find_fairest_meetup_point(addresses)

    print("Fetching nearby venues...")
    venues = get_nearby_venues(best_point[0], best_point[1], radius=800)

    print("Filtering venues...")
    filtered = filter_and_categorise(venues)

    display_results(addresses, best_point, variance, filtered)

if __name__ == "__main__": #example address for testing. results keep showing up in other code. 
    addresses = [
    "Tampines, Singapore",
    "Jurong East, Singapore",
    "Woodlands, Singapore",
    "Queenstown, Singapore"
]

    run(addresses) 