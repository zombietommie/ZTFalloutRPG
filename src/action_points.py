import discord
from discord import app_commands
from discord.ext import commands
from src import database_pg as database


# This is the action point where we will set the limit for the players but the
# Game master will have unlimited, but let's set a standard 25.
# will need to implement DB to persist the pool

# Reminder to self, no double quotes in double quotes!!!

# According to the book players share the one Action Point Pool
# The pool is maxed out at 5, any gained will be ignored.

# First start being able to view AP (GM and player group, then we'll split after)
def view_ap_commands(bot: commands.Bot):
    @bot.tree.command(name="view_ap" , description="Allow to view AP on both sides")
    async def view_ap(interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Players AP: {database.get_ap(database.PLAYER_AP_POOL)} \n"
            f"GM AP: {database.get_ap(database.GM_AP_POOL)}"
        )

# Adding AP
def add_ap_player_commands(bot: commands.Bot):
    @bot.tree.command(name="add_ap_player", description="[GM-only] Add AP to the pool of players.")
    @app_commands.describe(
        amount="The amount of AP to award."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def add_ap_player(interaction: discord.Interaction, amount: int):
        if amount <= 0:
            await interaction.response.send_message("You must enter a positive number of AP", ephemeral=True)
            return

        current_ap = database.get_ap(database.PLAYER_AP_POOL)

        if current_ap >= database.PLAYER_AP_POOL_MAX:
            await interaction.response.send_message("Player AP Pool maxed out, cannot add!")
            return

        new_ap = database.add_ap(database.PLAYER_AP_POOL, amount)

        if current_ap + amount > database.PLAYER_AP_POOL_MAX:
            await interaction.response.send_message(
                f"Player AP Pool maxed out at {new_ap}. Extra AP was ignored."
            )
            return

        await interaction.response.send_message(
            f"Added {amount} AP to the player pool!\nPlayer AP Pool: {new_ap}."
        )
