import random
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import disnake
from disnake import ButtonStyle, MessageInteraction, ModalInteraction, TextInputStyle

from sincere_singularities.modules.points import add_points, get_points
from sincere_singularities.utils import DISNAKE_COLORS

if TYPE_CHECKING:
    from sincere_singularities.modules.restaurant import Restaurant


@dataclass(frozen=True)
class CustomerInfo:
    """The Dataclass Containing Information added in the Customer Information Section."""

    order_id: str
    name: str
    address: str
    delivery_time: str
    extra_information: str


@dataclass(unsafe_hash=True)
class Order:
    """The Dataclass Containing Order Information."""

    order_timestamp: datetime | None = None
    customer_information: CustomerInfo | None = None
    restaurant_name: str | None = None
    foods: defaultdict[str, list[str]] = field(default_factory=lambda: defaultdict(list[str]))

    def __post_init__(self) -> None:
        # Recalculate the Order Timestamp to match Initialization
        self.order_timestamp = datetime.utcnow()  # Timezone doesnt matter
        self.penalty_seconds = random.randint(4 * 60, 6 * 60)
        self.penalty_timestamp = self.order_timestamp + timedelta(seconds=self.penalty_seconds)


class CustomerInfoModal(disnake.ui.Modal):
    """The Modal for entering Customer Information."""

    def __init__(self, order_view: "OrderView") -> None:
        self.order_view = order_view
        components = [
            disnake.ui.TextInput(label="Order ID", custom_id="order_id", style=TextInputStyle.short, max_length=64),
            disnake.ui.TextInput(label="Name", custom_id="name", style=TextInputStyle.short, max_length=64),
            disnake.ui.TextInput(label="Address", custom_id="address", style=TextInputStyle.short, max_length=64),
            disnake.ui.TextInput(
                label="Time of delivery", custom_id="time", style=TextInputStyle.short, required=False, max_length=64
            ),
            disnake.ui.TextInput(
                label="Extra information",
                custom_id="extra",
                style=TextInputStyle.paragraph,
                required=False,
                max_length=1028,
            ),
        ]
        super().__init__(title="Customer information", components=components)

    async def callback(self, inter: ModalInteraction) -> None:
        """The Callback when the User has entered the Customer Information."""
        # Check if wrong OrderID was entered
        if not self.order_view.restaurant.order_queue.get_order_by_id(inter.text_values["order_id"]):
            # Adding Error Message
            embed = self.order_view.embed
            embed.insert_field_at(index=0, name=" ", value=" ", inline=False)
            embed.insert_field_at(
                index=1,
                name=":rotating_light: :warning: Error :warning: :rotating_light:",
                value="**Incorrect order ID. Try again.**",
                inline=False,
            )
            await inter.response.edit_message(view=self.order_view, embed=embed)
            return

        self.order_view.order.restaurant_name = self.order_view.restaurant.name
        self.order_view.order.customer_information = CustomerInfo(
            order_id=inter.text_values["order_id"],
            name=inter.text_values["name"],
            address=inter.text_values["address"],
            delivery_time=inter.text_values["time"],
            extra_information=inter.text_values["extra"],
        )
        await inter.response.edit_message(view=self.order_view, embed=self.order_view.embed)


class FoodButton(disnake.ui.Button):
    """A Button for adding a specific Menu Item."""

    def __init__(self, food_view: "FoodsView", order: Order, menu_item: str, food: str) -> None:
        super().__init__(label=food, style=ButtonStyle.primary)
        self.food_view = food_view
        self.order = order
        self.menu_item = menu_item
        self.food = food

    async def callback(self, inter: MessageInteraction) -> None:
        """The Callback after adding a specific Menu Item."""
        self.order.foods[self.menu_item].append(self.food)
        await inter.response.edit_message(view=self.food_view, embed=self.food_view.order_view.embed)


