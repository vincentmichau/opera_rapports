from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True, slots=True)
class AuditEvent:
    """Minimal local audit event without guest personal data.

    The audit log intentionally stores counts and action names only. It helps the hotel
    understand operational usage while avoiding unnecessary personal data retention.
    """

    action: str
    details: str = ""
    created_at: str = ""

    @classmethod
    def create(cls, action: str, details: str = "") -> "AuditEvent":
        timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        return cls(action=action, details=details, created_at=timestamp)
