from __future__ import annotations

from datetime import date
from pathlib import Path

from opera_rapports.core.exports import export_arrivals_docx, export_arrivals_xlsx
from opera_rapports.core.models import Gender, Guest, Language
from opera_rapports.core.reports import ReportContext, ReportRenderer
from opera_rapports.core.settings import AppSettings
from opera_rapports.core.storage import Repository
from opera_rapports.mvc.models import ArrivalTableViewModel

DEFAULT_VISIBLE_COLUMNS = [
    "room_number",
    "last_name",
    "first_name",
    "gender",
    "language",
    "arrival_date",
    "departure_date",
    "room_type",
    "people_count",
]


class AppController:
    """Application controller coordinating the view, domain model and DAO-backed repository."""

    def __init__(self, repository: Repository | None = None, renderer: ReportRenderer | None = None) -> None:
        self.repository = repository or Repository()
        self.renderer = renderer or ReportRenderer()
        self.app_settings = self.repository.get_app_settings()
        self.repository.purge_imports_older_than(self.app_settings.retention_days)

    def load_arrivals(self, arrival: date | None = None) -> ArrivalTableViewModel:
        return ArrivalTableViewModel(
            guests=self.repository.list_guests(arrival),
            visible_columns=self.visible_columns(),
        )

    def replace_import(self, guests: list[Guest]) -> int:
        return self.repository.replace_import(guests)

    def update_guest_language_gender(self, reservation_id: str, language: Language, gender: Gender) -> None:
        self.repository.update_guest_language_gender(reservation_id, language, gender)

    def clear_arrivals(self) -> None:
        self.repository.clear_guests()

    def save_app_settings(self, settings: AppSettings) -> int:
        self.app_settings = settings
        self.repository.save_app_settings(settings)
        return self.repository.purge_imports_older_than(settings.retention_days)

    def visible_columns(self) -> list[str]:
        visible = self.repository.get_setting("visible_columns", DEFAULT_VISIBLE_COLUMNS)
        return visible if isinstance(visible, list) else DEFAULT_VISIBLE_COLUMNS

    def save_visible_columns(self, columns: list[str]) -> None:
        self.repository.set_setting("visible_columns", columns)

    def theme(self) -> str:
        return str(self.repository.get_setting("theme", "light"))

    def save_theme(self, theme: str) -> None:
        self.repository.set_setting("theme", theme)

    def render_report(self, kind: str, guests: list[Guest]) -> str:
        context = ReportContext(
            hotel_name=self.app_settings.hotel_name,
            manager_name=self.app_settings.manager_name,
            manager_role_fr=self.app_settings.manager_role_fr,
            logo_path=self.app_settings.logo_path,
        )
        if kind == "key":
            return self.renderer.render_key_cards(guests, context)
        if kind == "letter":
            return self.renderer.render_welcome_letters(guests, context)
        return self.renderer.render_arrivals_list(guests)

    def export_arrivals(self, kind: str, guests: list[Guest], target: str | Path) -> Path:
        if kind == "xlsx":
            return export_arrivals_xlsx(guests, target)
        return export_arrivals_docx(guests, target)
