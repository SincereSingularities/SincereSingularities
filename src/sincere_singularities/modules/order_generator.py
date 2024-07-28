import random
import string
from datetime import UTC, datetime, timedelta
from enum import Enum, auto

from faker import Faker

from sincere_singularities.data.extra_wishes import EXTRA_WISHES_WITH_ADDITIONS
from sincere_singularities.data.intros_outros import INTROS, OUTROS
from sincere_singularities.data.noise import NOISE
from sincere_singularities.modules.coins import get_restaurant_by_name
from sincere_singularities.modules.order import CustomerInformation, Order


class Difficulty(Enum):
    """The difficulty of the game."""

    EASY = auto()
    MEDIUM = auto()
    HARD = auto()


ORDER_ID_CHARS = string.ascii_lowercase + string.digits
INITIAL_DISH_PROBABILITY = {
    Difficulty.EASY: {
        "Starters": 0.7,
        "Main Courses": 1,
        "Desserts": 0.6,
        "Drinks": 0.4,
    },
    Difficulty.MEDIUM: {
        "Starters": 0.9,
        "Main Courses": 1,
        "Desserts": 0.8,
        "Drinks": 0.7,
    },
    Difficulty.HARD: {
        "Starters": 1,
        "Main Courses": 1,
        "Desserts": 0.9,
        "Drinks": 0.8,
    },
}
MULTIPLE_DISH_PROBABILITY = {
    Difficulty.EASY: {
        "Starters": 0.2,
        "Main Courses": 0.1,
        "Desserts": 0.15,
        "Drinks": 0.05,
    },
    Difficulty.MEDIUM: {
        "Starters": 0.3,
        "Main Courses": 0.2,
        "Desserts": 0.35,
        "Drinks": 0.1,
    },
    Difficulty.HARD: {
        "Starters": 0.5,
        "Main Courses": 0.6,
        "Desserts": 0.75,
        "Drinks": 0.2,
    },
}
CUSTOMER_INFORMATION_PROBABILITY = {
    Difficulty.EASY: {
        "Time": 0.4,
        "Extra Wish": 0.3,
    },
    Difficulty.MEDIUM: {
        "Time": 0.6,
        "Extra Wish": 0.5,
    },
    Difficulty.HARD: {
        "Time": 0.9,
        "Extra Wish": 0.7,
    },
}

fake = Faker()


def _generate_delivery_time() -> str:
    # Get the current time
    now = datetime.now(tz=UTC)
    # Generate a time within the next 30 - 120 Minutes
    random_hour_increment = random.randint(30, 120)
    time = now + timedelta(minutes=random_hour_increment)

    # Match-case statement to generate the corresponding time description (With Probabilities weight)
    match random.random():
        case p if p < 0.35:
            # 24-hour format (e.g. 19:00)
            time_description = time.strftime("%H:%M")
        case p if 0.35 <= p < 0.7:
            # 12-hour format (e.g. 7:00 pm)
            time_description = time.strftime("%I:%M %p").lower()
        case p if 0.7 <= p < 0.85:
            # O'clock format (7 o'clock)
            time_oclock = time.strftime("%I").replace(" 0", " ").replace(":00", "").lower()
            time_description = f"{time_oclock} o'clock"
        case _:
            # Period format (7 in the evening)
            hour = time.hour
            if 0 <= hour < 12:
                period = "in the morning"
            elif 12 <= hour < 18:
                period = "in the afternoon"
            else:
                period = "in the evening"
            time_period = time.strftime("%I").lstrip("0")
            time_description = f"{time_period} {period}"

    return time_description


