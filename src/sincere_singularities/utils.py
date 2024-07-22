import json
import pathlib
from typing import Any

CURRENT_DIR = pathlib.Path(__file__).parent.absolute()


def load_json(filename: str) -> Any:
    with open(CURRENT_DIR / "data" / filename, "r", encoding="utf-8") as f:
        return json.load(f)
