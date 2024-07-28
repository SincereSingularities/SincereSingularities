import random
import re
from typing import TYPE_CHECKING

import disnake

from sincere_singularities.modules.coins import (
    buy_restaurant,
    get_coins,
    has_restaurant,
)
from sincere_singularities.modules.order_queue import OrderQueue
from sincere_singularities.modules.restaurant import Restaurant
from sincere_singularities.utils import DISNAKE_COLORS, RESTAURANT_JSON

if TYPE_CHECKING:
    from sincere_singularities.modules.conditions import ConditionManager


class RestaurantPurchaseView(disnake.ui.View):
    """View subclass for buying a restaurant."""

    def __init__(self, user_id: int, restaurant: Restaurant, parent: "RestaurantsView") -> None:
        """
        Initialize a the restaurant purchase view.

        Args:
            user_id (int): The user's ID.
            restaurant (Restaurant): The restaurant.
            parent (RestaurantsView): The restaurants view.
        """
        super().__init__(timeout=None)
        self.user_id = user_id
        self.restaurant = restaurant
        self.parent = parent
        # Disable the buy button if the used doesn't have enough coins.
        if get_coins(user_id) < restaurant.coins:
            self._buy.disabled = True

    @disnake.ui.button(label="Buy", style=disnake.ButtonStyle.success)
    async def _buy(self, _: disnake.ui.Button, interaction: disnake.MessageInteraction) -> None:
        buy_restaurant(self.user_id, self.restaurant.name)
        self.parent.update_state()
        await interaction.response.edit_message(view=self.parent, embed=self.parent.embeds[self.parent.index])

    @disnake.ui.button(label="Cancel", style=disnake.ButtonStyle.secondary)
    async def _cancel(self, _: disnake.ui.Button, interaction: disnake.MessageInteraction) -> None:
        await interaction.response.edit_message(view=self.parent, embed=self.parent.embeds[self.parent.index])


class RestaurantsView(disnake.ui.View):
    """View subclass for choosing the restaurant."""

    def __init__(self, restaurants: "Restaurants", index: int = 0) -> None:
        """
        Initialize the restaurants view.

        Args:
            restaurants (Restaurants): The restaurants.
            index (int, optional): The index to start from. Defaults to 0.
        """
        super().__init__(timeout=None)
        self.restaurants = restaurants
        self.index = index

        # Sets the footer of the embeds with their respective page numbers.
        for i, embed in enumerate(self.embeds):
            embed.set_footer(text=f"Restaurant {i + 1} of {len(self.embeds)}")

        self.update_state()

    @property
    def embeds(self) -> list[disnake.Embed]:
        """list[disnake.Embed]: The embeds of the restaurants (on the restaurant selection screen)."""
        return self.restaurants.embeds

    def update_state(self) -> None:
        """Updating the State of the RestaurantsView"""
        # Disable previous/next button for first/last embeds
        self._prev_page.disabled = self.index == 0
        self._next_page.disabled = self.index == len(self.embeds) - 1
        if has_restaurant(self.restaurants.interaction.user.id, self.restaurants.all_restaurants[self.index].name):
            self._enter_restaurant.label = "Enter restaurant"
        else:
            self._enter_restaurant.label = "Buy"
        coins = get_coins(self.restaurants.interaction.user.id)
        description = self.embeds[self.index].description
        assert description
        self.embeds[self.index].description = re.sub(r"you have \d+", f"you have {coins}", description)

    @disnake.ui.button(emoji="◀", style=disnake.ButtonStyle.secondary, row=0)
    async def _prev_page(self, _: disnake.ui.Button, interaction: disnake.MessageInteraction) -> None:
        self.index -= 1
        self.update_state()

        await interaction.response.edit_message(embed=self.embeds[self.index], view=self)

    @disnake.ui.button(label="Enter Restaurant", style=disnake.ButtonStyle.success, row=0)
    async def _enter_restaurant(self, _: disnake.ui.Button, interaction: disnake.MessageInteraction) -> None:
        # Find restaurant based on current index
        restaurant = self.restaurants.all_restaurants[self.index]
        # Show purchase view if the user doesn't own the restaurant
        if not has_restaurant(interaction.user.id, restaurant.name):
            user_coins = get_coins(interaction.user.id)
            if user_coins < restaurant.coins:
                embed_title = "You do not have enough coins to buy this restaurant."
                embed_description = (
                    f"It costs {restaurant.coins} coins.\nYou have {user_coins}.\nTo buy it,"
                    f" you need {restaurant.coins - user_coins} more coins."
                )
            else:
                embed_title = "You do not own this restaurant."
                embed_description = (
                    f"It costs {restaurant.coins} coins.\nYou have {user_coins}.\nAfter buying it,"
                    f" you'd have {user_coins - restaurant.coins}."
                )

            await interaction.response.edit_message(
                view=RestaurantPurchaseView(interaction.user.id, restaurant, self),
                embed=disnake.Embed(
                    title=embed_title,
                    description=embed_description,
                    colour=disnake.Color.yellow(),
                ),
            )
            return
        # Stopping this view
        self.stop()
        await restaurant.enter_menu(interaction)

    @disnake.ui.button(emoji="▶", style=disnake.ButtonStyle.secondary, row=0)
    async def _next_page(self, _: disnake.ui.Button, interaction: disnake.MessageInteraction) -> None:
        self.index += 1
        self.update_state()

        await interaction.response.edit_message(embed=self.embeds[self.index], view=self)

    @disnake.ui.button(label="Pause Orders", style=disnake.ButtonStyle.secondary, row=1)
    async def _pause_orders(self, _: disnake.ui.Button, interaction: disnake.MessageInteraction) -> None:
        # Placebo Button. Doesn't do anything but looks nice (to give the user feeling of control.)
        # This button doesn't do anything because the game ensure the user has 3 orders at all times, so you won't get
        # more than 3 orders anyway, and they don't run out.
        await interaction.response.defer()

    @disnake.ui.button(label="Stop the Game", style=disnake.ButtonStyle.danger, row=1)
    async def _stop_game(self, *_: disnake.ui.Button | disnake.MessageInteraction) -> None:
        await self.restaurants.interaction.delete_original_message()
        await self.restaurants.order_queue.stop_orders()


