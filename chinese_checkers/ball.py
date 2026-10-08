"""A colored ball and its current board coordinate."""

from typing import Tuple


class Ball:
    """A colored ball; Game validates moves before updating its location."""

    def __init__(self, color: str, location: Tuple[int, int]):
        self.color = color
        self.location = location

    def __str__(self) -> str:
        return f"{self.color} ball at {self.location}"

    def get_position(self) -> tuple:
        """Return the current board coordinate."""
        return self.location

    def get_color(self) -> str:
        """Return the piece color."""
        return self.color

    def can_move_to(self, target: Tuple[int, int]) -> bool:
        """Check nonnegative coordinates; Board owns movement legality."""
        row = target[0]
        col = target[1]
        if row < 0 or col < 0:
            return False
        return True

    def move_to(self, target: Tuple[int, int]) -> bool:
        """Update the position if both coordinates are nonnegative."""
        if self.can_move_to(target):
            self.location = target
            return True
        else:
            return False