class OrderGenerator:
    """The OrderGenerator Class to generate Randomized Order Information and Noised Order Descriptions"""

    def __init__(self, difficulty: Difficulty) -> None:
        self.difficulty = difficulty

    @property
    def delivery_time_probability(self) -> float:
        """float: The probability of delivery time being specified."""
        return CUSTOMER_INFORMATION_PROBABILITY[self.difficulty]["Time"]

    @property
    def extra_wish_probability(self) -> float:
        """float: The probability of an extra wish being specified."""
        return CUSTOMER_INFORMATION_PROBABILITY[self.difficulty]["Extra Wish"]

    def generate(self, restaurant_name: str) -> tuple[Order, str]:
        """
        Generate a new Random Order and an Order Description.

        Args:
            restaurant_name (str): The name of the restaurant as it appears in `restaurants.json`.

        Returns:
            tuple[Order, str]: The generated Order Object and The Order Description in text form.
        """
        # Generation of all the order data
        order = Order(
            restaurant_name=restaurant_name,
        )

        # Randomize if Extra Wish should be added
        has_delivery_time = random.random() < self.delivery_time_probability
        has_extra_wish = random.random() < self.extra_wish_probability
        extra_wish = random.choice(list(EXTRA_WISHES_WITH_ADDITIONS.keys()))

        # Generating Customer Information
        order.customer_information = CustomerInformation(
            # Getting a Random 4 Char OrderID
            order_id="".join(random.sample(ORDER_ID_CHARS, 4)),
            # Random (Faker) Name
            name=fake.name(),
            # Random (Faker) Address Format: `Number StreetName`
            address=fake.street_address(),
            # Randomly Formatted Delivery Time if applicable
            delivery_time=_generate_delivery_time() if has_delivery_time else "",
            # Random Extra Wish if applicable
            extra_wish=extra_wish if has_extra_wish else "",
        )
        # Generating Foods
        order = self._generate_menu(order, restaurant_name)
        # Generating Order Description
        order_description = self._generate_order_description(order, has_delivery_time, has_extra_wish)

        return order, order_description

    def _generate_menu(self, order: Order, restaurant_name: str) -> Order:
        restaurant = get_restaurant_by_name(restaurant_name)
        # Get Probability to Generate Multiple Dishes in one Order
        multiple_dish_probabilities = MULTIPLE_DISH_PROBABILITY[self.difficulty]

        # Looping through the Menu Sections
        for dish_type in ("Starters", "Main Courses", "Desserts", "Drinks"):
            if random.random() > INITIAL_DISH_PROBABILITY[self.difficulty][dish_type]:
                continue

            while True:
                # Choose a Random Dish from Menu Section
                chosen_dish = random.choice(restaurant.menu[dish_type])
                # Adding one Menu Item of type chosen_dish
                order.foods[dish_type].append(chosen_dish)
                # Deciding whether to add more Dishes or not
                add_another_dish = random.random() <= multiple_dish_probabilities[dish_type]
                if not add_another_dish:
                    break

        return order

    def _generate_order_paragraph(self, order_description: str, paragraph: list[str]) -> str:
        # Adding Noise (Quantity) based on Difficulty
        noise_quantity = 0
        if self.difficulty == Difficulty.MEDIUM:
            noise_quantity = random.randint(0, 2)
        elif self.difficulty == Difficulty.HARD:
            noise_quantity = random.randint(1, 5)

        # Adding Noise to Paragraph
        for i in range(noise_quantity):
            # Only generate `relevant_noise` if the noise_quantity is more than 0
            if i:
                paragraph.append(random.choice(NOISE.relevant_noise))
            else:
                paragraph.append(random.choice(NOISE.noise))

        # Shuffling Items on harder difficulties
        if self.difficulty != Difficulty.EASY:
            random.shuffle(paragraph)
        # Joining together to a complete Paragraph.
        order_description += " ".join(paragraph) + "\n"

        return order_description

    @staticmethod
    def _generate_menu_items_description(
        order: Order,
        order_description: str,
        menu_section: str,
        string_template: str,
    ) -> str:
        # Getting Non-Duplicate Set of Menu Section Items
        menu_section_set = set(order.foods[menu_section])
        # Adding Formatted Menu Section Items to Order Description
        return order_description.replace(
            string_template,
            " and ".join(f"{order.foods[menu_section].count(item)} {item}" for item in menu_section_set),
        )

    def _generate_order_description(self, order: Order, has_delivery_time: bool, has_extra_wish: bool) -> str:
        # We'll add the Order Description to this string
        assert order.customer_information
        order_description = f":id: **Customer ID:** `{order.customer_information.order_id}`\n\n"
        # Whether to have the Customer Name in the Introduction
        customer_name_in_intro = random.randint(0, 1)

        # Generating Embeddable Noise Fillers, which are string templates which
        # we can inject the Customer Information into
        address_template = random.choice(NOISE.embeddable_noise.addresses)
        restaurant_name_template = random.choice(NOISE.embeddable_noise.restaurants)
        delivery_time_template = random.choice(NOISE.embeddable_noise.times) if has_delivery_time else ""
        # Menu Templates
        starters_menu_template = random.choice(NOISE.embeddable_noise.foods.starters)
        main_courses_menu_template = random.choice(NOISE.embeddable_noise.foods.main)
        desserts_menu_template = random.choice(NOISE.embeddable_noise.foods.desserts)
        drinks_menu_template = random.choice(NOISE.embeddable_noise.foods.drinks)

        # Introduction (potentially with the Customer Name)
        if customer_name_in_intro:
            order_description += random.choice(INTROS["intros_with_name"]) + " "
        else:
            order_description += random.choice(INTROS["intros_without_name"]) + " "

        # Description Paragraph
        description_paragraph = [
            restaurant_name_template,  # Restaurant mame
            delivery_time_template,  # Delivery time
            address_template,  # Address
        ]
        # Generate Order Description for Description Paragraph
        order_description = self._generate_order_paragraph(order_description, description_paragraph)
        order_description += "\n"

        # Menu Items paragraph
        menu_items_paragraph = [
            starters_menu_template if order.foods["Starters"] else "",  # Starters
            (main_courses_menu_template if order.foods["Main Courses"] else ""),  # Main Courses
            desserts_menu_template if order.foods["Desserts"] else "",  # Desserts
            drinks_menu_template if order.foods["Drinks"] else "",  # Drinks
        ]
        # Generate Order Description for Menu Items Paragraph
        order_description = self._generate_order_paragraph(order_description, menu_items_paragraph)

        # Outro (Check if Customer Name was already mentioned in the Intro)
        if not customer_name_in_intro:
            order_description += random.choice(OUTROS["outros_with_name"])
        else:
            order_description += random.choice(OUTROS["outros_without_name"])

        # Format the Final Description, Replace Template Strings with actual Order Information
        assert order.restaurant_name
        order_description = order_description.replace("<RESTAURANT>", order.restaurant_name)

        # Formatting Customer Information
        order_description = order_description.replace("<NAME>", order.customer_information.name)
        order_description = order_description.replace("<ADDRESS>", order.customer_information.address)
        if has_delivery_time:
            order_description = order_description.replace("<TIME>", order.customer_information.delivery_time)

        # Adding Starters
        order_description = self._generate_menu_items_description(order, order_description, "Starters", "<STARTERS>")
        # Adding Main Courses
        order_description = self._generate_menu_items_description(order, order_description, "Main Courses", "<MAIN>")
        # Adding Desserts
        order_description = self._generate_menu_items_description(order, order_description, "Desserts", "<DESSERTS>")
        # Adding Drinks
        order_description = self._generate_menu_items_description(order, order_description, "Drinks", "<DRINKS>")

        # Adding Extra Wish (if applicable)
        if has_extra_wish:
            extra_wish = EXTRA_WISHES_WITH_ADDITIONS[order.customer_information.extra_wish]
            order_description += f"\n:information_source: Customer Added: `{extra_wish}`"

        return order_description
