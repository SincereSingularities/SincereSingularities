from contextlib import suppress
from typing import ClassVar

from disnake import ApplicationCommandInteraction, ChannelType, Thread, Webhook, WebhookMessage
from disnake.ext.commands.errors import CommandInvokeError

from sincere_singularities.modules.order import Order
from sincere_singularities.utils import generate_random_avatar_url


class OrderQueue:
    """The Class for managing the order queue. Orders can be spawned and deleted from here."""

    orders: ClassVar[dict[str, tuple[Order, WebhookMessage]]] = {}
    webhook: Webhook
    orders_thread: Thread

    def __init__(self, inter: ApplicationCommandInteraction) -> None:
        self.user = inter.user
        self.channel = inter.channel

    async def start_orders(self) -> None:
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

    async def create_order(self, customer_name: str, order_message: str, order_result: Order) -> None:
        """
        Create a new Order, sends a message to the Discord and stores the result to check.

        Args:
            customer_name: The full name of the customer.
            order_message: The message to send to the Discord channel.
            order_result: The correct result the Order should give
        """
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
        if self.orders.get(order_id):
            del self.orders[order_id]

    async def stop_orders(self) -> None:
        """Stop All Orders (when stopping the game)."""
        with suppress(Exception):
            # Deleting Webhook
            await self.webhook.delete()
            # Deleting Orders Thread
            await self.orders_thread.delete()
