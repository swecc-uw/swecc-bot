import logging
from settings.context import BotContext
import mq
from pika import BasicProperties
from discord.ext import commands


@mq.consumer(
    exchange="swecc-bot-exchange",
    queue="loopback",
    routing_key="#",
)
async def loopback(body, properties: BasicProperties):
    logging.info(f"Loopback consumer received message: {body}")


@mq.consumer(
    exchange="swecc-server-exchange",
    queue="discord.verified-email",
    routing_key="server.verified-email",
    needs_context=True,
)
async def add_verified_role(
    body, properties, client: commands.Bot, context: BotContext
):
    message = body.decode("utf-8")
    discord_id = int(message)

    guild = client.get_guild(context.swecc_server)
    member = guild.get_member(discord_id)
    role = guild.get_role(context.verified_email_role_id)
    await member.add_roles(role)
