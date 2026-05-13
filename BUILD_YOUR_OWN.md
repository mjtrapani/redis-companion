# Build your own plugin

A guide for engineers who like the *shape* of `redis-companion` and want to apply it to a different workflow in their own org. You're forking the pattern, not the contents.

---

## What you're building

A Claude Code plugin that reads code in your repo and emits a piece of configuration — a permission policy, a deployment spec, a generated client, an API contract — with per-clause annotations explaining *why* each part is there. The value isn't the artifact; it's that the agent reads your code and can explain the output back to you in your terms.

## The shape that worked here

Four cooperating components, each doing one job:

| Component | Job | Why separate? |
|-----------|-----|---------------|
| **Skill** (knowledge) | Authoritative reference content — syntax, version deltas, mappings. Auto-loads on relevant conversation. | Reusable across agents and across sessions. Updating the syntax reference is a doc change, not a code change. |
| **Agent** (task) | The specific workflow: scan code → ask the user → synthesize → emit annotated output. Read-only filesystem, dedicated tool allowlist. | One agent = one task. Keeps the workflow legible and testable. Inherits skills + MCP tools from the session. |
| **Hook** (guardrail) | Local safety net — blocks committed credentials, malformed configs, or other "you didn't mean to do that" cases on `PreToolUse`. | Defense-in-depth. The agent could be perfect and the user could still paste a secret into a file by hand. The hook catches that. |
| **MCP** (live state) | External tool integration — talk to the target system itself (Redis, Postgres, K8s, AWS, etc.) for live validation, current-state queries, or (with explicit confirmation) actual application of the generated artifact. | Plugs you into the ecosystem without rebuilding it. When connected, the agent can sanity-check its output against reality and (carefully) close the loop. |

**Why this separation matters**: it lets the *agent* stay focused on its workflow, the *skill* stay focused on knowledge, the *hook* stay focused on safety, and the *MCP* stay focused on external integration. Each can be updated independently. A customer forking your plugin replaces the skill's reference docs and the agent's domain instructions — without rewriting anything else.

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

   The skill (`skills/redis-acl-patterns/`) becomes your domain's knowledge base. Rename the directory (e.g., to `postgres-grant-patterns`), update the `description` frontmatter in `SKILL.md` so it fires on your domain's keywords, and replace the four reference docs with your domain's syntax, version deltas, client-library patterns, and resource-extraction heuristics.

3. **Adjust the agent's system prompt**

   Open `agents/acl-generator.md` and rename it (e.g., `agents/grant-generator.md`). The 7-step process is reusable as scaffolding — keep the structure (load skill → discover from code → batched ask → optional MCP discovery → synthesize → emit → optional safety-gated apply). Replace:
   - Step 2: detection patterns for your domain's client libraries
   - Step 2b–2d: resource extraction (replace key/channel/stream with your domain's resource types)
   - Step 3 questions: the batched ask. Keep the *pattern* (ask, don't infer, batch the questions). Replace the *contents* with what your domain needs.
   - Step 5: synthesis logic. The `>50%` rule is Redis-specific — your domain may have different collapse heuristics.
   - Step 6: output shape. Match your domain's deployment formats.

4. **Adapt the hook's pattern matchers**

   `hooks/credential-guard.py` has a `PATTERNS` list of regexes for Redis credentials. Replace them with your domain's credential shapes (Postgres connection strings, kubeconfig tokens, AWS access keys, etc.). Keep the placeholder allow-list — it's how the agent's own output passes through unmolested.

5. **Swap the MCP**

   `.mcp.json` points at the Redis MCP server. Replace with the MCP server for your domain. Many domains have one already published (Postgres, Kubernetes, AWS, GitHub, Stripe, etc.). If your domain doesn't yet, the plugin still works without MCP — the agent just operates in degraded mode (no live validation, no apply).

6. **Update the README and this guide**

   Replace the persona description, install instructions are mostly the same. Adapt the demo to your sample target. Be honest about limitations — what your agent can and can't infer reliably.

## The principle

What makes this shape work is that **the agent reads your code and explains its output**. Any "translate intent to syntax" workflow fits — wherever a developer has to manually translate "what my service does" into a configuration artifact written in someone else's grammar, this pattern saves real time and reduces real mistakes.

The skill is *what the agent needs to know to be correct*. The agent is *the workflow*. The hook is *the safety net for the moments the agent isn't there*. The MCP is *the connection to reality* — what's actually deployed, what currently works, and (carefully) how to apply the generated artifact.

Each piece is independently editable. Each piece has one job. Together they let a domain expert ship a plugin that captures their org's specific judgment in a tool any backend engineer can run from their editor.

That's the shape. Make it yours.
