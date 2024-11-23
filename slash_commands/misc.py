import discord
from APIs.UselessAPIs import UselessAPIs
from APIs.CalendarAPI import CalendarAPI
from APIs.AdventOfCodeAPI import AdventOfCodeAPI
import os
from dotenv import load_dotenv

useless = UselessAPIs()
calendar = CalendarAPI()
aoc_api = AdventOfCodeAPI()

LEADERBOARD_KEY = os.getenv('AOC_LEADERBOARD_KEY')

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
    await ctx.response.send_message("Here is a comprehensive resume wiki: https://www.reddit.com/r/EngineeringResumes/wiki/index/")

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
        title=f"🎄 Current Leaderboard 🎄",
        description=f"",
        color=0x1f8b4c 
    )        

    if leaderboard_data:
        leaderboard_text = "\n".join(
            f"**#{index + 1}: {member['name']}** - {member['local_score']} points"
            for index, member in enumerate(leaderboard_data[:10])
        )
        embed.add_field(
            name="🎖️ Leaderboard (Top 10)",
            value=(f"{leaderboard_text}\n\n"
                f"[View full leaderboard]({aoc_api.get_leaderboard_url()})\n\n"
                f"Use key `{LEADERBOARD_KEY}` to join the leaderboard!"
            ),
            inline=False
        )

    embed.set_footer(text="Happy coding and good luck!")
    embed.set_thumbnail(url="https://adventofcode.com/favicon.png")
    await ctx.response.send_message(embed=embed, ephemeral=bot_context.ephemeral)


async def next_meeting(ctx: discord.Interaction):
    meeting_info = await calendar.get_next_meeting()
    calendar_hyperlink = f"[SWECC Public Calendar]({calendar.get_url()})"
    if meeting_info:
        embed = discord.Embed(
            title=f"📅 Next Meeting: {meeting_info['name']}",
            description=f"**Description:** {meeting_info['description'] or 'No description available.'}\n\n",
            color=discord.Color.blue()
        )

        embed.add_field(name="🕒 Date & Time", value=meeting_info['date'], inline=False)
        embed.add_field(name="📍 Location", value=meeting_info['location'] or "Not specified", inline=False)
        embed.add_field(name="🔗 Calendar Link", value=calendar_hyperlink, inline=False)
        
        await ctx.response.send_message(embed=embed)
    else:
        await ctx.response.send_message("No upcoming meetings found.")

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