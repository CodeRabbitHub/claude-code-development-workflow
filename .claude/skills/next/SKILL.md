---
name: next
description: Pop the next brief from plans/backlog/ and start the slice. Use at the start of an unattended session, or when HANDOFF.md is done and work should continue without waiting for the user.
---

Continue the loop without a human in the seat.

This is what makes the kit run overnight. Step 10 normally ends the
session; with a backlog it hands straight to the next slice instead.

1. Read HANDOFF.md. If the previous slice is incomplete, finish that
   first — never start a new slice on top of an unmerged one.
2. If `.claude/.replan_needed` exists, STOP. A breaker fired and a human
   must re-plan. Do not pop new work on top of a failed slice; say what
   the three attempts revealed and wait.
3. List `plans/backlog/*.md`, ignoring files starting with `_`. They run
   in filename order — that is why the naming is `NN-slug.md`.
4. Take the first one. Validate it against templates/brief.md with the
   same pushback rules as /brief: single-outcome goal, binary and runnable
   done-check, non-empty out-of-scope. A backlog brief that fails
   validation is NOT silently fixed — move it to `_blocked-<name>.md`,
   record why, and take the next one. An unattended agent guessing at an
   ambiguous brief is exactly how a night of slop gets made.
5. Move the brief to `plans/briefs/YYYY-MM-DD-<slug>.md`, create the slice
   branch, and enter the loop at step 3 (PLAN).
6. Gates still gate. Gate 1 and Gate 2 both notify and both wait — the
   backlog removes the waiting BETWEEN slices, never the waiting AT a
   gate. If you are running parallel streams, park this stream at its gate
   and let the others proceed.
7. When the backlog is empty, write HANDOFF.md, notify, and stop.
