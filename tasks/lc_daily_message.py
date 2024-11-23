import discord, os, datetime
from discord.ext import tasks
from APIs.LeetcodeAPI import LeetcodeAPI
from dotenv import load_dotenv

lc = LeetcodeAPI()
load_dotenv()
LC_CHANNEL_ID = int(os.getenv('LC_CHANNEL_ID'))

async def send_daily_message(client, ADMIN_CHANNEL):
    channel = client.get_channel(LC_CHANNEL_ID)
    admin_channel = client.get_channel(ADMIN_CHANNEL)
    if channel:
        daily_question = lc.get_leetcode_daily()
        if daily_question:
            colors = {
                "Easy": 0x00ff00,
                "Medium": 0xffa500,
                "Hard": 0xff0000
            }
            question_link = daily_question['link']
            question_title = daily_question['question']['title']
            difficulty = daily_question['question']['difficulty']

            embed = discord.Embed(
                title=question_title,
                url=question_link,
                description=f"**Difficulty:** {difficulty}",
                color=colors[difficulty]
            )
            embed.set_author(name="LeetCode Daily Challenge")
            embed.set_thumbnail(url="https://leetcode.com/static/images/LeetCode_logo.png")
            embed.set_footer(text="Good luck!")

            message = await channel.send(embed=embed)
            await message.add_reaction('✅')
            await message.add_reaction('❌')
            thread = await message.create_thread(name="Solutions")
            await thread.send("Post your solutions/discussion here!")
        else:
            await admin_channel.send("Failed to fetch the daily LeetCode question.")

def start_scheduled_task(client, ADMIN_CHANNEL):
    @tasks.loop(time=datetime.time(hour=0, minute=1, tzinfo=datetime.timezone.utc))
    async def scheduled_daily_message():
        await send_daily_message(client, ADMIN_CHANNEL)

    @scheduled_daily_message.before_loop
    async def before():
        await client.wait_until_ready()

    scheduled_daily_message.start()
