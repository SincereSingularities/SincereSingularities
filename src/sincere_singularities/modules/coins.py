from sincere_singularities import save_states
from sincere_singularities.data.savestates import generate_default_state
from sincere_singularities.utils import RESTAURANT_JSON, RestaurantJsonType


def get_restaurant_by_name(name: str) -> RestaurantJsonType:
    """
    Get a restaurant by its name.

    Args:
        name (str): The name of the restaurant as it appears in `restaurants.json`.

    Raises:
        ValueError: Raised when a restaurant with that name wasn't found.

    Returns:
        RestaurantJson: The restaurant.
    """
    for restaurant in RESTAURANT_JSON:
        if restaurant.name == name:
            return restaurant
    raise ValueError(f"Restaurant named {name!r} doesn't exist")


def get_coins(user_id: int) -> int:
    """
    Get the coins that the user has.

    Args:
        user_id (int): The user's ID.

    Returns:
        int: The amount of coins that the user has.
    """
    try:
        return save_states.load_game_state(user_id)["coins"]
    except (ValueError, KeyError):
        return 0


def add_coins(user_id: int, coins: int) -> None:
    """
    Add coins to the user.

    Args:
        user_id (int): The user's ID.
        coins (int): The amount of coins to add.
    """
    try:
        state = save_states.load_game_state(user_id)
    except ValueError:
        state = generate_default_state()

    state["coins"] += coins
    save_states.save_game_state(user_id, state)


def get_restaurants(user_id: int) -> list[str]:
    """
    Get the restaurants' name that the user owns.

    Args:
        user_id (int): The user's ID.

    Returns:
        list[str]: The names of the restaurants that the user owns.
    """
    try:
        return save_states.load_game_state(user_id)["restaurants"]
    except (ValueError, KeyError):
        return [RESTAURANT_JSON[0].name]


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
    try:
        state = save_states.load_game_state(user_id)
    except ValueError:
        state = generate_default_state()
    state["restaurants"].append(restaurant)
    save_states.save_game_state(user_id, state)


def buy_restaurant(user_id: int, restaurant_name: str) -> None:
    """
    Buy a restaurant.

    This function deducts the coins and adds the restaurant to the user.

    Args:
        user_id (int): The user's ID.
        restaurant_name (str): The restaurant's name.

    Raises:
        ValueError: Raised when the user already owns the restaurant.
        ValueError: Raised when the user doesn't have the coins necessary to buy the restaurant.
    """
    if has_restaurant(user_id, restaurant_name):
        # should be disallowed
        raise ValueError(f"User {user_id} already has restaurant {restaurant_name}!")
    restaurant = get_restaurant_by_name(restaurant_name)
    if get_coins(user_id) - restaurant.coins < 0:
        # should be disallowed
        raise ValueError(f"User {user_id} doesn't have the necessary coins to buy {restaurant_name}!")
    add_coins(user_id, -restaurant.coins)
    add_restaurant(user_id, restaurant_name)
