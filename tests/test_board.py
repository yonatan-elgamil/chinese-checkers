import pytest, copy
from chinese_checkers import ball, utils as util
from chinese_checkers.board import Board
from chinese_checkers.ball import Ball
from chinese_checkers.ai import ComputerStrategy
from types import SimpleNamespace


def strategy_for(board):
    return ComputerStrategy(SimpleNamespace(board=board, players=[]))
@pytest.fixture
def small_board():
    return Board(4)

@pytest.fixture
def medium_board():
    return Board(7)

@pytest.fixture
def large_board():
    return Board(10)

@pytest.fixture
def extra_large_board():
    return Board(13)

def test_board_creation(small_board, medium_board, large_board, extra_large_board):
    assert small_board.get_size() == 4
    assert medium_board.get_size() == 7
    assert large_board.get_size() == 10
    assert extra_large_board.get_size() == 13

def test_get_color_grid(small_board):
    assert small_board.get_color_grid() == [['O'], ['O', 'O', 'O', 'O'], ['O', 'O', 'O'], ['O', 'O', 'O', 'O'], ['O']]
    board = Board(4)
    br = [['O'], ['O', 'Y', 'O', 'O'], ['O', 'Y', 'O'], ['O', 'Y', 'O', 'O'], ['O']]
    board.load_color_grid(br)
    assert not small_board.get_color_grid() == [['O'], ['O', 'Y', 'O', 'O'], ['O', 'Y', 'O'], ['O', 'Y', 'O', 'O'], ['O']]
    assert board.get_color_grid() == [['O'], ['O', 'Y', 'O', 'O'], ['O', 'Y', 'O'], ['O', 'Y', 'O', 'O'], ['O']]

def test_cell_coordinates(small_board):
    assert small_board.cell_coordinates() == [(0, 0), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0),
                                    (2, 1), (2, 2), (3, 0), (3, 1), (3, 2), (3, 3), (4, 0)]

def test_is_empty(small_board):
    assert small_board.is_empty((1, 1))  # Empty cell
    board = Board(4)
    br = [['O'], ['O', 'Y', 'O', 'O'], ['O', 'Y', 'O'], ['O', 'Y', 'O', 'O'], ['O']]
    board.load_color_grid(br)
    assert not board.is_empty((2, 1))
    assert board.is_empty((2, 2))
    assert board.is_empty((4, 0))
    assert not board.is_empty((3, 1))

def test_load_color_grid(small_board):
    new_board = [['O', 'X'], ['X', 'O']]
    small_board.load_color_grid(new_board)
    assert small_board.get_color_grid() == new_board

def test_triangle_cells(small_board):
    triangles = small_board.triangle_cells(1)
    assert triangles['N'] == [(0,0)]
    triangles = small_board.triangle_cells(2)
    assert triangles['N'] == [(0, 0),(1,1),(1,2)]
    triangles = small_board.triangle_cells(1)
    assert triangles['S'] == [(4, 0)]
    triangles = small_board.triangle_cells(2)
    assert triangles['S'] == [(4, 0), (3, 1), (3, 2)]

def test_color_at(small_board):
    assert small_board.color_at((0,0)) == 'O'
    board = Board(4)
    br = [['O'], ['O', 'Y', 'O', 'O'], ['O', 'Y', 'O'], ['O', 'Y', 'O', 'O'], ['O']]
    board.load_color_grid(br)
    assert board.color_at((1,1)) == 'Y'
    assert not board.color_at((1,3)) == 'Y'
    assert board.color_at((4,0)) == 'O'

def test_add_ball_to_triangle(small_board):
    bal1 = Ball("P", (0, 0))
    assert small_board.add_ball_to_triangle(bal1, 'N', 1)
    bal2 = Ball("W", (1, 2))
    assert small_board.add_ball_to_triangle(bal2, 'N', 2)
    bal3 = Ball("Y", (2, 2))
    assert not small_board.add_ball_to_triangle(bal3, 'N', 2)
    assert small_board.color_at((0,0)) == "P"
    assert small_board.color_at((1,2)) == "W"
    assert small_board.color_at((2,2)) == "O"

def test_classify_neighbors(small_board):
    dic = small_board.classify_neighbors((0, 0))
    assert 'allowed' in dic
    assert 'banned' in dic
    assert 'not_exist' in dic
    assert (0,0) not in dic['allowed'] + dic['allowed'] + dic['not_exist']
    assert (1,1) in dic['allowed']
    assert (0,-1) in dic['not_exist']
    assert dic['banned'] == []
    board = Board(4)
    br = [['O'], ['O', 'Y', 'O', 'O'], ['O', 'Y', 'O'], ['O', 'Y', 'O', 'O'], ['O']]
    board.load_color_grid(br)
    dic2 = board.classify_neighbors((0, 0))
    assert (1,1) in dic2['banned']

