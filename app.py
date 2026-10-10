"""Streamlit interface for the repaired number-guessing game."""

import streamlit as st

from logic_utils import (
    ATTEMPT_LIMITS,
    create_game_state,
    get_hint,
    get_range_for_difficulty,
    process_guess,
)


def reset_game() -> None:
    """Reset the complete round before Streamlit renders its widgets."""
    # FIX B6: AI-assisted callback resets score, status, history, and input.
    st.session_state.game = create_game_state(st.session_state.difficulty)
    st.session_state.guess_input = ""


def submit_guess() -> None:
    """Apply a guess before rendering the updated attempts and score."""
    # FIX B2/B7: UI calls the same integer-based rules that pytest verifies.
    st.session_state.game = process_guess(
        st.session_state.game, st.session_state.guess_input
    )


st.set_page_config(page_title="Game Glitch Investigator", page_icon="🎮")
st.title("🎮 Game Glitch Investigator")
st.caption("A repaired number-guessing game with testable Python rules.")

st.sidebar.header("Settings")
difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
    key="difficulty",
    on_change=reset_game,
)

if "game" not in st.session_state:
    st.session_state.game = create_game_state(difficulty)
if "guess_input" not in st.session_state:
    st.session_state.guess_input = ""

game = st.session_state.game
low, high = get_range_for_difficulty(difficulty)
attempt_limit = ATTEMPT_LIMITS[difficulty]
finished = game["status"] != "playing"

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")
st.sidebar.caption("Changing difficulty starts a new round.")

st.subheader("Make a guess")
# FIX B5: Display the active range and post-callback attempt count.
st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {max(0, attempt_limit - game['attempts'])}"
)
st.write(f"Score: {game['score']}")

st.text_input("Enter your guess:", key="guess_input", disabled=finished)
col1, col2, col3 = st.columns(3)
with col1:
    st.button(
        "Submit Guess 🚀",
        key="submit_guess",
        on_click=submit_guess,
        disabled=finished,
    )
with col2:
    st.button("New Game 🔁", key="new_game", on_click=reset_game)
with col3:
    show_hint = st.checkbox("Show hint", value=True, key="show_hint")

if game["error"]:
    st.error(game["error"])
elif show_hint and game["last_outcome"] and not finished:
    st.warning(get_hint(game["last_outcome"]))

# Terminal results remain visible even when hints are turned off.
if game["status"] == "won":
    st.success(
        f"You won! The secret was {game['secret']}. "
        f"Final score: {game['score']}. Start a new game to play again."
    )
elif game["status"] == "lost":
    st.error(
        f"Out of attempts! The secret was {game['secret']}. "
        f"Score: {game['score']}. Start a new game to try again."
    )

with st.expander("Developer Debug Info"):
    st.caption("For project testing only: this panel reveals the answer.")
    st.write("Secret:", game["secret"])
    st.write("Attempts:", game["attempts"])
    st.write("Score:", game["score"])
    st.write("Difficulty:", game["difficulty"])
    st.write("History:", game["history"])
    st.write("Status:", game["status"])

st.divider()
st.caption("AI-assisted repairs; verify changes with tests and manual play.")
