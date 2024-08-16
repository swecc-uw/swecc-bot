import requests, os

class SweccAPI:
    def __init__(self):
        self.url = os.getenv('SWECC_URL')
        self.api_key = os.getenv('SWECC_API_KEY')
    
    def auth(self, discord_username, id, username):
        print(f"Authenticating {discord_username} with id {id} and username {username}")
        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "discord_id": id,
            "discord_username": discord_username,
            "username": username
        }

        response = requests.put(f"{self.url}/members/verify-discord/", headers=headers, json=data)
        return response.status_code
