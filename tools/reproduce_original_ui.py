"""Agent-run AppTest reproductions of defects in the unchanged starter.

These are automated Streamlit AppTest observations, not student observations
and not a real-browser play session. Only random.randint is patched, making
Normal difficulty choose secret 50 without changing the original app source.
"""

import hashlib
import json
import platform
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import streamlit
from streamlit.testing.v1 import AppTest


APP = Path(__file__).resolve().parents[1] / "evidence" / "original_app.py.txt"


def state(view):
    return {
        key: deepcopy(view.session_state[key])
        for key in ("secret", "attempts", "score", "status", "history")
    }


def messages(view):
    return {
        kind: [item.value for item in getattr(view, kind)]
        for kind in ("info", "warning", "error", "success")
    }


def fresh_game():
    view = AppTest.from_file(str(APP), default_timeout=10).run()
    assert not view.exception, view.exception
    assert view.session_state["secret"] == 50
    assert view.session_state["status"] == "playing"
    return view


def submit(view, raw):
    view.text_input(key="guess_input_Normal").set_value(raw)
    view.button[0].click().run()
    assert not view.exception, view.exception


def report(case, inputs, expected, actual):
    print(json.dumps({
        "case": case,
        "input_used": inputs,
        "expected_behavior": expected,
        "actual_behavior": actual,
        "console_error": "No app exception; AppTest messages are recorded above.",
        "defect_assertions": "PASS: defect reproduced",
    }, indent=2, ensure_ascii=False), flush=True)


def main():
    original_digest = hashlib.sha256(APP.read_bytes()).hexdigest()
    print("AGENT-RUN STREAMLIT APPTEST: ORIGINAL GAME DEFECT REPRODUCTIONS")
    print("Not student observations; not browser gameplay.")
    print("App: evidence/original_app.py.txt")
    print(f"App SHA-256: {original_digest}")
    print(f"Python: {platform.python_version()}")
    print(f"Streamlit: {streamlit.__version__}")
    print("Control: patch random.randint to return 50; no app-source changes.")
    print("Expected behavior below is an explicit proposed game policy.", flush=True)

    with patch("random.randint", return_value=50):
        view = fresh_game()
        submit(view, "50.9")
        assert view.session_state["status"] == "won"
        assert view.session_state["history"] == [50]
        assert any("You won!" in item.value for item in view.success)
        report(
            "1: Decimal accepted as a winning integer",
            "Fresh Normal game, secret 50; Submit Guess with 50.9.",
            "Reject non-whole-number input; do not convert the guess or award a win.",
            {"state": state(view), "messages": messages(view)},
        )

        won_score = view.session_state["score"]
        view.button[1].click().run()
        assert not view.exception, view.exception
        after_reset = {"state": state(view), "messages": messages(view)}
        assert view.session_state["status"] == "won"
        assert view.session_state["attempts"] == 0
        assert view.session_state["history"] == [50]
        assert view.session_state["score"] == won_score
        assert any("You already won" in item.value for item in view.success)
        submit(view, "40")
        assert view.session_state["status"] == "won"
        assert view.session_state["attempts"] == 0
        assert view.session_state["history"] == [50]
        report(
            "2: New Game after winning does not create a playable round",
            "After case 1: click New Game, then Submit Guess with 40.",
            "Start a fresh playing round, clear score/history, and process the next valid guess.",
            {"after_new_game": after_reset,
             "after_submitting_40": {"state": state(view), "messages": messages(view)}},
        )

        view = fresh_game()
        submit(view, "60")
        assert view.session_state["status"] == "playing"
        assert view.session_state["history"] == [60]
        assert any("Go HIGHER!" in item.value for item in view.warning)
        assert not any("LOWER" in item.value for item in view.warning)
        report(
            "3: Hint points away from the secret",
            "Fresh Normal game, secret 50; Submit Guess with 60.",
            "60 is greater than 50, so tell the player to guess LOWER.",
            {"state": state(view), "messages": messages(view)},
        )

        view = fresh_game()
        before = state(view)
        submit(view, "abc")
        assert view.session_state["attempts"] == before["attempts"] + 1
        assert view.session_state["history"] == ["abc"]
        assert any("That is not a number." in item.value for item in view.error)
        report(
            "4: Invalid input consumes an attempt",
            "Fresh Normal game; Submit Guess with abc.",
            "Display a validation error without consuming a valid guess attempt.",
            {"before": before, "after": state(view), "messages": messages(view)},
        )

    assert hashlib.sha256(APP.read_bytes()).hexdigest() == original_digest
    print("PASS: 4 defects reproduced by automated AppTest; original app source unchanged.")


if __name__ == "__main__":
    main()
