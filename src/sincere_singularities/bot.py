from disnake import ApplicationCommandInteraction, Intents, TextChannel
from disnake.ext import commands

from sincere_singularities.modules.order_queue import OrderQueue
from sincere_singularities.modules.restaurants_view import Restaurants

intents = Intents.default()
bot = commands.InteractionBot(intents=intents)


@bot.slash_command(name="start_game")
async def start_game(inter: ApplicationCommandInteraction) -> None:
    """Main Command of our Game: /start_game"""
    # Check if the Message was sent in a Text Channel
    if not isinstance(inter.channel, TextChannel):
        await inter.response.send_message(
            "You can only start a Game Session inside of a Text Channel!", ephemeral=True
        )

    # Start Order Queue
    order_queue = OrderQueue(inter)
    # Load Restaurants
    restaurants = Restaurants(inter, order_queue)
    await inter.response.send_message(embed=restaurants.embeds[0], view=restaurants.view, ephemeral=True)
    await order_queue.start_orders()

    # Creating Temporary example order
    from sincere_singularities.modules.order import CustomerInfo, Order

    customer_info = CustomerInfo(
        order_id="Test123",
        name="Customer Name",
        address="Customer Address",
        delivery_time="9 o'clock.",
        extra_information="Dont ring the bell.",
    )
    example_order_text = str(
        "OrderID: Test123 \n"
        "Hello, my name is Customer Name. I would like to have 2 Pizza Starter0 and a "
        "Main Course0 delivered to my house Customer Address at 9 o'clock. "
        "Please dont ring the bell."
    )
    example_order = Order(customer_information=customer_info, restaurant_name="Pizzaria")
    example_order.foods["Starters"].append("Pizza Starter0")
    example_order.foods["Starters"].append("Pizza Starter0")
    example_order.foods["Main Courses"].append("Main Course0")

    await order_queue.create_order("Customer Name", example_order_text, example_order)


@bot.event
async def on_ready() -> None:
    """Bot information logging when starting up."""
    print(
        f"Logged in as {bot.user} (ID: {bot.user.id}).\n"
        f"Running on {len(bot.guilds)} servers with {bot.latency * 1000:,.2f} ms latency.",
    )
