import discord
from discord import app_commands
from APIs.UselessAPIs import UselessAPIs
from APIs.CalendarAPI import CalendarAPI
from APIs.AdventOfCodeAPI import AdventOfCodeAPI
from APIs.SweccAPI import SweccAPI
from APIs.GeminiAPI import GeminiAPI
import os
from dotenv import load_dotenv
from mq.events import AttendanceEvent, CohortStatsUpdate
from .utils import handle_cohort_stat_update, is_valid_school_email
from typing import Optional
import mq.producers

useless = UselessAPIs()
calendar = CalendarAPI()
aoc_api = AdventOfCodeAPI()
swecc_api = SweccAPI()
gemini_api = GeminiAPI()

LEADERBOARD_KEY = os.getenv("AOC_LEADERBOARD_KEY")
TIMELINE_CHANNEL = int(os.getenv("TIMELINE_CHANNEL"))

async def bold_key_parts(ctx: discord.Interaction):
    message = (
        "Bold key parts of each experience so important details stand out — usually the tech stack or a standout metric. "
        "This draws attention without overloading your resume, keeping the focus on the most relevant skills.\n\n"
        "Example:\n"
        "- 'Designed a ticketing dashboard in **React** and **Node.js**, reducing support resolution time by 28%.'"

    )
    await ctx.response.send_message(message)


async def reverse_chronological(ctx: discord.Interaction):
    message = (
        "List your experiences in reverse chronological order — most recent first — so recruiters can quickly see your latest work. "
        "This is the standard format used in most resumes and avoids confusion when reviewing timelines.\n\n"
        "Example:\n"
        "Jun 2025 - Present : Software Engineering Intern, CompanyName\n"
        "Jan 2025 - May 2025 : Software Engineering Intern, CompanyName\n"
        "May 2024 - Aug 2024 : Research Assistant, LabName\n\n"
        "Even if you want to showcase older experiences, keeping everything in reverse chronological order makes it easier for recruiters to follow your career progression."
    )
    await ctx.response.send_message(message)


async def jakes_resume(ctx: discord.Interaction):
    message = (
        "Switch to Jake’s Resume format for a cleaner layout that’s easy for recruiters and ATS to scan: "
        "https://www.overleaf.com/latex/templates/jakes-resume/syzfjbzwjncs. "

        "\n\n If you use your UW email, you also get access to the student version of Overleaf for free."
    )
    await ctx.response.send_message(message)


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
    leaderboard_data = swecc_api.github_leaderboard(order_by=order)

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
    await mq.producers.publish_attend_event(
        AttendanceEvent(discord_id=ctx.user.id, session_key=session_key)
    )

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


async def cohort(ctx: discord.Interaction, show_all: bool = False):
    try:
        await ctx.response.defer(ephemeral=bot_context.ephemeral)
        cohorts = await swecc_api.get_cohort_stats(
            ctx.user.id if not show_all else None
        )

        if not cohorts:
            embed = discord.Embed(
                title="No Cohorts Found",
                description=(
                    "You are not currently enrolled in any cohorts."
                    if not show_all
                    else "No cohorts are available."
                ),
                color=discord.Color.red(),
            )
            await ctx.followup.send(embed=embed, ephemeral=bot_context.ephemeral)
            return

        for cohort in cohorts:
            cohort_name = cohort["cohort"]["name"]
            stats = cohort["stats"]
            total_apps = stats["applications"]
            success_rate = (stats["offers"] / total_apps * 100) if total_apps > 0 else 0

            formatted_stats = {key: f"{value:,}" for key, value in stats.items()}

            bar_length = 10
            filled_blocks = int(bar_length * success_rate / 100)
            progress_bar = "▰" * filled_blocks + "▱" * (bar_length - filled_blocks)

            embed = discord.Embed(
                title=f"🎓 {cohort_name}",
                color=discord.Color.blurple(),
                timestamp=ctx.created_at,
            )

            stats_text = (
                f"📝 **Applications:** {formatted_stats['applications']}\n"
                f"💻 **Online Assessments:** {formatted_stats['onlineAssessments']}\n"
                f"🎯 **Interviews:** {formatted_stats['interviews']}\n"
                f"🎊 **Offers:** {formatted_stats['offers']}\n"
                f"✅ **Daily Checks:** {formatted_stats['dailyChecks']}\n"
                f"🔥 **Streak** {formatted_stats['streak']}"
            )
            embed.add_field(name="Statistics", value=stats_text, inline=False)

            if total_apps > 0:
                progress_text = f"Success Rate: {success_rate:.1f}%\n" f"{progress_bar}"
                embed.add_field(name="Progress", value=progress_text, inline=True)

            embed.set_footer(text=f"Requested by {ctx.user.display_name}")

            await ctx.followup.send(embed=embed, ephemeral=bot_context.ephemeral)

    except Exception as e:
        error_embed = discord.Embed(
            title="Error",
            description="An error occurred while fetching cohort statistics. Please try again later.",
            color=discord.Color.red(),
        )
        await ctx.followup.send(embed=error_embed, ephemeral=True)


