import requests, os, logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s')

class SweccAPI:
    def __init__(self):
        self.url = os.getenv('SWECC_URL')
        self.api_key = os.getenv('SWECC_API_KEY')
        self.headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json",
        }
    
    def auth(self, discord_username, id, username):
        logging.info(f"Authenticating {discord_username} with id {id} and username {username}")

        data = {
            "discord_id": id,
            "discord_username": discord_username,
            "username": username
        }

        response = requests.put(f"{self.url}/members/verify-discord/", headers=self.headers, json=data)
        return response.status_code

    def leetcode_leaderboard(self, order_by="total"):
        logging.info("Fetching leetcode leaderboard order by %s", order_by)

        params = {"order_by": order_by }

        response = requests.get(
            f"{self.url}/leaderboard/leetcode/", headers=self.headers, params=params
        )

        if response.status_code == 200:
            return response.json()
        else:
            return None
        
    async def reset_password(self, discord_username, id):
        logging.info(f"Resetting password for {discord_username} with id {id}")

        data = {
            "discord_id": id,
        }

        response = requests.post(f"{self.url}/members/reset-password/", headers=self.headers, json=data)
        return response.json().get("reset_url")
