print("Fallout RPG Discord Bot!")

import discord
from discord.ext import commands
import os
from discord import app_commands
from dotenv import load_dotenv
import logging

from src import dice
from src import database_pg as database

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def setup_hook():
    await bot.tree.sync()
    print("Slash commands synced!")

@bot.event
async def on_ready():
    print(f'Database setting up!')
    database.setup_database()
    print(f'We have logged in as {bot.user}')
    print(f'discord.py API version: {discord.__version__}')

@bot.tree.command(name="hello", description="Saying Hello!")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello {interaction.user.mention}!!")

@bot.tree.command(name="caps", description="View how much caps you have.")
async def caps(interaction: discord.Interaction):
    await interaction.response.send_message(f'{interaction.user.mention} you have {database.get_player_caps(interaction.user.id)} caps!')

@bot.tree.command(name="award_caps", description="[GM-ONLY] Award caps to a player.")
@app_commands.describe(
    user_to_award="The player to award caps to",
    amount="The amount of caps to award"
)
@app_commands.checks.has_permissions(administrator=True)
async def award_caps(interaction: discord.Interaction, user_to_award: discord.User, amount: int):
    if amount <= 0:
        await interaction.response.send_message("You must award a positive number of caps.", ephemeral=True)
        return

    # Check if user exist in DB
    database.insert_player(user_to_award.id, user_to_award.name, 0)

    # Award the caps
    database.award_caps(user_to_award.id, amount)
    await interaction.response.send_message(f"Awarded {amount} caps to {user_to_award.mention}! You now have {database.get_player_caps(user_to_award.id)} caps")

@bot.tree.command(name="secret", description="Only you can see this!!!")
async def secret(interaction: discord.Interaction):
    await interaction.response.send_message("This is a private message!",ephemeral=True)

load_dotenv()

api_token = os.getenv("API_TOKEN")
if api_token is None:
    print("Error: API_TOKEN environment variable not set.")
else:
    bot.run(api_token, log_handler=handler, log_level=logging.DEBUG)