import disnake
from disnake.ext import commands

intents = disnake.Intents.default()
bot = commands.InteractionBot(intents=intents)


@bot.event
async def on_ready() -> None:
    """Bot information logging when starting up."""
    print(
        f"Logged in as {bot.user} (ID: {bot.user.id}).\n"
        f"Running on {len(bot.guilds)} servers with {bot.latency*1000:,.2f} ms latency.",
    )