class Restaurants:
    """Class to manage the restaurants and the UI."""

    def __init__(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        order_queue: OrderQueue,
        condition_manager: "ConditionManager",
    ) -> None:
        """
        Initialize the restaurants.

        Args:
            interaction (disnake.ApplicationCommandInteraction): The Disnake application command interaction.
            order_queue (OrderQueue): The order queue.
            condition_manager (ConditionManager): The condition manager.
        """
        self.interaction = interaction
        self.order_queue: OrderQueue = order_queue
        self.condition_manager = condition_manager

    @property
    def view(self) -> RestaurantsView:
        """RestaurantsView: The view object for the restaurants."""
        return RestaurantsView(self)

    @property
    def embeds(self) -> list[disnake.Embed]:
        """list[disnake.Embed]: The embeds of the restaurants (on the restaurant selection screen)."""
        # Generate embeds from restaurants
        embeds: list[disnake.Embed] = []

        for restaurant in RESTAURANT_JSON:
            if has_restaurant(self.interaction.user.id, restaurant.name):
                own = "You own this restaurant."
            else:
                own = ":lock: You don't own this restaurant."
            embed = disnake.Embed(
                title=f"{restaurant.icon} {restaurant.name} {restaurant.icon}",
                description=f"{restaurant.description} \n**Required coins**: {restaurant.coins}"
                f" (you have {get_coins(self.interaction.user.id)})\n{own}",
                colour=DISNAKE_COLORS.get(restaurant.icon, disnake.Color.random()),
            )
            # Setting Embed Author
            embed.set_author(name="Restaurant Rush: Kitchen Chaos")
            # Adding an empty field for better formatting
            embed.add_field(" ", " ")
            # Adding examples from the Menu
            embed.add_field(
                name="Example Starter",
                value=f"`{random.choice(restaurant.menu['Starters'])}`",
                inline=False,
            )
            embed.add_field(
                name="Example Main Course",
                value=f"`{random.choice(restaurant.menu['Main Courses'])}`",
                inline=False,
            )
            embed.add_field(
                name="Example Dessert",
                value=f"`{random.choice(restaurant.menu['Desserts'])}`",
                inline=False,
            )
            embed.add_field(
                name="Example Drink",
                value=f"`{random.choice(restaurant.menu['Drinks'])}`",
                inline=False,
            )

            embeds.append(embed)

        return embeds

    @property
    def restaurants(self) -> list[Restaurant]:
        """list[Restaurant]: The restaurants that the user owns, each restaurant is initialized via its JSON."""
        # Creating Restaurant Objects Based on the Data
        return [
            Restaurant(self, restaurant)
            for restaurant in RESTAURANT_JSON
            if has_restaurant(self.interaction.user.id, restaurant.name)
        ]

    @property
    def all_restaurants(self) -> list[Restaurant]:
        """list[Restaurant]: The restaurants list, each restaurant is initialized via its JSON."""
        # Creating Restaurant Objects Based on the Data
        return [Restaurant(self, restaurant) for restaurant in RESTAURANT_JSON]
