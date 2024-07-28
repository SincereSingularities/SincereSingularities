import os
from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Any

from dotenv import load_dotenv
from pymongo import MongoClient, errors

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME") or "bot_db"
DB_URI = f"mongodb://{DB_HOST}:{DB_PORT}"
utc_timezone = UTC


class ConnectError(Exception):
    """Connection error"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class DbClient:
    """db client"""

    def __init__(self) -> None:
        self.connected = False
        try:
            self.client = MongoClient(DB_URI)
            self.connected = True
            self.client.server_info()
            self.db = self.client[DB_NAME]
            self.restaurants = self.db.restaurants
        except errors.ConnectionFailure as err:
            self.connected = False
            print(f"Error: {err}")
            raise err from None

    def is_connected(self) -> bool:
        """Check if connected

        Returns:
            bool: True if connected, False otherwise
        """
        return self.connected

    def add_element(self, collection: str, data: dict[str, Any]) -> None:
        """Add element

        Args:
            collection (str): Collection name
            data (dict[str, Any]): Data to add

        Returns:
            None
        """
        if not self.connected:
            raise ConnectError("Not connected to the database")

        name = data["name"]
        # Check if it already exists
        if not self.db[collection].find_one({"name": name}):
            current_time = datetime.now(utc_timezone)
            data["created_at"] = current_time
            data["updated_at"] = current_time
            self.db[collection].insert_one(data)

    def add_many(self, collection: str, datas: Iterable[Any]) -> None:
        """Add many elements

        Args:
            collection (str): Collection name
            datas (Iterable[Any]): list of Datas to add

        Returns:
            None
        """
        for data in datas:
            self.add_element(collection, data)

    def delete_all(self, collection: str) -> None:
        """Delete all elements

        Args:
            collection (str): Collection name

        Returns:
            None
        """
        if not self.connected:
            raise ConnectError("Not connected to the database")
        self.db[collection].delete_many({})

    def delete_many(self, collection: str, datas: Iterable[Any]) -> None:
        """Delete many elements

        Args:
            collection (str): Collection name
            datas (Iterable[Any]): list of datas to delete

        Returns:
            None
        """
        if not self.connected:
            raise ConnectError("Not connected to the database")

        for data in datas:
            if not self.show_one(collection, data):
                raise ValueError("Element not found")
            self.db[collection].delete_one(data)

    def delete_one(self, collection: str, data: dict[str, Any]) -> None:
        """Delete one element

        Args:
            collection (str): Collection name
            data (dict[str, Any]): Data to delete

        Returns:
            None
        """
        if not self.connected:
            raise ConnectError("Not connected to the database")
        if not self.show_one(collection, data):
            raise ValueError("Element not found")
        self.db[collection].delete_one(data)

    def show_all(self, collection: str) -> list[dict[str, Any]]:
        """Show all elements

        Args:
            collection (str): Collection name

        Returns:
            list[Any]: All elements in the collection
        """
        if not self.connected:
            raise ConnectError("Not connected to the database")

        elements = self.db[collection].find({})
        return [dict(element) for element in elements]

    def show_one(self, collection: str, data: dict[str, Any]) -> dict[str, Any]:
        """Show one element

        Args:
            collection (str): Collection name
            data (dict[str, Any]): Data to show

        Returns:
            dict[str, Any]: Element found
        """
        if not self.connected:
            raise ConnectError("Not connected to the database")

        element = self.db[collection].find_one(data)
        if not element:
            raise ValueError("Element not found")
        return dict(element)

    def update_one(
        self,
        collection: str,
        data: dict[str, Any],
        new_data: dict[str, Any],
        *,
        upsert: bool = False,
    ) -> None:
        """Update one element in the collection

        Args:
            collection (str): Collection name
            data (dict[str, Any]): Data to update
            new_data (dict[str, Any]): New data to update
            upsert (bool, optional): Whether to upsert. Defaults to False.

        Returns:
            None
        """
        if not self.connected:
            raise ConnectError("Not connected to the database")

        if not upsert:
            element = self.show_one(collection, data)

            if not element:
                raise ValueError("Element not found")

        current_time = datetime.now(utc_timezone)
        new_data["updated_at"] = current_time
        self.db[collection].update_one(data, {"$set": new_data}, upsert=upsert)

    def update_many(self, collection: str, datas: Iterable[Any], new_datas: Iterable[Any]) -> None:
        """Update many elements in the collection

        Args:
            collection (str): Collection name
            datas (Iterable[Any]): list of datas to update
            new_datas (Iterable[Any]): list of new datas to update

        Returns:
            None
        """
        if not self.connected:
            raise ConnectError("Not connected to the database")

        for data, new_data in zip(datas, new_datas, strict=False):
            if not self.show_one(collection, data):
                raise ValueError("Element not found")
            self.db[collection].update_one(data, {"$set": new_data})
