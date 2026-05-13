# Key pattern extraction

How to derive `~prefix:*` (and `&channel:*`) clauses from source code.

This is the **most security-relevant** part of the agent's work. A rule with `~*` (all keys) and `+@read +@write` is barely better than the `default` user — anyone who compromises the service has full data access. A rule with `~app:users:*` confines blast radius to one prefix.

> The `~pattern` clause is the difference between a real security boundary and security theater.

---

## The case table

The agent must handle each of these cases when walking source code. Pub/sub channel patterns follow the same logic but emit `&channel-pattern` instead of `~key-pattern`. Stream names are accessed by key, so they follow the `~` rule.

| # | Case | Source example | Extracted pattern |
|---|------|---------------|-------------------|
| 1 | **String literal** | `r.set("user:123:name", v)` | `~user:*` |
| 2 | **f-string / template** (literal prefix) | `r.set(f"user:{uid}:name", v)` | `~user:*` |
| 3 | **Concatenation** (literal prefix) | `r.get("session:" + sid)` | `~session:*` |
| 4 | **Module-level constant** (resolve & trace) | `PREFIX = "app:"` … `r.set(f"{PREFIX}cfg", v)` | `~app:*` |
| 5 | **Multiple distinct prefixes in same file** | `r.set("user:...", v)` + `r.set("session:...", v)` | `~user:* ~session:*` (multiple clauses) |
| 6 | **Fully dynamic key** (no literal prefix discoverable) | `r.set(build_key(req), v)` | ⚠️ Flag. Conservative fallback `~*` with explicit warning that the rule offers no key isolation. ASK the user. |
| 7 | **Computed prefix from runtime input** | `r.set(f"{tenant_id}:cache:{k}", v)` | ⚠️ Cannot pin a static `~` pattern. ASK user — common resolutions: `~*:cache:*` (multi-tenant cache surface) or refactor to a known prefix bucket. |
| 8 | **Composite namespace function** | `def key_for(uid, kind): return f"{kind}:{uid}"` → `r.set(key_for(uid, "user"), v)` | If the function's literal-prefix arg is statically known at all call sites, extract per-call (here: `~user:*`). If varied, ASK. |
| 9 | **Constant from imported module** | `from config import REDIS_NS` … `r.set(f"{REDIS_NS}:x", v)` | Trace the import and resolve `REDIS_NS`. If resolvable to a literal, extract. If not, ASK. |
| 10 | **Loop emitting keys** | `for kind in ["user", "session"]: r.set(f"{kind}:{id}", v)` | `~user:* ~session:*` — enumerate the loop iterable if it's a literal collection; ASK if dynamic. |

---

## Case-by-case detail

### Case 1 — String literal

The prefix is everything up to the first `:` (or first interpolation point — for raw literals, the whole prefix before any variable part). Extract that prefix + `:*`.

```python
r.set("user:123:name", "alice")
```

→ Prefix segment: `user`. Pattern: `~user:*`.

If the literal has no colon (e.g., `r.set("just-a-key", v)`), emit `~just-a-key` (exact key) or `~just-a-key*` if the agent thinks variants exist (ASK if unsure).

### Case 2 — f-string / template with literal prefix

The agent extracts the **literal prefix portion** before any interpolation.

```python
r.set(f"user:{uid}:name", v)
r.set(f"cache:user:{uid}", v)
```

→ `~user:*` and `~cache:user:*` respectively (each extracted independently).

**Tighter pattern wins for security.** Don't collapse `~cache:user:*` into `~cache:*` unless the service also accesses `cache:` keys without the `user:` segment.

JavaScript template literals (`` `user:${uid}` ``) and Go's `fmt.Sprintf("user:%s", uid)` follow the same logic.

### Case 3 — String concatenation with literal prefix

```python
r.get("session:" + sid)
```

→ `~session:*`.

```javascript
client.get("session:" + sid);
```

→ `~session:*`.

If the concatenation has only variable parts (e.g., `prefix + ":" + suffix` where both `prefix` and `suffix` are variables), follow them — likely Case 4 or Case 6.

### Case 4 — Module-level constant prefix

The agent traces the constant back to its definition in the same module (or imported from another module — Case 9).

```python
CACHE_PREFIX = "cache:user:"

def cache_user(uid, profile):
    r.set(f"{CACHE_PREFIX}{uid}", json.dumps(profile))
```

→ `~cache:user:*`.

```javascript
const CACHE_PREFIX = "cache:user:";

function cacheUser(uid, profile) {
    client.set(`${CACHE_PREFIX}${uid}`, JSON.stringify(profile));
}
```

→ `~cache:user:*`.

```go
const CachePrefix = "cache:user:"

func CacheUser(ctx context.Context, uid string, profile []byte) {
    rdb.Set(ctx, CachePrefix+uid, profile, 0)
}
```

→ `~cache:user:*`.

### Case 5 — Multiple distinct prefixes in same file

When the same module touches multiple key prefixes, emit one `~` clause per distinct prefix.

```python
CACHE_PREFIX = "cache:user:"
SESSION_PREFIX = "session:"

def cache_user(uid, profile):
    r.set(f"{CACHE_PREFIX}{uid}", json.dumps(profile))

def create_session(token, uid):
    r.setex(f"{SESSION_PREFIX}{token}", 3600, uid)
```

