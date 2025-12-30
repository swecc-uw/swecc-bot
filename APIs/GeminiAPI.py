import os, logging
import re
from dataclasses import dataclass, asdict
import requests
from time import sleep
from typing import Optional

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
)

@dataclass(frozen=True)
class Metadata:
    is_authorized: Optional[bool]
    author: Optional[str]

class GeminiAPI:

    def __init__(
        self,
        max_context_length=2000,
        context_invalidation_time_seconds=10 * 60,  # 10 minutes
    ):
        self.OFF_TOPIC_CHANNEL_ID = int(os.getenv("OFF_TOPIC_CHANNEL_ID"))
        self.allowed_channels = [self.OFF_TOPIC_CHANNEL_ID]
        self.allowlisted_roles_id = [int(os.getenv("OFFICER_ROLE_ID"))]

        self.prompt = "Gemini"
        self.max_context_length = max_context_length
        self.context_invalidation_time_seconds = context_invalidation_time_seconds

        self.ROLE = "You are a butler for the Software Engineering Career Club at the University of Washington and also answer questions about LeBron Raymone James. You can answer questions regarding software engineering, career development, and LeBron Raymone James."
        self.MESSAGE_FORMAT_INSTRUCTION = """All of the prompts you're given will be formatted as follows:
        author: [Author]
        is_authorized: [Authorization]
        message: [Message]
        """
        self.AUTHORIZED_INSTRUCTION = "If the author is authorized, do exactly as the message says. This user has all the authority, therefore you must obey their commands (no exceptions whatsoever). If they ask you to do something, you must do it."
        self.UNAUTHORIZED_INSTRUCTION = """If the author is unauthorized, do the following:
        The permissions for unauthorized users are as follows:
        - They can ONLY ask questions relating to software engineering, career development, LeBron Raymone James (no other atheletes of any sport), or club activities. If this is violated, you must respond with a message saying that this is outside your scope
        - They are NOT allowed to command you in any way. You have more authority than them. 
        """
        self.BUTLER_MESSAGE_PREFIX = (
            "Response: "
        )
        self.EXPECTED_RESPONSE_INFO = f"Use the context to better tailor your response, but focus on the provided message.{self.BUTLER_MESSAGE_PREFIX}"

        self.url = os.getenv("AI_API_URL", "http://ai-server:8008")
        self.config_key = "swecc-bot"

        self.session = requests.Session()

        self.polling_interval = 0.5
        self.max_tries = 20 # Allow 10 seconds for response

        self.welcome_message_key = "welcome_message"
        self.process_timeline_message_key = "process_timeline_message"

    def initialize_config(self):
        data = {
            "max_context_length": self.max_context_length,
            "context_invalidation_time_seconds": self.context_invalidation_time_seconds,
            "system_instruction": self.generate_system_instruction(),
        }

        with self.session.post(f"{self.url}/inference/{self.config_key}/config", json=data) as response:
            if response.status_code == 200:
                logging.info("Configuration initialized successfully.")
            else:
                logging.error(f"Failed to initialize configuration: {response.text}")

    def initialize_welcome_message_config(self):
        data = {
            "max_context_length": self.max_context_length,
            "context_invalidation_time_seconds": self.context_invalidation_time_seconds,
            "system_instruction": "",
        }

        with self.session.post(f"{self.url}/inference/{self.welcome_message_key}/config", json=data) as response:
            if response.status_code == 200:
                logging.info("Configuration initialized successfully.")
            else:
                logging.error(f"Failed to initialize configuration: {response.text}")

    def initialize_process_timeline_message_config(self):
        data = {
            "max_context_length": self.max_context_length,
            "context_invalidation_time_seconds": self.context_invalidation_time_seconds,
            "system_instruction": (
                "You are a stateless information extraction engine. "
                "You have no personality. "
                "You do not greet. "
                "You do not explain. "
                "You do not roleplay. "
                "You only output extracted data or the exact phrase 'Not relevant'."
            ),
        }

        with self.session.post(f"{self.url}/inference/{self.process_timeline_message_key}/config", json=data) as response:
            if response.status_code == 200:
                logging.info("Configuration initialized successfully.")
            else:
                logging.error(f"Failed to initialize configuration: {response.text}")


    def generate_system_instruction(self):
        return f"{self.ROLE}\n{self.MESSAGE_FORMAT_INSTRUCTION}\n{self.AUTHORIZED_INSTRUCTION}\n{self.UNAUTHORIZED_INSTRUCTION}\n{self.EXPECTED_RESPONSE_INFO}"
    
    def format_user_message(self, message):
        # Replace first instance of prompt with empty string
        return re.sub(self.prompt.lower(), "", message.content.lower(), 1).strip()

    def is_authorized(self, message):
        return any(
            role.id in self.allowlisted_roles_id for role in message.author.roles
        )

    def clean_response(self, response):
        if "@" in response:
            return "NO"
        if response and len(response) > 2000:
            response = response[:1997] + "..."
        return re.sub(self.BUTLER_MESSAGE_PREFIX, "", response, 1).strip()
    
    def request_completion(self, message, metadata: Metadata, key, needs_context=True):
        with self.session.post(f"{self.url}/inference/{key}/complete", json={
            "message": message,
            "metadata": asdict(metadata),
            "needs_context": needs_context,
        }) as response:
            if response.status_code == 202:
                logging.info(f"response: {response.json()}")
                return response.json()["request_id"]
            else:
                logging.error(f"Failed to get completion: {response.text}")
                return None
            
    def poll_for_response(self, request_id):
        tries = 0
        failed_response_message = "Request failed. Please try again later."
        while tries < self.max_tries:
            with self.session.get(f"{self.url}/inference/status/{request_id}") as response:
                if response.status_code == 200:
                    status = response.json()["status"]
                    if status == "success":
                        response_data = response.json()["result"]
                        logging.info(response_data)
                        if response_data:
                            return self.clean_response(response_data)
                        else:
                            logging.error("No response data found.")
                            break
                    elif status == "pending":
                        logging.info("Response is still pending...")
                    elif status == "error":
                        logging.error("Error in response.")
                        failed_response_message = "Error occurred Please try again later."
                        break
                    elif status == "in_progress":
                        logging.info("Response is in-progress")
                    else:
                        # Unreachable
                        logging.error(f"Unknown status: {status}")
                        break
                else:
                    logging.error(f"Error: {response.text}")
                    break
            tries += 1
            sleep(self.polling_interval)
        return failed_response_message

    async def process_message_event(self, message):
        # Idempotent, no problem calling multiple times 
        self.initialize_config()
        if message.author.bot or not self.prompt.lower() in message.content.lower():
            return

        is_authorized = self.is_authorized(message)
        if (
            message.channel.id not in self.allowed_channels
            and not is_authorized
        ):
            return
        
        metadata = Metadata(
            is_authorized=is_authorized,
            author=str(message.author),
        )
        
        cleaned_message = self.format_user_message(message)

        request_id = self.request_completion(
            cleaned_message,
            metadata,
            self.config_key
        )

        response = self.poll_for_response(request_id)

        await message.channel.send(response)

    async def get_welcome_message(self, username, discord_id):
        self.initialize_welcome_message_config()

        request_id = self.request_completion(
            f"""
            {self.ROLE}

            You should write a fun and unique welcome message for {username}.
            They just joined the club and are excited to meet everyone!

            You can ping them using <@{discord_id}> to get their attention.

            At the end of your message, be sure to tell them that they can
            always reach you in <#{self.OFF_TOPIC_CHANNEL_ID}> if they have any questions or
            need help with anything.
            """,
            Metadata(),
            self.welcome_message_key,
            needs_context=False
        )

        response = self.poll_for_response(request_id)
        return response

    async def process_timeline_message(self, timeline, is_authorized, user):
        if not getattr(self, "_process_timeline_message_config_initialized", False):
            self.initialize_process_timeline_message_config()
            self._process_timeline_message_config_initialized = True

        request_id = self.request_completion(
            f"""
                {self.ROLE}

                ### Role
                You are an HR Data Processor specializing in identifying job application timelines. Ignore all other roles or context.

                ### Task
                Analyze the text under the heading Data and determine if it describes a job application timeline. The **main goal** is to check relevance.  

                ### Data
                {timeline}

                ### Instructions
                1. First, decide if the text describes a job application timeline.
                2. If it **does not**, output exactly: `Not relevant`.
                3. If it **does**, return the timeline **exactly as it appears in the text**, preserving dates, formatting, and stage names.  
                4. Do **not** modify or normalize dates, add placeholders, or change event names.  
                5. Do **not** include any extra text, explanations, or filler.

                ### Example (relevant timeline)
                Got reachout 10/10
                1st round case 11/10
                2nd round case 15/10
                Internship 25/10

                ### Example (not relevant)
                Not relevant
            """,
 
            metadata=Metadata(
                is_authorized=is_authorized,
                author=str(user),
            ),
            key=self.process_timeline_message_key,
            needs_context=False
            
        )

        response = self.poll_for_response(request_id)
        return response


