print("Fallout RPG Discord Bot!")

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

from src import dice, database

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

@bot.tree.command(name="hello", description="Saying Hello!")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello {interaction.user.mention}!!")

@bot.tree.command(name="caps", description="View how much caps you have.")
async def caps(interaction: discord.Interaction):
    await interaction.response.send_message(f'{interaction.user.mention} you have {database.get_player_caps(interaction.user.id)} caps!')

@bot.tree.command(name="secret", description="Only you can see this!!!")
async def secret(interaction: discord.Interaction):
    await interaction.response.send_message("This is a private message!",ephemeral=True)

load_dotenv()

api_token = os.getenv("API_TOKEN")
if api_token is None:
    print("Error: API_TOKEN environment variable not set.")
else:
    bot.run(api_token)