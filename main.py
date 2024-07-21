import os

import disnake
from disnake.ext import commands

TOKEN = os.getenv("BOT_TOKEN")

intents = disnake.Intents.default()
bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)


@bot.event  # type: ignore[misc]
async def on_ready() -> None:
    """
    Bot Information Logging when starting up.

    Returns:
        None
    """
    print(
        f"Logged in as {bot.user} (ID: {bot.user.id}). \n"
        f"Running on {len(bot.guilds)} servers with {bot.latency*1000:,.2f} ms latency.",
    )


if __name__ == "__main__":
    bot.run(TOKEN)
