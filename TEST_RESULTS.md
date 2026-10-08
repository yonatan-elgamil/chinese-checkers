# Refactor validation

Validation date: 2026-10-07. The baseline was the supplied `chinese-checkers(1).zip`.

Environment: Python 3.12, pytest 9.1.1 and Pygame 2.6.1 on Linux.

## Automated suite

- Original project before changes: **118 passed**.
- Refactored project: **145 passed**, with no skipped tests.
- All 118 existing cases retain their expected game outcomes. Calls and fixtures were migrated to the renamed API and the new strategy location.
- 27 additional cases cover shared `Ball` identity, movement and jump identity, rejected moves, detached snapshots, planning isolation, legacy saves, default-list isolation and ordinary-class value/read-only behavior.
- Pygame rendering and event-loop cases execute with a headless SDL display.

## Comparison with the original implementation

The two versions were loaded separately and given identical random seeds and player inputs.

| Comparison | Result |
| --- | --- |
| Match traces | 54 identical traces: 9 match types × 3 board sizes × 2 seeds |
| Turn snapshots | 748 identical snapshots, including legal moves, jump paths, turn events, standings and JSON checkpoints |
| Interrupted matches | Each eligible trace restored from a checkpoint after five completed turns |
| Random board positions | 60 identical positions, covering board sizes 4, 7 and 10 |
| Multi-turn BFS routes | 360 identical routes on those random boards |
| Graphical output | Identical rendered pixels for a six-player team match |

These finite comparisons support preservation of the existing behavior; they are not an exhaustive proof for every possible board state. The supplied heuristic strategy was retained.

Package metadata and build were checked with a successful wheel build using `pyproject.toml`.

## Reproduce the bundled suite

Run from the directory containing `pyproject.toml`:

```bash
python -m pip install -e ".[test,gui]"
python -m pytest -q
```

On Windows, `py -3` can replace `python`. The batch launchers retain their original commands; they were not executed on Windows during this validation.
