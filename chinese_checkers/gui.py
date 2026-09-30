"""Pygame board, input controller, and match/menu navigation."""

import argparse
from dataclasses import dataclass
import logging
import math
from pathlib import Path
import textwrap
from typing import Dict, Optional, Tuple

from .board import Board
from .game import Game
from .gui_setup import PygameSetupView, SetupSelection
from .session import GameSession, Move
from .setup import SetupOptions, build_game, restore_game
from .storage import GameStorage

Coordinate = Tuple[int, int]
Point = Tuple[int, int]

WINDOW_SIZE = (960, 740)
PIECE_COLORS = {
    "R": (233, 94, 86), "B": (76, 156, 238), "G": (81, 194, 139),
    "Y": (242, 192, 75), "P": (172, 126, 226), "W": (237, 235, 223),
}


def create_visual_game(store: GameStorage, versus_computer: bool = False) -> Game:
    """Compatibility helper for the original two-player graphical game."""
    return build_game(SetupOptions(4, 2, int(versus_computer), 1, 0),
                      ["Red"] if versus_computer else ["Red", "Blue"], store)


@dataclass(frozen=True)
class BoardLayout:
    """Map jagged board coordinates to screen pixels and mouse clicks."""

    points: Dict[Coordinate, Point]
    radius: int

    @classmethod
    def from_board(cls, board: Board, width: int, height: int) -> "BoardLayout":
        rows = board.get_br()
        spacing = min(92, (width - 342) / max(len(row) - 1 for row in rows),
                      (height - 210) / ((len(rows) - 1) * math.sqrt(3) / 2))
        center_x = (width - 250) / 2
        center_y = (height + 76) / 2
        points = {
            (row_index, column): (
                round(center_x + (column - (len(row) - 1) / 2) * spacing),
                round(center_y + (row_index - (len(rows) - 1) / 2)
                      * spacing * math.sqrt(3) / 2),
            )
            for row_index, row in enumerate(rows)
            for column in range(len(row))
        }
        return cls(points, max(4, round(spacing * .29)))

    def cell_at(self, position: Point) -> Optional[Coordinate]:
        """Select a hole only if the click is close enough to its center."""
        cell = min(self.points, key=lambda item: math.dist(position, self.points[item]))
        return cell if math.dist(position, self.points[cell]) <= self.radius + 7 else None


class VisualController:
    """Translate clicks into session moves; drawing knows no game rules."""

    def __init__(self, session: GameSession):
        self.session = session
        self.selected: Optional[Coordinate] = None
        self.targets = set()
        self.paths: Dict[Coordinate, list[Coordinate]] = {}
        self.jump_targets = set()
        self.hovered: Optional[Coordinate] = None
        self.last_path: list[Coordinate] = []
        self.message = "Select one of your pieces."
        self.last_move: Optional[Move] = None
        self._consume_events()

    def _consume_events(self) -> None:
        for event in self.session.drain_events():
            self.message = event.message
            if event.move is not None:
                self.last_move = event.move

    def click_cell(self, cell: Coordinate) -> None:
        """Select an owned piece or send a highlighted target to the session."""
        player = self.session.current_player
        if player is None or player.get_name() == "computer":
            return
        if self.selected is not None and cell in self.targets:
            path = self.paths[cell]
            was_jump = cell in self.jump_targets
            self.session.submit_move((self.selected, cell))
            self.last_path = path
            self.selected = None
            self.targets.clear()
            self.paths.clear()
            self.jump_targets.clear()
            self.hovered = None
            self._consume_events()
            if was_jump and self.session.status == "playing":
                self.message = f"Completed {len(path) - 1} jump(s) along the gold route."
            return
        if cell in self.session.game.loc_player(player):
            board = self.session.game.board
            self.selected = cell
            self.paths = {target: [cell, target]
                          for target in board.simple_good_move(cell)}
            jump_paths = board.jump_paths(cell)
            self.paths.update(jump_paths)
            self.jump_targets = set(jump_paths)
            self.targets = set(self.paths)
            self.hovered = None
            self.last_path = []
            self.message = ("Hover over a glowing cell to see its route." if self.targets
                            else "This piece cannot move. Choose another.")
            return
        self.message = "Choose one of your pieces or a highlighted destination."

    def preview(self, cell: Optional[Coordinate]) -> None:
        """Show the actual hop sequence for a destination under the cursor."""
        self.hovered = cell if cell in self.targets else None
        if self.hovered is not None:
            hops = len(self.paths[cell]) - 1
            self.message = (f"{hops} jump(s) along the gold route."
                            if cell in self.jump_targets else "One adjacent step.")

    def pass_turn(self) -> None:
        player = self.session.current_player
        if player is None or player.get_name() == "computer":
            return
        self.selected = None
        self.targets.clear()
        self.paths.clear()
        self.jump_targets.clear()
        self.hovered = None
        self.last_path = []
        self.session.submit_move(None)
        self._consume_events()

    def play_computer_turn(self) -> None:
        player = self.session.current_player
        if player is None or player.get_name() != "computer":
            return
        move = self.session.game.computer.choose_move(player)
        path = self.session.game.board.move_path(*move) if move else []
        self.session.submit_move(move)
        self.last_path = path
        self._consume_events()
        if len(path) > 2 and self.session.status == "playing":
            self.message = f"Computer made {len(path) - 1} jumps along the gold route."


