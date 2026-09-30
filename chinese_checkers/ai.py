"""Computer move selection. All move rules are supplied by Board."""

import copy
import random
from typing import Any, List, Tuple

from . import utils as util
from .player import Player


class ComputerStrategy:
    """Select a move from the current game state without owning that state."""

    def __init__(self, game):
        self.game = game
        self.board = game.board
        self.players = game.players

    def dic_targ(self):
        return self.game.dic_targ()

    def loc_color(self, color):
        return self.game.loc_color(color)

    def loc_player(self, player):
        return self.game.loc_player(player)

    def choose_move(self, player):
        """Return a legal computer move or None when no useful move exists."""
        if self.computer_stuck(player):
            return None
        locations = self.loc_player(player)
        if not locations:
            return None

        number_of_colors = len(player.get_color())
        # Move a ball already inside its goal when it would block later arrivals.
        for color in player.get_color():
            move = self.go_victory_places_strategy(number_of_colors, color)
            if move:
                return tuple(move)

        locations = self.victory_places_strategy(locations, player.get_color(),
                                                  number_of_colors)
        # Preserve the original random ordering among colors.
        colors = list(player.get_color())
        random.shuffle(colors)
        for color in colors:
            color_locations = [place for place in locations
                               if self.board.cell_contents(place) == color]
            if not color_locations:
                continue
            targets = self.go_target(color, number_of_colors, color_locations)
            if targets:
                return tuple(self.go_location(targets, color_locations,
                                              number_of_colors, color))
        return None

    def _victory_places_strategy(self, ln_color: int, direct_targ: str) -> List[List[Tuple[int, int]]]:
            """Gets a destination direction and returns all destinations
             that must be sorted in a list of lists by row"""
            if ln_color == 1 and len(self.players) == 2:
                typp = 2
            else:
                typp = 1
            loc_targ = self.board.target_triangles(typp)
            if direct_targ == 'N' or direct_targ == 'NE' or direct_targ == 'NW':
                sort_lst = util.group_coordinates_by_row(loc_targ[direct_targ])
            else:
                sort_lst = util.group_coordinates_by_row_descending(loc_targ[direct_targ])
            return sort_lst

    def victory_places_strategy(self, lst_loc: List[Tuple[int, int]],
                                clor_lst: List[str], ln_color: int) -> List[Any]:
        """receives a list of locations of a computer player in principle andreturns the locations
        without the targets if the board falls intoa category that can be problematic because then the
        computercan jam itself, so it returns without targets that have afull row, meaning that in the
        returned list it is onlythe locations that the computer player will play with and the other locations
         are not tired"""
        for colorr in clor_lst:
            dic_tar = self.dic_targ()
            direct_targ = dic_tar[colorr]
            sort_lst = self._victory_places_strategy(ln_color, direct_targ)
            if ((self.board.get_size() > 7) or
                    (self.board.get_size() == 7 and ln_color == 1 and len(self.players) == 2)):

                for lst in sort_lst:
                    mone = 0
                    for cor in lst:
                        if self.board.cell_contents(cor) == colorr:
                            mone += 1
                    if mone == len(lst):
                        lst_loc = util.exclude_coordinates(lst_loc, lst)
                    elif direct_targ == 'N' or direct_targ == 'S':
                        break
            else:
                for lst in sort_lst:
                    for cor in lst:
                        if self.board.cell_contents(cor) == colorr:
                            lst_loc.remove(cor)
        return lst_loc

    def go_victory_places_strategy(self, ln_color: int, clor: str) -> List[Any]:
        """This program is responsible for moving the computer its target locations in a
         situation where the board enters a problematic situation in terms of locations,
          meaning that if we do not operate the computer will block the target locations
         for itself, the program will check if the computer can zoom back in the destination
          and if so it will return the location from which it moved and the step of the move
          if it does not return a list empty"""
        if (self.board.get_size() > 7) or (self.board.get_size() == 7 and ln_color == 1 and len(self.players) == 2):
            dic_tar = self.dic_targ()
            direct_targ = dic_tar[clor]
            sort_lst = self._victory_places_strategy(ln_color, direct_targ)
            for i in range(len(sort_lst)-1):
                sort_lst = self._victory_places_strategy(ln_color, direct_targ)
                mone_color = 0
                lst_cor_others = []
                lst_cor_empty = []
                for cor in sort_lst[i]:
                    if self.board.cell_contents(cor) == clor:
                        mone_color += 1
                    if self.board.is_empty(cor):
                        lst_cor_empty.append(cor)
                    if not self.board.is_empty(cor) and self.board.cell_contents(cor) != clor:
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
                            if self.board.cell_contents(cr) == clor:
                                relevant_loc_ls.append(cr)
                    # print(lst_cor_empty)
                    all_arrive = self.board.can_arrive_target(lst_cor_empty, relevant_loc_ls)
                    if len(all_arrive) == 0:
                        return []
                    bast_path = self.board.all_best_paths(all_arrive, relevant_loc_ls)

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
        sort_trg = self._victory_places_strategy(ln_color, direction)
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

    def go_target(self, color: str, number_of_colors: int,
                  candidate_locations: List[Tuple[int, int]]) -> List[Any]:
        """Find reachable goal cells, or reachable cells closest to the goal."""
        direction = self.dic_targ()[color]
        triangle_type = 2 if number_of_colors == 1 and len(self.players) == 2 else 1
        locations = [place for place in self.loc_color(color)
                     if place in candidate_locations]
        if not locations:
            return []
        goal = self.board.target_triangles(triangle_type)[direction]
        locations = util.exclude_coordinates(locations, goal)
        reachable = self.board.can_arrive_target(
            self.board.empty_target(direction, triangle_type), locations
        )
        if reachable:
            return reachable
        return self._reachable_cells_near_goal(direction, triangle_type,
                                               number_of_colors, locations)

    def _free_paths_near(self, targets, direction, triangle_type, excluded):
        paths = []
        for target in targets:
            paths.extend(self.board.empty_near_target(
                target, [], direction, triangle_type, excluded
            ))
        return paths

    def _reachable_cells_near_goal(self, direction, triangle_type,
                                   number_of_colors, locations):
        """Expand rings of free cells until one can be reached by a ball."""
        remaining = self.board.all_empty()
        frontier = self.relevant_goal_edge_cells(direction, triangle_type, number_of_colors)
        if not frontier:
            return []
        if len(self.board.get_br()) > 30:
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
        reachable = self.board.can_arrive_target(frontier, locations)

        while not reachable:
            if not remaining:
                return []
            sources = ([random.choice(frontier)] if len(self.board.get_br()) > 30
                       else frontier)
            paths = self._free_paths_near(sources, direction, triangle_type, excluded)
            frontier = util.unique_path_destinations(paths)
            if not frontier:
                return []
            remaining = util.exclude_coordinates(remaining, frontier)
            excluded.extend(frontier)
            reachable = self.board.can_arrive_target(frontier, locations)

        matching = util.find_path_for_cell(paths, reachable)
        shortest = util.find_smallest_lists(matching)
        return util.unique_path_destinations(shortest)

    def go_location(self, go_targ: List[Tuple[int, int]], lc_lst: List[Tuple[int, int]]
                    , ln_color: int, clor: str) -> List[Any]:
        """This function is responsible for moving the computer outside the target
         in order to get as close as possible to the target. The program will receive
          the relevant targets and positions of the balls and return the step that will
           bring us from the closest location to the closest target
         The program uses special functions built especially for it in the game and on the board"""
        dic_targ_direct = self.dic_targ()
        dir_me = dic_targ_direct[clor]
        if ln_color == 1 and len(self.players) == 2:
            typp = 2
        else:
            typp = 1
        tar_cor = self.board.target_triangles(typp)
        tar_cor = tar_cor[dir_me]
        lc_lst = util.exclude_coordinates(lc_lst, tar_cor)
        # בדיקה אם המיקומים של היעד מחוץ למשולש אז....
        mone3 = 0
        for tr in go_targ:
            if tr in tar_cor:
                mone3 = 1
        bast_path = self.board.all_best_paths(go_targ, lc_lst)
        save_bast_path = copy.deepcopy(bast_path)
        #   אם כל המיקומים של היעד מחוץ ליעד המקורי
        path = random.choice(bast_path)
        if mone3 == 0:
            while len(path) == 2:
                lc_lst.remove(path[0])
                if len(lc_lst) == 0 or len(self.board.can_arrive_target(go_targ,lc_lst)) == 0:
                    break
                bast_path = self.board.all_best_paths(go_targ, lc_lst)
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

    def computer_stuck(self, playr: Player) -> bool:
        if len(playr.get_color()) == 1 and len(self.players) == 2:
            typp = 2
        else:
            typp = 1
        mone1 = 0
        for clor in playr.get_color():
            ls_loc = self.loc_player(playr)
            dic_targ_direct = self.dic_targ()
            direct = dic_targ_direct[clor]
            tar_cor = self.board.target_triangles(typp)
            tar_cor = tar_cor[direct]
            for cor in tar_cor:
                if self.board.cell_contents(cor) == clor and cor in ls_loc:
                    ls_loc.remove(cor)
            mone2 = 0
            ls_tr_move = []
            for locc in ls_loc:
                if len(self.board.all_options_move(locc)) == 0:
                    mone2 += 1
                else:
                    ls_tr_move = ls_tr_move + self.board.all_options_move(locc)
            if mone2 == len(ls_loc):
                mone1 = mone1 + 1
            else:
                all_cell = self.board.cell_list()
                direct = self.game.dic_color_loc[clor]
                tar_cor = self.board.target_triangles(typp)
                all_me = tar_cor[direct]
                all_cell = util.exclude_coordinates(all_cell, all_me)
                for cor in ls_tr_move:
                    if cor in all_cell:
                        return False
                mone1 = mone1 + 1
        if mone1 == len(playr.get_color()):
            return True
        else:
            return False
