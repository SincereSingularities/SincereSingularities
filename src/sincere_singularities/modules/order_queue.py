import asyncio
import random
from collections import defaultdict
from contextlib import suppress
from typing import Self

from disnake import (
    ApplicationCommandInteraction,
    ChannelType,
    HTTPException,
    NotFound,
    TextChannel,
    Thread,
    Webhook,
    WebhookMessage,
)
from disnake.ext.commands.errors import CommandInvokeError

from sincere_singularities import save_states
from sincere_singularities.data.savestates import generate_default_state
from sincere_singularities.modules.coins import has_restaurant
from sincere_singularities.modules.order import Order
from sincere_singularities.modules.order_generator import Difficulty, OrderGenerator
from sincere_singularities.utils import (
    RESTAURANT_JSON,
    RestaurantsType,
    generate_random_avatar_url,
)


def get_number_of_orders(user_id: int, restaurant: str) -> int:
    """
    Get the number of orders by a user.

    Args:
        user_id (int): The user's ID.
        restaurant (str): The restaurant's name.

    Returns:
        int: The number of orders completed.
    """
    try:
        return save_states.load_game_state(user_id)["number_of_orders"][restaurant]
    except (ValueError, KeyError):
        return 0


def add_number_of_orders(user_id: int, restaurant: str) -> None:
    """
    Add to the number of orders.

    Args:
        user_id (int): The user's ID.
        restaurant (str): The restaurant's name.
    """
    try:
        state = save_states.load_game_state(user_id)
    except ValueError:
        state = generate_default_state()

    state["number_of_orders"].setdefault(restaurant, 0)
    state["number_of_orders"][restaurant] += 1
    save_states.save_game_state(user_id, state)


class OrderQueue:
    """The class for managing the order queue. Orders can be spawned and deleted from here."""

    def __init__(self, interaction: ApplicationCommandInteraction, webhook: Webhook) -> None:
        """
        Initialize the order queue.

        Args:
            interaction (ApplicationCommandInteraction): The application command interaction.
            webhook (Webhook): The webhook.
        """
        self.interaction = interaction
        self.user = interaction.user
        self.orders: dict[str, tuple[Order, WebhookMessage]] = {}
        self.running = False
        self.webhook = webhook
        self.order_generators: defaultdict[str, OrderGenerator] = defaultdict(lambda: OrderGenerator(Difficulty.EASY))
        self.orders_thread: Thread | None = None

    @classmethod
    async def new(cls, interaction: ApplicationCommandInteraction) -> Self | None:
        """
        Create a new order queue.

        Args:
            interaction (ApplicationCommandInteraction): The application command interaction.

        Returns:
            Self | None: The new order queue, or None if a webhook couldn't be created.
        """
        if not isinstance(interaction.channel, TextChannel):
            raise TypeError("interaction.channel should be TextChannel")
        try:
            webhook = await interaction.channel.create_webhook(name="Restaurant Rush: Kitchen Chaos - Order Webhook")
        except CommandInvokeError:
            await interaction.channel.send(
                "Can't start Restaurant Rush: Kitchen Chaos: maximum amount of webhooks reached. "
                "Delete webhooks or try in another channel!"
            )
            return None

        return cls(
            interaction=interaction,
            webhook=webhook,
        )

    async def start_orders(self) -> None:
        """Start the orders queue. Spawns three orders."""
        self.running = True

        # Creating Orders Thread after initial Message was sent for proper message order.
        self.orders_thread = await self.interaction.channel.create_thread(
            name="Orders Thread", type=ChannelType.public_thread, invitable=False
        )
        assert self.orders_thread  # MYPY can be stupid at times...
        await self.orders_thread.add_user(self.interaction.user)

        # Spawn 3 Orders at the start, which get refreshed after one order is done
        for i in range(3):
            # Waiting after first order is sent for more realistic order messages
            if i:
                await asyncio.sleep(random.randint(5, 15))
            await self.spawn_order()

    async def spawn_order(self) -> None:
        """Spawning a new randomly generated order."""
        if not self.running:
            return

        # Filtering out the Restaurants the user has
        restaurants: RestaurantsType = [
            restaurant for restaurant in RESTAURANT_JSON if has_restaurant(self.user.id, restaurant.name)
        ]

        # Calculate the Order Amounts to relative values
        order_amounts_sum: int = sum(restaurant.order_amount for restaurant in restaurants)
        relative_order_amounts: list[float] = [
            restaurant.order_amount / order_amounts_sum for restaurant in restaurants
        ]

        # Getting a random restaurant weighed by their relative order amounts
        random_restaurant = random.choices(population=restaurants, weights=relative_order_amounts)[0].name
        order, order_description = self.order_generators[random_restaurant].generate(random_restaurant)
        await self.create_order(order, order_description)

    async def create_order(self, order_result: Order, order_message: str) -> None:
        """
        Create a new order, sends a message, and stores the result to check.

        Args:
            order_message (str): The message to send to the Discord thread.
            order_result (Order): The correct result the Order should give
        """
        if not order_result.customer_information:
            raise ValueError("missing customer_information")

        dc_tz = f"<t:{int(order_result.penalty_timestamp.timestamp())}:R>"
        order_message += (
            f"\n\n:warning: The order should be completed within {dc_tz} seconds or you will get a penalty! :warning:"
        )
        discord_message = await self.webhook.send(
            content=order_message,
            username=f"Restaurant Rush: Kitchen Chaos - OrderID: {order_result.customer_information.order_id}",
            avatar_url=generate_random_avatar_url(),
            wait=True,
            thread=self.orders_thread,
        )
        self.orders[order_result.customer_information.order_id] = (order_result, discord_message)

    def get_order_by_id(self, order_id: str) -> Order | None:
        """
        Get a specific order by its ID.

        Args:
            order_id (str): The ID of the order to retrieve.

        Returns:
            Order | None: The order with that ID or None.
        """
        if order := self.orders.get(order_id):
            return order[0]
        return None

    async def discard_order(self, order_id: str) -> None:
        """
        Discard a specific order by its ID after it's completed.

        Args:
            order_id (str): The ID of the order to discard.
        """
        order = self.orders[order_id][0]

        # Increase difficulty every 10 completed orders
        assert order.restaurant_name
        add_number_of_orders(self.user.id, order.restaurant_name)
        orders = get_number_of_orders(self.user.id, order.restaurant_name)
        if orders == 10:
            self.order_generators[order.restaurant_name].difficulty = Difficulty.MEDIUM
        elif orders == 20:
            self.order_generators[order.restaurant_name].difficulty = Difficulty.HARD

        del self.orders[order_id]

        # Wait 10-20 Seconds as an order cooldown
        await asyncio.sleep(random.randint(10, 20))
        await self.spawn_order()

    async def stop_orders(self) -> None:
        """Stop all orders (when stopping the game)."""
        self.running = False
        with suppress(HTTPException, NotFound):
            # Deleting webhook
            await self.webhook.delete()
        with suppress(HTTPException, NotFound, AssertionError):
            # Deleting orders thread
            assert self.orders_thread
            await self.orders_thread.delete()
