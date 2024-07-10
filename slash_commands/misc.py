import discord
from APIs.UselessAPIs import UselessAPIs

useless = UselessAPIs()

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

def setup(client, context):
    global bot_context
    bot_context = context
    client.tree.command(name="xyz")(google_xyz)
    client.tree.command(name="resume_guide")(full_resume_guide)
    client.tree.command(name="useless_fact")(useless_facts)
    client.tree.command(name="kanye")(kanye)
    client.tree.command(name="cat_fact")(cat_fact)