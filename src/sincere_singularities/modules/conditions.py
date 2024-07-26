import asyncio
import random
from collections import defaultdict
from contextlib import suppress
from dataclasses import dataclass, field
from enum import StrEnum, auto

from sincere_singularities.modules.order import CustomerInfo, Order
from sincere_singularities.modules.order_queue import OrderQueue
from sincere_singularities.modules.restaurants_view import Restaurants

CONDITIONS_PROBABILITIES = {
    "OUT_OF_STOCK_SECTION": 0.2,
    "OUT_OF_STOCK_ITEM": 0.4,
    "NO_FIRSTNAME": 0.1,
    "NO_DELIVERY": 0.1,
    "NO_DELIVERY_TIME": 0.1,
    "NO_EXTRA_INFORMATION": 0.1,
}


class ConditionType(StrEnum):
    """Enum Class to Define a ConditionType."""

    OUT_OF_STOCK_SECTION = auto()
    OUT_OF_STOCK_ITEM = auto()
    NO_FIRSTNAME = auto()
    NO_DELIVERY = auto()
    NO_DELIVERY_TIME = auto()
    NO_EXTRA_INFORMATION = auto()


@dataclass
class Conditions:
    """The Conditions Storage. Formated to be read by Restaurant Name."""

    # Missing Menu Section. Format: List[Dict[Restaurant_Name, Menu_Section]]
    out_of_stock_sections: defaultdict[str, list[str]] = field(default_factory=lambda: defaultdict(list[str]))
    # Out of Stock Items. Format: List[Dict[Restaurant_Name, dict[Menu_Section, Menu_Item]]]
    out_of_stock_items: defaultdict[str, dict[str, list[str]]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(list[str]))
    )
    # Customer Information Conditions
    no_firstname: dict[str, bool] = field(default_factory=lambda: defaultdict(bool))
    no_delivery: dict[str, bool] = field(default_factory=lambda: defaultdict(bool))
    no_delivery_time: dict[str, bool] = field(default_factory=lambda: defaultdict(bool))
    no_extra_information: dict[str, bool] = field(default_factory=lambda: defaultdict(bool))


