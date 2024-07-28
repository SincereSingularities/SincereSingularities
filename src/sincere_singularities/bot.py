import asyncio
from typing import cast

import disnake
from disnake import ApplicationCommandInteraction, Embed, Intents, Member, MessageInteraction, TextChannel
from disnake.ext import commands

from sincere_singularities import save_states
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


class IntroductionView(disnake.ui.View):
    """View for the introduction to the game."""

    @disnake.ui.button(style=disnake.ButtonStyle.success, label="Start!")
    async def _start(self, _: disnake.ui.Button, interaction: MessageInteraction) -> None:
        await start_the_game(interaction)


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

    try:
        save_states.load_game_state(interaction.user.id)
    except ValueError:
        embed = Embed(
            title="Introduction",
            description="Welcome to Restaurant Rush: Kitchen Chaos! In this game, you manage orders from customers for"
            " multiple restaurants, but make sure you don't get overwhelmed by the information overload.",
        )
        embed.add_field(
            name="Starting the game",
            description="Once you start the game, the orders will be sent as messages in a thread which will be"
            " created in this channel. The bot will also send the game menu where you can enter restaurants and"
            " add orders. You can buy restaurants with coins, but you already own the first one.",
            inline=False,
        )
        embed.add_field(
            name="Adding an order",
            description="When you get a new order, select the appropriate restaurant from the menu and enter it."
            " Press the buttons to add the menu items that the user requested. Then, input the customer"
            " information and click done. You will receive coins based on how correct you were.",
            inline=False,
        )
        embed.add_field(
            name="The information overload",
            description="The more you play the game, the more difficult it gets. Be quick because being slow will"
            " result in penalties!",
            inline=False,
        )
        embed.add_field(
            name="Buying restaurants",
            description="Once you gain enough coins, you can buy other restaurants.",
            inline=False,
        )
        interaction.response.send_message(embed=embed, view=IntroductionView())
    else:
        await start_the_game(interaction)


async def start_the_game(interaction: ApplicationCommandInteraction | MessageInteraction) -> None:
    """
    Actually start the game.

    Args:
        interaction (ApplicationCommandInteraction | MessageInteraction): The interaction that led to the start of
            the game.
    """
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
