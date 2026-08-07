# Eval — <behavior name>

Slice: <link to brief>
Created:
Runner: <command, or "manual">

<!-- An eval is a test whose answer isn't deterministic. That difference is
     why this template asks for more bookkeeping than a test does: a score
     with no record of WHAT PRODUCED IT cannot distinguish a regression you
     caused from a model that changed underneath you. -->

## What is being checked
<!-- The LLM-driven behavior or quality bar this protects. One sentence.
     If you can express it as a deterministic assertion, write a TEST
     instead — tests are free and run on every push; evals cost money and
     are non-deterministic, which is why they never belong on push CI. -->

## Pass threshold
<!-- Declare the bar BEFORE running, or you will rationalize whatever score
     you get. Two numbers:
       PASS  — at or above this, the slice may merge.
       FLOOR — below this, stop and re-plan: the approach is wrong, not the
               prompt. -->

Pass: ___ / ___ cases      Floor: ___ / ___ cases

## Provenance
<!-- Fill this EVERY run. Without it a score is uninterpretable. The most
     common false alarm in agent work is a "regression" that was really a
     model version change; the most common missed regression is a prompt
     edit nobody recorded. -->

| Field | Value |
|---|---|
| Model + version | <e.g. claude-sonnet-4-6> |
| Prompt version | <commit hash, or file@version> |
| Retrieval / context source | <index version, doc set, or n/a> |
| Temperature / sampling | |
| Run date | |

## Cases
<!-- Real inputs beat synthetic. Start with 5; every production or demo
     failure adds a case — that is how this file earns its keep. Re-run the
     WHOLE set on any prompt, model, or retrieval change: a subset proves
     nothing about the cases you skipped. -->

| # | Input | Expected | Actual | Pass? | Notes |
|---|-------|----------|--------|-------|-------|
| 1 |       |          |        |       |       |
| 2 |       |          |        |       |       |
| 3 |       |          |        |       |       |
| 4 |       |          |        |       |       |
| 5 |       |          |        |       |       |

## Grader
<!-- exact match / code assertion / LLM-as-judge with rubric / human.
     If LLM-as-judge: paste the rubric verbatim, and record the JUDGE's own
     model version above too — a judge that silently upgrades moves every
     score you have and looks exactly like a real change. -->

## Score history
<!-- Append one row per run, never overwrite. Gate 2 check 3 reads the
     previous row; a drop blocks the merge. This table IS the baseline that
     templates/review.md asks for. -->

| Date | Score | Model | Prompt ver | Verdict | What changed since last run |
|---|---|---|---|---|---|
|  |  |  |  |  | baseline |

## Known failure modes
<!-- The ways this behavior breaks that you have already seen. Each one
     should become a case above. Until it is a case, it is a rumor. -->
