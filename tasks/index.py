from tasks.advent_of_code_daily_message import start_scheduled_task as aoc_start_scheduled_task
from tasks.lc_daily_message import start_scheduled_task as lc_start_scheduled_task
from tasks.channels_anti_entropy_sync import start_scheduled_task as sync_channels_start_scheduled_task

class start_daily_tasks:
    def __init__(self, client, bot_context):
        self.client = client
        self.bot_context = bot_context

    def start_tasks(self):
        lc_start_scheduled_task(self.client, self.bot_context.admin_channel)
        sync_channels_start_scheduled_task(self.client)
        aoc_start_scheduled_task(self.client)
