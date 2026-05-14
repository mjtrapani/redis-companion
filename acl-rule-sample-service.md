# Redis ACL Rule for `sample-service`

## ACL Command

```
ACL SETUSER sample-service on ><changeme> resetkeys ~cache:user:* ~session:* ~activity:events resetchannels &notifications -@all +@connection +set +get +mget +setex +publish +xadd
```

> **Replace `<changeme>`** with a strong, randomly generated password before applying. Example: `openssl rand -base64 32`. For local-dev Redis with no auth, replace the entire `><changeme>` token with `nopass`. Never commit the plaintext password to source control — store it in your secret manager (Vault, AWS Secrets Manager, etc.) and inject at runtime.

---

## Per-Term Annotations

| Term | Rationale | Source |
|---|---|---|
| `on` | Enable the user. | ACL DSL |
| `><changeme>` | Password placeholder. Replace before applying. | — |
| `resetkeys` | Clear any inherited key permissions before applying explicit `~` patterns (defense-in-depth). | ACL DSL |
| `~cache:user:*` | Service reads/writes user cache entries via SET/GET/MGET. | `examples/sample-service/service.py:15` (`CACHE_PREFIX`), used at `:22`, `:26`, `:31` |
| `~session:*` | Service writes session entries via SETEX. | `examples/sample-service/service.py:16` (`SESSION_PREFIX`), used at `:36` |
| `~activity:events` | Single literal stream key for XADD. Not a pattern — exact match only. | `examples/sample-service/service.py:18` (`ACTIVITY_STREAM`), used at `:45` |
| `resetchannels` | Clear any inherited pub/sub channel permissions before applying explicit `&` (defense-in-depth). | ACL DSL |
| `&notifications` | Single literal channel for PUBLISH. | `examples/sample-service/service.py:17` (`NOTIFY_CHANNEL`), used at `:41` |
| `-@all` | Deny everything by default; whitelist only what's needed (defense-in-depth). | ACL DSL |
| `+@connection` | Allow AUTH, HELLO, PING, SELECT, RESET, CLIENT — required for `Redis.from_url(...)` handshake. | `examples/sample-service/service.py:10-13` |
| `+set` | SET — cache writes. | `examples/sample-service/service.py:22` |
| `+get` | GET — cache reads. | `examples/sample-service/service.py:26` |
| `+mget` | MGET — batch cache reads. | `examples/sample-service/service.py:31` |
| `+setex` | SETEX — session writes with TTL. | `examples/sample-service/service.py:36` |
| `+publish` | PUBLISH — pub/sub fanout. | `examples/sample-service/service.py:41` |
| `+xadd` | XADD — append to activity stream. | `examples/sample-service/service.py:45` |

**Excluded (per your direction):** `+subscribe` for the TODO at `service.py:40`. When that handler is implemented, regenerate the rule and add `+subscribe` plus the corresponding channel grant.

---

## Detected Context

- **Client library:** redis-py (>=5.0.0), sync `Redis.from_url(...)`
- **Service file:** `examples/sample-service/service.py`
- **Server edition:** Redis OSS (Open Source)
- **Effective target version:** **8.6.3** (from `INFO SERVER` via MCP)
- **Defense-in-depth:** Enabled (`resetkeys`, `resetchannels`, `-@all`)
- **Granularity:** Balanced — explicit per-command grants; category grant only for the unavoidable `@connection` handshake set
- **Commands resolved:** 6 explicit (SET, GET, MGET, SETEX, PUBLISH, XADD), all available since well before 8.6.3
- **Key patterns:** 2 prefix patterns + 1 exact literal
- **Channel patterns:** 1 exact literal
- **Speculation:** TODO at `service.py:40` (SUBSCRIBE) deliberately excluded

---

## How to Apply

### Pattern A — Extract from this file (recommended)

After editing the `<changeme>` placeholder above to your actual password (or to `nopass` for local-dev Redis with no auth), apply with:

```bash
grep -m1 '^ACL SETUSER' ./acl-rule-sample-service.md | redis-cli
```

For a remote target:

