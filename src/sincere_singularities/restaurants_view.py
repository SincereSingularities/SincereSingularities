from typing import List

import disnake

from sincere_singularities.utils import load_json
from sincere_singularities.restaurant import Restaurant

DISNAKE_COLORS = {
    "red": disnake.Colour.red(),
}


class RestaurantsView(disnake.ui.View):
    def __init__(self, ctx, embeds: List[disnake.Embed]) -> None:
        super().__init__(timeout=None)
        self.ctx = ctx
        self.embeds = embeds
        self.index = 0

        # Sets the footer of the embeds with their respective page numbers.
        for i, embed in enumerate(self.embeds):
            embed.set_footer(text=f"Restaurant {i + 1} of {len(self.embeds)}")

        self._update_state()

    def _update_state(self) -> None:
        self.prev_page.disabled = self.index == 0
        self.next_page.disabled = self.index == len(self.embeds) - 1

    @disnake.ui.button(emoji="◀", style=disnake.ButtonStyle.secondary)
    async def prev_page(self, button: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        self.index -= 1
        self._update_state()

        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @disnake.ui.button(label="Enter Restaurant", style=disnake.ButtonStyle.green)
    async def enter_restaurant(self, button: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        # Enter Restaurant based on current index
        restaurant = self.ctx.restaurants[self.index]
        restaurant.enter_menu(inter)

    @disnake.ui.button(emoji="▶", style=disnake.ButtonStyle.secondary)
    async def next_page(self, button: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        self.index += 1
        self._update_state()

        await inter.response.edit_message(embed=self.embeds[self.index], view=self)


class Restaurants:
    def __init__(self, inter: disnake.ApplicationCommandInteraction) -> None:
        self.inter = inter
        # Loading Restaurants
        self.restaurants_json = load_json("restaurants.json")
        self.view = RestaurantsView(self, self.embeds)

    @property
    def embeds(self) -> List[disnake.Embed]:
        # Generate Embeds from Restaurants
        embeds = []

        for restaurant in self.restaurants_json:
            embed = disnake.Embed(
                title=restaurant["name"],
                description=restaurant["description"],
                colour=DISNAKE_COLORS.get(restaurant["color"], disnake.Color.random()),
            )
            # embed.set_author(name=restaurant["name"], url=restaurant["img_url"])
            embeds.append(embed)

        return embeds

    @property
    def restaurants(self) -> List[Restaurant]:
        # Creating Restaurant Objects Based on the Data
        return [Restaurant(restaurant) for restaurant in self.restaurants_json]
