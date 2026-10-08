# Chinese Checkers

A configurable Chinese Checkers game developed in Python, featuring both a graphical interface built with Pygame and a terminal-based interface.

The project demonstrates object-oriented programming, modular software architecture, graph search algorithms, heuristic computer players, automated testing, and game-state persistence.

![Six-player team match](assets/gui-preview.png)

## Features

- **Multiple game modes:** Play with 2, 3, 4, or 6 players, including human and computer-controlled players.
- **Customizable board sizes:** Supports sizes 4, 7, 10, and larger valid sizes of the form `3n + 1`.
- **Computer opponents:** Automated players use heuristic strategies and pathfinding algorithms to select moves.
- **Team matches:** Supports team-based gameplay with four or six players.
- **Multiple colors:** Supports configurations where one player controls multiple colors.
- **Automatic setup:** Starting positions and player assignments are configured automatically based on the selected game settings.
- **Graphical interface:** Interactive, resizable Pygame window with highlighted legal moves and multi-jump path previews.
- **Terminal interface:** A command-line alternative using the same game logic.
- **Save and resume:** Game progress can be saved and restored using JSON files.
- **Game history:** Track moves and display previous turns.
- **Automated testing:** 145 tests covering game rules, algorithms, object consistency, game configurations, persistence, and graphical interaction.

## Technologies

- Python 3.9+
- Pygame
- Object-Oriented Programming (OOP)
- Breadth-First Search (BFS)
- Heuristic Algorithms
- JSON Serialization
- Pytest
- Git and GitHub

## Installation

### Requirements

- Python 3.9 or later
- pip

Clone the repository:

```bash
git clone https://github.com/yonatan-elgamil/chinese-checkers.git
cd chinese-checkers
```

### Install dependencies

For the graphical interface:

```bash
python -m pip install -e ".[gui]"
```

For the terminal interface only:

```bash
python -m pip install -e .
```

For development and testing:

```bash
python -m pip install -e ".[test,gui]"
```

On Windows, `py -3` can be used instead of `python` if necessary.

## Running the Game

### Graphical Interface

Start a new game with a computer opponent preselected:

```bash
python -m chinese_checkers.gui --new --computer
```

Resume an existing game or open the setup screen:

```bash
python -m chinese_checkers.gui
```

The `--new` option starts a new configuration and replaces the previous graphical save.

![Game setup screen](assets/setup-preview.png)

### Graphical Controls

| Control | Action |
| --- | --- |
| Click a piece | Select a playing piece |
| Click a highlighted cell | Move the selected piece |
| Hover over a highlighted destination | Preview the multi-jump route |
| P | Pass the current turn |
| H | Show or hide game history |
| N | Open new game settings |
| Esc | Exit the graphical interface |

### Windows Launchers

The project also includes Windows batch files for convenient execution:

- `start_new_game.bat` — Start a new graphical match.
- `start_gui.bat` — Resume a saved match or open the game settings.

These launchers can install the graphical dependency if necessary.

### Terminal Interface

Run the command-line version:

```bash
python -m chinese_checkers
```

Follow the instructions to configure a new match or resume a saved one.

Coordinates are entered using the format `row,column`, starting from 1.

Use `pass` at the beginning of a turn to skip it.

For command-line help:

```bash
python -m chinese_checkers --help
```

## Architecture

The project follows a modular, object-oriented design that separates game logic, computer strategies, user interfaces, and data persistence.

Both the terminal and graphical interfaces share the same game rules, configuration logic, and turn-management system.

### Main Components

| Component | Responsibility |
| --- | --- |
| `Board` | Board geometry, storage of `Ball` objects, legal movements, and jump paths |
| `Ball` | Individual playing pieces, their colors, and positions |
| `Player` | Player information, assigned colors, and results |
| `Game` | Match state, move validation, victory conditions, and rankings |
| `GameSession` | Turn progression and events shared between the interfaces |
| `ComputerStrategy` | Computer move selection, strategic pathfinding, and heuristics |
| `setup.py` | Game configuration, automatic placement, and save restoration |
| `gui.py` | Graphical gameplay and interaction |
| `gui_setup.py` | Graphical game configuration |
| `terminal.py`, `cli.py` | Terminal interaction and command-line execution |
| `storage.py` | JSON save and load functionality |
| `logs.py` | Game logging and turn history |

### Board and Piece Representation

The board stores actual `Ball` objects rather than using only color values to represent occupied cells.

Each occupied cell references a playing piece, while empty cells contain `None`.

The `Board` and `Game` maintain references to the same `Ball` instances, ensuring that board occupancy and piece positions remain synchronized.

