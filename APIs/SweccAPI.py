import requests, os, logging
import aiohttp

from random import random, choice

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)

aio_session_global = [None]


class SweccAPI:
    global aio_session_global

    def __init__(self):
        self.url = os.getenv("SWECC_URL")
        self.api_key = os.getenv("SWECC_API_KEY")
        self.headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json",
        }
        self.reaction_channel_subscriptions = {
            int(os.getenv("NEW_GRAD_CHANNEL_ID")),
            int(os.getenv("INTERNSHIP_CHANNEL_ID")),
        }
        self.COMPLETED_EMOJI = "✅"
        self.session = requests.Session()

    def set_session(self, session: aiohttp.ClientSession):
        aio_session_global[0] = session

    def get_session(self):
        if not aio_session_global[0]:
            logging.error("SweccAPI session not set")
            raise Exception("aiohttp session not set")
        return aio_session_global[0]

    def register(
        self, username, first_name, last_name, email, password, discord_username
    ):
        logging.info(f"Registering {username} with email {email}")

        try:

            data = {
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "discord_username": discord_username,
            }

            response = self.session.post(
                f"{self.url}/auth/register/ssflow/", headers=self.headers, json=data
            )

            return response.status_code, response.json()

        except Exception as e:
            logging.error(f"Registration error: {str(e)}")
            raise e

    def auth(self, discord_username, id, username):
        logging.info(
            f"Authenticating {discord_username} with id {id} and username {username}"
        )

        data = {
            "discord_id": id,
            "discord_username": discord_username,
            "username": username,
        }

        response = requests.put(
            f"{self.url}/members/verify-discord/", headers=self.headers, json=data
        )
        return response.status_code

    def leetcode_leaderboard(self, order_by="total"):
        logging.info("Fetching leetcode leaderboard order by %s", order_by)

        params = {"order_by": order_by}

        response = requests.get(
            f"{self.url}/leaderboard/leetcode/", headers=self.headers, params=params
        )

        if response.status_code == 200:
            return response.json()
        else:
            return None

    def github_leaderboard(self, order_by="commits"):
        logging.info("Fetching github leaderboard order by %s", order_by)

        params = {"order_by": order_by}

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

        response = requests.post(
            f"{self.url}/members/reset-password/", headers=self.headers, json=data
        )
        data = response.json()
        return f"https://interview.swecc.org/#/password-reset-confirm/{data['uid']}/{data['token']}/"

    async def process_reaction_event(self, payload, type):
        session = self.get_session()

        user_id, channel_id, emoji = (
            payload.user_id,
            payload.channel_id,
            payload.emoji,
        )

        if (
            channel_id in self.reaction_channel_subscriptions
            and self.COMPLETED_EMOJI == emoji.name
        ):

            data = {
                "discord_id": user_id,
                "channel_id": channel_id,
            }

            try:
                call = session.post if type == "REACTION_ADD" else session.delete
                async with call(
                    f"{self.url}/leaderboard/events/process/",
                    headers=self.headers,
                    json=data,
                ) as response:
                    if response.status != 202:
                        logging.error(
                            "Failed to send reaction event to backend, status code: %s",
                            response.status,
                        )
            except Exception as e:
                logging.error("Failed to send reaction event to backend: %s", e)

    async def process_message_event(self, message):
        discord_id = message.author.id
        channel_id = message.channel.id

        data = {
            "discord_id": discord_id,
            "channel_id": channel_id,
        }

        session = self.get_session()

        # todo: remove this log after successful testing in prod
        logging.info(
            f"Processing message event for {discord_id} in channel {channel_id}"
        )

        try:

            async with session.post(
                f"{self.url}/engagement/message/", headers=self.headers, json=data
            ) as response:
                if response.status != 202:
                    logging.error(
                        "Failed to send message event to backend, status code: %s",
                        response.status,
                    )
        except Exception as e:
            logging.error("Failed to send message event to backend: %s", e)

    async def attend_event(self, discord_id, session_key: str):
        logging.info(
            "Attempting to attend event with key %s for user with discord ID %d",
            session_key,
            discord_id,
        )

        data = {"discord_id": discord_id, "session_key": session_key}

        response = requests.post(
            f"{self.url}/engagement/attendance/attend", headers=self.headers, json=data
        )

        # Success
        if response.status_code == 201:
            return response.status_code, {}

        try:
            received_data = response.json()
            return response.status_code, received_data
        except requests.JSONDecodeError:
            return None, {"error": "Unable to parse response body."}

    async def sync_channels(self, channels):
        session = self.get_session()

        try:
            async with session.post(
                f"{self.url}/metasync/discord/anti-entropy/",
                headers=self.headers,
                json=channels,
            ) as response:
                if response.status != 200:
                    logging.error(
                        "Failed to sync channels, status code: %s, json: %s",
                        response.status,
                        await response.json(),
                    )
                else:
                    logging.info(
                        "Channels synced successfully, json: %s", await response.json()
                    )

                return response.status
        except Exception as e:
            logging.error("Failed to sync channels: %s", e)

    async def update_cohort_stats(self, discord_id, stat_url, cohort_name=None):
        session = self.get_session()

        data = {"discord_id": discord_id}
        if cohort_name is not None:
            data["cohort_name"] = cohort_name

        try:
            async with session.put(
                f"{self.url}/engagement/cohort/{stat_url}",
                headers=self.headers,
                json=data,
            ) as response:
                response_json = await response.json()
                if response.status != 200:
                    logging.error(
                        "Failed to update cohort stats, status code: %s, json: %s",
                        response.status,
                        response_json,
                    )
                    return None, {"message": response_json["error"]}
                else:
                    logging.info(
                        "Cohort stats updated successfully, json: %s",
                        response_json,
                    )

                return response_json["updated_cohorts"], None
        except Exception as e:
            logging.error("Failed to update cohort stats: %s", e)
            return {}, {"message": "Failed to update cohort stats"}

    async def get_cohort_stats(self, discord_id=None):
        session = self.get_session()

        try:
            async with session.get(
                f"{self.url}/cohorts/stats{f'?discord_id={discord_id}' if discord_id else ''}",
                headers=self.headers,
            ) as response:
                if response.status != 200:
                    logging.error(
                        "Failed to get cohort stats, status code: %s, json: %s",
                        response.status,
                        await response.json(),
                    )
                    return None
                return await response.json()

        except Exception as e:
            logging.error("Failed to get cohort stats: %s", e)
            return None

    async def get_school_email_verification_url(self, discord_id, email):
        logging.info(
            f"Getting school email verification url for {discord_id} with email {email}"
        )

        data = {
            "discord_id": discord_id,
            "school_email": email,
        }

        session = self.get_session()
        try:
            async with session.post(
                f"{self.url}/members/verify-school-email/",
                headers=self.headers,
                json=data,
            ) as response:
                if response.status != 200:
                    logging.error(
                        "Failed to get verification URL",
                        response.status,
                        await response.json(),
                    )
                    return None
                data = await response.json()
                logger.info("Received verification URL: %s", data)
                return True
        except Exception as e:
            logging.error("Failed to get verification URL: %s", e)
            return False

    async def get_cohort_metadata(self):
        session = self.get_session()

        try:
            async with session.get(
                f"{self.url}/cohorts/sync/discord/", headers=self.headers
            ) as response:
                if response.status != 200:
                    logging.error(
                        "Failed to get cohort metadata, status code: %s, json: %s",
                        response.status,
                        await response.json(),
                    )
                    return None

                data = await response.json()
                logger.info("Received cohort metadata: %s", data)
                return data
        except Exception as e:
            logging.error("Failed to get cohort metadata: %s", e)
            return None

    async def upload_cohort_metadata(self, data):
        session = self.get_session()
        logging.info("Uploading cohort metadata: %s", data)
        try:
            async with session.post(
                f"{self.url}/cohorts/sync/discord/",
                headers=self.headers,
                json=data,
            ) as response:
                if response.status != 200:
                    logging.error(
                        "Failed to upload cohort metadata, status code: %s, json: %s",
                        response.status,
                        await response.json(),
                    )
                    return None

                data = await response.json()
                logger.info("Received cohort metadata: %s", data)
                return data
        except Exception as e:
            logging.error("Failed to upload cohort metadata: %s", e)
            return None