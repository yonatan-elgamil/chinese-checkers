"""Match settings and the Pygame menu; the board builder lives in setup.py."""

from dataclasses import dataclass, field
import textwrap

from .setup import PLAYER_COUNTS, SetupOptions, build_game


@dataclass
class SetupSelection:
    """Editable settings, kept valid as the number of players changes."""

    size: int = 4
    player_count: int = 2
    computer_count: int = 0
    sets_per_player: int = 1
    teams: int = 0
    names: list[str] = field(default_factory=lambda: [f"Player {i}" for i in range(1, 7)])

    @classmethod
    def from_game(cls, game):
        players = game.players
        human_names = [player.get_name() for player in players
                       if player.get_name() != "computer"]
        selection = cls(game.board.size, len(players), len(players) - len(human_names),
                        len(players[0].get_color()), game.is_group)
        selection.names[:len(human_names)] = human_names
        return selection

    @property
    def human_count(self):
        return self.player_count - self.computer_count

    @property
    def options(self):
        return SetupOptions(self.size, self.player_count, self.computer_count,
                            self.sets_per_player, self.teams)

    def adjust(self, field, amount):
        """Change a setting and constrain settings that depend on it."""
        if field == "size":
            self.size = max(4, self.size + 3 * amount)
        elif field == "players":
            index = PLAYER_COUNTS.index(self.player_count)
            self.player_count = PLAYER_COUNTS[max(0, min(len(PLAYER_COUNTS) - 1,
                                                         index + amount))]
            self.computer_count = min(self.computer_count, self.player_count - 1)
            self.sets_per_player = min(self.sets_per_player,
                                       3 if self.player_count == 2 else
                                       2 if self.player_count == 3 else 1)
            if self.player_count not in (4, 6):
                self.teams = 0
        elif field == "computers":
            self.computer_count = max(0, min(self.player_count - 1,
                                             self.computer_count + amount))
        elif field == "sets" and self.player_count in (2, 3):
            limit = 3 if self.player_count == 2 else 2
            self.sets_per_player = max(1, min(limit, self.sets_per_player + amount))
        elif field == "teams" and self.player_count in (4, 6):
            self.teams = 1 - self.teams

    def build(self, store):
        """Use the same placement factory as the terminal."""
        return build_game(self.options, self.names[:self.human_count], store)


