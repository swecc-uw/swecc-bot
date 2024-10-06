import requests, os, logging, pytz
from ics import Calendar
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s')

class CalendarAPI:
    def __init__(self):
        self.url = os.getenv('CALENDAR_URL')

    def get_suffix(self, day):
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][day % 10 - 1]
        return str(day) + suffix
    
    def format_date(self, start_datetime, end_datetime):
        local_start = start_datetime.astimezone(pytz.timezone('America/Los_Angeles'))
        local_end = end_datetime.astimezone(pytz.timezone('America/Los_Angeles'))

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

        calendar = Calendar(response.text)
        now = datetime.now(pytz.utc)  

        next_event = None

        for event in calendar.events:
            event_start = event.begin.datetime 
            if event_start > now:
                if not next_event or event_start < next_event.begin.datetime:
                    next_event = event

        if next_event:
            return self.create_return_format(next_event)
        else:
            return "No upcoming meetings."