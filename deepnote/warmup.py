"""Tiny wake script — schedule this notebook/block so the machine is warm before you study."""

from datetime import datetime, timezone

print("Study Forge warmup", datetime.now(timezone.utc).isoformat())
print("Machine is awake. Start engine_api on 8080 if Incoming connections are enabled.")
