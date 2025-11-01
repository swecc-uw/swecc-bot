import discord
import secrets
from APIs.SweccAPI import SweccAPI

swecc = SweccAPI()


class RegisterModal(discord.ui.Modal, title="Register Your Account"):
    def __init__(self, bot_context, verified_role):
        super().__init__(timeout=None)
        self.bot_context = bot_context
        self.verified_role = verified_role

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

        self.add_item(self.username)
        self.add_item(self.first_name)
        self.add_item(self.last_name)
        self.add_item(self.email)

    async def on_submit(self, interaction: discord.Interaction):
        username = self.username.value
        first_name = self.first_name.value
        last_name = self.last_name.value
        email = self.email.value
        discord_username = interaction.user.name
        user_id = interaction.user.id

        password = secrets.token_urlsafe(32)

        status, response = swecc.register(
            username, first_name, last_name, email, password, discord_username
        )

        if status == 201:
            auth_response = swecc.auth(discord_username, user_id, username)

            (id, reset_password_url, detail) = (
                response["id"],
                response["reset_password_url"],
                response["detail"],
            )

            if auth_response == 200:
                usr_msg = f"{detail} Your account has been verified, and you can now reset your password [here]({reset_password_url})."
                sys_msg = f"{interaction.user.display_name} has registered and verified their account with username {username} and id {id}."

                await interaction.response.send_message(usr_msg, ephemeral=True)
                await self.bot_context.log(interaction, sys_msg)
                await interaction.user.add_roles(self.verified_role)

            else:
                usr_msg = f"Registration successful, but automatic verification failed. Please use /verify to link your account. Error: {auth_response}"
                sys_msg = f"{interaction.user.display_name} registered an account but automatic verification failed. - {auth_response}."

                await interaction.response.send_message(usr_msg, ephemeral=True)
                await self.bot_context.log(interaction, sys_msg)
        else:
            error_message = response.get(
                "detail",
                "Internal server error. Please try again later, or contact one of the officers.",
            )
            usr_msg = f"Registration failed. Please try again. Error: {error_message}"
            sys_msg = f"{interaction.user.display_name} has failed to register an account with status {status}. - {response}."

            await interaction.response.send_message(usr_msg, ephemeral=True)
            await self.bot_context.log(interaction, sys_msg)

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        if not interaction.response.is_done():
            await interaction.response.send_message(
                f"Something went wrong during registration: {error}", ephemeral=True
            )
            await self.bot_context.log(
                interaction,
                f"{interaction.user.display_name} has failed to register an account. - {error}",
            )


async def register(ctx: discord.Interaction):
    verified_rid = bot_context.verified_role_id
    if (role := ctx.guild.get_role(verified_rid)) and role in ctx.user.roles:
        usr_msg = f"You are already verified"
        sys_msg = (
            f"{ctx.user.display_name} has tried to register but is already verified."
        )

        await ctx.response.send_message(usr_msg, ephemeral=True)
        await bot_context.log(ctx, sys_msg)
    elif role is None:
        usr_msg = f"Something went wrong. Please contact an admin."
        sys_msg = f"ERROR: Role {verified_rid} not found, skipping registration for {ctx.user.display_name}"

        await ctx.response.send_message(usr_msg, ephemeral=True)
        await bot_context.log(ctx, sys_msg)
    else:
        await ctx.response.send_modal(RegisterModal(bot_context, role))


class VerifyModal(discord.ui.Modal, title="Verify Your Account"):
    def __init__(self, bot_context):
        super().__init__(timeout=None)

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

            if (
                role := interaction.guild.get_role(self.bot_context.verified_role_id)
            ) is None:
                await self.bot_context.log(
                    interaction,
                    f"ERROR: Role {self.bot_context.verified_role_id} not found for {interaction.user.display_name}",
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
