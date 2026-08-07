"""The deadman switch. Run this in a second terminal during any unattended run:

    NTFY_TOPIC=your-secret-topic python3 .claude/watchdog.py

Why it exists: silence is the most dangerous state an unattended agent can
be in. An agent that died at 01:40 - expired credentials, exhausted quota,
rate limit, crashed harness, closed laptop lid - produces exactly the same
thing as an agent working hard: nothing. Every other hook here reports
events; only this one reports the ABSENCE of events.

It watches .claude/.heartbeat (touched by hooks on every tool call). If the
heartbeat goes stale for longer than 2x heartbeat_seconds, it pages you
once with the last known activity, then goes quiet until the agent revives.

It also tails .claude/.events.log so a gate or breaker that fired while
your phone was off still reaches you, and prints a morning digest on exit.
"""
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent / "hooks"))
from _notify import EVENTS, HEARTBEAT, ROOT, load_config, notify  # noqa: E402

REPLAN = ROOT / ".claude/.replan_needed"


def last_activity() -> str:
    try:
        lines = [line for line in EVENTS.read_text("utf-8").splitlines() if line.startswith("[")]
        return lines[-1] if lines else "no events recorded"
    except Exception:
        return "no event log yet"


def digest() -> str:
    try:
        lines = [line for line in EVENTS.read_text("utf-8").splitlines() if line.startswith("[")]
    except Exception:
        return "no events"
    counts = {}
    for line in lines:
        parts = line.split("] ", 1)
        if len(parts) == 2:
            level = parts[1].split(" ", 1)[0]
            counts[level] = counts.get(level, 0) + 1
    return " · ".join(f"{level} {count}" for level, count in sorted(counts.items()))


def main() -> int:
    config = load_config()
    interval = config["notify"]["heartbeat_seconds"]
    grace = interval * 2

    print(f"watchdog: watching {ROOT.name}")
    print(f"  heartbeat window {interval}s, pages after {grace}s of silence")
    print(f"  push configured: ntfy={'yes' if __import__('os').environ.get('NTFY_TOPIC') else 'NO'}"
          f" webhook={'yes' if __import__('os').environ.get('NOTIFY_WEBHOOK') else 'NO'}")
    print("  ctrl-c for the digest\n")

    notify("info", "Watchdog started", f"grace {grace}s", config)
    paged_dead = False
    paged_replan = False

    try:
        while True:
            time.sleep(min(60, max(5, interval // 4)))
            now = time.time()

            # The agent stopped and asked for a human. Page once.
            if REPLAN.exists() and not paged_replan:
                notify("gate", "Agent is waiting for you",
                       "Circuit breaker fired - the slice needs a re-plan.\n"
                       + last_activity(), config)
                paged_replan = True
            elif not REPLAN.exists():
                paged_replan = False

            if not HEARTBEAT.exists():
                continue

            try:
                beat_at = float(HEARTBEAT.read_text("utf-8").strip())
            except Exception:
                continue

            silent_for = now - beat_at
            if silent_for > grace and not paged_dead:
                notify("dead", "Agent has gone silent",
                       f"No activity for {int(silent_for // 60)} min.\n"
                       f"Last event: {last_activity()}\n"
                       "Likely: expired auth, quota exhausted, rate limit, or "
                       "a crashed harness. It is NOT waiting at a gate.", config)
                paged_dead = True
                print(f"[{time.strftime('%H:%M:%S')}] PAGED: silent {int(silent_for)}s")
            elif silent_for <= grace and paged_dead:
                notify("info", "Agent revived", "", config)
                paged_dead = False
                print(f"[{time.strftime('%H:%M:%S')}] revived")

    except KeyboardInterrupt:
        print(f"\n--- digest ---\n{digest()}\nlast: {last_activity()}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
