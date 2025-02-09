import discord
from discord import app_commands
from APIs.UselessAPIs import UselessAPIs
from APIs.CalendarAPI import CalendarAPI
from APIs.AdventOfCodeAPI import AdventOfCodeAPI
from APIs.SweccAPI import SweccAPI
import os
from dotenv import load_dotenv
from .utils import handle_cohort_stat_update

useless = UselessAPIs()
calendar = CalendarAPI()
aoc_api = AdventOfCodeAPI()
swecc_api = SweccAPI()

LEADERBOARD_KEY = os.getenv("AOC_LEADERBOARD_KEY")


async def google_xyz(ctx: discord.Interaction):
    message = (
        "To make your resume stand out, consider using the Google XYZ format. "
        "This method highlights your achievements in a clear, concise way by structuring each bullet point as follows: "
        "'Accomplished [X] as measured by [Y], by doing [Z].' "
        "\n\nFor example:\n"
        "- 'Increased page views (X) by 23% (Y) in six months by implementing social media distribution strategies (Z).'\n"
        "- 'Reduced costs (X) by 10% (Y) by leading a major cost rationalization program (Z).'\n"
        "\nThis approach helps recruiters quickly understand your impact and how you achieved it, providing a comprehensive view of your successes. "
        "It's particularly effective for demonstrating practical abilities and aligning your skills with the company's values and priorities."
    )
    await ctx.response.send_message(message)


async def full_resume_guide(ctx: discord.Interaction):
    await ctx.response.send_message(
        "Here is a comprehensive resume wiki: https://www.reddit.com/r/EngineeringResumes/wiki/index/"
    )


async def useless_facts(ctx: discord.Interaction):
    fact = useless.useless_facts()
    await ctx.response.send_message(fact, ephemeral=bot_context.ephemeral)


async def kanye(ctx: discord.Interaction):
    data = useless.kanye_quote()
    await ctx.response.send_message(data, ephemeral=bot_context.ephemeral)


async def cat_fact(ctx: discord.Interaction):
    data = useless.cat_fact()
    await ctx.response.send_message(data, ephemeral=bot_context.ephemeral)


async def say_hi(ctx: discord.Interaction):
    await ctx.response.send_message("hi", ephemeral=True)


async def aoc_leaderboard(ctx: discord.Interaction):
    leaderboard_data = await aoc_api.get_leaderboard()

    embed = discord.Embed(
        title=f"🎄 Current Leaderboard 🎄", description=f"", color=0x1F8B4C
    )

    if leaderboard_data:
        leaderboard_text = "\n".join(
            f"**#{index + 1}: {member['name']}** - {member['local_score']} points"
            for index, member in enumerate(leaderboard_data[:10])
        )
        embed.add_field(
            name="🎖️ Leaderboard (Top 10)",
            value=(
                f"{leaderboard_text}\n\n"
                f"[View full leaderboard]({aoc_api.get_leaderboard_url()})\n\n"
            ),
            inline=False,
        )

    embed.set_footer(text=f"Leaderboard join key: {LEADERBOARD_KEY} ")
    embed.set_thumbnail(url="https://adventofcode.com/favicon.png")
    await ctx.response.send_message(embed=embed, ephemeral=bot_context.ephemeral)


@app_commands.describe(order="Sort leaderboard by different metrics")
@app_commands.choices(
    order=[
        app_commands.Choice(name="Total Problems Solved (default)", value="total"),
        app_commands.Choice(name="Easy Problems Solved", value="easy"),
        app_commands.Choice(name="Medium Problems Solved", value="medium"),
        app_commands.Choice(name="Hard Problems Solved", value="hard"),
    ]
)
async def leetcode_leaderboard(ctx: discord.Interaction, order: str = "total"):
    leaderboard_data = swecc_api.leetcode_leaderboard(order_by=order)

    embed = discord.Embed(
        title="🏆 Leetcode Leaderboard",
        description=f"By: **{order.title()}**",
        color=discord.Color.gold(),
    )

    if leaderboard_data:
        medals = ["🥇", "🥈", "🥉"] + [""] * 7
        leaderboard_text = [
            f"{medals[i]}{f'**#{i+1}**' if i > 2 else ''} "
            f"[**{user['user']['username']}**](https://leetcode.com/{user['user']['username']})\n"
            f"└─ 🔢 Total: {user['total_solved']} | "
            f"🟢 Easy: {user['easy_solved']} | "
            f"🟡 Med: {user['medium_solved']} | "
            f"🔴 Hard: {user['hard_solved']}"
            for i, user in enumerate(leaderboard_data["results"][:10])
        ]
        embed.add_field(
            name="Top 10", value="\n\n".join(leaderboard_text[:5]), inline=False
        )
        embed.add_field(name="", value="\n\n".join(leaderboard_text[5:]), inline=False)

    embed.add_field(
        name="🔗 View the full leaderboard below!",
        value=f"[leaderboard.swecc.org](https://leaderboard.swecc.org)",
        inline=False,
    )

    await ctx.response.send_message(embed=embed, ephemeral=bot_context.ephemeral)


