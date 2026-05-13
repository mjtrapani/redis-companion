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

## When the client isn't covered here

For Java (`jedis`, `lettuce`), Rust (`redis-rs`, `fred`), .NET (`StackExchange.Redis`), Ruby (`redis-rb`), PHP (`predis`, `phpredis`), the typical convention holds: method name (case-normalized) = Redis command. When in doubt, ASK the user — a 30-second clarification is cheaper than an incorrect rule.
