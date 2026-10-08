"""Regression tests across setup, rules, state, and persistence boundaries."""

import pytest

from chinese_checkers import Ball, Board, Game, Player
from chinese_checkers.setup import build_game, new_game, restore_game
from chinese_checkers import setup
from chinese_checkers.session import GameSession
from chinese_checkers.storage import GameStorage
from chinese_checkers.utils import is_valid_coordinate_input

def make_game(top="R", bottom="B"):
    board = Board(4)
    top_ball = Ball(top, (0, 0))
    bottom_ball = Ball(bottom, (4, 0))
    assert board.add_ball_to_triangle(top_ball, "N", 1)
    assert board.add_ball_to_triangle(bottom_ball, "S", 1)
    players = [Player("Alice", 0, 0, [top]), Player("Bob", 0, 0, [bottom])]
    return Game(board, {top: [top_ball], bottom: [bottom_ball]}, players, 0)

def test_games_do_not_share_directions_or_draw_state(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    first = make_game()
    second = make_game("G", "Y")
    first.unchanged_turns = 2
    assert first.starting_directions == {"R": "N", "B": "S"}
    assert second.starting_directions == {"G": "N", "Y": "S"}
    assert second.unchanged_turns == 0
    assert second.goal_directions() == {"G": "S", "Y": "N"}

def test_apply_move_checks_ownership_and_keeps_ball_in_sync(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    game = make_game()
    before = [row[:] for row in game.board.get_color_grid()]
    with pytest.raises(ValueError):
        game.apply_move(game.players[1], (0, 0), (1, 1))
    with pytest.raises(ValueError):
        game.apply_move(game.players[0], (0, 0), (-1, 0))
    assert game.board.get_color_grid() == before
    assert game.balls["R"][0].get_position() == (0, 0)

    game.apply_move(game.players[0], (0, 0), (1, 1))
    assert game.board.color_at((0, 0)) == "O"
    assert game.board.color_at((1, 1)) == "R"
    assert game.balls["R"][0].get_position() == (1, 1)

def test_save_restores_turn_order_and_original_directions(tmp_path):
    game = make_game()
    game.apply_move(game.players[0], (0, 0), (1, 1))
    store = GameStorage(tmp_path / "game_data.json")
    store.save(game.create_save_state([], [], [], game.players, "Bob", 1, 0,
                              game.starting_directions, []))
    restored = restore_game(store.load())
    assert [p.get_name() for p in restored.players] == ["Bob", "Alice"]
    assert restored.board.get_color_grid() == game.board.get_color_grid()
    assert restored.balls["R"][0].get_position() == (1, 1)
    assert restored.starting_directions == {"R": "N", "B": "S"}
    store.clear()
    assert not store.exists()

def test_interactive_setup_creates_a_match(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    answers = iter(["4", "2", "0", "1", "Alice", "Bob"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    game = new_game()
    assert game.starting_directions == {"R": "N", "B": "S"}
    assert len(game.balls["R"]) == len(game.balls["B"]) == 3
    assert len(game.board.legal_destinations((0, 0))) > 0

def test_reject_zero_coordinates_and_invalid_board_sizes():
    assert not is_valid_coordinate_input("0,1")
    assert not is_valid_coordinate_input("1,0")
    for size in (0, 1, 5, 8):
        with pytest.raises(ValueError):
            Board(size)

def test_human_turn_can_pass_or_move(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    game = make_game()
    monkeypatch.setattr("builtins.input", lambda _: "pass")
    game.play_terminal_turn(game.players[0])
    assert game.passed_turns == 1
    assert game.balls["R"][0].get_position() == (0, 0)

    entries = iter(["1,1", "2,2"])
    monkeypatch.setattr("builtins.input", lambda _: next(entries))
    game.play_terminal_turn(game.players[0])
    assert game.balls["R"][0].get_position() == (1, 1)

def test_computer_turn_uses_a_legal_move(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    board = Board(4)
    red = [Ball("R", place) for place in ((0, 0), (1, 1), (1, 2))]
    blue = [Ball("B", place) for place in ((4, 0), (3, 1), (3, 2))]
    for ball in red:
        assert board.add_ball_to_triangle(ball, "N", 2)
    for ball in blue:
        assert board.add_ball_to_triangle(ball, "S", 2)
    game = Game(board, {"R": red, "B": blue},
                [Player("computer", 0, 0, ["R"]), Player("Bob", 0, 0, ["B"])], 0)
    before = {piece.get_position() for piece in red}
    game.play_terminal_turn(game.players[0])
    after = {piece.get_position() for piece in red}
    assert before != after
    assert after == set(game.positions_for_color("R"))
    assert all(board.color_at(place) == "R" for place in after)

def test_play_resumes_remaining_players_in_round(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    board = Board(4)
    positions = [(0, 0), (1, 3), (4, 0)]
    colors = ["R", "B", "G"]
    directions = ["N", "NE", "S"]
    balls = {}
    for color, place, direction in zip(colors, positions, directions):
        piece = Ball(color, place)
        assert board.add_ball_to_triangle(piece, direction, 1)
        balls[color] = [piece]
    game = Game(board, balls, [Player(name, 0, 0, [color]) for name, color
                               in zip(("Alice", "Bob", "Charlie"), colors)], 0)

    class StopTurn(Exception):
        pass

    first_run = []

    def interrupted_turn(player):
        first_run.append(player.get_colors()[0])
        if len(first_run) == 2:
            raise StopTurn()

    monkeypatch.setattr(game, "play_terminal_turn", interrupted_turn)
    with pytest.raises(StopTurn):
        game.play()
    assert first_run == ["R", "B"]
    saved = GameStorage().load()
    assert saved["pending_colors"] == [["B"], ["G"]]

    resumed = restore_game(saved)
    second_run = []

    def resumed_turn(player):
        second_run.append(player.get_colors()[0])
        if len(second_run) == 2:
            raise StopTurn()

    monkeypatch.setattr(resumed, "play_terminal_turn", resumed_turn)
    with pytest.raises(StopTurn):
        resumed.play()
    assert second_run == ["B", "G"]

def test_resume_selects_correct_computer_when_names_repeat(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    board = Board(4)
    players = [Player("Alice", 0, 0, ["R"]), Player("computer", 0, 0, ["B"]),
               Player("computer", 0, 0, ["G"])]
    game = Game(board, {"R": [], "B": [], "G": []}, players, 0,
                color_directions={"R": "N", "B": "NE", "G": "S"})
    state = game.create_save_state([], [], [], players, "computer", 1, 0,
                           game.starting_directions, [])
    state["pending_colors"] = [["G"]]
    GameStorage().save(state)
    restored = restore_game(GameStorage().load())
    assert restored.players[0].get_colors() == ["G"]
    assert [player.get_colors() for player in restored._load_progress().pending_players] == [["G"]]

def test_play_records_team_winner_and_last_team(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    board = Board(4)
    places = {"G": (1, 1), "W": (4, 0), "Y": (1, 0), "R": (3, 3)}
    for color, (row, col) in places.items():
        board.place_ball(Ball(color, (row, col)))
    players = [Player(name, 0, 0, [color]) for name, color in
               (("Gina", "G"), ("Wendy", "W"), ("Yara", "Y"), ("Ron", "R"))]
    balls = {color: [Ball(color, place)] for color, place in places.items()}
    game = Game(board, balls, players, 1,
                color_directions={"G": "S", "W": "N", "Y": "NW", "R": "SE"})
    assert not game.is_finished()
    monkeypatch.setattr(game, "play_terminal_turn",
                        lambda player: game.apply_move(player, (1, 1), (0, 0)))
    monkeypatch.setattr("builtins.input", lambda _: "")
    game.play()
    assert [player.get_wins() for player in players] == [1, 1, 0, 0]
    assert [player.get_losses() for player in players] == [0, 0, 1, 1]
    assert "finished place: 1" in capsys.readouterr().out
    assert not GameStorage().exists()

@pytest.mark.parametrize("players,sets", [(2, 1), (2, 2), (2, 3),
                                          (3, 1), (3, 2), (4, 1), (6, 1)])
@pytest.mark.parametrize("size", [4, 7, 10])
def test_supported_player_setups_fill_distinct_corners(players, sets, size, tmp_path):
    options = setup.SetupOptions(size, players, players - 1, sets, 0)
    game = build_game(options, ["Alice"], GameStorage(tmp_path / "match.json"))
    assert len(game.players) == players
    assert len(game.balls) == players * sets
    assert len(set(game.starting_directions.values())) == players * sets
    if players == 3 and sets == 2:
        for player in game.players:
            first, second = player.get_colors()
            assert setup.utils.opposite_direction(game.starting_directions[first]) == [
                game.starting_directions[second]]
    for color, direction in game.starting_directions.items():
        expected = set(game.board.triangle_cells(options.triangle_type)[direction])
        assert set(game.positions_for_color(color)) == expected
        assert len(game.balls[color]) == options.balls_per_color
        assert all(game.board.color_at(cell) == color for cell in expected)

@pytest.mark.parametrize("players", [4, 6])
def test_automatic_team_assignment_pairs_opposite_corners(players, tmp_path):
    options = setup.SetupOptions(7, players, 2, 1, 1)
    game = build_game(options, [f"Human {i}" for i in range(players - 2)],
                      GameStorage(tmp_path / "match.json"))
    assert len(game.team_color_pairs()) == players // 2
    for pair in game.team_color_pairs():
        directions = [game.starting_directions[color] for color in pair]
        assert setup.utils.opposite_direction(directions[0]) == [directions[1]]
    assert game.teammate_for(game.players[0]) in game.players

@pytest.mark.parametrize("players,sets", [(2, 1), (2, 2), (2, 3),
                                          (3, 1), (3, 2), (4, 1), (6, 1)])
def test_existing_computer_strategy_still_picks_legal_moves(players, sets, tmp_path):
    store = GameStorage(tmp_path / "match.json")
    options = setup.SetupOptions(7, players, players - 1, sets, int(players in (4, 6)))
    game = build_game(options, ["Human"], store)
    session = GameSession(game)
    session.submit_move(None)
    computer_strategy = session.current_player
    assert computer_strategy.get_name() == "computer"
    move = game.computer_strategy.choose_move(computer_strategy)
    assert move is not None
    assert move[1] in game.board.legal_destinations(move[0])
    session.submit_move(move)
    assert game.board.color_at(move[1]) in computer_strategy.get_colors()

def test_terminal_team_setup_needs_only_options_and_human_names(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    answers = iter(["7", "4", "2", "1", "Alice", "Bob"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    game = new_game()
    assert [player.get_name() for player in game.players] == [
        "Alice", "Bob", "computer", "computer"]
    assert game.is_group == 1 and len(game.team_color_pairs()) == 2

@pytest.mark.parametrize("options", [
    (5, 2, 0, 1, 0), (4, 5, 0, 1, 0), (4, 2, 2, 1, 0),
    (4, 4, 0, 2, 0), (4, 3, 0, 1, 1),
])
def test_setup_rejects_invalid_combinations(options):
    with pytest.raises(ValueError):
        setup.SetupOptions(*options)