@app_commands.describe(order="Sort leaderboard by different metrics")
@app_commands.choices(
    order=[
        app_commands.Choice(name="Total Commits this Year (default)", value="commits"),
        app_commands.Choice(name="Total PRs this year", value="prs"),
        app_commands.Choice(name="Follower Count", value="followers"),
    ]
)
async def github_leaderboard(ctx: discord.Interaction, order: str = "commits"):
    leaderboard_data = swecc_api.github_leaderboard(order_by=order)[:10]

    embed = discord.Embed(
        title="🏆 Github Leaderboard",
        description=f"By: **{order.title()}**",
        color=discord.Color.green(),
    )

    if leaderboard_data:
        medals = ["🥇", "🥈", "🥉"] + [""] * 7
        leaderboard_text = [
            f"{medals[i]}{f'**#{i+1}**' if i > 2 else ''} "
            f"[**{user['user']['username']}**](https://github.com/{user['user']['username']})\n"
            f"└─ 🔢 Total Commits: {user['total_commits']} | "
            f"🔗 Total PRs: {user['total_prs']} | "
            f"👥 Followers: {user['followers']}"
            for i, user in enumerate(leaderboard_data["results"][:10])
        ]
        embed.add_field(
            name="Top 10", value="\n\n".join(leaderboard_text[:5]), inline=False
        )
        embed.add_field(name="", value="\n\n".join(leaderboard_text[5:]), inline=False)

    embed.add_field(
        name="🔗 View the full leaderboard below!",
        value=f"[leaderboard.swecc.org](https://leaderboard.swecc.org)",
        inline=False,
    )

    await ctx.response.send_message(embed=embed, ephemeral=bot_context.ephemeral)


async def next_meeting(ctx: discord.Interaction):
    meeting_info = await calendar.get_next_meeting()
    calendar_hyperlink = f"[SWECC Public Calendar]({calendar.get_url()})"
    if meeting_info:
        embed = discord.Embed(
            title=f"📅 Next Meeting: {meeting_info['name']}",
            description=f"**Description:** {meeting_info['description'] or 'No description available.'}\n\n",
            color=discord.Color.blue(),
        )

        embed.add_field(name="🕒 Date & Time", value=meeting_info["date"], inline=False)
        embed.add_field(
            name="📍 Location",
            value=meeting_info["location"] or "Not specified",
            inline=False,
        )
        embed.add_field(name="🔗 Calendar Link", value=calendar_hyperlink, inline=False)

        await ctx.response.send_message(embed=embed)
    else:
        await ctx.response.send_message("No upcoming meetings found.")


async def attend(ctx: discord.Interaction, session_key: str):
    status, data = await swecc_api.attend_event(ctx.user.id, session_key)

    if status == 201:
        embed = discord.Embed(
            title="Success!",
            description=f"Your attendance was successfully registered!",
            color=discord.Color.green(),
        )

        await ctx.response.send_message(
            embed=embed,
            ephemeral=bot_context.ephemeral,
        )
    else:

        embed = discord.Embed(
            title="Error", description=data["error"], color=discord.Color.red()
        )

        await ctx.response.send_message(embed=embed, ephemeral=bot_context.ephemeral)


async def daily_check(ctx: discord.Interaction, cohort_name: str):
    data, error = await swecc_api.update_cohort_stats(
        ctx.user.id, cohort_name, "dailycheck"
    )

    await handle_cohort_stat_update(
        ctx,
        data,
        error,
        bot_context,
        "Daily Check",
        "Your daily check was successfully recorded!",
    )


async def online_assessment(ctx: discord.Interaction, amt: int, cohort_name: str):
    data, error = await swecc_api.update_cohort_stats(
        ctx.user.id, cohort_name, f"oa/{amt}"
    )

    await handle_cohort_stat_update(
        ctx,
        data,
        error,
        bot_context,
        title="Online Assessment",
        description="Your online assessment was successfully recorded!",
    )


async def interview(ctx: discord.Interaction, amt: int, cohort_name: str):
    data, error = await swecc_api.update_cohort_stats(
        ctx.user.id, cohort_name, f"interview/{amt}"
    )

    await handle_cohort_stat_update(
        ctx,
        data,
        error,
        bot_context,
        "Interview",
        "Your interview was successfully recorded!",
    )


async def offer(ctx: discord.Interaction, amt: int, cohort_name: str):
    data, error = await swecc_api.update_cohort_stats(
        ctx.user.id, cohort_name, f"offer/{amt}"
    )

    await handle_cohort_stat_update(
        ctx,
        data,
        error,
        bot_context,
        "Offer",
        "Your offer was successfully recorded! (congrats! 🎉)",
    )


async def apply(ctx: discord.Interaction, amt: int, cohort_name: str):
    data, error = await swecc_api.update_cohort_stats(
        ctx.user.id, cohort_name, f"apply/{amt}"
    )

    await handle_cohort_stat_update(
        ctx,
        data,
        error,
        bot_context,
        "Application",
        "Your application was successfully recorded!",
    )


def setup(client, context):
    global bot_context
    bot_context = context
    client.tree.command(name="say_hi")(say_hi)
    client.tree.command(name="xyz")(google_xyz)
    client.tree.command(name="resume_guide")(full_resume_guide)
    client.tree.command(name="useless_fact")(useless_facts)
    client.tree.command(name="kanye")(kanye)
    client.tree.command(name="cat_fact")(cat_fact)
    client.tree.command(name="next_meeting")(next_meeting)
    client.tree.command(name="aoc_leaderboard")(aoc_leaderboard)
    client.tree.command(name="leetcode_leaderboard")(leetcode_leaderboard)
    client.tree.command(name="github_leaderboard")(github_leaderboard)
    client.tree.command(name="attend")(attend)
    client.tree.command(name="daily_check")(daily_check)
    client.tree.command(name="online_assessment")(online_assessment)
    client.tree.command(name="interview")(interview)
    client.tree.command(name="offer")(offer)
    client.tree.command(name="application")(apply)
