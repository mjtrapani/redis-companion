# Command-category map

Reference mapping of Redis commands to ACL categories. Structured **category → commands** so the >50% category-collapse rule is a direct count.

> ⚠️ **`ACL CAT @<category>` against the live server is the authoritative source** — it reflects the target's actual Redis version *and* loaded modules. This document is a fallback for degraded mode (no MCP connection) and a sanity check. When falling back to this map, surface a *"version drift possible — connect MCP for live verification"* note.

Counts and lists are accurate for **Redis 7.x core** (no modules loaded) unless otherwise noted. See `version-deltas.md` for what changes across Redis 6 / 7 / 8.

---

## Standard categories

### `@keyspace`

Commands that operate on keys — manage their existence, expiry, or metadata.

**Commands (Redis 7.x, ~25):**

`DEL`, `UNLINK`, `EXISTS`, `EXPIRE`, `EXPIREAT`, `PEXPIRE`, `PEXPIREAT`, `EXPIRETIME`, `PEXPIRETIME`, `PERSIST`, `TTL`, `PTTL`, `KEYS`, `MOVE`, `COPY`, `OBJECT`, `RENAME`, `RENAMENX`, `RANDOMKEY`, `SCAN`, `TYPE`, `WAIT`, `WAITAOF`, `DUMP`, `RESTORE`, `TOUCH`, `MIGRATE`, `DBSIZE`

> Several of these (`KEYS`, `MIGRATE`, `OBJECT`, `MOVE`) are also `@dangerous` — they overlap categories.

### `@read`

Commands that read data without modifying it.

**Commands (Redis 7.x, ~55):**

`GET`, `GETRANGE`, `GETBIT`, `MGET`, `EXISTS`, `STRLEN`, `SUBSTR`, `TYPE`, `KEYS`, `SCAN`, `TTL`, `PTTL`, `EXPIRETIME`, `PEXPIRETIME`, `DBSIZE`, `RANDOMKEY`, `OBJECT`, `DUMP`, `TOUCH`,
`HGET`, `HMGET`, `HGETALL`, `HEXISTS`, `HKEYS`, `HVALS`, `HLEN`, `HSTRLEN`, `HSCAN`, `HRANDFIELD`,
`LRANGE`, `LLEN`, `LINDEX`, `LPOS`,
`SISMEMBER`, `SMISMEMBER`, `SMEMBERS`, `SCARD`, `SUNION`, `SINTER`, `SINTERCARD`, `SDIFF`, `SRANDMEMBER`, `SSCAN`,
`ZRANGE`, `ZRANGEBYSCORE`, `ZRANGEBYLEX`, `ZREVRANGE`, `ZREVRANGEBYSCORE`, `ZREVRANGEBYLEX`, `ZRANK`, `ZREVRANK`, `ZSCORE`, `ZMSCORE`, `ZCARD`, `ZCOUNT`, `ZLEXCOUNT`, `ZRANDMEMBER`, `ZSCAN`, `ZUNION`, `ZINTER`, `ZINTERCARD`, `ZDIFF`,
`BITCOUNT`, `BITPOS`, `BITFIELD_RO`,
`GEODIST`, `GEOPOS`, `GEOHASH`, `GEORADIUS_RO`, `GEORADIUSBYMEMBER_RO`, `GEOSEARCH`,
`XLEN`, `XRANGE`, `XREVRANGE`, `XREAD`, `XINFO`, `XPENDING`,
`PFCOUNT`,
`LCS`, `GETEX`

### `@write`

Commands that modify data.

**Commands (Redis 7.x, ~85):**

