import discord
from discord import app_commands
from discord.ext import commands
from src import database_pg as database


# This is the action point where we will set the limit for the players but the
# Game master will have unlimited, but let's set a standard 25.
# will need to implement DB to persist the pool

# According to the book players share the one Action Point Pool
# The pool is maxed out at 5, any gained will be ignored.

# First start being able to view AP (GM and player group, then we'll split after)
def view_ap_commands(bot: commands.Bot):
    @bot.tree.command(name="view_ap" , description="Allow to view AP on both sides")
    async def view_ap(interaction: discord.Interaction):
        await interaction.response.send_message(f"Players AP: {database.get_ap("PLAYER_AP_POOL")} \n GM AP: {database.get_ap("GM_AP_POOL")}")