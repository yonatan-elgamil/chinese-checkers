import pytest, copy
from chinese_checkers import ball, utils as util
from chinese_checkers.board import Board
from chinese_checkers.ball import  Ball
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


def test_get_br(small_board):
    assert small_board.get_br() == [['O'], ['O', 'O', 'O', 'O'], ['O', 'O', 'O'], ['O', 'O', 'O', 'O'], ['O']]
    board = Board(4)
    br = [['O'], ['O', 'Y', 'O', 'O'], ['O', 'Y', 'O'], ['O', 'Y', 'O', 'O'], ['O']]
    board.set_br(br)
    assert not small_board.get_br() == [['O'], ['O', 'Y', 'O', 'O'], ['O', 'Y', 'O'], ['O', 'Y', 'O', 'O'], ['O']]
    assert board.get_br() == [['O'], ['O', 'Y', 'O', 'O'], ['O', 'Y', 'O'], ['O', 'Y', 'O', 'O'], ['O']]


def test_cell_list(small_board):
    assert small_board.cell_list() == [(0, 0), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0),
                                    (2, 1), (2, 2), (3, 0), (3, 1), (3, 2), (3, 3), (4, 0)]


def test_is_empty(small_board):
    assert small_board.is_empty((1, 1))  # Empty cell
    board = Board(4)
    br = [['O'], ['O', 'Y', 'O', 'O'], ['O', 'Y', 'O'], ['O', 'Y', 'O', 'O'], ['O']]
    board.set_br(br)
    assert not board.is_empty((2, 1))
    assert board.is_empty((2, 2))
    assert board.is_empty((4, 0))
    assert not board.is_empty((3, 1))


def test_get_set_br(small_board):
    new_board = [['O', 'X'], ['X', 'O']]
    small_board.set_br(new_board)
    assert small_board.get_br() == new_board


def test_target_triangles(small_board):
    triangles = small_board.target_triangles(1)
    assert triangles['N'] == [(0,0)]
    triangles = small_board.target_triangles(2)
    assert triangles['N'] == [(0, 0),(1,1),(1,2)]
    triangles = small_board.target_triangles(1)
    assert triangles['S'] == [(4, 0)]
    triangles = small_board.target_triangles(2)
    assert triangles['S'] == [(4, 0), (3, 1), (3, 2)]


def test_cell_contents(small_board):
    assert small_board.cell_contents((0,0)) == 'O'
    board = Board(4)
    br = [['O'], ['O', 'Y', 'O', 'O'], ['O', 'Y', 'O'], ['O', 'Y', 'O', 'O'], ['O']]
    board.set_br(br)
    assert board.cell_contents((1,1)) == 'Y'
    assert not board.cell_contents((1,3)) == 'Y'
    assert board.cell_contents((4,0)) == 'O'


def test_add_balls_triple_size(small_board):
    bal1 = Ball("P", (0, 0))
    assert small_board.add_balls_triple_size(bal1, 'N', 1)
    bal2 = Ball("W", (1, 2))
    assert small_board.add_balls_triple_size(bal2, 'N', 2)
    bal3 = Ball("Y", (2, 2))
    assert not small_board.add_balls_triple_size(bal3, 'N', 2)
    assert small_board.cell_contents((0,0)) == "P"
    assert small_board.cell_contents((1,2)) == "W"
    assert small_board.cell_contents((2,2)) == "O"


def test_simple_move(small_board):
    dic = small_board.simple_move((0, 0))
    assert 'allowed' in dic
    assert 'banned' in dic
    assert 'not_exist' in dic
    assert (0,0) not in dic['allowed'] + dic['allowed'] + dic['not_exist']
    assert (1,1) in dic['allowed']
    assert (0,-1) in dic['not_exist']
    assert dic['banned'] == []
    board = Board(4)
    br = [['O'], ['O', 'Y', 'O', 'O'], ['O', 'Y', 'O'], ['O', 'Y', 'O', 'O'], ['O']]
    board.set_br(br)
    dic2 = board.simple_move((0, 0))
    assert (1,1) in dic2['banned']


