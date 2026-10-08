"""The shared match controller and the graphical input boundary."""

from chinese_checkers import Ball, Board, Game, Player
from chinese_checkers.gui import (BoardLayout, PygameView, VisualController,
                                  WINDOW_SIZE, create_visual_game)
from chinese_checkers.gui_setup import PygameSetupView, SetupSelection
from chinese_checkers.session import GameSession
from chinese_checkers.setup import SetupOptions, build_game, restore_game
from chinese_checkers.storage import GameStorage

def test_click_move_and_resume_uses_same_rules(tmp_path):
    store = GameStorage(tmp_path / "visual_game_data.json")
    game = create_visual_game(store)
    controller = VisualController(GameSession(game))
    source = (1, 1)
    controller.click_cell(source)
    assert controller.targets == set(game.board.legal_destinations(source))
    destination = next(iter(controller.targets))
    controller.click_cell(destination)

    assert game.board.color_at(source) == "O"
    assert game.board.color_at(destination) == "R"
    assert destination in game.positions_for_color("R")
    assert controller.session.current_player.get_name() == "Blue"
    saved = store.load()
    restored = GameSession(restore_game(saved, store=store))
    assert restored.current_player.get_name() == "Blue"
    assert restored.game.board.get_color_grid() == game.board.get_color_grid()

def test_visual_pass_and_computer_use_shared_turn_order(tmp_path):
    store = GameStorage(tmp_path / "visual_game_data.json")
    controller = VisualController(GameSession(create_visual_game(store, True)))
    before = set(controller.session.game.positions_for_color("B"))
    controller.pass_turn()
    assert controller.session.current_player.get_name() == "computer"
    controller.play_computer_turn()
    assert controller.session.current_player.get_name() == "Red"
    after = set(controller.session.game.positions_for_color("B"))
    assert before != after
    assert all(controller.session.game.board.color_at(cell) == "B" for cell in after)

def test_immobile_players_reach_draw_without_input_or_infinite_loop(tmp_path, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: (_ for _ in ()).throw(
        AssertionError("GameSession must not ask for input")))
    players = [Player("Red", 0, 0, ["R"]), Player("Blue", 0, 0, ["B"])]
    store = GameStorage(tmp_path / "visual_game_data.json")
    game = Game(Board(4), {"R": [], "B": []}, players, 0,
                color_directions={"R": "N", "B": "S"}, store=store)
    session = GameSession(game)
    assert session.status == "draw"
    assert [event.kind for event in session.drain_events()].count("blocked") == 6
    assert not store.exists()

def test_every_hole_maps_to_its_screen_position(tmp_path):
    board = create_visual_game(GameStorage(tmp_path / "save.json")).board
    layout = BoardLayout.from_board(board, *WINDOW_SIZE)
    assert set(layout.points) == set(board.cell_coordinates())
    assert all(layout.cell_at(point) == cell for cell, point in layout.points.items())
    assert layout.cell_at((0, 0)) is None

def _game_from_reported_position(tmp_path):
    """The exact occupied cells visible in the user's screenshot."""
    board = Board(4)
    occupied = {
        (1, 1): "B", (1, 2): "R", (2, 0): "R",
        (3, 0): "R", (3, 2): "B", (4, 0): "B",
    }
    balls = {"R": [], "B": []}
    for position, color in occupied.items():
        board.place_ball(Ball(color, position))
        balls[color].append(Ball(color, position))
    return Game(board, balls,
                [Player("Red", 0, 0, ["R"]), Player("Blue", 0, 0, ["B"])],
                0, color_directions={"R": "N", "B": "S"},
                store=GameStorage(tmp_path / "save.json"))

def test_reported_destination_uses_two_real_jumps(tmp_path):
    game = _game_from_reported_position(tmp_path)
    source, target = (2, 0), (2, 2)
    path = game.board.move_path(source, target)
    assert path == [source, (0, 0), target]

    controller = VisualController(GameSession(game))
    controller.click_cell(source)
    assert controller.paths[target] == path
    assert target in controller.jump_targets
    controller.preview(target)
    assert "2 jump" in controller.message
    controller.click_cell(target)
    assert controller.last_path == path
    assert game.board.color_at(source) == "O"
    assert game.board.color_at(target) == "R"

