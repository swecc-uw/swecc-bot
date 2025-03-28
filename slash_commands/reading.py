import discord
from discord import app_commands
import datetime
from dataclasses import dataclass, field
from typing import List, Tuple
from pytz import timezone

@dataclass
class Chapter:
    number: int
    subtitle: str
    length: int

    def __str__(self) -> str:
        return f"**Chapter {self.number}.** *{self.subtitle}*"

    def with_pages(self) -> str:
        return f"{self} ({self.length} pages)"

@dataclass
class ReadingGroupConfig:
    message_title: str = "📚 Weekly Reading Assignment 📚"
    message_footer: str = "React with ✅ if you're in, ❌ if you're out"
    message_color: int = 0x1f8b4c

    timezone: timezone = timezone("US/Pacific")

    book_cover_url: str = "https://dataintensive.net/images/book-cover.png"
    book_url: str = "https://discord.com/channels/960050427657863218/1352172643469627443/1352178235999387699"

    chapters: List[Chapter] = field(default_factory=lambda: [
        Chapter(1,  "Reliable, Scalable, and Maintainable Applications", 24),
        Chapter(2,  "Data Models and Query Languages", 42),
        Chapter(3,  "Storage and Retrieval", 42),
        Chapter(4,  "Encoding and Evolution", 40),
        Chapter(5,  "Replication", 48),
        Chapter(6,  "Partitioning", 22),
        Chapter(7,  "Transactions", 52),
        Chapter(8,  "The Trouble with Distributed Systems", 48),
        Chapter(9,  "Consistency and Consensus", 68),
        Chapter(10, "Batch Processing", 50),
        Chapter(11, "Stream Processing", 50),
        Chapter(12, "The Future of Data Systems", 64)
    ])

    chapter_schedule: List[Tuple[int, ...]] = field(default_factory=lambda: [
        (0, 1),  # week 1: ch. 1, 2
        (2,),    # week 2: ch. 3
        (3,),    # week 3: ch. 4
        (4, 5),  # week 4: ch. 5, 6
        (6,),    # week 5: ch. 7
        (7,),    # week 6: ch. 8
        (8,),    # week 7: ch. 9
        (9,),    # week 8: ch. 10
        (10,),   # week 9: ch. 11
        (11,)    # week 10: ch. 12
    ])

config = ReadingGroupConfig()
bot_context = None

def format_reading_pages(chapter_indices: List[int]) -> Tuple[List[str], int]:
    assigned_chapters = [config.chapters[idx] for idx in chapter_indices]
    total_pages = sum(chapter.length for chapter in assigned_chapters)
    return [chapter.with_pages() for chapter in assigned_chapters], total_pages

@app_commands.command(name="reading", description="Create a reading group thread for a specific week and date")
@app_commands.describe(
    week="The week number (1-10)",
    date="The meeting date (format: YYYY-MM-DD)",
    time="Meeting time (format: HH:MM)",
    location="Meeting location"
)
async def create_reading_group_thread(interaction: discord.Interaction, week: int, date: str, time: str, location: str):
    await interaction.response.defer(ephemeral=True)

    officer_role = interaction.guild.get_role(bot_context.officer_role_id)
    if officer_role not in interaction.user.roles:
        await interaction.followup.send("You do not have permission to create reading group threads.", ephemeral=True)
        return

    if week < 1 or week > len(config.chapter_schedule):
        await interaction.followup.send(f"Invalid week. Please choose a week between 1 and {len(config.chapter_schedule)}.", ephemeral=True)
        return

    try:
        meeting_date = datetime.datetime.strptime(date, "%Y-%m-%d")
        parsed_time = datetime.datetime.strptime(time, "%H:%M").time()
        meeting_datetime = config.timezone.localize(
            datetime.datetime.combine(meeting_date.date(), parsed_time)
        )

        formatted_date = meeting_datetime.strftime('%A, %B %d, %Y')
        formatted_time = meeting_datetime.strftime('%I:%M %p')
    except ValueError as e:
        error_msg = "Invalid date format. Use YYYY-MM-DD." if "date" in str(e) else "Invalid time format. Use HH:MM."
        await interaction.followup.send(error_msg, ephemeral=True)
        return

    week_index = week - 1
    chapter_details, _ = format_reading_pages(config.chapter_schedule[week_index])

    description = f"{formatted_date} {formatted_time} {config.timezone.zone} at {location}\n\n{chr(10).join(chapter_details)}"

    try:
        channel = interaction.guild.get_channel(bot_context.reading_group_channel)
        if not channel:
            await interaction.followup.send("Reading group channel not found.", ephemeral=True)
            return

        embed = discord.Embed(
            title=config.message_title,
            url=config.book_url,
            description=description,
            color=config.message_color
        )
        embed.set_footer(text=config.message_footer)
        embed.set_thumbnail(url=config.book_cover_url)

        message = await channel.send(embed=embed)
        await message.add_reaction('✅')
        await message.add_reaction('❌')

        thread = await message.create_thread(name=f"Week {week} Discussion")
        await thread.send("Feel free to share your thoughts, questions, and insights on this week's reading.")

        await interaction.followup.send(f"Successfully posted reading assignment for Week {week}.", ephemeral=True)

        admin_channel = interaction.guild.get_channel(bot_context.admin_channel)
        if admin_channel:
            await admin_channel.send(f"User {interaction.user.mention} created reading assignment for Week {week}.")

    except Exception as e:
        error_msg = f"Failed to send reading group assignment: {e}"
        await interaction.followup.send(error_msg, ephemeral=True)

        admin_channel = interaction.guild.get_channel(bot_context.admin_channel)
        if admin_channel:
            await admin_channel.send(f"Failed to create reading group thread: {e}")

def setup(client, context):
    global bot_context
    bot_context = context
    client.tree.add_command(create_reading_group_thread)