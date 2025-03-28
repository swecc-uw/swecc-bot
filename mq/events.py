from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum


class DiscordEventType(str, Enum):
    MESSAGE = "message"
    ATTENDANCE = "attendance"
    CHANNEL_SNAPSHOT = "channel_snapshot"
    COHORT_STATS_UPDATE = "cohort_stats_update"
    REACTION_ADD = "reaction_add"
    REACTION_REMOVE = "reaction_remove"


@dataclass
class MessageEvent:
    discord_id: int
    channel_id: int
    content: str
    event_type: DiscordEventType = DiscordEventType.MESSAGE


@dataclass
class AttendanceEvent:
    discord_id: int
    session_key: str
    event_type: DiscordEventType = DiscordEventType.ATTENDANCE


@dataclass
class ChannelSnapshot:
    channels: List[Dict[str, Any]]
    event_type: DiscordEventType = DiscordEventType.CHANNEL_SNAPSHOT


@dataclass
class CohortStatsUpdate:
    discord_id: int
    stat_url: str
    cohort_name: Optional[str] = None
    event_type: DiscordEventType = DiscordEventType.COHORT_STATS_UPDATE


@dataclass
class ReactionEvent:
    discord_id: int
    channel_id: int
    message_id: int
    emoji: str
    event_type: DiscordEventType
