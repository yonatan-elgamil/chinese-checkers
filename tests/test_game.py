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
    board.set_br(br)
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
    board.set_br(br)
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

    board.set_br(br)
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
    board.set_br(br)
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
    dic_color_loc = setup_game.dic_color_loc
    assert dic_color_loc['W'] == 'N'
    assert dic_color_loc['Y'] == 'NW'
    assert dic_color_loc['R'] == 'NE'


def test_word_color(setup_game):

    player = Player('TestPlayer', 0, 0, ['W'])
    game = setup_game
    assert game.word_color(player) == 'W'
    player = Player('TestPlayer', 0, 0, ['W', 'Y'])
    game = setup_game
    assert game.word_color(player) == 'W and Y'
    player = Player('TestPlayer', 0, 0, ['W', 'Y', 'R'])
    game = setup_game
    assert game.word_color(player) == 'W and Y and R'


def test_loc_color(setup_game):
    assert setup_game.loc_color('W') == [(0,0),(1,0),(1,1)]
    assert setup_game.loc_color('Y') == [(2,0),(2,1),(3,0)]


def test_loc_player(setup_game, setup2_game):
    playr = setup_game.players[0]
    assert setup_game.loc_player(playr) == [(0,0),(1,0),(1,1)]
    playr = setup_game.players[1]
    assert setup_game.loc_player(playr) == [(2,0),(2,1),(3,0)]
    playr = setup2_game.players[0]
    assert setup_game.loc_player(playr) == [(0,0),(1,0),(1,1),(2,0),(2,1),(3,0)]


def test_dic_targ(setup_game):
    assert setup_game.dic_targ()['W'] == 'S'
    assert setup_game.dic_targ()['Y'] == 'SE'
    assert setup_game.dic_targ()['R'] == 'SW'


def test__victory_places_strategy(setup_game):
   assert setup_game._victory_places_strategy(1,'S') == [[(8,0)],[(7,0),(7,1)]]
   assert setup_game._victory_places_strategy(1,'N') == [[(0,0)],[(1,0),(1,1)]]


