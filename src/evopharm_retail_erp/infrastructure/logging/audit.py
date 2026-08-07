"""File-backed audit sink for local deployments.

This adapter is intentionally outside the Medicine domain: filesystem I/O,
JSON serialisation, and logging are infrastructure concerns. Application
services may depend on an audit port later without importing this module.
"""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

_logger = logging.getLogger(__name__)
_audit_lock = Lock()


@dataclass(frozen=True, slots=True)
class AuditEntry:
    """A serialisable record written to the append-only audit stream."""

    user_id: str
    action: str
    details: str
    status: str = "SUCCESS"
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class FileAuditLogger:
    """Append audit records to a JSON-lines file with process-local locking."""

    def __init__(self, log_file_path: str | Path = "logs/audit_trail.jsonl") -> None:
        self._log_file = Path(log_file_path)

    def log_event(
        self,
        *,
        user_id: str,
        action: str,
        details: str,
        status: str = "SUCCESS",
    ) -> None:
        entry = AuditEntry(
            user_id=user_id,
            action=action,
            details=details,
            status=status,
        )
        try:
            with _audit_lock:
                self._log_file.parent.mkdir(parents=True, exist_ok=True)
                with self._log_file.open("a", encoding="utf-8") as audit_file:
                    json.dump(asdict(entry), audit_file, separators=(",", ":"))
                    audit_file.write("\n")
        except OSError:
            _logger.exception("Failed to write audit log to %s", self._log_file)
            raise
