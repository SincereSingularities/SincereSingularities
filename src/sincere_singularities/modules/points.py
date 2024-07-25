from collections import defaultdict
from typing import TypedDict

from sincere_singularities.utils import RestaurantJson, RestaurantJsonType, load_json


def get_restaurant_by_name(name: str) -> RestaurantJson:
    """
    Get a restaurant by its name.

    Args:
        name (str): The name of the restaurant as it appears in `restaurants.json`.

    Raises:
        ValueError: Raised when a restaurant with that name wasn't found.

    Returns:
        RestaurantJson: The restaurant.
    """
    for restaurant in load_json("restaurants.json", RestaurantJsonType):
        if restaurant.name == name:
            return restaurant
    raise ValueError(f"Restaurant named {name!r} doesn't exist")


# vvv temporary until #6 gets merges vvv


class TemporaryDatabaseEntry(TypedDict):
    """
    An entry to the temporary database.

    Args:
        points (int): How many points the user has.
        restaurants (list[str]): The names of the restaurants that the user owns.
    """

    points: int
    restaurants: list[str]


temporary_database: defaultdict[int, TemporaryDatabaseEntry] = defaultdict(
    lambda: TemporaryDatabaseEntry(
        {"points": 0, "restaurants": [load_json("restaurants.json", RestaurantJsonType)[0].name]}
    )
)


def get_points(user_id: int) -> int:
    """
    Get the points that the user has.

    Args:
        user_id (int): The user's ID.

    Returns:
        int: The amount of points that the user has.
    """
    return temporary_database[user_id]["points"]


def add_points(user_id: int, points: int) -> None:
    """
    Add points to the user.

    Args:
        user_id (int): The user's ID.
        points (int): The amount of points to add.
    """
    temporary_database[user_id]["points"] += points


def get_restaurants(user_id: int) -> list[str]:
    """
    Get the restaurants' name that the user owns.

    Args:
        user_id (int): The user's ID.

    Returns:
        list[str]: The names of the restaurants that the user owns.
    """
    return temporary_database[user_id]["restaurants"]


def has_restaurant(user_id: int, restaurant_name: str) -> bool:
    """
    Returns whether the user owns a restaurant.

    Args:
        user_id (int): The user's ID
        restaurant_name (str): The restaurant's name.

    Returns:
        bool: Whether the user owns that restaurant.
    """
    return restaurant_name in get_restaurants(user_id)


def add_restaurant(user_id: int, restaurant: str) -> None:
    """
    Add a restaurant to the user.

    Args:
        user_id (int): The user's ID.
        restaurant (str): The restaurant's name.
    """
    temporary_database[user_id]["restaurants"].append(restaurant)


# ^^^ temporary ^^^


def buy_restaurant(user_id: int, restaurant_name: str) -> None:
    """
    Buy a restaurant.

    This function deducts the points and adds the restaurant to the user.

    Args:
        user_id (int): The user's ID.
        restaurant_name (str): The restaurant's name.

    Raises:
        ValueError: Raised when the user already owns the restaurant.
        ValueError: Raised when the user doesn't have the points necessary to buy the restaurant.
    """
    if has_restaurant(user_id, restaurant_name):
        # should be disallowed
        raise ValueError(f"User {user_id} already has restaurant {restaurant_name}!")
    restaurant = get_restaurant_by_name(restaurant_name)
    if get_points(user_id) - restaurant.points < 0:
        # should be disallowed
        raise ValueError(f"User {user_id} doesn't have the necessary points to buy {restaurant_name}!")
    add_points(user_id, -restaurant.points)
    add_restaurant(user_id, restaurant_name)
