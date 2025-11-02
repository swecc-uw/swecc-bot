import os


class BotContext:
    def __init__(self):
        self.ephemeral = True
        self.token = os.getenv("DISCORD_TOKEN")
        self.swecc_server = int(os.getenv("SWECC_SERVER"))

        self.admin_channel = int(os.getenv("ADMIN_CHANNEL"))
        self.transcripts_channel = int(os.getenv("TRANSCRIPTS_CHANNEL"))
        self.resume_channel = int(os.getenv("SWECC_RESUME_CHANNEL"))
        self.reading_group_channel = int(os.getenv("READING_GROUP_CHANNEL"))

        self.cohort_category_id = int(os.getenv("COHORT_CATEGORY_ID"))

        self.verified_role_id = int(os.getenv("VERIFIED_ROLE_ID"))
        self.officer_role_id = int(os.getenv("OFFICER_ROLE_ID"))
        self.verified_email_role_id = int(os.getenv("VERIFIED_EMAIL_ROLE_ID"))

        self.prefix = os.getenv("PREFIX_COMMAND")
        self.badwords = ["ticket", "free.*macbook", "macbook.*free", "\$", "seat.*section", "help.*offer", "lumen field", "personal assistant", "run(ning)?.*errands", "free.*gift.*card", "free.*visa", "free.*paypal", "work.*from.*home", "earn.*money.*fast", "crypto.*investment", "make.*money.*online", "air*free", "@everyone"]
        self.do_not_timeout = set()

    async def log(self, ctx, message):
        channel = ctx.guild.get_channel(self.transcripts_channel)
        await channel.send(message)
