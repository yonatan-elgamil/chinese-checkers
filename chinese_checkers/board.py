from .ball import Ball
from typing import List, Tuple, Iterable, Optional, Callable, Literal, Set, Dict, Any
import copy
from . import utils as util
from collections import deque

class Board:
    """Star-shaped board geometry, movement rules, and path searches."""

    def __init__(self, size: int):
        """Build an empty board of size 4, 7, 10, or another valid 3n + 1 size."""

        if not isinstance(size, int) or isinstance(size, bool) or size < 4 or (size - 1) % 3:
            raise ValueError("Board size must be 4, 7, 10, ...")
        self.size = size
        small_triple_size = int((self.size-1)/3)
        row_size = self.size+small_triple_size
        col_size = self.size
        total_list = []
        for i in range(row_size):
            total_list.append([])
        for i in range(small_triple_size):
            for j in range(small_triple_size-1-i,small_triple_size):
                total_list[i].append('O')
        mone_row = small_triple_size
        reduces_col = -1
        for i in range(mone_row,mone_row + small_triple_size+1):
            reduces_col += 1
            for j in range(col_size-reduces_col):
                total_list[i].append('O')
        mone_row += small_triple_size+1
        increases_col = -1
        for i in range(mone_row,mone_row + small_triple_size):
            increases_col += 1
            for j in range(col_size-small_triple_size+1+increases_col):
                total_list[i].append('O')
        mone_row += small_triple_size
        reduces_col = -1
        for i in range(mone_row,mone_row + small_triple_size):
            reduces_col += 1
            for j in range(small_triple_size - reduces_col):
                total_list[i].append('O')
        self.br = total_list

    def __str__(self) -> str:
        """The program will cause that in every printing of the
        board of board will be printed in the shape of a Star of David"""
        result = ""
        size = self.size
        br = self.br

        small_triple_size = int((size - 1) / 3)
        result += '\n'.join(' ' * (size - 1 - i) + ' '.join(row) for i, row in enumerate(br[:small_triple_size]))
        result += '\n'

        mone = 0
        for i in range(small_triple_size, small_triple_size * 2 + 1):
            result += ' ' * mone
            result += ' '.join(br[i])
            result += '\n'
            mone += 1

        mone = int((size - 1) / 3) - 1
        for i in range(small_triple_size * 2 + 1, small_triple_size * 3 + 1):
            result += ' ' * mone
            result += ' '.join(br[i])
            result += '\n'
            mone -= 1

        mone = int((size - 1) / 3)
        for i in range(small_triple_size * 3 + 1, small_triple_size * 4 + 1):
            result += ' ' * (size - mone)
            result += ' '.join(br[i])
            result += '\n'
            mone -= 1

        return result

    def get_size(self) -> int:
        """Gets board size return it"""
        return self.size

    def get_br(self) -> List[List[str]]:
        """Returns the board in the form of a list of lists"""
        return self.br

    def set_br(self, br: List[List[str]]):
        """Gets a list of a list in the form of a table and updates it"""
        self.br = br

    def cell_list(self) -> List[Tuple[int, int]]:
        """"The program returns all the coordinates of the given board"""
        cor_list = []
        for i in range(len(self.br)):
            for j in range(len(self.br[i])):
                cor_list.append((i, j))
        return cor_list

    def is_empty(self, coordinate: Tuple[int, int]) -> bool:
        """The program get a coordinate in the board and returns if it is empty"""
        row = coordinate[0]
        col = coordinate[1]
        if self.br[row][col] != 'O':
            return False
        return True

    def target_triangles(self, typ: int) -> Dict[str, List[Tuple[int, int]]]:
        """"The program returns a dictionary with keys according to the
          direction that returns a list of coordinates of the smalltriangle
          in the Star of David of the same size
          It's legal scrappers: 'N', 'NE', 'SE', 'S', 'SW', 'NW'"""
        dic = {}
        lst_n = []
        small_triple_size = int((self.size - 1) / 3)
        for i in range(small_triple_size):
            for j in range(len(self.br[i])):
                lst_n.append((i, j))
        if typ == 2:
            for i in range(small_triple_size+1):
                lst_n.append((small_triple_size, small_triple_size+i))
        dic['N'] = lst_n
        lst_ne = []
        reduces_col = -1
        for i in range(small_triple_size,small_triple_size*2):
            reduces_col += 1
            for j in range(self.size - small_triple_size, self.size-reduces_col):
                lst_ne.append((i, j))
        if typ == 2:
            for i in range(small_triple_size+1):
                lst_ne.append((small_triple_size + i, small_triple_size*2))
        dic['NE'] = lst_ne
        lst_se = []
        reduces_col = -1
        for i in range(small_triple_size*2+1, small_triple_size * 3 + 1):
            reduces_col += 1
            for j in range(len(self.br[i])-1-reduces_col, len(self.br[i])):
                lst_se.append((i, j))
        if typ == 2:
            for i in range(small_triple_size+1):
                lst_se.append((small_triple_size*2 + i, small_triple_size*2))
        dic['SE'] = lst_se
        lst_s = []
        for i in range(small_triple_size*3+1, small_triple_size * 4 + 1):
            for j in range(len(self.br[i])):
                lst_s.append((i, j))
        if typ == 2:
            for i in range(small_triple_size+1):
                lst_s.append((small_triple_size*3, small_triple_size+i))
        dic['S'] = lst_s
        lst_sw = []
        increases_col = 0
        for i in range(small_triple_size*2 + 1, small_triple_size*3 + 1):
            increases_col += 1
            for j in range(increases_col):
                lst_sw.append((i, j))
        if typ == 2:
            for i in range(small_triple_size+1):
                lst_sw.append((small_triple_size*2 + i, i))
        dic['SW'] = lst_sw
        lst_nw = []
        reduces_col = -1
        for i in range(small_triple_size, small_triple_size*2):
            reduces_col += 1
            for j in range(small_triple_size-reduces_col):
                lst_nw.append((i, j))
        if typ == 2:
            for i in range(small_triple_size+1):
                lst_nw.append((small_triple_size + i, small_triple_size - i))
        dic['NW'] = lst_nw
        return dic

    def cell_contents(self, loc: Tuple[int, int]) -> str:
        row = loc[0]
        col = loc[1]
        continn = self.br[row][col]
        return continn

    def add_balls_triple_size(self, ball: Ball, direction: str, typ: int) -> bool:
        """"Gets a ball and direction of the target triangle and adds the
         ball to that target triangle if it fails sends false If successful sends true """
        location = ball.location
        row = location[0]
        col = location[1]
        color = ball.color
        dic = self.target_triangles(typ)
        if (location in dic[direction]) and self.is_empty(location):
            self.br[row][col] = color
            return True
        else:
            return False

    def _neighbors(self, point: Tuple[int, int]) -> Dict[str, Tuple[int, int]]:
        """Six adjacent coordinates in compass order across the star's row seams."""
        row, col = point
        side = (self.size - 1) // 3

        if row == side:
            upper_left, upper_right = -side - 1, -side
        elif row == 3 * side + 1:
            upper_left, upper_right = side, side + 1
        elif row < side or 2 * side < row <= 3 * side:
            upper_left, upper_right = -1, 0
        else:
            upper_left, upper_right = 0, 1

        if row == side - 1:
            lower_right, lower_left = side + 1, side
        elif row == 3 * side:
            lower_right, lower_left = -side, -side - 1
        elif row < side - 1 or 2 * side <= row < 3 * side:
            lower_right, lower_left = 1, 0
        else:
            lower_right, lower_left = 0, -1

        return {
            'NW': (row - 1, col + upper_left),
            'NE': (row - 1, col + upper_right),
            'E': (row, col + 1),
            'SE': (row + 1, col + lower_right),
            'SW': (row + 1, col + lower_left),
            'W': (row, col - 1),
        }

    def simple_move(self, coordinate: Tuple[int, int]) -> Dict[str, List[Any]]:
        """Classify adjacent cells as empty, occupied, or outside the board."""
        result = {'allowed': [], 'banned': [], 'not_exist': []}
        cells = set(self.cell_list())
        for neighbor in self._neighbors(coordinate).values():
            if neighbor not in cells:
                result['not_exist'].append(neighbor)
            elif self.is_empty(neighbor):
                result['allowed'].append(neighbor)
            else:
                result['banned'].append(neighbor)
        return result


    def forbidden_direction(self, dic: Dict[str, List[Tuple[int, int]]],
                            current: Tuple[int, int], current_ban: Tuple[int, int]) -> str:
        """"A program receives a current member and a forbidden
         member and checks on which side the forbidden member is
          in relation to the current member"""
        row_current = current[0]
        row_current_ban = current_ban[0]
        col_current_ban = current_ban[1]
        if row_current_ban > row_current:
            word = 'S'
        if row_current_ban < row_current:
            word = 'N'
        if row_current_ban == row_current:
            word = ''
        al = dic['allowed'] + dic['banned'] + dic['not_exist']
        al.remove(current_ban)
        for cor in al:
            if row_current_ban == cor[0]:
                if col_current_ban > cor[1]:
                    word = word + 'E'
                    return word
                else:
                    word = word + 'W'
                    return word

    def next_direction(self, cor: Tuple[int, int], direction: str) -> Tuple[int, int]:
        """Return the adjacent coordinate in a compass direction."""
        return self._neighbors(cor)[direction]


    def jump_paths(self, source: Tuple[int, int]) -> Dict[Tuple[int, int], List[Tuple[int, int]]]:
        """Return a shortest sequence of landing cells for each reachable jump target.

        The moving piece vacates its starting cell. Every later hop must still
        cross a piece that occupies the middle cell on the current board.
        """
        cells = set(self.cell_list())
        if source not in cells:
            return {}
        paths = {source: [source]}
        queue = deque([source])
        while queue:
            current = queue.popleft()
            for direction, middle in self._neighbors(current).items():
                if middle not in cells or middle == source or self.is_empty(middle):
                    continue
                landing = self.next_direction(middle, direction)
                if (landing in cells and landing not in paths
                        and self.is_empty(landing)):
                    paths[landing] = paths[current] + [landing]
                    queue.append(landing)
        del paths[source]
        return paths

    def move_path(self, source: Tuple[int, int], target: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Explain a legal step or jump chain as visited cells, or return []."""
        if source not in self.cell_list():
            return []
        if target in self.simple_good_move(source):
            return [source, target]
        return self.jump_paths(source).get(target, [])

    def jumps_possible_move(self, cordinata: Tuple[int, int]) -> List[Any]:
        """Return all destinations reached by one or more valid jumps."""
        # Preserve the original set-derived ordering for existing callers.
        return list(set(self.jump_paths(cordinata)))

    def simple_good_move(self, cor: Tuple[int, int]) -> List[Any]:
        """The program receives a coordinate and returns a list of all the coordinates
         that can be reached simply by passing"""
        return self.simple_move(cor)['allowed']


    def simple_good_move_fat(self,corditata , direction, lst_simple_move):
        save_ls_good = copy.deepcopy(lst_simple_move)
        row = corditata[0]
        col = corditata[1]
        for cor in save_ls_good:
            if direction == 'N':
                if cor[0] < row:
                    lst_simple_move.remove(cor)
            if direction == 'S':
                if cor[0] > row:
                    lst_simple_move.remove(cor)
            if direction == 'NW' or direction == 'SW' :
                if cor[1] < col:
                    lst_simple_move.remove(cor)
            if direction == 'NE' or direction == 'SE' :
                if cor[1] > col:
                    lst_simple_move.remove(cor)
        return lst_simple_move


    def empty_target(self, direction: str, typ: int) -> List[Any]:
        """Gets a direction and returns all empty targets in that direction"""
        dic_targ = self.target_triangles(typ)
        lst_targ = dic_targ[direction]
        empty_lst_targ = []
        for cor in lst_targ:
            if self.is_empty(cor):
               empty_lst_targ.append(cor)
        return empty_lst_targ

    def empty_near_target(self, target: Tuple[int, int], path: list, drection: str, typ: int, ban: List[Tuple[int, int]]) -> List[Any]:
        """Gets a destination and returns path all the free places closest to it"""
        all_paths = []

        def dfs(target, path, ban):
            dic_drection = self.target_triangles(typ)
            lst_drection = dic_drection[drection]
            if self.is_empty(target) and target not in lst_drection and target not in ban:
                path.append(target)
                all_paths.append(copy.copy(path))
                path.pop()
                return
            dic_simple_move = self.simple_move(target)
            lst_simple_move = dic_simple_move['allowed'] + dic_simple_move['banned']
            lst_simple_move = self.simple_good_move_fat(target, drection, lst_simple_move)
            # print(lst_simple_move)
            for loc in lst_simple_move:
                if loc in path:
                    continue
                path.append(target)
                dfs(loc, path, ban)
                path.pop()

        dfs(target, path, ban)
        return all_paths

    def all_options_move(self, cor: Tuple[int, int]) -> List[Any]:
        """The program receives a coordinate and returns
        a list of all possible coordinates by a valid displacement
        A legal move: it is a move by me only one step to one of the
        sides or by me skipping over one soldier, several skips are possible"""

        all_options = self.simple_good_move(cor)+self.jumps_possible_move(cor)
        all_options = set(all_options)
        all_options = list(all_options)
        return all_options


    def _can_arrive_target(self, empty_target: Tuple[int, int], loc: Tuple[int, int], save_lst: list[Any]) -> bool:
        """Receives destination and location and tells if it is possible to reach the destination"""
        queue = deque([loc])
        while queue:
            current_loc = queue.popleft()
            if current_loc == empty_target:
                return True
            all_option = self.all_options_move(current_loc)
            for next_loc in all_option:
                if next_loc not in save_lst:
                    queue.append(next_loc)
                    save_lst.append(next_loc)
        return False

    def can_arrive_target(self, lst_empty_target: list, lst_loc: list) -> List[Any]:
        """Gets a list of destinations and a list of locations
         and returns a list of all destinations that can be reached"""
        new_lst_empty_target = []
        for empty_target in lst_empty_target:
            for loc in lst_loc:
                if self._can_arrive_target(empty_target, loc, []):
                    new_lst_empty_target.append(empty_target)
                    break
        return new_lst_empty_target

    def best_path(self, target: Tuple[int, int], loc: Tuple[int, int], path: list) -> List[Any]:
        """Gets a destination and location and returns the best route to the destination"""
        queue = deque([(loc, [loc])])
        visited = set()
        visited.add(loc)
        while queue:
            current_loc, current_path = queue.popleft()
            if current_loc == target:
                return current_path

            all_option = self.all_options_move(current_loc)
            for next_loc in all_option:
                if next_loc not in visited:
                    visited.add(next_loc)
                    queue.append(
                        (next_loc, current_path + [next_loc]))
        return []

    def all_best_paths(self, lst_empty_target: List[Tuple[int, int]], lst_loc: List[Tuple[int, int]]) -> List[Any]:
        """Gets a list of destinations and a list of locations and returns the best path to the destination"""
        path = []
        for empty_target in lst_empty_target:
            for loc in lst_loc:
                if not self._can_arrive_target(empty_target, loc, []):
                    continue
                if self.best_path(empty_target, loc, []):
                    path.append(self.best_path(empty_target, loc, []))
        bast_sort_path = util.find_smallest_lists(path)
        return bast_sort_path

    def replace(self, loc: Tuple[int, int], target: Tuple[int, int]) -> bool:
        """The program receives a location and destination and replaces them
        and returns false if it fails"""

        if self.is_empty(loc) or not self.is_empty(target):
            return False
        else:
            row_loc = loc[0]
            col_loc = loc[1]
            row_target = target[0]
            col_target = target[1]
            self.br[row_target][col_target] = self.br[row_loc][col_loc]
            self.br[row_loc][col_loc] = 'O'
            return True

    def me_target_taken(self, direction: str, typ: int, color: str) -> List[Any]:
        """Returns the occupied places in the destination"""
        dic_targ = self.target_triangles(typ)
        lst_targ = dic_targ[direction]
        taken_lst_targ = []
        for cor in lst_targ:
            if not self.is_empty(cor) and self.cell_contents(cor) != color:
                taken_lst_targ.append(cor)
        return taken_lst_targ

    def all_empty(self) -> List[Any]:
        """Returns all empty spaces in the board"""
        lst = []
        all_cell = self.cell_list()
        for cor in all_cell:
            if self.is_empty(cor):
                lst.append(cor)
        return lst
