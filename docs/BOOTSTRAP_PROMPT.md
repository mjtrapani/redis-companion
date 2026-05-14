# Bootstrap prompt: fork redis-companion into your domain's plugin

This is a prompt you can paste into Claude Code to have it walk you through forking `redis-companion` into a plugin for your own domain. Instead of working through the six fork steps in [BUILD_YOUR_OWN.md](../BUILD_YOUR_OWN.md) by hand, Claude will ask you targeted questions about your workflow first, then propose the file-by-file changes — and let you push back where you have domain expertise it doesn't.

## How to use it

1. **Clone the repo into your new plugin's directory:**

   ```bash
   git clone https://github.com/mjtrapani/redis-companion.git my-plugin
   cd my-plugin
   ```

2. **Open a Claude Code session in `my-plugin/`.**

3. **Paste the prompt below verbatim.** Claude will start by asking you questions about your domain before making any changes.

## The prompt

```text
I want to build a Claude Code plugin using this repository (redis-companion) as a template, forking it for my own domain.

Before making ANY changes, ask me targeted questions to understand the domain. Don't assume, and don't move on to changes until I've answered all of these:

1. **Persona** — who's the developer this plugin is for? Be specific (e.g., "backend engineers scoping Redis access" or "platform engineers rolling out Terraform").
2. **Output artifact** — what configuration does the plugin generate? Examples: a permission policy, a deployment manifest, an API contract, a generated client, a security rule.
3. **Syntax/grammar** — what notation is the artifact in? Examples: Postgres `GRANT` statements, Kubernetes YAML, JSON IAM policy, OpenAPI schema, Terraform HCL.
4. **What's inferable from code** — what should the agent extract from the user's codebase to inform the artifact? Examples: tables/columns accessed, K8s API resources used, AWS SDK calls made, secrets referenced.
5. **What CAN'T be inferred** — what does the agent need to ASK the user about (because no amount of code-reading would reveal it)? Examples: target deployment edition, security posture, compliance constraints, multi-tenancy boundaries.
6. **Credential shapes** — what credentials or sensitive values does this domain have that the hook should block? Examples: AWS access keys (`AKIA*`), Postgres connection strings (`postgresql://...`), JWT secrets, kubeconfig tokens.
7. **MCP availability** — is there an existing MCP server for this domain (e.g., postgres-mcp, kubernetes-mcp, AWS MCP)? If not, that's fine — the plugin can operate in degraded mode without live validation.

After I've answered, walk me through the fork file-by-file:

- Update `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` with the new plugin's name, description, and (if applicable) MCP server config.
- Replace `skills/acl-reference/` with my domain's knowledge base — rename the directory, update the `description` in `SKILL.md` so it fires on domain-relevant keywords, and replace the reference docs with my syntax, version deltas (if applicable), client/library patterns, and resource-extraction heuristics.
- Adapt `agents/acl-generator.md` for my two-mode contract: DISCOVERY (detect my domain's artifacts in code) and SYNTHESIS (compose the rule + write the markdown report).
- Adapt `hooks/credential-guard.py` `PATTERNS` regexes for my domain's credential shapes. Keep the placeholder allow-list — that's how the agent's own output passes through unmolested.
- If an MCP exists for my domain, wire it in `plugin.json`'s `mcpServers` block. If not, leave that block empty and document that the plugin operates without live validation.
- Update `README.md` for my persona, install steps, and honest limitations.

**Critical instructions for you (Claude):**

- Be honest about what redis-companion's patterns won't cleanly transfer to my domain. Examples I should expect:
  - My domain might need a different question flow (more or fewer baseline questions)
  - The "method name = command name" convention from client libraries may have no analog
  - The dual-output design (long artifact in `.md` + `grep`-extracted apply command) may or may not make sense depending on whether my artifact has shell-special characters
  - The `>50%` category-collapse rule is Redis-ACL-specific
- **Push back when you'd be guessing.** Tell me explicitly which decisions need my domain expertise to verify. Don't write code you can't defend in a code review.
- **Don't do everything at once.** Work through changes in passes — get questions answered first, then make one component's changes at a time so I can sanity-check before you move to the next.
```

## What to expect

- **It'll take a few rounds.** Claude will ask questions, you'll answer, it'll propose changes, you'll correct or refine. The first pass won't be perfect.
- **You'll catch errors.** That's the point. Claude tends to default to confident drafts that look right but are subtly under-sourced. Catching that is exactly what your domain expertise is for — see the [*"pick a domain you can steer Claude in as a peer"*](../BUILD_YOUR_OWN.md#before-you-start-pick-a-domain-you-can-steer-claude-in-as-a-peer) section of the guide.
- **Some parts won't transfer.** redis-companion has specific patterns (the version-deltas concept, the speculation-candidate question, the `commands.json`-derived category map) that may not have analogs in your domain. Drop what doesn't apply.

## When to read the long-form guide instead

If Claude proposes something and you don't understand *why* redis-companion does it that way, switch to [BUILD_YOUR_OWN.md](../BUILD_YOUR_OWN.md) for the explanation. The bootstrap prompt is the shortcut; the guide is the reference.
