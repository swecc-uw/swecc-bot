import requests


class SweccAPI:
    def __init__(self, url, api_key):
        self.url = url
        self.api_key = api_key
    
    def auth(self, username, id, code):
        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json",
        }

        # Define the data to be updated
        data = {
            "discord_id": id,
            "discord_username": username
        }

        response = requests.put(f"{self.url}/api/discord/{code}/", headers=headers, json=data)
        return response.status_code
