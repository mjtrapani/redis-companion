# redis-companion

A Claude Code plugin that reads your service's code and generates a least-privilege Redis ACL rule — version-aware, with per-clause annotations, and (optionally) provisioned and validated against a live Redis.

---

## What it does

You point it at a backend service's directory. It detects the Redis client library, infers the access patterns (keys, channels, streams, commands), asks you a few targeted questions (target edition, version, permission granularity, defense-in-depth preference), and emits a Redis ACL rule that grants only what the service actually needs.

For Redis OSS / Redis Cloud direct-connect, it emits a full `ACL SETUSER` command and can apply it via the Redis MCP after a safety gate. For Redis Enterprise, it emits just the ACL Rule body — paste into the admin UI or REST API.

## Who it's for

**Backend engineers scoping their service's Redis access to the minimum necessary permissions** — new or existing services, in any backend language. The pain is well-known:

- Redis ACL syntax is powerful but cryptic. Translating "this service reads from `cache:user:*`, publishes to `notifications`, and writes a stream" into a correct ACL DSL is a real cognitive load.
- Rules drift between Redis 6 / 7 / 8 — `@scripting` was split out of `@write` in 7, module commands joined `@read`/`@write` in 8, pub/sub default-deny flipped on.
- Neither Redis OS nor Redis Enterprise has a low-friction interface for constructing custom ACL rules from intent. Developers ship with the `default` user because the alternative is too much work.

This plugin removes that friction. It reads the code, derives the intent, and emits an annotated rule the user can apply directly or paste into Enterprise's admin UI.

## Install in under 5 minutes

