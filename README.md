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
    ```
4. Install dependencies with
   ```shell
   pip install -r requirements.txt
   ```

5. Configure  [MongoDB](https://www.prisma.io/dataguide/mongodb/setting-up-a-local-mongodb-database) and launch the server.
6.
   - Create the `.env` file, copy the contents of `.env.example`, paste it into `.env` and update the database variables with the values from your mongodb database in the `.env` file.

   - Set the `BOT_TOKEN` environment variable to your Token using the `.env` file.:
    ```shell
    BOT_TOKEN=your_bot_token

    DB_NAME=your_db_name
    DB_HOST=your_db_host
    DB_PORT=your_db_port
    ```

1. Run The Game:
   ```shell
   python -m sincere_singularities
    ```
2.  Test the bot in your discord server.
