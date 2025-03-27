import mq


@mq.consumer(
    exchange="message",
    queue="text",
    routing_key="example.text",
    needs_context=True,  # whether the callback needs client/bot_context
)
async def consume_discord_message(body, properties, client, context):
    message = body.decode("utf-8")
    print(f"Received message: {message}")

    if (channel := client.get_channel(context.admin_channel)) is not None:
        await channel.send(f"Received message: {message}")