@app_commands.describe(cohort_name="The cohort name (optional)")
async def daily_check(ctx: discord.Interaction, cohort_name: Optional[str] = None):
    stat_url = "dailycheck"
    data, error = await swecc_api.update_cohort_stats(
        ctx.user.id, stat_url, cohort_name
    )
    await mq.producers.publish_cohort_stats_update_event(
        CohortStatsUpdate(ctx.user.id, stat_url, cohort_name=cohort_name)
    )

    await handle_cohort_stat_update(
        ctx,
        data,
        error,
        bot_context,
        "Daily Check",
        "Your daily check was successfully recorded!",
    )


@app_commands.describe(cohort_name="The cohort name (optional)")
async def online_assessment(
    ctx: discord.Interaction, cohort_name: Optional[str] = None
):
    stat_url = "oa"
    data, error = await swecc_api.update_cohort_stats(
        ctx.user.id, stat_url, cohort_name
    )
    await mq.producers.publish_cohort_stats_update_event(
        CohortStatsUpdate(ctx.user.id, stat_url, cohort_name=cohort_name)
    )
    updated_cohorts = ", ".join(data)
    await handle_cohort_stat_update(
        ctx,
        data,
        error,
        bot_context,
        title="Online Assessment",
        description=f"Your online assessment was successfully recorded in {updated_cohorts}!",
    )


@app_commands.describe(cohort_name="The cohort name (optional)")
async def interview(ctx: discord.Interaction, cohort_name: Optional[str] = None):
    stat_url = "interview"
    data, error = await swecc_api.update_cohort_stats(
        ctx.user.id, stat_url, cohort_name=cohort_name
    )

    await mq.producers.publish_cohort_stats_update_event(
        CohortStatsUpdate(ctx.user.id, stat_url, cohort_name=cohort_name)
    )

    updated_cohorts = ", ".join(data)

    await handle_cohort_stat_update(
        ctx,
        data,
        error,
        bot_context,
        "Interview",
        f"Your interview was successfully recorded in {updated_cohorts}!",
    )


@app_commands.describe(cohort_name="The cohort name (optional)")
async def offer(ctx: discord.Interaction, cohort_name: Optional[str] = None):
    stat_url = "offer"
    data, error = await swecc_api.update_cohort_stats(ctx.user.id, "offer", cohort_name)
    await mq.producers.publish_cohort_stats_update_event(
        CohortStatsUpdate(ctx.user.id, stat_url, cohort_name=cohort_name)
    )

    updated_cohorts = ", ".join(data)

    await handle_cohort_stat_update(
        ctx,
        data,
        error,
        bot_context,
        "Offer",
        f"Your offer was successfully recorded in {updated_cohorts}! Congratulations on the offer! 🎉",
    )


@app_commands.describe(cohort_name="The cohort name (optional)")
async def apply(ctx: discord.Interaction, cohort_name: Optional[str] = None):
    stat_url = "apply"
    data, error = await swecc_api.update_cohort_stats(
        ctx.user.id, stat_url=stat_url, cohort_name=cohort_name
    )
    await mq.producers.publish_cohort_stats_update_event(
        CohortStatsUpdate(ctx.user.id, stat_url, cohort_name=cohort_name)
    )

    updated_cohorts = ", ".join(data)

    await handle_cohort_stat_update(
        ctx,
        data,
        error,
        bot_context,
        "Application",
        f"Your application was successfully recorded in {updated_cohorts}!",
    )


