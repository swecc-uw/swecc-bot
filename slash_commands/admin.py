import discord

# TODO: Implement admin endpoint to check if user is admin
async def set_ephemeral(ctx: discord.Interaction):
    if ctx.user.id == 408491888522428419:
        bot_context.ephemeral = not bot_context.ephemeral
        await ctx.response.send_message(f"Ephemeral set to {bot_context.ephemeral}", ephemeral=True)
    else:
        await ctx.response.send_message("You do not have permission to use this command.", ephemeral=True)

def setup(client, context):
    global bot_context
    bot_context = context
    client.tree.command(name="set_ephemeral")(set_ephemeral)