"""Regression tests: retain the three starter cases and add edge cases."""

from copy import deepcopy

import pytest

from logic_utils import (
    ATTEMPT_LIMITS,
    create_game_state,
    get_hint,
    get_range_for_difficulty,
    parse_guess,
    process_guess,
    update_score,
)

from logic_utils import check_guess

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"


@pytest.mark.parametrize(
    "difficulty, expected",
    [("Easy", (1, 20)), ("Normal", (1, 100)), ("Hard", (1, 50)),
     ("Unknown", (1, 100))],
)
def test_difficulty_ranges_are_preserved(difficulty, expected):
    assert get_range_for_difficulty(difficulty) == expected


@pytest.mark.parametrize(
    "raw, expected",
    [("1", 1), ("100", 100), ("50", 50), (" 50 ", 50),
     ("+50", 50), ("050", 50), ("\t25\n", 25)],
)
def test_parse_valid_whole_numbers(raw, expected):
    assert parse_guess(raw) == (True, expected, None)


@pytest.mark.parametrize(
    "raw",
    [None, "", "   ", "abc", "40.9", "50.0", "1e1", "1_0", "NaN", "inf",
     "-inf", "+", "--5", "0", "-1", "101", "99999999999999999999",
     "9" * 5000, 50, 50.5, True],
)
def test_bad_input_is_rejected_without_crashing(raw):
    ok, value, error = parse_guess(raw)
    assert ok is False
    assert value is None
    assert isinstance(error, str) and error


@pytest.mark.parametrize("low, high", [(1, 20), (1, 100), (1, 50)])
def test_parse_accepts_both_inclusive_boundaries(low, high):
    assert parse_guess(str(low), low, high) == (True, low, None)
    assert parse_guess(str(high), low, high) == (True, high, None)
    assert parse_guess(str(low - 1), low, high)[0] is False
    assert parse_guess(str(high + 1), low, high)[0] is False


def test_invalid_range_is_a_programming_error():
    with pytest.raises(ValueError):
        parse_guess("5", 10, 1)


@pytest.mark.parametrize(
    "guess, secret, expected",
    [(9, 50, "Too Low"), (100, 50, "Too High"), (2, 10, "Too Low"),
     (10, 2, "Too High"), (1, 1, "Win"), (100, 100, "Win")],
)
def test_comparisons_are_numeric(guess, secret, expected):
    assert check_guess(guess, secret) == expected


@pytest.mark.parametrize(
    "guess, secret",
    [(9, "50"), ("9", 50), (50.0, 50), (None, 50), (True, 1)],
)
def test_mixed_types_cannot_silently_become_string_comparisons(guess, secret):
    with pytest.raises(TypeError):
        check_guess(guess, secret)


@pytest.mark.parametrize(
    "outcome, expected",
    [("Too High", "Too High. Guess LOWER!"),
     ("Too Low", "Too Low. Guess HIGHER!"), ("Win", "Correct!")],
)
def test_hint_direction_matches_the_result(outcome, expected):
    assert get_hint(outcome) == expected


def test_unknown_hint_is_rejected():
    with pytest.raises(ValueError):
        get_hint("Something else")


@pytest.mark.parametrize("attempt", [1, 2, 3, 4, 8])
@pytest.mark.parametrize("outcome", ["Too High", "Too Low"])
def test_every_wrong_guess_costs_five_points(outcome, attempt):
    assert update_score(0, outcome, attempt) == -5
    assert update_score(20, outcome, attempt) == 15


@pytest.mark.parametrize("attempt, bonus", [(1, 100), (2, 90), (3, 80), (10, 10), (99, 10)])
def test_win_bonus_has_a_documented_one_based_count(attempt, bonus):
    assert update_score(-10, "Win", attempt) == -10 + bonus


@pytest.mark.parametrize("attempt", [0, -1, 1.5, True])
def test_invalid_attempt_number_is_rejected(attempt):
    with pytest.raises(ValueError):
        update_score(0, "Win", attempt)


def test_unknown_outcome_preserves_score():
    assert update_score(15, "Unknown", 1) == 15


@pytest.mark.parametrize("difficulty", ["Easy", "Normal", "Hard"])
def test_new_round_initializes_every_field(difficulty):
    state = create_game_state(difficulty, secret=10)
    assert state == {
        "difficulty": difficulty, "secret": 10, "attempts": 0, "score": 0,
        "status": "playing", "history": [], "last_outcome": None, "error": None,
    }