class PygameView:
    """Draw the game and handle window events; Pygame stays in this module."""

    def __init__(self, pygame, screen, controller: VisualController, store: GameStorage):
        self.pg = pygame
        self.screen = screen
        self.controller = controller
        self.store = store
        self.request_setup = False
        self.show_history = False
        self.history_offset = 0
        self.title_font = pygame.font.SysFont("arial", 31, bold=True)
        self.heading_font = pygame.font.SysFont("arial", 22, bold=True)
        self.button_font = pygame.font.SysFont("arial", 18, bold=True)
        self.body_font = pygame.font.SysFont("arial", 18)
        self.small_font = pygame.font.SysFont("arial", 15)
        self.resize(screen)

    def resize(self, screen) -> None:
        """Keep buttons and board coordinates aligned when the window changes."""
        self.screen = screen
        width, height = screen.get_size()
        self.layout = BoardLayout.from_board(self.controller.session.game.board, width, height)
        self.pass_button = self.pg.Rect(width - 234, height - 142, 188, 46)
        self.new_button = self.pg.Rect(width - 234, height - 88, 188, 46)
        self.history_button = self.pg.Rect(width - 234, 39, 188, 43)

    def new_game(self) -> None:
        """Open match settings; the old save stays until Start is pressed."""
        self.request_setup = True

    def handle_click(self, position: Point) -> None:
        if self.history_button.collidepoint(position):
            self.toggle_history()
        elif self.new_button.collidepoint(position):
            self.new_game()
        elif self.pass_button.collidepoint(position) and not self.show_history:
            self.controller.pass_turn()
        elif not self.show_history:
            cell = self.layout.cell_at(position)
            if cell is not None:
                self.controller.click_cell(cell)

    def handle_motion(self, position: Point) -> None:
        if not self.show_history:
            self.controller.preview(self.layout.cell_at(position))

    def toggle_history(self) -> None:
        """Show/hide moves from the visual game's log, without changing turns."""
        self.show_history = not self.show_history
        self.history_offset = 0

    def _history_lines(self):
        path = Path("visual_checkers.log")
        if not path.exists():
            return []
        lines = []
        for entry in path.read_text(encoding="utf-8").splitlines():
            lines.extend(textwrap.wrap(entry.removeprefix("INFO:root:"), 76))
        return lines

    def scroll_history(self, amount):
        """Move through older/newer history lines while the overlay is open."""
        if self.show_history:
            capacity = max(1, (self.screen.get_height() - 230) // 23)
            limit = max(0, len(self._history_lines()) - capacity)
            self.history_offset = max(0, min(limit, self.history_offset + amount))

    def _text(self, content, position, font, color=(227, 236, 245)):
        self.screen.blit(font.render(content, True, color), position)

    def _button(self, rect, text, enabled=True):
        fill = (47, 101, 131) if enabled else (43, 57, 70)
        self.pg.draw.rect(self.screen, fill, rect, border_radius=11)
        self.pg.draw.rect(self.screen, (88, 140, 166), rect, 1, border_radius=11)
        label = self.button_font.render(text, True, (237, 244, 249))
        self.screen.blit(label, label.get_rect(center=rect.center))

    def _route_path(self):
        if self.controller.selected is not None:
            return self.controller.paths.get(self.controller.hovered, [])
        return self.controller.last_path

    def _draw_route_lines(self, path):
        if len(path) < 2:
            return
        points = [self.layout.points[cell] for cell in path]
        self.pg.draw.lines(self.screen, (250, 195, 93), False, points, 4)
        for center in points[1:]:
            self.pg.draw.circle(self.screen, (250, 195, 93), center,
                                self.layout.radius + 5, 3)

    def _draw_route_badges(self, path):
        if len(path) < 3:
            return
        for number, cell in enumerate(path[1:], start=1):
            x, y = self.layout.points[cell]
            center = (x + self.layout.radius, y - self.layout.radius)
            self.pg.draw.circle(self.screen, (126, 81, 27), center, 12)
            label = self.small_font.render(str(number), True, (255, 238, 199))
            self.screen.blit(label, label.get_rect(center=center))

    def _board(self):
        pg = self.pg
        board = self.controller.session.game.board
        width, height = self.screen.get_size()
        panel = (28, 106, width - 306, height - 135)
        pg.draw.rect(self.screen, (20, 41, 59), panel,
                     border_radius=24)
        pg.draw.rect(self.screen, (44, 77, 98), panel, 2,
                     border_radius=24)
        for cell, origin in self.layout.points.items():
            for direction in ("E", "SE", "SW"):
                neighbor = board.next_direction(cell, direction)
                if neighbor in self.layout.points:
                    pg.draw.line(self.screen, (42, 67, 82), origin,
                                 self.layout.points[neighbor], 3)
        for cell, origin in self.layout.points.items():
            radius = self.layout.radius
            pg.draw.circle(self.screen, (9, 24, 36),
                           (origin[0], origin[1] + 3), radius + 4)
            pg.draw.circle(self.screen, (40, 64, 80), origin, radius + 2)
            pg.draw.circle(self.screen, (28, 50, 67), origin, max(2, radius - 1))
            if cell in self.controller.targets:
                pg.draw.circle(self.screen, (111, 213, 153), origin, radius + 4, 3)
                if cell in self.controller.jump_targets:
                    label = (self.body_font if radius >= 15 else self.small_font).render(
                        str(len(self.controller.paths[cell]) - 1), True,
                        (137, 231, 170))
                    self.screen.blit(label, label.get_rect(center=origin))
                else:
                    pg.draw.circle(self.screen, (111, 213, 153), origin, radius // 3)
            if cell == self.controller.selected:
                pg.draw.circle(self.screen, (255, 210, 115), origin, radius + 6, 4)
        path = self._route_path()
        self._draw_route_lines(path)
        for cell, origin in self.layout.points.items():
            radius = self.layout.radius
            color = board.cell_contents(cell)
            if color != "O":
                piece_color = PIECE_COLORS[color]
                pg.draw.circle(self.screen, (8, 20, 32),
                               (origin[0] + 2, origin[1] + 4), max(2, radius - 3))
                pg.draw.circle(self.screen, piece_color, origin, max(2, radius - 4))
                lighter = tuple(min(255, channel + 38) for channel in piece_color)
                pg.draw.circle(self.screen, lighter,
                               (origin[0] - radius // 4, origin[1] - radius // 4),
                               max(1, radius // 5))
        self._draw_route_badges(path)

    def _history(self):
        width, height = self.screen.get_size()
        panel = (28, 106, width - 306, height - 135)
        self.pg.draw.rect(self.screen, (20, 41, 59), panel, border_radius=24)
        self.pg.draw.rect(self.screen, (44, 77, 98), panel, 2, border_radius=24)
        self._text("MOVE HISTORY", (52, 128), self.heading_font)
        self._text("Scroll / Up / Down for earlier moves. H returns to the board.",
                   (52, 163), self.small_font, (153, 183, 201))
        lines = self._history_lines()
        capacity = max(1, (height - 230) // 23)
        end = max(0, len(lines) - self.history_offset)
        start = max(0, end - capacity)
        if not lines:
            self._text("No moves recorded yet.", (52, 211), self.body_font)
        for index, line in enumerate(lines[start:end]):
            self._text(line, (52, 207 + index * 23), self.small_font)

    def _sidebar(self):
        pg = self.pg
        game = self.controller.session.game
        session = self.controller.session
        width, height = self.screen.get_size()
        left = width - 258
        panel = (left, 106, 234, height - 135)
        pg.draw.rect(self.screen, (20, 41, 59), panel,
                     border_radius=24)
        pg.draw.rect(self.screen, (44, 77, 98), panel, 2,
                     border_radius=24)
        x = left + 24
        self._text("MATCH", (x, 132), self.heading_font)
        mode = "  |  Teams" if game.is_group else ""
        sets = len(game.players[0].get_color())
        self._text(f"Size {game.board.size}  |  {len(game.players)} players" + mode,
                   (x, 170), self.small_font,
                   (153, 183, 201))
        if sets > 1:
            self._text(f"{sets} colors per player", (x, 190), self.small_font,
                       (153, 183, 201))
        groups = game.group() if game.is_group else []
        computer_number = 0
        for index, player in enumerate(game.players):
            y = 216 + index * 42
            if session.current_player is player:
                pg.draw.rect(self.screen, (33, 65, 78), (x - 8, y - 5, 200, 37),
                             border_radius=7)
            for number, color in enumerate(player.get_color()):
                pg.draw.circle(self.screen, PIECE_COLORS[color],
                               (x + 11 + number * 16, y + 10), 7)
            name = player.get_name()
            if name == "computer":
                computer_number += 1
                name = f"Computer {computer_number}"
            name_x = x + 26 + (sets - 1) * 16
            self._text(name[:12], (name_x, y), self.small_font)
            if groups:
                team = next(i + 1 for i, colors in enumerate(groups)
                            if player.get_color()[0] in colors)
                self._text(f"T{team}", (x + 169, y), self.small_font,
                           (153, 183, 201))
            if session.current_player is player:
                self._text("TURN", (x + 145, y + 17), self.small_font,
                           (111, 213, 153))
        pg.draw.line(self.screen, (56, 88, 104),
                     (x, height - 276), (x + 185, height - 276), 1)
        heading = "GAME OVER" if session.status != "playing" else "CURRENT TURN"
        self._text(heading, (x, height - 247), self.heading_font)
        for index, line in enumerate(textwrap.wrap(self.controller.message, 25)[:3]):
            self._text(line, (x, height - 212 + index * 20), self.small_font,
                       (174, 199, 213))
        self._button(self.pass_button, "Pass  [P]", not self.show_history
                     and session.status == "playing"
                     and session.current_player is not None
                     and session.current_player.get_name() != "computer")
        self._button(self.new_button, "Settings  [N]")
        self._text("Esc  Close & save", (x, height - 24), self.small_font,
                   (153, 183, 201))

    def draw(self):
        self.screen.fill((10, 25, 38))
        self._text("CHINESE CHECKERS", (31, 35), self.title_font)
        self._text("Numbers show jump counts; hover to trace the route", (33, 78),
                   self.small_font, (153, 183, 201))
        self._history() if self.show_history else self._board()
        self._button(self.history_button, "Board  [H]" if self.show_history
                     else "History  [H]")
        self._sidebar()


class GraphicalApp:
    """Switch between setup and match views and route window events."""

    def __init__(self, pygame, screen, store, computer=False):
        self.pg = pygame
        self.screen = screen
        self.store = store
        saved = store.load()
        if saved and saved.get("started") == 1 and saved.get("end") == 0:
            self._open_game(restore_game(saved, store=store))
        else:
            self.view = PygameSetupView(pygame, screen, store,
                                        SetupSelection(computer_count=int(computer)))

    def _open_game(self, game):
        self.view = PygameView(self.pg, self.screen,
                               VisualController(GameSession(game)), self.store)

    def _menu_action(self, action):
        if action == "start":
            game = self.view.start_game()
        elif action == "resume":
            game = self.view.resume_game()
        else:
            return
        if game is not None:
            self._open_game(game)

    def _settings_if_requested(self):
        if isinstance(self.view, PygameView) and self.view.request_setup:
            selection = SetupSelection.from_game(self.view.controller.session.game)
            self.view = PygameSetupView(self.pg, self.screen, self.store, selection)

    def _key(self, event):
        if isinstance(self.view, PygameSetupView):
            self._menu_action(self.view.handle_key(event))
        elif event.key == self.pg.K_n:
            self.view.new_game()
        elif event.key == self.pg.K_h:
            self.view.toggle_history()
        elif event.key == self.pg.K_UP:
            self.view.scroll_history(3)
        elif event.key == self.pg.K_DOWN:
            self.view.scroll_history(-3)
        elif event.key == self.pg.K_p and not self.view.show_history:
            self.view.controller.pass_turn()

    def _click(self, position):
        if isinstance(self.view, PygameSetupView):
            self._menu_action(self.view.handle_click(position))
        else:
            self.view.handle_click(position)

    def handle_event(self, event):
        """Return False only when the user asks to close the window."""
        if event.type == self.pg.QUIT or (
            event.type == self.pg.KEYDOWN and event.key == self.pg.K_ESCAPE
        ):
            return False
        if event.type == self.pg.VIDEORESIZE:
            self.screen = self.pg.display.set_mode(
                (max(960, event.w), max(740, event.h)), self.pg.RESIZABLE)
            self.view.resize(self.screen)
        elif event.type == self.pg.KEYDOWN:
            self._key(event)
        elif event.type == self.pg.MOUSEBUTTONDOWN and event.button == 1:
            self._click(event.pos)
        elif event.type == self.pg.MOUSEMOTION and isinstance(self.view, PygameView):
            self.view.handle_motion(event.pos)
        elif event.type == self.pg.MOUSEWHEEL and isinstance(self.view, PygameView):
            self.view.scroll_history(event.y * 3)
        self._settings_if_requested()
        return True

    def draw(self):
        if isinstance(self.view, PygameView):
            self.view.controller.play_computer_turn()
        self.view.draw()


def run(argv=None):
    """Show settings for a new match, or resume a saved graphical match."""
    parser = argparse.ArgumentParser(description="Play Chinese checkers in a window.")
    parser.add_argument("--computer", action="store_true",
                        help="Preselect one computer player on the settings screen")
    parser.add_argument("--new", action="store_true", help="Discard the visual save")
    args = parser.parse_args(argv)
    try:
        import pygame
    except ImportError as exc:
        raise SystemExit('Install the GUI extra: python -m pip install -e ".[gui]"') from exc

    logging.basicConfig(filename="visual_checkers.log", level=logging.INFO,
                        encoding="utf-8")
    store = GameStorage("visual_game_data.json")
    if args.new:
        store.clear()
    pygame.init()
    try:
        screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
        pygame.display.set_caption("Chinese Checkers")
        app = GraphicalApp(pygame, screen, store, args.computer)
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if not app.handle_event(event):
                    running = False
            if running:
                app.draw()
                pygame.display.flip()
                clock.tick(30)
    finally:
        pygame.quit()


if __name__ == "__main__":
    run()
