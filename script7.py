#overlap start is the maximum of all start times, and overlap end is the minimum of all end times. if overlap start < overlap end, then we have a valid meeting time. otherwise, no common time slot exists.

def find_overlap(all_availability):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    results = []

    for day in days:
        day_slots =[]

        for person in all_availability:
            for slot in person["slots"]:
                if slot["day"] == day:
                    day_slots.append({
                        "name": person["name"],
                        "start": slot["start"],
                        "end": slot["end"]
                    })

        if len(day_slots) < len(all_availability):
            continue

        latest_start = max(slot["start"] for slot in day_slots)
        earliest_end = min(slot["end"] for slot in day_slots)

        if latest_start < earliest_end:
            results.append({
                "day": day,
                "start": latest_start,
                "end": earliest_end
            })  

    return results

def display_overlap(results):
    if not results:
        print("No overlapping availability found.")
        return
    
    print("\n=== AVAILABLE MEETING TIMES ===\n")
    for slot in results:
        print(f"{slot['day']}: {slot['start']} to {slot['end']}")

all_availability = [
    {
        "name": "Ahmad",
        "slots": [
            {"day": "Saturday", "start": "14:00", "end": "23:59"},
            {"day": "Sunday", "start": "08:00", "end": "12:00"}
        ]
    },
    {
        "name": "Sarah",
        "slots": [
            {"day": "Saturday", "start": "17:00", "end": "22:00"},
            {"day": "Sunday", "start": "08:00", "end": "23:59"}
        ]
    },
    {
        "name": "Wei Ming",
        "slots": [
            {"day": "Saturday", "start": "15:00", "end": "23:59"}
        ]
    },
    {
        "name": "Priya",
        "slots": [
            {"day": "Sunday", "start": "08:00", "end": "23:59"},
            {"day": "Saturday", "start": "16:00", "end": "23:59"}
        ]
    }
]

overlap = find_overlap(all_availability)
display_overlap(overlap)