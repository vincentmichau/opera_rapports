from __future__ import annotations

from opera_rapports.core.document_templates import DEFAULT_TEMPLATES, TemplateCatalog, TemplateKind
from opera_rapports.core.storage import Repository
from opera_rapports.mvc.controllers import AppController


def test_default_template_catalog_contains_required_document_models() -> None:
    kinds = {template.kind for template in DEFAULT_TEMPLATES}
    names = {template.name for template in DEFAULT_TEMPLATES}

    assert TemplateKind.KEY_CARD in kinds
    assert TemplateKind.WELCOME_LETTER in kinds
    assert TemplateKind.ARRIVALS_PORTRAIT in kinds
    assert TemplateKind.ARRIVALS_LANDSCAPE in kinds
    assert "Carton de clé A6 paysage" in names
    assert "Welcome letter DL paysage" in names


def test_template_catalog_crud_blocks_builtin_deletion() -> None:
    catalog = TemplateCatalog()
    builtin = catalog.get("builtin_key_card_a6")
    assert builtin is not None
    custom = builtin.duplicate()

    catalog.upsert(custom)

    assert catalog.get(custom.id) is not None
    assert catalog.delete("builtin_key_card_a6") is False
    assert catalog.delete(custom.id) is True


def test_controller_persists_custom_document_template(tmp_path) -> None:
    repository = Repository(tmp_path / "templates.sqlite3")
    controller = AppController(repository=repository)
    template = controller.create_document_template()
    template.name = "Lettre VIP personnalisée"
    template.kind = TemplateKind.WELCOME_LETTER

    controller.save_document_template(template)
    reloaded = AppController(repository=repository).list_document_templates()

    assert any(item.name == "Lettre VIP personnalisée" for item in reloaded)


def test_arrivals_lists_can_render_portrait_and_landscape(tmp_path) -> None:
    controller = AppController(repository=Repository(tmp_path / "render.sqlite3"))

    portrait = controller.render_report("arrivals_portrait", [])
    landscape = controller.render_report("arrivals_landscape", [])

    assert "@page { size: A4 portrait" in portrait
    assert "@page { size: A4 landscape" in landscape
