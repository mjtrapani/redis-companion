"""Sample backend service.

A small redis-py service used as a fixture for the redis-companion plugin.
The acl-generator agent reads this file, infers the access patterns, and emits
a tailored Redis ACL rule (the deployment-agnostic permission DSL) scoped to
the minimum permissions this service needs to perform its operations.
"""
import json
import os
from redis import Redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
r = Redis.from_url(REDIS_URL)

CACHE_PREFIX = "cache:user:"
SESSION_PREFIX = "session:"
NOTIFY_CHANNEL = "notifications"
ACTIVITY_STREAM = "activity:events"


def cache_user(user_id: str, profile: dict) -> None:
    r.set(f"{CACHE_PREFIX}{user_id}", json.dumps(profile))


def get_user(user_id: str) -> dict | None:
    raw = r.get(f"{CACHE_PREFIX}{user_id}")
    return json.loads(raw) if raw else None


def get_users(user_ids: list[str]) -> list[dict | None]:
    raws = r.mget([f"{CACHE_PREFIX}{uid}" for uid in user_ids])
    return [json.loads(v) if v else None for v in raws]


def create_session(token: str, user_id: str) -> None:
    r.setex(f"{SESSION_PREFIX}{token}", 3600, user_id)


def notify(event: dict) -> int:
    # TODO: add a subscribe handler for inbound notifications from other services
    return r.publish(NOTIFY_CHANNEL, json.dumps(event))


def record_activity(user_id: str, action: str) -> str:
    entry_id = r.xadd(ACTIVITY_STREAM, {"user": user_id, "action": action})
    return entry_id.decode()


if __name__ == "__main__":
    # Smoke test: invoke every public function once with sample data so a Redis
    # ACL applied to this service can be validated end-to-end.
    #
    # Usage:
    #   python3 service.py                              # default user
    #   REDIS_URL='redis://sample-service@host' python3 service.py    # locked-down user
    #
    # Exit code 0 if all six operations succeed, 1 if any fails.
    import sys
    import traceback

    def _step(name: str, fn) -> bool:
        print(f"  {name:40s}", end=" ", flush=True)
        try:
            fn()
            print("OK")
            return True
        except Exception as exc:
            print(f"FAIL - {exc.__class__.__name__}: {exc}")
            traceback.print_exc()
            return False

    print(f"Running sample-service against {REDIS_URL}\n")
    results = [
        _step("cache_user('42', ...)",          lambda: cache_user("42", {"id": 42, "name": "alice"})),
        _step("get_user('42')",                 lambda: get_user("42")),
        _step("get_users(['42', '43'])",        lambda: get_users(["42", "43"])),
        _step("create_session('tok1', '42')",   lambda: create_session("tok1", "42")),
        _step("notify({...})",                  lambda: notify({"event": "login", "user": "42"})),
        _step("record_activity('42', 'login')", lambda: record_activity("42", "login")),
    ]
    print()
    passed, total = sum(results), len(results)
    if passed == total:
        print(f"All {total}/{total} operations succeeded.")
        sys.exit(0)
    else:
        print(f"{total - passed}/{total} operations FAILED.")
        sys.exit(1)
