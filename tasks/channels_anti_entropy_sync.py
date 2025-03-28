import discord
import os
import datetime
from discord.ext import tasks
from APIs.SweccAPI import SweccAPI
import dotenv
import logging

from mq.events import ChannelSnapshot
import mq.producers

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
)

dotenv.load_dotenv()

swecc_api = SweccAPI()

ALLOWED_CHANNEL_TYPES = [
    discord.TextChannel,
    discord.VoiceChannel,
    discord.CategoryChannel,
    discord.StageChannel,
    discord.ForumChannel,
]

async def sync(guild):
    channels = [
        {
            "channel_id": channel.id,
            "channel_name": channel.name,
            "category_id": channel.category_id,
            "channel_type": channel.type[0].upper(),
            "guild_id": guild.id,
        }
        for channel in guild.channels
        if any(isinstance(channel, channel_type) for channel_type in ALLOWED_CHANNEL_TYPES)
    ]
    await swecc_api.sync_channels(
        channels=channels,
    )
    await mq.producers.publish_channel_snapshot(ChannelSnapshot(channels=channels))


SWECC_SERVER_ID = int(os.getenv("SWECC_SERVER"))


def start_scheduled_task(client):
    logging.info("Starting channels anti-entropy sync task")

    @tasks.loop(hours=1)
    async def scheduled_sync():
        if (guild := client.get_guild(SWECC_SERVER_ID)) is None:
            raise ValueError("SWECC server not found")

        await sync(guild)

    @scheduled_sync.before_loop
    async def before():
        await client.wait_until_ready()

    scheduled_sync.start()