class ConditionManager:
    """Managing the Conditions of each Order (e.g. Pizza is out)."""

    def __init__(self, order_queue: OrderQueue, restaurants: Restaurants) -> None:
        self.order_queue = order_queue
        self.orders_thread = order_queue.orders_thread
        self.webhook = order_queue.webhook
        self.restaurants = restaurants

        self.order_conditions = Conditions()

    async def spawn_conditions(self) -> None:
        """Constantly Spawn Conditions on the restaurants while the Game is running."""
        # while self.order_queue.running:
        for _ in range(1):
            spawn_interval = random.randint(6, 12)
            despawn_interval = float(random.randint(60, 120))
            await asyncio.sleep(spawn_interval)

            condition = ConditionType[
                random.choices(
                    population=list(CONDITIONS_PROBABILITIES.keys()),
                    weights=list(CONDITIONS_PROBABILITIES.values()),
                )[0]
            ]

            restaurant = random.choice(self.restaurants.restaurants)
            menu_section, menu_item = None, None

            if condition in (ConditionType.OUT_OF_STOCK_SECTION, ConditionType.OUT_OF_STOCK_ITEM):
                menu_section = random.choice(list(restaurant.menu.keys()))
                menu_item = random.choice(restaurant.menu[menu_section])

            await self.apply_condition(condition, restaurant.name, despawn_interval, menu_section, menu_item)
            asyncio.create_task(
                self.delete_condition(condition, restaurant.name, despawn_interval, menu_section, menu_item)
            )

    async def apply_condition(
        self,
        condition: ConditionType,
        restaurant_name: str,
        despawn_interval: float,
        menu_section: str | None = None,
        menu_item: str | None = None,
    ) -> None:
        """
        Applies a condition to a Restaurant.

        Args:
            condition: The condition to apply to the restaurant.
            restaurant_name: The name of the restaurant.
            despawn_interval: The amount of time to despawn the condition message.
            menu_section: The name of the menu section (OUT_OF_STOCK_SECTION).
            menu_item: The name of the menu item (OUT_OF_STOCK_ITEM).
        """
        match condition:
            case ConditionType.OUT_OF_STOCK_SECTION:
                assert menu_section
                self.order_conditions.out_of_stock_sections[restaurant_name].append(menu_section)
                message = f"{restaurant_name} is out of stock for {menu_section}!"
            case ConditionType.OUT_OF_STOCK_ITEM:
                assert menu_section
                assert menu_item
                self.order_conditions.out_of_stock_items[restaurant_name][menu_section].append(menu_item)
                message = f"{restaurant_name} is out of stock for {menu_item}!"
            case ConditionType.NO_FIRSTNAME:
                self.order_conditions.no_firstname[restaurant_name] = True
                message = f"For {restaurant_name} orders you shouldn't specify the first name of customers."
            case ConditionType.NO_DELIVERY:
                self.order_conditions.no_delivery[restaurant_name] = True
                message = (
                    f"{restaurant_name} doesnt do delivery anymore. \n"
                    f"Type in `No delivery available` for the address field!"
                )
            case ConditionType.NO_DELIVERY_TIME:
                self.order_conditions.no_delivery_time[restaurant_name] = True
                message = f"For {restaurant_name} orders you shouldn't specify delivery time."
            case ConditionType.NO_EXTRA_INFORMATION:
                self.order_conditions.no_extra_information[restaurant_name] = True
                message = f"For {restaurant_name} orders you shouldn't specify extra information."

        await self.webhook.send(
            content=message,
            username="🚨 Conditions Alert 🚨",
            wait=True,
            thread=self.orders_thread,
            delete_after=despawn_interval,
        )

    async def delete_condition(
        self,
        condition: ConditionType,
        restaurant_name: str,
        despawn_interval: float,
        menu_section: str | None = None,
        menu_item: str | None = None,
    ) -> None:
        """
        Deletes a condition from a Restaurant.

        Args:
            condition: The condition to delete from the restaurant.
            restaurant_name: The name of the restaurant.
            despawn_interval: The amount of time to despawn the condition message.
            menu_section: The name of the menu section (OUT_OF_STOCK_SECTION).
            menu_item: The name of the menu item (OUT_OF_STOCK_ITEM).
        """
        await asyncio.sleep(despawn_interval)

        match condition:
            case ConditionType.OUT_OF_STOCK_SECTION:
                assert menu_section
                self.order_conditions.out_of_stock_sections[restaurant_name].remove(menu_section)
            case ConditionType.OUT_OF_STOCK_ITEM:
                assert menu_section
                assert menu_item
                self.order_conditions.out_of_stock_items[restaurant_name][menu_section].remove(menu_item)
            case ConditionType.NO_FIRSTNAME:
                self.order_conditions.no_firstname[restaurant_name] = False
            case ConditionType.NO_DELIVERY:
                self.order_conditions.no_delivery[restaurant_name] = False
            case ConditionType.NO_DELIVERY_TIME:
                self.order_conditions.no_delivery_time[restaurant_name] = False
            case ConditionType.NO_EXTRA_INFORMATION:
                self.order_conditions.no_extra_information[restaurant_name] = False

    def adjust_order_to_conditions(self, order: Order) -> Order:
        """
        Adjust the order to conditions.

        Args:
            order: The (correct) Order to adjust.

        Returns:
            The Adjusted Order.
        """
        restaurant_name = order.restaurant_name
        assert restaurant_name

        # Deleting the Out-of-Stock Section if necessary
        for menu_section in self.order_conditions.out_of_stock_sections[restaurant_name]:
            with suppress(KeyError):
                del order.foods[menu_section]

        # Deleting the Out-of-Stock Menu Items if necessary
        for menu_section, menu_items in self.order_conditions.out_of_stock_items[restaurant_name].items():
            for menu_item in menu_items:
                with suppress(KeyError):
                    order.foods[menu_section].remove(menu_item)

        # Checking the Customer Information Section
        assert order.customer_information
        adjusted_name = order.customer_information.name
        adjusted_address = order.customer_information.address
        adjusted_delivery_time = order.customer_information.delivery_time
        adjusted_extra_information = order.customer_information.extra_information
        # First Name Check
        if self.order_conditions.no_firstname.get(restaurant_name):
            adjusted_name = adjusted_name.split()[-1]

        # No Delivery Check
        if self.order_conditions.no_delivery.get(restaurant_name):
            adjusted_address = "No delivery available"

        # No Delivery Time Check
        if self.order_conditions.no_delivery_time.get(restaurant_name):
            adjusted_delivery_time = ""

        # No Extra Information Check
        if self.order_conditions.no_extra_information.get(restaurant_name):
            adjusted_extra_information = ""

        # Generating new CustomerInformation
        adjusted_customer_information = CustomerInfo(
            order_id=order.customer_information.order_id,
            name=adjusted_name,
            address=adjusted_address,
            delivery_time=adjusted_delivery_time,
            extra_information=adjusted_extra_information,
        )
        order.customer_information = adjusted_customer_information

        return order
