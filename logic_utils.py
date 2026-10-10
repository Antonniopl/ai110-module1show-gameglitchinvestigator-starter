"""Game rules independent of Streamlit, so they can be tested directly."""

import random
import re
from typing import Literal, TypedDict


DIFFICULTY_RANGES = {"Easy": (1, 20), "Normal": (1, 100), "Hard": (1, 50)}
ATTEMPT_LIMITS = {"Easy": 6, "Normal": 8, "Hard": 5}


class GameState(TypedDict):
    """Values that belong to one game round."""

    difficulty: str
    secret: int
    attempts: int
    score: int
    status: Literal["playing", "won", "lost"]
    history: list[int]
    last_outcome: str | None
    error: str | None


def get_range_for_difficulty(difficulty: str) -> tuple[int, int]:
    """Return the starter's inclusive range; unknown names use Normal."""
    return DIFFICULTY_RANGES.get(difficulty, DIFFICULTY_RANGES["Normal"])


def parse_guess(
    raw: str | None, low: int = 1, high: int = 100
) -> tuple[bool, int | None, str | None]:
    """Accept a whole-number string inside the active inclusive range.

    Invalid player input returns an error instead of raising an exception.
    Decimals, scientific notation, and underscores are not accepted.
    """
    if low > high:
        raise ValueError("The lower bound must not exceed the upper bound.")
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return False, None, "Enter a guess."
    if not isinstance(raw, str):
        return False, None, "Enter a whole number."

    # FIX B3: AI-assisted repair rejects decimals instead of truncating them.
    text = raw.strip()
    if re.fullmatch(r"[+-]?[0-9]+", text) is None:
        return False, None, "Enter a whole number (no decimals)."
    try:
        value = int(text)
    except ValueError:
        # Python may reject extremely long integer strings; do not crash.
        return False, None, "That number is too large."
    if not low <= value <= high:
        return False, None, f"Enter a number from {low} to {high}."
    return True, value, None


def check_guess(guess: int, secret: int) -> str:
    """Return Win, Too High, or Too Low using integer comparisons only."""
    # FIX B2: AI-assisted refactor removes the misleading string fallback.
    # Preserve the result-string contract used by the original three tests.
    if type(guess) is not int or type(secret) is not int:
        raise TypeError("guess and secret must both be integers")
    if guess == secret:
        return "Win"
    if guess > secret:
        return "Too High"
    return "Too Low"


def get_hint(outcome: str) -> str:
    """Turn a result into an actionable hint without changing the rules."""
    # FIX B1: AI-assisted correction makes high guesses point downward.
    messages = {
        "Win": "Correct!",
        "Too High": "Too High. Guess LOWER!",
        "Too Low": "Too Low. Guess HIGHER!",
    }
    if outcome not in messages:
        raise ValueError(f"Unknown outcome: {outcome}")
    return messages[outcome]


def update_score(current_score: int, outcome: str, attempt_number: int) -> int:
    """Apply the documented scoring policy with a one-based attempt number.

    Wrong valid guesses cost 5 points. A win adds 100 points on the first
    valid attempt, 90 on the second, and so on, with a 10-point minimum bonus.
    The round score starts at zero and may be negative before a win.
    """
    if type(attempt_number) is not int or attempt_number < 1:
        raise ValueError("attempt_number must be a positive integer")
    if outcome == "Win":
        return current_score + max(10, 100 - 10 * (attempt_number - 1))
    # FIX B4: AI-assisted repair treats both kinds of wrong guesses equally.
    if outcome in ("Too High", "Too Low"):
        return current_score - 5
    return current_score


def create_game_state(difficulty: str, secret: int | None = None) -> GameState:
    """Create a clean round, optionally with a fixed secret for testing."""
    if difficulty not in DIFFICULTY_RANGES:
        raise ValueError(f"Unknown difficulty: {difficulty}")
    low, high = get_range_for_difficulty(difficulty)
    if secret is None:
        secret = random.randint(low, high)
    if type(secret) is not int or not low <= secret <= high:
        raise ValueError("The secret must be an integer in the difficulty range.")
    # FIX B5/B6: AI-assisted repair initializes every round field together.
    return {
        "difficulty": difficulty,
        "secret": secret,
        "attempts": 0,
        "score": 0,
        "status": "playing",
        "history": [],
        "last_outcome": None,
        "error": None,
    }


def process_guess(state: GameState, raw: str | None) -> GameState:
    """Return updated round state without mutating the caller's state.

    Invalid input consumes no attempt. Finished rounds ignore new guesses.
    A correct guess on the last allowed attempt still wins.
    """
    updated: GameState = {**state, "history": list(state["history"])}
    if state["status"] != "playing":
        return updated

    low, high = get_range_for_difficulty(state["difficulty"])
    ok, guess, error = parse_guess(raw, low, high)
    updated["error"] = error
    if not ok:
        return updated
    assert guess is not None

    # FIX B7: AI-assisted repair counts only a validated, in-range guess.
    updated["attempts"] += 1
    updated["history"].append(guess)
    outcome = check_guess(guess, updated["secret"])
    updated["last_outcome"] = outcome
    updated["score"] = update_score(
        updated["score"], outcome, updated["attempts"]
    )
    if outcome == "Win":
        updated["status"] = "won"
    elif updated["attempts"] >= ATTEMPT_LIMITS[updated["difficulty"]]:
        updated["status"] = "lost"
    return updated
