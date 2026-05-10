from __future__ import annotations

from datetime import date

from opera_rapports.core.models import Gender, Language

SALUTATIONS: dict[Language, dict[Gender, str]] = {
    Language.FR: {Gender.FEMALE: "Madame", Gender.MALE: "Monsieur", Gender.NEUTRAL: "Madame, Monsieur"},
    Language.EN: {Gender.FEMALE: "Mrs.", Gender.MALE: "Mr.", Gender.NEUTRAL: "Mr./Mrs."},
    Language.ES: {Gender.FEMALE: "Sra.", Gender.MALE: "Sr.", Gender.NEUTRAL: "Sr./Sra."},
    Language.DE: {Gender.FEMALE: "Frau", Gender.MALE: "Herr", Gender.NEUTRAL: "Frau/Herr"},
    Language.PT: {Gender.FEMALE: "Sra.", Gender.MALE: "Sr.", Gender.NEUTRAL: "Sr./Sra."},
    Language.IT: {Gender.FEMALE: "Sig.ra", Gender.MALE: "Sig.", Gender.NEUTRAL: "Sig./Sig.ra"},
}

ROOM_TYPES: dict[str, dict[Language, str]] = {
    "CLA": {Language.FR: "Classique", Language.EN: "Classic", Language.ES: "Clásica", Language.DE: "Klassik", Language.PT: "Clássico", Language.IT: "Classica"},
    "SUP": {Language.FR: "Supérieure", Language.EN: "Superior", Language.ES: "Superior", Language.DE: "Superior", Language.PT: "Superior", Language.IT: "Superior"},
    "DLX": {Language.FR: "Deluxe", Language.EN: "Deluxe", Language.ES: "Deluxe", Language.DE: "Deluxe", Language.PT: "Deluxe", Language.IT: "Deluxe"},
    "SU": {Language.FR: "Suite", Language.EN: "Suite", Language.ES: "Suite", Language.DE: "Suite", Language.PT: "Suite", Language.IT: "Suite"},
    "SOC": {Language.FR: "Supérieure Ocean", Language.EN: "Superior Ocean", Language.ES: "Superior Océano", Language.DE: "Superior Ocean", Language.PT: "Superior Ocean", Language.IT: "Superior Ocean"},
}

WELCOME_TEXT: dict[Language, str] = {
    Language.FR: "Nous avons le plaisir de vous accueillir au {hotel}. Votre chambre {room} vous attend. Séjour du {arrival} au {departure}. Nous sommes à votre disposition pour rendre votre séjour inoubliable.",
    Language.EN: "We are delighted to welcome you to {hotel}. Your room {room} awaits you. Stay: {arrival} to {departure}. We are at your disposal to make your stay unforgettable.",
    Language.ES: "Es un placer darle la bienvenida a {hotel}. Su habitación {room} le espera. Estancia del {arrival} al {departure}. Estamos a su disposición para hacer su estancia inolvidable.",
    Language.DE: "Wir freuen uns, Sie im {hotel} begrüßen zu dürfen. Ihr Zimmer {room} erwartet Sie. Aufenthalt vom {arrival} bis {departure}. Wir stehen Ihnen zur Verfügung, um Ihren Aufenthalt unvergesslich zu machen.",
    Language.PT: "Temos o prazer de lhe dar as boas-vindas ao {hotel}. O seu quarto {room} espera por si. Estadia de {arrival} a {departure}. Estamos à disposição para tornar a sua estadia inesquecível.",
    Language.IT: "Siamo lieti di darle il benvenuto al {hotel}. La sua camera {room} la attende. Soggiorno dal {arrival} al {departure}. Siamo a disposizione per rendere il suo soggiorno indimenticabile.",
}

MANAGER_ROLE: dict[Language, str] = {
    Language.FR: "Directrice de l'hôtel",
    Language.EN: "Hotel Manager",
    Language.ES: "Directora del hotel",
    Language.DE: "Hoteldirektorin",
    Language.PT: "Diretora do hotel",
    Language.IT: "Direttrice dell'hotel",
}


def salutation(language: Language, gender: Gender) -> str:
    return SALUTATIONS.get(language, SALUTATIONS[Language.FR]).get(gender, SALUTATIONS[Language.FR][Gender.NEUTRAL])


def room_type_label(code: str, language: Language) -> str:
    return ROOM_TYPES.get(code.upper(), {}).get(language, code)


MONTHS = {
    Language.FR: ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"],
    Language.EN: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    Language.ES: ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
    Language.DE: ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"],
    Language.PT: ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"],
    Language.IT: ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"],
}
WEEKDAYS = {
    Language.FR: ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"],
    Language.EN: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    Language.ES: ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"],
    Language.DE: ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"],
    Language.PT: ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"],
    Language.IT: ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"],
}


def long_date(value: date | None, language: Language) -> str:
    if value is None:
        return ""
    return f"{WEEKDAYS[language][value.weekday()]} {value:%d} {MONTHS[language][value.month - 1]} {value:%Y}"


def short_date(value: date | None, language: Language) -> str:
    if value is None:
        return ""
    if language == Language.EN:
        return value.strftime("%m/%d/%Y")
    return value.strftime("%d/%m/%Y")
