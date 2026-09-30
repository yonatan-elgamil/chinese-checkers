"""Terminal entry point: setup, resume, and history prompts."""

import argparse
import logging
from pathlib import Path

from . import logs
from .setup import new_game, restore_game
from .storage import GameStorage


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Play Chinese checkers in the terminal (2, 3, 4 or 6 players).",
        epilog=("Use 1-based row,column coordinates and N/NE/SE/S/SW/NW directions. "
                "Players can enter 'pass' at the start of a turn. "
                "Run without options to set up a match or resume a saved one."),
    )
    parser.parse_args(argv)

    logging.basicConfig(filename="checkers.log", level=logging.INFO)
    store = GameStorage()
    while True:
        saved = store.load()
        if saved and saved.get("started") == 1 and saved.get("end") == 0:
            choice = input("An unfinished game exists. Type 'want' to resume: ")
            if choice == "want":
                game = restore_game(saved)
            else:
                store.clear()
                Path("checkers.log").write_text("")
                game = new_game()
        else:
            store.clear()
            Path("checkers.log").write_text("")
            game = new_game()

        game.play()
        if Path("checkers.log").exists():
            logs.append_logs("checkers.log", "all_checkers.log")
        if input("Type 'go' to play another game, otherwise press Enter: ") != "go":
            return
        if input("Type 'want' to see the history of all games: ") == "want":
            logs.print_history(logs.load_log_file("all_checkers.log"))
