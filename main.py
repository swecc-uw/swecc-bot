import discord, logging
from discord.ext import commands
from dotenv import load_dotenv
from APIs.SweccAPI import SweccAPI
from tasks.lc_daily_message import start_scheduled_task
import slash_commands.misc as misc
import slash_commands.auth as auth
import slash_commands.admin as admin
from settings.context import BotContext
import asyncio

load_dotenv()

swecc = SweccAPI()
bot_context = BotContext()
intents = discord.Intents.all()
intents.message_content = True

client = commands.Bot(command_prefix=bot_context.prefix, intents=intents)
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s')

@client.event
async def on_ready():
    logging.info(f'{client.user} has connected to Discord!')
    try:
        synced = await client.tree.sync()
        logging.info(f"Synced {synced} commands")
    except Exception as e:
        logging.info(f"Failed to sync commands: {e}")
    start_scheduled_task(client, bot_context.admin_channel)
    logging.info("Bot is ready")

@client.event
async def on_member_remove(member: discord.Member):
    if member.guild.id == bot_context.swecc_server:
        channel = member.guild.get_channel(bot_context.transcripts_channel)

        if channel is not None:
            try:
                await channel.send(f"{member.mention} has left the server.")
            except:
                await channel.send(f"{member.display_name} has left the server.")


@client.event
async def on_message(message):
    if message.author == client.user:
        return


@client.event
async def on_thread_create(thread):
    if thread.guild.id == bot_context.swecc_server:

        if thread.parent_id == bot_context.resume_channel:
            await asyncio.sleep(5) 
            message = await thread.fetch_message(thread.id)
            if not message.attachments or not message.attachments[0].content_type.startswith("image"):
                try:
                    channelName = thread.parent.mention
                except:
                    channelName = thread.parent.name
                await message.thread.delete()
                await message.author.send(f"Hello {message.author.mention}, your resume post in {channelName} was deleted because it didn't contain a screenshot of your resume. Please try again.")
                mod_channel = thread.guild.get_channel(bot_context.transcripts_channel)
                await mod_channel.send(f"{message.author.mention}'s resume post in {channelName} was deleted because it didn't contain an image of their resume. File type: {message.attachments[0].content_type if message.attachments else 'none'}")


misc.setup(client, bot_context)
auth.setup(client, swecc)
admin.setup(client, bot_context)

client.run(bot_context.token)