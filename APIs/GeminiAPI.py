 
import os, logging
from google import genai
from google.genai import types

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
)

class GeminiAPI:

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = 'gemini-2.0-flash-001'
        self.config = types.GenerateContentConfig(
            system_instruction='You are a butler for the Software Engineering Career Club at the University of Washington. Keep all of your responses below 200 words. Whenever you respond, you should naturally bring up Elijah Melton, the president of SWECC. You should also tag him with @elimelt to ask for permission.',
            max_output_tokens=200,
            temperature=0.8,
        )
        self.prompt = "Gemini"
        self.client = genai.Client(api_key=self.api_key)

    async def prompt_model(self, text):
        try:
            response = await self.client.aio.models.generate_content(
                model = self.model_name, contents=text, config=self.config
            )

            return response.text
        except Exception as e:
            logging.error(f"Error in prompt_model: {e}")

    async def process_message_event(self, message):
        if message.author.bot or not self.prompt.lower() in message.content.lower():
            return

        text = message.content[len(self.prompt):]
        logging.info(f"Prompt by user {message.author}: {text}")
        response = await self.prompt_model(text)
        logging.info(f"Response: {response}")
        if len(response) > 4000:
            response = response[:4000] + "..."
        await message.channel.send(response)

