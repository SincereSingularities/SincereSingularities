import os

import dotenv

from sincere_singularities.bot import bot


def main() -> None:
    """Load .env, and run the bot."""
    dotenv.load_dotenv()
    token = os.getenv("BOT_TOKEN")
    bot.run(token)


if __name__ == "__main__":
    main()
