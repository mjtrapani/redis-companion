---
description: Synthesize a least-privilege Redis ACL rule for the codebase at the given path. Use when invoked via `/redis-companion:analyze <path>` or when the user explicitly asks to analyze a service for Redis ACL synthesis with a path argument. Dispatches to the `acl-generator` agent.
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

Then stop. Do not invoke the agent without a path.

## If `$ARGUMENTS` contains a path

Invoke the `acl-generator` subagent via the Task tool. Pass it this prompt:

> Analyze the codebase at `$ARGUMENTS` for Redis client usage and synthesize a least-privilege Redis ACL rule. Follow your standard process — discover (steps 1–2), batched ask (step 3), optional MCP discovery (step 4), synthesize (step 5), emit output (step 6), and offer the safety-gated apply workflow (step 7) if appropriate.

Do **not** attempt the analysis yourself in this conversation. The work belongs to the agent — it has its own context window, tool allowlist, and access to the `redis-acl-patterns` skill content. Delegating ensures the workflow runs as designed and your main conversation isn't flooded with grep/read results.

After dispatching, wait for the agent's response and surface it to the user as-is.
