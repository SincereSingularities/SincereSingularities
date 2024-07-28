from collections import defaultdict
from collections.abc import Iterable
from typing import Any, TypedDict

from sincere_singularities.data.db import ConnectError, DbClient
from sincere_singularities.utils import RESTAURANT_JSON


class State(TypedDict):
    """A user's game state."""

    coins: int
    restaurants: list[str]
    number_of_orders: dict[str, int]


class StateFormat(TypedDict):
    """Sate format"""

    player_id: str
    state: State


def generate_default_state() -> State:
    """
    Generate a default state for each user when they start the game for the first time.

    Returns:
        State: The default starter state.
    """
    return State(
        coins=0,
        restaurants=[RESTAURANT_JSON[0].name],
        number_of_orders=defaultdict(int),
    )


class SaveStates:
    """Save states"""

    def __init__(self) -> None:
        self.client = DbClient()
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
            self.client.add_element(self.collection, dict(data))

    def add_many_user_states(self, datas: Iterable[StateFormat]) -> None:
        """Add many states

        Args:
            datas (Iterable[StateFormat]): States to add

        Returns:
            None
        """
        for data in datas:
            self.add_user_state(data)

    def save_game_state(self, player_id: int, state: State) -> None:
        """Save state

        Args:
            player_id (int): User id
            state (State): State

        Returns:
            None
        """
        self.client.update_one(self.collection, {"player_id": player_id}, {"state": state}, upsert=True)

    def load_game_state(self, player_id: int) -> State:
        """Get state

        Args:
            player_id (int): User id

        Returns:
            State: The user's state.
        """
        state_dict = self.client.show_one(self.collection, {"player_id": player_id})["state"]
        return State(
            coins=state_dict["coins"],
            restaurants=state_dict["restaurants"],
            number_of_orders=state_dict["number_of_orders"],
        )

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
