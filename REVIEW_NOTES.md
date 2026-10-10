# Technical Review and Evidence Limits

## Findings and repairs

| Finding | Repair |
|---|---|
| Hint messages send players in the wrong direction. | `get_hint()` maps Too High to LOWER and Too Low to HIGHER. |
| The original UI sometimes converts the secret to a string and falls back to string comparison. | The repaired state stores an integer secret; `check_guess()` requires integers. |
| Decimals are truncated and values outside the active range are accepted. | `parse_guess()` validates whole-number syntax and inclusive bounds before a guess changes the round. |
| A wrong high guess can add five points. | Both wrong outcomes subtract five points. |
| The initial round starts with one attempt already used. | Every round starts with zero attempts. |
| Invalid input consumes attempts and changes history. | Validation errors preserve attempts, score, and history. |
| New Game leaves completed status, score, and history behind. | A single reset creates all round fields together and clears the input. |
| New Game always chooses a secret from 1–100, and difficulty changes retain the previous secret. | Both actions reset using the selected range. |
| The main range label is hard-coded and counters can lag behind a submitted guess. | Dynamic range text and callbacks render the current round values. |

The original helper behavior is reproducible from the preserved source. The completed rule suite and Streamlit `AppTest` suite check the repaired behavior, including the UI callbacks, resets, and displayed counters.

## Source and draft inconsistencies

1. The starter README claims that the secret changes on every Submit click. The inspected app initializes it only when `secret` is absent from session state, so that description is not supported by this version's ordinary-guess path. This was a misleading source claim, not evidence of an AI suggestion received during the project.
2. The original app returns a tuple from `check_guess()`, but the three starter tests expect an outcome string. The repair preserves those tests and separates hint formatting into `get_hint()`.
3. The handoff's AI-prepared reflection claimed that a wording-only hint repair had been considered and rejected. No supplied transcript supports that interaction. Codex removed the claim; the project log does not turn a hypothetical bad repair into an event that happened.
4. The handoff README referred readers to a completed local-check entry even though the corresponding reflection still contained a placeholder. That reference was replaced with actual test output.
5. The earlier `105 passed, 1 skipped` output skipped the entire UI module, containing 13 cases. It did not mean that all but one UI test passed. Streamlit is installed for the current full-suite run.

6. One assignment step names `test/test_game_logic.py`, while the starter and required-files list use `tests/test_game_logic.py`; the project keeps the existing `tests/` directory.

## Explicit design decisions

The original difficulty ranges and attempt limits are preserved, including Hard's smaller range and lower attempt limit. Every valid wrong guess costs five points; a win adds a decreasing bonus beginning at 100 points. Invalid inputs have no attempt or score penalty. New Game and difficulty changes reset score and history, and a correct guess on the final attempt wins. These are documented repair decisions rather than claims about a scoring formula mandated by the starter.

## Verification and attribution

The README and `test_results.txt` contain the actual current pytest output. Original-source reproduction and deterministic walkthrough scripts make the main results rerunnable. The earlier handoff's environment and results are preserved under `evidence/prior_assistant/` as historical evidence. The current full suite passed all 118 cases, with zero skips, on Python 3.11.13, Streamlit 1.60.0, and pytest 9.1.1. The original-app reproduction emits nonfatal AppTest context and sandbox CPU-probe warnings, retained in its log; they are not game exceptions. Codex's real-browser smoke check is recorded separately in `evidence/codex_browser_checks.txt`.

Codex performed the technical verification and documentation review described here. The personal-experience limitation is stated prominently in `reflection.md`; no student play, independent review, separate bug chat, or personal learning statement is inferred from automated test results. A public repository link is not evidence of course-portal submission.

## Dependencies and scope

The repaired requirements use Streamlit 1.31 or newer within major version 1, plus pytest. The app does not import Altair directly, so Streamlit resolves its compatible chart dependency. Only Challenge 1's advanced edge-case tests are claimed as an optional extension; there is no claim of persisted high scores, a model comparison, a linting challenge, or deployment.
