import asyncio
import random
from contextlib import suppress

from disnake import (
    ApplicationCommandInteraction,
    ChannelType,
    HTTPException,
    NotFound,
    Thread,
    Webhook,
    WebhookMessage,
)
from disnake.ext.commands.errors import CommandInvokeError

from sincere_singularities.modules.order import Order
from sincere_singularities.modules.points import has_restaurant
from sincere_singularities.utils import RestaurantJson, RestaurantJsonType, generate_random_avatar_url, load_json

# Temporary
ORDER_TEMPLATES = [
    (
        "Hello, I'd like to place an order for delivery. My name is {CUSTOMER_NAME}, and I live at {CUSTOMER_ADDRESS}."
        " I'd like to order {ORDER_ITEMS}. Oh, and by the way, I have a cat named Fluffy and I don't like it when"
        "people ring the doorbell, so please make sure to just knock politely. Please deliver it at {DELIVERY_TIME}. "
        "Thank you.",
        "Don't ring the bell",
    )
]


class OrderQueue:
    """The Class for managing the order queue. Orders can be spawned and deleted from here."""

    webhook: Webhook
    orders_thread: Thread

    def __init__(self, inter: ApplicationCommandInteraction) -> None:
        self.user = inter.user
        self.channel = inter.channel
        self.orders: dict[str, tuple[Order, WebhookMessage]] = {}
        self.running = False
        self.restaurant_json = load_json("restaurants.json", RestaurantJsonType)

    async def init_orders(self) -> None:
        """Start the orders queue. Spawn a new Webhook and Order Thread"""
        # Creating the Order Webhook
        try:
            self.webhook = await self.channel.create_webhook(name="GAME NAME Order Webhook")
        except CommandInvokeError:
            await self.channel.send(
                "Can't start GAME NAME: Maximum Amount of Webhooks reached. Delete Webhooks or try in another channel!"
            )
            await self.stop_orders()

        # Creating the Orders Thread
        self.orders_thread = await self.channel.create_thread(
            name="Orders Thread", type=ChannelType.public_thread, invitable=False
        )
        await self.orders_thread.add_user(self.user)
        self.running = True

        # Spawn 3 Orders at the start, which get refreshed after one order is done
        for _ in range(3):
            await self.spawn_order()

    async def spawn_order(self) -> None:
        """Spawning a new randomly genrated Order"""
        if not self.running:
            return

        # Filtering out the Restaurants the user has
        restaurants: list[RestaurantJson] = [
            restaurant for restaurant in self.restaurant_json if has_restaurant(self.user.id, restaurant.name)
        ]

        # Calculate the Order Amounts to relative values
        order_amounts_sum: int = sum(restaurant.order_amount for restaurant in restaurants)
        relative_order_amounts: list[float] = [
            restaurant.order_amount / order_amounts_sum for restaurant in restaurants
        ]

        # Getting a random restaurant wheighed by their relative order amounts
        random_restaurant = random.choices(population=restaurants, weights=relative_order_amounts)[0]
        print(random_restaurant)
        # TODO: Implement Cluckers Algo

    async def create_order(self, customer_name: str, order_message: str, order_result: Order) -> None:
        """
        Create a new Order, sends a message to the Discord and stores the result to check.

        Args:
            customer_name: The full name of the customer.
            order_message: The message to send to the Discord channel.
            order_result: The correct result the Order should give
        """
        discord_tz = f"<t:{order_result.penalty_timestamp.timestamp()}:R>"
        order_message += f" The order should be completed within {discord_tz} seconds or you will get a penalty!"
        order_message = await self.webhook.send(
            content=order_message,
            username=customer_name,
            avatar_url=generate_random_avatar_url(),
            wait=True,
            thread=self.orders_thread,
        )

        assert order_result.customer_information
        self.orders[order_result.customer_information.order_id] = (order_result, order_message)

    def get_order_by_id(self, order_id: str) -> Order | None:
        """
        Get a specific Order by ID.

        Args:
            order_id: The ID of the Order to retrieve.

        Returns:
            The Correct Order, the WebhookMessage (to delete after the order is done)
        """
        if order := self.orders.get(order_id):
            return order[0]
        return None

    async def discard_order(self, order_id: str) -> None:
        """
        Discard a specific Order by ID after its completed.

        Args:
            order_id: ID of the Order to discard.
        """
        with suppress(KeyError):
            del self.orders[order_id]

        # Wait 10-20 Seconds as an order Cooldown
        order_timeout = random.randint(10, 20)
        await asyncio.sleep(order_timeout)
        await self.spawn_order()

    async def stop_orders(self) -> None:
        """Stop All Orders (when stopping the game)."""
        self.running = False
        with suppress(HTTPException, NotFound):
            # Deleting Webhook
            await self.webhook.delete()
        with suppress(HTTPException, NotFound):
            # Deleting Orders Thread
            await self.orders_thread.delete()
