from script5 import find_fairest_meetup_point, get_nearby_venues, filter_and_categorise
from script6 import parse_availability
from script7 import find_overlap
from script4 import VENUE_CATEGORIES

addresses = [
    "80 Robinson Road, Singapore",
    "822415, Singapore",
    "The Florida, Singapore",
    "The Glades, Singapore"
]

availability_messages = [
    ("Russell", "Saturday 10am to 6pm and Sunday 5pm to 10pm"),
    ("Hemz", "Saturday 4pm to 8pm and Sunday anytime")
]

best_point, variance = find_fairest_meetup_point(addresses)
venues = get_nearby_venues(best_point[0], best_point[1])
filtered = filter_and_categorise(venues)

print("\n=== VENUE SUGGESTIONS ===\n")
for category in VENUE_CATEGORIES.keys():
    category_venues = [v for v in filtered if v["category"] == category]
    if not category_venues:
        continue
    print(f"--- {category.upper()} ---")
    for venue in category_venues[:2]:
        free_label = "FREE" if venue["is_free"] else "PAID"
        print(f"  {venue['name']} ({venue['rating']}) | {free_label}")
        print(f"  {venue['address']}")
    print()

all_availability = []
for name, message in availability_messages:
    parsed = parse_availability(name, message)
    print(f"{name}: {parsed}")
    all_availability.append(parsed)

overlap = find_overlap(all_availability)
print(f"\nOverlap: {overlap}")