"""Game state, legal turn execution, victory and turn order."""

from typing import Any, Dict, List, Tuple
import copy
from dataclasses import dataclass, field

from .player import Player
from .ball import Ball
from .board import Board
from . import utils as util
from . import logs
from .ai import ComputerStrategy
from .storage import GameStorage


@dataclass
class MatchProgress:
    """Transient match state, including rankings and remaining turns."""

    active_players: List[Player]
    rankings: List[Any] = field(default_factory=list)
    ranking_colors: List[Any] = field(default_factory=list)
    winner_names: List[str] = field(default_factory=list)
    winner_colors: List[List[str]] = field(default_factory=list)
    pending_players: List[Player] = field(default_factory=list)
    unchanged_rounds: int = 0
    pass_rounds: int = 0
    round_active: bool = False


class Game:
    """One match and its state; the board owns movement rules."""
    filename = 'game_data.json'
    checkers_log_filename = 'checkers.log'
    checkers_log_path = checkers_log_filename

    def __init__(self, board: Board, balls: Dict[str, List[Ball]], players: List[Player],
                 is_group: int, color_directions=None, store=None):
        """ Generates a game object according to the input of a player ball board and if there are teams in the game"""
        self.is_group = is_group
        self.board = board
        self.balls = balls
        self.players = players
        self.store = store if store is not None else GameStorage(self.filename)
        self.passed_turns = 0
        self.unchanged_turns = 0
        self.previous_board = copy.deepcopy(self.board.get_br())
        self.dic_color_loc = self._starting_directions(color_directions)
        self.computer = ComputerStrategy(self)

    def _starting_directions(self, saved_directions):
        if saved_directions is not None:
            return dict(saved_directions)
        directions = {}
        triangles = self.board.target_triangles(len(self.players[0].get_color()))
        for direction in ('N', 'NE', 'SE', 'S', 'SW', 'NW'):
            color = self.board.cell_contents(triangles[direction][0])
            if color != 'O':
                directions[color] = direction
        return directions

    def serialize(self, lst_wins: Any, lst_wins_color: Any, lst_name_wins: Any, save_players: Any,
                  playr: Any, started: Any,end: Any, dic_color_loc: Any, lst_color_wn: Any) -> Any:
        return {
            'is_group': self.is_group,
            'board': self.board,
            'balls': self.balls,
            'players': self.players,
            'lst_wins': lst_wins,
            'lst_wins_color': lst_wins_color,
            'lst_name_wins': lst_name_wins,
            'save_players': save_players,
            'playr': playr,
            'started': started,
            'end': end,
            'dic_color_loc': dic_color_loc,
            'lst_color_wn': lst_color_wn
        }

    def word_color(self, playr: Player) -> str:
        """Gets a player and holds a string of his colors"""
        colorr = ''
        for i in range(len(playr.get_color()) - 1):
            colorr = colorr + playr.get_color()[i] + ' and '
        colorr = colorr + playr.get_color()[len(playr.get_color()) - 1]
        return colorr

    def loc_color(self, color: str) -> List[Tuple[int, int]]:
        """Gets a color and returns its positions"""
        loc_lst = []
        for bal in self.balls[color]:
            loc_lst.append(bal.get_location())
        return loc_lst

    def loc_player(self, playr: Player) -> List[Tuple[int, int]]:
        """Gets a player and returns the positions of his balls"""
        loc_lst = []
        for colorr in playr.get_color():
            loc_lst += self.loc_color(colorr)
        return loc_lst


    def log_turn(self, player, move):
        logs.log_turn(player, move)

    def load_log_file(self, filename):
        return logs.load_log_file(filename)

    def print_history(self, moves):
        logs.print_history(moves)

    def dic_targ(self) -> Dict[str, str]:
        """The function returns a dictionary for each color and its target direction"""
        dic_target = {}
        lst_color = []
        for playr in self.players:
            for colorr in playr.get_color():
                lst_color.append(colorr)
        for colorr in lst_color:
            directionn = self.dic_color_loc[colorr]
            if directionn == 'N':
                dic_target[colorr] = 'S'
            if directionn == 'S':
                dic_target[colorr] = 'N'
            if directionn == 'NE':
                dic_target[colorr] = 'SW'
            if directionn == 'SW':
                dic_target[colorr] = 'NE'
            if directionn == 'NW':
                dic_target[colorr] = 'SE'
            if directionn == 'SE':
                dic_target[colorr] = 'NW'
        return dic_target

    # Keep the original public calls while the move selection lives in ai.py.
    def _victory_places_strategy(self, *args, **kwargs):
        return self.computer._victory_places_strategy(*args, **kwargs)

    def victory_places_strategy(self, *args, **kwargs):
        return self.computer.victory_places_strategy(*args, **kwargs)

    def go_victory_places_strategy(self, *args, **kwargs):
        return self.computer.go_victory_places_strategy(*args, **kwargs)

    def relevant_goal_edge_cells(self, *args, **kwargs):
        return self.computer.relevant_goal_edge_cells(*args, **kwargs)

    def go_target(self, *args, **kwargs):
        return self.computer.go_target(*args, **kwargs)

    def go_location(self, *args, **kwargs):
        return self.computer.go_location(*args, **kwargs)

    def computer_stuck(self, *args, **kwargs):
        return self.computer.computer_stuck(*args, **kwargs)

    def single_turn(self, player: Player):
        """Compatibility entry point for a turn played in the terminal."""
        from .terminal import play_single_turn

        return play_single_turn(self, player)

    def take_turn(self, player: Player, move):
        """Apply and record a submitted move without reading or displaying UI."""
        if move is None:
            if player.get_name() != "computer":
                self.passed_turns += 1
            self.log_turn(player.get_name() + " in color " + self.word_color(player),
                          "Choose to pass his turn and do nothing")
            return "Passed this turn"
        source, target = move
        self.apply_move(player, source, target)
        description = (f"Moved ball from row {source[0] + 1} and column {source[1] + 1} "
                       f"to row {target[0] + 1} and column {target[1] + 1}")
        self.log_turn(player.get_name() + " in color " + self.word_color(player),
                      description)
        return description

    def apply_move(self, playr: Player, source: Tuple[int, int], target: Tuple[int, int]):
        """Validate and apply a turn to both the board and the matching ball."""
        if source not in self.board.cell_list() or target not in self.board.cell_list():
            raise ValueError("Move coordinates must be on the board")
        color = self.board.cell_contents(source)
        piece = next(
            (ball for ball in self.balls.get(color, []) if ball.get_location() == source),
            None,
        )
        if color not in playr.get_color() or piece is None:
            raise ValueError("The source must contain one of this player's balls")
        if target not in self.board.all_options_move(source):
            raise ValueError("The target is not a legal move")
        if not self.board.replace(source, target):
            raise ValueError("The target is occupied")
        piece.replaces(target)

    def _is_win(self, playr: Player) -> bool:
        """Checks specifically for one player if he won"""
        if len(self.players) == 2 and len(playr.get_color()) == 1:
            typp = 2
        else:
            typp = 1
        for colorr in playr.get_color():
            targett = self.dic_targ()[colorr]
            dic_loc = self.board.target_triangles(typp)
            lst_loc = dic_loc[targett]
            for loc in lst_loc:
                if self.board.cell_contents(loc) != colorr:
                    return False
        return True

    def group(self) -> List[Any]:
        """Returns a list of lists with the colors of each group in a separate list"""
        lst_groups = []
        if self.is_group == 1:
            lst_color = []
            for playr in self.players:
                for colorr in playr.get_color():
                    lst_color.append(colorr)
            dic = copy.deepcopy(self.dic_color_loc)
            if len(lst_color) == 4:
                mone = 2
            else:
                mone = 3
            for i in range(mone):
                cur = dic[lst_color[0]]
                opp = util.opposite_direction(cur)
                for colorr in lst_color:
                    if dic[colorr] == opp[0]:
                        opp_color = colorr
                        break
                lst_groups.append([lst_color[0], opp_color])
                del dic[lst_color[0]]
                del dic[opp_color]
                lst_color.remove(lst_color[0])
                lst_color.remove(opp_color)
        return lst_groups

    def is_win(self, playr: Player) -> bool:
        """Returns if the player won (also checks if he is in the group)
         if in the group everyone has to reach the goal for him to be considered a winner"""
        if self.is_group == 0:
            return self._is_win(playr)
        else:
            opp_playr = self.opp_playr(playr)
            return self._is_win(playr) and self._is_win(opp_playr)

    def is_over(self) -> bool:
        """Returns true or false if the game is over"""
        num_player = len(self.players)
        if self.is_group == 1:
            num_and = num_player - 2
        else:
            num_and = num_player - 1
        mone = 0
        for playr in self.players:
            if self.is_win(playr):
                mone += 1
        if mone >= num_and:
            return True
        return False

    def opp_playr(self, playr: Player) -> Any:
        """Returns the player opposite the given player The function is readable only if 'is_groups' = 1"""
        if self.is_group == 0:
            return 0
        lst_group = self.group()
        colorr = playr.get_color()[0]
        for lst in lst_group:
            if colorr in lst:
                opp_color = lst
                opp_color.remove(colorr)
                opp_color = opp_color[0]
                break
        for playrr in self.players:
            if playrr.get_color()[0] == opp_color:
                opp_playr = playrr
                return opp_playr

    def ln_real_players(self) -> int:
        """Returns the number of real players in the game"""
        mon = 0
        for playr in self.players:
            if playr.get_name() != 'computer':
                mon += 1
        return mon

    def _load_progress(self) -> MatchProgress:
        """Rebuild rankings and the unfinished round from a checkpoint."""
        progress = MatchProgress(active_players=list(self.players))
        saved = self.store.load()
        if saved is None:
            return progress

        progress.rankings = list(saved.get('lst_wins', []))
        progress.ranking_colors = list(saved.get('lst_wins_color', []))
        progress.winner_names = list(saved.get('lst_name_wins', []))
        progress.winner_colors = list(saved.get('lst_color_wn', []))
        saved_active = saved.get('save_players')
        if saved_active:
            active_colors = [entry['color'] for entry in saved_active]
            progress.active_players = [player for player in self.players
                                       if player.get_color() in active_colors]

        if 'pending_colors' in saved:
            progress.pending_players = [
                next(player for player in progress.active_players
                     if player.get_color() == colors)
                for colors in saved['pending_colors']
            ]
            progress.round_active = True
        else:
            # Older saves did not record the position inside a round.
            progress.active_players = [player for player in progress.active_players
                                       if player.get_color() not in progress.winner_colors]

        progress.unchanged_rounds = saved.get('unchanged_rounds', 0)
        progress.pass_rounds = saved.get('pass_rounds', 0)
        self.passed_turns = saved.get('passed_turns', 0)
        self.unchanged_turns = saved.get('unchanged_turns', 0)
        self.previous_board = copy.deepcopy(saved.get('previous_board', self.board.get_br()))
        return progress

    def _begin_round(self, progress: MatchProgress):
        """Update draw streaks once, before the first turn of a new round."""
        if progress.round_active:
            return
        progress.unchanged_rounds = (progress.unchanged_rounds + 1
                                     if self.unchanged_turns == len(self.players) else 0)
        real_players = self.ln_real_players()
        progress.pass_rounds = (progress.pass_rounds + 1
                                if real_players and self.passed_turns == real_players else 0)
        self.unchanged_turns = 0
        self.passed_turns = 0
        progress.pending_players = list(progress.active_players)
        progress.round_active = True

    def _save_before_turn(self, progress: MatchProgress, player: Player):
        """Keep the original save fields and record the current round position."""
        checkpoint = self.serialize(
            progress.rankings, progress.ranking_colors, progress.winner_names,
            progress.active_players, player.get_name(), 1, 0,
            self.dic_color_loc, progress.winner_colors,
        )
        checkpoint.update({
            'pending_colors': [candidate.get_color()
                               for candidate in progress.pending_players],
            'unchanged_rounds': progress.unchanged_rounds,
            'pass_rounds': progress.pass_rounds,
            'passed_turns': self.passed_turns,
            'unchanged_turns': self.unchanged_turns,
            'previous_board': self.previous_board,
        })
        self.store.save(checkpoint)

    def _has_no_moves(self, player: Player) -> bool:
        """A player with no ball able to move loses this turn."""
        return all(not self.board.all_options_move(location)
                   for location in self.loc_player(player))

    def record_blocked_turn(self, player: Player) -> str:
        """Record a turn skipped because the player has no legal moves."""
        message = 'Nowhere to move with any balls so the turn goes to the next player'
        self.log_turn(player.get_name() + ' in color ' + self.word_color(player), message)
        self.passed_turns += 1
        return message

    def _record_board_change(self):
        if self.board.get_br() == self.previous_board:
            self.unchanged_turns += 1
        self.previous_board = copy.deepcopy(self.board.get_br())

    def _draw_reached(self, progress: MatchProgress) -> bool:
        """Stop after three consecutive rounds without progress or human turns."""
        return progress.unchanged_rounds >= 3 or progress.pass_rounds >= 3

    def _record_winner(self, progress: MatchProgress, player: Player):
        """Record one player or one team once, preserving the ranking format."""
        if player.get_color() in progress.winner_colors:
            return
        player.set_number_wins(player.get_number_wins() + 1)
        progress.winner_names.append(player.get_name())
        progress.winner_colors.append(player.get_color())
        if self.is_group:
            partner = self.opp_playr(player)
            partner.set_number_wins(partner.get_number_wins() + 1)
            progress.winner_names.append(partner.get_name())
            progress.winner_colors.append(partner.get_color())
            progress.rankings.append([player.get_name(), partner.get_name()])
            progress.ranking_colors.append([player.get_color()[0], partner.get_color()[0]])
            description = (f'{player.get_name()} in color: {player.get_color()[0]} and '
                           f'{partner.get_name()} in color: {partner.get_color()[0]}')
            self.log_turn(description, ' finished the game')
        else:
            progress.rankings.append(player.get_name())
            color = self.word_color(player)
            progress.ranking_colors.append(color)
            self.log_turn(player.get_name() + ' in color ' + color, ' finished the game')

    def _remove_round_winners(self, progress: MatchProgress):
        """Advance the remaining players to the next round."""
        progress.active_players = [player for player in progress.active_players
                                   if player.get_color() not in progress.winner_colors]
        progress.winner_names.clear()
        progress.winner_colors.clear()
        progress.pending_players.clear()
        progress.round_active = False

    def finish_draw(self) -> str:
        """Clear a completed draw and return its display message."""
        self.store.clear()
        message = 'The game ended in a draw'
        self.log_turn('end game', message)
        return message

    def finish_match(self, progress: MatchProgress) -> str:
        """Rank remaining players, clear the save, and return the result."""
        self.store.clear()
        self._remove_round_winners(progress)
        if self.is_group:
            last_team = progress.active_players
            progress.rankings.append([player.get_name() for player in last_team])
            progress.ranking_colors.append([player.get_color()[0] for player in last_team])
            for player in last_team:
                player.set_number_losses(player.get_number_losses() + 1)
            message = ' '.join(
                f'{names[0]} in color: {colors[0]} and '
                f'{names[1]} in color: {colors[1]} finished place: {place} .'
                for place, (names, colors) in enumerate(
                    zip(progress.rankings, progress.ranking_colors), start=1)
            )
        else:
            loser = progress.active_players[0]
            loser.set_number_losses(loser.get_number_losses() + 1)
            progress.rankings.append(loser.get_name())
            progress.ranking_colors.append(self.word_color(loser))
            message = ' '.join(
                f'{name} in color: {color} finished place: {place} .'
                for place, (name, color) in enumerate(
                    zip(progress.rankings, progress.ranking_colors), start=1)
            )
        self.log_turn('end game', message)
        return message

    def play(self):
        """Run the existing terminal UI through the shared match session."""
        from .terminal import play_game

        play_game(self)
