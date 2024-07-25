from collections import defaultdict
from typing import Self, TypedDict

from sincere_singularities.utils import load_json, RestaurantJsonType, RestaurantJson

def get_restaurant_by_name(name: str) -> RestaurantJson:
    for restaurant in load_json("restaurants.json", RestaurantJsonType):
        if restaurant.name == name:
            return restaurant
    raise ValueError(f"Restaurant named {name!r} doesn't exist")

# vvv temporary until #6 gets merges vvv

class TemporaryDatabaseEntry(TypedDict):
    points: int
    restaurants: list[str]

temporary_database: defaultdict[int, TemporaryDatabaseEntry] = defaultdict(lambda: TemporaryDatabaseEntry({"points": 0, "restaurants": [load_json("restaurants.json", RestaurantJsonType)[0].name]}))

def get_points(user_id: int) -> int:
    return temporary_database[user_id]["points"]

def add_points(user_id: int, points: int) -> None:
    temporary_database[user_id]["points"] += points

def get_restaurants(user_id: int) -> list[str]:
    return temporary_database[user_id]["restaurants"]

def has_restaurant(user_id: int, restaurant_name: str) -> bool:
    return restaurant_name in get_restaurants(user_id)

def add_restaurant(user_id: int, restaurant: str) -> None:
    temporary_database[user_id]["restaurants"].append(restaurant)

# ^^^ temporary ^^^

def buy_restaurant(user_id: int, restaurant_name: str) -> bool:
    if has_restaurant(user_id, restaurant_name):
        # should be disallowed
        raise ValueError(f"User {user_id} already has restaurant {restaurant_name}!")
    restaurant = get_restaurant_by_name(restaurant_name)
    if get_points(user_id) - restaurant.points < 0:
        return False
    add_points(user_id, -restaurant.points)
    add_restaurant(user_id, restaurant_name)
    return True

