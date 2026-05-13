# Client library patterns — method → Redis command

Reference for mapping client-library method calls to the underlying Redis commands. Used during the agent's discovery phase (step 2e) to build the command inventory.

Covers the three SPEC-named clients:

- **Python**: `redis-py` (the `redis` package)
- **Node.js**: `ioredis` (and `node-redis` notes where it differs)
- **Go**: `go-redis` (`github.com/redis/go-redis`)

Java, Rust, .NET, and other clients are future work. When the agent encounters one of those, it should detect the language, name the client if obvious, and ASK the user for method-to-command guidance (or assume direct method-name → command mapping when the client is a thin wrapper).

---

## Pattern: method names usually map directly to commands

Across all three covered clients, the convention is: **the method name (case-normalized) is the Redis command name.** Examples:

- `r.set(key, value)` → `SET`
- `client.get(key)` → `GET`
- `rdb.HSet(ctx, key, field, value)` → `HSET`

When a method name is non-obvious (e.g., aliases, helpers, language-specific naming), check the cases below.

---

## `redis-py` (Python — package `redis`)

Imports to look for:

```python
import redis
from redis import Redis
from redis.asyncio import Redis as AsyncRedis
```

Connection style (typical):

```python
r = redis.Redis(host="...", port=6379, db=0)
r = redis.Redis.from_url("redis://...")
```

### Direct-mapping methods

The method name (lowercased) is the Redis command:

| Method | Redis command |
|--------|---------------|
| `r.set(key, value, ex=ttl)` | `SET` (with `EX` modifier → equivalent to `SETEX` for ACL purposes) |
| `r.setex(key, time, value)` | `SETEX` |
| `r.get(key)` | `GET` |
| `r.mget(keys)` | `MGET` |
| `r.mset(mapping)` | `MSET` |
| `r.delete(*keys)` | `DEL` |
| `r.unlink(*keys)` | `UNLINK` |
| `r.exists(*keys)` | `EXISTS` |
| `r.expire(key, time)` | `EXPIRE` |
| `r.ttl(key)` | `TTL` |
| `r.hset(key, field, value)` | `HSET` |
| `r.hget(key, field)` | `HGET` |
| `r.hmget(key, *fields)` | `HMGET` |
| `r.hgetall(key)` | `HGETALL` |
| `r.lpush(key, *values)` | `LPUSH` |
| `r.rpush(key, *values)` | `RPUSH` |
| `r.lpop(key)` | `LPOP` |
| `r.rpop(key)` | `RPOP` |
| `r.lrange(key, start, end)` | `LRANGE` |
| `r.sadd(key, *values)` | `SADD` |
| `r.srem(key, *values)` | `SREM` |
| `r.smembers(key)` | `SMEMBERS` |
| `r.zadd(key, mapping)` | `ZADD` |
| `r.zrange(key, start, end)` | `ZRANGE` |
| `r.publish(channel, message)` | `PUBLISH` |
| `r.subscribe(*channels)` (via PubSub) | `SUBSCRIBE` |
| `r.xadd(stream, fields)` | `XADD` |
| `r.xread(streams)` | `XREAD` |
| `r.xlen(stream)` | `XLEN` |
| `r.geoadd(name, values)` | `GEOADD` |
| `r.bitcount(key)` | `BITCOUNT` |
| `r.pfadd(key, *values)` | `PFADD` |

### Notable redis-py specifics

- **Pipeline / transaction**: `r.pipeline()` opens a pipeline. Calls on the pipeline (e.g., `pipe.set(...)`) accumulate. `pipe.execute()` issues `MULTI`/`EXEC` if `transaction=True` (default). The ACL needs all the underlying commands AND `@transaction` (which includes `MULTI`/`EXEC`/`DISCARD`/`WATCH`/`UNWATCH`).
- **`r.eval(script, numkeys, *keys_and_args)`** → `EVAL` (`@scripting` on Redis 7+, `@write` on Redis 6).
- **`r.evalsha(sha1, numkeys, *keys_and_args)`** → `EVALSHA`.
- **`r.scan_iter(match="...")`** → uses `SCAN` repeatedly (preferred over `r.keys()` for prod).
- **`r.keys(pattern)`** → `KEYS` (in `@dangerous` — generally avoid).
- **Async** (`redis.asyncio.Redis`): same method names; async/await wraps them. Method → command mapping is identical.

### PubSub object

```python
ps = r.pubsub()
ps.subscribe("channel-1", "channel-2")
ps.psubscribe("pattern.*")
```

