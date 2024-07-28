import asyncio
from typing import cast

from disnake import ApplicationCommandInteraction, Intents, Member, TextChannel
from disnake.ext import commands

from sincere_singularities.modules.conditions import ConditionManager
from sincere_singularities.modules.order_queue import OrderQueue
from sincere_singularities.modules.restaurants_view import Restaurants

# Load Disnake Related Objects
intents = Intents.default()
bot = commands.InteractionBot(intents=intents)
# This global set is used to ensure that a (non-weak) reference is kept to background tasks created that aren't
# awaited. These tasks get added to this set, then once they're done, they remove themselves.
# See RUF006
background_tasks: set[asyncio.Task[None]] = set()


@bot.slash_command(name="clear_webhooks", description="Clears the webhooks in a channel.")
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

    Args:
        interaction (ApplicationCommandInteraction): The Disnake application command interaction.
    """
    # Check if the message was sent in a text channel
    if not isinstance(interaction.channel, TextChannel):
        await interaction.response.send_message(
            "You can only start a game session inside of a text channel!",
            ephemeral=True,
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
    condition_manager.restaurants = restaurants

    # Sending start menu
    await interaction.response.send_message(embed=restaurants.embeds[0], view=restaurants.view, ephemeral=True)

    # Spawning orders
    task = asyncio.create_task(order_queue.start_orders())
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

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
