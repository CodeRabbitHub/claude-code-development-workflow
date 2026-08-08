# Ratchet

**A disciplined harness for shipping software with Claude Code — contracts
before code, evidence over claims, and enforcement that doesn't depend on
anyone remembering the rules.**

Named for the mechanism at its centre: every correction made twice gets
promoted a notch — chat → rule → hook → skill → subagent → eval — and
nothing ever slips back down. The loop doesn't just ship projects. Each one
leaves the system stronger than it found it.

---

## The problem

Agents write code that looks finished. Tests pass because the agent adjusted
the test. "Done" gets claimed for work nobody ran. A rule you agreed on
three sessions ago quietly stops being followed, and you find out at merge
time — or later.

None of that is fixed by a better prompt, because the failure isn't
knowledge, it's the absence of a forcing function. Every workflow that lives
in a document decays, and it decays fastest under deadline, which is exactly
when you needed it.

Ratchet moves the rules out of the document and into hooks, subagents, and
CI. Not advice the agent may follow — machinery it cannot route around.

## How it works

Work happens in **slices**. One slice, one branch, one session:

```
brief → plan ⟨GATE 1⟩ → tests from the brief → build ⟲ → review
      → ⟨GATE 2⟩ → merge → log → handoff
```

Four properties make this different from a prompt library:

- **Tests are frozen.** They're written from the brief before any code
  exists, and paired hooks stop the builder from changing them to make them
  pass — whether through the edit tools *or* through the shell (`sed -i`,
  `tee`, redirects, delete-and-recreate). That single move is what
  separates code that works from code that looks like it works.
- **The agent can't grade its own homework.** It can't claim "done" while
  tests fail, *or* while they can't be run at all — a verifier that can't
  verify must not approve. Hooks block it from editing its own enforcement
  machinery — hooks, config, subagent definitions, CI workflow — by tool
  or by shell. CI re-checks everything on a clean machine and
  regression-tests the hooks themselves, including every known bypass.
  Honest scope: hooks are a strong speed bump, not a sandbox — for a truly
  adversarial or fully unattended agent, the hard boundary is a container
  or a non-privileged working copy.
- **It runs unattended.** Gates push to your phone, a queue feeds the next
  slice automatically, and a deadman switch pages you when the agent goes
  *silent* — the one failure nothing else can report, because a dead agent
  and a working agent produce identical output: nothing.
- **It compounds.** The second occurrence of any problem gets automated
  rather than repeated. Corrections become rules, rules become hooks, hooks
  become skills. Nothing that cost you once is allowed to cost you twice.

Built for Claude Code. The method is harness-agnostic — only `.claude/` is
Claude-specific.

Full method and reasoning: **[RUNBOOK.md](RUNBOOK.md)**.
One-page cheat sheet: **[WORKFLOW.md](WORKFLOW.md)**.

## Quick start

```bash
git clone https://github.com/CodeRabbitHub/claude-code-development-workflow my-project
cd my-project && rm -rf .git && git init
```

1. Fill **PLAN.md** (goal + milestones) and **ARCHITECT.md** (irreversible
   decisions only — everything else stays undecided until a slice forces it).
2. Fill the "What this project is" and Commands sections of **CLAUDE.md**.
3. Set `test_command` in **`.claude/config.json`** for your stack. Hooks and
   CI both read it; `stop_verify` fails closed, so a wrong command blocks
   every "done" until it's fixed.
4. Put your GitHub handle in **`.github/CODEOWNERS`**, then turn the human
   gate into a GitHub rule (~2 min): repo Settings → Rules → Rulesets →
   New branch ruleset targeting `main` → enable **Require a pull request
   before merging** (1 approval + *Require review from Code Owners* +
   *Dismiss stale approvals*), **Require status checks to pass** (add
   `gate`), and **Block force pushes**. Without this, "reviewed" is a file
   the agent can write; with it, "reviewed" is an approval only you can
   click — CI fails a real project that skips this step.
5. Commit, open Claude Code, and run **`/brief`** to write the first slice.
6. Follow the loop in [WORKFLOW.md](WORKFLOW.md).

For unattended runs, also:

```bash
export NTFY_TOPIC=<something-unguessable>   # install the ntfy app, subscribe
python3 .claude/watchdog.py                 # second terminal: the deadman switch
```

## What's wired up out of the box

**Skills** — slash commands that package a procedure:

