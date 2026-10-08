"""Star-shaped board containing Ball objects, geometry and legal moves."""

from collections import deque
from typing import Any, Dict, List, Optional, Tuple

from .ball import Ball

Coordinate = Tuple[int, int]


class Board:
    """Own the actual pieces; an empty cell contains None."""

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
                total_list[i].append(None)
        mone_row = small_triple_size
        reduces_col = -1
        for i in range(mone_row,mone_row + small_triple_size+1):
            reduces_col += 1
            for j in range(col_size-reduces_col):
                total_list[i].append(None)
        mone_row += small_triple_size+1
        increases_col = -1
        for i in range(mone_row,mone_row + small_triple_size):
            increases_col += 1
            for j in range(col_size-small_triple_size+1+increases_col):
                total_list[i].append(None)
        mone_row += small_triple_size
        reduces_col = -1
        for i in range(mone_row,mone_row + small_triple_size):
            reduces_col += 1
            for j in range(small_triple_size - reduces_col):
                total_list[i].append(None)
        self._cells = total_list

    def __str__(self) -> str:
        """Render the same star-shaped color display used by the terminal."""
        result = ""
        size = self.size
        br = self.get_color_grid()

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
        """Return the board size used to construct its geometry."""
        return self.size

    def get_cells(self) -> List[List[Optional[Ball]]]:
        """Return copied rows containing the board's actual Ball references."""
        return [row[:] for row in self._cells]

    def get_color_grid(self) -> List[List[str]]:
        """Return a detached color snapshot for display and legacy JSON saves."""
        return [[ball.color if ball is not None else 'O' for ball in row]
                for row in self._cells]

    def load_color_grid(self, colors: List[List[str]], balls=None) -> None:
        """Import a color grid, reusing supplied Ball objects when they match.

        Color strings exist only at the persistence and test-fixture boundary.
        Every occupied cell in the resulting board contains an actual Ball.
        """
        existing = {(ball.color, ball.location): ball
                    for pieces in (balls or {}).values() for ball in pieces}
        self._cells = []
        for row_index, row in enumerate(colors):
            cells = []
            for column, color in enumerate(row):
                location = (row_index, column)
                ball = None
                if color != 'O':
                    ball = existing.get((color, location))
                    if ball is None:
                        ball = Ball(color, location)
                cells.append(ball)
            self._cells.append(cells)

    def get_ball(self, coordinate: Coordinate) -> Optional[Ball]:
        """Return the exact piece at a coordinate, or None for an empty cell."""
        row, column = coordinate
        return self._cells[row][column]

    def color_at(self, coordinate: Coordinate) -> str:
        """Return a piece's color, or 'O' for display of an empty cell."""
        ball = self.get_ball(coordinate)
        return ball.color if ball is not None else 'O'

    def place_ball(self, ball: Ball) -> bool:
        """Place an existing Ball in an empty board cell."""
        if ball.location not in self.cell_coordinates() or not self.is_empty(ball.location):
            return False
        row, column = ball.location
        self._cells[row][column] = ball
        return True

    def remove_ball(self, coordinate: Coordinate) -> Optional[Ball]:
        """Remove and return a piece; used on isolated computer simulations."""
        row, column = coordinate
        ball = self._cells[row][column]
        self._cells[row][column] = None
        return ball

    def is_empty(self, coordinate: Coordinate) -> bool:
        return self.get_ball(coordinate) is None

    def to_dict(self) -> Dict[str, Any]:
        """Keep the original saved board shape and its color-based format."""
        return {'size': self.size, 'br': self.get_color_grid()}

    def cell_coordinates(self) -> List[Tuple[int, int]]:
        """Return every valid board coordinate in row order."""
        cor_list = []
        for i in range(len(self._cells)):
            for j in range(len(self._cells[i])):
                cor_list.append((i, j))
        return cor_list

    def triangle_cells(self, typ: int) -> Dict[str, List[Tuple[int, int]]]:
        """Return the six corner triangles for the requested set size."""
        dic = {}
        lst_n = []
        small_triple_size = int((self.size - 1) / 3)
        for i in range(small_triple_size):
            for j in range(len(self._cells[i])):
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
            for j in range(len(self._cells[i])-1-reduces_col, len(self._cells[i])):
                lst_se.append((i, j))
        if typ == 2:
            for i in range(small_triple_size+1):
                lst_se.append((small_triple_size*2 + i, small_triple_size*2))
        dic['SE'] = lst_se
        lst_s = []
        for i in range(small_triple_size*3+1, small_triple_size * 4 + 1):
            for j in range(len(self._cells[i])):
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

    def add_ball_to_triangle(self, ball: Ball, direction: str, triangle_type: int) -> bool:
        """Place the actual piece only if it belongs to this starting triangle."""
        if ball.location not in self.triangle_cells(triangle_type)[direction]:
            return False
        return self.place_ball(ball)

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

    def classify_neighbors(self, coordinate: Tuple[int, int]) -> Dict[str, List[Any]]:
        """Classify adjacent cells as empty, occupied, or outside the board."""
        result = {'allowed': [], 'banned': [], 'not_exist': []}
        cells = set(self.cell_coordinates())
        for neighbor in self._neighbors(coordinate).values():
            if neighbor not in cells:
                result['not_exist'].append(neighbor)
            elif self.is_empty(neighbor):
                result['allowed'].append(neighbor)
            else:
                result['banned'].append(neighbor)
        return result

    def direction_between(self, dic: Dict[str, List[Tuple[int, int]]],
                            current: Tuple[int, int], current_ban: Tuple[int, int]) -> str:
        """Find the compass direction of a classified neighboring cell."""
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

    def adjacent_coordinate(self, cor: Tuple[int, int], direction: str) -> Tuple[int, int]:
        """Return the adjacent coordinate in a compass direction."""
        return self._neighbors(cor)[direction]

    def jump_paths(self, source: Tuple[int, int]) -> Dict[Tuple[int, int], List[Tuple[int, int]]]:
        """Return a shortest sequence of landing cells for each reachable jump target.

        The moving piece vacates its starting cell. Every later hop must still
        cross a piece that occupies the middle cell on the current board.
        """
        cells = set(self.cell_coordinates())
        if source not in cells:
            return {}
        paths = {source: [source]}
        queue = deque([source])
        while queue:
            current = queue.popleft()
            for direction, middle in self._neighbors(current).items():
                if middle not in cells or middle == source or self.is_empty(middle):
                    continue
                landing = self.adjacent_coordinate(middle, direction)
                if (landing in cells and landing not in paths
                        and self.is_empty(landing)):
                    paths[landing] = paths[current] + [landing]
                    queue.append(landing)
        del paths[source]
        return paths

    def move_path(self, source: Tuple[int, int], target: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Explain a legal step or jump chain as visited cells, or return []."""
        if source not in self.cell_coordinates():
            return []
        if target in self.step_destinations(source):
            return [source, target]
        return self.jump_paths(source).get(target, [])

    def jump_destinations(self, cordinata: Tuple[int, int]) -> List[Any]:
        """Return all destinations reached by one or more valid jumps."""
        # Preserve the original set-derived ordering for existing callers.
        return list(set(self.jump_paths(cordinata)))

    def step_destinations(self, cor: Tuple[int, int]) -> List[Any]:
        """Return the empty cells reachable by one adjacent step."""
        return self.classify_neighbors(cor)['allowed']

    def empty_triangle_cells(self, direction: str, typ: int) -> List[Any]:
        """Return empty cells inside a given corner triangle."""
        goal_directions = self.triangle_cells(typ)
        lst_targ = goal_directions[direction]
        empty_lst_targ = []
        for cor in lst_targ:
            if self.is_empty(cor):
               empty_lst_targ.append(cor)
        return empty_lst_targ

    def legal_destinations(self, cor: Tuple[int, int]) -> List[Any]:
        """Return all destinations reachable by one step or a jump chain."""

        all_options = self.step_destinations(cor)+self.jump_destinations(cor)
        all_options = set(all_options)
        all_options = list(all_options)
        return all_options

    def move_ball(self, source: Coordinate, target: Coordinate) -> bool:
        """Relocate the same Ball and update its position in one operation.

        Game checks ownership and move legality before calling this method.
        """
        if self.is_empty(source) or not self.is_empty(target):
            return False
        ball = self.get_ball(source)
        source_row, source_column = source
        target_row, target_column = target
        self._cells[target_row][target_column] = ball
        self._cells[source_row][source_column] = None
        ball.move_to(target)
        return True

    def opponent_triangle_cells(self, direction: str, typ: int, color: str) -> List[Any]:
        """Return triangle cells occupied by a different color."""
        goal_directions = self.triangle_cells(typ)
        lst_targ = goal_directions[direction]
        taken_lst_targ = []
        for cor in lst_targ:
            if not self.is_empty(cor) and self.color_at(cor) != color:
                taken_lst_targ.append(cor)
        return taken_lst_targ

    def empty_cells(self) -> List[Any]:
        """Return every empty coordinate on the current board."""
        lst = []
        all_cell = self.cell_coordinates()
        for cor in all_cell:
            if self.is_empty(cor):
                lst.append(cor)
        return lst

