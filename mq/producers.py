import json
import mq
import logging
from mq.events import (
    MessageEvent,
    AttendanceEvent,
    ChannelSnapshot,
    CohortStatsUpdate,
    ReactionEvent,
)

logging.basicConfig(level=logging.INFO)


@mq.producer(routing_key="discord.message")
async def publish_message_event(event: MessageEvent):
    logging.info(
        f"publishing message event for {event.discord_id} in channel {event.channel_id} with content {event.content}"
    )

    return json.dumps(event.__dict__)

@mq.producer(routing_key="discord.attendance")
async def publish_attend_event(event: AttendanceEvent):
    logging.info(
        "Attempting to attend event with key %s for user with discord ID %d",
        event.session_key,
        event.discord_id,
    )

    return json.dumps(event.__dict__)

@mq.producer(routing_key="discord.channels")
async def publish_channel_snapshot(event: ChannelSnapshot):
    logging.info("Syncing channels with backend")

    return json.dumps(event.__dict__)

@mq.producer(routing_key="discord.cohort_stats")
async def publish_cohort_stats_update_event(event: CohortStatsUpdate):
    logging.info(
        f"Attempting to update cohort stats {event.stat_url} for user with discord ID {event.discord_id}"
    )

    return json.dumps(event.__dict__)

async def _process_reaction_event(event: ReactionEvent):
    logging.info(
        f"Processing reaction event for user {event.discord_id} in channel "
        f"{event.channel_id} with emoji {event.emoji} and message {event.message_id}"
    )

    return json.dumps(event.__dict__)

@mq.producer(routing_key="discord.reactions.add")
async def publish_reaction_add_event(event: ReactionEvent):
    return await _process_reaction_event(event)

@mq.producer(routing_key="discord.reactions.remove")
async def publish_reaction_remove_event(event: ReactionEvent):
    return await _process_reaction_event(event)