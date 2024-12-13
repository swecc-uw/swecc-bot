import os

class BotContext:
    def __init__(self):
        self.ephemeral = True
        self.token = os.getenv('DISCORD_TOKEN')
        self.admin_channel = int(os.getenv('ADMIN_CHANNEL'))
        self.prefix = os.getenv('PREFIX_COMMAND')
        self.swecc_server = int(os.getenv('SWECC_SERVER'))
        self.transcripts_channel = int(os.getenv('TRANSCRIPTS_CHANNEL'))
        self.resume_channel = int(os.getenv('SWECC_RESUME_CHANNEL'))
        self.badwords = ['ticket', 'free.*macbook']
        self.do_not_timeout = set()
    
    async def log(self, ctx, message):
        channel = ctx.guild.get_channel(self.transcripts_channel)
        await channel.send(message)