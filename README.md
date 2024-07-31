# Restaurant Rush: Kitchen Chaos

**Sincere Singularities** Python Discord Summer CodeJam 2024 project.
The technology is **Discord Application**, the theme is **Information Overload**, and our chosen framework
is [Disnake](https://github.com/DisnakeDev/disnake/).

---

Did you ever want to experience the information overload and stress of a phone operator?
Well, then you're at the right place!

We've created the first stressful Discord game, in which you play a phone operator for multiple restaurants.
No matter what dishes, customers, or special orders you have to serve, don't lose focus, or you might get overwhelmed by
the information overload!

## Table of contents
1. [Getting Started](https://github.com/SincereSingularities/SincereSingularities?tab=readme-ov-file#getting-started)
2. [Video Presentation](https://github.com/SincereSingularities/SincereSingularities?tab=readme-ov-file#video-presentation)
3. [Installation](https://github.com/SincereSingularities/SincereSingularities?tab=readme-ov-file#installation)
4. [Running](https://github.com/SincereSingularities/SincereSingularities?tab=readme-ov-file#running)
5. [Gameplay Tutorial](https://github.com/SincereSingularities/SincereSingularities?tab=readme-ov-file#gameplay)
6. [Discord Bot Installation Guide](https://github.com/SincereSingularities/SincereSingularities?tab=readme-ov-file#discord-bot-installation-guide)
7. [MongoDB Community Edition Installation Guide](https://github.com/SincereSingularities/SincereSingularities?tab=readme-ov-file#mongodb-community-edition-installation-guide)
8. [Credits](https://github.com/SincereSingularities/SincereSingularities?tab=readme-ov-file#credits)



## Getting Started

1. Python 3.11 is [recommended](https://github.com/DisnakeDev/disnake/pull/1135#issuecomment-1847303628). Python 3.10 - 3.12 will probably work.
2. Setup a [Discord Bot](https://docs.disnake.dev/en/stable/discord.html). <!-- TODO: explain better once we have an idea on how the bot works (e.g. what permissions are required) -->
3. Clone the repository :
   ```shell
   git clone https://github.com/SincereSingularities/SincereSingularities/
   cd SincereSingularities
   pip install -e .
   ```
4. Setup and run [MongoDB Community Edition](https://www.mongodb.com/docs/manual/administration/install-community/)
5. Set the `BOT_TOKEN`, `DB_HOST`, `DB_PORT` and `DB_NAME` environment variables using the `.env` file.
6. Run The Game:
   ```shell
   python -m sincere_singularities
   ```
7. Play!

## Video Presentation

Disclaimer: `The video contains Spoilers`

<details>
    <summary>Video Presentation / Description</summary>
    https://www.youtube.com/
</details>


## Installation
<details>
    <summary>Detailed Installation Guide ⚙️</summary>

### 1. Requirements:
   1. [Python 3.11](https://www.python.org/downloads/release/python-3110/)
   2. [MongoDB Community Edition](https://www.mongodb.com/docs/manual/administration/install-community/). See [MongoDB Installation Guide]
   3. [Discord Bot](https://docs.disnake.dev/en/stable/discord.html). See [Discord Bot SetUp Guide]
### 2. Download:
Run this command in the directory you want to download it to.
   ```shell
   git clone https://github.com/SincereSingularities/SincereSingularities/
   cd SincereSingularities
   ```
### 3. Install the Game as a PIP package & install requirements:
   ```shell
   pip install -e .
   ```
### 4. Setup local environment values:
Create & Edit an .env file (see .env.example)
```
BOT_TOKEN (Your Discord Bot Token)
DB_HOST (The IP address of your MongoDB Server)
DB_PORT (The port of your MongoDB Server)
DB_NAME (Your preffered name for the MongoDB Database)

```
   
</details>

## Running
<details>
    <summary>Detailed Running Guide ⚙️</summary>

### 1. Start your [MongoDB Server](https://www.mongodb.com/docs/manual/administration/install-community/). See [MongoDB Installation Guide]
### 2. Run the Game:
   ```shell
   python -m sincere_singularities
   ```
### 3. Start a Game Session in a Text Channel:
   ```
   /start_game
   ```
</details>

## Gameplay
<details>
    <summary>Gameplay Explanation 💡</summary>

1. Choose a text channel.
2. Run the `/start_game` command. That will create a thread.
3. The bot will send the menu. This contains multiple restaurants that you can buy. You already own the first one.
4. You will get orders in the thread as messages. Choose and enter the appropriate restaurant, and select the menu items that the customer requested.
5. Then enter the customer's information which consists of:
- Order ID
- Customer Name
- Customer Address
- Delivery Time
- Extra Wishes
6. Enter the ordered items.
7. Submit the order. You will get points based on the accuracy of the order. With your earned coins you can buy new restaurants.
8. From time to time, you will get Order Conditions. Pay attention to these Conditions when fulfilling a order. They will also disappear after some time.
</details>

## Discord Bot Installation Guide
<details>
    <summary>Discord Bot Installation Guide 🤖</summary>

Extended from [Disnake Bot Guide](https://docs.disnake.dev/en/stable/discord.html)
1. Create a new [Discord Application](https://discord.com/developers/applications).
2. Navigate to the Bot Tab. You can customize your bot. Reset the bot token and copy the freshly created one.
3. Navigate to the OAuth2 Tab.
   1. Under `Scopes`, check `bot` and `applications.commands`.
   2. Under `Bot Permissions`, check `Manage Webhooks`, `Send Messages`, `Create Public Threads`, `Send Messages in Threads`, `Manage Messages`, `Manage Threads`,
   3. Copy the `Generated URL`
4. Paste the `Generated URL` in your browser and invite the bot to your server.
</details>

## MongoDB Community Edition Installation Guide
<details>
    <summary>MongoDB Server Installation Guide 💾</summary>

Extended from [MongoDB Community Edition Installer](https://www.mongodb.com/docs/manual/administration/install-community/)
1. Install on Windows
   1. For Installation, follow [Windows Installation Guide](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-windows/#install-mongodb-community-edition)
   2. To Run MongoDB, follow [Windows Running Guide](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-windows/#run-mongodb-community-edition-from-the-command-interpreter)
2. Install on MacOS
   1. For Installation, follow [MacOS Installation Guide](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-os-x/#install-mongodb-community-edition)
   2. To Run MongoDB, follow [MacOS Running Guide](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-os-x/#run-mongodb-community-edition)
3. Install on Ubuntu
   1. For Installation, follow [Ubuntu Installation Guide](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/#install-mongodb-community-edition)
   2. To Run MongoDB, follow [Ubuntu Running Guide](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/#run-mongodb-community-edition)
4. Install on Debian
   1. For Installation, follow [Debian Installation Guide](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-debian/#install-mongodb-community-edition)
   2. To Run MongoDB, follow [Debian Running Guide](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-debian/#run-mongodb-community-edition)
5. Install on SUSE
   1. For Installation, follow [SUSE Installation Guide](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-suse/#install-mongodb-community-edition)
   2. To Run MongoDB, follow [SUSE Running Guide](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-suse/#run-mongodb-community-edition)

</details>

# Credits
This project was created by (in order of contributed LOC):

  | [Vinyzu](https://github.com/Vinyzu) | [koviubi1](https://github.com/koviubi56) | [WassCodeur](https://github.com/WassCodeur) | [clucker_m8](https://github.com/clucker-m8)  | [FoxFil](https://github.com/foxfil) |
  |-------------------------------------|------------------------------------------|---------------------------------------------|----------------------------------------------|-------------------------------------|
  |  Game                               | Game                                     | Database                                    | Order Generation                             | Restaurant Menus                    |
