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



## Getting Started
See [Installation](https://github.com/SincereSingularities/SincereSingularities?tab=readme-ov-file#installation) and [Running](#running) for detailed instructions.

1. Python 3.11 is [recommended](https://github.com/DisnakeDev/disnake/pull/1135#issuecomment-1847303628). Python 3.10 - 3.12 will probably work.
2. Setup a [Discord Bot](https://docs.disnake.dev/en/stable/discord.html). See [Discord Bot Installation Guide](#discord-bot-installation-guide).
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
[Video Presentation / Description](https://streamable.com/3rcyc0)


## Installation
<details>
    <summary>Detailed Installation Guide ⚙️</summary>

### 1. Requirements:
   1. [Python 3.11](https://www.python.org/downloads/release/python-3110/)
   2. [MongoDB Community Edition](https://www.mongodb.com/docs/manual/administration/install-community/). See [MongoDB Installation Guide](#mongodb-community-edition-installation-guide)
   3. [Discord Bot](https://docs.disnake.dev/en/stable/discord.html). See [Discord Bot SetUp Guide](#discord-bot-installation-guide)
### 2. Download:
Run this command in the directory you want to download it to.
   ```shell
   git clone https://github.com/SincereSingularities/SincereSingularities/
   cd SincereSingularities
   ```
### 3. Install the Game as a package via pip:
   ```shell
   pip install -e .
   ```
### 4. Setup local environment values:
Create and Edit an .env file (see .env.example)
```
BOT_TOKEN (Your Discord Bot Token)
DB_HOST (The IP address of your MongoDB Server)
DB_PORT (The port of your MongoDB Server)
DB_NAME (Your preferred name for the MongoDB Database, defaults to `bot_db`)
```

</details>

## Running
<details>
    <summary>Detailed Running Guide ⚙️</summary>

### 1. Start your [MongoDB Server](https://www.mongodb.com/docs/manual/administration/install-community/). See [MongoDB Installation Guide](#mongodb-community-edition-installation-guide)
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
6. Submit the order. You will get points based on the accuracy of the order. With your earned coins you can buy new restaurants.
7. From time to time, you will get Order Conditions. Pay attention to these Conditions when fulfilling a order. They will also disappear after some time.
</details>

## Helper Commands
<details>
    <summary>Helper Commands 🔨</summary>

- /clear_threads
</br>
  ``Clears the Threads in the Text Channel the Command was executed in. Requires the Author to have manage_threads permissions.``
- /clear_webhooks
</br>
  ``Clears the Webhooks in the Text Channel the Command was executed in. Requires the Author to have manage_webhooks permissions.``
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

## Preview Images
<details>
    <summary>Preview Images 📸</summary>

#### Main Menu:
<img src="https://github.com/user-attachments/assets/fbb6ae72-de95-45db-9cc3-a1c8c720d809" width="300">

#### Restaurant Menu:
<img src="https://github.com/user-attachments/assets/292bf979-7644-4385-a47e-f244ff04016e" width="300">

#### Easy Order (Pizzaria):
<img src="https://i.ibb.co/bvCNF5x/IMG-5599.jpg" width="300">

#### Medium Order (Fast Food):
<img src="https://i.ibb.co/ZY1xh8L/IMG-5600.jpg" width="300">

#### Hard Order (Sushi):
<img src="https://i.ibb.co/khxGccr/IMG-5601.jpg" width="300">
</details>

# Credits
This project was created by (in order of contributed LOC):

| [Vinyzu](https://github.com/Vinyzu)                                                                           | [koviubi1](https://github.com/koviubi56)                                                                                | [WassCodeur](https://github.com/WassCodeur)                                                                                   | [clucker_m8](https://github.com/clucker-m8)                                                                                   | [FoxFil](https://github.com/foxfil)                                                                           |
|---------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|
| [<img src="https://github.com/vinyzu.png" alt="vinyzu" title="Vinyzu" width="66">](https://github.com/vinyzu) | [<img src="https://github.com/koviubi56.png" alt="koviubi1" title="koviubi1" width="66">](https://github.com/koviubi56) | [<img src="https://github.com/WassCodeur.png" alt="WassCodeur" title="WassCodeur" width="66">](https://github.com/WassCodeur) | [<img src="https://github.com/clucker-m8.png" alt="clucker_m8" title="clucker_m8" width="66">](https://github.com/clucker-m8) | [<img src="https://github.com/foxfil.png" alt="FoxFil" title="FoxFil" width="66">](https://github.com/foxfil) |
| Game                                                                                                          | Game                                                                                                                    | Database                                                                                                                      | Order Generation                                                                                                              | Restaurant Menus                                                                                              |
