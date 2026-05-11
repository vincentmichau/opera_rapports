from __future__ import annotations

from datetime import date

from opera_rapports.core.models import Gender, Guest, Language
from opera_rapports.core.settings import AppSettings
from opera_rapports.core.storage import Repository


def sample_guest() -> Guest:
    return Guest(
        reservation_id="ABC",
        full_name="Jean Durand",
        last_name="DURAND",
        first_name="Jean",
        title_raw="M",
        gender=Gender.MALE,
        language=Language.FR,
        arrival_date=date(2026, 5, 11),
        departure_date=date(2026, 5, 12),
        room_number="204",
        room_type="CLA",
    )


def test_app_settings_roundtrip(tmp_path) -> None:
    repository = Repository(tmp_path / "settings.sqlite3")
    settings = AppSettings(
        hotel_name="Grand Hôtel",
        manager_name="Mme Martin",
        manager_role_fr="Directrice générale",
        default_printer="Reception A6",
        retention_days=14,
    )

    repository.save_app_settings(settings)

    loaded = repository.get_app_settings()
    assert loaded.hotel_name == "Grand Hôtel"
    assert loaded.manager_name == "Mme Martin"
    assert loaded.retention_days == 14


def test_clear_guests_removes_local_import(tmp_path) -> None:
    repository = Repository(tmp_path / "guests.sqlite3")
    repository.replace_import([sample_guest()])

    repository.clear_guests()

    assert repository.list_guests() == []
