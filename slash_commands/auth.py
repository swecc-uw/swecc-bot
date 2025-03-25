import discord
import os
from APIs.SweccAPI import SweccAPI
from APIs.GeminiAPI import GeminiAPI

swecc = SweccAPI()
gemini = GeminiAPI()

class RegisterModal(discord.ui.Modal, title="Register Your Account"):
    def __init__(self, bot_context):
        super().__init__(timeout=None)
        self.bot_context = bot_context
        self.VERIFIED_ROLE_ID = int(os.getenv("VERIFIED_ROLE_ID"))
        self.OFF_TOPIC_CHANNEL_ID = int(os.getenv("OFF_TOPIC_CHANNEL_ID"))

        self.username = discord.ui.TextInput(
            label="Username",
            style=discord.TextStyle.short,
            placeholder="Enter your desired username",
            required=True,
        )

        self.first_name = discord.ui.TextInput(
            label="First Name",
            style=discord.TextStyle.short,
            placeholder="Enter your first name",
            required=True,
        )

        self.last_name = discord.ui.TextInput(
            label="Last Name",
            style=discord.TextStyle.short,
            placeholder="Enter your last name",
            required=True,
        )

        self.email = discord.ui.TextInput(
            label="Email",
            style=discord.TextStyle.short,
            placeholder="Enter your email address",
            required=True,
        )

        self.password = discord.ui.TextInput(
            label="Password (remember this!)",
            style=discord.TextStyle.short,
            placeholder="Enter your password",
            required=True,
        )

        self.add_item(self.username)
        self.add_item(self.first_name)
        self.add_item(self.last_name)
        self.add_item(self.email)
        self.add_item(self.password)

    async def on_submit(self, interaction: discord.Interaction):
        username = self.username.value
        first_name = self.first_name.value
        last_name = self.last_name.value
        email = self.email.value
        password = self.password.value
        discord_username = interaction.user.name
        user_id = interaction.user.id

        response = swecc.register(
            username,
            first_name,
            last_name,
            email,
            password,
            discord_username
        )

        if response == 201:
            auth_response = swecc.auth(discord_username, user_id, username)

            if auth_response == 200:
                await interaction.response.send_message(
                    "Registration successful! Your account has been verified.",
                    ephemeral=True
                )

                await self.bot_context.log(
                    interaction,
                    f"{interaction.user.display_name} has registered and verified their account with username {username}."
                )

                if role := interaction.guild.get_role(self.VERIFIED_ROLE_ID):
                    await interaction.user.add_roles(role)

                return

            await interaction.response.send_message(
                f"Registration successful, but automatic verification failed. Please use /verify to link your account. Error: {auth_response}",
                ephemeral=True
            )
            await self.bot_context.log(
                interaction,
                f"{interaction.user.display_name} registered an account but automatic verification failed. - {auth_response}."
            )
            return

        await interaction.response.send_message(
            f"Registration failed. Please try again. Error: {response}",
            ephemeral=True
        )
        await self.bot_context.log(
            interaction,
            f"{interaction.user.display_name} has failed to register an account. - {response}."
        )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        if not interaction.response.is_done():
            await interaction.response.send_message(
                f"Something went wrong during registration: {error}",
                ephemeral=True
            )
            await self.bot_context.log(
                interaction,
                f"{interaction.user.display_name} has failed to register an account. - {error}"
            )

async def register(ctx: discord.Interaction):
    await ctx.response.send_modal(
        RegisterModal(
            bot_context,
        )
    )

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
    client.tree.command(name="register")(register)
