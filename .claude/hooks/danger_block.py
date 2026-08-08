"""PreToolUse hook on Bash|PowerShell: blocks destructive shell commands.

Honest scope note, because the previous version's name oversold it: this
is a speed bump, not a boundary. A determined or obfuscated command will
get through - the real boundary is running the agent in a container or a
non-privileged working copy. What this catches is the far more common
case: a competent agent doing something drastic by accident.

The v1 patterns missed 12 of 18 destructive commands under test, most
embarrassingly `rm -r -f` (separated flags). Fixes here: flags are
normalized before matching, each command in a pipeline/chain is checked
separately, and the pattern list covers deletion, history rewriting,
permissions, credential exfiltration, and pipe-to-shell.

v3 closes the hole the audit found: guard_writes freezes tests and the
governor against the Write/Edit TOOLS, but the shell could still do the
same damage - `sed -i` a frozen test, `tee` over config.json, `rm` a test
and recreate it weakened, or `touch .claude/.unlock` to grant itself the
human-only escape hatch. Protected-path prefixes are now read from
.claude/config.json (same source guard_writes uses - one list, two
enforcers) and common shell write verbs against them are blocked. Still a
speed bump against a determined adversary; a container is the boundary.
"""
import re
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _notify import beat, load_config, notify, read_hook_input  # noqa: E402

PATTERNS = [
    # --- deletion ---
    (r"\brm\b(?=(?:\s+-\S+)*\s+-\S*r)(?=(?:\s+-\S+)*\s+-\S*f)", "recursive force delete"),
    (r"\brm\b.*--recursive.*--force|\brm\b.*--force.*--recursive", "recursive force delete"),
    (r"\brm\b\s+(-\S+\s+)*/(\s|$)", "delete targeting /"),
    (r"Remove-Item\b(?=.*-Recurse)(?=.*-Force)", "recursive force delete"),
    (r"\bfind\b.*\s-delete\b", "find -delete removes files in bulk"),
    (r"\bfind\b.*-exec\s+rm\b", "find -exec rm removes files in bulk"),
    (r"\b(shred|truncate)\b", "destructive file overwrite"),
    (r"\bdd\b.*\bof=/dev/", "dd writing to a device"),
    (r">\s*/dev/(sd|nvme|disk)", "writing directly to a disk device"),
    (r"\bmkfs(\.\w+)?\b", "filesystem format"),

    # --- git history and work loss ---
    (r"git\s+push\s+(?!.*--force-with-lease).*(--force|-f)\b", "force push"),
    (r"git\s+reset\s+--hard", "hard reset discards uncommitted work"),
    (r"git\s+clean\s+-\w*f", "git clean deletes untracked files"),
    (r"git\s+checkout\s+(--\s+)?\.(\s|$)", "checkout . discards all local changes"),
    (r"git\s+restore\s+(?!.*--staged).*\.(\s|$)", "restore . discards all local changes"),
    (r"git\s+branch\s+-\w*D\b", "force branch delete"),
    (r"git\s+stash\s+(clear|drop)\b", "discards stashed work"),
    (r"git\s+filter-(branch|repo)\b", "rewrites history"),
    (r"git\s+commit\b.*--no-verify|git\s+push\b.*--no-verify", "bypassing hooks"),
    (r"git\s+update-ref\s+-d\b", "deleting a ref"),

    # --- secrets and exfiltration ---
    (r"(>|>>)\s*\.?env\b", "writing to .env"),
    (r"\b(cat|less|more|type)\b[^|;&]*\.env\b[^|;&]*\|", "piping .env somewhere"),
    (r"\bcurl\b[^|;&]*(-d|--data|-F)[^|;&]*\.env\b", "posting .env to the network"),
    (r"\b(id_rsa|id_ed25519|\.aws/credentials|\.ssh/config)\b", "touching credentials"),

    # --- arbitrary remote execution ---
    (r"\b(curl|wget)\b[^|]*\|\s*(sudo\s+)?(ba|z|k|s)?sh\b", "pipe-to-shell from the network"),
    (r"\b(base64|xxd)\b[^|]*\|\s*(ba|z|k|s)?sh\b", "executing decoded payload"),
    (r"\beval\b.*\$\(", "eval of a constructed command"),
    (r"\biwr\b.*\|\s*iex\b|\bInvoke-Expression\b", "PowerShell remote execution"),

    # --- permissions and irreversible publishing ---
    (r"\bchmod\b\s+(-\w+\s+)*(777|a\+rwx)", "world-writable permissions"),
    (r"\bchown\b\s+-\w*R\w*\s+.*\s/(\s|$)", "recursive chown of /"),
    (r"\b(npm|yarn|pnpm)\s+publish\b", "publishing a package"),
    (r"\bpypi\b.*upload|\btwine\s+upload\b", "publishing a package"),
    (r"\bdocker\s+system\s+prune\b.*-\w*a", "prunes all docker state"),
    (r"\b(kubectl|helm)\b.*\bdelete\b.*(--all|-A)\b", "cluster-wide delete"),
    (r"\bterraform\s+(destroy|apply)\b.*-auto-approve", "unreviewed infra change"),
    (r"\b(shutdown|reboot|halt)\b", "host power state"),
]


