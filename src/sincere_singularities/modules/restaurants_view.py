import random

import disnake

from sincere_singularities.modules.restaurant import Restaurant
from sincere_singularities.utils import (DISNAKE_COLORS, RestaurantJsonType,
                                         load_json)


class RestaurantsView(disnake.ui.View):
    """View Subclass for Choosing the Restaurant"""

    def __init__(self, ctx: "Restaurants", embeds: list[disnake.Embed]) -> None:
        super().__init__(timeout=None)
        self.ctx = ctx
        self.embeds = embeds
        self.index = 0

        # Sets the footer of the embeds with their respective page numbers.
        for i, embed in enumerate(self.embeds):
            embed.set_footer(text=f"Restaurant {i + 1} of {len(self.embeds)}")

        self._update_state()

    def _update_state(self) -> None:
        self._prev_page.disabled = self.index == 0
        self._next_page.disabled = self.index == len(self.embeds) - 1

    @disnake.ui.button(emoji="◀", style=disnake.ButtonStyle.secondary, row=0)
    async def _prev_page(self, _: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        self.index -= 1
        self._update_state()

        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @disnake.ui.button(label="Enter Restaurant", style=disnake.ButtonStyle.success, row=0)
    async def _enter_restaurant(self, _: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        # Stopping view
        self.stop()
        # Enter Restaurant based on current index
        restaurant = self.ctx.restaurants[self.index]
        await restaurant.enter_menu(inter)

    @disnake.ui.button(emoji="▶", style=disnake.ButtonStyle.secondary, row=0)
    async def _next_page(self, _: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        self.index += 1
        self._update_state()

        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @disnake.ui.button(label="Pause Orders", style=disnake.ButtonStyle.secondary, row=1)
    async def _pause_orders(self, *_: disnake.ui.Button | disnake.MessageInteraction) -> None:
        # TODO: Pause Orders
        # TODO: Fix awful typing when implemented
        return

    @disnake.ui.button(label="Stop the Game", style=disnake.ButtonStyle.danger, row=1)
    async def _stop_game(self, *_: disnake.ui.Button | disnake.MessageInteraction) -> None:
        # TODO: Savestates?
        # TODO: fix awful typing when implemented
        await self.ctx.inter.delete_original_message()


class Restaurants:
    """Class to Manage the Restaurants & UI"""

    def __init__(self, inter: disnake.ApplicationCommandInteraction) -> None:
        self.inter = inter
        # Loading Restaurants
        self.restaurants_json = load_json("restaurants.json", RestaurantJsonType)

    @property
    def view(self) -> RestaurantsView:
        """
        Getting the View Object for the Restaurant. Method to reload the View everytime.

        Returns:
            RestaurantsView: The View Object
        """
        return RestaurantsView(self, self.embeds)

    @property
    def embeds(self) -> list[disnake.Embed]:
        """
        Getting the Embeds of each Restaurant (On the Restaurant Selection Screen).

        Returns:
             List of Disnake Embeds

        """
        # Generate Embeds from Restaurants
        embeds = []

        for restaurant in self.restaurants_json:
            embed = disnake.Embed(
                title=f"{restaurant.icon} {restaurant.name} {restaurant.icon}",
                description=f"{restaurant.description} \n",
                colour=DISNAKE_COLORS.get(restaurant.icon, disnake.Color.random()),
            )
            # Adding an Empty Field for better formatting
            embed.add_field(" ", " ")
            # Adding Examples from the Menu
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
        """
        Getting the Restaurants List, each Restaurant is initialized via its JSON.

        Returns: List of Restaurant Classes

        """
        # Creating Restaurant Objects Based on the Data
        return [Restaurant(self, restaurant) for restaurant in self.restaurants_json]
