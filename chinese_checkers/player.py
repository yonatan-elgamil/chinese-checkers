"""Player identity, owned colors, and match statistics."""

from typing import List

class Player:
    """A human player or the computer, identified by the name 'computer'."""

    def __init__(self, name: str, number_wins: int, number_losses: int, color: List[str]):
        """Constructs a player with name attributes amount of wins and losses and game color"""
        self.name = name
        self.number_wins = number_wins
        self.number_losses = number_losses
        self.color = color

    def __str__(self) -> str:
        """Prints a player with name attributes amount of wins and losses and game color"""
        color_word = self.color[0]
        for i in range(1,len(self.color)):
            color_word = color_word+' ,'+self.color[i]
        word = self.name+' in color: '+color_word+' with: '+str(self.number_wins)+' wins and: '+str(self.number_losses)+' losses.'
        return word

    def get_name(self) -> str:
        """Returns the player name"""
        return self.name

    def get_number_wins(self) -> int:
        """Returns the player's number of wins"""
        return self.number_wins

    def get_number_losses(self) -> int:
        """Returns the player's number of losses"""
        return self.number_losses

    def get_color(self) -> List[str]:
        """Returns the color number of the player"""
        return self.color

    def set_number_wins(self, number_wins: int):
        """Gets a number of wins and replaces them with the current number"""
        self.number_wins = number_wins

    def set_number_losses(self, number_losses: int):
        """Gets a number of losses and replaces them with the current number"""
        self.number_losses = number_losses







