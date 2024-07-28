import json
import pathlib
from collections.abc import Iterable
from typing import Any, TypedDict

from db import ConnectError, DbClient


class StateFormat(TypedDict):
    """Sate format"""

    player_id: str
    state: dict[str, Any]


class SaveStates:
    """Save states"""

    def __init__(self) -> None:
        self.client = DbClient()
        self.client.db.states.create_index("player_id", unique=True)
        self.collection = self.client.db.states.name
        if not self.client.is_connected():
            raise ConnectError("Not connected to the database")

    def add_user_state(self, data: StateFormat) -> None:
        """Add state

        Args:
            data (StateFormat): State to add

        Returns:
            None
        """
        try:
            user = self.client.show_one(self.collection, {"player_id": data["player_id"]})
            if user:
                self.save_game_state(user["player_id"], data["state"])

        except ValueError:
            self.client.add_element(self.collection, data)

    def add_many_user_states(self, datas: Iterable[StateFormat]) -> None:
        """Add many states

        Args:
            datas (Iterable[StateFormat]): States to add

        Returns:
            None
        """
        for data in datas:
            self.add_user_state(data)

    def save_game_state(self, player_id: str, state: dict[str, Any]) -> None:
        """Save state

        Args:
            player_id (str): User id
            state (str): State

        Returns:
            None
        """
        if not self.client.show_one(self.collection, {"player_id": player_id}):
            self.add_user_state({"player_id": player_id, "state": state})
            return
        self.client.update_one(self.collection, {"player_id": player_id}, {"$set": {"state": state}})

    def load_game_state(self, player_id: str) -> dict[str, Any]:
        """Get states

        Returns:
            dict[str, Any]: List of states
        """
        return dict(self.client.show_one(self.collection, {"player_id": player_id}))

    def load_all_user_states(self) -> Iterable[Any]:
        """Get states

        Returns:
            Iterable[Any]: List of states
        """
        return list(self.client.show_all(self.collection))

    def delete_state(self, player_id: str) -> None:
        """Delete state

        Args:
            player_id (str): State id

        Returns:
            None
        """
        self.client.delete_one(self.collection, {player_id: player_id})


if __name__ == "__main__":
    save_states = SaveStates()
    path = pathlib.Path(__file__).parent / "states.json"

    with path.open("r") as file:
        states = json.load(file)

    save_states.add_many_user_states(states)
    print(save_states.load_all_user_states())
    data: StateFormat = {
        "player_id": "user123",
        "state": {"level": 2, "score": 10},
    }
    save_states.add_user_state(data)
    save_states.save_game_state("user123", {"score": 1.5, "level": 2})
    save_states.save_game_state("player457", {"score": 1.5, "level": 2})
