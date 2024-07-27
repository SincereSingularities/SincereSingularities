import asyncio
from typing import cast

from disnake import ApplicationCommandInteraction, Intents, Member, TextChannel
from disnake.ext import commands

from sincere_singularities.modules.conditions import ConditionManager
from sincere_singularities.modules.order_queue import OrderQueue
from sincere_singularities.modules.restaurants_view import Restaurants

intents = Intents.default()
bot = commands.InteractionBot(intents=intents)
# This global set is used to ensure that a (non-weak) reference is kept to background tasks created that aren't
# awaited. These tasks get added to this set, then once they're done, they remove themselves.
# See RUF006
background_tasks: set[asyncio.Task[None]] = set()


@bot.slash_command(name="clear_webhooks")
async def clear_webhooks(interaction: ApplicationCommandInteraction) -> None:
    """
    Clears the webhooks in a channel.

    Args:
        interaction (ApplicationCommandInteraction): The Disnake application command interaction.
    """
    # Check if the message was sent in a text channel
    if not isinstance(interaction.channel, TextChannel):
        await interaction.response.send_message(
            "I'm only able to clear webhooks inside of a text channel!", ephemeral=True
        )
        return

    # Check user permissions
    # We know this is a Member because interaction.channel is a guild text channel
    permissions = interaction.channel.permissions_for(cast(Member, interaction.author))
    if not permissions.manage_webhooks:
        await interaction.response.send_message("You don't have the permissions to manage webhooks!", ephemeral=True)
        return

    webhooks = await interaction.channel.webhooks()
    for webhook in webhooks:
        await webhook.delete()

    await interaction.response.send_message("Webhooks cleared!", ephemeral=True)


@bot.slash_command(name="clear_threads")
async def clear_threads(interaction: ApplicationCommandInteraction) -> None:
    """
    Clears the threads in a channel.

    Args:
        interaction (ApplicationCommandInteraction): The Disnake application command interaction.
    """
    # Check if the message was sent in a text channel
    if not isinstance(interaction.channel, TextChannel):
        await interaction.response.send_message(
            "I'm only able to clear threads inside of a text channel!", ephemeral=True
        )
        return

    # Check user permissions
    # We know this is a Member because interaction.channel is a guild text channel
    permissions = interaction.channel.permissions_for(cast(Member, interaction.author))
    if not permissions.manage_threads:
        await interaction.response.send_message("You don't have the permissions to manage threads!", ephemeral=True)
        return

    for thread in interaction.channel.threads:
        await thread.delete()

    await interaction.response.send_message("Threads cleared!", ephemeral=True)


@bot.slash_command(name="start_game")
async def start_game(interaction: ApplicationCommandInteraction) -> None:
    """
    Start the game.

    Args:
        interaction (ApplicationCommandInteraction): The Disnake application command interaction.
    """
    # Check if the message was sent in a text channel
    if not isinstance(interaction.channel, TextChannel):
        await interaction.response.send_message(
            "You can only start a game session inside of a text channel!", ephemeral=True
        )
        return

    # Start order queue
    order_queue = await OrderQueue.new(interaction)
    if not order_queue:
        # Return if we can't start the game (the user is already warned)
        return
    # Load Restaurants
    condition_manager = ConditionManager(order_queue)
    restaurants = Restaurants(interaction, order_queue, condition_manager)

    # Sending start menu
    await interaction.response.send_message(embed=restaurants.embeds[0], view=restaurants.view, ephemeral=True)

    # Spawning orders
    await order_queue.start_orders()

    # Spawning conditions
    task = asyncio.create_task(condition_manager.spawn_conditions())
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

    # Creating temporary example order
    from sincere_singularities.modules.order import CustomerInformation, Order

    customer_info = CustomerInformation(
        order_id="Test123",
        name="Customer Name",
        address="Customer Address",
        delivery_time="9 o'clock.",
        extra_information="Dont ring the bell.",
    )
    example_order_text = str(
        "OrderID: Test123 \n"
        "Hello, my name is Customer Name. I would like to have 2 Pizza Starter0 and a "
        "Main Course0 delivered to my house Customer Address at 9 o'clock. "
        "Please dont ring the bell."
    )
    example_order = Order(customer_information=customer_info, restaurant_name="Pizzaria")
    example_order.foods["Starters"].append("Garlic Knots")
    example_order.foods["Starters"].append("Garlic Knots")
    example_order.foods["Main Courses"].append("Veggie Pizza")

    await order_queue.create_order(example_order_text, example_order)


@bot.event
async def on_ready() -> None:
    """Bot information logging when starting up."""
    print(
        f"Logged in as {bot.user} (ID: {bot.user.id}).\n"
        f"Running on {len(bot.guilds)} servers with {bot.latency * 1000:,.2f} ms latency.",
    )
