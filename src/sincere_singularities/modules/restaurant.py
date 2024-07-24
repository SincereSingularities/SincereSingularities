from collections import Counter
from typing import TYPE_CHECKING

from disnake import MessageInteraction

from sincere_singularities.modules.order import Order, OrderView
from sincere_singularities.utils import RestaurantJson, check_pattern_similarity, compare_sentences

if TYPE_CHECKING:
    from sincere_singularities.modules.order_queue import OrderQueue
    from sincere_singularities.modules.restaurants_view import Restaurants


def count_differences(list0: list[str], list1: list[str]) -> int:
    """
    Count the Differences between two lists, indexes independent.

    Args:
        list0: First List to check.
        list1: Second List to check.

    Returns:
        The Amount of Differences.
    """
    # Initialize Counters on the Lists
    counter0 = Counter(list0)
    counter1 = Counter(list1)

    # Calculate the total differences
    return sum((counter0 - counter1).values()) + sum((counter1 - counter0).values())


class Restaurant:
    """Represents a single restaurant."""

    def __init__(self, restaurants: "Restaurants", restaurant_json: RestaurantJson) -> None:
        self.restaurants = restaurants
        self.restaurant_json = restaurant_json

        self.name = restaurant_json.name
        self.icon = restaurant_json.icon
        self.description = restaurant_json.description
        self.menu = restaurant_json.menu

        # Order Related
        self.order_queue: OrderQueue = restaurants.order_queue

    async def enter_menu(self, inter: MessageInteraction) -> None:
        """
        Function Called initially when the user enters the restaurant

        Args:
            inter: The Disnake MessageInteraction object.
        """
        view = OrderView(self)
        await inter.response.edit_message(embed=view.embed, view=view)

    def check_order(self, order: Order, correct_order: Order) -> float:
        """
        Checking if the order was correctly placed by the user.

        Args:
            order: The Order to check.
            correct_order: The Correct Order to check against.

        Returns:
            How correct the order was placed in percentage (as a float)
        """
        score = 1.0
        # The effect on the Score each wrong answer should have
        # (Length of Menu Items + Customer Information Items + 1 for the restaurant)
        score_percentile = 1 / (len(correct_order.foods) + 4 + 1)

        # Subtracting Sentiment Analysis Scores of the Customer Information
        # This is achieved using a linear interpolation, meaning if the check gives 1.0, 0.0 will be subtracted from
        # the score, but when the check gives 0.0, score_percentile will be subtracted
        correct_customer_information = correct_order.customer_information
        assert correct_customer_information
        customer_information = order.customer_information
        assert customer_information

        # Restaurant
        if correct_order.restaurant_name != order.restaurant_name:
            score -= score_percentile

        # Customer Name
        name_check = check_pattern_similarity(correct_customer_information.address, customer_information.address)
        score -= score_percentile + (-score_percentile * name_check)

        # Customer Address
        address_check = check_pattern_similarity(correct_customer_information.address, customer_information.address)
        score -= score_percentile + (-score_percentile * address_check)

        # Delivery Time
        delivery_time_check = compare_sentences(
            correct_customer_information.delivery_time, customer_information.delivery_time
        )
        score -= score_percentile + (-score_percentile * delivery_time_check)

        # Extra Information
        extra_info_check = compare_sentences(
            correct_customer_information.extra_information, customer_information.extra_information
        )
        score -= score_percentile + (-score_percentile * extra_info_check)

        # Now we can subtract score points for each wrong order
        # Getting every order item
        correct_order_items = [item for menu_items in correct_order.foods.values() for item in menu_items]
        all_order_items = [item for menu_items in order.foods.values() for item in menu_items]
        # Finding Differences between Orders and subtracting from Score
        order_differences = count_differences(correct_order_items, all_order_items)
        score -= score_percentile * order_differences

        return score