def test_direction_between(small_board):
    board = Board(4)
    br = [['O'], ['O', 'Y', 'Y', 'O'], ['O', 'Y', 'O'], ['O', 'Y', 'O', 'O'], ['O']]
    board.load_color_grid(br)
    dic = board.classify_neighbors((0, 0))
    direction = board.direction_between(dic, (0, 0), (1,1))
    assert direction == 'SW'
    direction = board.direction_between(dic, (0, 0), (1, 2))
    assert direction == 'SE'
    dic = board.classify_neighbors((2, 0))
    direction = board.direction_between(dic, (2, 0), (2, 1))
    assert direction == 'E'
    dic = board.classify_neighbors((3, 2))
    direction = board.direction_between(dic, (3, 2), (3, 1))
    assert direction == 'W'

def test_adjacent_coordinate(small_board):
    assert small_board.adjacent_coordinate((1,0),'E') == (1,1)
    assert small_board.adjacent_coordinate((0,0),'E') == (0,1)
    assert small_board.adjacent_coordinate((1,0),'W') == (1,-1)
    assert small_board.adjacent_coordinate((1,2),'NW') == (0,0)
    assert small_board.adjacent_coordinate((1,1),'NE') == (0,0)
    assert small_board.adjacent_coordinate((1,1),'SE') == (2,1)
    assert small_board.adjacent_coordinate((2,1),'SW') == (3,1)
    assert small_board.adjacent_coordinate((3,1),'SE') == (4,0)
    assert small_board.adjacent_coordinate((4,0),'NE') == (3,2)

def test_jump_destinations(small_board):
    board = Board(4)
    br = [['O'], ['O', 'Y', 'Y', 'O'], ['O', 'Y', 'O'], ['O', 'Y', 'O', 'O'], ['O']]
    board.load_color_grid(br)
    jumps = board.jump_destinations((0, 0))
    assert len(jumps) == 3
    assert jumps == [(4,0),(2,0),(2,2)]

def test_step_destinations(small_board):
    good_moves = small_board.step_destinations((1, 1))
    assert len(good_moves) == 5
    good_moves2 = small_board.step_destinations((0, 0))
    assert len(good_moves2) == 2
    good_moves3 = small_board.step_destinations((1, 0))
    assert len(good_moves3) == 2
    good_moves4 = small_board.step_destinations((3, 2))
    assert len(good_moves4) == 5

def test_empty_triangle_cells(small_board):
    empty_targets = small_board.empty_triangle_cells('N', 2)
    assert len(empty_targets) == 3
    empty_targets2 = small_board.empty_triangle_cells('N', 1)
    assert len(empty_targets2) == 1
    board = Board(4)
    br = [['O'], ['O', 'Y', 'Y', 'O'], ['O', 'Y', 'O'], ['O', 'Y', 'O', 'O'], ['O']]
    board.load_color_grid(br)
    empty_targets5 = board.empty_triangle_cells('N', 2)
    assert len(empty_targets5) == 1

def test_paths_to_empty_cells_near_goal(small_board):
    path = []
    empty_paths = strategy_for(small_board).paths_to_empty_cells_near_goal((2, 2), 'N', 2, [(2, 2)])
    assert util.unique_path_destinations(empty_paths) == [(3, 3), (3, 2), (2, 1)]
    empty_paths2 = strategy_for(small_board).paths_to_empty_cells_near_goal((1, 0), 'N', 1, [(1, 0)])
    assert util.unique_path_destinations(empty_paths2) == [(1, 1), (2, 0)]
    empty_paths3 = strategy_for(small_board).paths_to_empty_cells_near_goal((4, 0), 'S', 1, [(4, 0)])
    assert util.unique_path_destinations(empty_paths3) == [(3, 1), (3, 2)]

def test_legal_destinations(small_board):
    all_options = small_board.legal_destinations((1, 1))
    assert len(all_options) == 5
    assert all_options  == [(1, 2), (2, 1), (0, 0), (2, 0), (1, 0)]
    all_options2 = small_board.legal_destinations((0, 0))
    assert all_options2 == [(1, 1), (1, 2)]
    board = Board(4)
    br = [['O'], ['O', 'Y', 'Y', 'O'], ['O', 'Y', 'O'], ['O', 'Y', 'O', 'O'], ['O']]
    board.load_color_grid(br)
    all_options3 = board.legal_destinations((0, 0))
    assert all_options3 == [(4, 0), (2, 0), (2, 2)]