→ `SUBSCRIBE`, `PSUBSCRIBE` respectively.

### Stream consumer-group helpers

```python
r.xgroup_create(stream, group, id="$")
r.xreadgroup(group, consumer, streams)
r.xack(stream, group, *ids)
r.xclaim(stream, group, consumer, min_idle_time, *ids)
```

→ `XGROUP CREATE`, `XREADGROUP`, `XACK`, `XCLAIM`. All `@stream` (most also `@write`).

---

## `ioredis` (Node.js — preferred over deprecated `node-redis` v3)

Imports to look for:

```javascript
const Redis = require("ioredis");
const { Redis } = require("ioredis");
import Redis from "ioredis";
```

Connection style:

```javascript
const client = new Redis({ host: "...", port: 6379 });
const client = new Redis("redis://...");
```

### Direct-mapping methods

ioredis exposes each Redis command as a method, lowercased:

| Method | Redis command |
|--------|---------------|
| `client.set(key, value, "EX", ttl)` | `SET` |
| `client.setex(key, ttl, value)` | `SETEX` |
| `client.get(key)` | `GET` |
| `client.mget(...keys)` | `MGET` |
| `client.mset(...keyValues)` | `MSET` |
| `client.del(...keys)` | `DEL` |
| `client.unlink(...keys)` | `UNLINK` |
| `client.exists(...keys)` | `EXISTS` |
| `client.expire(key, seconds)` | `EXPIRE` |
| `client.hset(key, field, value)` | `HSET` |
| `client.hget(key, field)` | `HGET` |
| `client.hgetall(key)` | `HGETALL` |
| `client.lpush(key, ...values)` | `LPUSH` |
| `client.rpush(key, ...values)` | `RPUSH` |
| `client.lrange(key, start, stop)` | `LRANGE` |
| `client.sadd(key, ...values)` | `SADD` |
| `client.smembers(key)` | `SMEMBERS` |
| `client.zadd(key, ...args)` | `ZADD` |
| `client.publish(channel, message)` | `PUBLISH` |
| `client.subscribe(...channels)` | `SUBSCRIBE` |
| `client.xadd(stream, ...fields)` | `XADD` |
| `client.xread(...args)` | `XREAD` |

### Notable ioredis specifics

- **Multi/pipeline**: `client.multi()` opens a transaction; chained method calls and then `.exec()` issue `MULTI`/`EXEC`. Pipelines without transactions use `client.pipeline()`.
- **Stream subscribers via PubSub**: ioredis uses the same client for pubsub by default; calling `subscribe()` puts the connection into pub/sub mode. The ACL still needs `+@pubsub` or `+SUBSCRIBE`/`+PUBLISH`.
- **Lua**: `client.defineCommand("scriptName", { lua: "..." })` defines a command-style helper that calls `EVALSHA`. Maps to `EVAL` / `EVALSHA`.
- **Cluster mode**: `new Redis.Cluster([...])` for cluster connections. Same method-name → command mapping.

### `node-redis` v4+ differs slightly

The current `node-redis` package (v4+) uses camelCase method names:

- `client.set` → `SET` (same)
- `client.hSet(key, field, value)` → `HSET`
- `client.zAdd(key, ...)` → `ZADD`

The underlying commands are the same.

---

## `go-redis` (Go — `github.com/redis/go-redis/v9`)

Imports to look for:

```go
import "github.com/redis/go-redis/v9"
// older versions:
import "github.com/go-redis/redis/v8"
```

Connection style:

```go
rdb := redis.NewClient(&redis.Options{Addr: "...", DB: 0})
rdb := redis.NewClient(redis.ParseURL("redis://..."))
```

### Direct-mapping methods (PascalCase)

go-redis uses PascalCase method names with the Redis command as the suffix:

