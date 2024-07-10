import discord
from discord import app_commands

async def auth(ctx: discord.Interaction, auth_code: str):
    user_id = ctx.user.id
    username = ctx.user.name
    response = swecc.auth(username, user_id, auth_code)
    if response == 200:
        await ctx.response.send_message("Authentication successful!", ephemeral=True)
        return
    await ctx.response.send_message("Authentication failed. Please try again.", ephemeral=True)

async def say_hi(ctx: discord.Interaction):
    await ctx.response.send_message("hi", ephemeral=True)

def setup(client, swecc_instance):
    global swecc
    swecc = swecc_instance
    client.tree.command(name="auth")(auth)
    app_commands.describe(auth_code="Authentication code")(auth)
