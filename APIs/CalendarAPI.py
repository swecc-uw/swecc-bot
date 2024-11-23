import requests, os, logging, pytz
import re
from dateutil.rrule import rrulestr
from datetime import datetime
from dotenv import load_dotenv


logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s')

class CalendarAPI:
    def __init__(self):
        load_dotenv()
        self.url = os.getenv('CALENDAR_URL')
    
    def get_url(self):
        return self.url

    def get_suffix(self, day):
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][day % 10 - 1]
        return str(day) + suffix
    
    def format_date(self, local_start, local_end):
        formatted_date = local_start.strftime('%a, %b ')  
        day_with_suffix = self.get_suffix(local_start.day) 

        formatted_start_time = local_start.strftime('%I:%M %p').lstrip("0") 
        formatted_end_time = local_end.strftime('%I:%M %p').lstrip("0")  

        return f"{formatted_date}{day_with_suffix} {formatted_start_time} - {formatted_end_time}"


    def create_return_format(self, event):
        return {
                "name": event.name,
                "date": self.format_date(event.begin.datetime, event.end.datetime),
                "location": event.location,
                "description": event.description,
        }
    
    async def get_next_meeting(self):
        response = requests.get(self.url)
        response.raise_for_status()

        calendar_text = response.text
        now = datetime.now(pytz.utc)
        next_event = None

        event_tz = pytz.timezone("America/Los_Angeles")

        events = re.split(r"BEGIN:VEVENT", calendar_text)

        for raw_event in events:
            if "DTSTART" not in raw_event:
                continue

            dtstart_match = re.search(r"DTSTART;TZID=America/Los_Angeles:(\d+T\d+)", raw_event)
            dtend_match = re.search(r"DTEND;TZID=America/Los_Angeles:(\d+T\d+)", raw_event)
            rrule_match = re.search(r"RRULE:(.*)", raw_event)

            if not dtstart_match or not dtend_match:
                continue

            dtstart = event_tz.localize(datetime.strptime(dtstart_match.group(1), "%Y%m%dT%H%M%S"))
            dtend = event_tz.localize(datetime.strptime(dtend_match.group(1), "%Y%m%dT%H%M%S"))

            dtstart_utc = dtstart.astimezone(pytz.utc)

            if not rrule_match:
                if dtstart_utc > now:
                    if not next_event or dtstart_utc < next_event[0]:
                        next_event = (dtstart, dtend, raw_event)
                continue

            rrule_text = rrule_match.group(1)
            rule = rrulestr(rrule_text, dtstart=dtstart)
            for occurrence_start in rule:
                occurrence_end = occurrence_start + (dtend - dtstart)
                occurrence_start_utc = occurrence_start.astimezone(pytz.utc)
                if occurrence_start_utc > now:
                    if not next_event or occurrence_start_utc < next_event[0]:
                        next_event = (occurrence_start, occurrence_end, raw_event)
                    break

        if next_event:
            start_time, end_time, raw_event = next_event
            name_match = re.search(r"SUMMARY:(.*)", raw_event)
            location_match = re.search(r"LOCATION:(.*)", raw_event)
            description_match = re.search(r"DESCRIPTION:(.*)", raw_event)

            name = name_match.group(1) if name_match else "No Title"
            location = location_match.group(1) if location_match else "No Location"
            description = description_match.group(1) if description_match else "No Description"

            return {
                "name": name,
                "date": self.format_date(start_time, end_time),
                "location": location,
                "description": description,
            }
        else:
            return "No upcoming meetings."
