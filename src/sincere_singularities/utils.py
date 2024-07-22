import json
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias, TypeVar

import dacite

CURRENT_DIR = Path(__file__).parent.absolute()


@dataclass(unsafe_hash=True)
class RestaurantJson:
    """Represents a JSON-like object representing a Restaurant."""

    name: str
    icon: str
    description: str
    color: str
    menu: dict[str, list[str]]


RestaurantJsonType: TypeAlias = list[RestaurantJson]
T = TypeVar("T", bound=RestaurantJsonType)


def load_json(filename: str, json_type: type[T]) -> T:
    """
    Helper for Loading a Json File

    Args:
        filename: Filename, e.g. myfile.json
        json_type: Json Type

    Returns: JsonType

    """
    json_filepath = CURRENT_DIR / "data" / filename
    with json_filepath.open(mode="r", encoding="utf-8") as f:
        loaded_json = json.load(f)
        typed_json: T = dacite.from_dict(json_type, loaded_json)

        return typed_json
