import json
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias, TypeVar, get_args, get_origin

import dacite

CURRENT_DIR = Path(__file__).parent.absolute()


@dataclass(unsafe_hash=True)
class RestaurantJson:
    """Represents a JSON-like object representing a Restaurant."""

    name: str
    icon: str
    description: str
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
    # Opening the FilePath which is found under ./data/...
    json_filepath = CURRENT_DIR / "data" / filename
    with json_filepath.open(mode="r", encoding="utf-8") as f:
        loaded_json = json.load(f)

        if isinstance(loaded_json, list) and get_origin(json_type) is list:
            # This gets the Class Type of the first element of json_type
            # Note: We can assume the json_type list only has one element
            obj_type = get_args(json_type)[0]

            # Applying the Dataclass to every Object in the List.
            typed_objs: T = [dacite.from_dict(obj_type, obj) for obj in loaded_json]  # type: ignore[assignment]
            return typed_objs

        # Applying the Dataclass to the loaded_json
        typed_json: T = dacite.from_dict(json_type, loaded_json)

        return typed_json