```bash
grep -m1 '^ACL SETUSER' ./acl-rule-sample-service.md | redis-cli -h <host> -p <port> --user <admin> --askpass
```

This pattern is paste-safe: the only thing you type/paste in the terminal is the short `grep | redis-cli` command. The long rule stays in this file.

### Pattern B — Heredoc (interactive)

```bash
redis-cli <<'EOF'
ACL SETUSER sample-service on ><changeme> resetkeys ~cache:user:* ~session:* ~activity:events resetchannels &notifications -@all +@connection +set +get +mget +setex +publish +xadd
EOF
```

(The closing `EOF` must be at column 0 — pastes that preserve indentation will hang the shell at `heredoc>`.)

### Pattern C — Single-line, all special tokens single-quoted

```bash
redis-cli ACL SETUSER sample-service on '><changeme>' resetkeys '~cache:user:*' '~session:*' '~activity:events' resetchannels '&notifications' '-@all' +@connection +set +get +mget +setex +publish +xadd
```

### Pattern D — Persistent via `users.acl`

For durable, declarative ACL management across restarts. Add the line below (without the `ACL SETUSER` prefix — `users.acl` uses bare `user` definitions) to your `users.acl` file:

```
user sample-service on ><changeme> resetkeys ~cache:user:* ~session:* ~activity:events resetchannels &notifications -@all +@connection +set +get +mget +setex +publish +xadd
```

Ensure `redis.conf` contains `aclfile /path/to/users.acl`. Then reload:

```bash
redis-cli ACL LOAD
```

---

## Verify

After applying, confirm the user exists with the expected flags, keys, channels, and commands:

```bash
redis-cli ACL GETUSER sample-service
```

Expected:
- `flags`: includes `on`
- `keys`: `~cache:user:*`, `~session:*`, `~activity:events`
- `channels`: `&notifications`
- `commands`: `-@all +@connection +set +get +mget +setex +publish +xadd`

---

## Sanity Checks

Authenticate as `sample-service` and exercise both allowed and denied paths:

```bash
# Authenticate as the new user (replace password as needed):
redis-cli --user sample-service --pass '<password-or-omit-if-nopass>' SET cache:user:42 '{"id":42}'   # → OK
redis-cli --user sample-service --pass '<password-or-omit-if-nopass>' GET cache:user:42              # → returns value
redis-cli --user sample-service --pass '<password-or-omit-if-nopass>' MGET cache:user:1 cache:user:2 # → returns array
redis-cli --user sample-service --pass '<password-or-omit-if-nopass>' SETEX session:abc 3600 token   # → OK
redis-cli --user sample-service --pass '<password-or-omit-if-nopass>' PUBLISH notifications "hello"  # → integer
redis-cli --user sample-service --pass '<password-or-omit-if-nopass>' XADD activity:events '*' type login user 42  # → stream ID

# --- SHOULD FAIL (NOPERM) ---
redis-cli --user sample-service --pass '<password-or-omit-if-nopass>' GET other:key                  # NOPERM (key outside allowed)
redis-cli --user sample-service --pass '<password-or-omit-if-nopass>' DEL cache:user:42              # NOPERM (-@all denies DEL)
redis-cli --user sample-service --pass '<password-or-omit-if-nopass>' KEYS '*'                       # NOPERM (-@all denies KEYS)
redis-cli --user sample-service --pass '<password-or-omit-if-nopass>' PUBLISH other-channel "x"      # NOPERM (channel outside &notifications)
redis-cli --user sample-service --pass '<password-or-omit-if-nopass>' SUBSCRIBE notifications        # NOPERM (TODO not yet implemented)
redis-cli --user sample-service --pass '<password-or-omit-if-nopass>' FLUSHDB                        # NOPERM (-@all denies dangerous admin)
```

A `NOPERM` reply on each "SHOULD FAIL" line and an `OK`/expected reply on each "SHOULD SUCCEED" line confirms the rule is correctly scoped.

---

**Note on the TODO at `service.py:40`:** When the inbound subscribe handler is implemented, regenerate this rule with `+subscribe` and the appropriate `&<channel>` grant(s). Do not pre-grant — least privilege wins.
