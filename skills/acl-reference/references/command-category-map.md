# Command-category map

> **Generated from [redis/redis@8.6.3](https://github.com/redis/redis/tree/8.6.3/src/commands).** Run `scripts/build-category-map.py` to regenerate from a newer Redis release.
>
> Each command's ACL category membership is derived from upstream `acl_categories` (explicit, e.g., `STRING`→`@string`) and `command_flags` (`READONLY`→`@read`, `WRITE`→`@write`, `ADMIN`→`@admin`, `BLOCKING`→`@blocking`, `FAST`→`@fast`; everything not `@fast` is `@slow`).
>
> **422 commands** total (core Redis 8.6.3, no modules — see SUBMISSION_NOTE.md item #4 for module coverage as future work).
>
> The **Since** column shows the Redis version that introduced each command. The agent uses this to filter for the target version: a command with `Since: 7.0.0` is unavailable on Redis 6.x. **Cross-version category re-classifications** (e.g., `EVAL` moved from `@write` to `@scripting` in Redis 7.0) are documented in `version-deltas.md` and applied on top of this map.

---

## `@keyspace`

**36 commands** (Redis 8.6.3 — `Since: <X.Y.Z>` filters for older targets).

| Command | Since |
|---------|-------|
| `COPY` | 6.2.0 |
| `DBSIZE` | 1.0.0 |
| `DEL` | 1.0.0 |
| `DUMP` | 2.6.0 |
| `EXISTS` | 1.0.0 |
| `EXPIRE` | 1.0.0 |
| `EXPIREAT` | 1.2.0 |
| `EXPIRETIME` | 7.0.0 |
| `FLUSHALL` | 1.0.0 |
| `FLUSHDB` | 1.0.0 |
| `KEYS` | 1.0.0 |
| `MIGRATE` | 2.6.0 |
| `MOVE` | 1.0.0 |
| `OBJECT ENCODING` | 2.2.3 |
| `OBJECT FREQ` | 4.0.0 |
| `OBJECT HELP` | 6.2.0 |
| `OBJECT IDLETIME` | 2.2.3 |
| `OBJECT REFCOUNT` | 2.2.3 |
| `PERSIST` | 2.2.0 |
| `PEXPIRE` | 2.6.0 |
| `PEXPIREAT` | 2.6.0 |
| `PEXPIRETIME` | 7.0.0 |
| `PTTL` | 2.6.0 |
| `RANDOMKEY` | 1.0.0 |
| `RENAME` | 1.0.0 |
| `RENAMENX` | 1.0.0 |
| `RESTORE` | 2.6.0 |
| `RESTORE-ASKING` | 3.0.0 |
| `SCAN` | 2.8.0 |
| `SFLUSH` | 8.0.0 |
| `SWAPDB` | 4.0.0 |
| `TOUCH` | 3.2.1 |
| `TRIMSLOTS` | 8.4.0 |
| `TTL` | 1.0.0 |
| `TYPE` | 1.0.0 |
| `UNLINK` | 4.0.0 |

## `@read`

**95 commands** (Redis 8.6.3 — `Since: <X.Y.Z>` filters for older targets).

| Command | Since |
|---------|-------|
| `BITCOUNT` | 2.6.0 |
| `BITFIELD_RO` | 6.0.0 |
| `BITPOS` | 2.8.7 |
| `DBSIZE` | 1.0.0 |
| `DIGEST` | 8.4.0 |
| `DUMP` | 2.6.0 |
| `EVALSHA_RO` | 7.0.0 |
| `EVAL_RO` | 7.0.0 |
| `EXISTS` | 1.0.0 |
| `EXPIRETIME` | 7.0.0 |
| `FCALL_RO` | 7.0.0 |
| `GEODIST` | 3.2.0 |
| `GEOHASH` | 3.2.0 |
| `GEOPOS` | 3.2.0 |
| `GEORADIUSBYMEMBER_RO` | 3.2.10 |
| `GEORADIUS_RO` | 3.2.10 |
| `GEOSEARCH` | 6.2.0 |
| `GET` | 1.0.0 |
| `GETBIT` | 2.2.0 |
| `GETRANGE` | 2.4.0 |
| `HEXISTS` | 2.0.0 |
| `HEXPIRETIME` | 7.4.0 |
| `HGET` | 2.0.0 |
| `HGETALL` | 2.0.0 |
| `HKEYS` | 2.0.0 |
| `HLEN` | 2.0.0 |
| `HMGET` | 2.0.0 |
| `HPEXPIRETIME` | 7.4.0 |
| `HPTTL` | 7.4.0 |
| `HRANDFIELD` | 6.2.0 |
| `HSCAN` | 2.8.0 |
| `HSTRLEN` | 3.2.0 |
| `HTTL` | 7.4.0 |
| `HVALS` | 2.0.0 |
| `KEYS` | 1.0.0 |
| `LCS` | 7.0.0 |
| `LINDEX` | 1.0.0 |
| `LLEN` | 1.0.0 |
| `LOLWUT` | 5.0.0 |
| `LPOS` | 6.0.6 |
| `LRANGE` | 1.0.0 |
| `MEMORY USAGE` | 4.0.0 |
| `MGET` | 1.0.0 |
| `OBJECT ENCODING` | 2.2.3 |
| `OBJECT FREQ` | 4.0.0 |
| `OBJECT IDLETIME` | 2.2.3 |
| `OBJECT REFCOUNT` | 2.2.3 |
| `PEXPIRETIME` | 7.0.0 |
| `PFCOUNT` | 2.8.9 |
| `PTTL` | 2.6.0 |
| `RANDOMKEY` | 1.0.0 |
| `SCAN` | 2.8.0 |
| `SCARD` | 1.0.0 |
| `SDIFF` | 1.0.0 |
| `SINTER` | 1.0.0 |
| `SINTERCARD` | 7.0.0 |
| `SISMEMBER` | 1.0.0 |
| `SMEMBERS` | 1.0.0 |
| `SMISMEMBER` | 6.2.0 |
| `SORT_RO` | 7.0.0 |
| `SRANDMEMBER` | 1.0.0 |
| `SSCAN` | 2.8.0 |
| `STRLEN` | 2.2.0 |
| `SUBSTR` | 1.0.0 |
| `SUNION` | 1.0.0 |
| `TOUCH` | 3.2.1 |
| `TTL` | 1.0.0 |
| `TYPE` | 1.0.0 |
| `XINFO CONSUMERS` | 5.0.0 |
| `XINFO GROUPS` | 5.0.0 |
| `XINFO STREAM` | 5.0.0 |
| `XLEN` | 5.0.0 |
| `XPENDING` | 5.0.0 |
| `XRANGE` | 5.0.0 |
| `XREAD` | 5.0.0 |
| `XREVRANGE` | 5.0.0 |
| `ZCARD` | 1.2.0 |
| `ZCOUNT` | 2.0.0 |
| `ZDIFF` | 6.2.0 |
| `ZINTER` | 6.2.0 |
| `ZINTERCARD` | 7.0.0 |
| `ZLEXCOUNT` | 2.8.9 |
| `ZMSCORE` | 6.2.0 |
| `ZRANDMEMBER` | 6.2.0 |
| `ZRANGE` | 1.2.0 |
| `ZRANGEBYLEX` | 2.8.9 |
| `ZRANGEBYSCORE` | 1.0.5 |
| `ZRANK` | 2.0.0 |
| `ZREVRANGE` | 1.2.0 |
| `ZREVRANGEBYLEX` | 2.8.9 |
| `ZREVRANGEBYSCORE` | 2.2.0 |
| `ZREVRANK` | 2.0.0 |
| `ZSCAN` | 2.8.0 |
| `ZSCORE` | 1.2.0 |
| `ZUNION` | 6.2.0 |

## `@write`

**124 commands** (Redis 8.6.3 — `Since: <X.Y.Z>` filters for older targets).

| Command | Since |
|---------|-------|
| `APPEND` | 2.0.0 |
| `BITFIELD` | 3.2.0 |
| `BITOP` | 2.6.0 |
| `BLMOVE` | 6.2.0 |
| `BLMPOP` | 7.0.0 |
| `BLPOP` | 2.0.0 |
| `BRPOP` | 2.0.0 |
| `BRPOPLPUSH` | 2.2.0 |
| `BZMPOP` | 7.0.0 |
| `BZPOPMAX` | 5.0.0 |
| `BZPOPMIN` | 5.0.0 |
| `COPY` | 6.2.0 |
| `DECR` | 1.0.0 |
| `DECRBY` | 1.0.0 |
| `DEL` | 1.0.0 |
| `DELEX` | 8.4.0 |
| `EXPIRE` | 1.0.0 |
| `EXPIREAT` | 1.2.0 |
| `FLUSHALL` | 1.0.0 |
| `FLUSHDB` | 1.0.0 |
| `FUNCTION DELETE` | 7.0.0 |
| `FUNCTION FLUSH` | 7.0.0 |
| `FUNCTION LOAD` | 7.0.0 |
| `FUNCTION RESTORE` | 7.0.0 |
| `GEOADD` | 3.2.0 |
| `GEORADIUS` | 3.2.0 |
| `GEORADIUSBYMEMBER` | 3.2.0 |
| `GEOSEARCHSTORE` | 6.2.0 |
| `GETDEL` | 6.2.0 |
| `GETEX` | 6.2.0 |
| `GETSET` | 1.0.0 |
| `HDEL` | 2.0.0 |
| `HEXPIRE` | 7.4.0 |
| `HEXPIREAT` | 7.4.0 |
| `HGETDEL` | 8.0.0 |
| `HGETEX` | 8.0.0 |
| `HINCRBY` | 2.0.0 |
| `HINCRBYFLOAT` | 2.6.0 |
| `HMSET` | 2.0.0 |
| `HPERSIST` | 7.4.0 |
| `HPEXPIRE` | 7.4.0 |
| `HPEXPIREAT` | 7.4.0 |
| `HSET` | 2.0.0 |
| `HSETEX` | 8.0.0 |
| `HSETNX` | 2.0.0 |
| `INCR` | 1.0.0 |
| `INCRBY` | 1.0.0 |
| `INCRBYFLOAT` | 2.6.0 |
| `LINSERT` | 2.2.0 |
| `LMOVE` | 6.2.0 |
| `LMPOP` | 7.0.0 |
| `LPOP` | 1.0.0 |
| `LPUSH` | 1.0.0 |
| `LPUSHX` | 2.2.0 |
| `LREM` | 1.0.0 |
| `LSET` | 1.0.0 |
| `LTRIM` | 1.0.0 |
| `MIGRATE` | 2.6.0 |
| `MOVE` | 1.0.0 |
| `MSET` | 1.0.1 |
| `MSETEX` | 8.4.0 |
| `MSETNX` | 1.0.1 |
| `PERSIST` | 2.2.0 |
| `PEXPIRE` | 2.6.0 |
| `PEXPIREAT` | 2.6.0 |
| `PFADD` | 2.8.9 |
| `PFDEBUG` | 2.8.9 |
| `PFMERGE` | 2.8.9 |
| `PSETEX` | 2.6.0 |
| `RENAME` | 1.0.0 |
| `RENAMENX` | 1.0.0 |
| `RESTORE` | 2.6.0 |
| `RESTORE-ASKING` | 3.0.0 |
| `RPOP` | 1.0.0 |
| `RPOPLPUSH` | 1.2.0 |
| `RPUSH` | 1.0.0 |
| `RPUSHX` | 2.2.0 |
| `SADD` | 1.0.0 |
| `SDIFFSTORE` | 1.0.0 |
| `SET` | 1.0.0 |
| `SETBIT` | 2.2.0 |
| `SETEX` | 2.0.0 |
| `SETNX` | 1.0.0 |
| `SETRANGE` | 2.2.0 |
| `SFLUSH` | 8.0.0 |
| `SINTERSTORE` | 1.0.0 |
| `SMOVE` | 1.0.0 |
| `SORT` | 1.0.0 |
| `SPOP` | 1.0.0 |
| `SREM` | 1.0.0 |
| `SUNIONSTORE` | 1.0.0 |
| `SWAPDB` | 4.0.0 |
| `TRIMSLOTS` | 8.4.0 |
| `UNLINK` | 4.0.0 |
| `XACK` | 5.0.0 |
| `XACKDEL` | 8.2.0 |
| `XADD` | 5.0.0 |
| `XAUTOCLAIM` | 6.2.0 |
| `XCFGSET` | 8.6.0 |
| `XCLAIM` | 5.0.0 |
| `XDEL` | 5.0.0 |
| `XDELEX` | 8.2.0 |
| `XGROUP CREATE` | 5.0.0 |
| `XGROUP CREATECONSUMER` | 6.2.0 |
| `XGROUP DELCONSUMER` | 5.0.0 |
| `XGROUP DESTROY` | 5.0.0 |
| `XGROUP SETID` | 5.0.0 |
| `XIDMPRECORD` | 8.6.2 |
| `XREADGROUP` | 5.0.0 |
| `XSETID` | 5.0.0 |
| `XTRIM` | 5.0.0 |
| `ZADD` | 1.2.0 |
| `ZDIFFSTORE` | 6.2.0 |
| `ZINCRBY` | 1.2.0 |
| `ZINTERSTORE` | 2.0.0 |
| `ZMPOP` | 7.0.0 |
| `ZPOPMAX` | 5.0.0 |
| `ZPOPMIN` | 5.0.0 |
| `ZRANGESTORE` | 6.2.0 |
| `ZREM` | 1.2.0 |
| `ZREMRANGEBYLEX` | 2.8.9 |
| `ZREMRANGEBYRANK` | 2.0.0 |
| `ZREMRANGEBYSCORE` | 1.2.0 |
| `ZUNIONSTORE` | 2.0.0 |

## `@string`

**25 commands** (Redis 8.6.3 — `Since: <X.Y.Z>` filters for older targets).

| Command | Since |
|---------|-------|
| `APPEND` | 2.0.0 |
| `DECR` | 1.0.0 |
| `DECRBY` | 1.0.0 |
| `DELEX` | 8.4.0 |
| `DIGEST` | 8.4.0 |
| `GET` | 1.0.0 |
| `GETDEL` | 6.2.0 |
| `GETEX` | 6.2.0 |
| `GETRANGE` | 2.4.0 |
| `GETSET` | 1.0.0 |
| `INCR` | 1.0.0 |
| `INCRBY` | 1.0.0 |
| `INCRBYFLOAT` | 2.6.0 |
| `LCS` | 7.0.0 |
| `MGET` | 1.0.0 |
| `MSET` | 1.0.1 |
| `MSETEX` | 8.4.0 |
| `MSETNX` | 1.0.1 |
| `PSETEX` | 2.6.0 |
| `SET` | 1.0.0 |
| `SETEX` | 2.0.0 |
| `SETNX` | 1.0.0 |
| `SETRANGE` | 2.2.0 |
| `STRLEN` | 2.2.0 |
| `SUBSTR` | 1.0.0 |

## `@hash`

**28 commands** (Redis 8.6.3 — `Since: <X.Y.Z>` filters for older targets).

| Command | Since |
|---------|-------|
| `HDEL` | 2.0.0 |
| `HEXISTS` | 2.0.0 |
| `HEXPIRE` | 7.4.0 |
| `HEXPIREAT` | 7.4.0 |
| `HEXPIRETIME` | 7.4.0 |
| `HGET` | 2.0.0 |
| `HGETALL` | 2.0.0 |
| `HGETDEL` | 8.0.0 |
| `HGETEX` | 8.0.0 |
| `HINCRBY` | 2.0.0 |
| `HINCRBYFLOAT` | 2.6.0 |
| `HKEYS` | 2.0.0 |
| `HLEN` | 2.0.0 |
| `HMGET` | 2.0.0 |
| `HMSET` | 2.0.0 |
| `HPERSIST` | 7.4.0 |
| `HPEXPIRE` | 7.4.0 |
| `HPEXPIREAT` | 7.4.0 |
| `HPEXPIRETIME` | 7.4.0 |
| `HPTTL` | 7.4.0 |
| `HRANDFIELD` | 6.2.0 |
| `HSCAN` | 2.8.0 |
| `HSET` | 2.0.0 |
| `HSETEX` | 8.0.0 |
| `HSETNX` | 2.0.0 |
| `HSTRLEN` | 3.2.0 |
| `HTTL` | 7.4.0 |
| `HVALS` | 2.0.0 |

## `@list`

**24 commands** (Redis 8.6.3 — `Since: <X.Y.Z>` filters for older targets).

| Command | Since |
|---------|-------|
| `BLMOVE` | 6.2.0 |
| `BLMPOP` | 7.0.0 |
| `BLPOP` | 2.0.0 |
| `BRPOP` | 2.0.0 |
| `BRPOPLPUSH` | 2.2.0 |
| `LINDEX` | 1.0.0 |
| `LINSERT` | 2.2.0 |
| `LLEN` | 1.0.0 |
| `LMOVE` | 6.2.0 |
| `LMPOP` | 7.0.0 |
| `LPOP` | 1.0.0 |
| `LPOS` | 6.0.6 |
| `LPUSH` | 1.0.0 |
| `LPUSHX` | 2.2.0 |
| `LRANGE` | 1.0.0 |
| `LREM` | 1.0.0 |
| `LSET` | 1.0.0 |
| `LTRIM` | 1.0.0 |
| `RPOP` | 1.0.0 |
| `RPOPLPUSH` | 1.2.0 |
| `RPUSH` | 1.0.0 |
| `RPUSHX` | 2.2.0 |
| `SORT` | 1.0.0 |
| `SORT_RO` | 7.0.0 |

## `@set`

**19 commands** (Redis 8.6.3 — `Since: <X.Y.Z>` filters for older targets).

| Command | Since |
|---------|-------|
| `SADD` | 1.0.0 |
| `SCARD` | 1.0.0 |
| `SDIFF` | 1.0.0 |
| `SDIFFSTORE` | 1.0.0 |
| `SINTER` | 1.0.0 |
| `SINTERCARD` | 7.0.0 |
| `SINTERSTORE` | 1.0.0 |
| `SISMEMBER` | 1.0.0 |
| `SMEMBERS` | 1.0.0 |
| `SMISMEMBER` | 6.2.0 |
| `SMOVE` | 1.0.0 |
| `SORT` | 1.0.0 |
| `SORT_RO` | 7.0.0 |
| `SPOP` | 1.0.0 |
| `SRANDMEMBER` | 1.0.0 |
| `SREM` | 1.0.0 |
| `SSCAN` | 2.8.0 |
| `SUNION` | 1.0.0 |
| `SUNIONSTORE` | 1.0.0 |

## `@sortedset`

**37 commands** (Redis 8.6.3 — `Since: <X.Y.Z>` filters for older targets).

| Command | Since |
|---------|-------|
| `BZMPOP` | 7.0.0 |
| `BZPOPMAX` | 5.0.0 |
| `BZPOPMIN` | 5.0.0 |
| `SORT` | 1.0.0 |
| `SORT_RO` | 7.0.0 |
| `ZADD` | 1.2.0 |
| `ZCARD` | 1.2.0 |
| `ZCOUNT` | 2.0.0 |
| `ZDIFF` | 6.2.0 |
| `ZDIFFSTORE` | 6.2.0 |
| `ZINCRBY` | 1.2.0 |
| `ZINTER` | 6.2.0 |
| `ZINTERCARD` | 7.0.0 |
| `ZINTERSTORE` | 2.0.0 |
| `ZLEXCOUNT` | 2.8.9 |
| `ZMPOP` | 7.0.0 |
| `ZMSCORE` | 6.2.0 |
| `ZPOPMAX` | 5.0.0 |
| `ZPOPMIN` | 5.0.0 |
| `ZRANDMEMBER` | 6.2.0 |
| `ZRANGE` | 1.2.0 |
| `ZRANGEBYLEX` | 2.8.9 |
| `ZRANGEBYSCORE` | 1.0.5 |
| `ZRANGESTORE` | 6.2.0 |
| `ZRANK` | 2.0.0 |
| `ZREM` | 1.2.0 |
| `ZREMRANGEBYLEX` | 2.8.9 |
| `ZREMRANGEBYRANK` | 2.0.0 |
| `ZREMRANGEBYSCORE` | 1.2.0 |
| `ZREVRANGE` | 1.2.0 |
| `ZREVRANGEBYLEX` | 2.8.9 |
| `ZREVRANGEBYSCORE` | 2.2.0 |
| `ZREVRANK` | 2.0.0 |
| `ZSCAN` | 2.8.0 |
| `ZSCORE` | 1.2.0 |
| `ZUNION` | 6.2.0 |
| `ZUNIONSTORE` | 2.0.0 |

## `@bitmap`

**7 commands** (Redis 8.6.3 — `Since: <X.Y.Z>` filters for older targets).

| Command | Since |
|---------|-------|
| `BITCOUNT` | 2.6.0 |
| `BITFIELD` | 3.2.0 |
| `BITFIELD_RO` | 6.0.0 |
| `BITOP` | 2.6.0 |
| `BITPOS` | 2.8.7 |
| `GETBIT` | 2.2.0 |
| `SETBIT` | 2.2.0 |

## `@hyperloglog`

**5 commands** (Redis 8.6.3 — `Since: <X.Y.Z>` filters for older targets).

| Command | Since |
|---------|-------|
| `PFADD` | 2.8.9 |
| `PFCOUNT` | 2.8.9 |
| `PFDEBUG` | 2.8.9 |
| `PFMERGE` | 2.8.9 |
| `PFSELFTEST` | 2.8.9 |

## `@geo`

**10 commands** (Redis 8.6.3 — `Since: <X.Y.Z>` filters for older targets).

| Command | Since |
|---------|-------|
| `GEOADD` | 3.2.0 |
| `GEODIST` | 3.2.0 |
| `GEOHASH` | 3.2.0 |
| `GEOPOS` | 3.2.0 |
| `GEORADIUS` | 3.2.0 |
| `GEORADIUSBYMEMBER` | 3.2.0 |
| `GEORADIUSBYMEMBER_RO` | 3.2.10 |
| `GEORADIUS_RO` | 3.2.10 |
| `GEOSEARCH` | 6.2.0 |
| `GEOSEARCHSTORE` | 6.2.0 |

## `@stream`

**27 commands** (Redis 8.6.3 — `Since: <X.Y.Z>` filters for older targets).

| Command | Since |
|---------|-------|
| `XACK` | 5.0.0 |
| `XACKDEL` | 8.2.0 |
| `XADD` | 5.0.0 |
| `XAUTOCLAIM` | 6.2.0 |
| `XCFGSET` | 8.6.0 |
| `XCLAIM` | 5.0.0 |
| `XDEL` | 5.0.0 |
| `XDELEX` | 8.2.0 |
| `XGROUP CREATE` | 5.0.0 |
| `XGROUP CREATECONSUMER` | 6.2.0 |
| `XGROUP DELCONSUMER` | 5.0.0 |
| `XGROUP DESTROY` | 5.0.0 |
| `XGROUP HELP` | 5.0.0 |
| `XGROUP SETID` | 5.0.0 |
| `XIDMPRECORD` | 8.6.2 |
| `XINFO CONSUMERS` | 5.0.0 |
| `XINFO GROUPS` | 5.0.0 |
| `XINFO HELP` | 5.0.0 |
| `XINFO STREAM` | 5.0.0 |
| `XLEN` | 5.0.0 |
| `XPENDING` | 5.0.0 |
| `XRANGE` | 5.0.0 |
| `XREAD` | 5.0.0 |
| `XREADGROUP` | 5.0.0 |
| `XREVRANGE` | 5.0.0 |
| `XSETID` | 5.0.0 |
| `XTRIM` | 5.0.0 |

## `@pubsub`

**13 commands** (Redis 8.6.3 — `Since: <X.Y.Z>` filters for older targets).

| Command | Since |
|---------|-------|
| `PSUBSCRIBE` | 2.0.0 |
| `PUBLISH` | 2.0.0 |
| `PUBSUB CHANNELS` | 2.8.0 |
| `PUBSUB NUMPAT` | 2.8.0 |
| `PUBSUB NUMSUB` | 2.8.0 |
| `PUBSUB SHARDCHANNELS` | 7.0.0 |
| `PUBSUB SHARDNUMSUB` | 7.0.0 |
| `PUNSUBSCRIBE` | 2.0.0 |
| `SPUBLISH` | 7.0.0 |
| `SSUBSCRIBE` | 7.0.0 |
| `SUBSCRIBE` | 2.0.0 |
| `SUNSUBSCRIBE` | 7.0.0 |
| `UNSUBSCRIBE` | 2.0.0 |

## `@connection`

**38 commands** (Redis 8.6.3 — `Since: <X.Y.Z>` filters for older targets).

| Command | Since |
|---------|-------|
| `ASKING` | 3.0.0 |
| `AUTH` | 1.0.0 |
| `CLIENT CACHING` | 6.0.0 |
| `CLIENT GETNAME` | 2.6.9 |
| `CLIENT GETREDIR` | 6.0.0 |
| `CLIENT HELP` | 5.0.0 |
| `CLIENT ID` | 5.0.0 |
| `CLIENT INFO` | 6.2.0 |
| `CLIENT KILL` | 2.4.0 |
| `CLIENT LIST` | 2.4.0 |
| `CLIENT NO-EVICT` | 7.0.0 |
| `CLIENT NO-TOUCH` | 7.2.0 |
| `CLIENT PAUSE` | 3.0.0 |
| `CLIENT REPLY` | 3.2.0 |
| `CLIENT SETINFO` | 7.2.0 |
| `CLIENT SETNAME` | 2.6.9 |
| `CLIENT TRACKING` | 6.0.0 |
| `CLIENT TRACKINGINFO` | 6.2.0 |
| `CLIENT UNBLOCK` | 5.0.0 |
| `CLIENT UNPAUSE` | 6.2.0 |
| `COMMAND` | 2.8.13 |
| `COMMAND COUNT` | 2.8.13 |
| `COMMAND DOCS` | 7.0.0 |
| `COMMAND GETKEYS` | 2.8.13 |
| `COMMAND GETKEYSANDFLAGS` | 7.0.0 |
| `COMMAND HELP` | 5.0.0 |
| `COMMAND INFO` | 2.8.13 |
| `COMMAND LIST` | 7.0.0 |
| `ECHO` | 1.0.0 |
| `HELLO` | 6.0.0 |
| `PING` | 1.0.0 |
| `QUIT` | 1.0.0 |
| `READONLY` | 3.0.0 |
| `READWRITE` | 3.0.0 |
| `RESET` | 6.2.0 |
| `SELECT` | 1.0.0 |
| `WAIT` | 3.0.0 |
| `WAITAOF` | 7.2.0 |

## `@transaction`

**5 commands** (Redis 8.6.3 — `Since: <X.Y.Z>` filters for older targets).

| Command | Since |
|---------|-------|
| `DISCARD` | 2.0.0 |
| `EXEC` | 1.2.0 |
| `MULTI` | 1.2.0 |
| `UNWATCH` | 2.2.0 |
| `WATCH` | 2.2.0 |

## `@scripting`

**21 commands** (Redis 8.6.3 — `Since: <X.Y.Z>` filters for older targets).

| Command | Since |
|---------|-------|
| `EVAL` | 2.6.0 |
| `EVALSHA` | 2.6.0 |
| `EVALSHA_RO` | 7.0.0 |
| `EVAL_RO` | 7.0.0 |
| `FCALL` | 7.0.0 |
| `FCALL_RO` | 7.0.0 |
| `FUNCTION DELETE` | 7.0.0 |
| `FUNCTION DUMP` | 7.0.0 |
| `FUNCTION FLUSH` | 7.0.0 |
| `FUNCTION HELP` | 7.0.0 |
| `FUNCTION KILL` | 7.0.0 |
| `FUNCTION LIST` | 7.0.0 |
| `FUNCTION LOAD` | 7.0.0 |
| `FUNCTION RESTORE` | 7.0.0 |
| `FUNCTION STATS` | 7.0.0 |
| `SCRIPT DEBUG` | 3.2.0 |
| `SCRIPT EXISTS` | 2.6.0 |
| `SCRIPT FLUSH` | 2.6.0 |
| `SCRIPT HELP` | 5.0.0 |
| `SCRIPT KILL` | 2.6.0 |
| `SCRIPT LOAD` | 2.6.0 |

## `@admin`

**92 commands** (Redis 8.6.3 — `Since: <X.Y.Z>` filters for older targets).

| Command | Since |
|---------|-------|
| `ACL DELUSER` | 6.0.0 |
| `ACL DRYRUN` | 7.0.0 |
| `ACL GETUSER` | 6.0.0 |
| `ACL LIST` | 6.0.0 |
| `ACL LOAD` | 6.0.0 |
| `ACL LOG` | 6.0.0 |
| `ACL SAVE` | 6.0.0 |
| `ACL SETUSER` | 6.0.0 |
| `ACL USERS` | 6.0.0 |
| `BGREWRITEAOF` | 1.0.0 |
| `BGSAVE` | 1.0.0 |
| `CLIENT KILL` | 2.4.0 |
| `CLIENT LIST` | 2.4.0 |
| `CLIENT NO-EVICT` | 7.0.0 |
| `CLIENT PAUSE` | 3.0.0 |
| `CLIENT UNBLOCK` | 5.0.0 |
| `CLIENT UNPAUSE` | 6.2.0 |
| `CLUSTER ADDSLOTS` | 3.0.0 |
| `CLUSTER ADDSLOTSRANGE` | 7.0.0 |
| `CLUSTER BUMPEPOCH` | 3.0.0 |
| `CLUSTER COUNT-FAILURE-REPORTS` | 3.0.0 |
| `CLUSTER DELSLOTS` | 3.0.0 |
| `CLUSTER DELSLOTSRANGE` | 7.0.0 |
| `CLUSTER FAILOVER` | 3.0.0 |
| `CLUSTER FLUSHSLOTS` | 3.0.0 |
| `CLUSTER FORGET` | 3.0.0 |
| `CLUSTER MEET` | 3.0.0 |
| `CLUSTER MIGRATION` | 8.4.0 |
| `CLUSTER REPLICAS` | 5.0.0 |
| `CLUSTER REPLICATE` | 3.0.0 |
| `CLUSTER RESET` | 3.0.0 |
| `CLUSTER SAVECONFIG` | 3.0.0 |
| `CLUSTER SET-CONFIG-EPOCH` | 3.0.0 |
| `CLUSTER SETSLOT` | 3.0.0 |
| `CLUSTER SLAVES` | 3.0.0 |
| `CLUSTER SYNCSLOTS` | 8.4.0 |
| `CONFIG GET` | 2.0.0 |
| `CONFIG RESETSTAT` | 2.0.0 |
| `CONFIG REWRITE` | 2.8.0 |
| `CONFIG SET` | 2.0.0 |
| `DEBUG` | 1.0.0 |
| `FAILOVER` | 6.2.0 |
| `HOTKEYS GET` | 8.6.0 |
| `HOTKEYS RESET` | 8.6.0 |
| `HOTKEYS START` | 8.6.0 |
| `HOTKEYS STOP` | 8.6.0 |
| `LASTSAVE` | 1.0.0 |
| `LATENCY DOCTOR` | 2.8.13 |
| `LATENCY GRAPH` | 2.8.13 |
| `LATENCY HISTOGRAM` | 7.0.0 |
| `LATENCY HISTORY` | 2.8.13 |
| `LATENCY LATEST` | 2.8.13 |
| `LATENCY RESET` | 2.8.13 |
| `MODULE LIST` | 4.0.0 |
| `MODULE LOAD` | 4.0.0 |
| `MODULE LOADEX` | 7.0.0 |
| `MODULE UNLOAD` | 4.0.0 |
| `MONITOR` | 1.0.0 |
| `PFDEBUG` | 2.8.9 |
| `PFSELFTEST` | 2.8.9 |
| `PSYNC` | 2.8.0 |
| `REPLCONF` | 3.0.0 |
| `REPLICAOF` | 5.0.0 |
| `ROLE` | 2.8.12 |
| `SAVE` | 1.0.0 |
| `SENTINEL` | 2.8.4 |
| `SENTINEL CKQUORUM` | 2.8.4 |
| `SENTINEL CONFIG` | 6.2.0 |
| `SENTINEL DEBUG` | 7.0.0 |
| `SENTINEL FAILOVER` | 2.8.4 |
| `SENTINEL FLUSHCONFIG` | 2.8.4 |
| `SENTINEL GET-MASTER-ADDR-BY-NAME` | 2.8.4 |
| `SENTINEL INFO-CACHE` | 3.2.0 |
| `SENTINEL IS-MASTER-DOWN-BY-ADDR` | 2.8.4 |
| `SENTINEL MASTER` | 2.8.4 |
| `SENTINEL MASTERS` | 2.8.4 |
| `SENTINEL MONITOR` | 2.8.4 |
| `SENTINEL MYID` | 6.2.0 |
| `SENTINEL PENDING-SCRIPTS` | 2.8.4 |
| `SENTINEL REMOVE` | 2.8.4 |
| `SENTINEL REPLICAS` | 5.0.0 |
| `SENTINEL RESET` | 2.8.4 |
| `SENTINEL SENTINELS` | 2.8.4 |
| `SENTINEL SET` | 2.8.4 |
| `SENTINEL SIMULATE-FAILURE` | 3.2.0 |
| `SENTINEL SLAVES` | 2.8.0 |
| `SHUTDOWN` | 1.0.0 |
| `SLAVEOF` | 1.0.0 |
| `SLOWLOG GET` | 2.2.12 |
| `SLOWLOG LEN` | 2.2.12 |
| `SLOWLOG RESET` | 2.2.12 |
| `SYNC` | 1.0.0 |

## `@dangerous`

**14 commands** (Redis 8.6.3 — `Since: <X.Y.Z>` filters for older targets).

| Command | Since |
|---------|-------|
| `FLUSHALL` | 1.0.0 |
| `FLUSHDB` | 1.0.0 |
| `INFO` | 1.0.0 |
| `KEYS` | 1.0.0 |
| `LASTSAVE` | 1.0.0 |
| `MIGRATE` | 2.6.0 |
| `RESTORE` | 2.6.0 |
| `RESTORE-ASKING` | 3.0.0 |
| `ROLE` | 2.8.12 |
| `SFLUSH` | 8.0.0 |
| `SORT` | 1.0.0 |
| `SORT_RO` | 7.0.0 |
| `SWAPDB` | 4.0.0 |
| `TRIMSLOTS` | 8.4.0 |

## `@blocking`

**12 commands** (Redis 8.6.3 — `Since: <X.Y.Z>` filters for older targets).

| Command | Since |
|---------|-------|
| `BLMOVE` | 6.2.0 |
| `BLMPOP` | 7.0.0 |
| `BLPOP` | 2.0.0 |
| `BRPOP` | 2.0.0 |
| `BRPOPLPUSH` | 2.2.0 |
| `BZMPOP` | 7.0.0 |
| `BZPOPMAX` | 5.0.0 |
| `BZPOPMIN` | 5.0.0 |
| `WAIT` | 3.0.0 |
| `WAITAOF` | 7.2.0 |
| `XREAD` | 5.0.0 |
| `XREADGROUP` | 5.0.0 |

## `@fast`

**117 commands** (Redis 8.6.3 — `Since: <X.Y.Z>` filters for older targets).

| Command | Since |
|---------|-------|
| `APPEND` | 2.0.0 |
| `ASKING` | 3.0.0 |
| `AUTH` | 1.0.0 |
| `BITFIELD_RO` | 6.0.0 |
| `BZPOPMAX` | 5.0.0 |
| `BZPOPMIN` | 5.0.0 |
| `DBSIZE` | 1.0.0 |
| `DECR` | 1.0.0 |
| `DECRBY` | 1.0.0 |
| `DELEX` | 8.4.0 |
| `DIGEST` | 8.4.0 |
| `DISCARD` | 2.0.0 |
| `ECHO` | 1.0.0 |
| `EXISTS` | 1.0.0 |
| `EXPIRE` | 1.0.0 |
| `EXPIREAT` | 1.2.0 |
| `EXPIRETIME` | 7.0.0 |
| `GET` | 1.0.0 |
| `GETBIT` | 2.2.0 |
| `GETDEL` | 6.2.0 |
| `GETEX` | 6.2.0 |
| `GETSET` | 1.0.0 |
| `HDEL` | 2.0.0 |
| `HELLO` | 6.0.0 |
| `HEXISTS` | 2.0.0 |
| `HEXPIRE` | 7.4.0 |
| `HEXPIREAT` | 7.4.0 |
| `HEXPIRETIME` | 7.4.0 |
| `HGET` | 2.0.0 |
| `HGETDEL` | 8.0.0 |
| `HGETEX` | 8.0.0 |
| `HINCRBY` | 2.0.0 |
| `HINCRBYFLOAT` | 2.6.0 |
| `HLEN` | 2.0.0 |
| `HMGET` | 2.0.0 |
| `HMSET` | 2.0.0 |
| `HPERSIST` | 7.4.0 |
| `HPEXPIRE` | 7.4.0 |
| `HPEXPIREAT` | 7.4.0 |
| `HPEXPIRETIME` | 7.4.0 |
| `HPTTL` | 7.4.0 |
| `HSET` | 2.0.0 |
| `HSETEX` | 8.0.0 |
| `HSETNX` | 2.0.0 |
| `HSTRLEN` | 3.2.0 |
| `HTTL` | 7.4.0 |
| `INCR` | 1.0.0 |
| `INCRBY` | 1.0.0 |
| `INCRBYFLOAT` | 2.6.0 |
| `LASTSAVE` | 1.0.0 |
| `LLEN` | 1.0.0 |
| `LOLWUT` | 5.0.0 |
| `LPOP` | 1.0.0 |
| `LPUSH` | 1.0.0 |
| `LPUSHX` | 2.2.0 |
| `MGET` | 1.0.0 |
| `MOVE` | 1.0.0 |
| `MULTI` | 1.2.0 |
| `PERSIST` | 2.2.0 |
| `PEXPIRE` | 2.6.0 |
| `PEXPIREAT` | 2.6.0 |
| `PEXPIRETIME` | 7.0.0 |
| `PFADD` | 2.8.9 |
| `PING` | 1.0.0 |
| `PTTL` | 2.6.0 |
| `PUBLISH` | 2.0.0 |
| `QUIT` | 1.0.0 |
| `READONLY` | 3.0.0 |
| `READWRITE` | 3.0.0 |
| `RENAMENX` | 1.0.0 |
| `RESET` | 6.2.0 |
| `ROLE` | 2.8.12 |
| `RPOP` | 1.0.0 |
| `RPUSH` | 1.0.0 |
| `RPUSHX` | 2.2.0 |
| `SADD` | 1.0.0 |
| `SCARD` | 1.0.0 |
| `SELECT` | 1.0.0 |
| `SETNX` | 1.0.0 |
| `SISMEMBER` | 1.0.0 |
| `SMISMEMBER` | 6.2.0 |
| `SMOVE` | 1.0.0 |
| `SPOP` | 1.0.0 |
| `SPUBLISH` | 7.0.0 |
| `SREM` | 1.0.0 |
| `STRLEN` | 2.2.0 |
| `SWAPDB` | 4.0.0 |
| `TIME` | 2.6.0 |
| `TOUCH` | 3.2.1 |
| `TTL` | 1.0.0 |
| `TYPE` | 1.0.0 |
| `UNLINK` | 4.0.0 |
| `UNWATCH` | 2.2.0 |
| `WATCH` | 2.2.0 |
| `XACK` | 5.0.0 |
| `XACKDEL` | 8.2.0 |
| `XADD` | 5.0.0 |
| `XAUTOCLAIM` | 6.2.0 |
| `XCFGSET` | 8.6.0 |
| `XCLAIM` | 5.0.0 |
| `XDEL` | 5.0.0 |
| `XDELEX` | 8.2.0 |
| `XIDMPRECORD` | 8.6.2 |
| `XLEN` | 5.0.0 |
| `XSETID` | 5.0.0 |
| `ZADD` | 1.2.0 |
| `ZCARD` | 1.2.0 |
| `ZCOUNT` | 2.0.0 |
| `ZINCRBY` | 1.2.0 |
| `ZLEXCOUNT` | 2.8.9 |
| `ZMSCORE` | 6.2.0 |
| `ZPOPMAX` | 5.0.0 |
| `ZPOPMIN` | 5.0.0 |
| `ZRANK` | 2.0.0 |
| `ZREM` | 1.2.0 |
| `ZREVRANK` | 2.0.0 |
| `ZSCORE` | 1.2.0 |

## `@slow`

**305 commands** (Redis 8.6.3 — `Since: <X.Y.Z>` filters for older targets).

| Command | Since |
|---------|-------|
| `ACL` | 6.0.0 |
| `ACL CAT` | 6.0.0 |
| `ACL DELUSER` | 6.0.0 |
| `ACL DRYRUN` | 7.0.0 |
| `ACL GENPASS` | 6.0.0 |
| `ACL GETUSER` | 6.0.0 |
| `ACL HELP` | 6.0.0 |
| `ACL LIST` | 6.0.0 |
| `ACL LOAD` | 6.0.0 |
| `ACL LOG` | 6.0.0 |
| `ACL SAVE` | 6.0.0 |
| `ACL SETUSER` | 6.0.0 |
| `ACL USERS` | 6.0.0 |
| `ACL WHOAMI` | 6.0.0 |
| `BGREWRITEAOF` | 1.0.0 |
| `BGSAVE` | 1.0.0 |
| `BITCOUNT` | 2.6.0 |
| `BITFIELD` | 3.2.0 |
| `BITOP` | 2.6.0 |
| `BITPOS` | 2.8.7 |
| `BLMOVE` | 6.2.0 |
| `BLMPOP` | 7.0.0 |
| `BLPOP` | 2.0.0 |
| `BRPOP` | 2.0.0 |
| `BRPOPLPUSH` | 2.2.0 |
| `BZMPOP` | 7.0.0 |
| `CLIENT` | 2.4.0 |
| `CLIENT CACHING` | 6.0.0 |
| `CLIENT GETNAME` | 2.6.9 |
| `CLIENT GETREDIR` | 6.0.0 |
| `CLIENT HELP` | 5.0.0 |
| `CLIENT ID` | 5.0.0 |
| `CLIENT INFO` | 6.2.0 |
| `CLIENT KILL` | 2.4.0 |
| `CLIENT LIST` | 2.4.0 |
| `CLIENT NO-EVICT` | 7.0.0 |
| `CLIENT NO-TOUCH` | 7.2.0 |
| `CLIENT PAUSE` | 3.0.0 |
| `CLIENT REPLY` | 3.2.0 |
| `CLIENT SETINFO` | 7.2.0 |
| `CLIENT SETNAME` | 2.6.9 |
| `CLIENT TRACKING` | 6.0.0 |
| `CLIENT TRACKINGINFO` | 6.2.0 |
| `CLIENT UNBLOCK` | 5.0.0 |
| `CLIENT UNPAUSE` | 6.2.0 |
| `CLUSTER` | 3.0.0 |
| `CLUSTER ADDSLOTS` | 3.0.0 |
| `CLUSTER ADDSLOTSRANGE` | 7.0.0 |
| `CLUSTER BUMPEPOCH` | 3.0.0 |
| `CLUSTER COUNT-FAILURE-REPORTS` | 3.0.0 |
| `CLUSTER COUNTKEYSINSLOT` | 3.0.0 |
| `CLUSTER DELSLOTS` | 3.0.0 |
| `CLUSTER DELSLOTSRANGE` | 7.0.0 |
| `CLUSTER FAILOVER` | 3.0.0 |
| `CLUSTER FLUSHSLOTS` | 3.0.0 |
| `CLUSTER FORGET` | 3.0.0 |
| `CLUSTER GETKEYSINSLOT` | 3.0.0 |
| `CLUSTER HELP` | 5.0.0 |
| `CLUSTER INFO` | 3.0.0 |
| `CLUSTER KEYSLOT` | 3.0.0 |
| `CLUSTER LINKS` | 7.0.0 |
| `CLUSTER MEET` | 3.0.0 |
| `CLUSTER MIGRATION` | 8.4.0 |
| `CLUSTER MYID` | 3.0.0 |
| `CLUSTER MYSHARDID` | 7.2.0 |
| `CLUSTER NODES` | 3.0.0 |
| `CLUSTER REPLICAS` | 5.0.0 |
| `CLUSTER REPLICATE` | 3.0.0 |
| `CLUSTER RESET` | 3.0.0 |
| `CLUSTER SAVECONFIG` | 3.0.0 |
| `CLUSTER SET-CONFIG-EPOCH` | 3.0.0 |
| `CLUSTER SETSLOT` | 3.0.0 |
| `CLUSTER SHARDS` | 7.0.0 |
| `CLUSTER SLAVES` | 3.0.0 |
| `CLUSTER SLOT-STATS` | 8.2.0 |
| `CLUSTER SLOTS` | 3.0.0 |
| `CLUSTER SYNCSLOTS` | 8.4.0 |
| `COMMAND` | 2.8.13 |
| `COMMAND COUNT` | 2.8.13 |
| `COMMAND DOCS` | 7.0.0 |
| `COMMAND GETKEYS` | 2.8.13 |
| `COMMAND GETKEYSANDFLAGS` | 7.0.0 |
| `COMMAND HELP` | 5.0.0 |
| `COMMAND INFO` | 2.8.13 |
| `COMMAND LIST` | 7.0.0 |
| `CONFIG` | 2.0.0 |
| `CONFIG GET` | 2.0.0 |
| `CONFIG HELP` | 5.0.0 |
| `CONFIG RESETSTAT` | 2.0.0 |
| `CONFIG REWRITE` | 2.8.0 |
| `CONFIG SET` | 2.0.0 |
| `COPY` | 6.2.0 |
| `DEBUG` | 1.0.0 |
| `DEL` | 1.0.0 |
| `DUMP` | 2.6.0 |
| `EVAL` | 2.6.0 |
| `EVALSHA` | 2.6.0 |
| `EVALSHA_RO` | 7.0.0 |
| `EVAL_RO` | 7.0.0 |
| `EXEC` | 1.2.0 |
| `FAILOVER` | 6.2.0 |
| `FCALL` | 7.0.0 |
| `FCALL_RO` | 7.0.0 |
| `FLUSHALL` | 1.0.0 |
| `FLUSHDB` | 1.0.0 |
| `FUNCTION` | 7.0.0 |
| `FUNCTION DELETE` | 7.0.0 |
| `FUNCTION DUMP` | 7.0.0 |
| `FUNCTION FLUSH` | 7.0.0 |
| `FUNCTION HELP` | 7.0.0 |
| `FUNCTION KILL` | 7.0.0 |
| `FUNCTION LIST` | 7.0.0 |
| `FUNCTION LOAD` | 7.0.0 |
| `FUNCTION RESTORE` | 7.0.0 |
| `FUNCTION STATS` | 7.0.0 |
| `GEOADD` | 3.2.0 |
| `GEODIST` | 3.2.0 |
| `GEOHASH` | 3.2.0 |
| `GEOPOS` | 3.2.0 |
| `GEORADIUS` | 3.2.0 |
| `GEORADIUSBYMEMBER` | 3.2.0 |
| `GEORADIUSBYMEMBER_RO` | 3.2.10 |
| `GEORADIUS_RO` | 3.2.10 |
| `GEOSEARCH` | 6.2.0 |
| `GEOSEARCHSTORE` | 6.2.0 |
| `GETRANGE` | 2.4.0 |
| `HGETALL` | 2.0.0 |
| `HKEYS` | 2.0.0 |
| `HOTKEYS` | 8.6.0 |
| `HOTKEYS GET` | 8.6.0 |
| `HOTKEYS HELP` | 8.6.1 |
| `HOTKEYS RESET` | 8.6.0 |
| `HOTKEYS START` | 8.6.0 |
| `HOTKEYS STOP` | 8.6.0 |
| `HRANDFIELD` | 6.2.0 |
| `HSCAN` | 2.8.0 |
| `HVALS` | 2.0.0 |
| `INFO` | 1.0.0 |
| `KEYS` | 1.0.0 |
| `LATENCY` | 2.8.13 |
| `LATENCY DOCTOR` | 2.8.13 |
| `LATENCY GRAPH` | 2.8.13 |
| `LATENCY HELP` | 2.8.13 |
| `LATENCY HISTOGRAM` | 7.0.0 |
| `LATENCY HISTORY` | 2.8.13 |
| `LATENCY LATEST` | 2.8.13 |
| `LATENCY RESET` | 2.8.13 |
| `LCS` | 7.0.0 |
| `LINDEX` | 1.0.0 |
| `LINSERT` | 2.2.0 |
| `LMOVE` | 6.2.0 |
| `LMPOP` | 7.0.0 |
| `LPOS` | 6.0.6 |
| `LRANGE` | 1.0.0 |
| `LREM` | 1.0.0 |
| `LSET` | 1.0.0 |
| `LTRIM` | 1.0.0 |
| `MEMORY` | 4.0.0 |
| `MEMORY DOCTOR` | 4.0.0 |
| `MEMORY HELP` | 4.0.0 |
| `MEMORY MALLOC-STATS` | 4.0.0 |
| `MEMORY PURGE` | 4.0.0 |
| `MEMORY STATS` | 4.0.0 |
| `MEMORY USAGE` | 4.0.0 |
| `MIGRATE` | 2.6.0 |
| `MODULE` | 4.0.0 |
| `MODULE HELP` | 5.0.0 |
| `MODULE LIST` | 4.0.0 |
| `MODULE LOAD` | 4.0.0 |
| `MODULE LOADEX` | 7.0.0 |
| `MODULE UNLOAD` | 4.0.0 |
| `MONITOR` | 1.0.0 |
| `MSET` | 1.0.1 |
| `MSETEX` | 8.4.0 |
| `MSETNX` | 1.0.1 |
| `OBJECT` | 2.2.3 |
| `OBJECT ENCODING` | 2.2.3 |
| `OBJECT FREQ` | 4.0.0 |
| `OBJECT HELP` | 6.2.0 |
| `OBJECT IDLETIME` | 2.2.3 |
| `OBJECT REFCOUNT` | 2.2.3 |
| `PFCOUNT` | 2.8.9 |
| `PFDEBUG` | 2.8.9 |
| `PFMERGE` | 2.8.9 |
| `PFSELFTEST` | 2.8.9 |
| `PSETEX` | 2.6.0 |
| `PSUBSCRIBE` | 2.0.0 |
| `PSYNC` | 2.8.0 |
| `PUBSUB` | 2.8.0 |
| `PUBSUB CHANNELS` | 2.8.0 |
| `PUBSUB HELP` | 6.2.0 |
| `PUBSUB NUMPAT` | 2.8.0 |
| `PUBSUB NUMSUB` | 2.8.0 |
| `PUBSUB SHARDCHANNELS` | 7.0.0 |
| `PUBSUB SHARDNUMSUB` | 7.0.0 |
| `PUNSUBSCRIBE` | 2.0.0 |
| `RANDOMKEY` | 1.0.0 |
| `RENAME` | 1.0.0 |
| `REPLCONF` | 3.0.0 |
| `REPLICAOF` | 5.0.0 |
| `RESTORE` | 2.6.0 |
| `RESTORE-ASKING` | 3.0.0 |
| `RPOPLPUSH` | 1.2.0 |
| `SAVE` | 1.0.0 |
| `SCAN` | 2.8.0 |
| `SCRIPT` | 2.6.0 |
| `SCRIPT DEBUG` | 3.2.0 |
| `SCRIPT EXISTS` | 2.6.0 |
| `SCRIPT FLUSH` | 2.6.0 |
| `SCRIPT HELP` | 5.0.0 |
| `SCRIPT KILL` | 2.6.0 |
| `SCRIPT LOAD` | 2.6.0 |
| `SDIFF` | 1.0.0 |
| `SDIFFSTORE` | 1.0.0 |
| `SENTINEL` | 2.8.4 |
| `SENTINEL CKQUORUM` | 2.8.4 |
| `SENTINEL CONFIG` | 6.2.0 |
| `SENTINEL DEBUG` | 7.0.0 |
| `SENTINEL FAILOVER` | 2.8.4 |
| `SENTINEL FLUSHCONFIG` | 2.8.4 |
| `SENTINEL GET-MASTER-ADDR-BY-NAME` | 2.8.4 |
| `SENTINEL HELP` | 6.2.0 |
| `SENTINEL INFO-CACHE` | 3.2.0 |
| `SENTINEL IS-MASTER-DOWN-BY-ADDR` | 2.8.4 |
| `SENTINEL MASTER` | 2.8.4 |
| `SENTINEL MASTERS` | 2.8.4 |
| `SENTINEL MONITOR` | 2.8.4 |
| `SENTINEL MYID` | 6.2.0 |
| `SENTINEL PENDING-SCRIPTS` | 2.8.4 |
| `SENTINEL REMOVE` | 2.8.4 |
| `SENTINEL REPLICAS` | 5.0.0 |
| `SENTINEL RESET` | 2.8.4 |
| `SENTINEL SENTINELS` | 2.8.4 |
| `SENTINEL SET` | 2.8.4 |
| `SENTINEL SIMULATE-FAILURE` | 3.2.0 |
| `SENTINEL SLAVES` | 2.8.0 |
| `SET` | 1.0.0 |
| `SETBIT` | 2.2.0 |
| `SETEX` | 2.0.0 |
| `SETRANGE` | 2.2.0 |
| `SFLUSH` | 8.0.0 |
| `SHUTDOWN` | 1.0.0 |
| `SINTER` | 1.0.0 |
| `SINTERCARD` | 7.0.0 |
| `SINTERSTORE` | 1.0.0 |
| `SLAVEOF` | 1.0.0 |
| `SLOWLOG` | 2.2.12 |
| `SLOWLOG GET` | 2.2.12 |
| `SLOWLOG HELP` | 6.2.0 |
| `SLOWLOG LEN` | 2.2.12 |
| `SLOWLOG RESET` | 2.2.12 |
| `SMEMBERS` | 1.0.0 |
| `SORT` | 1.0.0 |
| `SORT_RO` | 7.0.0 |
| `SRANDMEMBER` | 1.0.0 |
| `SSCAN` | 2.8.0 |
| `SSUBSCRIBE` | 7.0.0 |
| `SUBSCRIBE` | 2.0.0 |
| `SUBSTR` | 1.0.0 |
| `SUNION` | 1.0.0 |
| `SUNIONSTORE` | 1.0.0 |
| `SUNSUBSCRIBE` | 7.0.0 |
| `SYNC` | 1.0.0 |
| `TRIMSLOTS` | 8.4.0 |
| `UNSUBSCRIBE` | 2.0.0 |
| `WAIT` | 3.0.0 |
| `WAITAOF` | 7.2.0 |
| `XGROUP` | 5.0.0 |
| `XGROUP CREATE` | 5.0.0 |
| `XGROUP CREATECONSUMER` | 6.2.0 |
| `XGROUP DELCONSUMER` | 5.0.0 |
| `XGROUP DESTROY` | 5.0.0 |
| `XGROUP HELP` | 5.0.0 |
| `XGROUP SETID` | 5.0.0 |
| `XINFO` | 5.0.0 |
| `XINFO CONSUMERS` | 5.0.0 |
| `XINFO GROUPS` | 5.0.0 |
| `XINFO HELP` | 5.0.0 |
| `XINFO STREAM` | 5.0.0 |
| `XPENDING` | 5.0.0 |
| `XRANGE` | 5.0.0 |
| `XREAD` | 5.0.0 |
| `XREADGROUP` | 5.0.0 |
| `XREVRANGE` | 5.0.0 |
| `XTRIM` | 5.0.0 |
| `ZDIFF` | 6.2.0 |
| `ZDIFFSTORE` | 6.2.0 |
| `ZINTER` | 6.2.0 |
| `ZINTERCARD` | 7.0.0 |
| `ZINTERSTORE` | 2.0.0 |
| `ZMPOP` | 7.0.0 |
| `ZRANDMEMBER` | 6.2.0 |
| `ZRANGE` | 1.2.0 |
| `ZRANGEBYLEX` | 2.8.9 |
| `ZRANGEBYSCORE` | 1.0.5 |
| `ZRANGESTORE` | 6.2.0 |
| `ZREMRANGEBYLEX` | 2.8.9 |
| `ZREMRANGEBYRANK` | 2.0.0 |
| `ZREMRANGEBYSCORE` | 1.2.0 |
| `ZREVRANGE` | 1.2.0 |
| `ZREVRANGEBYLEX` | 2.8.9 |
| `ZREVRANGEBYSCORE` | 2.2.0 |
| `ZSCAN` | 2.8.0 |
| `ZUNION` | 6.2.0 |
| `ZUNIONSTORE` | 2.0.0 |

---

## Regenerating this map

```bash
# From the repo root:
./scripts/build-category-map.py > skills/acl-reference/references/command-category-map.md
```

The script downloads the source tarball for the pinned Redis tag, extracts `src/commands/*.json`, and rebuilds this document. Bump the pinned tag in the script's header to regenerate for a different Redis release.