def test_victory_places_strategy(setup_game, setup2_game, setup3_game):
    gam = copy.deepcopy(setup_game)
    gam.board.set_br([['O'], ['W', 'W'], ['Y', 'Y', 'O', 'O', 'O', 'R', 'R'], ['Y', 'O', 'O', 'O', 'O', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O'],
          ['W']])
    assert gam.victory_places_strategy([(1,0),(1,1),(8,0)], ['W'], 1) == [(1,0),(1,1)]
    gam.board.set_br([['O'], ['W', 'W'], ['Y', 'Y', 'O', 'O', 'O', 'R', 'R'], ['Y', 'O', 'O', 'O', 'O', 'R'],
                      ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O', 'O'],
                      ['W', 'O'],
                      ['O']])
    assert gam.victory_places_strategy([(1,0),(1,1),(7,0)], ['W'], 1) == [(1,0),(1,1)]
    gam = copy.deepcopy(setup3_game)
    gam.board.set_br([['O'], ['W', 'W'], ['O', 'O', 'W', 'W', 'W', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'],
          ['O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'G', 'G', 'G', 'O', 'O'],
          ['G', 'G'], ['W']])
    assert gam.victory_places_strategy([(1,0),(1,1),(2,2),(2,3),(2,4),(8,0)], ['W'], 1) == [(1,0),(1,1),(2,2),(2,3),(2,4)]
    gam = copy.deepcopy(setup3_game)
    gam.board.set_br([['O'], ['W', 'W'], ['O', 'O', 'W', 'W', 'W', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'],
                      ['O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'G', 'G', 'G', 'O', 'O'],
                      ['W', 'G'], ['G']])
    assert gam.victory_places_strategy([(1, 0), (1, 1), (2, 2), (2, 3), (2, 4), (8, 0)], ['W'], 1) == [(1, 0), (1, 1),
                                                                                                       (2, 2), (2, 3),
                                                                                                       (2, 4),(8, 0)]
def test_go_victory_places_strategy(setup_game, setup3_game):
    gam = copy.deepcopy(setup3_game)
    gam.board.set_br([['O'], ['W', 'W'], ['O', 'O', 'W', 'W', 'W', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'],
                      ['O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'G', 'G', 'G', 'O', 'O'],
                      ['W', 'G'], ['G']])
    assert gam.go_victory_places_strategy(1,'W') == []
    gam = copy.deepcopy(setup3_game)
    gam.board.set_br([['O'], ['O', 'W'], ['O', 'O', 'W', 'W', 'W', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'],
                          ['O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'],
                          ['O', 'O', 'G', 'G', 'W', 'O', 'O'],
                          ['W', 'O'], ['G']])
    assert gam.go_victory_places_strategy(1, 'W') == []
    gam = copy.deepcopy(setup3_game)
    gam.board.set_br([['O'], ['O', 'W'], ['O', 'O', 'W', 'W', 'W', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'],
                      ['O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'],
                      ['O', 'O', 'G', 'G', 'W', 'O', 'O'],
                      ['W', 'O'], ['W']])
    assert gam.go_victory_places_strategy(1, 'W') == [(6,4),(7,1)]
    gam = copy.deepcopy(setup3_game)
    gam.board.set_br([['O'], ['O', 'W'], ['O', 'O', 'W', 'W', 'W', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'],
                      ['O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'],
                      ['O', 'O', 'G', 'G', 'W', 'O', 'O'],
                      ['W', 'G'], ['W']])
    assert gam.go_victory_places_strategy(1, 'W') == []


def test_go_target(setup_game):
    assert setup_game.go_target('W',1,[(0,0),(1,0),(1,1)]) == [(7,0),(7,1),(8,0)]
    gam = copy.deepcopy(setup_game)
    br = [['W'], ['W', 'W'], ['Y', 'Y', 'O', 'O', 'O', 'R', 'R'], ['Y', 'O', 'O', 'O', 'O', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O'],
          ['G']]
    gam.board.set_br(br)
    assert gam.go_target('W', 1, [(0, 0), (1, 0), (1, 1)]) == [(7, 0), (7, 1)]
    gam = copy.deepcopy(setup_game)
    br = [['W'], ['W', 'W'], ['Y', 'Y', 'O', 'O', 'O', 'R', 'R'], ['Y', 'O', 'O', 'O', 'O', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O', 'O'], ['G', 'G'],
          ['G']]
    gam.board.set_br(br)
    assert gam.go_target('W', 1, [(0, 0), (1, 0), (1, 1)]) == [(6, 2), (6, 3),(6,4)]


def test_go_location(setup_game):
    gam = copy.deepcopy(setup_game)
    br = [['W'], ['W', 'W'], ['Y', 'Y', 'O', 'O', 'O', 'R', 'R'], ['Y', 'O', 'O', 'O', 'O', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'W', 'O', 'O', 'O', 'O'], ['W', 'G'],
          ['O']]
    gam.board.set_br(br)
    assert gam.go_location([(8,0)],[(7,0),(0,0),(6,2)],1,'W') == [(6,2),(8,0)]
    gam = copy.deepcopy(setup_game)
    br = [['W'], ['W', 'W'], ['Y', 'Y', 'O', 'O', 'O', 'R', 'R'], ['Y', 'O', 'O', 'O', 'O', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'W', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O', 'O'], ['W', 'G'],
          ['O']]
    gam.board.set_br(br)
    assert gam.go_location([(8, 0)], [(7, 0), (0, 0), (5, 1)], 1, 'W') == [(5,1),(6, 2)]

def test_computer_stuck(setup_game):
    assert not setup_game.computer_stuck(setup_game.players[0])
    gam = copy.deepcopy(setup_game)
    br = [['W'], ['W', 'W'], ['Y', 'Y', 'Y', 'Y', 'Y', 'R', 'R'], ['Y', 'Y', 'Y', 'Y', 'Y', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O', 'O'], ['W', 'G'],
          ['O']]
    gam.board.set_br(br)
    assert gam.computer_stuck(gam.players[0])


def test_is_win(setup_game, setup2_game):
    assert not setup_game.is_win(setup_game.players[0])
    gam = copy.deepcopy(setup_game)
    br = [['O'], ['O', 'O'], ['Y', 'Y', 'Y', 'Y', 'Y', 'R', 'R'], ['Y', 'Y', 'Y', 'Y', 'Y', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O', 'O'], ['W', 'W'],
          ['W']]
    gam.board.set_br(br)
    assert gam.is_win(gam.players[0])
    gam = copy.deepcopy(setup_game)
    br = [['O'], ['O', 'O'], ['Y', 'Y', 'Y', 'Y', 'Y', 'R', 'R'], ['Y', 'Y', 'Y', 'Y', 'Y', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O', 'O'], ['W', 'W'],
          ['W']]
    gam.board.set_br(br)
    assert gam.is_win(gam.players[0])
    assert not setup2_game.is_win(setup2_game.players[0])
    gam = copy.deepcopy(setup2_game)
    br = [['O'], ['O', 'O'], ['Y', 'Y', 'O', 'O', 'O', 'R', 'R'], ['Y', 'O', 'O', 'O', 'O', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O', 'O'], ['W', 'W'],
          ['W']]
    gam.board.set_br(br)
    assert not gam.is_win(gam.players[0])
    gam = copy.deepcopy(setup2_game)
    br = [['O'], ['O', 'O'], ['O', 'O', 'O', 'O', 'O', 'R', 'R'], ['O', 'O', 'O', 'O', 'O', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'Y'], ['O', 'O', 'O', 'O', 'O', 'Y', 'Y'], ['W', 'W'],
          ['W']]
    gam.board.set_br(br)
    assert gam.is_win(gam.players[0])


def test_group(setup4_game):
    assert setup4_game.group() == [['W', 'G'], ['Y', 'R']]


def test_is_over(setup_game, setup2_game, setup4_game):
    assert not setup_game.is_over()
    assert not setup2_game.is_over()
    assert not setup4_game.is_over()
    gam = copy.deepcopy(setup_game)
    br = [['O'], ['O', 'O'], ['Y', 'Y', 'O', 'O', 'O', 'R', 'R'], ['Y', 'O', 'O', 'O', 'O', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O', 'O'], ['W', 'W'],
          ['W']]
    gam.board.set_br(br)
    assert not gam.is_over()
    gam = copy.deepcopy(setup_game)
    br = [['O'], ['O', 'O'], ['O', 'O', 'O', 'O', 'O', 'R', 'R'], ['O', 'O', 'O', 'O', 'O', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'Y'], ['O', 'O', 'O', 'O', 'O', 'Y', 'Y'], ['W', 'W'],
          ['W']]
    gam.board.set_br(br)
    assert gam.is_over()
    gam = copy.deepcopy(setup2_game)
    br = [['O'], ['O', 'O'], ['Y', 'Y', 'O', 'O', 'O', 'R', 'R'], ['Y', 'O', 'O', 'O', 'O', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O', 'O'], ['W', 'W'],
          ['W']]
    gam.board.set_br(br)
    assert not gam.is_over()
    gam = copy.deepcopy(setup2_game)
    br = [['G'], ['G', 'G'], ['Y', 'Y', 'O', 'O', 'O', 'R', 'R'], ['Y', 'O', 'O', 'O', 'O', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'O', 'O'], ['W', 'W'],
          ['W']]
    gam.board.set_br(br)
    assert not gam.is_over()
    gam = copy.deepcopy(setup2_game)
    br = [['O'], ['O', 'O'], ['O', 'O', 'O', 'O', 'O', 'R', 'R'], ['O', 'O', 'O', 'O', 'O', 'R'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'Y'], ['O', 'O', 'O', 'O', 'O', 'Y', 'Y'], ['W', 'W'],
          ['W']]
    gam.board.set_br(br)
    assert gam.is_over()
    gam = copy.deepcopy(setup4_game)
    br = [['G'], ['G', 'G'], ['Y', 'Y', 'W', 'W', 'W', 'O', 'O'], ['Y', 'O', 'O', 'O', 'O', 'O'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'R'], ['O', 'O', 'O', 'O', 'O', 'R', 'R'], ['O', 'O'],
          ['O']]
    gam.board.set_br(br)
    assert not gam.is_over()
    gam = copy.deepcopy(setup4_game)
    br = [['G'], ['G', 'G'], ['Y', 'Y', 'O', 'O', 'O', 'O', 'O'], ['Y', 'O', 'O', 'O', 'O', 'O'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'R'], ['O', 'O', 'O', 'O', 'O', 'R', 'R'], ['W', 'W'],
          ['W']]
    gam.board.set_br(br)
    assert gam.is_over()
    gam = copy.deepcopy(setup4_game)
    br = [['G'], ['G', 'G'], ['R', 'R', 'W', 'W', 'W', 'O', 'O'], ['O', 'R', 'O', 'O', 'O', 'O'],
          ['Y', 'O', 'O', 'O', 'O'], ['O', 'O', 'O', 'O', 'O', 'Y'], ['O', 'O', 'O', 'O', 'O', 'Y', 'Y'], ['O', 'O'],
          ['O']]
    gam.board.set_br(br)
    assert not gam.is_over()



def test_opp_playr(setup4_game):
    opp = setup4_game.opp_playr(setup4_game.players[0])
    name = opp.get_name()
    assert name == setup4_game.players[1].get_name()


def test_ln_real_players(setup_game, setup3_game, setup2_game):
    assert setup_game.ln_real_players() == 2
    assert setup2_game.ln_real_players() == 2
    assert setup3_game.ln_real_players() == 2