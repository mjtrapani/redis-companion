# Version deltas — Redis 6 → 7 → 8 (and Enterprise / Software)

What changed across major Redis versions that affects ACL rule generation. Knowing these lets you generate rules that *actually work* on the target — what's valid in Redis 7 may not parse in Redis 6, and what's needed in Redis 8 may not have existed earlier.

> ⚠️ For the target server's actual feature surface, `ACL CAT` (and `INFO server` for `redis_version`) are authoritative. This document is the offline reference.

---

## Redis 6 → Redis 7

### `@scripting` is now its own category

In **Redis 6**, server-side scripting (`EVAL`, `EVALSHA`, `SCRIPT *`) was bundled into `@write`. There was no `@scripting` category.

In **Redis 7**, `@scripting` was split out. It contains:

`EVAL`, `EVALSHA`, `EVAL_RO`, `EVALSHA_RO`, `SCRIPT LOAD`, `SCRIPT EXISTS`, `SCRIPT FLUSH`, `SCRIPT DEBUG`, `FCALL`, `FCALL_RO`, `FUNCTION LOAD`, `FUNCTION DUMP`, `FUNCTION RESTORE`, `FUNCTION FLUSH`, `FUNCTION LIST`, `FUNCTION STATS`, `FUNCTION DELETE`

