# Backlog — pre-written briefs, queued

Files here are full briefs (every field in templates/brief.md) waiting
their turn. `/next` pops the lowest-numbered one, validates it, moves it
to `plans/briefs/`, and starts the slice.

Naming: `NN-slug.md` — `01-auth-endpoint.md`, `02-rate-limit.md`.
Files starting with `_` are ignored (this file, and blocked briefs).

## Why this exists

Without it, step 10 ends the session and the machine idles until you come
back. With it, an approved slice rolls straight into the next one, so the
run continues overnight and only stops at gates and failures.

## The rule that keeps this safe

Queue only briefs you would have approved anyway. The backlog removes the
wait BETWEEN slices; it does not remove a gate, and it does not let a
vague brief through — `/next` parks anything that fails validation as
`_blocked-<name>.md` rather than guessing. Three or four queued slices is
a night's work; twenty is a plan you have not really thought about.
