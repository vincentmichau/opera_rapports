from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from typing import Any


class Language(StrEnum):
    FR = "fr"
    EN = "en"
    ES = "es"
    DE = "de"
    PT = "pt"
    IT = "it"


class Gender(StrEnum):
    FEMALE = "female"
    MALE = "male"
    NEUTRAL = "neutral"


@dataclass(slots=True)
class Guest:
    reservation_id: str
    full_name: str
    last_name: str
    first_name: str
    title_raw: str
    gender: Gender
    language: Language
    arrival_date: date | None
    departure_date: date | None
    room_number: str
    room_type: str
    adults: int = 1
    children: int = 0
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def display_name(self) -> str:
        return " ".join(part for part in [self.first_name, self.last_name] if part).strip()

    @property
    def nights(self) -> int:
        if not self.arrival_date or not self.departure_date:
            return 0
        return max((self.departure_date - self.arrival_date).days, 0)

    @property
    def people_count(self) -> int:
        return max(self.adults, 0) + max(self.children, 0)
