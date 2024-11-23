from tasks.advent_of_code_daily_message import start_scheduled_task as aoc_start_scheduled_task
from tasks.lc_daily_message import start_scheduled_task as lc_start_scheduled_task

class start_daily_tasks:
    def __init__(self, client, bot_context):
        lc_start_scheduled_task(client, bot_context.admin_channel)
        aoc_start_scheduled_task(client)