def test_reachable_targets(small_board):
    empty_targets = small_board.empty_triangle_cells('N', 2)
    lst_loc = [(1, 1)]
    reachable_targets = strategy_for(small_board).reachable_targets(empty_targets, lst_loc)
    assert len(reachable_targets) > 0
    board = Board(4)
    br = [['O'], ['O', 'Y', 'Y', 'O'], ['O', 'Y', 'O'], ['O', 'Y', 'O', 'O'], ['O']]
    board.load_color_grid(br)
    reachable_targets = strategy_for(board).reachable_targets([(0,0)], [(4,0)])
    assert len(reachable_targets) > 0
    board = Board(4)
    br = [['O'], ['O', 'Y', 'Y', 'O'], ['Y', 'Y', 'Y'], ['O', 'Y', 'O', 'O'], ['O']]
    board.load_color_grid(br)
    reachable_targets = strategy_for(board).reachable_targets([(0,0)], [(4,0)])
    assert len(reachable_targets) == 0

def test_find_shortest_path(small_board):
    best_path = strategy_for(small_board).find_shortest_path((1, 1), (2, 2))
    assert len(best_path) == 3
    best_path = strategy_for(small_board).find_shortest_path((0, 0), (3, 2))
    assert len(best_path) == 4
    board = Board(4)
    br = [['O'], ['O', 'O', 'Y', 'O'], ['O', 'Y', 'Y'], ['O', 'Y', 'O', 'O'], ['O']]
    board.load_color_grid(br)
    best_path = strategy_for(board).find_shortest_path((1, 1), (3, 0))
    assert len(best_path) == 2
    best_path = strategy_for(board).find_shortest_path((0, 0), (3, 0))
    assert len(best_path) == 3

def test_shortest_paths_to_targets(small_board):
    best_path = strategy_for(small_board).shortest_paths_to_targets([(1, 1),(0, 0)],[(2, 2),(3, 2)])
    assert len(best_path[0]) == 3
    board = Board(4)
    br = [['O'], ['O', 'O', 'Y', 'O'], ['Y', 'Y', 'Y'], ['O', 'Y', 'O', 'O'], ['O']]
    board.load_color_grid(br)
    best_path = strategy_for(board).shortest_paths_to_targets([(1, 1),(0, 0)],[(3, 0)])
    assert len(best_path[0]) == 2

def test_move_ball(small_board):
    assert not small_board.move_ball((1, 1), (2, 2))
    board = Board(4)
    br = [['O'], ['O', 'O', 'Y', 'O'], ['Y', 'Y', 'Y'], ['O', 'Y', 'O', 'O'], ['O']]
    board.load_color_grid(br)
    assert board.move_ball((1, 2), (3, 2))
    br = [['O'], ['O', 'O', 'Y', 'O'], ['Y', 'Y', 'Y'], ['O', 'Y', 'O', 'O'], ['O']]
    board.load_color_grid(br)
    assert board.move_ball((1, 2), (4, 0))
    br = [['O'], ['O', 'O', 'Y', 'O'], ['Y', 'Y', 'Y'], ['O', 'Y', 'O', 'O'], ['O']]
    board.load_color_grid(br)
    assert not board.move_ball((1, 1), (3, 2))
    br = [['O'], ['O', 'O', 'Y', 'O'], ['Y', 'Y', 'Y'], ['O', 'Y', 'O', 'O'], ['O']]
    board.load_color_grid(br)
    assert not board.move_ball((1, 2), (3, 1))

def test_opponent_triangle_cells(small_board):
    taken_targets = small_board.opponent_triangle_cells('N', 2, 'Y')
    assert len(taken_targets) == 0
    board =Board(4)
    br = [['O'], ['O', 'O', 'Y', 'O'], ['Y', 'Y', 'Y'], ['O', 'Y', 'O', 'O'], ['O']]
    board.load_color_grid(br)
    taken_targets = board.opponent_triangle_cells('N', 2, 'Y')
    assert len(taken_targets) == 0
    taken_targets = board.opponent_triangle_cells('N', 2, 'G')
    assert len(taken_targets) == 1
    taken_targets = board.opponent_triangle_cells('S', 2, 'G')
    assert len(taken_targets) == 1

def test_empty_cells(small_board):
    empty_cells = small_board.empty_cells()
    assert len(empty_cells) == 13
    board = Board(4)
    br = [['O'], ['O', 'O', 'Y', 'O'], ['Y', 'Y', 'Y'], ['O', 'Y', 'O', 'O'], ['O']]
    board.load_color_grid(br)
    empty_cells = board.empty_cells()
    assert len(empty_cells) == 8