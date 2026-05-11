import discord
from discord import app_commands
from discord.ext import commands
from src import database_pg as database

# view caps
def view_caps_commands(bot: commands.Bot) -> None:
    @bot.tree.command(name="view_caps", description="View your caps")
    async def caps(interaction: discord.Interaction):
        await interaction.response.send_message(f"{interaction.user.mention} you have {database.get_player_caps(interaction.user.id)} caps!")

# award caps
def award_caps_commands(bot: commands.Bot) -> None:
    @bot.tree.command(name="award caps", description="[GM-ONLY] Award caps to a player.")
    @app_commands.describe(
        user_to_award="The player to award caps to.",
        amoutn="The amount of caps to award."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def award_caps(interaction: discord.Interaction, user_to_award: discord.User, amount: int):
        if amount <= 0:
            await interaction.response.send_message("You must award a positive number of caps", ephemeral=True)
            return

        #Checks if user exist in DB
        database.insert_player(user_to_award.id, user_to_award.name, 0)

        # Award the caps
        database.award_caps(user_to_award.id, amount)
        await interaction.response.send_message(f"Awarded {amount} caps to {user_to_award.mention}! You now have {database.get_player_caps(user_to_award.id)} caps.")

# Removing caps
def remove_caps_commands(bot: commands.Bot) -> None:
    @bot.tree.command(name="remove_caps", description="[GM-ONLY] Remove caps from a player.")
    @app_commands.describe(
        user_to_remove="The player to remove caps from.",
        amount="The amount of caps to remove."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_caps(interaction: discord.Interaction, user_to_remove: discord.User, amount: int):
        if amount <= 0:
            await interaction.response.send_message("You must remove a positive number of caps", ephemeral=True)
            return

        # Checks if user exist in DB
        database.insert_player(user_to_remove.id, user_to_remove.name, 0)

        # Remove the caps
        new_cap = database.remove_caps_clamped(user_to_remove.id, amount)
        await interaction.response.send_message(f"Removed {amount} caps from {user_to_remove.mention}! You now have {new_cap} caps")