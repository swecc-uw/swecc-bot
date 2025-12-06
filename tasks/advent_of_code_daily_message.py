import discord
import os
import datetime
from discord.ext import tasks
from dotenv import load_dotenv
from pytz import timezone
from APIs.AdventOfCodeAPI import AdventOfCodeAPI

load_dotenv()

AOC_CHANNEL_ID = int(os.getenv('LC_CHANNEL_ID'))
ADMIN_CHANNEL_ID = int(os.getenv('ADMIN_CHANNEL'))
LEADERBOARD_KEY = os.getenv('AOC_LEADERBOARD_KEY')
LEADERBOARD_ID = os.getenv('AOC_LEADERBOARD_ID')

aoc_api = AdventOfCodeAPI()


async def send_daily_aoc_message(client):
    channel = client.get_channel(AOC_CHANNEL_ID)
    admin_channel = client.get_channel(ADMIN_CHANNEL_ID)
    est = timezone("US/Eastern")
    today = datetime.datetime.now(est)

    if today.month == 12 and today.day <= 12:
        try:
            year = today.year
            day = today.day
            puzzle_url = f"https://adventofcode.com/{year}/day/{day}"

            leaderboard_data = await aoc_api.get_leaderboard()

            embed = discord.Embed(
                title=f"🎄 Day {day} of Advent of Code {year} is here! 🎄",
                url=puzzle_url,
                description=f"",
                color=0x1f8b4c 
            )        

            if leaderboard_data:
                leaderboard_text = "\n".join(
                    f"**#{index + 1}: {member['name']}** - {member['local_score']} points"
                    for index, member in enumerate(leaderboard_data[:10])
                )
                embed.add_field(
                    name="🎖️ Leaderboard (Top 10)",
                    value=(f"{leaderboard_text}\n\n"
                        f"[View full leaderboard]({aoc_api.get_leaderboard_url()})\n\n"
                    ),
                    inline=False
                )

            embed.set_footer(text=f"Leaderboard join key: {LEADERBOARD_KEY} ")
            embed.set_thumbnail(url="https://adventofcode.com/favicon.png")

            message = await channel.send(embed=embed)
            await message.add_reaction('✅')
            await message.add_reaction('❌')
            thread = await message.create_thread(name="Solutions")
            await thread.send("Post your solutions/discussion here!")
        except Exception as e:
            if admin_channel:
                await admin_channel.send(f"Failed to send Advent of Code message: {e}")


def start_scheduled_task(client):
    est = timezone("US/Eastern")

    @tasks.loop(time=datetime.time(hour=0, minute=0, tzinfo=est))
    async def scheduled_daily_message():
        await send_daily_aoc_message(client)

    @scheduled_daily_message.before_loop
    async def before():
        await client.wait_until_ready()

    scheduled_daily_message.start()