# A path prefix must not match mid-word: "tests" must hit `tests/x.py` and
# `./tests` and `/abs/path/tests/x.py`, but never "mytests" or "tests_old".
def _anchor(prefix: str) -> str:
    escaped = re.escape(prefix.rstrip("/"))
    return rf"(?<![\w.-]){escaped}(/|\s|$)"


def protected_bash_patterns(config: dict) -> list:
    """Shell-write patterns for every protected path, built from config.

    Same single source of truth guard_writes reads. Covers the common write
    verbs; anything exotic (python -c, ed, patch) is out of scope for a
    speed bump. `cp/mv` also trigger when a protected path is the SOURCE -
    that is a deliberate false positive: renaming a frozen test out of the
    way is the delete-and-recreate bypass wearing a different hat.
    """
    protected = config.get("protected", {})
    unlock = protected.get("unlock_file", ".claude/.unlock")
    prefixes = (list(protected.get("always", []))
                + list(protected.get("frozen_after_create", []))
                + [unlock])
    patterns = []
    for prefix in prefixes:
        target = _anchor(prefix)
        why = f"shell write to protected path {prefix}"
        patterns += [
            (rf"(^|[^\w./-])(sed|perl)\s+(-\S+\s+)*-\S*i\S*\s+[^|;&]*{target}",
             f"in-place edit: {why}"),
            (rf"\btee\b[^|;&]*\s{target}", f"tee: {why}"),
            (rf"\d?>>?\s*\S*?{target}", f"redirect: {why}"),
            (rf"\b(mv|cp|rsync|install|ln)\b[^|;&]*\s{target}",
             f"copy/move/link: {why}"),
            (rf"\brm\b[^|;&]*\s{target}",
             f"delete (enables recreate-weakened): {why}"),
            (rf"\bgit\s+(mv|rm|checkout|restore)\b[^|;&]*\s{target}",
             f"git rewrite of: {why}"),
            (rf"\b(truncate|shred)\b[^|;&]*\s{target}", f"truncate: {why}"),
        ]
    patterns.append((
        rf"\btouch\b[^|;&]*\s(\S*/)?{re.escape(unlock)}(\s|$)",
        "agent creating its own unlock file - that consent is the human's"))
    return patterns


SPLIT = re.compile(r"\|\||&&|[;\n|]")


def normalize(segment: str) -> str:
    """Collapse whitespace so `rm  -r   -f` and `rm -r -f` look alike."""
    return re.sub(r"\s+", " ", segment).strip()


def main() -> int:
    data = read_hook_input()
    beat()
    command = (data.get("tool_input") or {}).get("command", "") or ""
    patterns = PATTERNS + protected_bash_patterns(load_config())

    for segment in [command] + SPLIT.split(command):
        candidate = normalize(segment)
        if not candidate:
            continue
        for pattern, why in patterns:
            if re.search(pattern, candidate, re.IGNORECASE):
                notify("blocked", "Dangerous command blocked", f"{why}: {candidate[:200]}")
                print(
                    f"BLOCKED by danger_block: {why}.\n"
                    f"  {candidate[:200]}\n"
                    "Do not work around this hook. If the command is genuinely "
                    "needed, stop and ask the user to run it or approve it "
                    "explicitly.",
                    file=sys.stderr,
                )
                return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
