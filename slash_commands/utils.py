import discord
import re


async def handle_cohort_stat_update(
    ctx: discord.Interaction, data, error, bot_context, title, description
):
    if not error:
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.green(),
        )

        await ctx.response.send_message(
            embed=embed,
            ephemeral=bot_context.ephemeral,
        )
    else:
        embed = discord.Embed(
            title="Error", description=error["message"], color=discord.Color.red()
        )
        await ctx.response.send_message(embed=embed, ephemeral=bot_context.ephemeral)


def is_valid_school_email(email: str) -> bool:
    return email.endswith("@uw.edu")

def slugify(value: str) -> str:
    value = value.lower().strip()
    # replace spaces with hyphens
    value = re.sub(r"\s+", "-", value)
    # ensure only single hyphens
    value = re.sub(r"-+", "-", value)
    # remove non-alphanumeric characters (except hyphens)
    value = re.sub(r"[^\w-]", "", value)
    return value