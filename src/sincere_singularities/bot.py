import disnake
from disnake.ext import commands

from sincere_singularities.restaurants_view import Restaurants

intents = disnake.Intents.default()
bot = commands.InteractionBot(intents=intents)


@bot.slash_command(name="start_game")
async def start_game(inter: disnake.ApplicationCommandInteraction):
    # Load Restaurants
    restaurants = Restaurants(inter)
    await inter.response.send_message(embed=restaurants.embeds[0], view=restaurants.view, ephemeral=True)


@bot.event
async def on_ready() -> None:
    """Bot information logging when starting up."""
    print(
        f"Logged in as {bot.user} (ID: {bot.user.id}).\n"
        f"Running on {len(bot.guilds)} servers with {bot.latency*1000:,.2f} ms latency.",
    )