def test_target_disappears_after_piece_in_jump_path_moves_away(tmp_path):
    game = _game_from_reported_position(tmp_path)
    assert (2, 2) in game.board.legal_destinations((2, 0))
    game.apply_move(game.players[0], (1, 2), (1, 3))
    assert game.board.color_at((1, 2)) == "O"
    assert (2, 2) not in game.board.legal_destinations((2, 0))
    assert game.board.move_path((2, 0), (2, 2)) == []

def test_pygame_view_can_draw_in_headless_mode(tmp_path, monkeypatch):
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")
    import pytest
    pygame = pytest.importorskip("pygame")
    pygame.init()
    try:
        store = GameStorage(tmp_path / "save.json")
        controller = VisualController(GameSession(create_visual_game(store)))
        screen = pygame.display.set_mode(WINDOW_SIZE)
        view = PygameView(pygame, screen, controller, store)
        view.draw()
        assert screen.get_at((0, 0))[:3] == (10, 25, 38)
        controller.click_cell((1, 1))
        target = next(iter(controller.targets))
        view.handle_motion(view.layout.points[target])
        assert controller.hovered == target
        view.draw()
    finally:
        pygame.quit()

def test_menu_keeps_all_settings_valid_and_builds_the_same_game(tmp_path):
    store = GameStorage(tmp_path / "save.json")
    selection = SetupSelection()
    selection.adjust("size", 2)
    selection.adjust("players", 3)
    selection.adjust("computers", 2)
    selection.adjust("teams", 1)
    assert selection.options == SetupOptions(10, 6, 2, 1, 1)
    selection.names[:4] = ["Ada", "Bea", "Cid", "Dot"]
    game = selection.build(store)
    assert [p.get_name() for p in game.players] == ["Ada", "Bea", "Cid", "Dot",
                                                     "computer", "computer"]
    assert len(game.team_color_pairs()) == 3
    restored_settings = SetupSelection.from_game(game)
    assert restored_settings.options == selection.options
    assert restored_settings.names[:4] == selection.names[:4]
    selection.adjust("players", -3)
    assert selection.player_count == 2
    assert selection.computer_count == 1
    assert selection.teams == 0
    selection.adjust("sets", 2)
    assert selection.options.sets_per_player == 3

def test_graphical_settings_and_six_player_match_render_and_resume(tmp_path, monkeypatch):
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")
    import pytest
    pygame = pytest.importorskip("pygame")
    pygame.init()
    try:
        screen = pygame.display.set_mode(WINDOW_SIZE)
        store = GameStorage(tmp_path / "save.json")
        selection = SetupSelection(size=7, player_count=6, computer_count=2, teams=1)
        menu = PygameSetupView(pygame, screen, store, selection)
        menu.draw()
        assert menu.handle_click(menu.name_fields[0].center) is None
        assert menu.focus == 0
        menu.handle_key(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a, unicode="A"))
        assert menu.selection.names[0] == "A"
        menu.selection.names[0] = "Alice"
        assert menu.handle_click(menu.start_button.center) == "start"
        game = menu.start_game()
        assert game is not None
        controller = VisualController(GameSession(game))
        view = PygameView(pygame, screen, controller, store)
        view.draw()
        assert screen.get_at((0, 0))[:3] == (10, 25, 38)
        assert set(view.layout.points) == set(game.board.cell_coordinates())
        assert all(view.layout.cell_at(point) == cell
                   for cell, point in view.layout.points.items())
        controller.pass_turn()
        assert store.exists()
        view.new_game()
        assert view.request_setup and store.exists()
        menu = PygameSetupView(pygame, screen, store, SetupSelection.from_game(game))
        assert menu.resume_available
        resumed = menu.resume_game()
        assert resumed.board.get_color_grid() == game.board.get_color_grid()
        assert resumed.is_group == 1
        assert resumed.starting_directions == game.starting_directions
        bigger = pygame.display.set_mode((1200, 850))
        view.resize(bigger)
        view.draw()
        assert all(view.layout.cell_at(point) == cell
                   for cell, point in view.layout.points.items())
    finally:
        pygame.quit()