@app_commands.describe(email="The UW email to verify. E.g.: [net-id]@uw.edu")
async def request_verify_school_email(ctx: discord.Interaction, email: str):

    if not is_valid_school_email(email):
        embed = discord.Embed(
            title="Invalid Email",
            description="Please use your UW email address to verify.",
            color=discord.Color.red(),
        )

        await ctx.response.send_message(
            embed=embed,
            ephemeral=bot_context.ephemeral,
        )
        return

    await ctx.response.defer(ephemeral=bot_context.ephemeral)

    data = await swecc_api.get_school_email_verification_url(ctx.user.id, email)

    if not data:
        embed = discord.Embed(
            title="Error",
            description="An error occurred while processing your request. Please try again later.",
            color=discord.Color.red(),
        )

        await ctx.followup.send(
            embed=embed,
            ephemeral=bot_context.ephemeral,
        )
        return

    embed = discord.Embed(
        title="Success!",
        description=f"An email has been sent to {email} with a verification link.",
        color=discord.Color.green(),
    )

    await ctx.followup.send(
        embed=embed,
        ephemeral=bot_context.ephemeral,
    )

class ProcessModal(discord.ui.Modal, title="Submit Process Timeline"):
    def __init__(self, bot_context, is_authorized, username, bot):
        super().__init__(timeout=None)
        self.bot_context = bot_context
        self.bot = bot
        self.is_authorized = is_authorized
        self.username = username

        self.company_name = discord.ui.TextInput(
            label="Company Name",
            style=discord.TextStyle.short,
            placeholder="Enter company name",
            required=True,
        )

        self.role = discord.ui.TextInput(
            label="Role",
            style=discord.TextStyle.short,
            placeholder="Enter role Eg. Software Engineer Intern",
            required=True,
        )

        self.timeline = discord.ui.TextInput(
            label="Timeline",
            style=discord.TextStyle.long,
            placeholder="Enter process timeline",
            required=True,
        )

        self.add_item(self.company_name)
        self.add_item(self.role)
        self.add_item(self.timeline)
    
    async def on_submit(self, interaction):
        await interaction.response.defer(ephemeral=True)

        company_name = self.company_name.value
        role = self.role.value
        timeline = self.timeline.value

        processed_timeline = await gemini_api.process_timeline_message(timeline, self.is_authorized, self.username) # pass only the timeline

        channel = self.bot.get_channel(TIMELINE_CHANNEL)

        if processed_timeline == "Not relevant":
            await interaction.followup.send(
                "Your description was not relevant!",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"Process for {company_name}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Company:", value=company_name, inline=True)
        embed.add_field(name="Role:", value=role, inline=True)
        embed.add_field(name="Timeline:", value=processed_timeline, inline=False)

        await channel.send(embed=embed)

        await interaction.followup.send(
            "Your process timeline was submitted!",
            ephemeral=True
        )
        
async def process(ctx: discord.Interaction):
    verified_rid = bot_context.verified_role_id
    if (role := ctx.guild.get_role(verified_rid)) and role in ctx.user.roles:
        sys_msg = (
            f"{ctx.user.display_name} has tried to add a process timeline for a company."
        )
        await ctx.response.send_modal(
            ProcessModal(
                bot_context,
                is_authorized=True,
                username=ctx.user.display_name,
                bot=ctx.client,
            )
        )
        await bot_context.log(ctx, sys_msg)
    else:
        usr_msg = f"You are not verified. Please use /verify to be able to add a process timeline."
        sys_msg = f"ERROR: {ctx.user.display_name} not verified and tried to add a process timeline."

        await ctx.response.send_message(usr_msg, ephemeral=True)
        await bot_context.log(ctx, sys_msg)

def setup(client, context):
    global bot_context
    bot_context = context

    client.tree.command(name="say_hi")(say_hi)
    client.tree.command(name="xyz")(google_xyz)
    client.tree.command(name="jakes")(jakes_resume)
    client.tree.command(name="reverse_order")(reverse_chronological)
    client.tree.command(name="bold")(bold_key_parts)
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
    client.tree.command(name="cohort")(cohort)
    client.tree.command(name="verify_school_email")(request_verify_school_email)
    client.tree.command(name="process")(process)
