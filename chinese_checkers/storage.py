"""Persistence of the existing JSON save format."""

import json
from pathlib import Path


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
        # The original project's board, ball, and player objects are simple
        # records; preserve their existing JSON representation for old saves.
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(state, file, default=lambda obj: obj.__dict__)

    def clear(self):
        self.path.unlink(missing_ok=True)