class PygameSetupView:
    """Draw the menu and collect only settings and human names."""

    FIELDS = ("size", "players", "computers", "sets", "teams")

    def __init__(self, pygame, screen, store, selection=None):
        self.pg = pygame
        self.store = store
        self.selection = selection or SetupSelection()
        self.focus = None
        self.replace_on_type = False
        self.message = "Starting corners, colors and pieces are placed automatically."
        self.resume_available = self._saved_game() is not None
        self.title_font = pygame.font.SysFont("arial", 31, bold=True)
        self.heading_font = pygame.font.SysFont("arial", 23, bold=True)
        self.body_font = pygame.font.SysFont("arial", 19)
        self.small_font = pygame.font.SysFont("arial", 16)
        self.button_font = pygame.font.SysFont("arial", 18, bold=True)
        self.resize(screen)

    def _saved_game(self):
        saved = self.store.load()
        return saved if saved and saved.get("started") == 1 and saved.get("end") == 0 else None

    def resize(self, screen):
        self.screen = screen
        width, height = screen.get_size()
        left = (width - 908) // 2
        self.left_panel = self.pg.Rect(left, 106, 430, height - 135)
        self.right_panel = self.pg.Rect(left + 450, 106, 458, height - 135)
        self.controls = {}
        for index, field in enumerate(self.FIELDS):
            y = 218 + index * 72
            self.controls[field] = (self.pg.Rect(left + 272, y, 40, 36),
                                    self.pg.Rect(left + 366, y, 40, 36))
        self.name_fields = [self.pg.Rect(left + 478, 220 + index * 61, 400, 39)
                            for index in range(6)]
        self.resume_button = self.pg.Rect(left + 474, height - 99, 170, 48)
        self.start_button = self.pg.Rect(left + 666, height - 99, 212, 48)

    def handle_click(self, position):
        if self.start_button.collidepoint(position):
            return "start"
        if self.resume_available and self.resume_button.collidepoint(position):
            return "resume"
        self.focus = None
        for index, rect in enumerate(self.name_fields[:self.selection.human_count]):
            if rect.collidepoint(position):
                self.focus = index
                self.replace_on_type = True
                return None
        for field, (minus, plus) in self.controls.items():
            if minus.collidepoint(position):
                self.selection.adjust(field, -1)
            elif plus.collidepoint(position):
                self.selection.adjust(field, 1)
        return None

    def handle_key(self, event):
        if self.focus is None:
            return "start" if event.key == self.pg.K_RETURN else None
        if event.key == self.pg.K_RETURN:
            self.focus = None
        elif event.key == self.pg.K_TAB:
            self.focus = (self.focus + 1) % self.selection.human_count
            self.replace_on_type = True
        elif event.key == self.pg.K_BACKSPACE:
            self.selection.names[self.focus] = ("" if self.replace_on_type else
                                                self.selection.names[self.focus][:-1])
            self.replace_on_type = False
        elif (event.unicode.isprintable() and
              (self.replace_on_type or len(self.selection.names[self.focus]) < 18)):
            if self.replace_on_type:
                self.selection.names[self.focus] = ""
            self.selection.names[self.focus] += event.unicode
            self.replace_on_type = False
        return None

    def start_game(self):
        """Validate first; replace an existing save only after a valid setup."""
        try:
            game = self.selection.build(self.store)
        except ValueError as exc:
            self.message = str(exc)
            return None
        self.store.clear()
        return game

    def resume_game(self):
        from .setup import restore_game

        saved = self._saved_game()
        return restore_game(saved, store=self.store) if saved else None

    def _text(self, value, x, y, font, color=(227, 236, 245)):
        self.screen.blit(font.render(value, True, color), (x, y))

    def _button(self, rect, label, enabled=True):
        fill = (47, 101, 131) if enabled else (43, 57, 70)
        self.pg.draw.rect(self.screen, fill, rect, border_radius=9)
        self.pg.draw.rect(self.screen, (88, 140, 166), rect, 1, border_radius=9)
        text = self.button_font.render(label, True, (237, 244, 249))
        self.screen.blit(text, text.get_rect(center=rect.center))

    def _settings(self):
        s = self.selection
        values = (str(s.size), str(s.player_count), str(s.computer_count),
                  str(s.sets_per_player) if s.player_count in (2, 3) else "1",
                  "Yes" if s.teams else "No")
        labels = ("Board size", "Players", "Computer players", "Colors per player", "Teams")
        for index, field in enumerate(self.FIELDS):
            y = 219 + index * 72
            available = field not in ("sets", "teams") or (
                field == "sets" and s.player_count in (2, 3) or
                field == "teams" and s.player_count in (4, 6))
            color = (227, 236, 245) if available else (111, 133, 146)
            self._text(labels[index], self.left_panel.x + 24, y + 5,
                       self.body_font, color)
            minus, plus = self.controls[field]
            self._button(minus, "-", available)
            self._text(values[index], minus.right + 10, y + 6, self.body_font, color)
            self._button(plus, "+", available)

    def _names(self):
        s = self.selection
        for index, rect in enumerate(self.name_fields[:s.human_count]):
            self._text(f"Human {index + 1}", rect.x, rect.y - 19, self.small_font,
                       (153, 183, 201))
            self.pg.draw.rect(self.screen, (28, 50, 67), rect, border_radius=7)
            outline = (111, 213, 153) if index == self.focus else (70, 104, 124)
            self.pg.draw.rect(self.screen, outline, rect, 2, border_radius=7)
            if index == self.focus and self.replace_on_type:
                label_width = min(rect.width - 18, self.body_font.size(s.names[index])[0])
                self.pg.draw.rect(self.screen, (47, 101, 131),
                                  (rect.x + 9, rect.y + 5, label_width + 2, 28),
                                  border_radius=3)
            self._text(s.names[index][:18], rect.x + 10, rect.y + 7, self.body_font)
        if s.computer_count:
            self._text(f"+ {s.computer_count} computer player(s)",
                       self.right_panel.x + 24, 568, self.small_font,
                       (153, 183, 201))

    def draw(self):
        screen = self.screen
        screen.fill((10, 25, 38))
        self._text("CHINESE CHECKERS", 31, 35, self.title_font)
        self._text("Choose a match, then play on the automatically filled board.",
                   33, 78, self.small_font, (153, 183, 201))
        for panel in (self.left_panel, self.right_panel):
            self.pg.draw.rect(screen, (20, 41, 59), panel, border_radius=24)
            self.pg.draw.rect(screen, (44, 77, 98), panel, 2, border_radius=24)
        self._text("MATCH SETTINGS", self.left_panel.x + 24, 133, self.heading_font)
        self._text("Board sizes: 4, 7, 10, 13, ...", self.left_panel.x + 24,
                   174, self.small_font, (153, 183, 201))
        self._settings()
        self._text("HUMAN PLAYERS", self.right_panel.x + 24, 133, self.heading_font)
        self._text("Click a name to edit it", self.right_panel.x + 24, 165,
                   self.small_font, (153, 183, 201))
        self._names()
        for index, line in enumerate(textwrap.wrap(self.message, 39)[:2]):
            self._text(line, self.left_panel.x + 24,
                       self.screen.get_height() - 154 + index * 21,
                       self.small_font, (174, 199, 213))
        self._button(self.resume_button, "Resume save", self.resume_available)
        self._button(self.start_button, "Start game")
