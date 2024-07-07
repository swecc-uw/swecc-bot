import os, datetime, discord, logging
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv
from APIs.LeetcodeAPI import LeetcodeAPI

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
SWECC_URL = os.getenv('SWECC_URL')
SWECC_API_KEY = os.getenv('SWECC_API_KEY')
LC_CHANNEL_ID = int(os.getenv('LC_CHANNEL_ID'))
ADMIN_CHANNEL = int(os.getenv('ADMIN_CHANNEL'))
PREFIX_COMMAND = os.getenv('PREFIX_COMMAND')

lc = LeetcodeAPI()
intents = discord.Intents.all()
intents.message_content = True

client = commands.Bot(command_prefix=PREFIX_COMMAND, intents=intents)
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s')

@client.event
async def on_ready():
    logging.info(f'{client.user} has connected to Discord!')
    send_daily_message.start()
    logging.info("Bot is ready")


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    

@tasks.loop(time=datetime.time(hour=0, minute=1, tzinfo=datetime.timezone.utc))
async def send_daily_message():
    channel = client.get_channel(LC_CHANNEL_ID)
    admin_channel = client.get_channel(ADMIN_CHANNEL)
    if channel:
        daily_question = lc.get_leetcode_daily()
        if daily_question:
            print(daily_question)
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


@send_daily_message.before_loop
async def before():
    await client.wait_until_ready()


client.run(TOKEN)