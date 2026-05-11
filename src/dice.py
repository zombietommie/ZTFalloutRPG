import random

import discord
from discord.ext import commands

def roll_dice() -> str:
    d1 = random.randint(1, 20)
    d2 = random.randint(1, 20)
    return f"You rolled {d1} and {d2}"

def dice_commands(bot: commands.Bot) -> None:
    @bot.tree.command(name="roll", description="Roll 2d20s")
    async def roll(interaction: discord.Interaction) -> None:
        await interaction.response.send_message(f"Rolling.... {roll_dice()}")

