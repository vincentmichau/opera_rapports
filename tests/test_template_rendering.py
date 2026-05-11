from __future__ import annotations

import pytest

from opera_rapports.core.document_templates import DocumentTemplate, TemplateKind
from opera_rapports.core.template_rendering import AVAILABLE_FIELDS, render_template_preview, validate_template
from opera_rapports.core.reports import ReportContext
from opera_rapports.core.storage import Repository
from opera_rapports.mvc.controllers import AppController


def custom_template(content: str) -> DocumentTemplate:
    return DocumentTemplate(
        id="custom",
        name="Test",
        kind=TemplateKind.WELCOME_LETTER,
        description="",
        content=content,
        css=".sheet { font-family: Aptos; }",
    )


def test_template_validation_lists_unknown_fields() -> None:
    validation = validate_template(custom_template("Bonjour {nom} {champ_inconnu}"))

    assert not validation.is_valid
    assert validation.unknown_fields == ["champ_inconnu"]


def test_template_preview_renders_known_fields_safely() -> None:
    html = render_template_preview(
        custom_template("Bonjour {civilite} {nom}, chambre {chambre}"),
        ReportContext("Grand Hôtel", "Mme Martin", "Directrice"),
    )

    assert "Bonjour Monsieur DURAND, chambre 204" in html
    assert "Grand Hôtel" not in html  # not used by this template


def test_controller_rejects_invalid_template_before_persistence(tmp_path) -> None:
    controller = AppController(repository=Repository(tmp_path / "invalid_template.sqlite3"))

    with pytest.raises(ValueError, match="champ_inconnu"):
        controller.save_document_template(custom_template("{champ_inconnu}"))


def test_available_fields_expose_hotel_and_guest_placeholders() -> None:
    assert "nom" in AVAILABLE_FIELDS
    assert "hotel" in AVAILABLE_FIELDS
    assert "directeur" in AVAILABLE_FIELDS
