import requests, os, logging, pytz
import re
from dateutil.rrule import rrulestr
from datetime import datetime, timedelta
from dotenv import load_dotenv


logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s')

class AdventOfCodeAPI:
    def __init__(self):
        load_dotenv()
        self.leaderboard_id = os.getenv('AOC_LEADERBOARD_ID')
        self.year = datetime.now().year
        self.url = f"https://adventofcode.com/{self.year}/leaderboard/private/view/{self.leaderboard_id}.json"
        self.leaderboard_url = f"https://adventofcode.com/{self.year}/leaderboard/private/view/{self.leaderboard_id}"
        self.headers = {
                    "Content-Type": "application/json",
                    "Cookie": f"session={os.getenv('AOC_SESSION')}",
                    "User-Agent": "github.com/swecc-uw/swecc-bot by shawnc6@cs.washington.edu",
                }
        self.cache = {
            "last_accessed": None,
            "data": None,
        }
    

    def get_leaderboard_url(self):
        return self.leaderboard_url


    def parse_leaderboard(self, data):
        members = [
            {"name": member.get("name", "Anonymous"), "local_score": member["local_score"]}
            for member in data.get("members", {}).values()
        ]
        members.sort(key=lambda x: x["local_score"], reverse=True)
        return members


    async def get_leaderboard(self):
        now = datetime.now()
        if self.cache["data"] and self.cache["last_accessed"] and (now - self.cache["last_accessed"]) <= timedelta(minutes=16):
            logging.info("Returning cached leaderboard data")
            return self.cache["data"]
        else:
            logging.info("Fetching new leaderboard data from Advent of Code")
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()
            
            leaderboard_data = self.parse_leaderboard(response.json())
            self.cache["data"] = leaderboard_data
            self.cache["last_accessed"] = now
            
            return leaderboard_data
