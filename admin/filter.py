from datetime import datetime, timedelta, timezone
import discord, re

class TimeoutActionView(discord.ui.View):
    def __init__(self, member, bot_context):
        super().__init__(timeout=None)
        self.member = member
        self.bot_context = bot_context

    @discord.ui.button(label="Ban", style=discord.ButtonStyle.danger)
    async def ban_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.member.ban(reason="Banned for suspected spamming.")
        await interaction.response.edit_message(content=f"{self.member.mention} has been banned.", view=None)

    @discord.ui.button(label="Remove timeout", style=discord.ButtonStyle.success)
    async def ignore_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.bot_context.do_not_timeout.add(self.member.id)
        await self.member.edit(timed_out_until=None)
        await interaction.response.edit_message(content=f"{self.member.mention} will not be timed out again.", view=None)

async def filter_message(message, bot_context):
        member = message.author
        if isinstance(member, discord.Member) and member.joined_at:
            one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            if member.joined_at > one_week_ago and member.id not in bot_context.do_not_timeout:
                for word in bot_context.badwords:
                    pattern = re.compile(word, re.IGNORECASE)
                    if pattern.search(message.content):
                        log_message = f"Deleted message from {member.mention} for containing the word '{word}'. Full message: {message.content}"
                        await message.delete()
                        await member.timeout(timedelta(hours=12), reason=f"Suspected spammer")                        
                        
                        view = TimeoutActionView(member, bot_context)
                        channel = message.guild.get_channel(bot_context.transcripts_channel)
                        await channel.send(log_message)
                        await channel.send("How should we handle it?", view=view)
                        break