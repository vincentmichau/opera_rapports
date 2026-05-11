from __future__ import annotations

from pathlib import Path

from opera_rapports.core.document_templates import TemplateKind
from opera_rapports.core.storage import Repository
from opera_rapports.core.xml_importer import import_opera_xml
from opera_rapports.mvc.controllers import AppController


def test_importer_tolerates_invalid_people_counts(tmp_path: Path) -> None:
    xml = tmp_path / "bad_counts.xml"
    xml.write_text(
        """
        <arrivals><reservation>
          <confirmation_no>BAD1</confirmation_no><guest_name>Test, Alice</guest_name>
          <arrival>2026-05-11</arrival><departure>2026-05-12</departure>
          <room>101</room><adults>N/A</adults><children></children>
        </reservation></arrivals>
        """,
        encoding="utf-8",
    )

    guests = import_opera_xml(xml)

    assert guests[0].adults == 1
    assert guests[0].children == 0


def test_repository_records_non_personal_audit_events(tmp_path: Path) -> None:
    repository = Repository(tmp_path / "audit.sqlite3")

    repository.record_audit("unit_test", "2 rows")

    event = repository.recent_audit_events(1)[0]
    assert event.action == "unit_test"
    assert event.details == "2 rows"
    assert "T" in event.created_at


def test_controller_audits_template_save_and_export(tmp_path: Path) -> None:
    repository = Repository(tmp_path / "controller_audit.sqlite3")
    controller = AppController(repository=repository)
    template = controller.create_document_template()
    template.kind = TemplateKind.KEY_CARD
    controller.save_document_template(template)
    controller.record_print_preparation("key", 0)

    actions = [event.action for event in repository.recent_audit_events(10)]
    assert "template_saved" in actions
    assert "print_prepared" in actions
