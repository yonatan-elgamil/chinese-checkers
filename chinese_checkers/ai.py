"""Computer move selection. All move rules are supplied by Board."""

import copy
from collections import deque
import random
from typing import Any, List, Tuple

from . import utils as util
from .player import Player
from .ball import Ball


class ComputerStrategy:
    """Select a move from the current game state without owning that state."""

    def __init__(self, game):
        self.game = game
        self.board = game.board
        self.players = game.players

    def choose_move(self, player):
        """Return a legal computer move or None when no useful move exists."""
        if self.is_stuck(player):
            return None
        locations = self.game.positions_for_player(player)
        if not locations:
            return None

        number_of_colors = len(player.get_colors())
        # Move a ball already inside its goal when it would block later arrivals.
        for color in player.get_colors():
            move = self.find_goal_rearrangement_move(number_of_colors, color)
            if move:
                return tuple(move)

        locations = self.filter_settled_balls(locations, player.get_colors(),
                                                  number_of_colors)
        # Preserve the original random ordering among colors.
        colors = list(player.get_colors())
        random.shuffle(colors)
        for color in colors:
            color_locations = [place for place in locations
                               if self.board.color_at(place) == color]
            if not color_locations:
                continue
            targets = self.reachable_goal_targets(color, number_of_colors, color_locations)
            if targets:
                return tuple(self.choose_move_toward_targets(targets, color_locations,
                                              number_of_colors, color))
        return None

    def _goal_rows(self, ln_color: int, direct_targ: str) -> List[List[Tuple[int, int]]]:
        """Order the goal rows from the deepest row toward its entrance."""
        if ln_color == 1 and len(self.players) == 2:
            typp = 2
        else:
            typp = 1
        loc_targ = self.board.triangle_cells(typp)
        if direct_targ == 'N' or direct_targ == 'NE' or direct_targ == 'NW':
            sort_lst = util.group_coordinates_by_row(loc_targ[direct_targ])
        else:
            sort_lst = util.group_coordinates_by_row_descending(loc_targ[direct_targ])
        return sort_lst

    def filter_settled_balls(self, lst_loc: List[Tuple[int, int]],
                                clor_lst: List[str], ln_color: int) -> List[Any]:
        """Exclude settled goal pieces using the original board-size rules."""
        for colorr in clor_lst:
            dic_tar = self.game.goal_directions()
            direct_targ = dic_tar[colorr]
            sort_lst = self._goal_rows(ln_color, direct_targ)
            if ((self.board.get_size() > 7) or
                    (self.board.get_size() == 7 and ln_color == 1 and len(self.players) == 2)):

                for lst in sort_lst:
                    mone = 0
                    for cor in lst:
                        if self.board.color_at(cor) == colorr:
                            mone += 1
                    if mone == len(lst):
                        lst_loc = util.exclude_coordinates(lst_loc, lst)
                    elif direct_targ == 'N' or direct_targ == 'S':
                        break
            else:
                for lst in sort_lst:
                    for cor in lst:
                        if self.board.color_at(cor) == colorr:
                            lst_loc.remove(cor)
        return lst_loc

    def find_goal_rearrangement_move(self, ln_color: int, clor: str) -> List[Any]:
        """Find a move inside the goal that leaves room for later arrivals."""
        if (self.board.get_size() > 7) or (self.board.get_size() == 7 and ln_color == 1 and len(self.players) == 2):
            dic_tar = self.game.goal_directions()
            direct_targ = dic_tar[clor]
            sort_lst = self._goal_rows(ln_color, direct_targ)
            for i in range(len(sort_lst)-1):
                sort_lst = self._goal_rows(ln_color, direct_targ)
                mone_color = 0
                lst_cor_others = []
                lst_cor_empty = []
                for cor in sort_lst[i]:
                    if self.board.color_at(cor) == clor:
                        mone_color += 1
                    if self.board.is_empty(cor):
                        lst_cor_empty.append(cor)
                    if not self.board.is_empty(cor) and self.board.color_at(cor) != clor:
                        lst_cor_others.append(cor)
                if mone_color == len(sort_lst[i]):
                    continue
                if len(lst_cor_others) == len(sort_lst[i]):
                    return []
                if len(lst_cor_others) > 0 and len(lst_cor_empty) == 0:
                    return []
                if len(lst_cor_empty) > 0:
                    relevant_loc_ls = []
                    for j in range(i+1, len(sort_lst)):
                        for cr in sort_lst[j]:
                            if self.board.color_at(cr) == clor:
                                relevant_loc_ls.append(cr)
                    # print(lst_cor_empty)
                    all_arrive = self.reachable_targets(lst_cor_empty, relevant_loc_ls)
                    if len(all_arrive) == 0:
                        return []
                    bast_path = self.shortest_paths_to_targets(all_arrive, relevant_loc_ls)

                    path = random.choice(bast_path)

                    loc = path[0]
                    tar = path[1]
                    ls = []
                    ls.append(loc)
                    ls.append(tar)
                    return ls
            return []
        else:
            return []

    def relevant_goal_edge_cells(self, direction: Any , typ: Any, ln_color: Any):
        new_lst = []
        sort_trg = self._goal_rows(ln_color, direction)
        if direction == 'N' or direction == 'S':
            new_lst = sort_trg[-1]
            return new_lst
        if direction == 'NW' or direction == 'SW':
            for lst in sort_trg:
                new_lst.append(lst[-1])
            return new_lst
        else:
            for lst in sort_trg:
                new_lst.append(lst[0])
            return new_lst

    def reachable_goal_targets(self, color: str, number_of_colors: int,
                  candidate_locations: List[Tuple[int, int]]) -> List[Any]:
        """Find reachable goal cells, or reachable cells closest to the goal."""
        direction = self.game.goal_directions()[color]
        triangle_type = 2 if number_of_colors == 1 and len(self.players) == 2 else 1
        locations = [place for place in self.game.positions_for_color(color)
                     if place in candidate_locations]
        if not locations:
            return []
        goal = self.board.triangle_cells(triangle_type)[direction]
        locations = util.exclude_coordinates(locations, goal)
        reachable = self.reachable_targets(
            self.board.empty_triangle_cells(direction, triangle_type), locations
        )
        if reachable:
            return reachable
        return self._reachable_cells_near_goal(direction, triangle_type,
                                               number_of_colors, locations)

    def _free_paths_near(self, targets, direction, triangle_type, excluded):
        paths = []
        for target in targets:
            paths.extend(self.paths_to_empty_cells_near_goal(
                target, direction, triangle_type, excluded
            ))
        return paths

    def _reachable_cells_near_goal(self, direction, triangle_type,
                                   number_of_colors, locations):
        """Expand rings of free cells until one can be reached by a ball."""
        remaining = self.board.empty_cells()
        frontier = self.relevant_goal_edge_cells(direction, triangle_type, number_of_colors)
        if not frontier:
            return []
        if len(self.board.get_cells()) > 30:
            frontier = [random.choice(frontier)]
        paths = self._free_paths_near(frontier, direction, triangle_type, frontier)
        # Different goal points may yield the same path in the first ring.
        seen = set()
        paths = [path for path in paths
                 if tuple(path) not in seen and not seen.add(tuple(path))]
        frontier = util.unique_path_destinations(paths)
        if not frontier:
            return []
        excluded = list(frontier)
        remaining = util.exclude_coordinates(remaining, frontier)
        reachable = self.reachable_targets(frontier, locations)

        while not reachable:
            if not remaining:
                return []
            sources = ([random.choice(frontier)] if len(self.board.get_cells()) > 30
                       else frontier)
            paths = self._free_paths_near(sources, direction, triangle_type, excluded)
            frontier = util.unique_path_destinations(paths)
            if not frontier:
                return []
            remaining = util.exclude_coordinates(remaining, frontier)
            excluded.extend(frontier)
            reachable = self.reachable_targets(frontier, locations)

        matching = util.find_path_for_cell(paths, reachable)
        shortest = util.find_smallest_lists(matching)
        return util.unique_path_destinations(shortest)

    def choose_move_toward_targets(self, go_targ: List[Tuple[int, int]], lc_lst: List[Tuple[int, int]]
                    , ln_color: int, clor: str) -> List[Any]:
        """Choose the first turn of a shortest route using the original tie-breaking."""
        dic_targ_direct = self.game.goal_directions()
        dir_me = dic_targ_direct[clor]
        if ln_color == 1 and len(self.players) == 2:
            typp = 2
        else:
            typp = 1
        tar_cor = self.board.triangle_cells(typp)
        tar_cor = tar_cor[dir_me]
        lc_lst = util.exclude_coordinates(lc_lst, tar_cor)
        # בדיקה אם המיקומים של היעד מחוץ למשולש אז....
        mone3 = 0
        for tr in go_targ:
            if tr in tar_cor:
                mone3 = 1
        bast_path = self.shortest_paths_to_targets(go_targ, lc_lst)
        save_bast_path = copy.deepcopy(bast_path)
        #   אם כל המיקומים של היעד מחוץ ליעד המקורי
        path = random.choice(bast_path)
        if mone3 == 0:
            while len(path) == 2:
                lc_lst.remove(path[0])
                if len(lc_lst) == 0 or len(self.reachable_targets(go_targ,lc_lst)) == 0:
                    break
                bast_path = self.shortest_paths_to_targets(go_targ, lc_lst)
                save_bast_path = copy.deepcopy(bast_path)
                path = random.choice(bast_path)
        bast_path = save_bast_path
        path = random.choice(bast_path)
        loc = path[0]
        targ = path[1]
        lst_go = []
        lst_go.append(loc)
        lst_go.append(targ)
        return lst_go

    def is_stuck(self, playr: Player) -> bool:
        if len(playr.get_colors()) == 1 and len(self.players) == 2:
            typp = 2
        else:
            typp = 1
        mone1 = 0
        for clor in playr.get_colors():
            ls_loc = self.game.positions_for_player(playr)
            dic_targ_direct = self.game.goal_directions()
            direct = dic_targ_direct[clor]
            tar_cor = self.board.triangle_cells(typp)
            tar_cor = tar_cor[direct]
            for cor in tar_cor:
                if self.board.color_at(cor) == clor and cor in ls_loc:
                    ls_loc.remove(cor)
            mone2 = 0
            ls_tr_move = []
            for locc in ls_loc:
                if len(self.board.legal_destinations(locc)) == 0:
                    mone2 += 1
                else:
                    ls_tr_move = ls_tr_move + self.board.legal_destinations(locc)
            if mone2 == len(ls_loc):
                mone1 = mone1 + 1
            else:
                all_cell = self.board.cell_coordinates()
                direct = self.game.starting_directions[clor]
                tar_cor = self.board.triangle_cells(typp)
                all_me = tar_cor[direct]
                all_cell = util.exclude_coordinates(all_cell, all_me)
                for cor in ls_tr_move:
                    if cor in all_cell:
                        return False
                mone1 = mone1 + 1
        if mone1 == len(playr.get_colors()):
            return True
        else:
            return False

    def _neighbors_away_from_goal(self, source, direction, neighbors):
        """Keep the original directional preference when expanding goal rings."""
        row, column = source
        for neighbor in list(neighbors):
            if direction == 'N' and neighbor[0] < row:
                neighbors.remove(neighbor)
            if direction == 'S' and neighbor[0] > row:
                neighbors.remove(neighbor)
            if direction in ('NW', 'SW') and neighbor[1] < column:
                neighbors.remove(neighbor)
            if direction in ('NE', 'SE') and neighbor[1] > column:
                neighbors.remove(neighbor)
        return neighbors

    def paths_to_empty_cells_near_goal(self, target, direction, triangle_type, excluded):
        """Find the same free cells outside the goal using the original DFS."""
        paths = []
        path = []

        def search(current):
            goal = self.board.triangle_cells(triangle_type)[direction]
            if self.board.is_empty(current) and current not in goal and current not in excluded:
                path.append(current)
                paths.append(path[:])
                path.pop()
                return
            neighborhood = self.board.classify_neighbors(current)
            neighbors = neighborhood['allowed'] + neighborhood['banned']
            neighbors = self._neighbors_away_from_goal(current, direction, neighbors)
            for neighbor in neighbors:
                if neighbor in path:
                    continue
                path.append(current)
                search(neighbor)
                path.pop()

        search(target)
        return paths

    def reachable_targets(self, targets, sources):
        """Return targets reachable by at least one of the candidate pieces."""
        reachable = []
        for target in targets:
            for source in sources:
                if self.find_shortest_path(source, target):
                    reachable.append(target)
                    break
        return reachable

    def find_shortest_path(self, source, target):
        """Plan a shortest route across future turns with the original BFS.

        Every candidate board is a copy, so planning cannot move live pieces.
        Board remains responsible for the legal destinations of each turn.
        """
        cells = set(self.board.cell_coordinates())
        if source not in cells or target not in cells:
            return []
        original_piece = self.board.get_ball(source)
        color = original_piece.color if original_piece is not None else 'X'
        queue = deque([(source, [source])])
        visited = {source}
        while queue:
            current, path = queue.popleft()
            if current == target:
                return path
            simulated_board = copy.deepcopy(self.board)
            simulated_board.remove_ball(source)
            simulated_board.place_ball(Ball(color, current))
            for destination in simulated_board.legal_destinations(current):
                if destination not in visited:
                    visited.add(destination)
                    queue.append((destination, path + [destination]))
        return []

    def shortest_paths_to_targets(self, targets, sources):
        """Keep only the shortest routes among the given source/target pairs."""
        paths = []
        for target in targets:
            for source in sources:
                path = self.find_shortest_path(source, target)
                if path:
                    paths.append(path)
        return util.find_smallest_lists(paths) if paths else []
