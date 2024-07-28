import asyncio
import random
from collections import defaultdict
from contextlib import suppress
from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import TYPE_CHECKING

from disnake import WebhookMessage

from sincere_singularities.modules.order import CustomerInformation, Order
from sincere_singularities.modules.order_generator import Difficulty
from sincere_singularities.modules.order_queue import OrderQueue

if TYPE_CHECKING:
    from sincere_singularities.modules.restaurants_view import Restaurants

# This global set is used to ensure that a (non-weak) reference is kept to background tasks created that aren't
# awaited. These tasks get added to this set, then once they're done, they remove themselves.
# See RUF006
background_tasks: set[asyncio.Task[None]] = set()


class ConditionType(StrEnum):
    """Enum class for different conditions."""

    # An entire menu section (e.g. Main Courses) is out of stock.
    OUT_OF_STOCK_SECTION = auto()
    # A menu item (e.g. Lemonade) is out of stock.
    OUT_OF_STOCK_ITEM = auto()
    # The user shouldn't specify the firstnames of customers.
    NO_FIRSTNAME = auto()
    # There are no deliveries available. "No delivery available" should be put in the address field.
    NO_DELIVERY = auto()
    # The delivery time shouldn't be specified.
    NO_DELIVERY_TIME = auto()
    # Extra wish shouldn't be specified.
    NO_EXTRA_WISH = auto()


# The probabilities of each condition happening. The numbers should add up to 1.
CONDITIONS_PROBABILITIES = {
    ConditionType.OUT_OF_STOCK_SECTION: 0.2,
    ConditionType.OUT_OF_STOCK_ITEM: 0.4,
    ConditionType.NO_FIRSTNAME: 0.1,
    ConditionType.NO_DELIVERY: 0.1,
    ConditionType.NO_DELIVERY_TIME: 0.1,
    ConditionType.NO_EXTRA_WISH: 0.1,
}

CONDITION_FREQUENCIES = {
    Difficulty.EASY: (120, 240),
    Difficulty.MEDIUM: (60, 120),
    Difficulty.HARD: (30, 60),
}


@dataclass(slots=True)
class Conditions:
    """The condition's storage. Every dictionary's keys are restaurant names."""

    # Out of stock menu section. Format: Dict[Restaurant_Name, List[Menu_Section]]
    out_of_stock_sections: defaultdict[str, list[str]] = field(default_factory=lambda: defaultdict(list[str]))
    # Out of stock items. Format: Dict[Restaurant_Name, dict[Menu_Section, List[Menu_Item]]]
    out_of_stock_items: defaultdict[str, dict[str, list[str]]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(list[str]))
    )
    # Customer information conditions
    no_firstname: defaultdict[str, bool] = field(default_factory=lambda: defaultdict(bool))
    no_delivery: defaultdict[str, bool] = field(default_factory=lambda: defaultdict(bool))
    no_delivery_time: defaultdict[str, bool] = field(default_factory=lambda: defaultdict(bool))
    no_extra_wish: defaultdict[str, bool] = field(default_factory=lambda: defaultdict(bool))