def test_invalid_setup_does_not_delete_save(tmp_path, monkeypatch):
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")
    import pytest
    pygame = pytest.importorskip("pygame")
    pygame.init()
    try:
        screen = pygame.display.set_mode(WINDOW_SIZE)
        store = GameStorage(tmp_path / "save.json")
        controller = VisualController(GameSession(create_visual_game(store)))
        assert store.exists()
        menu = PygameSetupView(pygame, screen, store)
        menu.selection.names[:2] = ["Same", "Same"]
        assert menu.start_game() is None
        assert store.exists()
        assert "unique" in menu.message
    finally:
        pygame.quit()

def test_gui_draws_each_terminal_match_type(tmp_path, monkeypatch):
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")
    import pytest
    pygame = pytest.importorskip("pygame")
    pygame.init()
    try:
        screen = pygame.display.set_mode(WINDOW_SIZE)
        for players, sets, teams in [(2, 1, 0), (2, 2, 0), (2, 3, 0),
                                     (3, 1, 0), (3, 2, 0), (4, 1, 1), (6, 1, 1)]:
            store = GameStorage(tmp_path / f"{players}-{sets}.json")
            selection = SetupSelection(size=10, player_count=players,
                                       computer_count=players - 1,
                                       sets_per_player=sets, teams=teams)
            menu = PygameSetupView(pygame, screen, store, selection)
            menu.draw()
            game = menu.start_game()
            view = PygameView(pygame, screen, VisualController(GameSession(game)), store)
            view.draw()
            assert len(view.layout.points) == len(game.board.cell_coordinates())
            assert view.layout.cell_at(view.layout.points[(0, 0)]) == (0, 0)
    finally:
        pygame.quit()

def test_gui_event_loop_starts_moves_and_resumes(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")
    import pytest
    pygame = pytest.importorskip("pygame")
    from chinese_checkers.gui import run

    starting = create_visual_game(GameStorage(tmp_path / "other.json"))
    source = (1, 1)
    target = next(iter(starting.board.legal_destinations(source)))
    layout = BoardLayout.from_board(starting.board, *WINDOW_SIZE)
    steps = [
        [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(798, 665))],
        [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=layout.points[source])],
        [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=layout.points[target])],
        [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_n, unicode="n")],
        [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(585, 665))],
        [pygame.event.Event(pygame.QUIT)],
    ]
    monkeypatch.setattr(pygame.event, "get", lambda: steps.pop(0))
    run(["--new"])
    assert not steps
    saved = GameStorage(tmp_path / "visual_game_data.json").load()
    assert saved is not None
    assert saved["board"]["br"][source[0]][source[1]] == "O"
    assert saved["board"]["br"][target[0]][target[1]] == "R"

def test_graphical_history_shows_moves_and_keeps_the_turn(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")
    import pytest
    pygame = pytest.importorskip("pygame")
    pygame.init()
    try:
        screen = pygame.display.set_mode(WINDOW_SIZE)
        store = GameStorage(tmp_path / "save.json")
        controller = VisualController(GameSession(create_visual_game(store)))
        view = PygameView(pygame, screen, controller, store)
        (tmp_path / "visual_checkers.log").write_text(
            "\n".join(f"INFO:root:2026-09-28 - Player Red: move {i}"
                      for i in range(50)), encoding="utf-8")
        player = controller.session.current_player
        view.handle_click(view.history_button.center)
        assert view.show_history
        view.scroll_history(10)
        assert view.history_offset == 10
        view.draw()
        view.handle_click(view.history_button.center)
        assert not view.show_history
        assert controller.session.current_player is player
    finally:
        pygame.quit()
