---
description: Synthesize a least-privilege Redis ACL rule for the codebase at the given path. Use when invoked via `/redis-companion:analyze <path>` or when the user explicitly asks to analyze a service for Redis ACL synthesis with a path argument. Orchestrates the `acl-generator` agent across two phases (discovery, synthesis) and gathers user input between them via `AskUserQuestion`.
---

# Analyze a service for Redis ACL synthesis

The user requested analysis of the path: `$ARGUMENTS`

## If `$ARGUMENTS` is empty or missing

Respond exactly with:

> The `/redis-companion:analyze` command needs a path argument.
>
> **Usage:** `/redis-companion:analyze <path>`
>
> **Example:** `/redis-companion:analyze ./my-service`
>
> If you want a more conversational entry point, just say something like *"scope a Redis ACL for ./my-service"* and Claude will route you to the `acl-generator` agent.

Then stop. Do not proceed without a path.

---

## If `$ARGUMENTS` contains a path — the three-phase orchestration

You will run this analysis in **three phases**: discovery (sub-agent), batched ask (`AskUserQuestion`), and synthesis (sub-agent). Do not deviate from the order. Do not skip phases. Do not attempt the analysis yourself outside these phase boundaries.

Why this structure exists: Claude Code sub-agents run single-shot — they can't pause mid-response to ask the user a question. So the interactive step lives in the skill (here, in the main conversation), via `AskUserQuestion`, between two stateless sub-agent dispatches. Read `.spec/EXPECTED_BEHAVIOR.md` if it's available to you for the full test oracle.

### Phase 1 — Discovery (sub-agent)

Spawn the `acl-generator` sub-agent via the Task tool with this prompt:

> **Mode: DISCOVERY ONLY.**
>
> Analyze the codebase at `$ARGUMENTS` for Redis client usage. Run steps 1, 2, and 2h from your standard process (load reference knowledge, scan codebase, INFO SERVER via MCP if connected). Then **return a structured discovery summary and stop. Do not ask any questions. Do not synthesize a rule.**
>
> Your structured summary must include:
> - **Client library** (name + how detected, e.g., `redis-py` from `from redis import Redis` in service.py:10)
> - **Commands used** (table: call site → method → Redis command)
> - **Key patterns** (table: pattern → constant or literal source → call sites using it)
> - **Channel patterns** (same shape as keys, but `&` prefix)
> - **Stream keys** (same shape as keys, but note these are stream-typed)
> - **Speculation candidates** (TODO/FIXME comments near Redis calls that imply future commands — e.g., a `# TODO: add subscribe` near `r.publish(...)`). For each: file path, line number, comment text, and what command(s) it implies.
> - **Server version from `INFO SERVER`** if MCP is connected (else: note "MCP not connected")
> - **Mapping notes** (any ambiguous client-library method→command mappings you flagged via step 2g)
>
> Permitted tools: `Read`, `Grep`, `Glob`, `Skill` (for loading `redis-acl-patterns` once), `mcp__plugin_redis-companion_redis__info` (INFO SERVER, once), `WebFetch` (one-shot, for ambiguous mappings). Forbidden: `Bash`, any data-reading MCP tool (`scan_keys`, `get`, `hgetall`, etc.).

Wait for the agent's return. Read the discovery summary carefully — you will use it to format Phase 2 questions and pass it back to the agent in Phase 3.

### Phase 2 — Batched ask (AskUserQuestion)

Use the `AskUserQuestion` tool to ask the user **all baseline questions at once, plus Q5 if Phase 1 surfaced any speculation candidates**. This is the only Claude Code primitive that actually pauses the conversation for structured user input — natural-language "wait for the user" instructions don't enforce a pause.

Construct the question set as follows.

**Q1 — Target Redis edition:**
- header: "Edition"
- question: "Which Redis edition is this rule for?"
- options:
  - label: "Open Source (Redis OSS)" — description: "I'll emit a full `ACL SETUSER` command runnable via `redis-cli`."
  - label: "Enterprise (Redis Software / Cloud)" — description: "I'll emit just the rule body for the ACL Rule object (paste into admin UI or REST API)."

**Rule for option ordering: the recommended / safest / most-common option ALWAYS goes first.** The Claude Code UI cursor defaults to the first option, so the default choice should be the one most users want.

**Q2 — Target Redis major version:**

