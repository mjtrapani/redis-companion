---
description: Use when working with Redis client code, generating or reviewing Redis ACL rules, or discussing Redis access-control syntax. Provides the Redis ACL DSL primer, OSS-vs-Enterprise fork map, and pointers to detailed reference docs (command-category mappings, version deltas, client-library patterns, key-pattern extraction).
---

# redis-acl-patterns

Knowledge base for Redis Access Control Lists (ACLs). Loads automatically when the conversation touches Redis client code, ACL rule construction, or ACL syntax discussion. Also loaded by the companion `acl-generator` agent at task start.

## What lives here

- **Top-level orientation** (this file): the ACL DSL primer + OSS vs Enterprise fork map + when to consult `ACL CAT` live
- **Reference docs** (`references/`): exhaustive lookup tables and case-handling guides — load on demand, not all at once

---

## Redis ACL DSL — the primitives

A Redis ACL "rule" is a sequence of these primitives, applied in order.

### Authentication / lifecycle

| Primitive | Meaning |
|-----------|---------|
| `on` | Enable the user |
| `off` | Disable the user (cannot authenticate) |
| `>password` | Add the password (stored SHA256-hashed) |
| `<password` | Remove the password |
| `nopass` | Allow authentication with any password (DEV ONLY — never ship to prod) |
| `resetpass` | Remove all passwords; user has no way to authenticate |
| `reset` | Reset *everything*: passwords, keys, channels, commands |

> **On Enterprise**, authentication-related primitives (`on`/`off`, `>password`, `nopass`) are configured at the **User object** level, not in the ACL Rule body. Don't include them in the rule body for Enterprise output.

### Keyspace

| Primitive | Meaning |
|-----------|---------|
| `~pattern` | Grant access to keys matching `pattern` (glob: `*`, `?`, `[abc]`) |
| `allkeys` / `~*` | Grant access to all keys |
| `resetkeys` | Reset all key patterns |
| `%R~pattern` | (Redis 7+) Read-only access to matching keys |
| `%W~pattern` | (Redis 7+) Write-only access to matching keys |
| `%RW~pattern` | (Redis 7+) Read + write (equivalent to `~pattern`) |

### Pub/sub channels

| Primitive | Meaning |
|-----------|---------|
| `&pattern` | Grant access to channels matching `pattern` |
| `allchannels` / `&*` | Grant access to all channels |
| `resetchannels` | Reset all channel patterns |

> ⚠️ **Recent Redis versions default to restrictive pub/sub** — channels are blocked unless an `&` clause grants them. Any rule for a service that publishes or subscribes MUST include `&` patterns. The default behavior is controlled by `acl-pubsub-default` on Enterprise (added in Redis Software 6.4.2).

### Commands

| Primitive | Meaning |
|-----------|---------|
| `+COMMAND` | Allow a specific command |
| `-COMMAND` | Deny a specific command |
| `+@category` | Allow all commands in a category (e.g. `+@read`, `+@write`) |
| `-@category` | Deny all commands in a category |
| `+COMMAND\|subcommand` | Allow a specific subcommand (e.g. `+CLIENT\|GETNAME`) |
| `allcommands` / `+@all` | Allow all commands (almost never what you want) |
| `nocommands` / `-@all` | Deny all commands (often a clean starting point — then add explicit grants) |

### Selectors (Redis 7+)

Selectors are parenthesized groups that scope permissions to a narrower context. They model real access shapes more precisely than flat rules:

```
ACL SETUSER alice on >pw resetkeys +@read (+SET ~cache:*) (+XADD ~stream:logs:*)
```

This grants `alice`:
- Read commands everywhere with the default key scope (but `resetkeys` cleared `~*`, so... see below)
- `SET` only on keys matching `cache:*`
- `XADD` only on keys matching `stream:logs:*`

Selectors are powerful but easy to get wrong. For most application rules, flat permissions are sufficient. Use selectors when a service has genuinely different scopes per operation (e.g., reads everything, writes only one prefix).

---

## OSS vs Enterprise — fork map

The ACL DSL itself is identical on both editions. What differs is **how a rule is applied** and where user-level concerns (auth, source IP allowlists) live.

