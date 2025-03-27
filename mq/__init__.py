import logging
from typing import Callable
from discord.ext import commands
from pika.exchange_type import ExchangeType
from mq.core.manager import RabbitMQManager

logger = logging.getLogger(__name__)

_manager = RabbitMQManager()


def consumer(
    exchange, queue, routing_key, exchange_type=ExchangeType.topic, needs_context=False
):
    """decorator for registering consumers"""
    return _manager.register_callback(
        exchange, queue, routing_key, exchange_type, needs_context
    )


def producer(
    exchange, exchange_type=ExchangeType.topic, routing_key=None, needs_context=False
):
    """decorator for registering producers"""
    return _manager.register_producer(
        exchange, exchange_type, routing_key, needs_context
    )


async def publish_raw(exchange, routing_key, message, properties=None):
    """convenience function for ad-hoc publishing"""
    producer_name = f"raw.{exchange}.{routing_key}"
    producer = _manager.get_or_create_producer(
        producer_name, exchange, ExchangeType.topic, routing_key
    )
    return await producer.publish(message, properties=properties)


def setup(bot, bot_context):
    """
    setup function for the module, called in bot entrypoint to hook
    into lifecycle management, inject deps, etc.
    """
    logger.info("Setting up RabbitMQ")

    # bot has a rabbit parasite. "what's mine is yours", it says.
    _manager.set_context(bot, bot_context)

    from mq import consumers, producers

    bot_setup_hook = getattr(bot, "setup_hook", None)

    async def wrapped_setup_hook():
        if bot_setup_hook:
            if callable(bot_setup_hook):
                await bot_setup_hook()

        await initialize_rabbitmq(bot)

    bot.setup_hook = wrapped_setup_hook
    bot_close = bot.close

    async def wrapped_close():
        await shutdown_rabbitmq()
        await bot_close()

    bot.close = wrapped_close

    return _manager


async def initialize_rabbitmq(bot):
    global _manager

    _manager.create_consumers()

    await _manager.start_consumers(bot.loop)
    await _manager.connect_producers(bot.loop)

    logger.info("RabbitMQ consumers and producers initialized")


async def shutdown_rabbitmq():
    global _manager

    if _manager:
        await _manager.stop_all()