`SET`, `SETNX`, `SETEX`, `PSETEX`, `MSET`, `MSETNX`, `APPEND`, `INCR`, `INCRBY`, `INCRBYFLOAT`, `DECR`, `DECRBY`, `GETSET`, `GETEX`, `GETDEL`, `SETRANGE`, `SETBIT`, `BITFIELD`, `BITOP`,
`DEL`, `UNLINK`, `EXPIRE`, `EXPIREAT`, `PEXPIRE`, `PEXPIREAT`, `PERSIST`, `RENAME`, `RENAMENX`, `COPY`, `MOVE`, `RESTORE`,
`HSET`, `HMSET`, `HSETNX`, `HDEL`, `HINCRBY`, `HINCRBYFLOAT`,
`LPUSH`, `LPUSHX`, `RPUSH`, `RPUSHX`, `LPOP`, `RPOP`, `LMPOP`, `LINSERT`, `LSET`, `LREM`, `LTRIM`, `LMOVE`, `RPOPLPUSH`,
`SADD`, `SREM`, `SPOP`, `SMOVE`, `SUNIONSTORE`, `SINTERSTORE`, `SDIFFSTORE`,
`ZADD`, `ZREM`, `ZINCRBY`, `ZPOPMIN`, `ZPOPMAX`, `ZMPOP`, `ZREMRANGEBYRANK`, `ZREMRANGEBYSCORE`, `ZREMRANGEBYLEX`, `ZUNIONSTORE`, `ZINTERSTORE`, `ZDIFFSTORE`, `ZRANGESTORE`,
`GEOADD`, `GEORADIUS`, `GEORADIUSBYMEMBER`, `GEOSEARCHSTORE`,
`XADD`, `XDEL`, `XTRIM`, `XGROUP`, `XACK`, `XCLAIM`, `XAUTOCLAIM`, `XSETID`,
`PFADD`, `PFMERGE`,
`FLUSHDB`, `FLUSHALL`,
`SORT`, `SORT_RO`

> `FLUSHDB`/`FLUSHALL` are also `@dangerous` — they overlap. If the user wants to deny destructive writes, `-@dangerous` is the typical defense.

### `@string`

String data-type operations.

**Commands (Redis 7.x, ~25):**

`SET`, `GET`, `SETEX`, `PSETEX`, `SETNX`, `MSET`, `MSETNX`, `MGET`, `GETSET`, `GETEX`, `GETDEL`, `APPEND`, `STRLEN`, `SUBSTR`, `GETRANGE`, `SETRANGE`, `INCR`, `INCRBY`, `INCRBYFLOAT`, `DECR`, `DECRBY`, `LCS`

### `@hash`

Hash data-type operations.

**Commands (Redis 7.x, ~17):**

`HSET`, `HGET`, `HMSET`, `HMGET`, `HSETNX`, `HEXISTS`, `HDEL`, `HLEN`, `HSTRLEN`, `HKEYS`, `HVALS`, `HGETALL`, `HRANDFIELD`, `HINCRBY`, `HINCRBYFLOAT`, `HSCAN`, `HEXPIRE` (7.4+), `HPERSIST` (7.4+), `HTTL` (7.4+)

### `@list`

List data-type operations.

**Commands (Redis 7.x, ~24):**

`LPUSH`, `LPUSHX`, `RPUSH`, `RPUSHX`, `LPOP`, `RPOP`, `LMPOP`, `BLPOP`, `BRPOP`, `BLMPOP`, `LLEN`, `LRANGE`, `LINDEX`, `LSET`, `LINSERT`, `LREM`, `LTRIM`, `LPOS`, `LMOVE`, `BLMOVE`, `RPOPLPUSH`, `BRPOPLPUSH`

### `@set`

Unordered-set data-type operations.

**Commands (Redis 7.x, ~17):**

`SADD`, `SREM`, `SCARD`, `SMEMBERS`, `SISMEMBER`, `SMISMEMBER`, `SRANDMEMBER`, `SPOP`, `SMOVE`, `SUNION`, `SUNIONSTORE`, `SINTER`, `SINTERSTORE`, `SINTERCARD`, `SDIFF`, `SDIFFSTORE`, `SSCAN`

### `@sortedset`

Sorted-set data-type operations.

**Commands (Redis 7.x, ~36):**

`ZADD`, `ZREM`, `ZSCORE`, `ZMSCORE`, `ZINCRBY`, `ZRANGE`, `ZREVRANGE`, `ZRANGEBYSCORE`, `ZREVRANGEBYSCORE`, `ZRANGEBYLEX`, `ZREVRANGEBYLEX`, `ZRANGESTORE`, `ZRANK`, `ZREVRANK`, `ZCARD`, `ZCOUNT`, `ZLEXCOUNT`, `ZUNION`, `ZUNIONSTORE`, `ZINTER`, `ZINTERSTORE`, `ZINTERCARD`, `ZDIFF`, `ZDIFFSTORE`, `ZPOPMIN`, `ZPOPMAX`, `BZPOPMIN`, `BZPOPMAX`, `ZMPOP`, `BZMPOP`, `ZREMRANGEBYRANK`, `ZREMRANGEBYSCORE`, `ZREMRANGEBYLEX`, `ZSCAN`, `ZRANDMEMBER`

