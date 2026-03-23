import requests 
import os 
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
print(f"API Key: {API_KEY}")

def get_commute_time(origin, destination):
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    
    params = {
        "origins": origin,
        "destinations": destination,
        "mode": "transit",
        "key": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    duration = data["rows"][0]["elements"][0]["duration"]["text"]
    print(f"Commute time from {origin} to {destination}: {duration}")
get_commute_time("Tampines, Singapore", "Orchard Road, Singapore")