"""A colored ball and its current board coordinate."""

from typing import Tuple


class Ball:
    """A colored ball; Game validates moves before updating its location."""

    def __init__(self, color: str, location: Tuple[int, int]):
        self.color = color
        self.location = location

    def __str__(self) -> str:
        return f"{self.color} ball at {self.location}"

    def get_location(self) -> tuple:
        """A program that returns the location of the ball"""
        return self.location

    def get_color(self) -> str:
        """A program that returns the color of the ball"""
        return self.color

    def is_possible_replaces(self, targer: Tuple[int, int]) -> bool:
        """"A program that checks if the replacement of the location
         is possible and returns true and false accordingly"""
        row = targer[0]
        col = targer[1]
        if row < 0 or col < 0:
            return False
        return True

    def replaces(self, targer: Tuple[int, int]) -> bool:
        """A program that replaces a bullet if it fails sends a false"""
        if self.is_possible_replaces(targer):
            self.location = targer
            return True
        else:
            return False