| Method | Redis command |
|--------|---------------|
| `rdb.Set(ctx, key, value, ttl)` | `SET` (with `EX` if ttl != 0) |
| `rdb.SetEx(ctx, key, value, ttl)` | `SETEX` |
| `rdb.Get(ctx, key)` | `GET` |
| `rdb.MGet(ctx, keys...)` | `MGET` |
| `rdb.MSet(ctx, values...)` | `MSET` |
| `rdb.Del(ctx, keys...)` | `DEL` |
| `rdb.Unlink(ctx, keys...)` | `UNLINK` |
| `rdb.Exists(ctx, keys...)` | `EXISTS` |
| `rdb.Expire(ctx, key, ttl)` | `EXPIRE` |
| `rdb.HSet(ctx, key, values...)` | `HSET` |
| `rdb.HGet(ctx, key, field)` | `HGET` |
| `rdb.HGetAll(ctx, key)` | `HGETALL` |
| `rdb.LPush(ctx, key, values...)` | `LPUSH` |
| `rdb.RPush(ctx, key, values...)` | `RPUSH` |
| `rdb.LRange(ctx, key, start, stop)` | `LRANGE` |
| `rdb.SAdd(ctx, key, members...)` | `SADD` |
| `rdb.SMembers(ctx, key)` | `SMEMBERS` |
| `rdb.ZAdd(ctx, key, members...)` | `ZADD` |
| `rdb.ZRange(ctx, key, start, stop)` | `ZRANGE` |
| `rdb.Publish(ctx, channel, message)` | `PUBLISH` |
| `rdb.Subscribe(ctx, channels...)` | `SUBSCRIBE` |
| `rdb.XAdd(ctx, &redis.XAddArgs{...})` | `XADD` |
| `rdb.XRead(ctx, &redis.XReadArgs{...})` | `XREAD` |

### Notable go-redis specifics

- **Pipeline / TxPipeline**: `rdb.Pipeline()` and `rdb.TxPipeline()`. The latter wraps in `MULTI`/`EXEC` → needs `@transaction`.
- **Script execution**: `redis.NewScript("...")` and `.Run(ctx, rdb, keys, args...)` → `EVAL`/`EVALSHA` (`@scripting` on Redis 7+).
- **Stream consumer groups**: `rdb.XGroupCreate(...)`, `rdb.XReadGroup(...)`, `rdb.XAck(...)`, `rdb.XClaim(...)`.
- **Cluster mode**: `redis.NewClusterClient(...)` for cluster connections.

---

## Patterns to watch for during scanning

When grepping for Redis usage, look for these signals:

| Signal | Hint |
|--------|------|
| `import redis` + `redis.Redis(...)` | redis-py |
| `from redis import` | redis-py |
| `require("ioredis")` / `from "ioredis"` | ioredis |
| `require("redis")` / `createClient` from `redis` | node-redis v4+ |
| `github.com/redis/go-redis` in go.mod | go-redis v9 |
| `github.com/go-redis/redis` in go.mod | go-redis v8 (older) |

Variable-name conventions to grep on for usage:

- Python: `r.`, `redis_client.`, `cache.`, `client.`
- Node: `client.`, `redis.`, `cache.`, `pubsub.`
- Go: `rdb.`, `client.`, `cache.`

Don't rely on variable names alone — verify with the import. A variable named `client` might not be a Redis client.

---

## Caveats — where the convention breaks

The "method name = Redis command name" convention covers most simple-CRUD usage but breaks for several real cases. When the agent encounters any of these, it must **flag for verification** (or recommend the user run `MONITOR` to confirm wire-level commands). This document's mappings are based on each library's documented API, not on first-party source review or wire-level observation.

### Scripting helpers issue both `EVAL` and `EVALSHA`

Most clients have a "smart" eval helper that:

1. First call: sends `EVAL <script> ...`
2. Subsequent calls: may switch to `EVALSHA <sha1> ...` (after the script is cached server-side)
3. On `NOSCRIPT` error: falls back to `EVAL`

**ACL implication:** `+EVAL` alone is **not** enough. Need `+EVAL +EVALSHA` (or `+@scripting` on Redis 7+, or `+@write` on Redis 6). Same goes for the read-only variants `EVAL_RO` / `EVALSHA_RO`.

Affected helpers:

- redis-py: `r.eval(...)`, `r.evalsha(...)`
- ioredis: `client.eval(...)`, scripts defined via `client.defineCommand({lua: "..."})`
- go-redis: `redis.NewScript("...").Run(ctx, rdb, ...)`

### Locking helpers use `SET` + `EVAL` internally

`r.lock(name)` (redis-py), the `redlock` family of libraries, and bespoke distributed-lock helpers typically:

- **Acquire**: `SET key value NX PX ttl`
- **Release**: `EVAL <atomic-check-and-delete-script> ...`

**ACL implication:** Grant `+SET +EVAL +EVALSHA` (plus the lock-key pattern in `~`). A user with `+SET` alone gets a lock helper that can acquire but can't release.

### Subcommand-named methods

Redis commands like `CLIENT`, `OBJECT`, `CONFIG`, `CLUSTER`, `MEMORY`, `SCRIPT`, `FUNCTION` have many subcommands. Clients expose them with underscore-separated method names that mask the subcommand structure:

