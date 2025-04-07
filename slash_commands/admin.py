from calendar import c
import logging
import discord
from APIs.SweccAPI import SweccAPI

swecc = SweccAPI()

# TODO: Implement admin endpoint to check if user is admin
async def set_ephemeral(ctx: discord.Interaction):
    if ctx.user.id == 408491888522428419:
        bot_context.ephemeral = not bot_context.ephemeral
        await ctx.response.send_message(f"Ephemeral set to {bot_context.ephemeral}", ephemeral=True)
    else:
        await ctx.response.send_message("You do not have permission to use this command.", ephemeral=True)

async def sync_cohort_channels(ctx: discord.Interaction) -> None:

    ctx.response.defer(ephemeral=bot_context.ephemeral)

    category_id = bot_context.cohort_category_id

    cohort_metadata = await swecc.get_cohort_metadata()

    guild = ctx.guild
    category = guild.get_channel(category_id)
    if category is None:
        await ctx.response.send_message("Cohort category not found.", ephemeral=True)
        return

    writes = []

    msg = []
    for cohort in cohort_metadata:
        channel_id = cohort.get("discord_channel_id")
        role_id = cohort.get("discord_role_id")
        channel = None if channel_id is None else guild.get_channel(channel_id)
        role = None if role_id is None else guild.get_role(role_id)

        w = {
            "id": cohort["id"],
            "discord_channel_id": channel_id,
            "discord_role_id": role_id,
        }

        if channel is None:
            channel = await guild.create_text_channel(
                name=cohort["name"],
                category=category,
                topic=f"{cohort['name']}",
                reason="Cohort channel created by bot.",
            )
            w["discord_channel_id"] = channel.id
            msg.append(f"Created channel {channel.mention} for cohort {cohort['name']}")
        else:
            existing_channel_name = channel.name

            if existing_channel_name != cohort["name"].lower().replace(" ", "-").replace("'", ""):
                await channel.edit(name=cohort["name"], reason="Cohort channel name updated by bot.")
                msg.append(f"Updated channel {channel.mention} to {cohort['name']}")
            else:
                msg.append(f"Channel {channel.mention} already exists for cohort {cohort['name']}")

        if role is None:
            role = await guild.create_role(
                name=cohort["name"],
                reason="Cohort role created by bot.",
                mentionable=True
            )
            w["discord_role_id"] = role.id
            msg.append(f"Created role {role.name} for cohort {cohort['name']}")
        else:
            existing_role_name = role.name

            if existing_role_name != cohort["name"]:
                await role.edit(name=cohort["name"], reason="Cohort role name updated by bot.")
                msg.append(f"Updated role {role.name} to {cohort['name']}")
            else:
                msg.append(f"Role {role.name} already exists for cohort {cohort['name']}")
        if channel_id is None or role_id is None:
            writes.append(w)

    if msg:
        await ctx.response.send_message("\n".join(msg), ephemeral=bot_context.ephemeral)

    await swecc.upload_cohort_metadata(writes)


def setup(client, context):
    global bot_context
    bot_context = context
    client.tree.command(name="set_ephemeral")(set_ephemeral)
    client.tree.command(name="sync_cohort_channels")(sync_cohort_channels)