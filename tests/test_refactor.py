"""Regressions for shared Ball identity, planning isolation and legacy saves."""

import random

import pytest

from chinese_checkers import Ball, Board
from chinese_checkers.game import MatchProgress
from chinese_checkers.gui import BoardLayout
from chinese_checkers.gui_setup import SetupSelection
from chinese_checkers.session import GameSession, SessionEvent
from chinese_checkers.setup import SetupOptions, build_game, restore_game
from chinese_checkers.storage import GameStorage


MATCH_TYPES = [(2, 1, 0), (2, 2, 0), (2, 3, 0), (3, 1, 0), (3, 2, 0),
               (4, 1, 0), (4, 1, 1), (6, 1, 0), (6, 1, 1)]


def make_game(tmp_path):
    return build_game(SetupOptions(4, 2, 1, 1, 0), ['Human'],
                      GameStorage(tmp_path / 'match.json'))


@pytest.mark.parametrize('players,sets,teams', MATCH_TYPES)
@pytest.mark.parametrize('size', [4, 7])
def test_board_owns_the_same_balls_as_every_player(size, players, sets, teams, tmp_path):
    game = build_game(SetupOptions(size, players, players - 1, sets, teams), ['Human'],
                      GameStorage(tmp_path / 'match.json'))
    occupied = [ball for row in game.board.get_cells() for ball in row if ball is not None]
    expected = [ball for pieces in game.balls.values() for ball in pieces]
    assert {id(ball) for ball in occupied} == {id(ball) for ball in expected}
    for ball in expected:
        assert game.board.get_ball(ball.get_position()) is ball
        assert game.board.color_at(ball.get_position()) == ball.get_color()


def test_a_move_relocates_one_shared_instance(tmp_path):
    game = make_game(tmp_path)
    source = (1, 1)
    target = game.board.legal_destinations(source)[0]
    ball = game.board.get_ball(source)
    game.apply_move(game.players[0], source, target)
    assert game.board.get_ball(source) is None
    assert game.board.get_ball(target) is ball
    assert ball in game.balls['R']
    assert ball.get_position() == target


def test_invalid_moves_preserve_pieces_and_their_identity(tmp_path):
    game = make_game(tmp_path)
    original = [(ball, ball.get_position()) for pieces in game.balls.values() for ball in pieces]
    with pytest.raises(ValueError):
        game.apply_move(game.players[1], (1, 1), (2, 0))
    with pytest.raises(ValueError):
        game.apply_move(game.players[0], (1, 1), (3, 1))
    for ball, position in original:
        assert ball.get_position() == position
        assert game.board.get_ball(position) is ball


def test_a_color_snapshot_and_copied_rows_cannot_replace_live_cells(tmp_path):
    game = make_game(tmp_path)
    ball = game.board.get_ball((0, 0))
    colors = game.board.get_color_grid()
    rows = game.board.get_cells()
    colors[0][0] = 'B'
    rows[0][0] = None
    assert game.board.get_ball((0, 0)) is ball
    assert game.board.color_at((0, 0)) == 'R'


def test_jump_chain_keeps_the_original_ball_instance():
    board = Board(4)
    moving = Ball('R', (0, 0))
    for ball in (moving, Ball('B', (1, 1)), Ball('B', (3, 1))):
        assert board.place_ball(ball)
    assert board.move_path((0, 0), (4, 0)) == [(0, 0), (2, 0), (4, 0)]
    assert board.move_ball((0, 0), (4, 0))
    assert board.get_ball((4, 0)) is moving
    assert moving.get_position() == (4, 0)
    assert board.get_ball((1, 1)).color == board.get_ball((3, 1)).color == 'B'


def test_computer_planning_never_moves_live_balls(tmp_path):
    game = make_game(tmp_path)
    original = [(ball, ball.get_position()) for pieces in game.balls.values() for ball in pieces]
    before = game.board.get_color_grid()
    random.seed(17)
    source = original[0][1]
    assert game.computer_strategy.find_shortest_path(source, (2, 0))
    game.computer_strategy.choose_move(game.players[1])
    assert game.board.get_color_grid() == before
    for ball, position in original:
        assert ball.get_position() == position
        assert game.board.get_ball(position) is ball


def test_legacy_save_resumes_and_keeps_shared_objects(tmp_path):
    legacy = {
        'board': {'size': 4, 'br': [['R'], ['O'] * 4, ['O'] * 3, ['O'] * 4, ['B']]},
        'balls': {'R': [{'color': 'R', 'location': [0, 0]}],
                  'B': [{'color': 'B', 'location': [4, 0]}]},
        'players': [{'name': 'Alice', 'number_wins': 0, 'number_losses': 0, 'color': ['R']},
                    {'name': 'Bob', 'number_wins': 0, 'number_losses': 0, 'color': ['B']}],
        'is_group': 0, 'playr': 'Bob', 'started': 1, 'end': 0,
        'dic_color_loc': {'R': 'N', 'B': 'S'},
    }
    store = GameStorage(tmp_path / 'legacy.json')
    store.save(legacy)
    game = restore_game(store.load(), store)
    session = GameSession(game)
    assert session.current_player.get_name() == 'Bob'
    blue = game.balls['B'][0]
    assert game.board.get_ball((4, 0)) is blue
    session.submit_move(((4, 0), (3, 2)))
    assert game.board.get_ball((3, 2)) is blue
    saved = store.load()
    assert set(saved['board']) == {'size', 'br'}
    assert saved['board']['br'][3][2] == 'B'
    assert saved['balls']['B'][0]['location'] == [3, 2]
    resumed = restore_game(saved)
    for pieces in resumed.balls.values():
        for ball in pieces:
            assert resumed.board.get_ball(ball.get_position()) is ball


def test_draw_tracking_compares_detached_color_snapshots(tmp_path):
    game = make_game(tmp_path)
    before = game.previous_board
    game._record_board_change()
    assert game.unchanged_turns == 1
    source = (1, 1)
    game.apply_move(game.players[0], source, game.board.legal_destinations(source)[0])
    assert before[source[0]][source[1]] == 'R'
    game._record_board_change()
    assert game.unchanged_turns == 1
    assert game.previous_board[source[0]][source[1]] == 'O'


def test_regular_classes_keep_independent_default_lists():
    first, second = MatchProgress([]), MatchProgress([])
    first.rankings.append('Winner')
    first.pending_players.append('Player')
    assert second.rankings == second.pending_players == []
    first_settings, second_settings = SetupSelection(), SetupSelection()
    first_settings.names[0] = 'Changed'
    assert second_settings.names[0] == 'Player 1'


def test_regular_option_and_event_classes_keep_value_equality():
    options = SetupOptions(7, 4, 2, 1, 1)
    assert options == SetupOptions(7, 4, 2, 1, 1)
    assert hash(options) == hash(SetupOptions(7, 4, 2, 1, 1))
    assert SessionEvent('pass', 'Passed') == SessionEvent('pass', 'Passed')
    with pytest.raises(AttributeError):
        options.size = 10
    event = SessionEvent('pass', 'Passed')
    with pytest.raises(AttributeError):
        event.kind = 'move'
    layout = BoardLayout({(0, 0): (100, 100)}, 8)
    assert layout == BoardLayout({(0, 0): (100, 100)}, 8)
    with pytest.raises(AttributeError):
        layout.radius = 12