| Method | Wire-level command |
|--------|--------------------|
| `r.client_setname("x")` (redis-py) | `CLIENT SETNAME x` |
| `r.client_getname()` | `CLIENT GETNAME` |
| `r.object_encoding(key)` | `OBJECT ENCODING key` |
| `r.config_get("maxmemory")` | `CONFIG GET maxmemory` |
| `r.config_set(...)` | `CONFIG SET` |
| `r.cluster_info()` | `CLUSTER INFO` |
| `r.memory_usage(key)` | `MEMORY USAGE key` |
| `r.script_load(script)` | `SCRIPT LOAD script` |

**ACL implication:** ACL granularity is at the top-level command. `+CLIENT` allows all `CLIENT` subcommands; for tighter scope, use `+CLIENT|SETNAME` syntax. Note that the top-level commands like `CONFIG`, `CLUSTER`, `MEMORY`, `DEBUG`, `ACL` are usually in `@admin` / `@dangerous` — be deliberate about granting them.

### Pipeline `exec()` may issue `MULTI` / `EXEC`

Most clients have a transactional-pipeline mode that wraps the buffered calls in `MULTI` and `EXEC`:

- **redis-py**: `r.pipeline()` defaults to `transaction=True` → wraps in `MULTI`/`EXEC`. Pass `transaction=False` for a plain pipeline.
- **ioredis**: `client.multi().exec()` is transactional. `client.pipeline().exec()` is non-transactional.
- **go-redis**: `rdb.TxPipeline()` is transactional. `rdb.Pipeline()` is non-transactional.

**ACL implication:** If transactional pipelines are used, the rule needs `MULTI`, `EXEC`, plus optionally `WATCH`/`UNWATCH`/`DISCARD` (the `@transaction` category covers them all). Non-transactional pipelines don't need this.

### Sentinel / Cluster client mode

When the application uses a Sentinel-aware client (`redis.sentinel.Sentinel`) or a Cluster-aware client (`new Redis.Cluster([...])`, `redis.NewClusterClient(...)`), the client itself issues `SENTINEL *` or `CLUSTER *` commands beyond what application code references.

**ACL implication:** These commands are typically `@admin` and should NOT be granted to application users — they're handled by infrastructure-level credentials. If the application code path doesn't explicitly call admin commands but uses a Sentinel/Cluster client, the application's ACL should still NOT include `+@admin` or `+SENTINEL`/`+CLUSTER`.

### Sharded pub/sub on Redis Cluster

On Redis Cluster, sharded pub/sub uses `SSUBSCRIBE`/`SUNSUBSCRIBE`/`SPUBLISH` (Redis 7+) which is shard-local rather than cluster-wide. Some clients switch transparently when the connection is to a cluster.

**ACL implication:** Grant `+@pubsub` (covers all pub/sub variants) rather than individual `+SUBSCRIBE` if cluster mode is involved.

### Scan iterators

Helpers like `r.scan_iter(match="user:*")` (redis-py), `client.scanStream(...)` (ioredis), and `rdb.Scan(ctx, ...).Iterator()` (go-redis) issue multiple `SCAN` calls in a loop.

**ACL implication:** `+SCAN` is sufficient; the iteration is client-side. This case is mentioned for completeness — it's not actually a convention break.

---

## For absolute certainty: `MONITOR`

When the agent cannot be confident in a method-to-command mapping — or when the user wants to verify before locking in a rule — the authoritative answer is **`MONITOR`**, Redis's built-in command-stream debugger.

Workflow (manual today):

1. Connect a `redis-cli` client to a **test instance** of Redis (never production — `MONITOR` is very chatty)
2. Run `MONITOR` in that client
3. Execute the service code path in question
4. Observe the actual wire-level commands

v1 of the plugin doesn't automate this. **Future work**: with the Redis MCP connected, the agent could run `MONITOR` itself against a user-specified test target while the user triggers the code path, capture the command stream, and use it to disambiguate the flagged calls. That'd close the loop on "can this be known with absolute certainty without reviewing source code." For now: ask, flag, suggest `MONITOR`.

---

## When the client isn't covered here

For Java (`jedis`, `lettuce`), Rust (`redis-rs`, `fred`), .NET (`StackExchange.Redis`), Ruby (`redis-rb`), PHP (`predis`, `phpredis`), the typical convention holds: method name (case-normalized) = Redis command. When in doubt, ASK the user — a 30-second clarification is cheaper than an incorrect rule.