class FoodsView(disnake.ui.View):
    """The View for adding a Menu Items (e.g. Main Courses)."""

    def __init__(
        self, restaurant: "Restaurant", order_view: "OrderView", order: Order, menu_item: str, foods: Iterable[str]
    ) -> None:
        super().__init__()
        self.restaurant = restaurant
        self.order_view = order_view
        self.order = order
        self.menu_item = menu_item
        for food in foods:
            self.add_item(FoodButton(self, self.order, self.menu_item, food))

    @disnake.ui.button(label="Back", style=disnake.ButtonStyle.secondary, row=1)
    async def _food_back(self, _: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        await inter.response.edit_message(view=self.order_view, embed=self.order_view.embed)


class MenuItemButton(disnake.ui.Button):
    """The Button for accessing a Menu Part (e.g. Main Courses)"""

    def __init__(
        self, restaurant: "Restaurant", order_view: "OrderView", order: Order, menu_item: str, btn_index: int
    ) -> None:
        row_index = 0 if btn_index <= 1 else 1
        super().__init__(label=menu_item, style=ButtonStyle.primary, row=row_index, custom_id=menu_item)
        self.restaurant = restaurant
        self.order_view = order_view
        self.order = order
        self.menu_item = menu_item

    async def callback(self, inter: MessageInteraction) -> None:
        """The Callback to access a Menu Part."""
        food_view = FoodsView(
            self.restaurant,
            self.order_view,
            self.order,
            self.menu_item,
            self.restaurant.restaurant_json.menu[self.menu_item],
        )
        await inter.response.edit_message(view=food_view, embed=self.order_view.embed)


class OrderView(disnake.ui.View):
    """The view in which the order is displayed and managed by the user."""

    def __init__(self, restaurant: "Restaurant") -> None:
        super().__init__()
        self.restaurant = restaurant
        self.order = Order()
        for i, menu_item in enumerate(restaurant.menu):
            self.add_item(MenuItemButton(restaurant, self, self.order, menu_item, i))

    @property
    def embed(self) -> disnake.Embed:
        """Generating a new dynamic Embed for the Order Overview."""
        embed = disnake.Embed(
            title=f"{self.restaurant.icon} MENU: {self.restaurant.name} {self.restaurant.icon}",
            description=f"{self.restaurant.description} \n",
            colour=DISNAKE_COLORS.get(self.restaurant.icon, disnake.Color.random()),
        )
        # Adding an Empty Field for better formatting
        embed.add_field(" ", " ")
        # Adding Already Added Menu Items
        for menu_name, menu_items in self.order.foods.items():
            embed.add_field(
                name=f"Added {menu_name} Items",
                value="\n".join(f"- `{item_name}`: {menu_items.count(item_name)}" for item_name in set(menu_items)),
                inline=False,
            )

        return embed

    @disnake.ui.button(label="Customer Information", style=disnake.ButtonStyle.success, row=2)
    async def _customer_information(self, _: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        await inter.response.send_modal(CustomerInfoModal(self))

    @disnake.ui.button(label="Done", style=disnake.ButtonStyle.success, row=2)
    async def _order_done(self, _: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        # Sending Order Placed Message and back to Start Screen
        if not self.order.customer_information:
            embed = self.embed
            embed.insert_field_at(index=0, name=" ", value=" ", inline=False)
            embed.insert_field_at(
                index=1,
                name=":rotating_light: :warning: Error :warning: :rotating_light:",
                value="**Customer information missing!**",
                inline=False,
            )
            await inter.response.edit_message(embed=embed, view=self)
            return

        # Getting the correct order
        correct_order = self.restaurant.order_queue.get_order_by_id(self.order.customer_information.order_id)
        assert correct_order

        # Calculating Correctness and Discarding Order
        correctness = self.restaurant.check_order(self.order, correct_order)
        await self.restaurant.order_queue.discard_order(self.order.customer_information.order_id)
        points = round(correctness * 10)  # 100% -> 10p

        # Checking how long Order Completion took
        assert correct_order.order_timestamp
        time_taken = (datetime.utcnow() - correct_order.order_timestamp).total_seconds()  # Timezone doesnt matter
        bonus_interval = 60  # (seconds)
        completion_message = ""
        if time_taken <= bonus_interval:
            points += 5
            completion_message = "You've completed the order in under a minute and get 5 bonus points! \n"
        elif time_taken >= correct_order.penalty_seconds:
            points -= 5
            completion_message = "You've took to long to complete the order and receive a 5 points penalty! \n"

        add_points(inter.user.id, points)

        # Adding Info to embed
        embed = self.restaurant.restaurants.embeds[0]
        embed.insert_field_at(index=0, name=" ", value=" ", inline=False)
        embed.insert_field_at(
            index=1,
            name=":loudspeaker: :white_check_mark: Info :white_check_mark: :loudspeaker:",
            value=f"**Order placed successfully! Correctness: {round(correctness, 4) * 100}%.\n {completion_message}"
            f"You gained {points} points; you now have {get_points(inter.user.id)}!**",
            inline=False,
        )
        await inter.response.edit_message(embed=embed, view=self.restaurant.restaurants.view)

    @disnake.ui.button(label="Show conditions", style=disnake.ButtonStyle.secondary, row=2)
    async def _show_conditions(self, _: disnake.ui.Button, inter: disnake.Message.Interaction) -> None:
        embed = disnake.Embed(title="Current conditions", color=disnake.Color.blue())
        condition = self.restaurant.restaurants.condition_manager.order_conditions
        if menu_section := condition.out_of_stock_sections.get(self.restaurant.name):
            embed.add_field(
                "Out of stock menu sections",
                f"The following menu sections are out of stock: {', '.join(menu_section)}",
                inline=False,
            )
        if sections := condition.out_of_stock_items.get(self.restaurant.name):
            out_of_stock_items = ", ".join([item for menu in sections.values() for item in menu])
            embed.add_field(
                "Out of stock menu items",
                f"The following menu items are out of stock: {out_of_stock_items}",
                inline=False,
            )
        if condition.no_firstname.get(self.restaurant.name):
            embed.add_field("No firstname", "You shouldn't specify the first names of the customers.", inline=False)
        if condition.no_delivery.get(self.restaurant.name):
            embed.add_field("No delivery", "Type in `No delivery available` for the address field.", inline=False)
        if condition.no_delivery_time.get(self.restaurant.name):
            embed.add_field("No delivery time", "You shouldn't specify the delivery time.", inline=False)
        if condition.no_extra_information.get(self.restaurant.name):
            embed.add_field("No extra information", "You shouldn't specify extra informations.", inline=False)
        if not embed.fields:
            embed.description = "No conditions at this time."
        await inter.response.send_message(ephemeral=True, embed=embed)
