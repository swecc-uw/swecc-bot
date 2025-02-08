import discord


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
