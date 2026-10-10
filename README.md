# Game Glitch Investigator: The Repaired Guesser

A Python and Streamlit number-guessing game repaired from the CodePath starter. Choose a difficulty, enter whole-number guesses, and follow the hints to find the secret before running out of attempts.

[GitHub repository](https://github.com/Antonniopl/ai110-module1show-gameglitchinvestigator-starter)

## Setup

Use Python 3.10 or newer. From the project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

On Windows, use `.venv\Scripts\activate` instead of the `source` command. Open the local URL printed by Streamlit.

Run the complete test suite with:

```bash
python -m pytest -q -ra
```

## Game rules

| Difficulty | Secret range, inclusive | Attempts |
|---|---|---|
| Easy | 1–20 | 6 |
| Normal | 1–100 | 8 |
| Hard | 1–50 | 5 |

Each round starts at zero points. A valid wrong guess costs 5 points. A win adds `max(10, 100 - 10 * (attempt_number - 1))` points: 100 on the first valid attempt, 90 on the second, and so on. Negative scores are allowed. This is the repair's explicit scoring policy; the starter does not define a complete scoring specification.

Blank input, decimals, letters, and numbers outside the active range show an error without using an attempt or changing the score or history. Whitespace and a leading plus sign are accepted for valid integers. A correct final-attempt guess wins. New Game and difficulty changes reset the whole round; a finished round accepts no further guesses.

## Document Your Experience

- The objective is to find the secret within the selected attempt limit.
- Reproduced bugs included reversed hints, string comparisons, decimal truncation, missing range validation, and a wrong guess increasing the score. Source review also found incomplete resets and invalid input consuming attempts.
- Core rules now live in `logic_utils.py`. The interface uses callbacks to update round state before rendering the counters and messages. One reset function starts every round consistently.

The original three starter tests are preserved. Their result-string contract is implemented by `check_guess()`, with hint text supplied separately by `get_hint()`. See [reflection.md](reflection.md) for the reproduction log and the distinction between assistant verification and personal reflection, and [REVIEW_NOTES.md](REVIEW_NOTES.md) for review decisions.

## Demo Walkthrough

This deterministic example uses Normal difficulty and a fixed secret of 50. It is checked by `test_exact_demo_walkthrough` and can be reproduced with `python -m tools.demo_walkthrough`. A browser round chooses its own random secret.

1. Start with score 0, no guesses used, and eight attempts available.
2. Enter `40`. The game says Too Low and tells the player to guess HIGHER. Score becomes -5 and seven attempts remain.
3. Enter `70`. The game says Too High and tells the player to guess LOWER. Score becomes -10 and six attempts remain.
4. Enter `50`. The game wins on attempt three. The 80-point bonus produces a final score of 70.
5. Further guesses do not change the completed round.
6. Select New Game. The score, attempts, history, and status reset, and the app generates a secret within the selected range.

The Developer Debug Info panel reveals the current secret for checking the game during this learning exercise.

## Test Results

The complete suite was executed with Streamlit installed, including the real Streamlit `AppTest` callback checks. The previous handoff's result of 105 passed and one skipped module did not execute its 13 UI cases; the current full-suite result replaces that incomplete verification.

```text
Executed by: Codex
Command: python -m pytest -q -ra
Python: 3.11.13
Streamlit: 1.60.0
pytest: 9.1.1

........................................................................ [ 61%]
..............................................                           [100%]
118 passed in 4.34s

Exit status: 0
```

See `test_results.txt` for the recorded command output. The suite covers the original comparisons, hint direction, scoring, invalid inputs, range boundaries, final-attempt wins, complete resets, difficulty changes, and UI counter updates. `AppTest` runs the application and its callbacks. Codex also checked decimal rejection, both hint directions, stable secrets, winning, and New Game in a real browser; see `evidence/codex_browser_checks.txt` and its win screenshot. These checks were performed by Codex, not supplied as student observations.

## Stretch Features

**Challenge 1: Advanced Edge-Case Testing** is implemented. Tests include negative numbers, decimals, very large values, empty input, inclusive boundaries, and a win on the final attempt. [ai_interactions.md](ai_interactions.md) records the available AI-assistance evidence and the reason for each edge case. No other optional challenge is claimed.

## Files

- `app.py`: Streamlit interface and callbacks.
- `logic_utils.py`: input validation, comparison, hints, scoring, and round transitions.
- `tests/test_game_logic.py` and `tests/test_app.py`: rule and interface regression tests.
- `tools/`: deterministic walkthrough and original-helper reproduction scripts.
- `evidence/`: preserved original source and execution evidence.
- `reflection.md`, `ai_interactions.md`, and `REVIEW_NOTES.md`: factual project notes and review history.
