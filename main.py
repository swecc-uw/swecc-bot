import discord, logging
from discord.ext import commands
from dotenv import load_dotenv
from APIs.SweccAPI import SweccAPI
from tasks.lc_daily_message import start_scheduled_task
import slash_commands.misc as misc
import slash_commands.auth as auth
import slash_commands.admin as admin
from settings.context import BotContext

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
async def on_message(message):
    if message.author == client.user:
        return
    
misc.setup(client, bot_context)
auth.setup(client, swecc)
admin.setup(client, bot_context)

client.run(bot_context.token)