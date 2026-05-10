from __future__ import annotations

from dataclasses import dataclass, field

from opera_rapports.core.models import Guest


@dataclass(slots=True)
class ArrivalTableViewModel:
    """View model exposed by the controller to keep the Qt view simple."""

    guests: list[Guest] = field(default_factory=list)
    visible_columns: list[str] = field(default_factory=list)

    @property
    def row_count(self) -> int:
        return len(self.guests)

    @property
    def people_count(self) -> int:
        return sum(guest.people_count for guest in self.guests)

    @property
    def room_type_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for guest in self.guests:
            key = guest.room_type or "—"
            counts[key] = counts.get(key, 0) + 1
        return counts
