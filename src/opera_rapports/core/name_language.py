from __future__ import annotations

import re
import unicodedata

from opera_rapports.core.models import Gender, Language

TITLE_HINTS: dict[str, tuple[Gender, Language | None]] = {
    "MR": (Gender.MALE, Language.EN),
    "MISTER": (Gender.MALE, Language.EN),
    "M": (Gender.MALE, Language.FR),
    "MONSIEUR": (Gender.MALE, Language.FR),
    "MRS": (Gender.FEMALE, Language.EN),
    "MS": (Gender.FEMALE, Language.EN),
    "MISS": (Gender.FEMALE, Language.EN),
    "MME": (Gender.FEMALE, Language.FR),
    "MADAME": (Gender.FEMALE, Language.FR),
    "MLLE": (Gender.FEMALE, Language.FR),
    "SR": (Gender.MALE, Language.ES),
    "SRA": (Gender.FEMALE, Language.ES),
    "SENOR": (Gender.MALE, Language.ES),
    "SENORA": (Gender.FEMALE, Language.ES),
    "HERR": (Gender.MALE, Language.DE),
    "FRAU": (Gender.FEMALE, Language.DE),
    "SIG": (Gender.MALE, Language.IT),
    "SIGRA": (Gender.FEMALE, Language.IT),
    "SRTA": (Gender.FEMALE, Language.ES),
}

SPANISH_SURNAME_HINTS = {"GARCIA", "RODRIGUEZ", "MARTINEZ", "LOPEZ", "HERNANDEZ", "GONZALEZ", "PEREZ", "SANCHEZ"}
ENGLISH_SURNAME_HINTS = {"SMITH", "JOHNSON", "WILLIAMS", "BROWN", "JONES", "MILLER", "WILSON", "TAYLOR"}
PORTUGUESE_SURNAME_HINTS = {"SILVA", "SANTOS", "FERREIRA", "PEREIRA", "COSTA", "OLIVEIRA"}
ITALIAN_SURNAME_HINTS = {"ROSSI", "RUSSO", "FERRARI", "ESPOSITO", "BIANCHI", "ROMANO"}
GERMAN_SURNAME_HINTS = {"MULLER", "MUELLER", "SCHMIDT", "SCHNEIDER", "FISCHER", "WEBER", "MEYER"}


def normalize_token(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^A-Za-z]", "", ascii_value).upper()


def split_name(full_name: str, explicit_last_name: str = "", explicit_first_name: str = "") -> tuple[str, str]:
    if explicit_last_name or explicit_first_name:
        return explicit_last_name.strip().upper(), explicit_first_name.strip().title()
    value = " ".join(full_name.replace(",", " ").split())
    if not value:
        return "", ""
    parts = value.split()
    if len(parts) == 1:
        return parts[0].upper(), ""
    if full_name.count(",") == 1:
        left, right = full_name.split(",", 1)
        return left.strip().upper(), right.strip().title()
    return parts[-1].upper(), " ".join(parts[:-1]).title()


def infer_gender_language(title: str, last_name: str, nationality: str = "") -> tuple[Gender, Language]:
    title_key = normalize_token(title)
    if title_key in TITLE_HINTS:
        gender, language = TITLE_HINTS[title_key]
        return gender, language or Language.FR

    nationality_key = normalize_token(nationality)
    if nationality_key in {"ES", "ESP", "SPAIN", "SPANISH"}:
        return Gender.NEUTRAL, Language.ES
    if nationality_key in {"GB", "UK", "USA", "US", "EN", "ENGLISH", "AMERICAN"}:
        return Gender.NEUTRAL, Language.EN
    if nationality_key in {"DE", "DEU", "GERMANY", "GERMAN"}:
        return Gender.NEUTRAL, Language.DE
    if nationality_key in {"PT", "PRT", "PORTUGAL", "PORTUGUESE", "BR", "BRAZIL"}:
        return Gender.NEUTRAL, Language.PT
    if nationality_key in {"IT", "ITA", "ITALY", "ITALIAN"}:
        return Gender.NEUTRAL, Language.IT

    surname_key = normalize_token(last_name)
    if surname_key in SPANISH_SURNAME_HINTS:
        return Gender.NEUTRAL, Language.ES
    if surname_key in ENGLISH_SURNAME_HINTS:
        return Gender.NEUTRAL, Language.EN
    if surname_key in PORTUGUESE_SURNAME_HINTS:
        return Gender.NEUTRAL, Language.PT
    if surname_key in ITALIAN_SURNAME_HINTS:
        return Gender.NEUTRAL, Language.IT
    if surname_key in GERMAN_SURNAME_HINTS:
        return Gender.NEUTRAL, Language.DE
    return Gender.NEUTRAL, Language.FR