### `@bitmap`

Bitmap operations on string values.

**Commands (Redis 7.x, ~7):**

`SETBIT`, `GETBIT`, `BITCOUNT`, `BITOP`, `BITPOS`, `BITFIELD`, `BITFIELD_RO`

### `@hyperloglog`

HyperLogLog cardinality estimation.

**Commands (Redis 7.x, 3):**

`PFADD`, `PFCOUNT`, `PFMERGE`

### `@geo`

Geospatial operations.

**Commands (Redis 7.x, ~10):**

`GEOADD`, `GEODIST`, `GEOHASH`, `GEOPOS`, `GEORADIUS`, `GEORADIUS_RO`, `GEORADIUSBYMEMBER`, `GEORADIUSBYMEMBER_RO`, `GEOSEARCH`, `GEOSEARCHSTORE`

### `@stream`

Redis Stream operations.

**Commands (Redis 7.x, ~16):**

`XADD`, `XLEN`, `XREAD`, `XREADGROUP`, `XRANGE`, `XREVRANGE`, `XINFO`, `XDEL`, `XTRIM`, `XGROUP`, `XACK`, `XCLAIM`, `XAUTOCLAIM`, `XSETID`, `XPENDING`

### `@pubsub`

Publish-subscribe and sharded pub/sub.

**Commands (Redis 7.x, ~9):**

`PUBLISH`, `SUBSCRIBE`, `UNSUBSCRIBE`, `PSUBSCRIBE`, `PUNSUBSCRIBE`, `PUBSUB`, `SSUBSCRIBE` (7.0+), `SUNSUBSCRIBE` (7.0+), `SPUBLISH` (7.0+)

> ⚠️ Recent Redis defaults to **restrictive** pub/sub — any service that publishes or subscribes must have an `&channel-pattern` clause in its rule.

### `@connection`

Connection lifecycle, authentication, and session-level commands.

**Commands (Redis 7.x, ~14):**

`AUTH`, `HELLO`, `CLIENT`, `PING`, `ECHO`, `QUIT`, `SELECT`, `RESET`, `CLIENT GETNAME`, `CLIENT SETNAME`, `CLIENT LIST`, `CLIENT INFO`, `CLIENT NO-EVICT`, `CLIENT NO-TOUCH`

> `CLIENT` is one command with many subcommands; the ACL `@connection` grant covers most subcommands except those flagged `@admin`/`@dangerous` (e.g., `CLIENT KILL`, `CLIENT PAUSE`).

### `@transaction`

MULTI/EXEC transaction primitives.

**Commands (Redis 7.x, 5):**

`MULTI`, `EXEC`, `DISCARD`, `WATCH`, `UNWATCH`

### `@scripting` (Redis 7+ — new category)

Server-side scripting (Lua and Redis Functions).

**Commands (Redis 7.x, ~16):**

`EVAL`, `EVALSHA`, `EVAL_RO`, `EVALSHA_RO`, `SCRIPT LOAD`, `SCRIPT EXISTS`, `SCRIPT FLUSH`, `SCRIPT DEBUG`, `FCALL`, `FCALL_RO`, `FUNCTION LOAD`, `FUNCTION DUMP`, `FUNCTION RESTORE`, `FUNCTION FLUSH`, `FUNCTION LIST`, `FUNCTION STATS`, `FUNCTION DELETE`

> **In Redis 6**, scripting commands were bundled into `@write`. If you're synthesizing a rule for Redis 6, treat `EVAL`/`EVALSHA` as `@write` members and don't expect `+@scripting` to be available.

### `@admin`

Server administration. **Almost never granted to application users.**

**Commands (Redis 7.x, ~25):**

