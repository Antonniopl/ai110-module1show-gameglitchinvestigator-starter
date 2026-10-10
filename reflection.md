# Reflection: Game Glitch Investigator

## 1. What was broken when you started?

Codex inspected the original Streamlit game and reproduced defects using its unchanged helper functions.
The initial targets are incorrect high/low hints and invalid-input handling; string comparisons and scoring also need repair.
These observations are automated checks performed by Codex, not personal gameplay reports.
Personal play observations and independent review have not been supplied.

### Bug Reproduction Log — Codex helper checks

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|---|---|---|---|
| `check_guess(60, 50)` | Too High; guess lower | Hint says go higher | `('Too High', '📈 Go HIGHER!')`; no exception |
| `check_guess(9, "50")` | Numeric comparison: Too Low | Lexicographic comparison reports Too High | `('Too High', '📈 Go HIGHER!')`; no exception |
| `parse_guess("40.9")` | Reject a decimal | Converts to 40 and accepts it | `(True, 40, None)`; no exception |
| `parse_guess("-1")` | Reject below-range guess | Accepts -1 | `(True, -1, None)`; no exception |
| `update_score(0, "Too High", 2)` | Apply a consistent wrong-guess penalty | Adds 5 points | `5`; no exception |

Reproduction command: `python tools/reproduce_starter_bugs.py`.
Fresh output and original source are preserved in `evidence/`.
Original starter tests also run before repairs so their real baseline failures remain visible.

## Remaining reflection stages

AI collaboration, repaired-game verification, state explanations, and development habits will be documented after implementation.
Student-specific experiences will remain unconfirmed unless supplied.

### Codex Streamlit AppTest observations

With the original source and a controlled secret of 50, automated UI checks also reproduced decimal 50.9 being accepted as a win, New Game preserving won status and blocking subsequent play, and abc consuming an attempt. These are AppTest results, not student or browser gameplay. The executable reproduction and its fresh output are in tools/reproduce_original_ui.py and evidence/codex_original_ui_results.txt.
