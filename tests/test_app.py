"""Streamlit callback checks; require Streamlit and must also be run locally.

A missing Streamlit installation skips this module explicitly. Such a skip
is not evidence that the UI passed. The logic suite remains runnable alone.
"""

from pathlib import Path

import pytest

from logic_utils import create_game_state

streamlit_testing = pytest.importorskip(
    "streamlit.testing.v1", reason="Streamlit is needed to verify the real UI"
)
AppTest = streamlit_testing.AppTest
APP = Path(__file__).resolve().parents[1] / "app.py"


@pytest.fixture
def app():
    view = AppTest.from_file(str(APP), default_timeout=10).run()
    assert not view.exception
    view.session_state["game"] = create_game_state("Normal", secret=50)
    view.run()
    return view


def submit(app, raw):
    app.text_input(key="guess_input").set_value(raw)
    app.button(key="submit_guess").click().run()
    assert not app.exception
    return app.session_state["game"]


def test_ui_starts_with_eight_attempts(app):
    assert "Attempts left: 8" in app.info[0].value
    assert app.session_state["game"]["attempts"] == 0


def test_ui_updates_hint_and_counter_without_an_extra_click(app):
    state = submit(app, "40")
    assert state["score"] == -5
    assert "HIGHER" in app.warning[0].value
    assert "Attempts left: 7" in app.info[0].value


@pytest.mark.parametrize("raw", ["abc", "40.9", "-1", "999999999999999999999"])
def test_ui_invalid_input_does_not_count(app, raw):
    state = submit(app, raw)
    assert state["attempts"] == 0
    assert state["history"] == []
    assert len(app.error) == 1


def test_ui_win_disables_further_submission(app):
    state = submit(app, "50")
    assert state["status"] == "won"
    assert app.button(key="submit_guess").disabled
    assert app.text_input(key="guess_input").disabled
    assert "You won!" in app.success[0].value


def test_ui_new_game_resets_after_a_win(app):
    submit(app, "50")
    app.button(key="new_game").click().run()
    assert not app.exception
    state = app.session_state["game"]
    assert state["status"] == "playing"
    assert state["score"] == 0 and state["attempts"] == 0
    assert state["history"] == []
    assert app.text_input(key="guess_input").value == ""
    assert not app.button(key="submit_guess").disabled


def test_ui_new_game_resets_after_a_loss(app):
    for _ in range(8):
        submit(app, "40")
    assert app.session_state["game"]["status"] == "lost"
    assert "Attempts left: 0" in app.info[0].value
    app.button(key="new_game").click().run()
    assert not app.exception
    assert app.session_state["game"]["status"] == "playing"
    assert app.session_state["game"]["attempts"] == 0


@pytest.mark.parametrize("difficulty, high, limit", [("Easy", 20, 6), ("Hard", 50, 5)])
def test_ui_difficulty_change_starts_a_matching_round(app, difficulty, high, limit):
    submit(app, "40")
    app.selectbox(key="difficulty").set_value(difficulty).run()
    assert not app.exception
    state = app.session_state["game"]
    assert state["difficulty"] == difficulty
    assert 1 <= state["secret"] <= high
    assert state["attempts"] == 0 and state["score"] == 0
    assert state["history"] == []
    assert f"between 1 and {high}" in app.info[0].value
    assert f"Attempts left: {limit}" in app.info[0].value


def test_ui_hiding_hints_does_not_hide_a_win(app):
    app.checkbox(key="show_hint").set_value(False).run()
    submit(app, "50")
    assert "You won!" in app.success[0].value


def test_ui_hint_toggle_preserves_the_round(app):
    submit(app, "40")
    before = dict(app.session_state["game"])
    app.checkbox(key="show_hint").set_value(False).run()
    assert not app.exception
    assert app.session_state["game"] == before
    assert len(app.warning) == 0