When a move is performed:

1. The game validates the selected piece and destination.
2. The board verifies the move and updates the occupied cells.
3. The original `Ball` object is moved to its new position.
4. The game continues using the updated state.

Separate color snapshots are used for serialization and board-state comparisons.

This design provides a clear separation between the active object-based game state and its serialized representation.

### Separation of Responsibilities

The main components have distinct responsibilities:

**Board**

Responsible for board geometry, occupied cells, legal steps, and multi-jump movements.

**ComputerStrategy**

Responsible for move selection, goal-directed heuristics, and strategic path searches.

Computer planning is performed without modifying the active game state.

**Game**

Responsible for managing players, validating moves, tracking match progress, and determining results.

**GameSession**

Controls turn progression independently of graphical rendering or terminal input.

This allows both interfaces to use the same game rules.

## Algorithms and Computer Player

### Breadth-First Search (BFS)

The project uses BFS for pathfinding.

The `Board.jump_paths` method explores reachable destinations through legal jumps and identifies shortest jump sequences.

Each jump requires an occupied intermediate cell and an empty landing cell.

The graphical interface uses these paths to display possible multi-jump routes.

### Heuristic Computer Strategy

Computer-controlled players use a heuristic approach rather than exhaustive adversarial search.

The strategy considers factors such as:

- Progress toward the target area.
- Reachability of goal positions.
- Shortest paths to selected destinations.
- Availability of empty cells near the goal.
- Avoiding moves that obstruct the player's own target area.

Strategic pathfinding and decision-making logic are centralized in the `ComputerStrategy` class.

Some decisions involve randomized selections.

The strategy is designed to make legal, goal-directed moves, but it does not guarantee optimal play.

## Saving and Loading Games

The project supports JSON-based persistence.

Game saves include information such as:

- Board state and piece locations.
- Player information and assigned colors.
- Current turn and game progress.
- Match configuration.
- Information required to resume the game.

The object-based board representation is compatible with the existing JSON save format.

Terminal and graphical games use separate save files.

Generated save files and logs are excluded from version control.

## Automated Testing

The project includes unit, integration, and graphical interaction tests using Pytest.

The test suite covers:

- Board geometry and valid coordinates.
- Legal steps and multi-jump movements.
- `Ball` and `Player` functionality.
- Shared object identity and position synchronization.
- Computer move selection and planning isolation.
- Player configurations and team assignments.
- Turn progression and victory conditions.
- Saving, loading, and compatibility with legacy saves.
- Graphical rendering and input handling.

### Running Tests

Install the development dependencies:

```bash
python -m pip install -e ".[test,gui]"
```

Run all tests:

```bash
python -m pytest -v
```

For a shorter output:

```bash
python -m pytest -q
```

### Test Results

**145 tests passed.**

Verified locally on Windows with Python 3.11.2:

```text
145 passed in 2.12s
```

Additional regression validation compared the refactored implementation with the original project, including match traces, board states, pathfinding results, saved-game restoration, and graphical rendering.

Detailed validation information is available in [TEST_RESULTS.md](TEST_RESULTS.md).

## Project Structure

```text
chinese-checkers/
|
|-- assets/
|   |-- gui-preview.png
|   |-- setup-preview.png
|
|-- chinese_checkers/
|   |-- __init__.py
|   |-- __main__.py
|   |-- ai.py
|   |-- ball.py
|   |-- board.py
|   |-- cli.py
|   |-- game.py
|   |-- gui.py
|   |-- gui_setup.py
|   |-- logs.py
|   |-- player.py
|   |-- session.py
|   |-- setup.py
|   |-- storage.py
|   |-- terminal.py
|   |-- utils.py
|
|-- tests/
|   |-- test_ball.py
|   |-- test_board.py
|   |-- test_game.py
|   |-- test_integration.py
|   |-- test_player.py
|   |-- test_refactor.py
|   |-- test_utils.py
|   |-- test_visual.py
|
|-- .gitignore
|-- pyproject.toml
|-- README.md
|-- TEST_RESULTS.md
|-- start_gui.bat
|-- start_new_game.bat
```

## Development and Design

This project was developed as part of object-oriented programming practice and subsequently extended and refactored to improve code organization and maintainability.

The refactoring focused on:

- Representing playing pieces as objects directly within the board.
- Separating computer decision-making from board movement rules.
- Improving method naming and code readability.
- Using explicit constructors for data-holding classes.
- Maintaining consistency between board state and piece objects.
- Preserving existing game behavior and save compatibility.
- Expanding regression testing.

The resulting design emphasizes modularity, encapsulation, separation of responsibilities, and reusable game logic.