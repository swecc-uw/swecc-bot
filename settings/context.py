import os, asyncpraw

class BotContext:
    def __init__(self):
        self.ephemeral = False
        self.token = os.getenv('DISCORD_TOKEN')
        self.admin_channel = int(os.getenv('ADMIN_CHANNEL'))
        self.prefix = os.getenv('PREFIX_COMMAND')