"""Print the same deterministic sample round described in the README."""

from logic_utils import create_game_state, get_hint, process_guess


def main() -> None:
    """Run a fixed-secret logic demo, not a browser play session."""
    state = create_game_state("Normal", secret=50)
    print("Logic demo: Normal difficulty, fixed secret 50, 8 attempts, score 0")
    for raw in ("40", "70", "50"):
        state = process_guess(state, raw)
        print(
            f"Input {raw}: {get_hint(state['last_outcome'])} "
            f"Score={state['score']}; attempts={state['attempts']}; "
            f"status={state['status']}"
        )
    stopped = process_guess(state, "50")
    print(f"Another guess after the win changes nothing: {stopped == state}")
    fresh = create_game_state("Normal", secret=75)
    print(
        f"Fresh round: score={fresh['score']}; attempts={fresh['attempts']}; "
        f"status={fresh['status']}; history={fresh['history']}"
    )


if __name__ == "__main__":
    main()
