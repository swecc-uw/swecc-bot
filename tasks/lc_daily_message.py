import discord, os, datetime
from discord.ext import tasks
from APIs.LeetcodeAPI import LeetcodeAPI

lc = LeetcodeAPI()
LC_CHANNEL_ID = int(os.getenv('LC_CHANNEL_ID'))

async def send_daily_message(client, ADMIN_CHANNEL):
    channel = client.get_channel(LC_CHANNEL_ID)
    admin_channel = client.get_channel(ADMIN_CHANNEL)
    if channel:
        daily_question = lc.get_leetcode_daily()
        if daily_question:
            question_link = daily_question['link']
            question_title = daily_question['question']['title']
            difficulty = daily_question['question']['difficulty']
            tags = ", ".join(daily_question['question']['topicTags'])

            embed = discord.Embed(
                title=question_title,
                url=question_link,
                description=f"**Difficulty:** {difficulty}\n**Tags:** {tags}",
                color=0x00ff00
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
