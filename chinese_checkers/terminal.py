"""Terminal input for a human turn. Coordinates shown to players are 1-based."""

from .utils import is_valid_coordinate_input
from .session import GameSession


def _coordinate(prompt):
    while True:
        value = input(prompt)
        if is_valid_coordinate_input(value):
            row, column = map(int, value.split(","))
            return row - 1, column - 1


def prompt_human_move(game, player):
    """Return (source, target), or None when the player passes."""
    print(game.board)
    name = player.get_name()
    first = input(f"{name}, choose a ball (row,column) or type 'pass': ")
    if first == "pass":
        return None
    while True:
        if is_valid_coordinate_input(first):
            row, column = map(int, first.split(","))
            source = (row - 1, column - 1)
            if source in game.positions_for_player(player) and game.board.legal_destinations(source):
                break
        first = input("Choose one of your balls with at least one legal move: ")
    while True:
        target = _coordinate("Choose a legal target (row,column): ")
        if target in game.board.legal_destinations(source):
            return source, target
        print("That target is not a legal move.")


def play_single_turn(game, player):
    """Ask a human or the computer for a move and display a successful move."""
    move = (game.computer_strategy.choose_move(player) if player.get_name() == "computer"
            else prompt_human_move(game, player))
    game.take_turn(player, move)
    if move is not None:
        print(game.board)


def _offer_history(game, prompt="Type 'want' to see the turn history: "):
    if input(prompt) == "want":
        game.print_history(game.load_log_file(game.checkers_log_path))


def play_game(game):
    """Drive the shared session with terminal input and output."""
    session = GameSession(game)
    while True:
        for event in session.drain_events():
            if event.kind == "blocked":
                if event.player.get_name() != "computer":
                    _offer_history(
                        game, event.player.get_name() +
                        " if you want to see the turn history type 'want': "
                    )
                print(event.message)
            elif event.kind in ("draw", "finished"):
                print(game.board)
                print(event.message)
                _offer_history(game)
        if session.status != "playing":
            return
        game.play_terminal_turn(session.current_player)
        session.complete_turn()
