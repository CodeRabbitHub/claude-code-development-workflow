"""Shared notification + config layer for every hook.

Not a hook itself. Two jobs:
  1. load_config() - one place reads .claude/config.json, so no hook
     hardcodes a test command or a path list ever again.
  2. notify() - every event lands in .claude/.events.log; the levels
     listed in config push to your phone.

Push channels, both optional, both env-var driven so no secret is ever
committed:
  NTFY_TOPIC       zero-setup mobile push. Pick an unguessable topic,
                   install the ntfy app, subscribe to it.
  NOTIFY_WEBHOOK   generic JSON POST: Slack/Discord/Telegram relay.

Silence is the dangerous state, so notify() never raises and never blocks
the agent. A failed push is logged and swallowed.
"""
import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.request

ROOT = pathlib.Path.cwd()
CONFIG_PATH = ROOT / ".claude/config.json"
EVENTS = ROOT / ".claude/.events.log"
HEARTBEAT = ROOT / ".claude/.heartbeat"

DEFAULTS = {
    "test_command": ["python3", "-m", "unittest", "discover", "tests", "-v"],
    "test_timeout_seconds": 300,
    "tests_dir": "tests",
    "eval_command": None,
    "max_attempts": 3,
    "diff_cap": {"lines": 400, "files": 8},
    "protected": {
        "frozen_after_create": ["tests/"],
        "always": [".claude/hooks/", ".claude/settings.json",
                   ".claude/config.json", ".env"],
        "unlock_file": ".claude/.unlock",
    },
    "notify": {
        "enabled": True,
        "heartbeat_seconds": 900,
        "ntfy_topic_env": "NTFY_TOPIC",
        "ntfy_server": "https://ntfy.sh",
        "webhook_env": "NOTIFY_WEBHOOK",
        "levels_that_push": ["gate", "breaker", "blocked", "stopped", "dead"],
    },
}


def _merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for key, value in over.items():
        if key.startswith("_"):
            continue
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


def load_config() -> dict:
    """Config file is advisory for values, never for existence. A missing or
    corrupt config falls back to defaults rather than disabling enforcement."""
    try:
        return _merge(DEFAULTS, json.loads(CONFIG_PATH.read_text("utf-8")))
    except Exception:
        return dict(DEFAULTS)


def _post_json(url: str, payload: dict, timeout: int = 8) -> None:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    urllib.request.urlopen(request, timeout=timeout).read()


def _project_name() -> str:
    return ROOT.name


def notify(level: str, title: str, body: str = "", config: dict = None) -> None:
    """Record an event and push it if its level warrants waking you.

    level: gate | breaker | blocked | stopped | dead | info | merged
    """
    config = config or load_config()
    settings = config.get("notify", {})
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")

    try:
        EVENTS.parent.mkdir(parents=True, exist_ok=True)
        with EVENTS.open("a", encoding="utf-8") as handle:
            handle.write(f"[{stamp}] {level.upper()} {title}\n")
            for line in (body or "").splitlines():
                handle.write(f"    {line}\n")
    except Exception:
        pass

    if not settings.get("enabled", True):
        return
    if level not in settings.get("levels_that_push", []):
        return

    tagged = f"[{_project_name()}] {title}"
    trimmed = (body or "")[:1500]

    topic = os.environ.get(settings.get("ntfy_topic_env", "NTFY_TOPIC") or "")
    if topic:
        priority = {"dead": "urgent", "breaker": "high", "stopped": "high",
                    "gate": "default", "blocked": "default"}.get(level, "low")
        try:
            _post_json(
                f"{settings.get('ntfy_server', 'https://ntfy.sh')}/{topic}",
                {"topic": topic, "title": tagged, "message": trimmed or level,
                 "priority": priority, "tags": [level]},
            )
        except Exception as error:
            _log_push_failure("ntfy", error)

    webhook = os.environ.get(settings.get("webhook_env", "NOTIFY_WEBHOOK") or "")
    if webhook:
        try:
            _post_json(webhook, {"text": f"{tagged}\n{trimmed}",
                                 "level": level, "project": _project_name()})
        except Exception as error:
            _log_push_failure("webhook", error)


def _log_push_failure(channel: str, error: Exception) -> None:
    try:
        with EVENTS.open("a", encoding="utf-8") as handle:
            handle.write(f"    !! push via {channel} failed: {error}\n")
    except Exception:
        pass


def beat() -> None:
    """Mark the agent as alive. The watchdog reads this file; a stale
    heartbeat is how you find out the run died instead of finishing."""
    try:
        HEARTBEAT.parent.mkdir(parents=True, exist_ok=True)
        HEARTBEAT.write_text(str(int(time.time())), encoding="utf-8")
    except Exception:
        pass


def git(*args: str, timeout: int = 15) -> str:
    try:
        return subprocess.run(["git", *args], capture_output=True, text=True,
                              timeout=timeout).stdout
    except Exception:
        return ""


def read_hook_input() -> dict:
    try:
        return json.load(sys.stdin) or {}
    except Exception:
        return {}