`REPLICAOF`, `SLAVEOF`, `CONFIG`, `DEBUG`, `SHUTDOWN`, `MONITOR`, `SAVE`, `BGSAVE`, `BGREWRITEAOF`, `ACL`, `COMMAND`, `CLUSTER`, `FAILOVER`, `LATENCY`, `MODULE`, `SLOWLOG`, `MEMORY`, `LASTSAVE`, `ROLE`, `SWAPDB`, `RESET`, `REPLICATE`, `PSYNC`, `REPLCONF`, `SYNC`

### `@dangerous`

Commands with high blast radius. Frequently denied via `-@dangerous` even when granted positively via `+@write` or `+@admin`, so the rule body doesn't accidentally include them.

**Commands (Redis 7.x, ~30 — many overlap with `@admin`):**

`KEYS`, `FLUSHDB`, `FLUSHALL`, `MIGRATE`, `MOVE`, `RESTORE`, `DEBUG`, `MONITOR`, `CLIENT KILL`, `CLIENT PAUSE`, `CLIENT UNPAUSE`, `CLUSTER`, `CONFIG`, `DBSIZE`, `FAILOVER`, `LASTSAVE`, `LATENCY`, `MEMORY`, `MODULE`, `OBJECT`, `PSYNC`, `REPLCONF`, `REPLICAOF`, `SLAVEOF`, `RESET`, `SAVE`, `BGSAVE`, `BGREWRITEAOF`, `SHUTDOWN`, `SLOWLOG`, `SWAPDB`, `SYNC`, `WAIT`, `WAITAOF`, `WAITAOF`, `ACL` (overlap with @admin)

### `@blocking`

Commands that can block the client connection waiting for a value.

**Commands (Redis 7.x, ~12):**

`BLPOP`, `BRPOP`, `BLMOVE`, `BRPOPLPUSH`, `BLMPOP`, `BZPOPMIN`, `BZPOPMAX`, `BZMPOP`, `XREAD` (with `BLOCK`), `XREADGROUP` (with `BLOCK`), `WAIT`, `WAITAOF`, `CLIENT PAUSE` (blocks server)

> Note: `XREAD`/`XREADGROUP` are in `@blocking` only when called with the `BLOCK` argument. ACL grants them on a command basis (no per-argument granularity), so granting `+XREAD` includes blocking usage. For services that use blocking operations, the persona should know the call site can pause the client.

### `@fast`

Commands with O(1) or amortized-O(1) complexity (excluding network overhead).

Used primarily by infrastructure tooling (e.g., monitoring). Application rules rarely reference `@fast` directly; agent should not collapse to it.

### `@slow`

Commands with worse-than-O(log N) complexity. Includes most aggregations, set operations on large sets, and `KEYS`.

Used primarily by tooling. Application rules rarely reference `@slow` directly.

---

## Module categories

These categories **only exist on the live server if the corresponding module is loaded.** Common Enterprise / Redis Stack deployments load several. **Always verify via `ACL CAT @<module-category>` against the live server** — this section is a guide, not authoritative.

### `@json` (RedisJSON)

**Commands (typical):** `JSON.SET`, `JSON.GET`, `JSON.DEL`, `JSON.FORGET`, `JSON.MGET`, `JSON.MSET`, `JSON.NUMINCRBY`, `JSON.NUMMULTBY`, `JSON.STRAPPEND`, `JSON.STRLEN`, `JSON.ARRAPPEND`, `JSON.ARRINDEX`, `JSON.ARRINSERT`, `JSON.ARRLEN`, `JSON.ARRPOP`, `JSON.ARRTRIM`, `JSON.OBJKEYS`, `JSON.OBJLEN`, `JSON.RESP`, `JSON.TYPE`, `JSON.CLEAR`, `JSON.TOGGLE`, `JSON.DEBUG`

In Redis 8 core, JSON commands also contribute to `@read`/`@write` standard categories. On Redis 7 with RedisJSON loaded, they only appear in `@json`.

### `@search` (RediSearch)

