# Re-plan — <slice name>

Date:
Brief: <link to the brief that failed>
Breaker fired after: 3 attempts

<!-- The circuit breaker just stopped a slice. This file exists because
     that moment is the highest-information event the loop produces and it
     otherwise evaporates into chat.

     The premise: three GENUINELY DIFFERENT failures almost never mean the
     model is weak. They mean something one level up is wrong — an
     ambiguous brief, a false architectural assumption, a test that encodes
     something the brief never promised, or a slice cut across a boundary
     that doesn't hold. Attempt #4 cannot fix any of those, which is why
     the breaker refuses to allow one.

     Fill this BEFORE proposing a new plan. The diagnosis is the point;
     the new brief is just its consequence. -->

## What each attempt tried, and what it revealed

<!-- One row per attempt. "Revealed" is the column that matters — if all
     three say the same thing, you were retrying, not diagnosing, and the
     real cause is still unidentified. -->

| # | Approach taken | How it failed | What that ruled out |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |

## The failure they have in common
<!-- One sentence. If you cannot write it, do not re-plan yet — gather one
     more piece of evidence instead (read the failing test's assumptions,
     check the ARCHITECT decision it depends on, run the smallest possible
     repro by hand). -->

## Where the real problem lives
<!-- Tick one. This determines what changes, and each has a different fix.
     Choosing "the code" after three failures is almost always wrong — that
     is the answer attempts 1-3 already disproved. -->

- [ ] **The brief** — ambiguous, or promised something under-specified.
      → Rewrite the brief. The done-check probably wasn't binary in practice.
- [ ] **The tests** — they encode something the brief never promised, or
      test an implementation detail.
      → Amend via `.claude/.unlock`, and record it in the slice log.
- [ ] **The architecture** — a decision in ARCHITECT.md doesn't hold.
      → Amend ARCHITECT.md explicitly. Never let this drift silently.
- [ ] **The slice boundary** — too big, or cut across a seam that doesn't exist.
      → Re-cut into smaller slices; write the first one only.
- [ ] **An external reality** — the API, data, or dependency isn't what we
      assumed.
      → Record the finding; the brief's Inputs were wrong.

## What changes
<!-- The specific edit to the brief, tests, architecture, or slice cut.
     Be concrete: "add UTC assumption to Constraints", not "clarify". -->

## The new first slice
<!-- Smaller than the one that failed. If it isn't smaller, you have not
     actually re-planned — you have restated. Every field in templates/brief.md; this becomes
     the next brief. -->

Goal:
Constraints:
Inputs:
Outputs:
Assumptions:
Done-check:
Out-of-scope:
Rollback:

## Promote?
<!-- The ratchet applies here too. If this cause has now appeared twice,
     it graduates: a standing rule in CLAUDE.md, a line in
     templates/no-slop.md, a hook, or a case in an eval. A breaker that
     fires twice for the same reason is a system defect, not bad luck. -->

Seen before? (y/n):    Promoting to:

## Clear the flag
<!-- After the user approves the new plan:  rm .claude/.replan_needed
     Do this LAST. While it exists, /next refuses to pop new work and
     session_start warns — which is correct, because an unresolved re-plan
     is exactly what you don't want a fresh session building on top of. -->
