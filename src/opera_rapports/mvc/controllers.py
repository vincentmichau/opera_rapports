from __future__ import annotations

from datetime import date
from pathlib import Path

from opera_rapports.core.document_templates import DocumentTemplate, TemplateCatalog
from opera_rapports.core.exports import export_arrivals_docx, export_arrivals_xlsx
from opera_rapports.core.models import Gender, Guest, Language
from opera_rapports.core.reports import ReportContext, ReportRenderer
from opera_rapports.core.settings import AppSettings
from opera_rapports.core.template_rendering import TemplateValidation, render_template_preview, validate_template
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
        self.template_catalog = self.load_template_catalog()
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
        self.repository.record_audit("manual_guest_correction", "language/gender adjusted")

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

    def report_context(self) -> ReportContext:
        return ReportContext(
            hotel_name=self.app_settings.hotel_name,
            manager_name=self.app_settings.manager_name,
            manager_role_fr=self.app_settings.manager_role_fr,
            logo_path=self.app_settings.logo_path,
        )

    def render_report(self, kind: str, guests: list[Guest]) -> str:
        context = self.report_context()
        if kind == "key":
            return self.renderer.render_key_cards(guests, context)
        if kind == "letter":
            return self.renderer.render_welcome_letters(guests, context)
        if kind == "arrivals_portrait":
            return self.renderer.render_arrivals_list(guests, orientation="portrait")
        return self.renderer.render_arrivals_list(guests, orientation="landscape")

    def export_arrivals(self, kind: str, guests: list[Guest], target: str | Path) -> Path:
        if kind == "xlsx":
            exported = export_arrivals_xlsx(guests, target)
        else:
            exported = export_arrivals_docx(guests, target)
        self.repository.record_audit("export_arrivals", f"{kind}:{len(guests)} rows")
        return exported

    def record_print_preparation(self, kind: str, count: int) -> None:
        self.repository.record_audit("print_prepared", f"{kind}:{count} rows")

    def load_template_catalog(self) -> TemplateCatalog:
        return TemplateCatalog.from_settings(self.repository.get_setting("document_templates", None))

    def list_document_templates(self) -> list[DocumentTemplate]:
        self.template_catalog = self.load_template_catalog()
        return self.template_catalog.list()

    def validate_document_template(self, template: DocumentTemplate) -> TemplateValidation:
        return validate_template(template)

    def preview_document_template(self, template: DocumentTemplate) -> str:
        return render_template_preview(template, self.report_context())

    def save_document_template(self, template: DocumentTemplate) -> None:
        validation = self.validate_document_template(template)
        if not validation.is_valid:
            raise ValueError(validation.message)
        self.template_catalog.upsert(template)
        self.repository.set_setting("document_templates", self.template_catalog.to_settings())
        self.repository.record_audit("template_saved", template.kind.value)

    def delete_document_template(self, template_id: str) -> bool:
        deleted = self.template_catalog.delete(template_id)
        if deleted:
            self.repository.set_setting("document_templates", self.template_catalog.to_settings())
            self.repository.record_audit("template_deleted", template_id)
        return deleted

    def duplicate_document_template(self, template_id: str) -> DocumentTemplate | None:
        template = self.template_catalog.get(template_id)
        if template is None:
            return None
        duplicate = template.duplicate()
        self.save_document_template(duplicate)
        return duplicate

    def create_document_template(self) -> DocumentTemplate:
        template = self.template_catalog.create_blank()
        self.save_document_template(template)
        return template
