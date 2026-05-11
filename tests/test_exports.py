from __future__ import annotations

import zipfile
from datetime import date

from opera_rapports.core.exports import export_arrivals_docx, export_arrivals_xlsx
from opera_rapports.core.models import Gender, Guest, Language


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


def test_export_arrivals_xlsx_creates_workbook(tmp_path) -> None:
    target = export_arrivals_xlsx([sample_guest()], tmp_path / "arrivals.xlsx")

    with zipfile.ZipFile(target) as archive:
        assert "xl/workbook.xml" in archive.namelist()
        sheet = archive.read("xl/worksheets/sheet1.xml").decode()
    assert "DURAND" in sheet
    assert "204" in sheet


def test_export_arrivals_docx_creates_document(tmp_path) -> None:
    target = export_arrivals_docx([sample_guest()], tmp_path / "arrivals.docx")

    with zipfile.ZipFile(target) as archive:
        assert "word/document.xml" in archive.namelist()
        document = archive.read("word/document.xml").decode()
    assert "Liste des arrivées" in document
    assert "DURAND" in document