| Concern | Redis OSS / Redis Cloud direct-connect | Redis Enterprise / Redis Software |
|---------|---------------------------------------|------------------------------------|
| Rule application | `ACL SETUSER <user> on >pw <rule>` — single command, applied directly | Create an **ACL Rule** object with the rule body → attach to a **Role** → assign Role to a **User**. Via admin UI or REST API. |
| User auth (password, source IPs, cert) | Inline in `ACL SETUSER` (or via `>password`, `nopass`, etc.) | Configured at the **User** object level, separately from the rule body |
| Live `ACL SETUSER` | ✅ Works directly | ❌ Blocked at cluster level — ACL writes are gated through the cluster manager REST API, not the data plane |
| Read-side ACL commands (`ACL LIST`, `ACL GETUSER`, `ACL WHOAMI`) | ✅ | ✅ Work for read; output shape may differ — handle gracefully |
| `ACL CAT` and `ACL CAT @<category>` | ✅ Authoritative for this server's category set | ✅ Authoritative for this database's category set (including loaded modules) |
| Default user | `default` user is implicit and always present (start by reviewing/locking it down) | Enterprise deployments typically use explicit users only |
| Pub/sub default | Permissive in older versions, restrictive in recent | Controlled by `acl-pubsub-default` cluster setting (Software 6.4.2+) |

### What this means for rule output

- **For Redis OSS**: emit a full `ACL SETUSER <user> on ><password> <rule>` command — directly runnable via `redis-cli`. Replace `<password>` with the actual credential before running.
- **For Redis Enterprise**: emit just the rule body (the permission DSL). The customer applies it as an ACL Rule body in the admin UI or REST API. User authentication is separate. *(Generating the Enterprise REST API JSON payload is future work for this plugin.)*

### Enterprise's two-axis version model

Redis Enterprise has **two** versions to be aware of, no OSS user thinks about both:

- **Database version** — what the Redis instance reports via `INFO`. Drives the ACL feature surface (e.g., pub/sub ACLs need 6.2+; selectors and `%R~`/`%W~` need 7.2+; Redis 8 expanded standard categories to include module commands).
- **Cluster / Software version** — what the surrounding Enterprise platform runs. Controls which DB versions are supported and adds cluster-wide ACL settings (e.g., `acl-pubsub-default` was added in Software 6.4.2).

For v1, use `ACL CAT` against the live database as the practical proxy for "what works here." Querying the cluster manager API for the cluster's Software version is future work.

---

## `ACL CAT` — the live source of truth

When working against a connected Redis (MCP), prefer `ACL CAT` and `ACL CAT @<category>` over any baked-in reference. Reasons:

- Categories drift between Redis 6 / 7 / 8 — see `references/version-deltas.md`
- Module commands (RedisJSON, RediSearch, RedisTimeSeries, etc.) only appear on the live server if the module is loaded
- The `>50%` category-collapse decision becomes a direct count when you can list category commands live

Fall back to the static `references/command-category-map.md` only when no MCP connection is available, or for offline reasoning. When falling back, surface a *"version drift possible — connect MCP for live verification"* note.

---

## Reference docs — what's in each, when to consult

| Reference | When to consult |
|-----------|-----------------|
| `references/command-category-map.md` | You need an offline command-to-category lookup, or the inverse (which commands belong to `@write`). Structured **category → commands** with per-version columns (Redis 6 / 7 / 8). Includes common module categories (`@json`, `@search`, `@timeseries`, etc.) with a "module-loaded" caveat. |
| `references/version-deltas.md` | The target Redis version affects the rule. Highlights `@scripting` split out of `@write` in Redis 7, ACL selectors and `%R~`/`%W~` in 7+, Redis 8's expansion of standard categories to module commands, and the pub/sub default flip. |
| `references/client-library-patterns.md` | You're reading source code and need to map a client method to its underlying Redis command (e.g., `r.setex(...)` in redis-py → `SETEX`). Covers `redis-py`, `ioredis` (Node), and `go-redis`. |
| `references/key-pattern-extraction.md` | You need to derive `~prefix:*` clauses from source code. Handles string literals, f-strings, concatenation, module-level constants, multi-pattern files, and fully-dynamic keys. The `~pattern` clause is the difference between a real security boundary and security theater. |

---

## Companion: the `acl-generator` agent

If the user wants to **generate a complete Redis ACL rule for a specific service** (rather than discuss the syntax in the abstract), invoke the `acl-generator` agent. It:

- Scans the target codebase for Redis usage
- Asks the user for edition (OSS vs Enterprise), version, and defense-in-depth preference
- Synthesizes a least-privilege rule with per-term annotations
- (Optional, OSS + Redis MCP connected) Applies the rule after a safety gate, verifies via `ACL GETUSER`, validates by impersonation

Invocation paths:
- Natural language: *"scope an ACL for ./my-service"*
- Slash command: `/redis-companion:analyze <path>`
- Agent picker: `/agents` → `acl-generator`
