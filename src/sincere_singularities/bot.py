import asyncio

from disnake import ApplicationCommandInteraction, Intents, TextChannel
from disnake.ext import commands

from sincere_singularities.modules.conditions import ConditionManager
from sincere_singularities.modules.order_queue import OrderQueue
from sincere_singularities.modules.restaurants_view import Restaurants

intents = Intents.default()
bot = commands.InteractionBot(intents=intents)
background_tasks = set()

    # Check user permissions
    # We know this is a Member because interaction.channel is a guild text channel
    permissions = interaction.channel.permissions_for(cast(Member, interaction.author))
    if not permissions.manage_webhooks:
        await interaction.response.send_message("You don't have the permissions to manage webhooks!", ephemeral=True)
        return

    await interaction.response.send_message("Webhooks cleared!", ephemeral=True)

    webhooks = await interaction.channel.webhooks()
    for webhook in webhooks:
        await webhook.delete()


@bot.slash_command(name="clear_threads", description="Clears the threads in a channel.")
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

    await interaction.response.send_message("Threads cleared!", ephemeral=True)

    for thread in interaction.channel.threads:
        await thread.delete()


@bot.slash_command(name="start_game", description="Starts the game.")
async def start_game(interaction: ApplicationCommandInteraction) -> None:
    """
    Start the game.

@bot.slash_command(name="start_game")
async def start_game(inter: ApplicationCommandInteraction) -> None:
    """Main Command of our Game: /start_game"""
    # Check if the Message was sent in a Text Channel
    if not isinstance(inter.channel, TextChannel):
        await inter.response.send_message(
            "You can only start a Game Session inside of a Text Channel!", ephemeral=True
        )
        return

    # Start order queue
    order_queue = await OrderQueue.new(interaction)
    if not order_queue:
        # Return if we can't start the game (the user is already warned)
        return
    # Load Restaurants
    restaurants = Restaurants(inter, order_queue)

    # Sending Start Menu Embed
    await inter.response.send_message(embed=restaurants.embeds[0], view=restaurants.view, ephemeral=True)

    # Spawning Orders
    await order_queue.spawn_orders()

    # Load ConditionManager (Orders need to be initialized)
    condition_manager = ConditionManager(order_queue, restaurants)
    restaurants.condition_manager = condition_manager
    # Spawning Conditions
    task = asyncio.create_task(condition_manager.spawn_conditions())
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

    # Creating Temporary example order
    from sincere_singularities.modules.order import CustomerInfo, Order

    customer_info = CustomerInfo(
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
    example_order.foods["Starters"].append("Pizza Starter0")
    example_order.foods["Starters"].append("Pizza Starter0")
    example_order.foods["Main Courses"].append("Main Course0")

    # Spawning conditions
    task = asyncio.create_task(condition_manager.spawn_conditions())
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)


@bot.event
async def on_ready() -> None:
    """Bot information logging when starting up."""
    print(
        f"Logged in as {bot.user} (ID: {bot.user.id}).\n"
        f"Running on {len(bot.guilds)} servers with {bot.latency * 1000:,.2f} ms latency.",
    )
