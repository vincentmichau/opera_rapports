from __future__ import annotations

from datetime import date

from opera_rapports.core.dao import DAOFactory
from opera_rapports.core.models import Gender, Guest, Language
from opera_rapports.core.storage import Repository
from opera_rapports.mvc.controllers import AppController


def sample_guest() -> Guest:
    return Guest(
        reservation_id="DAO1",
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
        adults=2,
    )


def test_dao_factory_creates_guest_and_settings_daos(tmp_path) -> None:
    factory = DAOFactory(tmp_path / "dao.sqlite3")

    factory.guests.replace_all([sample_guest()])
    factory.settings.set("theme", "dark")

    assert factory.guests.list()[0].reservation_id == "DAO1"
    assert factory.settings.get("theme") == "dark"


def test_controller_loads_view_model_and_renders_report(tmp_path) -> None:
    repository = Repository(tmp_path / "controller.sqlite3")
    controller = AppController(repository=repository)
    controller.replace_import([sample_guest()])

    view_model = controller.load_arrivals(date(2026, 5, 11))
    html = controller.render_report("key", view_model.guests)

    assert view_model.row_count == 1
    assert view_model.people_count == 2
    assert view_model.room_type_counts == {"CLA": 1}
    assert "MV Boli" in html
