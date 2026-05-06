print("Fallout RPG Discord Bot!")

import discord
import os
from dotenv import load_dotenv

from src import dice, database

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Database setting up!')
    database.setup_database()
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('/hello'):
        await message.channel.send(f'Hello {message.author.mention}! I am a bot!')
    if message.content.startswith('/roll'):
        await message.channel.send(f"@{message.author.mention} you rolled{dice.rollDice()}")
    if message.content.startswith('/caps'):
        caps = database.get_player_caps(message.author.id)
        await message.channel.send(f'@{message.author.mention} you have {caps} caps!')

load_dotenv()

api_token = os.getenv("API_TOKEN")
if api_token is None:
    print("Error: API_TOKEN environment variable not set.")
else:
    client.run(api_token)