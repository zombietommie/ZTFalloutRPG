import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging

from src.hello import hello
from src.dice import dice_commands
from src.caps import view_caps_commands
from src.caps import award_caps_commands
from src.caps import remove_caps_commands
from src.action_points import view_ap_commands
from src.action_points import add_ap_player_commands

from src import database_pg as database

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Setup
@bot.event
async def setup_hook():
    await bot.tree.sync()
    print("Slash commands synced!")

@bot.event
async def on_ready():
    database.setup_database()
    print(f'We have logged in as {bot.user}')
    print(f'discord.py API version: {discord.__version__}')

# Commands
hello(bot)
dice_commands(bot)
view_caps_commands(bot)
award_caps_commands(bot)
remove_caps_commands(bot)
view_ap_commands(bot)
add_ap_player_commands(bot)



def main() -> None:
    load_dotenv()
    api_token = os.getenv("API_TOKEN")
    if api_token is None:
        print("Error: API_TOKEN environment variable not set.")
        return
    bot.run(api_token, log_handler=handler, log_level=logging.DEBUG)

if __name__ == "__main__":
    main()
