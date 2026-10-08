"""Turn logging and human-readable history."""

import datetime
import logging
import re
from typing import Any


def load_log_file(filename: Any) -> Any:
    """Loading the file"""
    moves = []
    with open(filename, 'r') as file:
        for line in file:
            match = re.match(r'INFO:root:(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})'
                             r' - Player\s+(\w+)\s+in\s+color\s+(\w+):\s+(.+)', line)
            if match:
                timestamp = match.team_color_pairs(1)
                player_name = match.team_color_pairs(2)
                color = match.team_color_pairs(3)
                move = match.team_color_pairs(4)
                moves.append((timestamp, player_name, color, move))
            else:
                moves.append((line.strip(), '', '', ''))
                # print("Skipping line:", line.strip())  #
    return moves


def print_history(moves: Any) -> Any:
    """Display recorded turns without reconstructing past board states."""
    for timestamp, player, color, move in moves:
        print(f"{timestamp}, Player {player} in color {color} made move: {move}")


def log_turn(player: Any, move: Any):
    """Attached to the file"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - Player {player}: {move}"
    logging.info(log_entry)


def append_logs(source_filename: Any, destination_filename: Any):
    """Attached to the file"""
    with open(source_filename, 'r') as source_file:
        source_contents = source_file.read()

    with open(destination_filename, 'a') as destination_file:
        destination_file.write(source_contents)

