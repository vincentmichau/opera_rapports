from __future__ import annotations

from collections.abc import Iterable
from datetime import date
from pathlib import Path

from platformdirs import user_data_dir

from opera_rapports.core.dao import DAOFactory
from opera_rapports.core.models import Gender, Guest, Language
from opera_rapports.core.settings import AppSettings

APP_NAME = "OperaRapports"


def default_db_path() -> Path:
    root = Path(user_data_dir(APP_NAME, appauthor=False))
    root.mkdir(parents=True, exist_ok=True)
    return root / "opera_rapports.sqlite3"


class Repository:
    """Compatibility facade over DAO objects used by controllers and tests."""

    def __init__(self, path: str | Path | None = None, dao_factory: DAOFactory | None = None) -> None:
        self.path = Path(path) if path else default_db_path()
        self.dao_factory = dao_factory or DAOFactory(self.path)
        self.guests = self.dao_factory.guests
        self.settings = self.dao_factory.settings

    def close(self) -> None:
        self.dao_factory.close()

    def replace_import(self, guests: Iterable[Guest]) -> int:
        return self.guests.replace_all(guests)

    def list_guests(self, arrival: date | None = None) -> list[Guest]:
        return self.guests.list(arrival)

    def update_guest_language_gender(self, reservation_id: str, language: Language, gender: Gender) -> None:
        self.guests.update_language_gender(reservation_id, language, gender)

    def clear_guests(self) -> None:
        self.guests.clear()

    def purge_imports_older_than(self, days: int) -> int:
        return self.guests.purge_older_than(days)

    def get_app_settings(self) -> AppSettings:
        return AppSettings.from_mapping(self.get_setting("app_settings", {}))

    def save_app_settings(self, settings: AppSettings) -> None:
        self.set_setting("app_settings", settings.to_mapping())

    def get_setting(self, key: str, default: object = None) -> object:
        return self.settings.get(key, default)

    def set_setting(self, key: str, value: object) -> None:
        self.settings.set(key, value)
