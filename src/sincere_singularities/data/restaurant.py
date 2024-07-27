import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any, TypedDict

from db import ConnectError, DbClient


class RestaurantFormat(TypedDict):
    """Restaurant format"""
    name: str
    icon: str
    description: str
    points: int
    order_amount: int
    menu: dict[str, Any]


class Restaurants:
    """restaurants"""
    def __init__(self) -> None:
        self.client = DbClient()
        self.collection = self.client.db.restaurants.name
        if not self.client.is_connected():
            raise ConnectError("Not connected to the database")

    def add_restaurant(self, data: RestaurantFormat) -> None:
        """Add restaurant

        Args:
            data (RestaurantFormat): Restaurant to add

        Returns:
            None
        """
        try:
            restaurant = self.client.show_one(self.collection, {"name": data["name"]})
            if restaurant:
                self.update_restaurant(restaurant["name"], data)
        except ValueError:
            self.client.add_element(self.collection, data)

    def add_many_restaurants(self, datas: Iterable[RestaurantFormat]) -> None:
        """Add many restaurants

        Args:
            datas (Iterable[RestaurantFormat]): Restaurants to add

        Returns:
            None
        """
        for data in datas:
            self.add_restaurant(data)

    def update_restaurant(self, name: str, data: dict[str, Any]) -> None:
        """Update restaurant

        Args:
            name (str): Restaurant name
            data (dict[str, Any]): Restaurant data

        Returns:
            None
        """
        self.client.update_one(self.collection, {"name": name}, data)

    def delete_restaurant(self, data: RestaurantFormat) -> None:
        """Delete restaurant

        Args:
            data (RestaurantFormat): Restaurant to delete

        Returns:
            None
        """
        self.client.delete_one(self.collection, data)

    def delete_many_restaurants(self, datas: Iterable[RestaurantFormat]) -> None:
        """Delete many restaurants

        Args:
            datas (Iterable[RestaurantFormat]): Restaurants to delete

        Returns:
            None
        """
        for data in datas:
            self.delete_restaurant(data)

    def delete_all_restaurants(self) -> None:
        """Delete all restaurants

        Returns:
            None
        """
        self.client.delete_all(self.collection)

    def show_restaurant(self, name: str) -> dict[str, Any]:
        """Show restaurant

        Args:
            name (str): Restaurant name

        Returns:
            dict[str, Any]: Restaurant data
        """
        return self.client.show_one(self.collection, {"name": name})

if __name__ == "__main__":
    db = DbClient()
    path = Path(__file__).parent / "restaurants.json"

    with path.open() as f:
        restaurants = json.load(f)

    db.add_many("restaurants", restaurants)
    print(db.show_all("restaurants"))

    print(db.show_all("restaurants"))
