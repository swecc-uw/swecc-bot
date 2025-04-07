import logging
from .utils import slugify
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

    await ctx.response.defer(ephemeral=True)

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

        write = {
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
            write["discord_channel_id"] = channel.id
            msg.append(f"Created channel {channel.mention} for cohort {cohort['name']}")
        else:
            existing_channel_name = channel.name
            slug = slugify(cohort["name"])
            if existing_channel_name != slug:
                await channel.edit(name=slug, reason="Cohort channel name updated by bot.")
                msg.append(f"Updated channel {channel.mention} to {slug} for cohort {cohort['name']}")
            else:
                msg.append(f"Channel {channel.mention} already exists for cohort {cohort['name']}")

        if role is None:
            role = await guild.create_role(
                name=cohort["name"],
                reason="Cohort role created by bot.",
                mentionable=True
            )
            write["discord_role_id"] = role.id
            msg.append(f"Created role {role.name} for cohort {cohort['name']}")
        else:
            existing_role_name = role.name

            if existing_role_name != cohort["name"]:
                await role.edit(name=cohort["name"], reason="Cohort role name updated by bot.")
                msg.append(f"Updated role {role.name} to {cohort['name']}")
            else:
                msg.append(f"Role {role.name} already exists for cohort {cohort['name']}")
        if channel_id is None or role_id is None:
            writes.append(write)

        # add perms to channel
        await channel.set_permissions(role, read_messages=True, send_messages=True)

        # add members to role
        for discord_id in cohort["discord_member_ids"]:
            member = guild.get_member(discord_id)
            if member is not None:
                await member.add_roles(role, reason="Cohort role added by bot.")
                msg.append(f"Added {member.mention} to role {role.name} for cohort {cohort['name']}")
            else:
                msg.append(f"Member {discord_id} not found in guild for cohort {cohort['name']}")


    if msg:
        await bot_context.log(ctx, "\n".join(msg))

    await swecc.upload_cohort_metadata(writes)


def setup(client, context):
    global bot_context
    bot_context = context
    client.tree.command(name="set_ephemeral")(set_ephemeral)
    client.tree.command(name="sync_cohort_channels")(sync_cohort_channels)