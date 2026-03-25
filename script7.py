#overlap start is the maximum of all start times, and overlap end is the minimum of all end times. if overlap start < overlap end, then we have a valid meeting time. otherwise, no common time slot exists.

def find_overlap(all_availability):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    results = []
#loop thru ecah day and create an empty list for each one, which will store each persons slot for that specfic day. 
    for day in days:
        day_slots =[]
#2 nested loops. outer loop goes thru each person, inner loop goes thru each slot of that person, if the slot's day matches the current day we are processing, we add it to the day_slots list. after this nested loop, we have a list of all slots for that specific day, then we can find the overlap.
        for person in all_availability:
            for slot in person["slots"]:
                if slot["day"] == day:
                    day_slots.append({
                        "name": person["name"],
                        "start": slot["start"],
                        "end": slot["end"]
                    })
#if not everyone has a slot for that day, just skip. no point finding an overlap. continue will jump straight to next day in loop/ 
        if len(day_slots) < len(all_availability):
            continue
#impt part. time strings are in format HH:MM so we can compare them directly as strings/ 
        latest_start = max(slot["start"] for slot in day_slots)
        earliest_end = min(slot["end"] for slot in day_slots)
#if latest start is before earliest end, we have a valid overlap. if latest start was after earlioest end, it would mean there are no windows where every1 is free simultaenously/
        if latest_start < earliest_end:
            results.append({
                "day": day,
                "start": latest_start,
                "end": earliest_end
            })  

    return results
#display function. if no overlaps, print no overlapping availability. 
def display_overlap(results):
    if not results:
        print("No overlapping availability found.")
        return
    
    print("\n=== AVAILABLE MEETING TIMES ===\n")
    for slot in results:
        print(f"{slot['day']}: {slot['start']} to {slot['end']}")
if __name__ == "__main__":#just for testing overlap indedependtly
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