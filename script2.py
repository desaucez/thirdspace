#need to handle multiple addresses and a midpoint(not by distance, butby commute timing, so a commute equalised midpoint)
#so what i will do is take everyone's address and change to coordinates, using the geocoding api. 
#then i will get the geometric midpoint of the coordinates, so i will get a central point to start from
#then generate a set of candidate locations around that midpoint, so a grid of points within a radius
#for each candidate point, i will call dist matrix api to get commute times from every persons address to that point
#for eacg candidate, calculate the variance in commute times for all users, becuse variance will measure how unequal times are
#i will pick the candidate with the lowest variance, so the most equal commute times, as the fairest location

import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def get_coordinates(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    location= data["results"][0]["geometry"]["location"]
    return location["lat"], location["lng"]

def get_geometric_midpoint(coordinates):
    avg_lat = sum(coord[0] for coord in coordinates) / len(coordinates)
    avg_lng = sum(coord[1] for coord in coordinates) / len(coordinates)
    return avg_lat, avg_lng

def get_commute_time_seconds(origin, destination_lat, destination_lng):
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": origin,
        "destinations": f"{destination_lat},{destination_lng}",
        "key": API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    element = data["rows"][0]["elements"][0]
    if element["status"]=="OK":
        return element["duration"]["value"] 
    return None

def generate_candidates(midpoint_lat, midpoint_lng, radius=0.02, grid_size=3 ): 
    candidates = []
    for i in range(-grid_size, grid_size + 1):
        for j in range(-grid_size, grid_size + 1):
            lat = midpoint_lat + i * radius
            lng = midpoint_lng + j * radius
            candidates.append((lat, lng))
    return candidates

def find_fairest_meetup_point(addresses):
    print("Getting coordinates for all addresses...")
    coordinates = [get_coordinates(addr) for addr in addresses]

    print("Calculating geometric midpoint...")
    midpoint = get_geometric_midpoint(coordinates)
    print(f"Midpoint: {midpoint}")

    print("Generating candidate locations...")
    candidates = generate_candidates(midpoint[0], midpoint[1])

    best_candidate = None
    best_variance = float("inf")

    print("Finding fairest meetup point...")
    for candidates in candidates:
        times = []
        for address in addresses:
            time = get_commute_time_seconds(address, candidates[0], candidates[1])
            if time is not None:
                times.append(time)

        if len(times) == len(addresses):
            avg = sum(times) / len(times)
            variance = sum((t - avg) ** 2 for t in times) / len(times)

            if variance < best_variance:
                best_variance = variance
                best_candidate = candidates 

    print(f"\nFairest meeting point coordinates: {best_candidate}")
    print(f"Variance in commute times: {best_variance:.2f} seconds squared")
    return best_candidate

addresses = [
    "Tampines, Singapore",
    "Jurong East, Singapore",
    "Woodlands, Singapore",
    "Queenstown, Singapore"
]

find_fairest_meetup_point(addresses)