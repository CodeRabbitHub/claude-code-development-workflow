# Brief — <slice name>

Date:
Milestone: <which PLAN.md milestone this serves>

Goal:
<!-- The one outcome, in a sentence. -->

Constraints:
<!-- What it must (and must not) do. Stack, perf, style, security. -->

Inputs:
<!-- What the agent starts with. Files, data, an API, an example. -->

Outputs:
<!-- What exists when it's finished. Files, endpoints, behavior. -->

Assumptions:
<!-- What you are taking as true without having checked. Every slice has
     some; the ones that sink a slice are the ones nobody wrote down, because
     an agent resolves unstated ambiguity silently and confidently.
     Examples: "the API returns UTC", "input is already validated upstream",
     "this runs single-threaded", "the file fits in memory".
     If an assumption turns out false mid-slice, that is a re-plan trigger,
     not a thing to code around. -->

Expected size:
<!-- Rough files touched and lines changed, against diff_cap in
     .claude/config.json. Declared HERE so Gate 2 check 1 confirms a
     prediction instead of delivering a surprise after the work is done.
     If the estimate is already over the cap, the slice is too big — cut it
     now, when cutting is free. -->

Done-check:
<!-- The concrete test that proves it works. Binary, and runnable as a
     single command — its pasted output is the only definition of done. -->

Out-of-scope:
<!-- What NOT to touch, so the agent doesn't wander. Binding, never empty. -->

Rollback:
<!-- How this gets undone. Usually "git revert <sha>" — say so explicitly
     if it isn't, i.e. if there is a migration, a schema change, or written
     external state. Named at brief time rather than at the gate, because
     discovering a slice is irreversible AFTER building it is the expensive
     order to find out. -->
