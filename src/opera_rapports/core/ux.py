from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HelpStep:
    title: str
    description: str


QUICK_START_STEPS = [
    HelpStep("1. Importer", "Cliquez sur Importer XML et choisissez le rapport d'arrivées Opera Cloud."),
    HelpStep("2. Vérifier", "Contrôlez la date, la civilité et la langue directement dans le tableau."),
    HelpStep("3. Imprimer", "Sélectionnez une ligne ou lancez les impressions en lot avec les boutons du ruban."),
]

EMPTY_STATE_TEXT = (
    "Aucune arrivée affichée pour cette date. Importez un XML Opera Cloud ou choisissez une autre date."
)

HELP_HTML = """
<h2>Mode d'emploi rapide</h2>
<ol>
  <li><b>Importer XML</b> : charge le fichier Opera Cloud et remplit le tableau.</li>
  <li><b>Date d'arrivée</b> : filtre les clients à préparer pour aujourd'hui, demain ou une date précise.</li>
  <li><b>Civilité / Langue</b> : corrigez si besoin avec les listes déroulantes.</li>
  <li><b>Aperçu</b> : contrôlez le document avant impression.</li>
  <li><b>Imprimer</b> : imprime la sélection, tous les cartons ou toutes les lettres.</li>
</ol>
<p>Conseil : les boutons d'impression restent désactivés tant qu'aucune arrivée n'est affichée.</p>
""".strip()


def quick_start_text() -> str:
    return "  •  ".join(f"{step.title} : {step.description}" for step in QUICK_START_STEPS)
