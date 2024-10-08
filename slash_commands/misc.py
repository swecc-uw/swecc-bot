import discord
from APIs.UselessAPIs import UselessAPIs
from APIs.CalendarAPI import CalendarAPI

useless = UselessAPIs()
calendar = CalendarAPI()

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

async def next_meeting(ctx: discord.Interaction):
    meeting_info = await calendar.get_next_meeting()
    caldendar_url = "https://calendar.google.com/calendar/u/0?cid=Y19kYmU2YWQ2ODliNTE2MjMzMjMyZjcwNDk4NDA1OWIwOTVhNWE5YmVhZmIyZGVmZTBiZjQ4YmFhZWJiMTA4ZThhQGdyb3VwLmNhbGVuZGFyLmdvb2dsZS5jb20"
    calendar_hyperlink = f"[SWECC Public Calendar]({caldendar_url})"
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