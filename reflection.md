# Reflection: Game Glitch Investigator

> **Student confirmation required before submission:** Personal gameplay observations, independent review, learning statements, and separate bug chats were not supplied or verified. The answers below are a factual project record prepared by Codex, not a claim about the student's personal experience.

## 1. What was broken when you started?

The starter presented a number-guessing game with a difficulty selector, text input, and a debug panel showing the secret. Executing its original helpers reproduced reversed hints, string comparisons that gave the wrong outcome, decimal truncation, and a wrong guess increasing the score. Automated Streamlit checks also confirmed that invalid inputs consumed attempts and that New Game did not reset every round field. The table records assistant-run helper checks.

### Bug Reproduction Logs

The original definitions are preserved in `evidence/original_app.py.txt`, and the reproduction command is `python tools/reproduce_starter_bugs.py`.

| Input Used | Expected Behavior | Actual Behavior | Console Error / Output |
|---|---|---|---|
| `check_guess(60, 50)` | Too High; tell the player to guess lower. | Outcome was Too High, but the hint pointed higher. | No exception; `('Too High', '📈 Go HIGHER!')` |
| `check_guess(9, "50")` | Compare numeric values: 9 is too low. | String comparison reported Too High. | No exception; `('Too High', '📈 Go HIGHER!')` |
| `parse_guess("40.9")` | Reject a decimal. | Accepted the changed value 40. | No exception; `(True, 40, None)` |
| `parse_guess("-1")` | Reject a guess below the minimum of 1. | Accepted -1; the original caller also lacked a range check. | No exception; `(True, -1, None)` |
| `update_score(0, "Too High", 2)` | Apply the same 5-point penalty as other wrong guesses. | Added five points for a wrong guess. | No exception; `5` |

The additional original-UI reproduction command is `python tools/reproduce_original_ui.py`; its output in `evidence/codex_original_ui_results.txt` records decimal acceptance, reset failure, reversed hints, and invalid input consuming an attempt.

## 2. How did you use AI as a teammate?

The supplied handoff contained ChatGPT-prepared repairs, tests, and draft documentation, which Codex reviewed and verified in this workspace. A correct technical proposal was to separate numeric comparison from hint formatting while preserving the original three test contracts; the regression suite checks both the outcome and the displayed direction. An AI-prepared documentation claim was not accepted as written: the draft said that a wording-only hint fix had been proposed and rejected, but no provided transcript establishes that exchange. Codex removed that unsupported claim after comparing the draft with the available conversation evidence.

## 3. Debugging and testing your fixes

Verification compares the original failing behavior with targeted regression cases and runs the full suite after repairs. The deterministic walkthrough checks guesses of 40, 70, and 50 against a secret of 50, including hint direction, attempts, and the final score of 70. Additional AI-assisted tests cover invalid input, scoring, loss conditions, resets, and difficulty changes. The current full-suite output is recorded in `test_results.txt` and the README, including all 13 Streamlit `AppTest` cases that were skipped in the earlier handoff environment. Codex separately checked the repaired game in a real browser, with the observed inputs and results saved in `evidence/codex_browser_checks.txt`.

## 4. What did you learn about Streamlit and state?

Streamlit runs the application's script again when a user interacts with a widget. Session state acts like a notebook that keeps the current secret, score, attempt count, and history between those reruns. The repaired game updates that state in callbacks before drawing its counters and messages. An ordinary guess preserves the secret, while New Game or a difficulty change creates a complete new round.

## 5. Looking ahead: your developer habits

The project supports a useful debugging habit: record a reproducible input and its expected result before editing the code. A focused follow-up request should then ask AI to explain one issue, propose a small repair, and identify the test that would catch the original failure. The review also shows why generated documentation needs evidence checks, just as generated code needs tests. The resulting code is easier to assess when each repair has an explicit rule and a matching regression test.
