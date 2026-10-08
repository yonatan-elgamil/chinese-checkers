"""Game state, legal turn execution, victory and turn order."""

from typing import Any, Dict, List, Tuple
import copy

from .player import Player
from .ball import Ball
from .board import Board
from . import utils as util
from . import logs
from .ai import ComputerStrategy
from .storage import GameStorage


class MatchProgress:
    """Transient match state; each instance owns its default lists."""

    def __init__(self, active_players, rankings=None, ranking_colors=None,
                 winner_names=None, winner_colors=None, pending_players=None,
                 unchanged_rounds=0, pass_rounds=0, round_active=False):
        self.active_players = active_players
        self.rankings = [] if rankings is None else rankings
        self.ranking_colors = [] if ranking_colors is None else ranking_colors
        self.winner_names = [] if winner_names is None else winner_names
        self.winner_colors = [] if winner_colors is None else winner_colors
        self.pending_players = [] if pending_players is None else pending_players
        self.unchanged_rounds = unchanged_rounds
        self.pass_rounds = pass_rounds
        self.round_active = round_active

    def __eq__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self.__dict__ == other.__dict__


class Game:
    """One match and its state; the board owns movement rules."""
    filename = 'game_data.json'
    checkers_log_filename = 'checkers.log'
    checkers_log_path = checkers_log_filename

    def __init__(self, board: Board, balls: Dict[str, List[Ball]], players: List[Player],
                 is_group: int, color_directions=None, store=None):
        """Create a match and share its Ball objects with the board."""
        self.is_group = is_group
        self.board = board
        self.balls = balls
        self.board.load_color_grid(self.board.get_color_grid(), balls)
        self.players = players
        self.store = store if store is not None else GameStorage(self.filename)
        self.passed_turns = 0
        self.unchanged_turns = 0
        self.previous_board = copy.deepcopy(self.board.get_color_grid())
        self.starting_directions = self._resolve_starting_directions(color_directions)
        self.computer_strategy = ComputerStrategy(self)

    def _resolve_starting_directions(self, saved_directions):
        if saved_directions is not None:
            return dict(saved_directions)
        directions = {}
        triangles = self.board.triangle_cells(len(self.players[0].get_colors()))
        for direction in ('N', 'NE', 'SE', 'S', 'SW', 'NW'):
            color = self.board.color_at(triangles[direction][0])
            if color != 'O':
                directions[color] = direction
        return directions

    def create_save_state(self, rankings, ranking_colors, winner_names, active_players,
                          next_player_name, started, end, starting_directions, winner_colors):
        """Export the original JSON field names for save-file compatibility."""
        return {
            'is_group': self.is_group,
            'board': self.board,
            'balls': self.balls,
            'players': self.players,
            'lst_wins': rankings,
            'lst_wins_color': ranking_colors,
            'lst_name_wins': winner_names,
            'save_players': active_players,
            'playr': next_player_name,
            'started': started,
            'end': end,
            'dic_color_loc': starting_directions,
            'lst_color_wn': winner_colors
        }

    def describe_player_colors(self, playr: Player) -> str:
        """Describe the owned colors in their existing display order."""
        colorr = ''
        for i in range(len(playr.get_colors()) - 1):
            colorr = colorr + playr.get_colors()[i] + ' and '
        colorr = colorr + playr.get_colors()[len(playr.get_colors()) - 1]
        return colorr

    def positions_for_color(self, color: str) -> List[Tuple[int, int]]:
        """Return the positions of the shared balls for one color."""
        loc_lst = []
        for bal in self.balls[color]:
            loc_lst.append(bal.get_position())
        return loc_lst

    def positions_for_player(self, playr: Player) -> List[Tuple[int, int]]:
        """Return the positions of all balls owned by the player."""
        loc_lst = []
        for colorr in playr.get_colors():
            loc_lst += self.positions_for_color(colorr)
        return loc_lst

    def log_turn(self, player, move):
        logs.log_turn(player, move)

    def load_log_file(self, filename):
        return logs.load_log_file(filename)

    def print_history(self, moves):
        logs.print_history(moves)

    def goal_directions(self) -> Dict[str, str]:
        """Map each color to the corner opposite its starting corner."""
        dic_target = {}
        lst_color = []
        for playr in self.players:
            for colorr in playr.get_colors():
                lst_color.append(colorr)
        for colorr in lst_color:
            directionn = self.starting_directions[colorr]
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

    def play_terminal_turn(self, player: Player):
        """Play one turn through the terminal input and output adapter."""
        from .terminal import play_single_turn

        return play_single_turn(self, player)

    def take_turn(self, player: Player, move):
        """Apply and record a submitted move without reading or displaying UI."""
        if move is None:
            if player.get_name() != "computer":
                self.passed_turns += 1
            self.log_turn(player.get_name() + " in color " + self.describe_player_colors(player),
                          "Choose to pass his turn and do nothing")
            return "Passed this turn"
        source, target = move
        self.apply_move(player, source, target)
        description = (f"Moved ball from row {source[0] + 1} and column {source[1] + 1} "
                       f"to row {target[0] + 1} and column {target[1] + 1}")
        self.log_turn(player.get_name() + " in color " + self.describe_player_colors(player),
                      description)
        return description

    def apply_move(self, playr: Player, source: Tuple[int, int], target: Tuple[int, int]):
        """Validate a move; the board then relocates the shared Ball once."""
        if source not in self.board.cell_coordinates() or target not in self.board.cell_coordinates():
            raise ValueError("Move coordinates must be on the board")
        color = self.board.color_at(source)
        piece = next(
            (ball for ball in self.balls.get(color, []) if ball.get_position() == source),
            None,
        )
        if (color not in playr.get_colors() or piece is None
                or self.board.get_ball(source) is not piece):
            raise ValueError("The source must contain one of this player's balls")
        if target not in self.board.legal_destinations(source):
            raise ValueError("The target is not a legal move")
        if not self.board.move_ball(source, target):
            raise ValueError("The target is occupied")

    def _has_completed_goals(self, playr: Player) -> bool:
        """Check whether all target cells contain this player's colors."""
        if len(self.players) == 2 and len(playr.get_colors()) == 1:
            typp = 2
        else:
            typp = 1
        for colorr in playr.get_colors():
            targett = self.goal_directions()[colorr]
            dic_loc = self.board.triangle_cells(typp)
            lst_loc = dic_loc[targett]
            for loc in lst_loc:
                if self.board.color_at(loc) != colorr:
                    return False
        return True

    def team_color_pairs(self) -> List[Any]:
        """Return each team as a pair of colors in opposite starting corners."""
        lst_groups = []
        if self.is_group == 1:
            lst_color = []
            for playr in self.players:
                for colorr in playr.get_colors():
                    lst_color.append(colorr)
            dic = copy.deepcopy(self.starting_directions)
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

    def has_player_won(self, playr: Player) -> bool:
        """Check goal completion for one player, including their teammate."""
        if self.is_group == 0:
            return self._has_completed_goals(playr)
        else:
            teammate_for = self.teammate_for(playr)
            return self._has_completed_goals(playr) and self._has_completed_goals(teammate_for)

    def is_finished(self) -> bool:
        """Check whether enough players or teams have completed their goals."""
        num_player = len(self.players)
        if self.is_group == 1:
            num_and = num_player - 2
        else:
            num_and = num_player - 1
        mone = 0
        for playr in self.players:
            if self.has_player_won(playr):
                mone += 1
        if mone >= num_and:
            return True
        return False

    def teammate_for(self, playr: Player) -> Any:
        """Return the player in the opposite corner when teams are enabled."""
        if self.is_group == 0:
            return 0
        lst_group = self.team_color_pairs()
        colorr = playr.get_colors()[0]
        for lst in lst_group:
            if colorr in lst:
                opp_color = lst
                opp_color.remove(colorr)
                opp_color = opp_color[0]
                break
        for playrr in self.players:
            if playrr.get_colors()[0] == opp_color:
                teammate_for = playrr
                return teammate_for

    def human_player_count(self) -> int:
        """Count players whose name does not mark them as a computer."""
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
                                       if player.get_colors() in active_colors]

        if 'pending_colors' in saved:
            progress.pending_players = [
                next(player for player in progress.active_players
                     if player.get_colors() == colors)
                for colors in saved['pending_colors']
            ]
            progress.round_active = True
        else:
            # Older saves did not record the position inside a round.
            progress.active_players = [player for player in progress.active_players
                                       if player.get_colors() not in progress.winner_colors]

        progress.unchanged_rounds = saved.get('unchanged_rounds', 0)
        progress.pass_rounds = saved.get('pass_rounds', 0)
        self.passed_turns = saved.get('passed_turns', 0)
        self.unchanged_turns = saved.get('unchanged_turns', 0)
        self.previous_board = copy.deepcopy(saved.get('previous_board', self.board.get_color_grid()))
        return progress

    def _begin_round(self, progress: MatchProgress):
        """Update draw streaks once, before the first turn of a new round."""
        if progress.round_active:
            return
        progress.unchanged_rounds = (progress.unchanged_rounds + 1
                                     if self.unchanged_turns == len(self.players) else 0)
        real_players = self.human_player_count()
        progress.pass_rounds = (progress.pass_rounds + 1
                                if real_players and self.passed_turns == real_players else 0)
        self.unchanged_turns = 0
        self.passed_turns = 0
        progress.pending_players = list(progress.active_players)
        progress.round_active = True

    def _save_before_turn(self, progress: MatchProgress, player: Player):
        """Keep the original save fields and record the current round position."""
        checkpoint = self.create_save_state(
            progress.rankings, progress.ranking_colors, progress.winner_names,
            progress.active_players, player.get_name(), 1, 0,
            self.starting_directions, progress.winner_colors,
        )
        checkpoint.update({
            'pending_colors': [candidate.get_colors()
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
        return all(not self.board.legal_destinations(location)
                   for location in self.positions_for_player(player))

    def record_blocked_turn(self, player: Player) -> str:
        """Record a turn skipped because the player has no legal moves."""
        message = 'Nowhere to move with any balls so the turn goes to the next player'
        self.log_turn(player.get_name() + ' in color ' + self.describe_player_colors(player), message)
        self.passed_turns += 1
        return message

    def _record_board_change(self):
        if self.board.get_color_grid() == self.previous_board:
            self.unchanged_turns += 1
        self.previous_board = copy.deepcopy(self.board.get_color_grid())

    def _draw_reached(self, progress: MatchProgress) -> bool:
        """Stop after three consecutive rounds without progress or human turns."""
        return progress.unchanged_rounds >= 3 or progress.pass_rounds >= 3

    def _record_winner(self, progress: MatchProgress, player: Player):
        """Record one player or one team once, preserving the ranking format."""
        if player.get_colors() in progress.winner_colors:
            return
        player.set_wins(player.get_wins() + 1)
        progress.winner_names.append(player.get_name())
        progress.winner_colors.append(player.get_colors())
        if self.is_group:
            partner = self.teammate_for(player)
            partner.set_wins(partner.get_wins() + 1)
            progress.winner_names.append(partner.get_name())
            progress.winner_colors.append(partner.get_colors())
            progress.rankings.append([player.get_name(), partner.get_name()])
            progress.ranking_colors.append([player.get_colors()[0], partner.get_colors()[0]])
            description = (f'{player.get_name()} in color: {player.get_colors()[0]} and '
                           f'{partner.get_name()} in color: {partner.get_colors()[0]}')
            self.log_turn(description, ' finished the game')
        else:
            progress.rankings.append(player.get_name())
            color = self.describe_player_colors(player)
            progress.ranking_colors.append(color)
            self.log_turn(player.get_name() + ' in color ' + color, ' finished the game')

    def _remove_round_winners(self, progress: MatchProgress):
        """Advance the remaining players to the next round."""
        progress.active_players = [player for player in progress.active_players
                                   if player.get_colors() not in progress.winner_colors]
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
            progress.ranking_colors.append([player.get_colors()[0] for player in last_team])
            for player in last_team:
                player.set_losses(player.get_losses() + 1)
            message = ' '.join(
                f'{names[0]} in color: {colors[0]} and '
                f'{names[1]} in color: {colors[1]} finished place: {place} .'
                for place, (names, colors) in enumerate(
                    zip(progress.rankings, progress.ranking_colors), start=1)
            )
        else:
            loser = progress.active_players[0]
            loser.set_losses(loser.get_losses() + 1)
            progress.rankings.append(loser.get_name())
            progress.ranking_colors.append(self.describe_player_colors(loser))
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
