import os, datetime, discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')



intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    send_daily_message.start()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

@tasks.loop(time=datetime.time(hour=0, minute=0, tzinfo=datetime.timezone.utc))
async def send_daily_message():
    channel = client.get_channel(1009984603676749824) 
    if channel:
        message = await channel.send("New daily leetcode! Let's solve it!")
        await message.add_reaction('✅')
        await message.add_reaction('❌')
        thread = await message.create_thread(name="Solutions")
        await thread.send("Post your solutions here.")

@send_daily_message.before_loop
async def before():
    await client.wait_until_ready()


client.run(TOKEN)
