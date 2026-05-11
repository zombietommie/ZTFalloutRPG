import discord
from discord.ext import commands

def hello(bot: commands.Bot) -> None:
    @bot.tree.command(name="hello", description="Bot says hello")
    async def say_hello(interaction: discord.Interaction):
        await interaction.response.send_message(f"Hello {interaction.user.mention}!")