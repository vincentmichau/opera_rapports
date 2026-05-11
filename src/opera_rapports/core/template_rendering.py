from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from html import escape

from opera_rapports.core.document_templates import DocumentTemplate
from opera_rapports.core.localization import long_date, salutation, short_date
from opera_rapports.core.models import Gender, Guest, Language
from opera_rapports.core.reports import ReportContext

FIELD_PATTERN = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")
AVAILABLE_FIELDS = {
    "civilite": "Civilité localisée du client",
    "nom": "Nom du client en majuscules",
    "prenom": "Prénom du client",
    "chambre": "Numéro de chambre",
    "arrivee": "Date d'arrivée courte",
    "depart": "Date de départ courte",
    "date": "Date d'arrivée courte",
    "date_longue": "Date d'arrivée longue dans la langue client",
    "hotel": "Nom de l'hôtel",
    "directeur": "Nom de la directrice ou du directeur",
    "fonction": "Fonction imprimée dans la signature",
    "type_chambre": "Code/type de chambre",
}


@dataclass(frozen=True, slots=True)
class TemplateValidation:
    unknown_fields: list[str]

    @property
    def is_valid(self) -> bool:
        return not self.unknown_fields

    @property
    def message(self) -> str:
        if self.is_valid:
            return "Tous les champs du modèle sont reconnus."
        return "Champs inconnus : " + ", ".join(self.unknown_fields)


def validate_template(template: DocumentTemplate) -> TemplateValidation:
    fields = set(FIELD_PATTERN.findall(template.content)) | set(FIELD_PATTERN.findall(template.css))
    unknown = sorted(field for field in fields if field not in AVAILABLE_FIELDS)
    return TemplateValidation(unknown_fields=unknown)


def sample_guest() -> Guest:
    return Guest(
        reservation_id="preview",
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
        adults=2,
    )


def render_template_preview(
    template: DocumentTemplate,
    context: ReportContext,
    guest: Guest | None = None,
) -> str:
    """Render a safe HTML preview for the simple model designer.

    Unknown placeholders are intentionally left visible as ``{field}`` so a non-technical
    user can see and correct the mistake instead of getting a blocking exception.
    """
    guest = guest or sample_guest()
    mapping = template_context(guest, context)
    body = substitute_fields(template.content, mapping)
    css = substitute_fields(template.css, mapping)
    return f"""<!doctype html>
<html lang="fr">
<head><meta charset="utf-8"><title>{escape(template.name)}</title><style>{css}</style></head>
<body><section class="sheet"><pre>{escape(body)}</pre></section></body>
</html>"""


def template_context(guest: Guest, context: ReportContext) -> dict[str, str]:
    return {
        "civilite": salutation(guest.language, guest.gender),
        "nom": guest.last_name,
        "prenom": guest.first_name,
        "chambre": guest.room_number,
        "arrivee": short_date(guest.arrival_date, guest.language),
        "depart": short_date(guest.departure_date, guest.language),
        "date": short_date(guest.arrival_date, guest.language),
        "date_longue": long_date(guest.arrival_date, guest.language),
        "hotel": context.hotel_name,
        "directeur": context.manager_name,
        "fonction": context.manager_role_fr,
        "type_chambre": guest.room_type,
    }


def substitute_fields(value: str, mapping: dict[str, str]) -> str:
    return FIELD_PATTERN.sub(lambda match: mapping.get(match.group(1), match.group(0)), value)
