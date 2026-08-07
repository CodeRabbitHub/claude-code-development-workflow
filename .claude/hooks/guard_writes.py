"""PreToolUse hook on Write|Edit|MultiEdit|NotebookEdit.

Closes the hole that Bash-only enforcement leaves open. Two classes of
protected path, from .claude/config.json:

  frozen_after_create (tests/)
      CREATING a new file is allowed - that is test-writer at step 4.
      EDITING or OVERWRITING an existing one is blocked - that is the
      builder bending the test to fit the code, which is the single
      failure mode this whole method exists to prevent. The test is the
      contract; the contract is frozen once written.

  always (.claude/hooks/, settings.json, config.json, .env)
      The governor may not edit itself. An agent that can rewrite
      stop_verify.py has no governor at all.

Escape hatch, deliberately manual and deliberately loud: the human runs
    touch .claude/.unlock            # unlock everything, one write
    echo tests/test_api.py > .claude/.unlock   # or scope it to a prefix
The hook consumes the unlock (deletes it) after one allowed write and
logs it to .claude/.events.log. A test amended this way must be named in
the slice log - that is what makes the amendment reviewable instead of
silent.

Exit 2 = block the tool call, stderr is fed back to the agent.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _notify import ROOT, load_config, notify, read_hook_input  # noqa: E402

EDIT_TOOLS = {"Edit", "MultiEdit", "NotebookEdit"}


def targets(data: dict) -> list:
    """Pull every path a write-ish tool call would touch."""
    tool_input = data.get("tool_input") or {}
    found = []
    for key in ("file_path", "path", "notebook_path", "filePath"):
        if tool_input.get(key):
            found.append(str(tool_input[key]))
    for entry in tool_input.get("edits") or []:
        if isinstance(entry, dict):
            for key in ("file_path", "path"):
                if entry.get(key):
                    found.append(str(entry[key]))
    return found


def relative(path: str) -> str:
    try:
        return pathlib.Path(path).resolve().relative_to(ROOT.resolve()).as_posix()
    except Exception:
        return pathlib.Path(path).as_posix()


def matches(rel: str, prefixes: list) -> bool:
    return any(rel == prefix.rstrip("/") or rel.startswith(prefix.rstrip("/") + "/")
               or rel == prefix for prefix in prefixes)


def unlock_covers(config: dict, rel: str) -> bool:
    unlock = ROOT / config["protected"].get("unlock_file", ".claude/.unlock")
    if not unlock.exists():
        return False
    try:
        scope = unlock.read_text("utf-8").strip()
    except Exception:
        scope = ""
    if scope and not (rel == scope or rel.startswith(scope.rstrip("/") + "/")):
        return False
    try:
        unlock.unlink()
    except Exception:
        pass
    notify("info", "Protected write unlocked", f"{rel} (unlock consumed)", config)
    return True


def main() -> int:
    data = read_hook_input()
    config = load_config()
    protected = config["protected"]
    tool = data.get("tool_name") or data.get("tool") or ""

    for raw in targets(data):
        rel = relative(raw)

        if matches(rel, protected.get("always", [])):
            reason = ("the agent's own enforcement machinery" if ".claude" in rel
                      else "a secrets file")
            if unlock_covers(config, rel):
                continue
            notify("blocked", "Write to protected path blocked", rel, config)
            print(
                f"BLOCKED by guard_writes: {rel} is {reason} and cannot be "
                "modified by an agent. If this change is genuinely needed, "
                "stop and ask the user to make it or to run "
                "`touch .claude/.unlock` for a single write.",
                file=sys.stderr,
            )
            return 2

        if matches(rel, protected.get("frozen_after_create", [])):
            exists = (ROOT / rel).exists()
            is_edit = tool in EDIT_TOOLS
            if not exists and not is_edit:
                continue  # new test file: this is step 4 doing its job
            if unlock_covers(config, rel):
                continue
            notify("blocked", "Frozen test edit blocked", rel, config)
            print(
                f"BLOCKED by guard_writes: {rel} is a frozen test. Tests are "
                "written from the brief BEFORE the code and are the contract "
                "the code must satisfy - editing one to make it pass inverts "
                "the method.\n"
                "If the test is genuinely wrong, that is a brief problem, not "
                "a code problem: stop, say which assertion contradicts the "
                "brief's done-check, and ask the user to amend the brief. "
                "They can allow one write with `touch .claude/.unlock`.",
                file=sys.stderr,
            )
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
