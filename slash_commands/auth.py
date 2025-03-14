import discord
import os
from APIs.SweccAPI import SweccAPI

swecc = SweccAPI()

class VerifyModal(discord.ui.Modal, title="Verify Your Account"):
    def __init__(self, bot_context):
        super().__init__(timeout=None)

        self.VERIFIED_ROLE_ID = int(os.getenv("VERIFIED_ROLE_ID"))

        self.bot_context = bot_context

        self.code = discord.ui.TextInput(
            label="Username",
            style=discord.TextStyle.short,
            placeholder="Enter your website username.",
        )

        self.add_item(self.code)

    async def on_submit(self, interaction: discord.Interaction):
        username = interaction.user.name
        user_id = interaction.user.id
        auth_code = self.code.value

        response = swecc.auth(username, user_id, auth_code)
        if response == 200:
            await interaction.response.send_message(
                "Authentication successful!", ephemeral=True
            )
            await self.bot_context.log(
                interaction,
                f"{interaction.user.display_name} has verified their account.",
            )

            if (role := interaction.guild.get_role(self.VERIFIED_ROLE_ID)) is None:
                await self.bot_context.log(
                    interaction,
                    f"ERROR: Role {self.VERIFIED_ROLE_ID} not found for {interaction.user.display_name}",
                )
                return

            await interaction.user.add_roles(role)
            return
        await interaction.response.send_message(
            f"Authentication failed. Please try again. Verify you signed up with the correct username: **{username}**.",
            ephemeral=True,
        )
        await self.bot_context.log(
            interaction,
            f"{interaction.user.display_name} has failed to verified their account. - {response}.",
        )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        if not interaction.response.is_done():
            await interaction.response.send_message(
                f"Something went wrong", ephemeral=True
            )
            await self.bot_context.log(
                interaction,
                f"{interaction.user.display_name} has failed to verified their account. - {error}",
            )


async def auth(ctx: discord.Interaction):
    await ctx.response.send_modal(
        VerifyModal(
            bot_context,
        )
    )


async def reset_password(ctx: discord.Interaction):
    try:
        url = await swecc.reset_password(ctx.user.name, ctx.user.id)
        embed = discord.Embed(
            title="Reset Password",
            description=f"[Click here to reset your password]({url})",
            color=discord.Color.blue(),
        )
        await bot_context.log(
            ctx, f"{ctx.user.display_name} has requested to reset their password."
        )
        await ctx.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        await ctx.response.send_message("Something went wrong", ephemeral=True)
        await bot_context.log(
            ctx, f"ERROR: Password reset failed for {ctx.user.display_name}: {e}"
        )


def setup(client, context):
    global bot_context
    bot_context = context
    client.tree.command(name="verify")(auth)
    client.tree.command(name="reset_password")(reset_password)
