print("Fallout RPG Discord Bot!")

import discord
import os
from dotenv import load_dotenv

from src import dice

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('/hello'):
        await message.channel.send('Hello!')
    if message.content.startswith('/roll'):
        await message.channel.send(f"@{message.author} you rolled{dice.rollDice()}")

load_dotenv()

api_token = os.getenv("API_TOKEN")
if api_token is None:
    print("Error: API_TOKEN environment variable not set.")
else:
    client.run(api_token)