| Command | What it does |
|---|---|
| `/brief` | Interviews you into a slice contract; refuses vague done-checks, empty out-of-scope, and unstated assumptions |
| `/gate` | Runs the reviewer subagent, shows diff + fresh proof, records your verdict |
| `/capture` | Writes the slice log; mechanics pre-filled, judgment asked |
| `/handoff` | Rewrites HANDOFF.md with verified state + the next brief |
| `/next` | Pops the next brief from `plans/backlog/` so a run continues unattended |

**Subagents** — separate instances with restricted tools:

| Agent | Why it's restricted |
|---|---|
| test-writer | Never reads the implementation plan, so tests are independent of the builder's blind spots |
| no-slop-reviewer | Read, Grep, Glob only — no Bash, no Write, no Edit. A reviewer that physically cannot change code or run commands is mechanically trustworthy |

**Hooks** — the enforcement layer, invoked automatically:

| Hook | What it does |
|---|---|
| `danger_block` | Blocks destructive shell commands: recursive deletes (including `rm -r -f` with separated flags), force-push, history rewriting, pipe-to-shell, credential reads |
| `guard_writes` | Freezes existing tests; blocks the agent from editing its own hooks, config, CI workflow, or `.env` |
| `stop_verify` | Fails **closed** — can't claim "done" while tests fail, or while they can't be run at all. 3 strikes → forced re-plan |
| `capture_commit` | Heartbeat for the watchdog; appends each commit's stat and diff size |
| `notify_gate` | Pushes gates to your phone so you can approve without sitting at the machine |
| `session_start` | Warns immediately if the machinery is broken or a breaker flag is still set |

**Outside the harness** — because everything above can be bypassed by
working in a plain terminal:

| Piece | What it does |
|---|---|
| `.claude/watchdog.py` | Deadman switch — pages you on silence, which no hook can report |
| `.github/workflows/gate.yml` | Re-runs the gate on a clean machine and asserts the hooks still block what they claim. Holds **no API keys** by design |
| `.github/CODEOWNERS` + branch ruleset | The human gate GitHub enforces: nothing merges to `main` without an approval from a listed human. CI checks the ruleset exists and fails a project running without it |

## Adapting it

- **Different test runner?** Set `test_command` in `.claude/config.json`.
  That's the only place it lives.
- **Windows?** Hooks are invoked with `python3` in `.claude/settings.json`.
  On macOS and modern Linux this is the only safe choice (`python` either
  doesn't exist or points at Python 2, and command-not-found returns 127,
  making every hook silently no-op). On **Windows** the opposite is true:
  `python3` doesn't exist — the binary is `python` (and it is always
  Python 3). Run `python .claude/hooks/session_start.py` to verify, then
  replace every `"python3 .claude/hooks/` with `"python .claude/hooks/`
  in `.claude/settings.json`. The CI runs on `ubuntu-latest` and still
  uses `python3`; this change is local only.
- **Adding an eval suite?** Set `eval_command` and it becomes gating: both
  `stop_verify` and CI run it, and a regression blocks the merge. Keep it off
  push-triggered CI — evals cost money and are non-deterministic, so they
  belong on manual dispatch or a nightly schedule. Unit tests must never make
  a live model call, which is why CI needs no API keys.
- **New slop pattern caught twice?** Add a line to `templates/no-slop.md` —
  the reviewer agent reads it as its rubric, so every future review improves.
- **New standing rule?** One line in CLAUDE.md. Still getting violated?
  Promote it to a hook. That's the ratchet doing its job.
- Templates are the single source of truth: skills and agents *reference*
  them, never copy them. Edit the template and everything downstream follows.

## Layout

```
CLAUDE.md  PLAN.md  ARCHITECT.md  HANDOFF.md   the project's head
RUNBOOK.md  WORKFLOW.md                        the method
templates/                                     blank forms (source of truth)
  brief · log · review · re-plan · design-note
  no-slop · eval · parallel-plan · handoff
plans/briefs/  plans/logs/                     contracts and evidence
plans/backlog/                                 queued briefs for /next
artifacts/reviews/  artifacts/design/          gate records, visual contracts
evals/  tests/                                 quality checks
.claude/skills|agents|hooks + settings.json    the machinery
.claude/config.json                            single source: test cmd, caps, paths
.claude/watchdog.py                            deadman switch (run separately)
.github/workflows/gate.yml                     CI that doesn't trust the agent
```

## Status

The machinery is tested — hooks are verified in both directions (they block
what they should and allow what they shouldn't block), `stop_verify` is
verified closed on every unverifiable path, and CI regression-tests the hooks
on every push.

The loop itself has not yet run a real project end to end. Treat it as a
solid v1 rather than a battle-tested one, and expect the first slice to find
something.

## License

MIT — see [LICENSE](LICENSE).