import copy

import pytest
import pytest
from chinese_checkers import ball
from chinese_checkers import game as game1
from chinese_checkers.ball import Ball
from chinese_checkers.game import Game, Board, Player, Ball

@pytest.fixture
def setup_game():
    # Set up a sample game for testing
    board = Board(7)  # Create a board object
    br = [['W'], ['W', 'W'], ['Y', 'Y', 'O', 'O', 'O', 'R', 'R'], ['Y', 'O', 'O', 'O', 'O', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O'],
          ['O']]
    board.load_color_grid(br)
    balls = {
        'W': [Ball('W',(0,0)), Ball('W',(1,0)), Ball('W',(1,1))],
        'Y': [Ball('Y',(2, 0)), Ball('Y',(2, 1)), Ball('Y',(3,0))],
        'R': [Ball('R',(2,5)), Ball('R',(2,6)), Ball('R',(3,5))]}
    # Create player objects
    player1 = Player('Alice',0,0, ['W'])
    player2 = Player('computer',0,0, ['Y'])
    player3 = Player('Charlie',0,0, ['R'])
    players = [player1, player2, player3]
    # Create a Game object
    gamee = game1.Game(board, balls, players, 0)
    return gamee

@pytest.fixture
def setup2_game():
    # Set up a sample game for testing
    board = Board(7)  # Create a board object
    br = [['W'], ['W', 'W'], ['Y', 'Y', 'O', 'O', 'O', 'R', 'R'], ['Y', 'O', 'O', 'O', 'O', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O', 'O'], ['G', 'G'],
          ['G']]
    board.load_color_grid(br)
    balls = {
        'W': [Ball('W',(0,0)), Ball('W',(1,0)), Ball('W',(1,1))],
        'Y': [Ball('Y',(2, 0)), Ball('Y',(2, 1)), Ball('Y',(3,0))],
        'G': [Ball('G', (8, 0)), Ball('G', (7, 0)), Ball('G', (7, 1))],
        'R': [Ball('R',(2,5)), Ball('R',(2,6)), Ball('R',(3,5))]}

    # Create player objects
    player1 = Player('Alice',0,0, ['W', 'Y'])
    player2 = Player('Bob',0,0, ['G', 'R'])
    players = [player1, player2]
    # Create a Game object
    game2 = game1.Game(board, balls, players, 0)
    return game2

@pytest.fixture
def setup3_game():
    # Set up a sample game for testing
    board = Board(7)  # Create a board object
    br = [['W'], ['W', 'W'], ['O', 'O', 'W', 'W', 'W', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'],
          ['O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'G', 'G', 'G', 'O', 'O'],
          ['G', 'G'], ['G']]

    board.load_color_grid(br)
    balls = {
        'W': [Ball('W', (0, 0)), Ball('W', (1, 0)), Ball('W', (1, 1)),
              Ball('W', (2, 2)), Ball('W', (2, 3)), Ball('W', (2, 4))],
        'G': [Ball('G', (8, 0)), Ball('G', (7, 0)), Ball('G', (7, 1)),
              Ball('W', (6, 2)), Ball('W', (6, 3)), Ball('W', (6, 4))]}

    # Create player objects
    player1 = Player('Alice', 0, 0, ['W'])
    player2 = Player('Bob', 0, 0, ['G'])
    players = [player1, player2]
    # Create a Game object
    game3 = game1.Game(board, balls, players, 0)
    return game3

@pytest.fixture
def setup4_game():
    # Set up a sample game for testing
    board = Board(7)  # Create a board object
    br = [['W'], ['W', 'W'], ['Y', 'Y', 'O', 'O', 'O', 'O', 'O'], ['Y', 'O', 'O', 'O', 'O', 'O'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'R'], ['O', 'O', 'O', 'O', 'O', 'R', 'R'], ['G', 'G'],
          ['G']]
    board.load_color_grid(br)
    balls = {
        'W': [Ball('W',(0,0)), Ball('W',(1,0)), Ball('W',(1,1))],
        'Y': [Ball('Y',(2, 0)), Ball('Y',(2, 1)), Ball('Y',(3,0))],
        'G': [Ball('G', (8, 0)), Ball('G', (7, 0)), Ball('G', (7, 1))],
        'R': [Ball('R',(7,5)), Ball('R',(7,6)), Ball('R',(6,5))]}

    # Create player objects
    player1 = Player('Alice',0,0, ['W'])
    player2 = Player('dor',0,0, ['G'])
    player3 = Player('Bob',0,0, ['Y'])
    player4 = Player('san',0,0, ['R'])
    players = [player1, player2, player3, player4]
    # Create a Game object
    game2 = game1.Game(board, balls, players, 1)
    return game2

def test_dic_color_loc(setup_game):
    # Test the dic_targ method of the Game class
    starting_directions = setup_game.starting_directions
    assert starting_directions['W'] == 'N'
    assert starting_directions['Y'] == 'NW'
    assert starting_directions['R'] == 'NE'

def test_describe_player_colors(setup_game):

    player = Player('TestPlayer', 0, 0, ['W'])
    game = setup_game
    assert game.describe_player_colors(player) == 'W'
    player = Player('TestPlayer', 0, 0, ['W', 'Y'])
    game = setup_game
    assert game.describe_player_colors(player) == 'W and Y'
    player = Player('TestPlayer', 0, 0, ['W', 'Y', 'R'])
    game = setup_game
    assert game.describe_player_colors(player) == 'W and Y and R'

def test_positions_for_color(setup_game):
    assert setup_game.positions_for_color('W') == [(0,0),(1,0),(1,1)]
    assert setup_game.positions_for_color('Y') == [(2,0),(2,1),(3,0)]

def test_positions_for_player(setup_game, setup2_game):
    playr = setup_game.players[0]
    assert setup_game.positions_for_player(playr) == [(0,0),(1,0),(1,1)]
    playr = setup_game.players[1]
    assert setup_game.positions_for_player(playr) == [(2,0),(2,1),(3,0)]
    playr = setup2_game.players[0]
    assert setup_game.positions_for_player(playr) == [(0,0),(1,0),(1,1),(2,0),(2,1),(3,0)]

def test_goal_directions(setup_game):
    assert setup_game.goal_directions()['W'] == 'S'
    assert setup_game.goal_directions()['Y'] == 'SE'
    assert setup_game.goal_directions()['R'] == 'SW'

def test_goal_rows(setup_game):
   assert setup_game.computer_strategy._goal_rows(1,'S') == [[(8,0)],[(7,0),(7,1)]]
   assert setup_game.computer_strategy._goal_rows(1,'N') == [[(0,0)],[(1,0),(1,1)]]

def test_filter_settled_balls(setup_game, setup2_game, setup3_game):
    gam = copy.deepcopy(setup_game)
    gam.board.load_color_grid([['O'], ['W', 'W'], ['Y', 'Y', 'O', 'O', 'O', 'R', 'R'], ['Y', 'O', 'O', 'O', 'O', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O'],
          ['W']])
    assert gam.computer_strategy.filter_settled_balls([(1,0),(1,1),(8,0)], ['W'], 1) == [(1,0),(1,1)]
    gam.board.load_color_grid([['O'], ['W', 'W'], ['Y', 'Y', 'O', 'O', 'O', 'R', 'R'], ['Y', 'O', 'O', 'O', 'O', 'R'],
                      ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O', 'O'],
                      ['W', 'O'],
                      ['O']])
    assert gam.computer_strategy.filter_settled_balls([(1,0),(1,1),(7,0)], ['W'], 1) == [(1,0),(1,1)]
    gam = copy.deepcopy(setup3_game)
    gam.board.load_color_grid([['O'], ['W', 'W'], ['O', 'O', 'W', 'W', 'W', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'],
          ['O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'G', 'G', 'G', 'O', 'O'],
          ['G', 'G'], ['W']])
    assert gam.computer_strategy.filter_settled_balls([(1,0),(1,1),(2,2),(2,3),(2,4),(8,0)], ['W'], 1) == [(1,0),(1,1),(2,2),(2,3),(2,4)]
    gam = copy.deepcopy(setup3_game)
    gam.board.load_color_grid([['O'], ['W', 'W'], ['O', 'O', 'W', 'W', 'W', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'],
                      ['O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'G', 'G', 'G', 'O', 'O'],
                      ['W', 'G'], ['G']])
    assert gam.computer_strategy.filter_settled_balls([(1, 0), (1, 1), (2, 2), (2, 3), (2, 4), (8, 0)], ['W'], 1) == [(1, 0), (1, 1),
                                                                                                       (2, 2), (2, 3),
                                                                                                       (2, 4),(8, 0)]
def test_find_goal_rearrangement_move(setup_game, setup3_game):
    gam = copy.deepcopy(setup3_game)
    gam.board.load_color_grid([['O'], ['W', 'W'], ['O', 'O', 'W', 'W', 'W', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'],
                      ['O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'G', 'G', 'G', 'O', 'O'],
                      ['W', 'G'], ['G']])
    assert gam.computer_strategy.find_goal_rearrangement_move(1,'W') == []
    gam = copy.deepcopy(setup3_game)
    gam.board.load_color_grid([['O'], ['O', 'W'], ['O', 'O', 'W', 'W', 'W', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'],
                          ['O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'],
                          ['O', 'O', 'G', 'G', 'W', 'O', 'O'],
                          ['W', 'O'], ['G']])
    assert gam.computer_strategy.find_goal_rearrangement_move(1, 'W') == []
    gam = copy.deepcopy(setup3_game)
    gam.board.load_color_grid([['O'], ['O', 'W'], ['O', 'O', 'W', 'W', 'W', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'],
                      ['O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'],
                      ['O', 'O', 'G', 'G', 'W', 'O', 'O'],
                      ['W', 'O'], ['W']])
    assert gam.computer_strategy.find_goal_rearrangement_move(1, 'W') == [(6,4),(7,1)]
    gam = copy.deepcopy(setup3_game)
    gam.board.load_color_grid([['O'], ['O', 'W'], ['O', 'O', 'W', 'W', 'W', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'],
                      ['O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'],
                      ['O', 'O', 'G', 'G', 'W', 'O', 'O'],
                      ['W', 'G'], ['W']])
    assert gam.computer_strategy.find_goal_rearrangement_move(1, 'W') == []

def test_reachable_goal_targets(setup_game):
    assert setup_game.computer_strategy.reachable_goal_targets('W',1,[(0,0),(1,0),(1,1)]) == [(7,0),(7,1),(8,0)]
    gam = copy.deepcopy(setup_game)
    br = [['W'], ['W', 'W'], ['Y', 'Y', 'O', 'O', 'O', 'R', 'R'], ['Y', 'O', 'O', 'O', 'O', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O'],
          ['G']]
    gam.board.load_color_grid(br)
    assert gam.computer_strategy.reachable_goal_targets('W', 1, [(0, 0), (1, 0), (1, 1)]) == [(7, 0), (7, 1)]
    gam = copy.deepcopy(setup_game)
    br = [['W'], ['W', 'W'], ['Y', 'Y', 'O', 'O', 'O', 'R', 'R'], ['Y', 'O', 'O', 'O', 'O', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O', 'O'], ['G', 'G'],
          ['G']]
    gam.board.load_color_grid(br)
    assert gam.computer_strategy.reachable_goal_targets('W', 1, [(0, 0), (1, 0), (1, 1)]) == [(6, 2), (6, 3),(6,4)]

def test_choose_move_toward_targets(setup_game):
    gam = copy.deepcopy(setup_game)
    br = [['W'], ['W', 'W'], ['Y', 'Y', 'O', 'O', 'O', 'R', 'R'], ['Y', 'O', 'O', 'O', 'O', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'W', 'O', 'O', 'O', 'O'], ['W', 'G'],
          ['O']]
    gam.board.load_color_grid(br)
    assert gam.computer_strategy.choose_move_toward_targets([(8,0)],[(7,0),(0,0),(6,2)],1,'W') == [(6,2),(8,0)]
    gam = copy.deepcopy(setup_game)
    br = [['W'], ['W', 'W'], ['Y', 'Y', 'O', 'O', 'O', 'R', 'R'], ['Y', 'O', 'O', 'O', 'O', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'W', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O', 'O'], ['W', 'G'],
          ['O']]
    gam.board.load_color_grid(br)
    assert gam.computer_strategy.choose_move_toward_targets([(8, 0)], [(7, 0), (0, 0), (5, 1)], 1, 'W') == [(5,1),(6, 2)]

def test_is_stuck(setup_game):
    assert not setup_game.computer_strategy.is_stuck(setup_game.players[0])
    gam = copy.deepcopy(setup_game)
    br = [['W'], ['W', 'W'], ['Y', 'Y', 'Y', 'Y', 'Y', 'R', 'R'], ['Y', 'Y', 'Y', 'Y', 'Y', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O', 'O'], ['W', 'G'],
          ['O']]
    gam.board.load_color_grid(br)
    assert gam.computer_strategy.is_stuck(gam.players[0])

def test_has_player_won(setup_game, setup2_game):
    assert not setup_game.has_player_won(setup_game.players[0])
    gam = copy.deepcopy(setup_game)
    br = [['O'], ['O', 'O'], ['Y', 'Y', 'Y', 'Y', 'Y', 'R', 'R'], ['Y', 'Y', 'Y', 'Y', 'Y', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O', 'O'], ['W', 'W'],
          ['W']]
    gam.board.load_color_grid(br)
    assert gam.has_player_won(gam.players[0])
    gam = copy.deepcopy(setup_game)
    br = [['O'], ['O', 'O'], ['Y', 'Y', 'Y', 'Y', 'Y', 'R', 'R'], ['Y', 'Y', 'Y', 'Y', 'Y', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O', 'O'], ['W', 'W'],
          ['W']]
    gam.board.load_color_grid(br)
    assert gam.has_player_won(gam.players[0])
    assert not setup2_game.has_player_won(setup2_game.players[0])
    gam = copy.deepcopy(setup2_game)
    br = [['O'], ['O', 'O'], ['Y', 'Y', 'O', 'O', 'O', 'R', 'R'], ['Y', 'O', 'O', 'O', 'O', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O', 'O'], ['W', 'W'],
          ['W']]
    gam.board.load_color_grid(br)
    assert not gam.has_player_won(gam.players[0])
    gam = copy.deepcopy(setup2_game)
    br = [['O'], ['O', 'O'], ['O', 'O', 'O', 'O', 'O', 'R', 'R'], ['O', 'O', 'O', 'O', 'O', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'Y'], ['O', 'O', 'O', 'O', 'O', 'Y', 'Y'], ['W', 'W'],
          ['W']]
    gam.board.load_color_grid(br)
    assert gam.has_player_won(gam.players[0])

def test_team_color_pairs(setup4_game):
    assert setup4_game.team_color_pairs() == [['W', 'G'], ['Y', 'R']]

def test_is_finished(setup_game, setup2_game, setup4_game):
    assert not setup_game.is_finished()
    assert not setup2_game.is_finished()
    assert not setup4_game.is_finished()
    gam = copy.deepcopy(setup_game)
    br = [['O'], ['O', 'O'], ['Y', 'Y', 'O', 'O', 'O', 'R', 'R'], ['Y', 'O', 'O', 'O', 'O', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O', 'O'], ['W', 'W'],
          ['W']]
    gam.board.load_color_grid(br)
    assert not gam.is_finished()
    gam = copy.deepcopy(setup_game)
    br = [['O'], ['O', 'O'], ['O', 'O', 'O', 'O', 'O', 'R', 'R'], ['O', 'O', 'O', 'O', 'O', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'Y'], ['O', 'O', 'O', 'O', 'O', 'Y', 'Y'], ['W', 'W'],
          ['W']]
    gam.board.load_color_grid(br)
    assert gam.is_finished()
    gam = copy.deepcopy(setup2_game)
    br = [['O'], ['O', 'O'], ['Y', 'Y', 'O', 'O', 'O', 'R', 'R'], ['Y', 'O', 'O', 'O', 'O', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O', 'O'], ['W', 'W'],
          ['W']]
    gam.board.load_color_grid(br)
    assert not gam.is_finished()
    gam = copy.deepcopy(setup2_game)
    br = [['G'], ['G', 'G'], ['Y', 'Y', 'O', 'O', 'O', 'R', 'R'], ['Y', 'O', 'O', 'O', 'O', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O', 'O'], ['W', 'W'],
          ['W']]
    gam.board.load_color_grid(br)
    assert not gam.is_finished()
    gam = copy.deepcopy(setup2_game)
    br = [['O'], ['O', 'O'], ['O', 'O', 'O', 'O', 'O', 'R', 'R'], ['O', 'O', 'O', 'O', 'O', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'Y'], ['O', 'O', 'O', 'O', 'O', 'Y', 'Y'], ['W', 'W'],
          ['W']]
    gam.board.load_color_grid(br)
    assert gam.is_finished()
    gam = copy.deepcopy(setup4_game)
    br = [['G'], ['G', 'G'], ['Y', 'Y', 'W', 'W', 'W', 'O', 'O'], ['Y', 'O', 'O', 'O', 'O', 'O'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'R'], ['O', 'O', 'O', 'O', 'O', 'R', 'R'], ['O', 'O'],
          ['O']]
    gam.board.load_color_grid(br)
    assert not gam.is_finished()
    gam = copy.deepcopy(setup4_game)
    br = [['G'], ['G', 'G'], ['Y', 'Y', 'O', 'O', 'O', 'O', 'O'], ['Y', 'O', 'O', 'O', 'O', 'O'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'R'], ['O', 'O', 'O', 'O', 'O', 'R', 'R'], ['W', 'W'],
          ['W']]
    gam.board.load_color_grid(br)
    assert gam.is_finished()
    gam = copy.deepcopy(setup4_game)
    br = [['G'], ['G', 'G'], ['R', 'R', 'W', 'W', 'W', 'O', 'O'], ['O', 'R', 'O', 'O', 'O', 'O'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'Y'], ['O', 'O', 'O', 'O', 'O', 'Y', 'Y'], ['O', 'O'],
          ['O']]
    gam.board.load_color_grid(br)
    assert not gam.is_finished()

def test_teammate_for(setup4_game):
    opp = setup4_game.teammate_for(setup4_game.players[0])
    name = opp.get_name()
    assert name == setup4_game.players[1].get_name()

def test_human_player_count(setup_game, setup3_game, setup2_game):
    assert setup_game.human_player_count() == 2
    assert setup2_game.human_player_count() == 2
    assert setup3_game.human_player_count() == 2