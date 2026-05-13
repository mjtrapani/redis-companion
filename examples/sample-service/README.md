# sample-service

A ~30-line redis-py service used as a fixture for the `redis-companion` plugin.

## What it does

A toy backend that:

- Caches user profiles (`cache:user:<id>`)
- Stores session tokens (`session:<token>`)
- Publishes notifications on the `notifications` channel
- Appends to an `activity:events` stream

It uses these Redis commands: `SET`, `GET`, `MGET`, `SETEX`, `PUBLISH`, `XADD`.

## Why it exists

This is the demo target for the plugin's `acl-generator` agent. Point the agent at
this directory and it will:

1. Detect `redis-py` from the import
2. Infer the key patterns (`cache:user:*`, `session:*`) and pubsub/stream names
3. Map the call sites to the minimum command set + categories needed (`@read`, `@write`, `@pubsub`, `@stream`)
4. Emit a tailored Redis ACL rule (the deployment-agnostic permission DSL) with per-term annotations
5. Note how to apply the rule in Redis OSS / Cloud (`ACL SETUSER`) vs Redis Enterprise (ACL Rule object via REST API or admin UI)
6. Optionally validate the rule against a live Redis if a Redis MCP server is connected

## Try it

From the plugin root, open Claude Code and run:

```text
/redis-companion:acl-generator examples/sample-service/
```

You should see a generated `ACL SETUSER` block followed by a per-term explanation.

## Run it (optional)

The service won't actually do anything useful without a Redis instance, but if
you want to verify it imports cleanly:

```bash
pip install -r requirements.txt
python -c "import service; print('imports ok')"
```
