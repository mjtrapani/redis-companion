# Build your own plugin

A guide for engineers who like the *shape* of `redis-companion` and want to apply it to a different workflow in their own org. You're forking the pattern, not the contents.

---

## What you're building

A Claude Code plugin that reads code in your repo and emits a piece of configuration — a permission policy, a deployment spec, a generated client, an API contract — with per-term annotations explaining *why* each part is there. The value isn't the artifact; it's that the agent reads your code and can explain the output back to you in your terms.

## The shape that worked here

Four cooperating components, each doing one job:

| Component | Job | Why separate? |
|-----------|-----|---------------|
| **Skill** (knowledge) | Authoritative reference content — syntax, version deltas, mappings. Auto-loads on relevant conversation. | Reusable across agents and across sessions. Updating the syntax reference is a doc change, not a code change. |
| **Agent** (task) | The specific workflow: scan code → ask the user → synthesize → emit annotated output. Read-only filesystem, dedicated tool allowlist. | One agent = one task. Keeps the workflow legible and testable. Inherits skills + MCP tools from the session. |
| **Hook** (guardrail) | Project-level invariant enforced from outside the agent. Scans every `Write`/`Edit` Claude makes for a domain-specific failure shape (here: literal credentials) and blocks the call if it matches. | The agent's output contract is "never embed a real credential in the file." The hook is what keeps that contract enforced if the agent ever stops honoring it — model drift, prompt injection, or the user asking Claude to "just save my password somewhere." Defense-in-depth, and the most portable piece across forks. |
| **MCP** (live state) | External tool integration — talk to the target system itself (Redis, Postgres, K8s, AWS, etc.) for live validation, current-state queries, or (with explicit confirmation) actual application of the generated artifact. | Plugs you into the ecosystem without rebuilding it. When connected, the agent can sanity-check its output against reality and (carefully) close the loop. |

**Why this separation matters**: it lets the *agent* stay focused on its workflow, the *skill* stay focused on knowledge, the *hook* stay focused on safety, and the *MCP* stay focused on external integration. Each can be updated independently. A customer forking your plugin replaces the skill's reference docs and the agent's domain instructions — without rewriting anything else.

## Two patterns inside the shape worth borrowing

**Three-phase orchestration (skill → sub-agent → user → sub-agent).** Claude Code sub-agents run single-shot — they can't pause mid-execution to ask the user a question. So the user-interactive step lives in the *skill* (the orchestrator in the main conversation), via `AskUserQuestion`, between two stateless sub-agent dispatches: DISCOVERY (read code, return structured summary) → batched ask → SYNTHESIS (compose the artifact from the summary + answers). Keeps the sub-agent context-bounded and lets the user steer with structured choices instead of free-text.

**Dual output (condensed prompt + comprehensive `.md` file).** Long generated artifacts get mangled by terminal copy-paste — word-wrap inserts hard breaks, shell-special chars need quoting, heredoc indentation breaks the terminator. Write the full artifact to a file in the user's cwd, then surface a short *extraction command* in the prompt: `grep -m1 '^ACL SETUSER' ./acl-rule-<user>.md | redis-cli`. The user copies a one-liner; the artifact itself is never copy-pasted. Generalizes to any domain where the artifact is more than ~120 chars (GRANT scripts, RBAC YAML, IAM JSON).

## Three concrete adaptations

Same shape, different domain. Each one is a real plugin idea you could ship in a day.

### Postgres role builder

| Component | What it becomes |
|-----------|----------------|
| Skill | Postgres `GRANT` syntax, role inheritance, RLS policies. Per-version differences (PG 14 vs 16 — predefined roles, RLS bypass). |
| Agent | Scans for SQL queries and ORM usage (psycopg, SQLAlchemy, GORM, ActiveRecord). Identifies tables/schemas read and written. Emits a tailored `CREATE ROLE` + `GRANT` script. |
| Hook | Blocks committed Postgres connection strings (`postgresql://user:pw@...`). |
| MCP | A Postgres MCP server. With it: query `\du`, `\dp`, `pg_policy` to verify existing roles, and optionally apply the generated GRANTs in a transaction with a rollback option. |

### Kubernetes RBAC builder

| Component | What it becomes |
|-----------|----------------|
| Skill | K8s API resources (verbs, groups, resources), `Role` vs `ClusterRole`, `RoleBinding` vs `ClusterRoleBinding`, aggregated cluster roles. |
| Agent | Scans Helm charts / Kustomize / raw manifests + client-go / kubernetes-client usage. Identifies API objects accessed, namespaces touched, verbs needed. Emits `Role` + `RoleBinding` YAML. |
| Hook | Blocks committed kubeconfig files with embedded tokens or certificate data. |
| MCP | A Kubernetes MCP server. With it: query existing RBAC via `kubectl auth can-i`, check for naming collisions, and (in dev clusters) apply the manifests. |

### AWS IAM policy builder

| Component | What it becomes |
|-----------|----------------|
| Skill | IAM policy JSON structure — actions, resources, conditions, principals. Service-specific action namespaces (`s3:`, `sqs:`, `dynamodb:`). Predefined AWS managed policies. |
| Agent | Scans for AWS SDK usage (boto3, aws-sdk-js, aws-sdk-go). Identifies services, actions, and resource ARNs from code. Emits a minimum-privilege policy JSON. |
| Hook | Blocks committed AWS access keys (`AKIA*`, `aws_access_key_id=*`). |
| MCP | An AWS MCP server. With it: query existing roles and policies, use `iam:SimulateCustomPolicy` to verify the generated policy allows the intended actions and denies the rest. |

## Steps to fork