def test_forbidden_direction(small_board):
    board = Board(4)
    br = [['O'], ['O', 'Y', 'Y', 'O'], ['O', 'Y', 'O'], ['O', 'Y', 'O', 'O'], ['O']]
    board.set_br(br)
    dic = board.simple_move((0, 0))
    direction = board.forbidden_direction(dic, (0, 0), (1,1))
    assert direction == 'SW'
    direction = board.forbidden_direction(dic, (0, 0), (1, 2))
    assert direction == 'SE'
    dic = board.simple_move((2, 0))
    direction = board.forbidden_direction(dic, (2, 0), (2, 1))
    assert direction == 'E'
    dic = board.simple_move((3, 2))
    direction = board.forbidden_direction(dic, (3, 2), (3, 1))
    assert direction == 'W'

def test_next_direction(small_board):
    assert small_board.next_direction((1,0),'E') == (1,1)
    assert small_board.next_direction((0,0),'E') == (0,1)
    assert small_board.next_direction((1,0),'W') == (1,-1)
    assert small_board.next_direction((1,2),'NW') == (0,0)
    assert small_board.next_direction((1,1),'NE') == (0,0)
    assert small_board.next_direction((1,1),'SE') == (2,1)
    assert small_board.next_direction((2,1),'SW') == (3,1)
    assert small_board.next_direction((3,1),'SE') == (4,0)
    assert small_board.next_direction((4,0),'NE') == (3,2)


def test_jumps_possible_move(small_board):
    board = Board(4)
    br = [['O'], ['O', 'Y', 'Y', 'O'], ['O', 'Y', 'O'], ['O', 'Y', 'O', 'O'], ['O']]
    board.set_br(br)
    jumps = board.jumps_possible_move((0, 0))
    assert len(jumps) == 3
    assert jumps == [(4,0),(2,0),(2,2)]

def test_simple_good_move(small_board):
    good_moves = small_board.simple_good_move((1, 1))
    assert len(good_moves) == 5
    good_moves2 = small_board.simple_good_move((0, 0))
    assert len(good_moves2) == 2
    good_moves3 = small_board.simple_good_move((1, 0))
    assert len(good_moves3) == 2
    good_moves4 = small_board.simple_good_move((3, 2))
    assert len(good_moves4) == 5


def test_empty_target(small_board):
    empty_targets = small_board.empty_target('N', 2)
    assert len(empty_targets) == 3
    empty_targets2 = small_board.empty_target('N', 1)
    assert len(empty_targets2) == 1
    board = Board(4)
    br = [['O'], ['O', 'Y', 'Y', 'O'], ['O', 'Y', 'O'], ['O', 'Y', 'O', 'O'], ['O']]
    board.set_br(br)
    empty_targets5 = board.empty_target('N', 2)
    assert len(empty_targets5) == 1


def test_empty_near_target(small_board):
    path = []
    empty_paths = small_board.empty_near_target((2, 2), [], 'N', 2, [(2, 2)])
    assert util.unique_path_destinations(empty_paths) == [(3, 3), (3, 2), (2, 1)]
    empty_paths2 = small_board.empty_near_target((1, 0), [], 'N', 1, [(1, 0)])
    assert util.unique_path_destinations(empty_paths2) == [(1, 1), (2, 0)]
    empty_paths3 = small_board.empty_near_target((4, 0), [], 'S', 1, [(4, 0)])
    assert util.unique_path_destinations(empty_paths3) == [(3, 1), (3, 2)]


def test_all_options_move(small_board):
    all_options = small_board.all_options_move((1, 1))
    assert len(all_options) == 5
    assert all_options  == [(1, 2), (2, 1), (0, 0), (2, 0), (1, 0)]
    all_options2 = small_board.all_options_move((0, 0))
    assert all_options2 == [(1, 1), (1, 2)]
    board = Board(4)
    br = [['O'], ['O', 'Y', 'Y', 'O'], ['O', 'Y', 'O'], ['O', 'Y', 'O', 'O'], ['O']]
    board.set_br(br)
    all_options3 = board.all_options_move((0, 0))
    assert all_options3 == [(4, 0), (2, 0), (2, 2)]


