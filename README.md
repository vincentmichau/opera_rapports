# Opera Rapports

Application desktop Windows 11 en Python pour la réception et le night audit d'un hôtel. Elle importe un fichier XML Opera Cloud, stocke les arrivées dans SQLite, permet de corriger civilité/langue, puis génère des cartons de clés A6 paysage, des welcome letters DL paysage et une liste d'arrivées imprimable.

## Objectifs fonctionnels

- Interface moderne PySide6 avec ruban, filtres de date, choix de modèle, actions d'impression, menu thème clair/sombre et barre d'état.
- Import XML Opera Cloud non bloquant avec barre de progression.
- Normalisation RGPD-friendly : stockage local SQLite, données limitées à l'import opérationnel, remplacement complet à chaque import.
- Parsing des noms : nom en majuscules, prénom en casse titre, civilité et langue déduites puis rectifiables.
- Tableau triable/filtrable par date d'arrivée, avec listes déroulantes civilité et langue.
- KPI rapides : nombre d'arrivées, nombre de personnes, répartition par type de chambre.
- Modèles HTML/CSS imprimables : `@page { size: A6 landscape }` pour les cartons et `@page { size: 220mm 110mm landscape }` pour les welcome letters.
- Base technique prête pour l'export PDF/DOCX/Excel, le concepteur de rapports graphique et les modèles personnalisables.

## Installation développeur

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows
pip install -e .[dev]
opera-rapports
```

## Packaging Windows

Le dépôt contient un workflow GitHub Actions qui produit trois familles d'artefacts :

1. **Installable EXE** avec Inno Setup (`packaging/inno/setup.iss`) : installe l'application, crée les raccourcis et embarque les dépendances Python dans le bundle PyInstaller.
2. **PortableApps** (`packaging/portableapps/AppInfo/appinfo.ini`) : archive portable autonome basée sur la sortie PyInstaller `onedir`.
3. **MSI** avec WiX Toolset (`packaging/wix/Product.wxs`) : installe les fichiers du bundle et expose une base MSI standard.

Le runtime Python et les bibliothèques sont inclus dans les bundles PyInstaller afin que les utilisateurs néophytes n'aient rien à installer séparément.

## Feuille de route suggérée

- Ajouter un écran de paramétrage hôtel : nom, logo, directrice, imprimantes favorites, formats papier.
- Ajouter un concepteur graphique de rapports : grille aimantée, règle, zones texte/images/champs, expressions conditionnelles.
- Ajouter l'export natif PDF via Chromium/Qt WebEngine ou WeasyPrint, DOCX via `python-docx` et Excel via `openpyxl`.
- Ajouter une politique de purge automatique des imports anciens, un journal d'audit local et un mode anonymisation.
- Ajouter des tests d'import sur des échantillons XML Opera Cloud réels anonymisés.