You need [Claude Code](https://code.claude.com/) installed and authenticated.

```bash
# 1. Clone the repo
git clone https://github.com/mjtrapani/redis-companion.git
cd redis-companion

# 2. Launch Claude Code with the plugin loaded
claude --plugin-dir .
```

That's it. The plugin is active.

To verify, in the Claude Code prompt:

```
/agents
```

You should see `acl-generator` in the list. And:

```
say something Redis-adjacent — like "what does +@read grant in Redis 7?"
```

You should see the `redis-acl-patterns` skill auto-load and inform Claude's answer.

## Try the demo

A ~40-line sample service is included at `examples/sample-service/`. It uses `redis-py` and exercises strings, hashes, lists, sets, pub/sub, and streams.

In Claude Code:

```
/redis-companion:analyze examples/sample-service
```

The agent will:

1. Detect `redis-py` from the imports + `requirements.txt`
2. Find the key patterns (`cache:user:*`, `session:*`), the pub/sub channel (`notifications`), and the stream (`activity:events`)
3. Inventory the commands: `SET`, `GET`, `MGET`, `SETEX`, `PUBLISH`, `XADD`
4. Ask you for: target Redis **edition** (OSS / Enterprise), target Redis **major version** (6 / 7 / 8), **defense-in-depth deny** preference, and **permission granularity** (strict / balanced / brevity)
5. Emit something like:

```
ACL SETUSER my-service-user on >REPLACE_WITH_PASSWORD ~cache:user:* ~session:* &notifications +GET +MGET +SET +SETEX +PUBLISH +XADD
```

…with a per-clause annotation table citing the source lines that justified each grant, plus instructions on how to apply (`ACL SETUSER` for OSS, "paste into an ACL Rule body" for Enterprise).

You can also invoke conversationally:

```
scope a Redis ACL for examples/sample-service
```

…and Claude will route to the agent via its description.

## Optional: connect a Redis MCP for live validation and apply

The plugin works fully without an MCP connection. With one, you get three additional capabilities:

1. **Live category verification** via `ACL CAT @<category>` — more accurate than the baked command-category reference, especially on Redis 8 or with modules loaded.
2. **Existing-user inspection** via `ACL LIST` / `ACL GETUSER` — avoid naming collisions and learn from existing rule shapes.
3. **Safety-gated apply (OSS only)** — agent applies the rule via `ACL SETUSER` after you type `yes`, verifies with `ACL GETUSER`, and validates by impersonation (in-scope commands succeed, out-of-scope are blocked).

### Setup

The plugin ships `.mcp.json` pre-wired to [`redis/mcp-redis`](https://github.com/redis/mcp-redis), the official Redis MCP server. To activate:

```bash
# 1. Install uv (one-time): https://docs.astral.sh/uv/getting-started/installation/
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Set REDIS_URL — point at the target Redis using an admin-capable user
export REDIS_URL='redis://default:<password>@localhost:6379/0'
# For local dev with no password: redis://localhost:6379

# 3. Restart Claude Code
claude --plugin-dir .
```

After restart, `mcp__redis__*` tools will be available, the agent will use them automatically when relevant, and `apply` will be enabled in OSS output.

### About the `/doctor` warning

If you launch the plugin without setting `REDIS_URL`, `/doctor` shows:

> `[Warning] [redis] mcpServers.redis: Missing environment variables: REDIS_URL`

This is **expected and benign** — the plugin's skill, agent, and hook all work without MCP. The warning just says the optional Redis MCP server can't auto-start without `REDIS_URL`. Set it (above) and the warning goes away.

## How it works

The plugin is four cooperating components, each doing one job:

### Skill: `redis-acl-patterns`

Knowledge base, in `skills/redis-acl-patterns/`. Loads automatically when conversation touches Redis client code or ACL syntax. Contains the ACL DSL primer, the OSS vs Enterprise fork map, and pointers to four detailed references that load on demand:

- `command-category-map.md` — categories → commands for the >50% category-collapse rule
- `version-deltas.md` — Redis 6 / 7 / 8 changes (scripting split, selectors, module-category expansion)
- `client-library-patterns.md` — `redis-py` / `ioredis` / `go-redis` method → Redis command mappings, with a caveats section for non-1:1 cases (scripting helpers, locks, subcommand methods, transactional pipelines)
- `key-pattern-extraction.md` — ten-case table for deriving `~prefix:*` clauses from source code

### Agent: `acl-generator`

Task executor, in `agents/acl-generator.md`. Read-only filesystem access (Write/Edit/MultiEdit are disallowed). Inherits MCP tools from the session when the Redis MCP is connected. Process: load knowledge → discover from code → ask the user (batched) → optional MCP discovery → synthesize the rule → emit annotated output → offer apply (OSS + MCP only) behind a safety gate.

### Hook: `credential-guard`

PreToolUse hook on Write / Edit / MultiEdit, in `hooks/`. Blocks file writes that contain literal Redis credentials — `REDIS_PASS=` with a real value, `redis://user:pw@host`, or `redis-cli -a <pw>`. Recognized placeholders (`REPLACE_WITH_PASSWORD`, `<password>`, `${REDIS_PASS}`, etc.) pass through, so the agent's own output isn't blocked. Defense-in-depth for the local working directory — separate from the live-server safety gate.

### MCP config: `.mcp.json`

Wires the Redis MCP server (`redis/mcp-redis`) using `${REDIS_URL}`. Auto-starts when the env var is set, stays out of the way otherwise. All ACL-related Redis commands (`ACL CAT`, `ACL LIST`, `ACL GETUSER`, `ACL SETUSER`, `ACL WHOAMI`) are exposed as tools when connected.

## Limitations

The agent **always asks** for these because they can't be inferred reliably:

- **Target Redis edition** (OSS vs Enterprise). No command-only fingerprint definitively identifies Enterprise — `INFO` heuristics are probabilistic, not authoritative.
- **Target Redis major version.** Package files reveal client library version, not server version.

The agent **flags but doesn't silently bake** these:

- **Client method → Redis command mappings** for non-CRUD usage (scripting helpers, locks, subcommand-named methods, transactional pipelines, Sentinel/Cluster client mode, sharded pub/sub). The convention "method name = command name" holds for ~90% of calls but breaks for the rest. The agent surfaces flagged calls in its output and recommends `MONITOR` against a test instance for absolute certainty.
- **Inferred grants from comments** (e.g., a `# TODO: add scripting` near pubsub code). Surfaced as a question; never baked in.

The agent **doesn't do these in v1**:

- **Generate Redis Enterprise REST API JSON payloads** or make the API call. Enterprise output is the rule body only — paste into the admin UI or REST API yourself.
- **Automate `MONITOR` for client-mapping disambiguation.** Suggested manually when ambiguity is flagged.
- **Multi-client / multi-language analysis in a single pass.** If your codebase has both `redis-py` and `go-redis`, the agent asks you which to focus on first and handles one at a time.
- **Apply ACLs on Redis Enterprise.** Direct `ACL SETUSER` is blocked at the cluster level; Enterprise ACL writes flow through the cluster manager REST API, which the plugin doesn't call.

## What's next

The biggest future-work items:

- **Execute Enterprise provisioning end-to-end** — generate the REST API JSON payload and make the call, either by extending the Redis Cloud admin MCP (which today scopes to subscription/infra, not ACL/user/role) or by having the agent make raw Enterprise REST API calls.
- **MCP-driven `MONITOR` for client-mapping verification** — when an ambiguous client method is flagged, run `MONITOR` against a user-specified test target, capture the actual wire commands, and use those to disambiguate. Closes the loop on "can this be known without reviewing client source."
- **Module command coverage** — `@json` (RedisJSON), `@search` (RediSearch), `@timeseries`, Bloom filter family. First-class in most Enterprise deployments.
- **Database-scoped ACLs** for multi-tenant Enterprise — Enterprise lets ACLs be scoped per-database; v1 treats the target as a single ACL surface.
- **`ACL LOG`-driven denial diagnosis** — inverse of the v1 workflow: read the audit trail of recent ACL denials, group them, and suggest minimal additions to unblock the application.
- **Auto-fix mode** — rewrite detected anti-patterns in place (`r.keys("user:*")` → `r.scan_iter(match="user:*")`), with a dry-run default.

## Credits

This plugin's predecessor is **[Redis ACL Builder](https://github.com/markotrapani/redis-acl-builder)** (MIT) — an Electron GUI I shipped last year after watching Redis support tickets pile up about ACL syntax confusion. The Builder helped manually. `redis-companion` removes the manual step: an agent that reads the code, derives the intent, and emits the rule.

MCP integration uses [`redis/mcp-redis`](https://github.com/redis/mcp-redis), the official general-purpose Redis MCP server.

## License

MIT — see `.claude-plugin/plugin.json` for plugin metadata.
