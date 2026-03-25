import re

def parse_time(text):
    start_time = "08:00"
    end_time = "23:59"
#fallback values if no specific time is found. 
    if "morning" in text:
        start_time = "08:00"
        end_time = "12:00"
    elif "afternoon" in text:
        start_time = "12:00"
        end_time = "17:00"
    elif "evening" in text:
        start_time = "17:00"
        end_time = "22:00"
    #added whole day and anytime as options for free all day 
    elif "all day" in text or "anytime" in text or "whole day" in text: 
        start_time = "08:00"
        end_time = "23:59"
    #regex that looks for time ranges. so looks for numbers, optional  minutes and am pm, and then a - or to, and then again for a number, optional minutes and optional am pm. so can input things like 7pm -10pm.
    range_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\s*(?:to|-)\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text)
    #extract all 6 captured values from regex match 
    if range_match:
        start_hour = int(range_match.group(1))
        start_min = range_match.group(2) or "00"
        start_period = range_match.group(3)
        end_hour = int(range_match.group(4))
        end_min = range_match.group(5) or "00"
        end_period = range_match.group(6)
#same conversion for end time, but also added a condition where if someone says 7pm to 10, (no am pm on the 10) , we know that 10 means 2200, as it is less than 19 hours(7pm). Essentially, instead of checking if the hour is less than 8, we check if it is less than the start hour. 
        if start_period == "pm" and start_hour != 12:
            start_hour += 12
        elif start_period == "am" and start_hour == 12:
            start_hour = 0
        if start_period is None and start_hour < 8:
            start_hour += 12

        if end_period == "pm" and end_hour != 12:
            end_hour += 12
        elif end_period == "am" and end_hour == 12:
            end_hour = 0
        elif end_period is None and end_hour < start_hour:
            end_hour += 12
        # format and returns times in HH:MM, then exit function. return is used so if range is found, do not continue to single time match logic 
        start_time = f"{start_hour:02d}:{start_min}"
        end_time = f"{end_hour:02d}:{end_min}"
        return start_time, end_time
    #only runs if no time match is found above
    single_match = re.search(r'(?:after|from)\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text)
    if not single_match:
        single_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)', text)

    if single_match:
        hour = int(single_match.group(1))
        minutes = single_match.group(2) or "00"
        period = single_match.group(3)

        if period == "pm" and hour != 12:
            hour += 12
        elif period == "am" and hour == 12:
            hour = 0
        elif period is None and hour < 8:
            hour += 12

        start_time = f"{hour:02d}:{minutes}"
        end_time = "23:59"

    return start_time, end_time

#claude help for the regex to extract time info. first one, looks for after X from X, then a raw time with am/pm. 
    time_match = re.search(r'after\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text)
    if not time_match:
        time_match = re.search(r'from\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text)
    if not time_match:
        time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)', text)
#group 1 is hours, group 2 is minutes which is optional, and defaults to 00 if not provided. group 3 is am/pm also optional 
    if time_match:
        hour = int(time_match.group(1))
        minutes = time_match.group(2) or "00"
        period = time_match.group(3)
#conv to 24 hr format. 3rd condition is for a bug, in the case wheere if no am/pm specified, and hour is less than 8, we assume it is pm, bcause for example nobody will meet at 4am, so we will take it as 1600hrs.
        if period == "pm" and hour != 12:
            hour += 12
        elif period == "am" and hour == 12:
            hour = 0
        elif period is None and hour < 8:
            hour += 12

        start_time = f"{hour:02d}:{minutes}"
        end_time = "23:59"

    return start_time, end_time
#also a bug fix. instead of finding which days appear, we find position of each day in the messsage using message.find(day), which returns the character position. store each day alongside its position, then sort so we can processs days in order they appear in message 
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
    # claude help for this. For each day, remove the relevant portion of the message. If Ahmad says "Saturday after 2pm and Sunday morning", we slice "saturday after 2pm and " as Saturday's chunk and "sunday morning" as Sunday's chunk. then each chunk is parsed indepednetly/. Sat is 1400hrs, sun is 0800hrs-1200hrs 
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
    if not slots: #no day detected bug fix. to handle cases where people say something like whole day. 
        return{"name":name, 
               "slots":[],
               "error":"No day mentioned. Please include a day like Saturday or Sunday."}
    return {
        "name": name,
        "slots": slots
    }
if __name__ == "__main__": #for testing only
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