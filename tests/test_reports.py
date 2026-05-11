from __future__ import annotations

from datetime import date

from opera_rapports.core.models import Gender, Guest, Language
from opera_rapports.core.reports import ReportContext, ReportRenderer


def sample_guest() -> Guest:
    return Guest(
        reservation_id="1",
        full_name="Jean Durand",
        last_name="DURAND",
        first_name="Jean",
        title_raw="M",
        gender=Gender.MALE,
        language=Language.FR,
        arrival_date=date(2026, 5, 11),
        departure_date=date(2026, 5, 13),
        room_number="204",
        room_type="CLA",
    )


def test_key_card_contains_print_size_and_guest() -> None:
    html = ReportRenderer().render_key_cards([sample_guest()], ReportContext("Grand Hôtel", "Mme Martin"))

    assert "@page { size: A6 landscape" in html
    assert "DURAND" in html
    assert "204" in html


def test_welcome_letter_contains_dl_print_size() -> None:
    html = ReportRenderer().render_welcome_letters([sample_guest()])

    assert "@page { size: 220mm 110mm landscape" in html
    assert "Votre chambre 204 vous attend" in html


def test_welcome_letter_uses_custom_french_manager_role() -> None:
    html = ReportRenderer().render_welcome_letters(
        [sample_guest()],
        ReportContext("Grand Hôtel", "Mme Martin", "Directrice générale"),
    )

    assert "Directrice générale" in html


def test_key_card_uses_mv_boli_for_whole_card() -> None:
    html = ReportRenderer().render_key_cards([sample_guest()])

    assert "font-family: 'MV Boli'" in html
    assert ".sheet { width: 148mm" in html


def test_welcome_letter_uses_aptos_11pt() -> None:
    html = ReportRenderer().render_welcome_letters([sample_guest()])

    assert "font-family: Aptos" in html
    assert "font-size: 11pt" in html
    assert ".message { margin-top: 6mm; font-size: 11pt" in html
