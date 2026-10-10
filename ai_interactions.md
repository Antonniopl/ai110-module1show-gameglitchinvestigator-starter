# AI Interactions Log

This log distinguishes available conversation evidence from the earlier handoff's descriptions. The personal-reflection limitation is recorded in `reflection.md`.

## Request and assistance

The user supplied a prepared project handoff, asked whether Codex could complete it, and later requested completion. Codex used the supplied repair candidate as a starting point, checked it against the actual starter repository, ran the tests with Streamlit available, and reviewed the documentation for unsupported claims.

The handoff attributes its initial generation to ChatGPT and records this earlier request:

> Can you thoroughly review this and complete what you can? I also need you to include very simple instructions on what I need to do for submission for this and anything you cannot do.

That quotation is transcribed from the supplied handoff, not independently verified against a separate chat export. Neither the provided history nor the current conversation contains a distinct student-authored prompt asking for each individual edge-case test. The table therefore reports the tests and their rationale without inventing prompts.

## Test Generation — Challenge 1

| Edge case | AI-assisted regression coverage | Why chosen |
|---|---|---|
| Negative number, `-1` | Invalid-input parsing and unchanged-round checks. | It is below every difficulty's minimum and must not consume an attempt. |
| Decimal, `40.9` | Decimal rejection and unchanged-round checks. | The original parser silently changed it to 40. |
| Extremely large input, including 5,000 digits | Invalid-input parsing and unchanged-round checks. | The app should return an error instead of crashing or changing the round. |
| Empty input and letters | Error handling in logic and relevant UI checks. | A submit click should not count as a guess before validation succeeds. |
| Lowest and highest allowed values | Inclusive-boundary tests. | Both endpoints are legal guesses. |
| Correct guess on the final attempt | Final-attempt win regression. | A win must take priority over the exhausted-attempt loss condition. |

The actual full-suite output appears in `test_results.txt` and the README. It includes Streamlit `AppTest` coverage, which the earlier handoff skipped because Streamlit was unavailable there.

## Accepted technical proposal

The candidate separates `check_guess()` from `get_hint()`, uses integer comparisons, and preserves the three starter tests. Codex retained that design after verifying comparison outcomes and hint direction with regression tests.

## Correction to an AI-prepared draft

The handoff's draft claimed that a wording-only HIGHER/LOWER fix had been suggested and rejected. The available record contains no transcript establishing that exchange, so Codex rejected the claim as unsupported and removed it. The technical observation remains valid—changing words alone would not fix string comparisons—but it is not presented as an interaction that actually occurred.

The draft also pointed to a completed local verification entry that was still a placeholder. The final documentation instead links to the current recorded test output.
