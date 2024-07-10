import requests, os

class SweccAPI:
    def __init__(self):
        self.url = os.getenv('SWECC_URL')
        self.api_key = os.getenv('SWECC_API_KEY')
    
    def auth(self, username, id, code):
        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "discord_id": id,
            "discord_username": username
        }

        response = requests.put(f"{self.url}/api/discord/{code}/", headers=headers, json=data)
        return response.status_code
