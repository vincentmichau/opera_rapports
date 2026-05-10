from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime
from pathlib import Path
from xml.etree import ElementTree as ET

from opera_rapports.core.models import Guest
from opera_rapports.core.name_language import infer_gender_language, split_name

ProgressCallback = Callable[[int, int], None]

FIELD_ALIASES = {
    "reservation_id": ["reservation_id", "confirmation_no", "confirmationNumber", "resv_name_id", "RESV_NAME_ID"],
    "full_name": ["guest_name", "name", "full_name", "guestName", "GUEST_NAME"],
    "last_name": ["last_name", "surname", "family_name", "lastName", "LAST_NAME"],
    "first_name": ["first_name", "given_name", "firstName", "FIRST_NAME"],
    "title": ["title", "salutation", "name_title", "TITLE"],
    "arrival_date": ["arrival", "arrival_date", "arrivalDate", "ARRIVAL"],
    "departure_date": ["departure", "departure_date", "departureDate", "DEPARTURE"],
    "room_number": ["room", "room_no", "room_number", "roomNumber", "ROOM"],
    "room_type": ["room_type", "roomType", "ROOM_TYPE", "rtc", "RTC"],
    "adults": ["adults", "adult", "ADULTS"],
    "children": ["children", "child", "CHILDREN"],
    "nationality": ["nationality", "country", "language", "NATIONALITY"],
}

RECORD_TAG_HINTS = {"reservation", "resv", "guest", "row", "record"}


def parse_date(value: str) -> date | None:
    value = value.strip()
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y%m%d", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(value[:19], fmt).date()
        except ValueError:
            continue
    return None


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _flatten(element: ET.Element) -> dict[str, str]:
    values: dict[str, str] = {}
    for child in element.iter():
        key = _local_name(child.tag)
        text = (child.text or "").strip()
        if text and key not in values:
            values[key] = text
    values.update({key: value for key, value in element.attrib.items() if value})
    return values


def _pick(values: dict[str, str], field: str) -> str:
    lowered = {key.lower(): value for key, value in values.items()}
    for alias in FIELD_ALIASES[field]:
        if alias in values:
            return values[alias]
        if alias.lower() in lowered:
            return lowered[alias.lower()]
    return ""


def _candidate_records(root: ET.Element) -> list[ET.Element]:
    candidates = [el for el in root.iter() if _local_name(el.tag).lower() in RECORD_TAG_HINTS]
    if candidates:
        return candidates
    leaf_parents = [el for el in root.iter() if len(list(el)) >= 3]
    return leaf_parents or [root]


def import_opera_xml(path: str | Path, progress: ProgressCallback | None = None) -> list[Guest]:
    tree = ET.parse(path)
    records = _candidate_records(tree.getroot())
    guests: list[Guest] = []
    total = len(records)
    for index, record in enumerate(records, start=1):
        raw = _flatten(record)
        full_name = _pick(raw, "full_name")
        last_name, first_name = split_name(full_name, _pick(raw, "last_name"), _pick(raw, "first_name"))
        title = _pick(raw, "title")
        gender, language = infer_gender_language(title, last_name, _pick(raw, "nationality"))
        guest = Guest(
            reservation_id=_pick(raw, "reservation_id") or f"xml-{index}",
            full_name=full_name or " ".join([first_name, last_name]).strip(),
            last_name=last_name,
            first_name=first_name,
            title_raw=title,
            gender=gender,
            language=language,
            arrival_date=parse_date(_pick(raw, "arrival_date")),
            departure_date=parse_date(_pick(raw, "departure_date")),
            room_number=_pick(raw, "room_number"),
            room_type=_pick(raw, "room_type"),
            adults=int(_pick(raw, "adults") or 1),
            children=int(_pick(raw, "children") or 0),
            raw=raw,
        )
        if guest.last_name or guest.room_number or guest.arrival_date:
            guests.append(guest)
        if progress:
            progress(index, total)
    return guests
