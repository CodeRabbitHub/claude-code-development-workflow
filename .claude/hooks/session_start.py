"""SessionStart hook: check the machinery is actually alive, then beat.

Guards against the failure this kit already suffered once: hooks that
silently do nothing. If enforcement is broken, the session should say so
in its first breath rather than after a night of ungoverned work.

Also pops the next brief from plans/backlog/ into view so a fresh session
knows what it is picking up.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _notify import ROOT, beat, load_config, notify  # noqa: E402

REQUIRED = ["danger_block.py", "guard_writes.py", "stop_verify.py",
            "capture_commit.py", "_notify.py"]


def main() -> int:
    beat()
    config = load_config()
    problems = []

    hooks_dir = ROOT / ".claude/hooks"
    for name in REQUIRED:
        if not (hooks_dir / name).exists():
            problems.append(f"missing hook: {name}")

    if not (ROOT / config["tests_dir"]).is_dir():
        problems.append(f"no {config['tests_dir']}/ directory - stop_verify will block 'done'")

    if (ROOT / ".claude/.replan_needed").exists():
        problems.append("BREAKER STATE ACTIVE: a previous slice failed 3x and "
                        "needs a re-plan before new work starts")

    backlog = sorted((ROOT / "plans/backlog").glob("*.md")) if (ROOT / "plans/backlog").is_dir() else []
    queued = [path.name for path in backlog if not path.name.startswith("_")]

    if problems:
        notify("stopped", "Session started with broken machinery",
               "\n".join(problems), config)
        print("MACHINERY CHECK FAILED:\n  " + "\n  ".join(problems), file=sys.stderr)
        print("Tell the user before doing any work.", file=sys.stderr)

    if queued:
        print(f"Backlog: {len(queued)} brief(s) queued. Next: {queued[0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
