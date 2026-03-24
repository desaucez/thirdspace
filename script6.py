import re

def parse_time(text):
    start_time = "08:00"
    end_time = "23:59"

    if "morning" in text:
        start_time = "08:00"
        end_time = "12:00"
    elif "afternoon" in text:
        start_time = "12:00"
        end_time = "17:00"
    elif "evening" in text:
        start_time = "17:00"
        end_time = "22:00"
    elif "all day" in text or "anytime" in text:
        start_time = "08:00"
        end_time = "23:59"

#claude help for the regex to extract time info. 
    time_match = re.search(r'after\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text)
    if not time_match:
        time_match = re.search(r'from\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text)
    if not time_match:
        time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)', text)

    if time_match:
        hour = int(time_match.group(1))
        minutes = time_match.group(2) or "00"
        period = time_match.group(3)

        if period == "pm" and hour != 12:
            hour += 12
        elif period == "am" and hour == 12:
            hour = 0
        elif period is None and hour < 8:
            hour += 12

        start_time = f"{hour:02d}:{minutes}"
        end_time = "23:59"

    return start_time, end_time

def parse_availability(name, message):
    message = message.lower()
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    day_positions = []
    for day in days:
        pos = message.find(day)
        if pos != -1:
            day_positions.append((pos, day))

    day_positions.sort()

    slots = []
    for i, (pos, day) in enumerate(day_positions):
        if i + 1 < len(day_positions):
            next_pos = day_positions[i + 1][0]
            chunk = message[pos:next_pos]
        else:
            chunk = message[pos:]

        start_time, end_time = parse_time(chunk)
        slots.append({
            "day": day.capitalize(),
            "start": start_time,
            "end": end_time
        })

    return {
        "name": name,
        "slots": slots
    }

availability_messages = [
    ("Ahmad", "I'm free Saturday after 2pm and Sunday morning"),
    ("Sarah", "Saturday evening works for me, or anytime Sunday"),
    ("Wei Ming", "Can do Saturday from 3pm onwards"),
    ("Priya", "Free all day Sunday, Saturday only after 4pm")
]

results = []
for name, message in availability_messages:
    print(f"Parsing {name}'s availability...")
    parsed = parse_availability(name, message)
    results.append(parsed)
    print(f"{name}: {parsed['slots']}\n")

print("All availability parsed successfully.")