If Phase 1's discovery summary included a version from `INFO SERVER` (e.g., `8.6.3`), present this as a CONFIRMATION with the live-server version FIRST:
- header: "Version"
- question: "I see **Redis <X.Y.Z>** from `INFO SERVER`. Use Redis <X> as the target?"
- options:
  - label: "Yes, Redis <X>" — description: "Matches the live server (recommended). Effective version <X.Y.Z>."
  - label: "Redis <X-1>" — description: "Override; generating rule for a different deployment."
  - label: "Redis <X-2>" — description: "Override; generating rule for a much older deployment."

(Always order: confirm-live-version first, then descending. If MCP read 6.x or 7.x, only include the older option(s).)

If MCP did NOT provide a version, present as an open question. **Order: newest version FIRST** (Redis 8 = most-likely target for greenfield, most-features):
- header: "Version"
- question: "Which Redis major version is the target server?"
- options:
  - label: "Redis 8" — description: "Most recent stable. Standard categories include module commands."
  - label: "Redis 7" — description: "@scripting is its own category; selectors and `%R~`/`%W~` available; pub/sub default-deny."
  - label: "Redis 6" — description: "@scripting lives inside @write; no selectors; pub/sub default permissive."

**If MCP didn't provide a version AND the user picked a major, fire a SECOND `AskUserQuestion` for the minor version.** Order: latest minor of that major FIRST (recommended; matches what the upstream-derived map covers most precisely):

If user picked **Redis 8**:
- header: "Minor version"
- question: "Which Redis 8 minor version is the target? (This affects which 8.x-added commands are eligible — e.g., `HSETEX` was added in 8.0, `MSETEX` in 8.4.)"
- options:
  - label: "Redis 8.6 (recommended — latest stable)" — description: "Effective version 8.6. All Redis 8 features and commands eligible."
  - label: "Redis 8.4" — description: "Effective version 8.4. Commands added in 8.6 excluded."
  - label: "Redis 8.2" — description: "Effective version 8.2. Commands added in 8.4+ excluded."
  - label: "Redis 8.0" — description: "Effective version 8.0. Commands added in 8.2+ excluded."

If user picked **Redis 7**:
- header: "Minor version"
- question: "Which Redis 7 minor version is the target?"
- options:
  - label: "Redis 7.4 (recommended — latest stable)" — description: "Effective version 7.4. Includes hash-field-TTL commands (HEXPIRE, HPEXPIRE, etc.)."
  - label: "Redis 7.2" — description: "Effective version 7.2. Selectors available; HEXPIRE family excluded."
  - label: "Redis 7.0" — description: "Effective version 7.0. No selectors-with-%R~/%W~; no HEXPIRE family."

If user picked **Redis 6**:
- header: "Minor version"
- question: "Which Redis 6 minor version is the target?"
- options:
  - label: "Redis 6.2 (recommended — latest 6.x)" — description: "Effective version 6.2. Channel ACLs available; BITFIELD_RO added."
  - label: "Redis 6.0" — description: "Effective version 6.0. No channel ACLs; minimal ACL feature set."

**Q3 — Defense-in-depth denies:**
- header: "Deny clauses"
- question: "Include explicit deny clauses (`-@admin -@dangerous`) even when those categories aren't used by the service?"
- options:
  - label: "Yes (recommended)" — description: "Industry best practice for service accounts. Prevents accidental category-grant overreach (e.g., `+@write` would otherwise pull in `FLUSHDB`)."
  - label: "No" — description: "Only emit positive grants. Tighter rule body, but relies on you to remember the denies in your provisioning script."

