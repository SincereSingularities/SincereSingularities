import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any, TypedDict

from db import ConnectError, DbClient


class OrderFormat(TypedDict):
    """Order format"""

    order_id: str
    name: str
    address: str
    delivery_time: str
    extra_information: str

class Orders:
    """Orders"""

    def __init__(self) -> None:
        self.client = DbClient()
        self.collection = self.client.db.orders.name
        if not self.client.is_connected():
            raise ConnectError("Not connected to the database")

    def add_order(self, data: OrderFormat) -> None:
        """Add order

        Args:
            data (OrderFormat): Order to add

        Returns:
            None
        """
        try:
            order = self.client.show_one(self.collection, {"order_id": data["order_id"]})
            if order:
                self.update_order(order["order_id"], data)
        except ValueError:
            self.client.add_element(self.collection, data)

    def add_many_orders(self, datas: Iterable[OrderFormat]) -> None:
        """Add many orders

        Args:
            datas (Iterable[OrderFormat]): Orders to add

        Returns:
            None
        """
        for data in datas:
            self.add_order(data)

    def update_order(self, order_id: str, data: dict[str, Any]) -> None:
        """Update order

        Args:
            order_id (str): Order id
            data (dict[str, Any]): Order data

        Returns:
            None
        """
        self.client.update_one(self.collection, {"order_id": order_id}, data)

    def delete_order(self, order_id: str) -> None:
        """Delete order

        Args:
            order_id (str): Order id

        Returns:
            None
        """
        self.client.delete_one(self.collection, {"order_id": order_id})


if __name__ == "__main__":
    order = Orders()

    path = Path(__file__).parent / "orders.json"
    with path.open("r") as f:
        orders = json.load(f)

    print(orders)
    order.update_order(
        "order124",
        {
            "name": "John Doe",
            "address": "1234 Main St",
            "delivery_time": "ASAP",
            "extra_information": "N/A",
        },
        )
