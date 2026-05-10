from __future__ import annotations

from dataclasses import dataclass
from html import escape
from importlib import resources
from pathlib import Path

from opera_rapports.core.localization import MANAGER_ROLE, WELCOME_TEXT, long_date, room_type_label, salutation, short_date
from opera_rapports.core.models import Guest, Language


@dataclass(frozen=True)
class ReportContext:
    hotel_name: str = "l'Hôtel"
    manager_name: str = "La Direction"
    manager_role_fr: str = "Directrice de l'hôtel"
    logo_path: str = ""


def _css() -> str:
    return resources.files("opera_rapports.resources.templates").joinpath("base_print.css").read_text(encoding="utf-8")


class ReportRenderer:
    def render_key_cards(self, guests: list[Guest], context: ReportContext | None = None) -> str:
        context = context or ReportContext()
        sheets = []
        for guest in guests:
            sheets.append(f"""
<section class="sheet">
  <header class="hotel">{escape(context.hotel_name)}</header>
  <main>
    <div class="guest">{escape(salutation(guest.language, guest.gender))} {escape(guest.last_name)}</div>
    <div class="room">{escape(guest.room_number)}</div>
    <div class="roomtype muted">{escape(room_type_label(guest.room_type, guest.language))}</div>
  </main>
  <footer class="dates">{escape(short_date(guest.arrival_date, guest.language))} → {escape(short_date(guest.departure_date, guest.language))}</footer>
</section>""")
        return f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><title>Cartons de clés</title><style>
{_css()}
@page {{ size: A6 landscape; margin: 0; }}
.sheet {{ width: 148mm; height: 105mm; padding: 13mm 14mm; display: flex; flex-direction: column; justify-content: space-between; border: 1px solid #e8dfd0; }}
.guest {{ font-family: 'MV Boli', 'Segoe Print', cursive; font-size: 22pt; }}
.room {{ font-size: 54pt; font-weight: 700; color: #9b7a36; line-height: 1; }}
.dates {{ font-size: 13pt; }}
.roomtype {{ font-size: 11pt; text-transform: uppercase; letter-spacing: .08em; }}
@media print {{ body {{ margin: 0; }} .sheet {{ border: 0; }} }}
</style></head><body>{''.join(sheets)}</body></html>"""

    def render_welcome_letters(self, guests: list[Guest], context: ReportContext | None = None) -> str:
        context = context or ReportContext()
        sheets = []
        for guest in guests:
            text = WELCOME_TEXT[guest.language].format(
                hotel=context.hotel_name,
                room=guest.room_number,
                arrival=short_date(guest.arrival_date, guest.language),
                departure=short_date(guest.departure_date, guest.language),
            )
            manager_role = context.manager_role_fr if guest.language == Language.FR else MANAGER_ROLE[guest.language]
            sheets.append(f"""
<section class="sheet" lang="{guest.language.value}">
  <div class="date">{escape(long_date(guest.arrival_date, guest.language))}</div>
  <div class="salute">{escape(salutation(guest.language, guest.gender))} {escape(guest.last_name)},</div>
  <p class="message">{escape(text)}</p>
  <div class="signature"><strong>{escape(context.manager_name)}</strong><br><span class="muted">{escape(manager_role)}</span></div>
</section>""")
        return f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><title>Welcome letters</title><style>
{_css()}
@page {{ size: 220mm 110mm landscape; margin: 0; }}
.sheet {{ width: 220mm; height: 110mm; padding: 13mm 18mm; border: 1px solid #e8dfd0; position: relative; }}
.date {{ text-align: right; font-size: 10pt; }}
.salute {{ margin-top: 9mm; font-size: 14pt; font-weight: 600; }}
.message {{ margin-top: 6mm; font-size: 12pt; line-height: 1.45; max-width: 168mm; }}
.signature {{ position: absolute; right: 18mm; bottom: 12mm; text-align: right; line-height: 1.35; }}
@media print {{ body {{ margin: 0; }} .sheet {{ border: 0; }} }}
</style></head><body>{''.join(sheets)}</body></html>"""

    def render_arrivals_list(self, guests: list[Guest], language: Language = Language.FR) -> str:
        rows = []
        for guest in guests:
            rows.append(f"""<tr><td>{escape(guest.room_number)}</td><td>{escape(guest.last_name)}</td><td>{escape(guest.first_name)}</td><td>{escape(salutation(guest.language, guest.gender))}</td><td>{escape(short_date(guest.arrival_date, language))}</td><td>{escape(short_date(guest.departure_date, language))}</td><td class="note"></td></tr>""")
        title_date = f" — {long_date(guests[0].arrival_date, language)}" if guests and guests[0].arrival_date else ""
        return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Liste des arrivées</title><style>{_css()}
@page {{ size: A4 landscape; margin: 12mm; }} body {{ padding: 10mm; }} h1 {{ margin: 0 0 8mm; font-size: 18pt; }} table {{ width: 100%; border-collapse: collapse; font-size: 10pt; }} th, td {{ border: 1px solid #cfd6df; padding: 6px; text-align: left; }} th {{ background: #f2f5f8; }} .note {{ width: 34%; height: 24px; }}</style></head><body><h1>Liste des arrivées{escape(title_date)}</h1><table><thead><tr><th>Chambre</th><th>Nom</th><th>Prénom</th><th>Civilité</th><th>Arrivée</th><th>Départ</th><th>Annotation</th></tr></thead><tbody>{''.join(rows)}</tbody></table></body></html>"""

    def save_html(self, html: str, target: str | Path) -> Path:
        target_path = Path(target)
        target_path.write_text(html, encoding="utf-8")
        return target_path
