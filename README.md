# Game Title Here

**Sincere Singularities** Python Discord Summer CodeJam 2024 project.
The technology is **Discord Application**, the theme is **Information Overload**, and our chosen framework
is [Disnake](https://github.com/DisnakeDev/disnake/).

---

Did you ever want to experience the information overload and stress of a phone operator?
Well, then you're at the right place!

We've created a first stressful Discord game, in which you play a phone operator for a restaurant.
No matter what dishes, customers, or special orders you have to serve, don't lose focus, or you might get overwhelmed by
the information overload!

## Running the bot

1. Python 3.11 is [recommended](https://github.com/DisnakeDev/disnake/pull/1135#issuecomment-1847303628).
2. Setup a [Discord Bot](https://docs.disnake.dev/en/stable/discord.html). <!-- TODO: explain better once we have an idea on how the bot works (e.g. what permissions are required) -->
3. clone the repository:
   ```shell
   git clone https://github.com/SincereSingularities/SincereSingularities/
   cd SincereSingularities
   pip install -e .
   ```
4. Set the `BOT_TOKEN` environment variable to your Token using the `.env` file.
5. Run The Game:
   ```shell
   python -m sincere_singularities
   ```
6. Play!

## Gameplay

1. Choose a text channel.
2. Run the `/start_game` command. That will create a thread.
3. The bot will send the menu. This contains multiple restaurants that you can buy. You already own the first one.
4. You will get orders in the thread as messages. Choose and enter the appropriate restaurant, and select the menu items that the customer requested.
5. Then enter the customer's information. 
