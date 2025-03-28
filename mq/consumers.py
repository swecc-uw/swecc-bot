import logging
from settings.context import BotContext
import mq
from pika import BasicProperties

@mq.consumer(
    exchange="swecc-bot-exchange",
    queue="loopback",
    routing_key="#",
)
async def loopback(body, properties: BasicProperties):
    logging.info(f"Loopback consumer received message: {body}")