**Implication for the agent:**
- A service that uses `EVAL` on Redis 6 needs `+@write` (or `+EVAL` individually).
- The same service on Redis 7+ needs `+@scripting` (or `+EVAL`).
- A rule like `+@write -@scripting` will deny scripting on Redis 7+ but is a no-op on Redis 6 (since `@scripting` doesn't exist there). Generate version-appropriate rules.

### Redis Functions (`FCALL`, `FUNCTION *`) introduced

Redis 7 added Redis Functions as a successor to EVAL-based scripting. The `FUNCTION *` and `FCALL`/`FCALL_RO` commands are all in `@scripting`. Rules synthesized for Redis 6 should not include these.

### ACL selectors

Redis 7 introduced **selectors** — parenthesized permission groups that scope grants to a narrower context:

```
ACL SETUSER alice on >pw +@read (+SET ~cache:*) (+XADD ~stream:logs:*)
```

This grants `alice` read access plus targeted writes scoped to specific key patterns.

**Implication:** Don't emit selector syntax for Redis 6 — it will be rejected. For Redis 7+, selectors are an optional precision tool; flat rules still work and remain the easier-to-explain choice for v1.

### Read/write key modifiers `%R~`, `%W~`, `%RW~`

Redis 7 added per-pattern read/write modifiers:

- `%R~pattern` — read-only access to keys matching `pattern`
- `%W~pattern` — write-only access to keys matching `pattern`
- `%RW~pattern` — read + write (equivalent to `~pattern`)

**Implication:** Useful for splitting read and write capabilities by key prefix without selectors. Don't emit these on Redis 6.

### Sharded pub/sub

Redis 7 added cluster-shard-local pub/sub: `SSUBSCRIBE`, `SUNSUBSCRIBE`, `SPUBLISH`. These are in `@pubsub`.

**Implication:** Don't emit these on Redis 6. If a service uses sharded pub/sub on Redis 7+, the `@pubsub` count goes up by 3 → may shift `>50%` collapse decisions.

### `EXPIRETIME`, `PEXPIRETIME`

Redis 7 added these read-side TTL inspection commands (return the absolute expiry timestamp, not remaining TTL).

### `BITFIELD_RO`, `GEORADIUS_RO`, etc.

Redis 7 (and late Redis 6.2) split read-only variants of read+write commands into separate commands. These belong to `@read` cleanly, where the original write-capable forms are in both `@read` and `@write`.

**Implication:** Granting `+BITFIELD_RO` is strictly read-only and safer than `+BITFIELD`. The agent should prefer `_RO` variants when the service only reads.

---

## Redis 7 → Redis 8

### Module commands contribute to standard categories

This is the biggest semantic shift in Redis 8: **module commands** (RedisJSON, RediSearch, RedisTimeSeries, Bloom filters, etc.) are now included in the **standard** ACL categories.

**Before (Redis 7 with modules loaded):**
- `JSON.GET` is in `@json` only
- `JSON.SET` is in `@json` only
- A rule with `+@read +@write` does NOT grant any JSON commands; the user must add `+@json`

**Redis 8:**
- `JSON.GET` is in `@read` AND `@json`
- `JSON.SET` is in `@write` AND `@json`
- A rule with `+@read +@write` DOES grant the read/write JSON commands

**Implication for the agent:**
- On Redis 8 with modules loaded, prefer `+@read +@write` granular grants — module commands are covered "for free."
- For granular control over module surface, still emit module-category grants/denies.
- Detection requires either `INFO modules` (live, MCP) or asking the user. Without MCP, ask.

### Other categories expanded

Several standard categories were expanded with new core commands and module-contributed commands. The most reliable way to know the Redis 8 category surface is `ACL CAT` live.

### Hash field expiration (Redis 7.4+ / 8)

Per-hash-field TTLs were added in late Redis 7 / Redis 8:
- `HEXPIRE`, `HEXPIREAT`, `HPEXPIRE`, `HPEXPIREAT` — write-side, in `@hash` + `@write`
- `HEXPIRETIME`, `HPEXPIRETIME`, `HTTL`, `HPTTL` — read-side, in `@hash` + `@read`
- `HPERSIST` — write-side

A service using these on Redis 8 expects them; on Redis 7.0–7.3 they don't exist.

---

## Pub/sub default deny — across versions

Older Redis defaulted to **permissive** pub/sub (any user could publish/subscribe to any channel). Recent versions default to **restrictive** — channels are blocked unless an explicit `&pattern` clause grants them.

| Version | Default behavior |
|---------|------------------|
| Redis OSS ≤ 6.0 | Permissive — no channel ACLs at all |
| Redis OSS 6.2+ | Channel ACLs introduced; default still permissive (`&*`) |
| Redis OSS 7.0+ | Default flipped to restrictive |
| Redis Enterprise / Software ≤ 6.4.1 | Permissive |
| Redis Software 6.4.2+ | Controlled by `acl-pubsub-default` cluster setting (defaults to permissive for backward compat; admins can set restrictive) |

**Implication:** For any service that does pubsub on a recent Redis, the rule MUST include explicit `&channel-pattern` clauses. Failing to include them means the service can't publish or subscribe even though the rule otherwise looks correct.

---

## Enterprise's two-axis version model

Redis Enterprise has **two** versions that interact, no OSS user thinks about both:

| Axis | What it controls |
|------|------------------|
| **Database version** (reported by `INFO server`) | The ACL feature surface — pub/sub ACLs need DB 6.2+; selectors and `%R~`/`%W~` need DB 7.2+; Redis 8 expanded standard categories to include module commands |
| **Cluster / Software version** (reported by the cluster manager API) | Which DB versions are supported; cluster-wide settings like `acl-pubsub-default` (added in Software 6.4.2) |

**For v1** of `acl-generator`: use the database version (asked from the user, or `INFO server` via MCP) as the proxy for "what works here." Run `ACL CAT` against the live DB if MCP is connected — that's the practical authority. Querying the cluster manager API for Software version is future work.

---

## Quick lookup

| Feature | Redis 6 | Redis 7 | Redis 8 |
|---------|---------|---------|---------|
| `@scripting` category | ❌ (bundled in `@write`) | ✅ | ✅ |
| ACL selectors | ❌ | ✅ | ✅ |
| `%R~` / `%W~` modifiers | ❌ | ✅ (7.2+) | ✅ |
| Sharded pub/sub (`SSUBSCRIBE` etc.) | ❌ | ✅ | ✅ |
| Modules in `@read`/`@write` | ❌ | ❌ | ✅ |
| Per-hash-field TTL (`HEXPIRE` etc.) | ❌ | ✅ (7.4+) | ✅ |
| Default-deny pub/sub | ❌ | ✅ | ✅ |
| `EVAL`/`EVALSHA` category | `@write` | `@scripting` | `@scripting` |
