from script5 import find_fairest_meetup_point, get_nearby_venues, filter_and_categorise
from script6 import parse_availability
from script7 import find_overlap

addresses = [
    "Tampines, Singapore",
    "Jurong East, Singapore"
]

availability_messages = [
    ("Russell", "Saturday 7pm to 10pm"),
    ("Hemz", "Saturday whole day")
]

best_point, variance = find_fairest_meetup_point(addresses)
venues = get_nearby_venues(best_point[0], best_point[1])
filtered = filter_and_categorise(venues)

all_availability = []
for name, message in availability_messages:
    parsed = parse_availability(name, message)
    print(f"{name}: {parsed}")
    all_availability.append(parsed)

overlap = find_overlap(all_availability)
print(f"\nOverlap: {overlap}")