→ `~cache:user:* ~session:*` (sorted alphabetically for stable output).

### Case 6 — Fully dynamic key

If the key cannot be traced to any literal prefix (it's built from a function whose inputs are runtime-only), the agent has two paths:

1. **Conservative fallback**: emit `~*` and explicitly warn in the output: *"Key isolation could not be inferred from the code at `service.py:42` (key built by `build_key(req)`). Rule emits `~*`, which provides NO key boundary. Either refactor to a known prefix or accept that this user can touch any key on the database."*
2. **Refuse to emit**: tell the user the agent cannot generate a safe rule without a clearer key scheme, and stop.

**Default to option 1 with a loud warning.** Option 2 is appropriate only if the codebase has many such cases and the rule would be effectively useless.

### Case 7 — Computed prefix from runtime input

```python
def cache_for_tenant(tenant_id, k, v):
    r.set(f"{tenant_id}:cache:{k}", v)
```

The prefix depends on a runtime variable. There are several real resolutions; the agent should ASK:

- *"Are tenant IDs from a closed set known at deploy time? If yes, list them and I'll emit a discrete clause per tenant."* (Best — minimum-necessary multi-tenant scope.)
- *"Should this user have access to all tenants' cache prefixes? If yes, I'll emit `~*:cache:*`."* (Broader — usable when the service is the central multi-tenant cache layer.)
- *"Should we refactor to a known top-level namespace?"* (Architectural change — out of scope for the rule.)

### Case 8 — Composite namespace function

```python
def key_for(uid: str, kind: str) -> str:
    return f"{kind}:{uid}"

r.set(key_for(uid, "user"), profile)
r.set(key_for(sid, "session"), token)
```

The function abstracts the prefix but each call site passes a literal `kind`. The agent should:

1. Locate `key_for`'s definition (resolved via the import path / scope chain).
2. Identify the literal-prefix argument's position (here, `kind`).
3. For each call site, extract the literal value passed to that position.
4. Emit one `~` clause per distinct literal value.

→ `~user:* ~session:*`.

If a call site passes a runtime value (e.g., `key_for(uid, kind_from_request)`), drop that call into Case 7.

### Case 9 — Constant imported from another module

```python
# config.py
REDIS_NS = "myapp"

# service.py
from config import REDIS_NS
r.set(f"{REDIS_NS}:user:{uid}", profile)
```

The agent resolves the import:

1. Find the import statement (`from config import REDIS_NS`).
2. Read `config.py`, find the `REDIS_NS = "myapp"` assignment.
3. Use the resolved literal in pattern extraction.

→ `~myapp:user:*`.

If `config.py` reads the value from an env var (`REDIS_NS = os.environ["REDIS_NS"]`), it's no longer statically inferable — ASK the user.

### Case 10 — Loop emitting keys

```python
for kind in ("user", "session", "notification"):
    r.delete(f"{kind}:{id}")
```

If the loop iterable is a literal collection (list/tuple/set of strings), enumerate it and emit one clause per literal.

→ `~notification:* ~session:* ~user:*`.

If the iterable is dynamic (e.g., `for kind in get_kinds_from_config():`), drop into Case 7.

---

## Channels — same logic, different sigil

Pub/sub channels follow the identical case table but emit `&channel-pattern` instead of `~key-pattern`.

| Source | Extracted pattern |
|--------|-------------------|
| `r.publish("notifications", msg)` | `&notifications` |
| `r.publish(f"alerts:{tenant}", msg)` | `&alerts:*` |
| `NOTIFY_CHANNEL = "events:user"` … `r.publish(NOTIFY_CHANNEL, m)` | `&events:user` (exact, no wildcard unless variants seen) |
| `for c in ("a", "b"): r.subscribe(c)` | `&a &b` |

> Remember: recent Redis defaults to **restrictive** pub/sub. The `&` clauses are mandatory for any service that publishes or subscribes, or the rule will block legitimate pub/sub even with `+@pubsub`.

---

## Streams — `~` rule with stream-name awareness

XADD/XREAD/XREADGROUP etc. target a stream by **key name**. The extracted pattern uses the same `~` clause logic:

```python
ACTIVITY_STREAM = "activity:events"
r.xadd(ACTIVITY_STREAM, {"user": uid, "action": a})
```

→ `~activity:events` (exact key, since there's no variant). For multiple streams sharing a prefix:

```python
r.xadd(f"audit:{service_name}", event)
```

→ `~audit:*`.

---

## Sorting and deduplication

For stable output across runs:

- **Deduplicate**: if the same pattern is extracted from multiple call sites, emit one clause, but list all source citations in the annotation table.
- **Sort**: alphabetical by pattern. `~cache:user:* ~session:*` not `~session:* ~cache:user:*`.

---

## When the case table doesn't fit

Some real codebases have key schemes the agent can't infer cleanly — domain-specific encoding, key-builder utilities with complex logic, or schemes that change at runtime based on config.

**Default behavior:** ASK. State what was found, what was ambiguous, and request the user's intended pattern. Don't guess and don't silently emit `~*`.

The agent's value is *correctness*, not coverage. A rule built from "I asked the engineer for the right prefix" is better than a rule built from a wrong inference.
