import discord
from APIs.SweccAPI import SweccAPI

class VerifyModal(discord.ui.Modal, title="Verify your account"):
    def __init__(self, bot_context):
        super().__init__(timeout=None)
        self.bot_context = bot_context
        self.swecc = SweccAPI()

        self.code = discord.ui.TextInput(
            label="Code",
            style=discord.TextStyle.short,  
            placeholder="Enter your verification code",
        )

        self.add_item(self.code)

    async def on_submit(self, interaction: discord.Interaction):
        username = interaction.user.id
        user_id = interaction.user.name
        auth_code = self.code.value
        response = self.swecc.auth(username, user_id, auth_code)
        if response == 200:
            await interaction.response.send_message("Authentication successful!", ephemeral=True)
            await self.bot_context.log(interaction, f"{interaction.user.display_name} has verified their account.")
            return
        await interaction.response.send_message("Authentication failed. Please try again.", ephemeral=True)
        await self.bot_context.log(interaction, f"{interaction.user.display_name} has failed to verified their account. - {response}")

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        if not interaction.response.is_done():
            await interaction.response.send_message(f"Something went wrong", ephemeral=True)
            await self.bot_context.log(interaction, f"{interaction.user.display_name} has failed to verified their account. - {error}")

async def auth(ctx: discord.Interaction):
    await ctx.response.send_modal(VerifyModal(bot_context))

def setup(client, context):
    global bot_context
    bot_context = context
    client.tree.command(name="auth")(auth)
