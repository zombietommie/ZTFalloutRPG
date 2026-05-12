import os
import logging
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

from src.hello import hello
from src.dice import dice_commands
from src.caps import view_caps_commands, award_caps_commands, remove_caps_commands
from src.action_points import view_ap_commands, spend_ap_player_commands, add_ap_player_commands, add_ap_gm_commands, \
    spend_ap_gm_commands

from src import database_pg as database

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = Path(os.getenv("LOG_FILE", BASE_DIR / "logs" / "discord.log"))
LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def configure_logging() -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(LOG_FORMAT)
    file_handler = logging.FileHandler(filename=LOG_FILE, encoding="utf-8", mode="a")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    logging.getLogger("discord").setLevel(logging.DEBUG)


configure_logging()
logger = logging.getLogger("ztfalloutrpg")
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Setup
@bot.event
async def setup_hook():
    await bot.tree.sync()
    logger.info("Slash commands synced.")

@bot.event
async def on_ready():
    database.setup_database()
    logger.info("We have logged in as %s", bot.user)
    logger.info("discord.py API version: %s", discord.__version__)

# Commands
hello(bot)
dice_commands(bot)
view_caps_commands(bot)
award_caps_commands(bot)
remove_caps_commands(bot)
view_ap_commands(bot)
add_ap_player_commands(bot)
spend_ap_player_commands(bot)
add_ap_gm_commands(bot)
spend_ap_gm_commands(bot)


def main() -> None:
    load_dotenv()
    api_token = os.getenv("API_TOKEN")
    if api_token is None:
        logger.error("API_TOKEN environment variable not set.")
        return

    logger.info("Writing bot logs to %s", LOG_FILE)
    bot.run(api_token, log_handler=None)

if __name__ == "__main__":
    main()