class ConditionManager:
    """Managing the conditions of restaurants."""

    def __init__(self, order_queue: OrderQueue) -> None:
        """
        Initialize the condition manager.

        Args:
            order_queue (OrderQueue): The order queue.
        """
        self.order_queue = order_queue
        self.webhook = order_queue.webhook
        self.user_id = order_queue.user.id

        self.restaurants: Restaurants | None = None
        self.order_conditions = Conditions()

    async def spawn_conditions(self) -> None:
        """Constantly spawn conditions on the restaurants while the game is running."""
        while self.order_queue.running:
            # Choose a random restaurant
            assert self.restaurants
            restaurant = random.choice(self.restaurants.restaurants)

            spawn_sleep_seconds = random.randint(
                *CONDITION_FREQUENCIES[self.order_queue.order_generators[restaurant.name].difficulty]
            )
            delete_sleep_seconds = float(
                random.randint(*CONDITION_FREQUENCIES[self.order_queue.order_generators[restaurant.name].difficulty])
            )
            await asyncio.sleep(spawn_sleep_seconds)

            # Choose a random condition with the provided probabilities.
            condition = random.choices(
                population=list(CONDITIONS_PROBABILITIES.keys()),
                weights=list(CONDITIONS_PROBABILITIES.values()),
            )[0]

            # Choose a menu section and item if needed.
            menu_section, menu_item = None, None
            if condition in (ConditionType.OUT_OF_STOCK_SECTION, ConditionType.OUT_OF_STOCK_ITEM):
                menu_section = random.choice(list(restaurant.menu.keys()))
                if condition == ConditionType.OUT_OF_STOCK_ITEM:
                    menu_item = random.choice(restaurant.menu[menu_section])

            # Apply the condition.
            message = await self.apply_condition(
                condition,
                restaurant.name,
                menu_section,
                menu_item,
            )
            # Create and store the created delete task.
            task = asyncio.create_task(
                self.delete_condition(
                    condition,
                    message,
                    restaurant.name,
                    delete_sleep_seconds,
                    menu_section,
                    menu_item,
                )
            )
            background_tasks.add(task)
            task.add_done_callback(background_tasks.discard)

    async def apply_condition(
        self,
        condition: ConditionType,
        restaurant_name: str,
        menu_section: str | None = None,
        menu_item: str | None = None,
    ) -> WebhookMessage:
        """
        Applies a condition to a restaurant.

        Args:
            condition (ConditionType): The condition to apply to the restaurant.
            restaurant_name (str): The name of the restaurant.
            menu_section (str | None, optional): The name of the menu section (OUT_OF_STOCK_SECTION). Defaults to None.
            menu_item (str | None, optional): The name of the menu item (OUT_OF_STOCK_ITEM). Defaults to None.
        """
        match condition:
            case ConditionType.OUT_OF_STOCK_SECTION:
                if not menu_section:
                    raise ValueError("missing menu_section")
                self.order_conditions.out_of_stock_sections[restaurant_name].append(menu_section)
                message = f"{restaurant_name} is out of stock for {menu_section}!"
            case ConditionType.OUT_OF_STOCK_ITEM:
                if not menu_section:
                    raise ValueError("missing menu_section")
                if not menu_item:
                    raise ValueError("missing menu_item")
                self.order_conditions.out_of_stock_items[restaurant_name][menu_section].append(menu_item)
                message = f"{restaurant_name} is out of stock for {menu_item}!"
            case ConditionType.NO_FIRSTNAME:
                self.order_conditions.no_firstname[restaurant_name] = True
                message = f"For {restaurant_name} orders you shouldn't specify the first name of customers."
            case ConditionType.NO_DELIVERY:
                self.order_conditions.no_delivery[restaurant_name] = True
                message = (
                    f"{restaurant_name} doesn't do delivery anymore. \n"
                    f"Type in `No delivery available` for the address field!"
                )
            case ConditionType.NO_DELIVERY_TIME:
                self.order_conditions.no_delivery_time[restaurant_name] = True
                message = f"For {restaurant_name} orders you shouldn't specify delivery time."
            case ConditionType.NO_EXTRA_WISH:
                self.order_conditions.no_extra_wish[restaurant_name] = True
                message = f"For {restaurant_name} orders you shouldn't specify extra wishes."

        return await self.webhook.send(
            content=message,
            username="🚨 Conditions Alert 🚨",
            wait=True,
            thread=self.order_queue.orders_thread,
            avatar_url="https://www.emojibase.com/resources/img/emojis/apple/1f6a8.png",
        )

    async def delete_condition(
        self,
        condition: ConditionType,
        message: WebhookMessage,
        restaurant_name: str,
        delete_seconds: float,
        menu_section: str | None = None,
        menu_item: str | None = None,
    ) -> None:
        """
        Deletes a condition from a restaurant after waiting.

        Args:
            condition (ConditionType): The condition to delete from the restaurant.
            message (WebhookMessage): The message to delete.
            restaurant_name (str): The name of the restaurant.
            delete_seconds (float): The amount of time in seconds to wait before deleting the condition.
            menu_section (str | None, optional): The name of the menu section (OUT_OF_STOCK_SECTION). Defaults to None.
            menu_item (str | None, optional): The name of the menu item (OUT_OF_STOCK_ITEM). Defaults to None.
        """
        await asyncio.sleep(delete_seconds)

        # Deleting Webhook message (Note: delete_after or message.delete() dont work presumably because of the thread)
        assert self.order_queue.orders_thread
        await self.order_queue.orders_thread.delete_messages([message])

        match condition:
            case ConditionType.OUT_OF_STOCK_SECTION:
                if not menu_section:
                    raise ValueError("missing menu_section")
                self.order_conditions.out_of_stock_sections[restaurant_name].remove(menu_section)
            case ConditionType.OUT_OF_STOCK_ITEM:
                if not menu_section:
                    raise ValueError("missing menu_section")
                if not menu_item:
                    raise ValueError("missing menu_item")
                self.order_conditions.out_of_stock_items[restaurant_name][menu_section].remove(menu_item)
            case ConditionType.NO_FIRSTNAME:
                self.order_conditions.no_firstname[restaurant_name] = False
            case ConditionType.NO_DELIVERY:
                self.order_conditions.no_delivery[restaurant_name] = False
            case ConditionType.NO_DELIVERY_TIME:
                self.order_conditions.no_delivery_time[restaurant_name] = False
            case ConditionType.NO_EXTRA_WISH:
                self.order_conditions.no_extra_wish[restaurant_name] = False

    def adjust_order_to_conditions(self, order: Order) -> Order:
        """
        Adjust the order to the current conditions.

        For example, if the current condition is `NO_FIRSTNAME`, then this function removes the firstname from this
        order.

        Args:
            order (Order): The (correct) order to adjust.

        Returns:
            Order: The adjusted order.
        """
        restaurant_name = order.restaurant_name
        if not restaurant_name:
            raise ValueError("missing restaurant_name")

        # Deleting the out-of-stock section if necessary
        for menu_section in self.order_conditions.out_of_stock_sections[restaurant_name]:
            with suppress(KeyError):
                del order.foods[menu_section]

        # Deleting the out-of-stock menu items if necessary
        for menu_section, menu_items in self.order_conditions.out_of_stock_items[restaurant_name].items():
            for menu_item in menu_items:
                with suppress(ValueError):
                    order.foods[menu_section].remove(menu_item)

        # Checking the customer information section
        if not order.customer_information:
            raise ValueError("missing customer_information")
        adjusted_name = order.customer_information.name
        adjusted_address = order.customer_information.address
        adjusted_delivery_time = order.customer_information.delivery_time
        adjusted_extra_wish = order.customer_information.extra_wish

        # Firstname check
        if self.order_conditions.no_firstname.get(restaurant_name):
            adjusted_name = adjusted_name.split()[-1]

        # No delivery check
        if self.order_conditions.no_delivery.get(restaurant_name):
            adjusted_address = "No delivery available"

        # No delivery time check
        if self.order_conditions.no_delivery_time.get(restaurant_name):
            adjusted_delivery_time = ""

        # No extra wish check
        if self.order_conditions.no_extra_wish.get(restaurant_name):
            adjusted_extra_wish = ""

        # Generating new CustomerInformation
        adjusted_customer_information = CustomerInformation(
            order_id=order.customer_information.order_id,
            name=adjusted_name,
            address=adjusted_address,
            delivery_time=adjusted_delivery_time,
            extra_wish=adjusted_extra_wish,
        )
        order.customer_information = adjusted_customer_information

        return order
