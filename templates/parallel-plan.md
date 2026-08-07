# Parallel plan

Qualifies only if: workstreams are independent (short shared-files list),
each has its own brief + proof, and you have review capacity for all.
Otherwise: don't parallelize — re-cut the boundaries or go sequential.

Goal:
<!-- The one milestone all workstreams serve. -->

Workstream A: <link to its brief>
Workstream B: <link to its brief>

Max 3 streams. Beyond that YOU are the bottleneck — the gates queue up
and the extra streams just generate work you cannot review.

The real payoff is not speed. It is that parallel streams ABSORB GATE
LATENCY: when one stream hits Gate 2 at 03:00 and waits for you, the
others keep working until morning instead of the machine idling.

File ownership:
<!-- Every stream declares the files it OWNS. One owner per file, no
     exceptions. Any file two streams both need goes on the shared list
     below and is serialized instead — built by one stream, consumed by
     the other after merge. -->
| Stream | Owns |
|---|---|
| A |  |
| B |  |

Shared files:
<!-- The collision list. Best case: empty. If long, stop and re-cut.
     Merge conflicts are cheap and loud. The expensive ones are SEMANTIC:
     two streams change the same contract in ways that both look right,
     merge clean, and fail together. File ownership is what prevents that;
     git cannot. -->

Review gate:
<!-- Who gates each stream, and the checklist applied. Each stream gates
     SEPARATELY before merge. -->

Merge order:
<!-- Decided BEFORE work starts. Dependency-holder merges first. -->

Proof:
<!-- The integration check run AFTER all streams land. Individual proofs
     passing does not prove the streams work together. -->