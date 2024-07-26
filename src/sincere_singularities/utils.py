import difflib
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias, TypeVar, get_args, get_origin

import dacite
import disnake
import torch
from sentence_transformers import SentenceTransformer, util

CURRENT_DIR = Path(__file__).parent.absolute()
DISNAKE_COLORS = {
    ":pizza:": disnake.Color.from_rgb(229, 97, 38),
    ":sushi:": disnake.Color.from_rgb(255, 153, 153),
}

# Use GPU if available
device = "cuda" if torch.cuda.is_available() else "cpu"
# Load the MiniLM SentenceTransformer Model
minilm_model = SentenceTransformer("all-MiniLM-L6-v2", device=device)


@dataclass(unsafe_hash=True)
class RestaurantJson:
    """Represents a JSON-like object representing a Restaurant."""

    name: str
    icon: str
    description: str
    points: int
    order_amount: int
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


def check_pattern_similarity(first: str, second: str) -> float:
    """
    Measure of the strings' similarity as a float using Gestalt Pattern Matching Algorithm.

    Args:
        first (str): The first string.
        second (str): The second string.

    Returns:
        float: The similarity of the two strings [0, 1]
    """
    return difflib.SequenceMatcher(None, first, second).ratio()


def compare_sentences(first: str, second: str) -> float:
    """
    Measure of the strings' similarity as a float using Sentence Transformer's MiniLM.

    Args:
        first (str): The first string.
        second (str): The second string.

    Returns:
        float: The similarity of the two strings [0, 1]
    """
    # Encode sentences in batch to speed up the process
    embeddings = minilm_model.encode([first, second], convert_to_tensor=True, device=device)
    # Check Similarity using Cosine Similarity
    similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1])
    return similarity.item()  # type: ignore[no-any-return]


def generate_random_avatar_url() -> str:
    """
    Generate a random avatar image URL.

    Returns:
        str: A random image URL.
    """
    seed = random.random()
    flip = random.choice(("true", "false"))
    background_color = hex(random.randrange(0x000000, 0xFFFFFF))[2:].zfill(6)
    return f"https://api.dicebear.com/9.x/notionists/svg?seed={seed}&flip={flip}&backgroundColor={background_color}"
