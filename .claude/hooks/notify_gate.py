"""Notification hook: the agent needs you. Push it to your phone.

This is the hook that makes unattended running actually work. Without it a
gate reached at 03:00 means the machine idles until you wake up; with it
you approve from bed and the run continues.

Notification payloads carry the harness's message (permission request,
idle prompt). We enrich it with the one thing you need to triage from a
phone: which slice, how big the diff is, and whether tests are green.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _notify import ROOT, beat, git, load_config, notify, read_hook_input  # noqa: E402


def context() -> str:
    branch = git("rev-parse", "--abbrev-ref", "HEAD").strip() or "?"
    numstat = git("diff", "--numstat", "HEAD")
    added = removed = files = 0
    for line in numstat.splitlines():
        parts = line.split("\t")
        if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit():
            added, removed, files = added + int(parts[0]), removed + int(parts[1]), files + 1

    briefs = sorted((ROOT / "plans/briefs").glob("*.md")) if (ROOT / "plans/briefs").is_dir() else []
    brief = briefs[-1].name if briefs else "no brief yet"
    replan = " | BREAKER FIRED" if (ROOT / ".claude/.replan_needed").exists() else ""
    return f"branch {branch} | {brief}\n{files} files, +{added}/-{removed}{replan}"


def main() -> int:
    data = read_hook_input()
    beat()
    message = data.get("message") or data.get("notification") or "Agent needs input"
    notify("gate", str(message)[:120], context(), load_config())
    return 0


if __name__ == "__main__":
    sys.exit(main())
