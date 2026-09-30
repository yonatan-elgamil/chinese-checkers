"""Turn-by-turn match controller shared by terminal and graphical interfaces."""

from dataclasses import dataclass
from typing import List, Optional, Tuple

from .game import Game, MatchProgress
from .player import Player

Coordinate = Tuple[int, int]
Move = Tuple[Coordinate, Coordinate]


@dataclass(frozen=True)
class SessionEvent:
    """A change an interface can display without changing the game rules."""

    kind: str
    message: str
    player: Optional[Player] = None
    move: Optional[Move] = None


class GameSession:
    """Advance a match one turn at a time, without asking for input or printing."""

    def __init__(self, game: Game):
        self.game = game
        self.progress: MatchProgress = game._load_progress()
        self.status = "playing"
        self.current_player: Optional[Player] = None
        self._events: List[SessionEvent] = []
        self._advance()

    def drain_events(self) -> List[SessionEvent]:
        """Return new events once, in the order they happened."""
        events = self._events[:]
        self._events.clear()
        return events

    def submit_move(self, move: Optional[Move]) -> None:
        """Apply a human or computer choice and prepare the next turn."""
        player = self._require_player()
        message = self.game.take_turn(player, move)
        self._events.append(SessionEvent("pass" if move is None else "move",
                                         message, player, move))
        self.complete_turn()

    def complete_turn(self) -> None:
        """Finish a turn already applied by the terminal compatibility API."""
        player = self._require_player()
        self.game._record_board_change()
        if self.game.is_win(player):
            self.game._record_winner(self.progress, player)
        self.progress.pending_players.pop(0)
        self.current_player = None
        self._advance()

    def _require_player(self) -> Player:
        if self.status != "playing" or self.current_player is None:
            raise RuntimeError("There is no active turn")
        return self.current_player

    def _finish(self, kind: str, message: str) -> None:
        self.status = kind
        self.current_player = None
        self._events.append(SessionEvent(kind, message))

    def _advance(self) -> None:
        """Prepare a turn, automatically passing players with no legal moves."""
        while self.status == "playing":
            if self.game.is_over():
                self._finish("finished", self.game.finish_match(self.progress))
                return
            if not self.progress.round_active:
                self.game._begin_round(self.progress)
            if not self.progress.pending_players:
                self.game._remove_round_winners(self.progress)
                continue
            if self.game._draw_reached(self.progress):
                self._finish("draw", self.game.finish_draw())
                return

            player = self.progress.pending_players[0]
            self.game._save_before_turn(self.progress, player)
            if self.game._has_no_moves(player):
                message = self.game.record_blocked_turn(player)
                self.game._record_board_change()
                self.progress.pending_players.pop(0)
                self._events.append(SessionEvent("blocked", message, player))
                continue

            self.current_player = player
            return
