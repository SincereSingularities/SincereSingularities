import random
from typing import TYPE_CHECKING

import disnake

from sincere_singularities.modules.order_queue import OrderQueue
from sincere_singularities.modules.points import buy_restaurant, get_points, has_restaurant
from sincere_singularities.modules.restaurant import Restaurant
from sincere_singularities.utils import DISNAKE_COLORS

if TYPE_CHECKING:
    from sincere_singularities.modules.conditions import ConditionManager


class RestaurantPurchaseView(disnake.ui.View):
    """View subclass for buying a restaurant"""

    def __init__(self, user_id: int, restaurant: Restaurant, parent: "RestaurantsView") -> None:
        super().__init__(timeout=None)
        self.user_id = user_id
        self.restaurant = restaurant
        self.parent = parent
        if get_points(user_id) < restaurant.points:
            self._buy.disabled = True

    @disnake.ui.button(label="Buy", style=disnake.ButtonStyle.success)
    async def _buy(self, _: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        buy_restaurant(self.user_id, self.restaurant.name)
        await inter.response.edit_message(view=self.parent, embed=self.parent.embeds[self.parent.index])

    @disnake.ui.button(label="Cancel", style=disnake.ButtonStyle.secondary)
    async def _cancel(self, _: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        await inter.response.edit_message(view=self.parent, embed=self.parent.embeds[self.parent.index])


class RestaurantsView(disnake.ui.View):
    """View Subclass for Choosing the Restaurant"""

    def __init__(self, ctx: "Restaurants", embeds: list[disnake.Embed], index: int = 0) -> None:
        super().__init__(timeout=None)
        self.ctx = ctx
        self.embeds = embeds
        self.index = index

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
        # Find Restaurant based on current index
        restaurant = self.ctx.restaurants[self.index]
        if not has_restaurant(inter.user.id, restaurant.name):
            user_points = get_points(inter.user.id)
            await inter.response.edit_message(
                view=RestaurantPurchaseView(inter.user.id, restaurant, self),
                embed=disnake.Embed(
                    title="You do not own this restaurant.",
                    description=f"It costs {restaurant.points} points.\nYou have {user_points}.\nAfter buying it,"
                    f" you'd have {user_points - restaurant.points}.",
                    colour=disnake.Color.yellow(),
                ),
            )
            return
        # Stopping view
        self.stop()
        await restaurant.enter_menu(inter)

    @disnake.ui.button(emoji="▶", style=disnake.ButtonStyle.secondary, row=0)
    async def _next_page(self, _: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        self.index += 1
        self._update_state()

        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @disnake.ui.button(label="Pause Orders", style=disnake.ButtonStyle.secondary, row=1)
    async def _pause_orders(self, *_: disnake.ui.Button | disnake.MessageInteraction) -> None:
        # Placebo Button. Doesnt do anything but looks nice (to give the user feeling of control.)
        # This button doesnt do anything because the game ensure the user has 3 orders at all times, so you wont get
        # more than 3 orders anyway, and they dont run out
        return

    @disnake.ui.button(label="Stop the Game", style=disnake.ButtonStyle.danger, row=1)
    async def _stop_game(self, *_: disnake.ui.Button | disnake.MessageInteraction) -> None:
        # TODO: Savestates?
        # TODO: fix awful typing when implemented
        await self.ctx.inter.delete_original_message()
        await self.ctx.order_queue.stop_orders()


class Restaurants:
    """Class to Manage the Restaurants & UI"""

    condition_manager: "ConditionManager"

    def __init__(self, inter: disnake.ApplicationCommandInteraction, order_queue: OrderQueue) -> None:
        self.inter = inter
        self.order_queue = order_queue
        # Loading Restaurants
        self.restaurants_json = order_queue.restaurant_json

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
                description=f"{restaurant.description} \n**Required points**: {restaurant.points}"
                f" (you have {get_points(self.inter.user.id)})",
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
        return [
            Restaurant(self, restaurant)
            for restaurant in self.restaurants_json
            if has_restaurant(self.inter.user.id, restaurant.name)
        ]
