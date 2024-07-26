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

# This global set is used to ensure that a (non-weak) reference is kept to background tasks created that aren't
# awaited. These tasks get added to this set, then once they're done, they remove themselves.
# See RUF006
background_tasks: set[asyncio.Task[None]] = set()


@dataclass(frozen=True, slots=True)
class CustomerInformation:
    """The dataclass containing information added in the customer information section."""

    order_id: str
    name: str
    address: str
    delivery_time: str
    extra_information: str


@dataclass
class Order:
    """The dataclass containing order information."""

    customer_information: CustomerInformation | None = None
    restaurant_name: str | None = None
    foods: defaultdict[str, list[str]] = field(default_factory=lambda: defaultdict(list[str]))

    def __post_init__(self) -> None:
        # Recalculate the Order Timestamp to match Initialization
        self.order_timestamp = datetime.utcnow()  # Timezone doesnt matter
        self.penalty_seconds = random.randint(4 * 60, 6 * 60)
        self.penalty_timestamp = self.order_timestamp + timedelta(seconds=self.penalty_seconds)


class CustomerInformationModal(disnake.ui.Modal):
    """The modal for entering customer information."""

    def __init__(self, order_view: "OrderView") -> None:
        """
        Initialize a CustomerInfoModal instance.

        Args:
            order_view (OrderView): The order view.
        """
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

    async def callback(self, interaction: ModalInteraction) -> None:
        """
        The callback when the user has entered the customer information.

        This function checks if the order ID is correct (warns the user if not) and stores the provided data.

        Args:
            interaction (ModalInteraction): The modal interaction.
        """
        # Check if wrong OrderID was entered
        if not self.order_view.restaurant.order_queue.get_order_by_id(interaction.text_values["order_id"]):
            # Adding error message
            embed = self.order_view.embed
            embed.insert_field_at(index=0, name=" ", value=" ", inline=False)
            embed.insert_field_at(
                index=1,
                name=":rotating_light: :warning: Error :warning: :rotating_light:",
                value="**Incorrect order ID. Try again.**",
                inline=False,
            )
            await interaction.response.edit_message(view=self.order_view, embed=embed)
            return

        self.order_view.order.restaurant_name = self.order_view.restaurant.name
        self.order_view.order.customer_information = CustomerInformation(
            order_id=interaction.text_values.get("order_id", ""),
            name=interaction.text_values.get("name", ""),
            address=interaction.text_values.get("address", ""),
            delivery_time=interaction.text_values.get("time", ""),
            extra_information=interaction.text_values.get("extra", ""),
        )
        await interaction.response.edit_message(view=self.order_view, embed=self.order_view.embed)


class MenuItemButton(disnake.ui.Button):
    """A button for adding a specific menu item."""

    def __init__(self, menu_item_view: "MenuItemView", order: Order, menu_section: str, menu_item: str) -> None:
        """
        Initialize the menu item button.

        Args:
            menu_item_view (MenuItemView): The menu item view.
            order (Order): The order.
            menu_section (str): The menu section.
            menu_item (str): The menu item.
        """
        super().__init__(label=menu_item, style=ButtonStyle.primary)
        self.menu_item_view = menu_item_view
        self.order = order
        self.menu_section = menu_section
        self.menu_item = menu_item

    async def callback(self, interaction: MessageInteraction) -> None:
        """
        The callback after adding a specific menu item.

        This function stores the clicked menu item.

        Args:
            interaction (MessageInteraction): The message interaction.
        """
        self.order.foods[self.menu_section].append(self.menu_item)
        await interaction.response.edit_message(view=self.menu_item_view, embed=self.menu_item_view.order_view.embed)


class MenuItemView(disnake.ui.View):
    """The view for adding menu items from a menu section."""

    def __init__(
        self,
        restaurant: "Restaurant",
        order_view: "OrderView",
        order: Order,
        menu_section: str,
        menu_item: Iterable[str],
    ) -> None:
        """
        Initialize the menu item view.

        Args:
            restaurant (Restaurant): The restaurant.
            order_view (OrderView): The order view.
            order (Order): The order.
            menu_section (str): The menu section.
            menu_item (Iterable[str]): The menu items of the menu section.
        """
        super().__init__()
        self.restaurant = restaurant
        self.order_view = order_view
        self.order = order
        self.menu_section = menu_section
        for food in menu_item:
            self.add_item(MenuItemButton(self, self.order, self.menu_section, food))

    @disnake.ui.button(label="Back", style=disnake.ButtonStyle.secondary, row=2)
    async def _food_back(self, _: disnake.ui.Button, interaction: disnake.MessageInteraction) -> None:
        await interaction.response.edit_message(view=self.order_view, embed=self.order_view.embed)


