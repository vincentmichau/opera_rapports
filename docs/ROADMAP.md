# Roadmap proposée

## Priorité 1 — Production réception

- Importer des échantillons XML Opera Cloud réels anonymisés et enrichir les alias de champs.
- Ajouter la prévisualisation intégrée dans l'application avec Qt WebEngine ou un composant HTML interne.
- Finaliser le dialogue d'impression : imprimante favorite, bac papier, orientation et format par modèle.
- Ajouter la configuration hôtel : nom, logo, directrice, signatures et textes multilingues.

## Priorité 2 — Modèles personnalisables

- Éditeur graphique de modèles avec grille aimantée, règles, zones texte/image/champ et aperçu instantané.
- Bibliothèque de champs disponibles : client, réservation, chambre, séjour, type chambre, formules.
- Versionnement des modèles et bouton restaurer les modèles par défaut.

## Priorité 3 — Exports et conformité

- Export PDF natif validé pour les formats A6, DL et A4.
- Journal local des imports/exports sans données sensibles inutiles.
- Politique de purge automatique configurable.
- Tests de packaging Windows sur runner GitHub Actions et machine Windows 11 réelle.


## Architecture MVC / DAO

- Continuer à déplacer la logique métier vers `AppController` plutôt que dans la fenêtre Qt.
- Ajouter progressivement des interfaces DAO pour faciliter les tests et une éventuelle migration SQLite → autre stockage.
- Remplacer à terme le `QTableWidget` par un `QAbstractTableModel` Qt complet, branché sur `ArrivalTableViewModel`.