**Commands (typical):** `FT.CREATE`, `FT.ALTER`, `FT.DROPINDEX`, `FT.SEARCH`, `FT.AGGREGATE`, `FT.PROFILE`, `FT.EXPLAIN`, `FT.EXPLAINCLI`, `FT.INFO`, `FT._LIST`, `FT.CONFIG`, `FT.SPELLCHECK`, `FT.DICTADD`, `FT.DICTDEL`, `FT.DICTDUMP`, `FT.SYNUPDATE`, `FT.SYNDUMP`, `FT.SUGADD`, `FT.SUGGET`, `FT.SUGDEL`, `FT.SUGLEN`, `FT.TAGVALS`, `FT.MGET`, `FT.CURSOR`

### `@timeseries` (RedisTimeSeries)

**Commands (typical):** `TS.CREATE`, `TS.ALTER`, `TS.DEL`, `TS.ADD`, `TS.MADD`, `TS.INCRBY`, `TS.DECRBY`, `TS.CREATERULE`, `TS.DELETERULE`, `TS.RANGE`, `TS.REVRANGE`, `TS.MRANGE`, `TS.MREVRANGE`, `TS.GET`, `TS.MGET`, `TS.INFO`, `TS.QUERYINDEX`

### `@bf` (RedisBloom — Bloom Filters)

**Commands (typical):** `BF.RESERVE`, `BF.ADD`, `BF.MADD`, `BF.INSERT`, `BF.EXISTS`, `BF.MEXISTS`, `BF.SCANDUMP`, `BF.LOADCHUNK`, `BF.INFO`, `BF.CARD`

### `@cf` (RedisBloom — Cuckoo Filters)

**Commands (typical):** `CF.RESERVE`, `CF.ADD`, `CF.ADDNX`, `CF.INSERT`, `CF.INSERTNX`, `CF.EXISTS`, `CF.MEXISTS`, `CF.DEL`, `CF.COUNT`, `CF.SCANDUMP`, `CF.LOADCHUNK`, `CF.INFO`

### `@cms` (RedisBloom — Count-Min Sketch)

**Commands (typical):** `CMS.INITBYDIM`, `CMS.INITBYPROB`, `CMS.INCRBY`, `CMS.QUERY`, `CMS.MERGE`, `CMS.INFO`

### `@topk` (RedisBloom — Top-K)

**Commands (typical):** `TOPK.RESERVE`, `TOPK.ADD`, `TOPK.INCRBY`, `TOPK.QUERY`, `TOPK.COUNT`, `TOPK.LIST`, `TOPK.INFO`

### `@tdigest` (RedisBloom — t-digest)

**Commands (typical):** `TDIGEST.CREATE`, `TDIGEST.RESET`, `TDIGEST.ADD`, `TDIGEST.MERGE`, `TDIGEST.MIN`, `TDIGEST.MAX`, `TDIGEST.QUANTILE`, `TDIGEST.CDF`, `TDIGEST.TRIMMED_MEAN`, `TDIGEST.RANK`, `TDIGEST.REVRANK`, `TDIGEST.INFO`

### `@graph` (RedisGraph — deprecated)

RedisGraph reached end-of-life in early 2024. If a deployment still loads it, commands include `GRAPH.QUERY`, `GRAPH.RO_QUERY`, `GRAPH.PROFILE`, `GRAPH.EXPLAIN`, `GRAPH.DELETE`, `GRAPH.LIST`, `GRAPH.CONFIG`, `GRAPH.SLOWLOG`. Avoid recommending `@graph` for new rules.

---

## Notes for the >50% rule

When deciding whether to collapse `+CMD1 +CMD2 +CMD3` to `+@category`:

1. **Count what's in the category live**: prefer `ACL CAT @<category>` over this map.
2. **Count what the service uses** in that category (from the discovery phase).
3. **If used / total > 50%**: this is a collapse opportunity → ask the user (per `acl-generator` step 3).
4. **Else**: emit individual command grants.

Some commands appear in **multiple categories** (e.g., `XADD` is in both `@write` and `@stream`). Count each category independently — a service using `XADD` contributes 1 to `@write`'s usage and 1 to `@stream`'s usage.

---

## When this map is wrong, fix it

This document is approximate. If a deployment's live `ACL CAT @<category>` differs materially from what's here — especially on Redis 8 or with modules loaded — trust the live answer. The map exists for offline reasoning when MCP isn't available.
