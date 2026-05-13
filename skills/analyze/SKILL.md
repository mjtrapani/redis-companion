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

**Q2 — Target Redis major version:**

If Phase 1's discovery summary included a version from `INFO SERVER` (e.g., `8.6.3`), present this as a CONFIRMATION:
- header: "Version"
- question: "I see **Redis <X.Y.Z>** from `INFO SERVER`. Use Redis <X> as the target?"
- options:
  - label: "Yes, Redis <X>" — description: "Matches the live server (recommended)."
  - label: "Redis 7" — description: "Override; generating rule for a different deployment."
  - label: "Redis 6" — description: "Override; generating rule for a much older deployment."

(Omit the "Yes, Redis <X>" option if `<X>` is already 6 or 7. Always include all options not already shown.)

If MCP did NOT provide a version, present as an open question:
- header: "Version"
- question: "Which Redis major version is the target server?"
- options:
  - label: "Redis 8" — description: "Most recent. Standard categories include module commands (Search, JSON, TS, probabilistic)."
  - label: "Redis 7" — description: "@scripting is its own category; selectors and `%R~`/`%W~` available; pub/sub default-deny."
  - label: "Redis 6" — description: "@scripting lives inside @write; no selectors; pub/sub default permissive."

**Q3 — Defense-in-depth denies:**
- header: "Deny clauses"
- question: "Include explicit deny clauses (`-@admin -@dangerous`) even when those categories aren't used by the service?"
- options:
  - label: "Yes (recommended)" — description: "Industry best practice for service accounts. Prevents accidental category-grant overreach (e.g., `+@write` would otherwise pull in `FLUSHDB`)."
  - label: "No" — description: "Only emit positive grants. Tighter rule body, but relies on you to remember the denies in your provisioning script."

**Q4 — Permission granularity:**
- header: "Granularity"
- question: "Which permission granularity do you want?"
- options:
  - label: "Strict least-privilege" — description: "Grant only the specific commands your code uses. Never collapse to category, regardless of usage percentage."
  - label: "Balanced (recommended)" — description: "If >50% of a category's commands are used, ask whether to collapse. Else, individual grants."
  - label: "Favor brevity" — description: "Auto-collapse to `+@category` whenever >50% is used. Shorter rule, slightly broader access."

**Q5 (conditional — only if Phase 1 surfaced speculation candidates):**

For each speculation candidate in Phase 1's discovery summary, add a question. For example, a TODO at service.py:40 suggesting `SUBSCRIBE` is planned:
- header: "Speculation"
- question: "I noticed a `# TODO: add a subscribe handler` at service.py:40, suggesting `SUBSCRIBE` may be added later. Include `+SUBSCRIBE` and `&notifications` channel grants now?"
- options:
  - label: "Include now" — description: "Grant `+SUBSCRIBE` and the `&notifications` channel for subscribe. Rule covers the planned addition without re-running."
  - label: "Leave out (recommended)" — description: "Stricter least-privilege. Re-run me when subscribe is actually wired up."

Call `AskUserQuestion` ONCE with all the above questions in a single call. Do not split into multiple calls. Do not narrate before/after the call — let the structured UI carry the interaction.

### Phase 3 — Synthesis (sub-agent)

Spawn the `acl-generator` agent again with this prompt:

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
> - Version: <answer to Q2>
> - Defense-in-depth denies: <answer to Q3>
> - Granularity: <answer to Q4>
> - Speculation candidates: <answer(s) to Q5, one per candidate>
>
> Run steps 5 (synthesize), 6 (emit output) from your standard process. Apply version-aware category filtering using the upstream-derived `command-category-map.md` and `version-deltas.md`. Use the username derived from the analyzed directory's basename (`<basename of $ARGUMENTS>`) — if it has invalid Redis username chars, fall back to `my-service-user`.
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
