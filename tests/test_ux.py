from __future__ import annotations

from opera_rapports.core.ux import EMPTY_STATE_TEXT, HELP_HTML, QUICK_START_STEPS, quick_start_text


def test_quick_start_is_three_simple_steps() -> None:
    text = quick_start_text()

    assert len(QUICK_START_STEPS) == 3
    assert "1. Importer" in text
    assert "2. Vérifier" in text
    assert "3. Imprimer" in text


def test_help_text_guides_neophyte_user() -> None:
    assert "Importer XML" in HELP_HTML
    assert "Aperçu" in HELP_HTML
    assert "désactivés" in HELP_HTML
    assert "Aucune arrivée" in EMPTY_STATE_TEXT
