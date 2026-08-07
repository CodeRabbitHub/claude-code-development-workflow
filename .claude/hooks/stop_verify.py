"""Stop hook: the build loop, fail-CLOSED.

When the agent claims done, the suite runs. Failure bounces it back to
work, capped at max_attempts, then the circuit breaker fires and demands
a re-plan instead of a fourth try.

The previous version returned 0 - "you may stop" - whenever it could not
check: no tests dir, subprocess error, timeout. That is the wrong default
for a governor. Every one of those paths now exits 2. A governor that
cannot verify must not approve.

Also new: runs the eval suite when config.eval_command is set, so evals
are gating rather than archival; and pushes to your phone on breaker or
on any unverifiable stop, because an overnight run that stopped is only
useful if you find out.

Exit 2 = the agent may not stop; stderr tells it why.
State (gitignored): .claude/.stop_attempts, .claude/.replan_needed
"""
import os
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _notify import ROOT, beat, load_config, notify, read_hook_input  # noqa: E402

ATTEMPTS = ROOT / ".claude/.stop_attempts"
REPLAN = ROOT / ".claude/.replan_needed"


def run(command, timeout):
    """Always run with bytecode writing off.

    Found the hard way: two files written inside the same mtime second let
    Python reuse a stale .pyc, and a FAILING suite reported green. A
    verifier that can be fooled by a filesystem timestamp is not a
    verifier.
    """
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run(command, capture_output=True, text=True,
                          timeout=timeout, env=environment)


def tail(result, lines=30):
    text = (result.stderr or "") + "\n" + (result.stdout or "")
    return "\n".join(text.strip().splitlines()[-lines:])


def block(message, level, title, config):
    """Bounce the agent back - but count the bounce.

    An unverifiable stop must escalate like any other failure, or the agent
    deadlocks: it cannot stop (this hook says no) and it cannot repair the
    cause (guard_writes protects config.json and the hooks). After
    max_attempts we set the re-plan flag, page the human, and let the
    session end so they can act. Three bounces informs; infinite bounces
    just burns tokens until the quota dies at 4am.
    """
    if REPLAN.exists():
        return 0

    attempts = int(ATTEMPTS.read_text()) + 1 if ATTEMPTS.exists() else 1
    if attempts >= config["max_attempts"]:
        ATTEMPTS.unlink(missing_ok=True)
        REPLAN.touch()
        notify(level if level == "breaker" else "dead",
               f"HUMAN NEEDED: {title}", message[:800], config)
        print(message + "\n\nThis has now failed "
              f"{config['max_attempts']} times. Stop, report the above to the "
              "user, and wait - do not retry.", file=sys.stderr)
        return 2

    ATTEMPTS.write_text(str(attempts))
    notify(level, f"{title} ({attempts}/{config['max_attempts']})",
           message[:800], config)
    print(message, file=sys.stderr)
    return 2


def main() -> int:
    read_hook_input()
    beat()
    config = load_config()
    timeout = config["test_timeout_seconds"]

    tests_dir = ROOT / config["tests_dir"]
    if not tests_dir.is_dir():
        return block(
            f"CANNOT VERIFY: {config['tests_dir']}/ does not exist, so 'done' "
            "cannot be demonstrated. Nothing is done without pasted proof. "
            "Write the tests from the brief first (test-writer subagent), or "
            "ask the user to confirm this slice is genuinely test-exempt.",
            "stopped", "Stop blocked: no tests directory", config)

    try:
        result = run(config["test_command"], timeout)
    except subprocess.TimeoutExpired:
        return block(
            f"CANNOT VERIFY: the test command exceeded {timeout}s and was "
            "killed. A suite that cannot finish is not a passing suite. "
            "Report this to the user - do not claim done.",
            "stopped", "Stop blocked: test timeout", config)
    except FileNotFoundError:
        return block(
            f"CANNOT VERIFY: test command not found: {config['test_command']}. "
            "Fix test_command in .claude/config.json. Enforcement is broken "
            "until it runs - tell the user.",
            "stopped", "Stop blocked: test command missing", config)
    except Exception as error:
        return block(
            f"CANNOT VERIFY: the test command could not be run ({error}). "
            "Report this; do not claim done.",
            "stopped", "Stop blocked: test runner error", config)

    output = (result.stdout or "") + (result.stderr or "")
    passed = result.returncode == 0
    ran_nothing = "Ran 0 tests" in output or "NO TESTS RAN" in output

    if passed and ran_nothing:
        return block(
            "CANNOT VERIFY: the suite ran 0 tests, so a green result proves "
            "nothing. Write tests that encode the brief's done-check before "
            "claiming done.",
            "stopped", "Stop blocked: zero tests collected", config)

    if passed and config.get("eval_command"):
        try:
            evaluation = run(config["eval_command"], timeout)
            if evaluation.returncode != 0:
                passed = False
                result = evaluation
                output = (evaluation.stdout or "") + (evaluation.stderr or "")
        except Exception as error:
            return block(
                f"CANNOT VERIFY: eval suite failed to run ({error}). LLM "
                "behavior changed in this slice and the evals gate it.",
                "stopped", "Stop blocked: eval runner error", config)

    if passed:
        ATTEMPTS.unlink(missing_ok=True)
        REPLAN.unlink(missing_ok=True)
        notify("info", "Slice verified green", tail(result, 5), config)
        return 0

    return block(
        "Not done - the suite is failing. Fix the CODE, never the test.\n"
        "If you believe the test itself is wrong, that is a brief problem: "
        "say which assertion contradicts the brief's done-check and stop.\n"
        + tail(result),
        "breaker", "Circuit breaker: slice needs re-plan", config)


if __name__ == "__main__":
    sys.exit(main())