class MenuSectionButton(disnake.ui.Button):
    """The button for accessing a menu section (e.g. Main Courses)"""

    def __init__(
        self, restaurant: "Restaurant", order_view: "OrderView", order: Order, menu_section: str, button_index: int
    ) -> None:
        """
        Initialize the menu section button.

        Args:
            restaurant (Restaurant): The restaurant.
            order_view (OrderView): The order view.
            order (Order): The order.
            menu_section (str): The menu section.
            button_index (int): The button's index.
        """
        row_index = 0 if button_index <= 1 else 1
        super().__init__(label=menu_section, style=ButtonStyle.primary, row=row_index, custom_id=menu_section)
        self.restaurant = restaurant
        self.order_view = order_view
        self.order = order
        self.menu_item = menu_section

    async def callback(self, interaction: MessageInteraction) -> None:
        """
        The callback to access a menu section.

        This function edits the original message to view the chosen FoodsView.

        Args:
            interaction (MessageInteraction): The message interaction.
        """
        food_view = MenuItemView(
            self.restaurant,
            self.order_view,
            self.order,
            self.menu_item,
            self.restaurant.restaurant_json.menu[self.menu_item],
        )
        await interaction.response.edit_message(view=food_view, embed=self.order_view.embed)


class OrderView(disnake.ui.View):
    """The view in which the order is displayed and managed by the user."""

    def __init__(self, restaurant: "Restaurant") -> None:
        """
        Initialize the order view.

        Args:
            restaurant (Restaurant): The restaurant.
        """
        super().__init__()
        self.restaurant = restaurant
        self.order = Order()
        for i, menu_item in enumerate(restaurant.menu):
            self.add_item(MenuSectionButton(restaurant, self, self.order, menu_item, i))

    @property
    def embed(self) -> disnake.Embed:
        """disnake.Embed: An embed for the order overview."""
        embed = disnake.Embed(
            title=f"{self.restaurant.icon} MENU: {self.restaurant.name} {self.restaurant.icon}",
            description=f"{self.restaurant.description} \n",
            colour=DISNAKE_COLORS.get(self.restaurant.icon, disnake.Color.random()),
        )
        # Adding an empty field for better formatting
        embed.add_field(" ", " ")
        # Adding already added menu items
        for menu_name, menu_items in self.order.foods.items():
            embed.add_field(
                name=f"Added {menu_name} items",
                value="\n".join(f"- `{item_name}`: {menu_items.count(item_name)}" for item_name in set(menu_items)),
                inline=False,
            )

        return embed

    @disnake.ui.button(label="Customer Information", style=disnake.ButtonStyle.success, row=2)
    async def _customer_information(self, _: disnake.ui.Button, interaction: disnake.MessageInteraction) -> None:
        await interaction.response.send_modal(CustomerInformationModal(self))

    @disnake.ui.button(label="Done", style=disnake.ButtonStyle.success, row=2)
    async def _order_done(self, _: disnake.ui.Button, interaction: disnake.MessageInteraction) -> None:
        # Warn user if customer information is missing.
        if not self.order.customer_information:
            embed = self.embed
            embed.insert_field_at(index=0, name=" ", value=" ", inline=False)
            embed.insert_field_at(
                index=1,
                name=":rotating_light: :warning: Error :warning: :rotating_light:",
                value="**Customer information missing!**",
                inline=False,
            )
            await interaction.response.edit_message(embed=embed, view=self)
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

        # Discarding Order in Background
        task = asyncio.create_task(self.restaurant.order_queue.discard_order(self.order.customer_information.order_id))
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)

        # Checking how long order completion took
        time_taken = (datetime.now(tz=UTC) - correct_order.order_timestamp).total_seconds()
        bonus_seconds = 60
        completion_message = ""
        if time_taken <= bonus_seconds:
            points += 5
            completion_message = "You've completed the order in under a minute and get 5 bonus points! \n"
        elif time_taken >= correct_order.penalty_seconds:
            points -= 5
            completion_message = "You've took to long to complete the order and receive a 5 points penalty! \n"

        add_points(interaction.user.id, points)

        # Adding info to embed
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