def test_can_arrive_target(small_board):
    empty_targets = small_board.empty_target('N', 2)
    lst_loc = [(1, 1)]
    reachable_targets = small_board.can_arrive_target(empty_targets, lst_loc)
    assert len(reachable_targets) > 0
    board = Board(4)
    br = [['O'], ['O', 'Y', 'Y', 'O'], ['O', 'Y', 'O'], ['O', 'Y', 'O', 'O'], ['O']]
    board.set_br(br)
    reachable_targets = board.can_arrive_target([(0,0)], [(4,0)])
    assert len(reachable_targets) > 0
    board = Board(4)
    br = [['O'], ['O', 'Y', 'Y', 'O'], ['Y', 'Y', 'Y'], ['O', 'Y', 'O', 'O'], ['O']]
    board.set_br(br)
    reachable_targets = board.can_arrive_target([(0,0)], [(4,0)])
    assert len(reachable_targets) == 0



def test_best_path(small_board):
    best_path = small_board.best_path((2, 2), (1, 1), [])
    assert len(best_path) == 3
    best_path = small_board.best_path((3, 2), (0, 0), [])
    assert len(best_path) == 4
    board = Board(4)
    br = [['O'], ['O', 'O', 'Y', 'O'], ['O', 'Y', 'Y'], ['O', 'Y', 'O', 'O'], ['O']]
    board.set_br(br)
    best_path = board.best_path((3, 0), (1, 1), [])
    assert len(best_path) == 2
    best_path = board.best_path((3, 0), (0, 0), [])
    assert len(best_path) == 3


def test_all_best_paths(small_board):
    best_path = small_board.all_best_paths([(1, 1),(0, 0)],[(2, 2),(3, 2)])
    assert len(best_path[0]) == 3
    board = Board(4)
    br = [['O'], ['O', 'O', 'Y', 'O'], ['Y', 'Y', 'Y'], ['O', 'Y', 'O', 'O'], ['O']]
    board.set_br(br)
    best_path = board.all_best_paths([(1, 1),(0, 0)],[(3, 0)])
    assert len(best_path[0]) == 2


def test_replace(small_board):
    assert not small_board.replace((1, 1), (2, 2))
    board = Board(4)
    br = [['O'], ['O', 'O', 'Y', 'O'], ['Y', 'Y', 'Y'], ['O', 'Y', 'O', 'O'], ['O']]
    board.set_br(br)
    assert board.replace((1, 2), (3, 2))
    br = [['O'], ['O', 'O', 'Y', 'O'], ['Y', 'Y', 'Y'], ['O', 'Y', 'O', 'O'], ['O']]
    board.set_br(br)
    assert board.replace((1, 2), (4, 0))
    br = [['O'], ['O', 'O', 'Y', 'O'], ['Y', 'Y', 'Y'], ['O', 'Y', 'O', 'O'], ['O']]
    board.set_br(br)
    assert not board.replace((1, 1), (3, 2))
    br = [['O'], ['O', 'O', 'Y', 'O'], ['Y', 'Y', 'Y'], ['O', 'Y', 'O', 'O'], ['O']]
    board.set_br(br)
    assert not board.replace((1, 2), (3, 1))


def test_me_target_taken(small_board):
    taken_targets = small_board.me_target_taken('N', 2, 'Y')
    assert len(taken_targets) == 0
    board =Board(4)
    br = [['O'], ['O', 'O', 'Y', 'O'], ['Y', 'Y', 'Y'], ['O', 'Y', 'O', 'O'], ['O']]
    board.set_br(br)
    taken_targets = board.me_target_taken('N', 2, 'Y')
    assert len(taken_targets) == 0
    taken_targets = board.me_target_taken('N', 2, 'G')
    assert len(taken_targets) == 1
    taken_targets = board.me_target_taken('S', 2, 'G')
    assert len(taken_targets) == 1


def test_all_empty(small_board):
    empty_cells = small_board.all_empty()
    assert len(empty_cells) == 13
    board = Board(4)
    br = [['O'], ['O', 'O', 'Y', 'O'], ['Y', 'Y', 'Y'], ['O', 'Y', 'O', 'O'], ['O']]
    board.set_br(br)
    empty_cells = board.all_empty()
    assert len(empty_cells) == 8