@pytest.mark.parametrize("difficulty", ["Easy", "Normal", "Hard"])
def test_random_secret_uses_the_selected_range(monkeypatch, difficulty):
    calls = []

    def pick_upper_bound(low, high):
        calls.append((low, high))
        return high

    monkeypatch.setattr("logic_utils.random.randint", pick_upper_bound)
    state = create_game_state(difficulty)
    assert calls == [get_range_for_difficulty(difficulty)]
    assert state["secret"] == get_range_for_difficulty(difficulty)[1]


@pytest.mark.parametrize("secret", [0, 21, "10", True])
def test_invalid_fixed_secret_is_rejected(secret):
    with pytest.raises(ValueError):
        create_game_state("Easy", secret=secret)


def test_new_round_rejects_unknown_difficulty():
    with pytest.raises(ValueError):
        create_game_state("Impossible")


@pytest.mark.parametrize("raw", ["", "abc", "40.9", "-1", "101", "9" * 5000])
def test_invalid_guess_preserves_attempts_score_and_history(raw):
    original = create_game_state("Normal", secret=50)
    before = deepcopy(original)
    state = process_guess(original, raw)
    assert original == before
    assert state["attempts"] == 0
    assert state["score"] == 0
    assert state["history"] == []
    assert state["status"] == "playing"
    assert state["secret"] == 50
    assert state["error"]


def test_error_clears_after_a_valid_guess():
    state = process_guess(create_game_state("Normal", secret=50), "abc")
    state = process_guess(state, "40")
    assert state["error"] is None
    assert state["last_outcome"] == "Too Low"
    assert state["attempts"] == 1


def test_first_guess_can_win_with_full_bonus():
    state = process_guess(create_game_state("Normal", secret=50), "50")
    assert state["status"] == "won"
    assert state["attempts"] == 1
    assert state["score"] == 100
    assert state["history"] == [50]


def test_exact_demo_walkthrough():
    state = create_game_state("Normal", secret=50)
    state = process_guess(state, "40")
    assert (state["last_outcome"], state["score"], state["attempts"]) == ("Too Low", -5, 1)
    state = process_guess(state, "70")
    assert (state["last_outcome"], state["score"], state["attempts"]) == ("Too High", -10, 2)
    state = process_guess(state, "50")
    assert (state["status"], state["score"], state["attempts"]) == ("won", 70, 3)
    assert state["history"] == [40, 70, 50]


@pytest.mark.parametrize("difficulty", ["Easy", "Normal", "Hard"])
def test_game_loses_after_exactly_the_allowed_valid_guesses(difficulty):
    state = create_game_state(difficulty, secret=10)
    for attempt in range(1, ATTEMPT_LIMITS[difficulty] + 1):
        state = process_guess(state, "1")
        expected = "lost" if attempt == ATTEMPT_LIMITS[difficulty] else "playing"
        assert state["status"] == expected
        assert state["attempts"] == attempt
        assert state["secret"] == 10
    assert state["score"] == -5 * ATTEMPT_LIMITS[difficulty]


@pytest.mark.parametrize("difficulty", ["Easy", "Normal", "Hard"])
def test_correct_guess_on_last_attempt_wins(difficulty):
    state = create_game_state(difficulty, secret=10)
    for _ in range(ATTEMPT_LIMITS[difficulty] - 1):
        state = process_guess(state, "1")
    state = process_guess(state, "10")
    assert state["attempts"] == ATTEMPT_LIMITS[difficulty]
    assert state["status"] == "won"


@pytest.mark.parametrize("terminal_status", ["won", "lost"])
def test_finished_game_ignores_more_guesses(terminal_status):
    state = create_game_state("Normal", secret=50)
    state["status"] = terminal_status
    state["score"] = 70
    before = deepcopy(state)
    assert process_guess(state, "50") == before
    assert state == before


def test_processing_does_not_mutate_prior_state_or_share_history():
    old = create_game_state("Normal", secret=50)
    updated = process_guess(old, "40")
    assert old["history"] == []
    assert updated["history"] == [40]
    assert old["attempts"] == 0
    updated["history"].append(70)
    assert old["history"] == []


def test_new_round_does_not_inherit_a_finished_round():
    finished = process_guess(create_game_state("Normal", secret=50), "50")
    fresh = create_game_state("Easy", secret=10)
    assert finished["status"] == "won"
    assert fresh["status"] == "playing"
    assert fresh["score"] == 0 and fresh["attempts"] == 0
    assert fresh["history"] == [] and fresh["difficulty"] == "Easy"


def test_secret_does_not_change_between_submissions():
    state = create_game_state("Normal", secret=50)
    for raw in ["9", "abc", "40", "70", "50"]:
        state = process_guess(state, raw)
        assert state["secret"] == 50
        assert type(state["secret"]) is int
