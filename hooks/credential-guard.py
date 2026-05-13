#!/usr/bin/env python3
"""credential-guard — PreToolUse hook for the redis-companion plugin.

Reads a Claude Code hook payload from stdin, scans Write/Edit/MultiEdit content
for literal Redis credentials (env-var assignments, URIs with embedded auth,
redis-cli auth flags), and blocks the write if a real credential is found.

Recognized placeholders (e.g., <replace_password_here>, ${VAR}, $REDIS_PASS) are
allowed through — they're how the agent's own output is structured.
"""
import json
import re
import sys

PATTERNS = [
    (
        re.compile(
            r"(?im)^\s*(?:export\s+)?REDIS_(?:PASS|PASSWORD|PWD|AUTH)\s*=\s*[\"']?([^\s\"'`#\n]+)"
        ),
        "REDIS_PASS / REDIS_PASSWORD / REDIS_PWD / REDIS_AUTH env-var assignment with literal value",
    ),
    (
        re.compile(r"rediss?://[^/\s\"'`@:]+:([^/\s\"'`@:]+)@"),
        "Redis URI with embedded user:password@host",
    ),
    (
        re.compile(
            r"redis-cli[^\n]*?(?:--pass(?:word)?|(?:^|\s)-a)\s+[\"']?([^\s\"'`#\n]+)"
        ),
        "redis-cli --pass / --password / -a with literal value",
    ),
]

PLACEHOLDERS = {
    "replace_password_here",
    "replace_with_password",
    "replace_password",
    "your_password",
    "your-password",
    "your_password_here",
    "changeme",
    "change_me",
    "change-me",
    "password",
    "secret",
    "xxx",
    "xxxx",
    "xxxxx",
    "placeholder",
    "none",
    "null",
    "redacted",
    "example",
}


def is_placeholder(value: str) -> bool:
    """Heuristic: is this value an obvious placeholder, not a real credential?"""
    v = value.strip().strip("\"'").lower()
    if not v:
        return True
    if v in PLACEHOLDERS:
        return True
    if v.startswith("<") and v.endswith(">"):
        return True
    if v.startswith("${") and v.endswith("}"):
        return True
    if re.fullmatch(r"\$[a-z_][a-z0-9_]*", v):
        return True
    return False


def line_of(content: str, idx: int) -> str:
    start = content.rfind("\n", 0, idx) + 1
    end = content.find("\n", idx)
    return content[start : end if end != -1 else len(content)].strip()


def scan(content: str) -> list[str]:
    findings = []
    for pattern, label in PATTERNS:
        for match in pattern.finditer(content):
            value = match.group(1) if match.lastindex else match.group(0)
            if is_placeholder(value):
                continue
            line = line_of(content, match.start())
            findings.append(f"  - {label}\n      line: {line}")
    return findings


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # Fail open on malformed input — better than blocking everything.

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {})

    contents = []
    if tool_name == "Write":
        contents.append(tool_input.get("content", ""))
    elif tool_name == "Edit":
        contents.append(tool_input.get("new_string", ""))
    elif tool_name == "MultiEdit":
        for edit in tool_input.get("edits", []):
            contents.append(edit.get("new_string", ""))
    else:
        return 0

    findings = []
    for content in contents:
        if content:
            findings.extend(scan(content))

    if not findings:
        return 0

    file_path = tool_input.get("file_path", "(unknown path)")
    sys.stderr.write(
        f"\ncredential-guard: refused to write {file_path}\n\n"
        f"Detected literal Redis credential(s) in the content:\n\n"
        + "\n".join(findings)
        + "\n\nBest practice: load Redis credentials from environment variables "
        "(REDIS_PASS, etc.) at runtime, or use a secret manager. Don't commit "
        "literal credentials.\n\n"
        "If this is intentional (e.g., a test fixture or local-dev override), "
        "use a recognized placeholder — <replace_password_here>, ${REDIS_PASS}, $REDIS_PASS, "
        "etc. — or temporarily disable the redis-companion plugin.\n"
    )
    return 2  # Non-zero exit + stderr → Claude Code blocks the tool call.


if __name__ == "__main__":
    sys.exit(main())
