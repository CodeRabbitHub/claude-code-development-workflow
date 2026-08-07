# Review gate — <slice name>

Date:
Brief: <link>
Diff reviewed: <commit hash or branch diff>

A practical gate has five checks. All five pass or nothing merges.

## 1. The diff is small enough to review
<!-- MECHANICAL. Cap lives in .claude/config.json (diff_cap) and CI
     enforces it, so this is no longer a judgement call:
       git diff --numstat <base>...HEAD | awk '{a+=$1;r+=$2} END{print NR" files "a+r" lines"}'
     Over cap = FAIL. Split the slice and gate the pieces. "I read it all
     anyway" does not pass; the cap exists because attention degrades
     silently and you cannot feel it happening. -->

Files: ___ / cap ___    Lines: ___ / cap ___

## 2. The stated goal matches the actual change
<!-- The brief's Goal vs what the diff actually does. Extra "improvements"
     or missing behavior both fail this check. -->

## 3. The eval or test passed
<!-- The done-check RUN FRESH BY THE REVIEWER, output pasted verbatim.
     If this slice touched LLM behavior, the WHOLE eval set runs and the
     score must not regress against the last recorded score. Evals that
     are captured but never gated are an archive, not a check — the
     previous score goes in the box below so regression is visible. -->

Eval score: ___ (previous: ___ , from the eval's Score history table)
Model / prompt version this run: ___
<!-- A drop blocks the merge. If the model version differs from the
     baseline row, that is a model change, not necessarily a regression —
     say which it is rather than letting the number decide for you. -->
```
<paste>
```

## 4. The no-slop review found no unresolved issues
<!-- Reviewer subagent findings + how each was resolved. An open finding
     with no resolution fails this check. -->

## 5. The shipping proof is attached
<!-- Evidence it works in reality, not just in tests: the command output,
     screenshot, rendered page, or API response from actually running it. -->

## Rejected or changed
<!-- At least one thing, or explicit justification for zero. -->

## Rollback
<!-- Mandatory before merge. Answer both:
     1. The revert command for this slice (git revert <sha> is usually
        enough — say so explicitly if there is a migration, a schema
        change, or written external state that revert alone won't undo).
     2. Is this behind a flag? User-facing behavior merged without one
        means rollback = redeploy. Name the flag or justify its absence.
     A slice you cannot undo in one command at 3am is not shippable, no
     matter how green the tests are. -->

Revert: 
Flag: 

## Verdict
<!-- accept / accept-with-changes / reject — with all five checks green. -->