**Q4 — Permission granularity** (Balanced first — it's the recommended default):
- header: "Granularity"
- question: "Which permission granularity do you want?"
- options:
  - label: "Balanced (recommended)" — description: "If >50% of a category's commands are used, ask whether to collapse. Else, individual grants."
  - label: "Strict least-privilege" — description: "Grant only the specific commands your code uses. Never collapse to category, regardless of usage percentage."
  - label: "Favor brevity" — description: "Auto-collapse to `+@category` whenever >50% is used. Shorter rule, slightly broader access."

**Q5 (conditional — only if Phase 1 surfaced speculation candidates):**

For each speculation candidate, add a question. **Leave out first — it's the safer default.** For example, a TODO at service.py:40 suggesting `SUBSCRIBE` is planned:
- header: "Speculation"
- question: "I noticed a `# TODO: add a subscribe handler` at service.py:40, suggesting `SUBSCRIBE` may be added later. Include the planned grants now or leave them out?"
- options:
  - label: "Leave out (recommended)" — description: "Stricter least-privilege. Re-run me when subscribe is actually wired up."
  - label: "Include now" — description: "Grant `+SUBSCRIBE`. Rule covers the planned addition without re-running."

**Calling `AskUserQuestion`:** the platform limit is 4 questions per call. Plan your calls:

- **With MCP-provided version + speculation candidates:** Call 1 = Q1, Q2 (confirm), Q3, Q4 (4 questions). Call 2 = Q5 only.
- **With MCP-provided version, no speculation:** Single call = Q1, Q2 (confirm), Q3, Q4.
- **No MCP version + speculation candidates:** Call 1 = Q1, Q2 (major), Q3, Q4. Call 2 = minor-version follow-up for the user's Q2 major answer. Call 3 = Q5.
- **No MCP version, no speculation:** Call 1 = Q1, Q2 (major), Q3, Q4. Call 2 = minor-version follow-up.

Do not narrate before/after the calls — let the structured UI carry the interaction.

### Phase 3 — Synthesis (sub-agent)

**Compute the effective target version before dispatching.** This is how minor-version filtering works:

- **If Phase 1's discovery summary included a `redis_version` from `INFO SERVER` (e.g., `8.6.3`):** use that exact version. The agent will filter the category map by `Since: <= 8.6.3`, so commands like `HEXPIRE` (Since 7.4.0) are included only if 7.4.0 ≤ 8.6.3 — yes, included.
- **If Phase 1 reported "MCP not connected":** the user picked both major (Q2 major) and minor (the follow-up minor-version question). Combine into a precise version cutoff, e.g., "Redis 7.4" → effective version `7.4`. Filter by `Since: <= 7.4`. No assumption needed — the user told us.

Spawn the `acl-generator` agent with this prompt:

> **Mode: SYNTHESIS.**
>
> Here is the discovery summary from Phase 1:
>
> ```
> <paste the full Phase 1 return verbatim>
> ```
>
> The user answered:
> - Edition: <answer to Q1>
> - Version (major): <answer to Q2>
> - Defense-in-depth denies: <answer to Q3>
> - Granularity: <answer to Q4>
> - Speculation candidates: <answer(s) to Q5, one per candidate>
>
> **Effective target version for filtering: `<exact_version>`** (either from `INFO SERVER` directly, or the assumed latest minor of the user's major-version pick — state which one explicitly here). Filter the `command-category-map.md` such that only commands with `Since: <= <exact_version>` are eligible. Surface this version assumption in the Detected Context output.
>
> Run S1 (map commands → categories with version filtering), S2 (decide grant strategy), S3 (compose rule body), and emit the OSS or Enterprise output per the user's edition answer. Use the username derived from the analyzed directory's basename (`<basename of $ARGUMENTS>`) — if it has invalid Redis username chars, fall back to `my-service-user`.
>
> Required output sections, in order:
> 1. The `ACL SETUSER <user> on ><changeme> ...` command (OSS) or rule body only (Enterprise)
> 2. A clearly-flagged callout block before apply instructions explaining how to substitute the password: `><strong_password>` for non-local deployments, `nopass` (replacing the whole `><changeme>` token) for local-dev Redis without auth
> 3. Per-term annotation table with source line citations from the discovery summary
> 4. "Detected context" block (client library, edition, version + how known, defense-in-depth, granularity, MCP status, mapping notes)
> 5. How to apply — `redis-cli` examples for both password and `nopass` cases
> 6. Do NOT offer "type apply" — MCP can't run `ACL SETUSER`
>
> Forbidden tools: any tool that reads or writes data; this phase is text-only synthesis from the inputs above.

Surface the agent's final output to the user as-is.

---

## Important constraints

- **Never skip Phase 2.** Even if you think you can infer the answers from the discovery summary, you MUST call `AskUserQuestion`. The user's answer is authoritative; your inference is not.
- **Never bake speculation candidates into the rule** without asking Q5.
- **Never claim live apply works.** Output must reflect that apply is manual via `redis-cli`.
- **Don't dump the Phase 1 summary to the user verbatim.** The user sees the questions (Phase 2) and the final rule (Phase 3). Discovery is internal context.
