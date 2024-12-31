import discord
import os
import datetime
from discord.ext import tasks
from APIs.SweccAPI import SweccAPI
import dotenv

import logging

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
)

dotenv.load_dotenv()

swecc_api = SweccAPI()


def get_channel_type(channel):
    if isinstance(channel, discord.TextChannel):
        return "TEXT"
    elif isinstance(channel, discord.VoiceChannel):
        return "VOICE"
    elif isinstance(channel, discord.CategoryChannel):
        return "CATEGORY"
    elif isinstance(channel, discord.StageChannel):
        return "STAGE"
    elif isinstance(channel, discord.ForumChannel):
        return "FORUM"
    else:
        return "UNKNOWN"


async def sync(guild):
    await swecc_api.sync_channels(
        [
            {
                "channel_id": channel.id,
                "channel_name": channel.name,
                "category_id": channel.category_id,
                "channel_type": get_channel_type(channel),
                "guild_id": guild.id,
            }
            for channel in guild.channels
        ]
    )


SWECC_SERVER_ID = int(os.getenv("SWECC_SERVER"))


def start_scheduled_task(client):
    logging.info("Starting channels anti-entropy sync task")

    @tasks.loop(hours=1)
    async def scheduled_sync():
        for guild in client.guilds:
            if guild.id == SWECC_SERVER_ID:
                await sync(guild)
                return
        raise ValueError("SWECC server not found")

    @scheduled_sync.before_loop
    async def before():
        await client.wait_until_ready()

    scheduled_sync.start()
