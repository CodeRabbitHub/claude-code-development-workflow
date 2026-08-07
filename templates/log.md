# Slice log — <slice name>

Date:
Brief: <link to plans/briefs/...>

## The plan you approved
<!-- The approach that got the yes at Gate 1, in 2-3 lines. -->

## The diff you accepted
<!-- Commit hash + one-line description. Hook pre-fills mechanics in
     plans/logs/_auto-capture.md — reference it. -->

## The done-check output
<!-- Pasted verbatim. Not "tests passed" — the actual output. -->

## One thing you rejected or changed
<!-- Mandatory. If nothing, justify why this wasn't a rubber-stamp.
     If this repeats a pattern: promote it to CLAUDE.md / templates/no-slop.md. -->

## Cost
<!-- Wall-clock, tokens if you have them, and attempts used (1-3 from the
     breaker). Once the loop runs unattended this is the main governor you
     have left: a slice that took 3 attempts and 40 minutes is telling you
     the brief was ambiguous, not that the model was weak. Trends here are
     what justify promoting something up the ratchet. -->
Wall-clock:      Attempts: __/3      Tokens:

## Frozen-test amendments
<!-- Every .claude/.unlock consumed this slice, and why. Empty is the
     normal case. Anything here means a test written from the brief was
     changed to fit the code — the exact move the method exists to
     prevent — so it must be justified in writing or reverted. -->

## The next smallest slice
<!-- One sentence, written while context is hot. Feeds the next brief. -->