# Design note — <surface name>

Date:
Slice: <link to brief>
Surface: <what the user sees/touches — CLI output, page, endpoint, report>

## Who uses this and what are they trying to do
<!-- One sentence of user intent. Design starts here, not at the widget. -->

## The decision
<!-- What the surface does and looks like. If a design tool (Stitch, Figma,
     v0) produced it, commit the export/screenshot to artifacts/design/ and
     link it here — it becomes the visual contract Gate 2 checks against. -->

## Empty, loading, and error states
<!-- Mandatory, because this is where the slop lives. The happy path gets
     designed by default; these get improvised at 2am by whoever is
     implementing. Answer all three:
       EMPTY   — first run, no data yet. What does the user see, and what
                 is the one action that gets them out of it?
       LOADING — what is on screen while waiting, and at what point does
                 slow become broken?
       ERROR   — what failed, in the user's words, and what can they do
                 about it. "Something went wrong" is a non-answer. -->

## Rejected alternative
<!-- The one serious alternative and why it lost. -->

## Why
<!-- 2-3 lines. Boring and standard beats clever. If this conflicts with
     ARCHITECT.md, the architecture wins unless explicitly amended. -->

## Open design debts
<!-- Shortcuts taken on purpose, revisit only if the surface earns it. -->
