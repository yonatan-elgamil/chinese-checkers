"""Player identity, owned colors, and match statistics."""

from typing import List


class Player:
    """A human player or the computer, identified by the name 'computer'."""

    def __init__(self, name: str, number_wins: int, number_losses: int, color: List[str]):
        """Store a player name, owned colors and match statistics."""
        self.name = name
        self.number_wins = number_wins
        self.number_losses = number_losses
        self.color = color

    def __str__(self) -> str:
        """Describe the player, owned colors and win/loss statistics."""
        color_word = self.color[0]
        for i in range(1,len(self.color)):
            color_word = color_word+' ,'+self.color[i]
        word = self.name+' in color: '+color_word+' with: '+str(self.number_wins)+' wins and: '+str(self.number_losses)+' losses.'
        return word

    def get_name(self) -> str:
        """Returns the player name"""
        return self.name

    def get_wins(self) -> int:
        """Returns the player's number of wins"""
        return self.number_wins

    def get_losses(self) -> int:
        """Returns the player's number of losses"""
        return self.number_losses

    def get_colors(self) -> List[str]:
        """Return all colors owned by this player."""
        return self.color

    def set_wins(self, number_wins: int):
        """Update the recorded number of wins."""
        self.number_wins = number_wins

    def set_losses(self, number_losses: int):
        """Update the recorded number of losses."""
        self.number_losses = number_losses

