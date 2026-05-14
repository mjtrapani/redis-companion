# Expected behavior — test oracle

This document defines what the plugin **must do** when invoked against `examples/sample-service/`. It served as the spec we scored actual behavior against during the build — when the agent first ran and drifted (skipping the question phase, miscategorizing `PUBLISH`, baking in speculation), we had a concrete behavioral contract to redirect against. Anything not specified here is implementation discretion.

For anyone forking the plugin: this file is the behavioral spec your fork should honor (with your domain's specifics swapped in for keys/channels/streams/commands). Run your plugin against your own equivalent of `sample-service/` and score it against an oracle of this shape.

---

## Test scenario

**Setup:**
- Plugin v0.4.11+ installed via marketplace as `mjtrapani/redis-companion`
- Redis 8.6.3 running locally on `127.0.0.1:6379`, no auth, default user
- `REDIS_URL=redis://localhost:6379` exported in the shell environment (so the plugin's MCP autostarts)
- MCP `redis/mcp-redis` server connected via the `mcpServers` block in `.claude-plugin/plugin.json`
- Current working directory: the repo root (where `examples/sample-service/` is reachable as a relative path)

**Trigger:**
```
/redis-companion:rule examples/sample-service
```

---

## Phase 1 — Skill loads inline

**Expected:** The `rule` skill begins executing in the main conversation (not dispatched as a sub-agent). User sees a brief "starting analysis" line, no more.

**Forbidden:**
- Dumping the entire skill prompt to the user
- Pre-emptively asking questions before discovery

---

## Phase 2 — Discovery (sub-agent, single shot)

**Expected:** The skill spawns the `redis-companion:acl-generator` sub-agent (plugin agents require the fully-qualified namespaced name as the `subagent_type`) in **discovery-only mode** with a prompt that includes the target path and instructs it to:
1. Detect client library
2. Walk the codebase for Redis client method calls
3. Extract key/channel/stream patterns
4. Build command inventory
5. Flag speculation candidates (TODO/FIXME comments near Redis calls)
6. Read Redis version via `INFO SERVER` (MCP)
7. Return a structured summary — **no questions**, no synthesis

**Allowed tools in this phase (for the sub-agent):**
- `Read`, `Grep`, `Glob` (filesystem discovery)
- `mcp__plugin_redis-companion_redis__info` (version probe — once)
- `WebFetch` (one-shot, only for ambiguous client-library method mappings)
- `Skill` (load `acl-reference` reference, once)

**Forbidden tools:**
- `Bash` (disallowed in agent frontmatter)
- `Write`, `Edit`, `MultiEdit` (disallowed)
- `mcp__*__scan_keys`, `mcp__*__scan_all_keys`, `mcp__*__get`, `mcp__*__hgetall`, `mcp__*__lrange`, or any data-reading MCP tool — ACL generation derives intent from source, not live data

**Expected discovery summary returned to the skill** (the agent's text response — content matters more than exact wording, but it must be parseable and complete):

```markdown
## Discovery

**Client library:** redis-py (from `from redis import Redis` in service.py:10 and `redis` in requirements.txt:1)

**Connection style:** `Redis.from_url(REDIS_URL)` (synchronous, no Sentinel/Cluster, no pipeline)

**Commands used** (6):

| Call site (service.py) | Method | Redis command |
|------------------------|--------|----------------|
| L22 | `r.set(...)` | `SET` |
| L26 | `r.get(...)` | `GET` |
| L31 | `r.mget(...)` | `MGET` |
| L36 | `r.setex(...)` | `SETEX` |
| L41 | `r.publish(...)` | `PUBLISH` |
| L44 | `r.xadd(...)` | `XADD` |

**Key patterns** (3, all Case 4 — resolved from module-level constants):

| Pattern | Constant | Used by |
|---------|----------|---------|
| `~cache:user:*` | `CACHE_PREFIX = "cache:user:"` (L15) | SET, GET, MGET |
| `~session:*` | `SESSION_PREFIX = "session:"` (L16) | SETEX |
| `~activity:events` | `ACTIVITY_STREAM = "activity:events"` (L18) | XADD |

**Channels** (1):

| Pattern | Constant | Used by |
|---------|----------|---------|
| `&notifications` | `NOTIFY_CHANNEL = "notifications"` (L17) | PUBLISH |

**Speculation candidates** (1):

- **service.py:40** — `# TODO: add a subscribe handler for inbound notifications from other services` — suggests future `SUBSCRIBE` + `&notifications` grants. Not baking in.

**Server version** (from `INFO SERVER` via MCP): Redis **8.6.3**

**Mapping notes:** No ambiguous method→command mappings detected.
```

**Pass criteria for Phase 2:**
- Discovery summary contains every section above
- All 6 commands identified with correct line numbers
- All 3 key patterns extracted as Case 4 (constants resolved)
- 1 channel pattern extracted
- TODO at L40 flagged as a speculation candidate
- Redis version 8.6.3 read from `INFO SERVER` (not asked)
- ≤ 10 tool calls total

---

## Phase 3 — Batched ask (via `AskUserQuestion`)

**Expected:** The skill calls `AskUserQuestion` **once** with all baseline questions plus Q3 (conditional on speculation candidate found in Phase 2). Each question is structured with options the user picks from.

**Verbatim question texts** (the skill must ask these — wording can vary slightly but the *semantics* are fixed):

### Q1: Target Redis edition?

> Which Redis edition is this rule for?

Options:
- **Open Source (Redis OSS)** — I'll emit a full `ACL SETUSER` command runnable via `redis-cli`
- **Enterprise (Redis Software / Redis Cloud)** — I'll emit just the rule body for the ACL Rule object (paste into admin UI or REST API)

### Q2: Target Redis major version?

**If MCP read a version via `INFO SERVER` in Phase 2** (e.g., 8.6.3), present as a confirmation:

> I see **Redis 8.6.3** from `INFO SERVER`. Use Redis 8 as the target?

Options:
- **Yes, Redis 8** — matches the live server (recommended)
- **Redis 7** — override; generating rule for a different deployment
- **Redis 6** — override; generating rule for a much older deployment

**If MCP is not connected** (no version pre-read), present as an open question:

> Which Redis major version is the target server?

Options:
- **Redis 6** — `@scripting` lives inside `@write`; no selectors; pub/sub default permissive
- **Redis 7** — `@scripting` is its own category; selectors and `%R~`/`%W~` available; pub/sub default-deny
- **Redis 8** — All Redis 7 features plus standard categories include module commands

### v1 design choices (no longer asked)

Two questions were intentionally removed in v1 in favor of safe hardcoded defaults:

- **Permission granularity is always "strict least-privilege".** Individual command grants only; never collapse to `+@category` regardless of usage ratios. Safest default; removes a confusing user-facing choice. The agent's S2 step retains the balanced/brevity logic for future re-enablement.
- **Defense-in-depth denies (`-@admin -@dangerous`) are always omitted.** With strict individual grants and the `nocommands` baseline (= `-@all`), the user has zero permissions by default and only the explicitly-granted 6 commands are runnable. None of those 6 are in `@admin` or `@dangerous`, so adding the denies would remove categories that were never granted — a functional no-op that just adds visual noise. Defense-in-depth denies matter when using `+@category` grants, which v1 never emits.

### Q3 (conditional): Speculation candidate

> I noticed a `# TODO: add a subscribe handler` at service.py:40, suggesting `SUBSCRIBE` may be added later. Should I include `+SUBSCRIBE` and `&notifications` channel grants now, or leave them out (you can re-run me when subscribe is actually wired up)?

Options:
- **Include now** — Grant `+SUBSCRIBE` and the `&notifications` channel for subscribe; rule covers the planned subscribe addition without re-running
- **Leave out (recommended)** — Stricter least-privilege. Rule covers only what the code actually does today; re-run me when you implement subscribe

**Pass criteria for Phase 3:**
- `AskUserQuestion` is called (this is enforced — the parent CAN'T continue without user input)
- Both baseline questions (Q1 edition, Q2 version) present, in order, with semantically-correct option lists
- Q3 fires because Phase 2 flagged the TODO
- No questions about "flat vs selector-scoped" (that's an output detail, not a user-facing choice)
- No "run live MCP verification?" prompt (we already read version in Phase 2; no other MCP discovery needed)
- No fallback "if you just say go, I'll pick defaults" — the user MUST answer

---

## Phase 4 — Synthesis (sub-agent, single shot)

**Expected:** The skill dispatches the `redis-companion:acl-generator` agent again (same namespaced-name dispatch rule as Phase 2), this time in **synthesis mode**, passing:
- The discovery summary from Phase 2
- The user's answers from Phase 3

The agent applies version-aware category mapping and emits the final rule. Granularity is hardcoded to strict; defense-in-depth denies are omitted (see *v1 design choices* in Phase 3 above).

**For the demo test case** (OSS, Redis 8.6.3, leave-out speculation):

**Pass criteria — the rule must be exactly:**

```
ACL SETUSER sample-service on ><changeme> resetkeys ~activity:events ~cache:user:* ~session:* resetchannels &notifications nocommands +SET +SETEX +XADD +GET +MGET +PUBLISH
```

**Where:**
- **`sample-service`** — username auto-derived from the analyzed directory (`examples/sample-service/` → `sample-service`). If the directory name doesn't yield a valid Redis username (contains `/`, `:`, etc.), fall back to `my-service-user`.
- `><changeme>` is the **exact** placeholder (not `>password`, `>REPLACE_WITH_PASSWORD`, `>replace_with_strong_password`, etc.)
- **`resetkeys`** and **`resetchannels`** clear any prior `~pattern` and `&pattern` grants — makes the rule "self-contained" (running it twice yields the same state, not additive)
- Key patterns: `~activity:events`, `~cache:user:*`, `~session:*` (alphabetical — these are a flat list, no semantic grouping makes sense)
- Single channel: `&notifications`
- **`nocommands`** (alias for `-@all`) is the baseline deny — without this, the user could run any command not in @admin/@dangerous (e.g., `BITFIELD`, `RPOPLPUSH`). Required for true least-privilege.
- Positive grants **grouped by category, in code-flow order**: writes (`+SET +SETEX +XADD`), reads (`+GET +MGET`), pubsub (`+PUBLISH`). Strict per v1 default — no `+@category` collapse.
- No `+SUBSCRIBE` (because user picked "leave out" for Q3 speculation)
- **No trailing `-@admin -@dangerous`** — v1 omits them. With `nocommands` baseline and strict individual grants, the user has no permissions for admin/dangerous commands; adding explicit denies would remove categories that were never granted.

---

## Phase 5 — Output (dual: comprehensive `.md` + condensed prompt message)

**Expected:** The skill writes the full synthesis output to `./acl-rule-<username>.md` in cwd, then emits a condensed message in the Claude Code prompt. The long rule line itself never gets copy-pasted from the prompt — the apply path uses `grep` to extract it from the `.md`.

### Part A — The `./acl-rule-<username>.md` file (comprehensive)

Required sections, in order:

#### A.1. The `ACL SETUSER` command (or rule body for Enterprise)

```
ACL SETUSER sample-service on ><changeme> resetkeys ~activity:events ~cache:user:* ~session:* resetchannels &notifications nocommands +SET +SETEX +XADD +GET +MGET +PUBLISH
```

Must appear on its own line starting with `ACL SETUSER ` so the `grep -m1 '^ACL SETUSER'` apply pattern works.

#### A.2. Before-you-apply callout — substitute the password term

A clearly-flagged note (callout block, blockquote, or boldface line — visible enough that no one copy-pastes without seeing it):

> **⚠️ Before running:** replace `><changeme>` with your actual credential choice:
>
> - **`>YOUR_STRONG_PASSWORD`** — sets the user's password (recommended for any non-local deployment). Use a strong, randomly-generated value (`openssl rand -base64 32`).
> - **`nopass`** — allows the user to authenticate without a password. Only appropriate for local development against a Redis that has no `requirepass` set. Replace the entire `><changeme>` token (don't keep both).
>
> The `redis-companion` plugin can't make this substitution for you — the official `redis/mcp-redis` MCP server doesn't expose `ACL SETUSER`, so apply is manual.

#### A.3. Per-term annotations table

| Term | Grants | Justified by |
|------|--------|--------------|
| `on` | User enabled for authentication | (required) |
| `><changeme>` | Sets the user's password | **Replace before running.** See callout above. |
| `resetkeys` | Wipes any pre-existing `~pattern` grants on this user | Self-contained rule — re-running yields same state, not additive |
| `~activity:events` | Read/write `activity:events` stream key | `service.py:18` (`ACTIVITY_STREAM`); `service.py:44` (record_activity) |
| `~cache:user:*` | Read/write `cache:user:*` keys | `service.py:15` (`CACHE_PREFIX`); `service.py:22,26,31` (cache_user, get_user, get_users) |
| `~session:*` | Read/write `session:*` keys | `service.py:16` (`SESSION_PREFIX`); `service.py:36` (create_session) |
| `resetchannels` | Wipes any pre-existing `&pattern` grants on this user | Self-contained rule; also relevant because pub/sub defaults to restrictive on Redis 7+ |
| `&notifications` | Publish/subscribe on `notifications` channel | `service.py:17` (`NOTIFY_CHANNEL`); `service.py:41` (notify → PUBLISH) |
| `nocommands` | Deny all commands as baseline (alias for `-@all`) | Required for true least-privilege — without this, the user could run any command not explicitly denied |
| `+SET` | Single-key write | `service.py:22` (cache_user) |
| `+SETEX` | Write with TTL | `service.py:36` (create_session) |
| `+XADD` | Append to stream | `service.py:44` (record_activity) |
| `+GET` | Single-key read | `service.py:26` (get_user) |
| `+MGET` | Multi-key read | `service.py:31` (get_users) |
| `+PUBLISH` | Publish on channel | `service.py:41` (notify) |

#### A.4. "Detected context" block

```
- **Client library:** redis-py (from `requirements.txt`: redis>=5.0.0)
- **Target Redis edition:** OSS (asked)
- **Target Redis version:** 8.6.3 (read from `INFO SERVER` via MCP; effective version for filtering)
- **Permission granularity:** strict least-privilege (hardcoded in v1)
- **Defense-in-depth denies:** omitted (hardcoded in v1 — see *v1 design choices*)
- **Speculation candidate (service.py:40 TODO):** left out (asked)
- **MCP status:** connected — Redis version read from `INFO SERVER`
- **Mapping notes:** No ambiguous mappings detected
```

#### A.5. Apply patterns (multiple — for documentation; the condensed prompt only surfaces the recommended one)

- **Pattern A — Apply from this file (recommended).** `grep -m1 '^ACL SETUSER' ./acl-rule-sample-service.md | redis-cli` after editing the file, or one-liner with inline `sed`.
- **Pattern B — HEREDOC piped to `redis-cli`.**
- **Pattern C — Single-line with quoted special tokens.**
- **Pattern D — `users.acl` file for `aclfile`-configured deployments.**

#### A.6. Verify and smoke-test sections

- `redis-cli ACL GETUSER sample-service`
- `REDIS_URL='redis://sample-service:@127.0.0.1:6379' python3 examples/sample-service/service.py` → expect "6/6 operations succeeded"
- `redis-cli -u 'redis://sample-service:@127.0.0.1:6379' FLUSHDB` → expect NOPERM

### Part B — The condensed Claude Code message

Required content (terse — the user reads the prompt for *what they need next*, not for full detail):

1. **Header:** `✅ Rule generated for sample-service (Redis OSS 8.6.3, 6 commands, strict least-privilege)`
2. **The rule** in a fenced code block (so the user can see the shape of what was generated)
3. **Pointer to `./acl-rule-sample-service.md`** for per-term annotations, detected context, full apply-pattern alternatives
4. **Apply one-liner:** `sed 's/><changeme>/nopass/' ./acl-rule-sample-service.md | grep -m1 '^ACL SETUSER' | redis-cli` (plus a passworded variant)
5. **Two-step alternative** if the user prefers editing the file before applying
6. **Verify command:** `redis-cli ACL GETUSER sample-service`
7. **Smoke-test command:** `REDIS_URL='redis://sample-service:@127.0.0.1:6379' python3 examples/sample-service/service.py` (note the colon-no-password URL form)
8. **Negative-test command:** `redis-cli -u 'redis://sample-service:@127.0.0.1:6379' FLUSHDB` (expects NOPERM)
9. **Speculation note** if Q3 was answered "leave out": *"the TODO at service.py:40 was left out per your choice — re-run /redis-companion:rule once SUBSCRIBE is wired up"*

### What the output must NOT do

- Must **not** offer "Type `apply` to apply this rule" or imply that MCP can apply it. Manual `redis-cli` only.
- Must **not** dump the entire `.md` content into the Claude Code message — the dual-output design exists specifically to avoid that.
- Must **not** put a literal password in the rule body — `><changeme>` is the placeholder, never a real value.
- Must **not** copy-paste the long rule line into the apply commands — extract via `grep` from the `.md`.

---

## Failure modes to detect

If any of these happen, the test fails:

| # | Failure | Means |
|---|---------|-------|
| 1 | Skill jumps straight to synthesis without asking | Step 3 boundary broken |
| 2 | Skill asks questions in free-form text instead of via `AskUserQuestion` | Interactivity pattern not implemented |
| 3 | Skill paraphrases questions (e.g., "flat vs selectors", "live MCP verification?") | Question template not respected |
| 4 | Q3 doesn't fire despite TODO at L40 | Speculation candidate not surfaced |
| 5 | Agent calls `scan_keys`, `redis-cli` via Bash, or any data-reading MCP tool | Tool discipline broken |
| 6 | Placeholder is anything other than `><changeme>` | Placeholder drift |
| 7 | Detected-context block claims MCP can apply | False capability claim |
| 8 | Per-term annotations missing line numbers | Citations missing |
| 9 | Key patterns not alphabetical OR commands not category-grouped | Output stability broken |
| 10 | Tool call count > 15 across all phases | Workflow inefficient |

---

## Variations to also test (after the primary path passes)

Once the OSS happy-path works, also verify:

1. **Enterprise edition** (answer Q1 = Enterprise): output is rule body only (no `ACL SETUSER`, no `>password`), with admin UI / REST API instructions
2. **Redis 6** (answer Q2 = 6): output omits `@scripting` (folded into `@write`), no selectors, no `%R~`/`%W~`
3. ~~Defense-in-depth toggled off~~ — no longer applicable in v1 (always off)
4. ~~Granularity = Favor brevity~~ — no longer applicable in v1 (always strict)
5. **Q3 = Include now**: output includes `+SUBSCRIBE` and `&notifications` (already there for PUBLISH, but explicit grant is fine)
6. **No MCP connected** (`REDIS_URL` unset, Redis stopped): skill still works; Q2 must be asked (no `INFO SERVER`); detected-context says MCP not connected

These are the secondary paths the primary test (OSS, Redis 8.6.3, MCP connected, balanced, leave-out) doesn't exercise. Run the primary first; treat the variations as time permits.

---

## Notes for the implementer

- **`AskUserQuestion` is the load-bearing primitive.** It's the only Claude Code mechanism that *actually pauses* the conversation for structured user input. Natural-language instructions like "wait for the user" don't enforce a pause — the parent LLM continues with whatever defaults it picks. This is what failed in 0.1.4 through 0.1.7.
- **Two sub-agent dispatches** are fine. One for discovery (with tools limited), one for synthesis (no tools needed beyond reading the input). Sub-agent context cost is acceptable because each pass is bounded.
- **No SendMessage loop** — we're not continuing a sub-agent across user turns. Discovery and synthesis are independent. The user's answers are passed in as part of the synthesis prompt.
- **The `acl-generator` agent definition still does meaningful work** (steps 1–2, 4, 5, 6 from its prompt). What changes: step 3 is no longer in the agent — it's the skill's responsibility, executed via `AskUserQuestion`.