1. **Clone and rename**

   ```bash
   git clone https://github.com/mjtrapani/redis-companion.git my-plugin
   cd my-plugin
   ```

   Edit `.claude-plugin/plugin.json` — update `name`, `description`, `author`. The `name` becomes your plugin's namespace prefix (e.g., `name: "postgres-companion"` → slash command `/postgres-companion:analyze`).

2. **Replace the skill's reference docs**

   The skill (`skills/acl-reference/`) becomes your domain's knowledge base. Rename the directory (e.g., to `postgres-grant-patterns`), update the `description` frontmatter in `SKILL.md` so it fires on your domain's keywords, and replace the four reference docs with your domain's syntax, version deltas, client-library patterns, and resource-extraction heuristics.

   Two implementation notes that will save you an hour:
   - **Reference paths**: when the agent reads these docs, use `${CLAUDE_SKILL_DIR}/references/<file>.md` in the agent prompt, not a relative path. Sub-agents inherit cwd from the user's invocation, not the plugin cache — relative paths silently read the wrong file (or fail outright).
   - **Derive from upstream when possible**: if your domain has a source-of-truth artifact (a command JSON list, an API spec, an OpenAPI doc), generate your reference docs from it rather than hand-curating. We do this with `scripts/build-category-map.py`, which pulls `Since:` annotations from `redis/redis@8.6.3/src/commands/*.json` for 422 commands. Regenerating from upstream is a one-liner; staying in sync with upstream changes is automatic.

3. **Adjust the agent's two modes**

   Open `agents/acl-generator.md` and rename it (e.g., `agents/grant-generator.md`). The agent has two modes — the orchestrator skill dispatches each in a separate sub-agent call:
   - **DISCOVERY** (steps D1–D9): scans code, returns a structured summary. Replace the detection patterns for your domain's client libraries and the resource-extraction logic (key/channel/stream → your domain's resource types).
   - **SYNTHESIS** (steps S1–S3): takes the discovery summary plus the user's batched answers and composes the artifact. Replace the category-mapping logic, the collapse heuristic (the `>50%` rule is Redis-specific — your domain may have different ones), and the output shape.

   The user-interactive step lives in `skills/rule/SKILL.md`, not the agent — that's where you replace the `AskUserQuestion` question set with your domain's choices (in this plugin: edition and version; you'd add whatever's not detectable for your domain). Keep the *pattern* (ask the user only what you can't detect, don't infer, batch within the 4-questions-per-call limit). Resist the urge to add questions just because you can — every question is on-camera explanation cost for the user. This plugin originally had four questions and was cut to two after live testing showed the extras were either redundant or confusing.

   **Optional: specify a model.** The agent has `model: claude-sonnet-4-6` in its frontmatter. Specifying `model:` is optional — useful for picking a cheaper or faster model when the sub-agent's job is procedural (follow steps, look things up in your reference docs) rather than open-ended reasoning. **Tightening the prompt does more for correctness than model selection** — early Opus runs of this agent reasoned creatively that `PUBLISH` belongs in `@write` because "publishing writes to channels," and the fix was a stricter S1 instruction ("use the map verbatim, do not infer from semantic similarity"), not the model swap.

4. **Adapt the hook's pattern matchers**

   `hooks/credential-guard.py` has a `PATTERNS` list of regexes for Redis credentials. Replace them with your domain's credential shapes (Postgres connection strings, kubeconfig tokens, AWS access keys, etc.). Keep the placeholder allow-list — it's how the agent's own output (which uses `<changeme>` and friends) passes through. The hook's value is in being the *outside-the-agent* enforcement of "no real credentials touch disk via Claude in this repo" — your domain's customer gets the same guarantee for free as long as your regex set is reasonably complete.

   **Scope to be aware of** before you advertise the hook as a guarantee:
   - **Disk only, not prompt output.** `PreToolUse` on `Write` / `Edit` / `MultiEdit` means the hook sees file writes. It doesn't scan text the agent emits to the conversation — that safety lives in the agent's prompt design.
   - **Low-entropy values pass through.** The allow-list contains `password`, `secret`, `xxx`, `redacted`, etc. — necessary to avoid blocking docstring examples, but it means a real credential that happens to be the string `secret` won't be caught. Entropy-scoring is a meaningful refinement if your domain has stricter compliance requirements.
   - **Only the new content of the write.** The hook scans `tool_input.content` for Write, `new_string` for Edit / MultiEdit. It doesn't read the file's existing on-disk contents — an already-present credential won't be discovered.

5. **Swap the MCP**

   The `mcpServers` block in `.claude-plugin/plugin.json` declares the Redis MCP server. Replace with the MCP server for your domain. Many domains have one already published (Postgres, Kubernetes, AWS, GitHub, Stripe, etc.). If your domain doesn't yet, the plugin still works without MCP — the agent just operates in degraded mode (no live validation, no apply).

6. **Update the README and this guide**

   Replace the persona description, install instructions are mostly the same. Adapt the demo to your sample target. Be honest about limitations — what your agent can and can't infer reliably.

## The principle

What makes this shape work is that **the agent reads your code and explains its output**. Any "translate intent to syntax" workflow fits — wherever a developer has to manually translate "what my service does" into a configuration artifact written in someone else's grammar, this pattern saves real time and reduces real mistakes.

The skill is *what the agent needs to know to be correct*. The agent is *the workflow*. The hook is *the safety net for the moments the agent isn't there*. The MCP is *the connection to reality* — what's actually deployed, what currently works, and (carefully) how to apply the generated artifact.

Each piece is independently editable. Each piece has one job. Together they let a domain expert ship a plugin that captures their org's specific judgment in a tool any backend engineer can run from their editor.

That's the shape. Make it yours.
