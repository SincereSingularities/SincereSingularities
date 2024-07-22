from disnake import MessageInteraction

from sincere_singularities.utils import RestaurantJson


class Restaurant:
    """Represents a single restaurant."""

    def __init__(self, restaurant_json: RestaurantJson) -> None:
        self.restaurant_json = restaurant_json

        self.name = restaurant_json.name

    async def enter_menu(self, inter: MessageInteraction) -> None:
        """
        Function Called initially when the user enters the restaurant

        Args:
            inter: The Disnake MessageInteraction object.
        """
        await inter.response.send_message(f"Restaurant {self.name} is entering menu")
