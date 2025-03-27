import aiohttp
import discord, logging
from discord.ext import commands
from dotenv import load_dotenv
from APIs.GeminiAPI import GeminiAPI
from APIs.SweccAPI import SweccAPI
import slash_commands.misc as misc
import slash_commands.auth as auth
import slash_commands.admin as admin
import slash_commands.reading as reading
from settings.context import BotContext
import asyncio
from tasks.index import start_daily_tasks
import admin.filter as filter

load_dotenv()

swecc = SweccAPI()
gemini = GeminiAPI()
bot_context = BotContext()
intents = discord.Intents.all()
intents.message_content = True
do_not_timeout = set()

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

    logging.info("Bot is ready")

@client.event
async def on_member_remove(member: discord.Member):
    if member.guild.id == bot_context.swecc_server:
            await bot_context.log(member, f"{member.display_name} ({member.id}) has left the server.")

@client.event
async def on_message(message):
    member = message.author
    if member == client.user:
        return
    
    await filter.filter_message(message, bot_context)
    await swecc.process_message_event(message)
    await gemini.process_message_event(message)
        
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
                if not message.attachments:
                    await message.author.send(f"Hello {message.author.mention}, your resume post in {channelName} was deleted because it didn't contain a screenshot of your resume. Please try again.")
                else:
                    await message.author.send(f"Hello {message.author.mention}, your resume post in {channelName} was deleted because it didn't contain a screenshot of your resume. Please try again with a screenshot instead of {message.attachments[0].content_type}.")

                await bot_context.log(message, f"{message.author.mention}'s resume post in {channelName} was deleted. File type: {message.attachments[0].content_type if message.attachments else 'none'}")


@client.event
async def on_raw_reaction_add(payload):
    await swecc.process_reaction_event(payload, "REACTION_ADD")


@client.event
async def on_raw_reaction_remove(payload):
    await swecc.process_reaction_event(payload, "REACTION_REMOVE")

misc.setup(client, bot_context)
auth.setup(client, bot_context)
admin.setup(client, bot_context)
reading.setup(client, bot_context)

async def main():
    async with aiohttp.ClientSession() as session, client:
        client.session = session
        swecc.set_session(session)

        try:
            start_daily_tasks(client, bot_context).start_tasks()
            logging.info("Started daily tasks successfully!!!")
        except Exception as e:
            logging.info(f"Failed to start daily tasks: {e}")

        await client.start(bot_context.token)

asyncio.run(main())