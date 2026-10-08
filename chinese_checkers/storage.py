"""Persistence of the existing JSON save format."""

import json
from pathlib import Path

from .board import Board


def _json_record(obj):
    """Keep object references inside the game and colors inside saved boards."""
    return obj.to_dict() if isinstance(obj, Board) else obj.__dict__


class GameStorage:
    def __init__(self, path="game_data.json"):
        self.path = Path(path)

    def exists(self):
        return self.path.is_file() and self.path.stat().st_size > 0

    def load(self):
        if not self.exists():
            return None
        with self.path.open(encoding="utf-8") as file:
            return json.load(file)

    def save(self, state):
        # Save colors at the JSON boundary, while the live board owns Balls.
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(state, file, default=_json_record)

    def clear(self):
        self.path.unlink(missing_ok=True)
