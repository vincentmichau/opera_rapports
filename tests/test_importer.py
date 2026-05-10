from __future__ import annotations

from pathlib import Path

from opera_rapports.core.models import Gender, Language
from opera_rapports.core.xml_importer import import_opera_xml


def test_import_opera_xml_normalizes_guest(tmp_path: Path) -> None:
    xml = tmp_path / "arrivals.xml"
    xml.write_text(
        """
        <arrivals>
          <reservation>
            <confirmation_no>ABC123</confirmation_no>
            <guest_name>durand, jean</guest_name>
            <title>M</title>
            <arrival>2026-05-11</arrival>
            <departure>2026-05-13</departure>
            <room>204</room>
            <room_type>CLA</room_type>
            <adults>2</adults>
          </reservation>
          <reservation>
            <confirmation_no>XYZ999</confirmation_no>
            <firstName>Maria</firstName>
            <lastName>Garcia</lastName>
            <title>Sra.</title>
            <arrival>11/05/2026</arrival>
            <departure>12/05/2026</departure>
            <room>305</room>
            <room_type>SOC</room_type>
          </reservation>
        </arrivals>
        """,
        encoding="utf-8",
    )

    guests = import_opera_xml(xml)

    assert len(guests) == 2
    assert guests[0].last_name == "DURAND"
    assert guests[0].first_name == "Jean"
    assert guests[0].gender == Gender.MALE
    assert guests[0].language == Language.FR
    assert guests[0].room_number == "204"
    assert guests[1].last_name == "GARCIA"
    assert guests[1].language == Language.ES
