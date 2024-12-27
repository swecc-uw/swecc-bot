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
        self.reaction_channel_subscriptions = {
            os.getenv('NG_CHANNEL_ID'),
            os.getenv('INTERNSHIPS_CHANNEL_ID')
        }
        self.COMPLETED_EMOJI = ":white_check_mark:"

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

    def github_leaderboard(self, order_by="commits"):
        logging.info("Fetching github leaderboard order by %s", order_by)

        params = {"order_by": order_by }

        response = requests.get(
            f"{self.url}/leaderboard/github/", headers=self.headers, params=params
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
        data = response.json()
        return f"https://interview.swecc.org/#/password-reset-confirm/{data['uid']}/{data['token']}/"

    async def process_reaction_event(self, payload, type):
        user_id, channel_id, emoji = (
            payload.user_id,
            payload.channel_id,
            payload.emoji,
        )


        logging.info(emoji.name, emoji.id, emoji)
        if channel_id in self.reaction_channel_subscriptions and self.COMPLETED_EMOJI == emoji.name:

            data = {
                "discord_id": user_id,
                "channel_id": channel_id,
            }

            try:
                call = requests.post if type == "REACTION_ADD" else requests.delete

                response = call(
                    f"{self.url}/leaderboard/events/process/",
                    headers=self.headers,
                    json=data,
                )
            except Exception as e:
                logging.error("Failed to send reaction event to backend: %s", e)
        else:
            logging.info("Ignoring reaction event in channel %s", channel_id)
