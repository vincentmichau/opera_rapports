from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class AppSettings:
    hotel_name: str = "Votre Hôtel"
    manager_name: str = "La Directrice"
    manager_role_fr: str = "Directrice de l'hôtel"
    default_printer: str = ""
    retention_days: int = 7
    default_arrival_filter: str = "tomorrow"
    logo_path: str = ""

    @classmethod
    def from_mapping(cls, value: object) -> "AppSettings":
        if not isinstance(value, dict):
            return cls()
        allowed = {field: value[field] for field in cls.__dataclass_fields__ if field in value}
        settings = cls(**allowed)
        settings.retention_days = max(int(settings.retention_days), 1)
        settings.logo_path = str(Path(settings.logo_path)) if settings.logo_path else ""
        return settings

    def to_mapping(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["retention_days"] = max(int(self.retention_days), 1)
        return payload
