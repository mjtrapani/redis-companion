#!/usr/bin/env python3
"""
Build a verified command-category map from upstream redis/redis command JSONs.

Source of truth: src/commands/*.json from a tagged Redis release.

Each command's category membership is derived from:
- acl_categories (explicit, e.g., "STRING" -> @string)
- command_flags (READONLY -> @read, WRITE -> @write, ADMIN -> @admin,
                 BLOCKING -> @blocking, FAST -> @fast)

Subcommand handling:
- Filename `config-get.json` containing JSON key "GET" -> "CONFIG GET"
- Filename `client-no-evict.json` containing JSON key "NO-EVICT" -> "CLIENT NO-EVICT"
- Filename `set.json` containing JSON key "SET" -> "SET"
"""

import json
import os
import sys
from collections import defaultdict
from glob import glob


FLAG_TO_CATEGORY = {
    "READONLY": "@read",
    "WRITE": "@write",
    "ADMIN": "@admin",
    "BLOCKING": "@blocking",
    "FAST": "@fast",
    "PUBSUB": "@pubsub",
}


def acl_cat_to_category(cat):
    return "@" + cat.lower()


def full_command_name(filename, json_key):
    """Compose the full Redis command name from filename + JSON key.

    Heuristic: if the filename basename (uppercased) matches the JSON key,
    it's a top-level command with a possibly-hyphenated name. Otherwise,
    the filename's first hyphen-segment is the parent and the JSON key is
    the subcommand.

    Examples:
        ('set.json', 'SET')              -> 'SET'              (top-level)
        ('restore-asking.json', 'RESTORE-ASKING') -> 'RESTORE-ASKING'  (top-level, hyphenated)
        ('config-get.json', 'GET')       -> 'CONFIG GET'       (subcommand)
        ('client-no-evict.json', 'NO-EVICT') -> 'CLIENT NO-EVICT'  (subcommand)
        ('acl-getuser.json', 'GETUSER')  -> 'ACL GETUSER'      (subcommand)
    """
    base = filename.replace(".json", "").upper()
    if base == json_key.upper():
        return json_key.upper()
    parent = base.split("-", 1)[0]
    return f"{parent} {json_key.upper()}"


def parse_command(path):
    with open(path) as f:
        data = json.load(f)
    json_key = next(iter(data.keys()))
    info = data[json_key]
    full_name = full_command_name(os.path.basename(path), json_key)
    return full_name, info


def derive_categories(info):
    categories = set()

    for cat in info.get("acl_categories", []):
        categories.add(acl_cat_to_category(cat))

    flags = info.get("command_flags", [])
    for flag in flags:
        if flag in FLAG_TO_CATEGORY:
            categories.add(FLAG_TO_CATEGORY[flag])

    # @fast vs @slow: everything not @fast is @slow (matches Redis source).
    if "@fast" not in categories:
        categories.add("@slow")

    return categories


def main():
    cmd_dir = glob("/tmp/redis-cmds/redis-redis-*/src/commands/")[0]
    files = sorted(glob(os.path.join(cmd_dir, "*.json")))

    by_category = defaultdict(list)
    all_commands = {}

    for path in files:
        try:
            name, info = parse_command(path)
        except Exception as e:
            print(f"WARN: failed to parse {path}: {e}", file=sys.stderr)
            continue

        since = info.get("since", "unknown")
        if name in all_commands:
            print(f"WARN: duplicate command name {name} from {path}", file=sys.stderr)
        all_commands[name] = {"since": since, "info": info}

        cats = derive_categories(info)
        for cat in cats:
            by_category[cat].append((name, since))

    for cat in by_category:
        by_category[cat].sort(key=lambda x: x[0])

    # Output
    print("# Command-category map")
    print()
    print("> **Generated from [redis/redis@8.6.3](https://github.com/redis/redis/tree/8.6.3/src/commands).** Run `scripts/build-category-map.py` to regenerate from a newer Redis release.")
    print(">")
    print("> Each command's ACL category membership is derived from upstream `acl_categories` (explicit, e.g., `STRING`→`@string`) and `command_flags` (`READONLY`→`@read`, `WRITE`→`@write`, `ADMIN`→`@admin`, `BLOCKING`→`@blocking`, `FAST`→`@fast`; everything not `@fast` is `@slow`).")
    print(">")
    print(f"> **{len(all_commands)} commands** total (core Redis 8.6.3, no modules — see SUBMISSION_NOTE.md item #4 for module coverage as future work).")
    print(">")
    print("> The **Since** column shows the Redis version that introduced each command. The agent uses this to filter for the target version: a command with `Since: 7.0.0` is unavailable on Redis 6.x. **Cross-version category re-classifications** (e.g., `EVAL` moved from `@write` to `@scripting` in Redis 7.0) are documented in `version-deltas.md` and applied on top of this map.")
    print()
    print("---")
    print()

    standard = ["@keyspace", "@read", "@write", "@string", "@hash", "@list",
                "@set", "@sortedset", "@bitmap", "@hyperloglog", "@geo",
                "@stream", "@pubsub", "@connection", "@transaction", "@scripting"]
    meta = ["@admin", "@dangerous", "@blocking", "@fast", "@slow"]

    all_cats = list(by_category.keys())
    ordered = []
    for c in standard + meta:
        if c in by_category:
            ordered.append(c)
            if c in all_cats:
                all_cats.remove(c)
    for c in sorted(all_cats):
        ordered.append(c)

    for cat in ordered:
        cmds = by_category[cat]
        print(f"## `{cat}`")
        print()
        print(f"**{len(cmds)} commands** (Redis 8.6.3 — `Since: <X.Y.Z>` filters for older targets).")
        print()
        print("| Command | Since |")
        print("|---------|-------|")
        for name, since in cmds:
            print(f"| `{name}` | {since} |")
        print()

    print("---")
    print()
    print("## Regenerating this map")
    print()
    print("```bash")
    print("# From the repo root:")
    print("./scripts/build-category-map.py > skills/acl-reference/references/command-category-map.md")
    print("```")
    print()
    print("The script downloads the source tarball for the pinned Redis tag, extracts `src/commands/*.json`, and rebuilds this document. Bump the pinned tag in the script's header to regenerate for a different Redis release.")


if __name__ == "__main__":
    main()
