# Architecture — irreversible decisions only

Rules for this file:
- Only decisions that are EXPENSIVE TO REVERSE belong here (language,
  storage, component boundaries, external services, auth approach).
  Everything else stays deliberately undecided until a slice forces it.
- Every decision gets a one-line why.
- Changes happen by explicit amendment at a gate — never by drift. If a
  generated design or a library pulls in a new assumption (a framework, a
  build step), that is a PROPOSAL to amend this file, not a decision.

## Decisions

<!-- Example format:
- Python 3, stdlib core — must run anywhere with zero install.
- SQLite for state — single user, single file, no server to operate.
- CLI first, web UI later — logic testable before any rendering exists.
-->
