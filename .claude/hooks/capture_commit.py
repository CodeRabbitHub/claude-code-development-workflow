"""PostToolUse hook: heartbeat on every command, plus commit capture.

Two jobs now:
  1. beat() on EVERY bash call - this is the pulse the watchdog reads.
     Doing it here rather than in a dedicated hook means any tool activity
     counts as alive, which is what we actually want to measure.
  2. After a real git commit, append hash + stat to the auto-capture log so
     /capture pre-fills mechanically, and record cost signals for the log.

v1 matched the substring "git commit", so `echo "run git commit"` produced
a phantom entry. Now the command is parsed properly and the commit is
confirmed against git itself.

Never blocks anything.
"""
import datetime
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _notify import beat, git, load_config, notify, read_hook_input  # noqa: E402

COMMIT = re.compile(r"(^|[;&|]\s*)git\s+(-\S+\s+)*commit\b")


def main() -> int:
    data = read_hook_input()
    beat()

    command = (data.get("tool_input") or {}).get("command", "") or ""
    if not COMMIT.search(command):
        return 0

    head = git("log", "-1", "--format=%H|%ct|%s")
    if not head.strip():
        return 0
    sha, timestamp, subject = (head.strip().split("|", 2) + ["", ""])[:3]

    marker = pathlib.Path(".claude/.last_capture")
    if marker.exists() and marker.read_text("utf-8").strip() == sha:
        return 0  # same commit already captured; no phantom entries
    marker.write_text(sha, encoding="utf-8")

    stat = git("log", "-1", "--stat", "--format=")
    numstat = git("diff", "--numstat", "HEAD~1", "HEAD")
    added = removed = files = 0
    for line in numstat.splitlines():
        parts = line.split("\t")
        if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit():
            added += int(parts[0])
            removed += int(parts[1])
            files += 1

    config = load_config()
    cap = config["diff_cap"]
    over = added + removed > cap["lines"] or files > cap["files"]

    log_dir = pathlib.Path("plans/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with (log_dir / "_auto-capture.md").open("a", encoding="utf-8") as handle:
        handle.write(f"\n## {stamp} — {sha[:8]} — {subject}\n")
        handle.write(f"Size: {files} files, +{added}/-{removed} lines "
                     f"(cap: {cap['files']} files / {cap['lines']} lines)"
                     f"{'  ** OVER CAP **' if over else ''}\n")
        handle.write(f"```\n{stat}```\n")

    if over:
        notify("info", "Commit over diff cap",
               f"{files} files, {added + removed} lines — Gate 2 check 1 will "
               "fail this. Consider splitting the slice.", config)
    return 0


if __name__ == "__main__":
    sys.exit(main())
