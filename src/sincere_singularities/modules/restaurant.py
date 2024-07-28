from collections import Counter
from collections.abc import Iterable
from typing import TYPE_CHECKING

from disnake import MessageInteraction

from sincere_singularities.modules.order import Order, OrderView
from sincere_singularities.utils import (
    RestaurantJsonType,
    check_pattern_similarity,
    compare_sentences,
)

if TYPE_CHECKING:
    from sincere_singularities.modules.order_queue import OrderQueue
    from sincere_singularities.modules.restaurants_view import Restaurants


def count_differences(first_iterable: Iterable[object], second_iterable: Iterable[object]) -> int:
    """
    Count the differences between two iterables, indexes independent.

    Args:
        first_iterable (Iterable[object]): First iterable to check.
        second_iterable (Iterable[object]): Second iterable to check.

    Returns:
        int: The amount of differences.
    """
    # Initialize counters
    counter0 = Counter(first_iterable)
    counter1 = Counter(second_iterable)

    # Calculate the total differences
    return sum((counter0 - counter1).values()) + sum((counter1 - counter0).values())


class Restaurant:
    """Represents a single restaurant."""

    def __init__(self, restaurants: "Restaurants", restaurant_json: RestaurantJsonType) -> None:
        """
        Initialize the restaurant.

        Args:
            restaurants (Restaurants): The restaurants.
            restaurant_json (RestaurantJson): The restaurants JSON.
        """
        self.restaurants = restaurants
        self.restaurant_json = restaurant_json

        self.name = restaurant_json.name
        self.icon = restaurant_json.icon
        self.description = restaurant_json.description
        self.coins = restaurant_json.coins
        self.menu = restaurant_json.menu

        self.order_queue: OrderQueue = restaurants.order_queue

    async def enter_menu(self, interaction: MessageInteraction) -> None:
        """
        Function called initially when the user enters the restaurant.

        Args:
            interaction (MessageInteraction): The Disnake MessageInteraction object.
        """
        view = OrderView(self)
        await interaction.response.edit_message(embed=view.embed, view=view)

    def check_order(self, order: Order, correct_order: Order) -> float:
        """
        Checking if the order was correctly placed by the user.

        Args:
            order (Order): The order to check.
            correct_order (Order): The correct order to check against.

        Returns:
            float: How correct the order was placed in percentage
        """
        # Adjust order to conditions
        correct_order = self.restaurants.condition_manager.adjust_order_to_conditions(correct_order)

        score = 1.0
        # The effect on the score each wrong answer should have
        # (Length of menu items + customer information items + 1 for the restaurant)
        score_percentile = 1 / (len(correct_order.foods) + 4 + 1)

        # Subtracting sentiment analysis scores of the customer information
        # This is achieved using a linear interpolation, meaning if the check gives 1.0, 0.0 will be subtracted from
        # the score, but when the check gives 0.0, score_percentile will be subtracted
        correct_customer_information = correct_order.customer_information
        if not correct_customer_information:
            raise ValueError("missing correct_order.customer_information")
        customer_information = order.customer_information
        if not customer_information:
            raise ValueError("missing order.customer_information")

        # Restaurant
        if correct_order.restaurant_name != order.restaurant_name:
            score -= score_percentile

        # Customer name
        name_check = check_pattern_similarity(correct_customer_information.address, customer_information.address)
        score -= score_percentile + (-score_percentile * name_check)

        # Customer address
        address_check = check_pattern_similarity(correct_customer_information.address, customer_information.address)
        score -= score_percentile + (-score_percentile * address_check)

        # Delivery time
        delivery_time_check = compare_sentences(
            correct_customer_information.delivery_time,
            customer_information.delivery_time,
        )
        score -= score_percentile + (-score_percentile * delivery_time_check)

        # Extra wish
        extra_wish_check = compare_sentences(
            correct_customer_information.extra_wish,
            customer_information.extra_wish,
        )
        score -= score_percentile + (-score_percentile * extra_wish_check)

        # Now we can subtract score coins for each wrong order
        # Getting every order item
        correct_order_items = [item for menu_items in correct_order.foods.values() for item in menu_items]
        all_order_items = [item for menu_items in order.foods.values() for item in menu_items]
        # Finding differences between orders and subtracting from score
        order_differences = count_differences(correct_order_items, all_order_items)
        score -= score_percentile * order_differences

        return score
