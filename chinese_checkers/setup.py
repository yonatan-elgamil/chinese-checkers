"""Build a ready match from options, or restore one from saved JSON."""

from . import utils
from .ball import Ball
from .board import Board
from .game import Game
from .player import Player

COLORS = ("R", "B", "G", "Y", "P", "W")
PLAYER_COUNTS = (2, 3, 4, 6)
# Every corner is used once. The first two colors in a two-player match
# start opposite one another; four-player teams also occupy opposite corners.
STARTING_CORNERS = {
    (2, 1): (("N",), ("S",)),
    (2, 2): (("N", "NE"), ("S", "SW")),
    (2, 3): (("N", "NE", "SE"), ("S", "SW", "NW")),
    (3, 1): (("N",), ("SE",), ("SW",)),
    (3, 2): (("N", "S"), ("NE", "SW"), ("SE", "NW")),
    (4, 1): (("NE",), ("SE",), ("SW",), ("NW",)),
    (6, 1): (("N",), ("NE",), ("SE",), ("S",), ("SW",), ("NW",)),
}


class SetupOptions:
    """Validated, read-only match options implemented as an ordinary class."""

    def __init__(self, size, player_count, computer_count, sets_per_player, teams):
        self._size = size
        self._player_count = player_count
        self._computer_count = computer_count
        self._sets_per_player = sets_per_player
        self._teams = teams
        self._validate()

    @property
    def size(self):
        return self._size

    @property
    def player_count(self):
        return self._player_count

    @property
    def computer_count(self):
        return self._computer_count

    @property
    def sets_per_player(self):
        return self._sets_per_player

    @property
    def teams(self):
        return self._teams

    def _values(self):
        return (self.size, self.player_count, self.computer_count,
                self.sets_per_player, self.teams)

    def __eq__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self._values() == other._values()

    def __hash__(self):
        return hash(self._values())

    def __repr__(self):
        return (f"SetupOptions(size={self.size}, player_count={self.player_count}, "
                f"computer_count={self.computer_count}, sets_per_player={self.sets_per_player}, "
                f"teams={self.teams})")

    def _validate(self):
        valid_size = (isinstance(self.size, int) and not isinstance(self.size, bool)
                      and self.size >= 4 and (self.size - 1) % 3 == 0)
        if not valid_size:
            raise ValueError("Board size must be 4, 7, 10, ...")
        if type(self.player_count) is not int or self.player_count not in PLAYER_COUNTS:
            raise ValueError("Choose 2, 3, 4 or 6 players")
        if (type(self.computer_count) is not int or
                not 0 <= self.computer_count < self.player_count):
            raise ValueError("At least one player must be human")
        if (type(self.sets_per_player) is not int or
                (self.player_count, self.sets_per_player) not in STARTING_CORNERS):
            raise ValueError("Invalid number of color sets for this player count")
        if self.teams not in (0, 1) or self.teams and self.player_count not in (4, 6):
            raise ValueError("Teams are available only for 4 or 6 players")

    @property
    def triangle_type(self):
        return 2 if self.player_count == 2 and self.sets_per_player == 1 else 1

    @property
    def balls_per_color(self):
        side = (self.size - 1) // 3
        count = side * (side + 1) // 2
        if self.triangle_type == 2:
            count += side + 1
        return count


def _ask_number(prompt, valid):
    while True:
        answer = input(prompt)
        if answer.isdecimal() and valid(int(answer)):
            return int(answer)
        print("Please enter a valid number.")


def _ask_options():
    size = _ask_number("Board size (4, 7, 10, ...): ",
                       lambda value: value >= 4 and (value - 1) % 3 == 0)
    players = _ask_number("How many players (2, 3, 4, 6)?: ",
                          lambda value: value in (2, 3, 4, 6))
    computers = _ask_number("How many computer players?: ",
                            lambda value: 0 <= value < players)
    sets = 1
    if players in (2, 3):
        max_sets = 3 if players == 2 else 2
        sets = _ask_number(f"Sets per player (1-{max_sets})?: ",
                           lambda value: 1 <= value <= max_sets)
    teams = 0
    if players in (4, 6):
        teams = _ask_number("Play in teams? 1=yes, 0=no: ",
                            lambda value: value in (0, 1))
        if teams:
            print("Players in opposite starting corners form a team.")
    return SetupOptions(size, players, computers, sets, teams)


def _player_name(index, used_names):
    while True:
        name = input(f'Player {index + 1}, enter your name: ').strip()
        if name and name.casefold() != 'computer' and name.casefold() not in used_names:
            used_names.add(name.casefold())
            return name
        print("Choose a unique name other than 'computer'.")


def build_game(options: SetupOptions, human_names, store=None) -> Game:
    """Assign colors/corners and fill every starting triangle automatically."""
    names = [name.strip() for name in human_names]
    human_count = options.player_count - options.computer_count
    unique_names = {name.casefold() for name in names}
    if (len(names) != human_count or any(not name or name.casefold() == "computer"
                                         for name in names) or len(unique_names) != human_count):
        raise ValueError("Supply a unique, nonempty name for each human player")

    board = Board(options.size)
    triangles = board.triangle_cells(options.triangle_type)
    balls = {}
    players = []
    directions = {}
    color_index = 0
    arrangement = STARTING_CORNERS[options.player_count, options.sets_per_player]
    for index, corners in enumerate(arrangement):
        player_colors = []
        for direction in corners:
            color = COLORS[color_index]
            color_index += 1
            pieces = [Ball(color, location) for location in triangles[direction]]
            if len(pieces) != options.balls_per_color:
                raise ValueError("Starting triangle has an unexpected size")
            for piece in pieces:
                if not board.add_ball_to_triangle(piece, direction, options.triangle_type):
                    raise ValueError("Starting triangles overlap")
            balls[color] = pieces
            directions[color] = direction
            player_colors.append(color)
        name = names[index] if index < human_count else "computer"
        players.append(Player(name, 0, 0, player_colors))
    return Game(board, balls, players, options.teams, color_directions=directions, store=store)


def new_game():
    """Ask for match options and names; construct the initial board itself."""
    options = _ask_options()
    used_names = set()
    names = [_player_name(index, used_names)
             for index in range(options.player_count - options.computer_count)]
    game = build_game(options, names)
    print("Starting board (colors and pieces placed automatically):")
    print(game.board)
    return game


def restore_game(data, store=None):
    """Recreate domain objects and the next player from an existing save."""
    saved_board = data["board"]
    board = Board(int(saved_board["size"]))
    balls = {
        color: [Ball(color, tuple(item["location"])) for item in pieces]
        for color, pieces in data["balls"].items()
    }
    board.load_color_grid(saved_board["br"], balls)
    saved_players = data["players"]
    if data.get("pending_colors"):
        next_colors = data["pending_colors"][0]
        first = next(index for index, item in enumerate(saved_players)
                     if item["color"] == next_colors)
        saved_players = saved_players[first:] + saved_players[:first]
    else:
        # Older saves only recorded the name of the next player.
        saved_players = utils.rearrange_list(saved_players, data["playr"])
    players = [
        Player(item["name"], int(item["number_wins"]),
               int(item["number_losses"]), item["color"])
        for item in saved_players
    ]
    return Game(board, balls, players, int(data["is_group"]),
                color_directions=data.get("dic_color_loc"), store=store)
