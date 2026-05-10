# Guide d'utilisation — Opera Rapports

## 1. Importer les arrivées

1. Cliquez sur **Importer XML**.
2. Choisissez le fichier XML exporté depuis Opera Cloud.
3. Attendez la fin de la barre de progression : l'import se fait en arrière-plan pour garder l'interface réactive.
4. Les arrivées sont stockées localement dans SQLite et remplacées à chaque nouvel import.

## 2. Filtrer et contrôler

- Utilisez **Aujourd'hui**, **Demain** ou le sélecteur de date pour afficher les arrivées voulues.
- Utilisez le bouton **Colonnes** pour choisir les colonnes visibles. Le choix est mémorisé localement.
- Corrigez la **civilité** ou la **langue** avec les listes déroulantes si la détection automatique n'est pas parfaite.

## 3. Imprimer et exporter

- **Imprimer la sélection** : imprime le modèle sélectionné pour la ligne choisie.
- **Tous les cartons** : prépare tous les cartons de clés A6 paysage de la date affichée.
- **Toutes les lettres** : prépare toutes les welcome letters DL paysage de la date affichée.
- Menu **Application → Exporter Excel (.xlsx)** : exporte la liste des arrivées.
- Menu **Application → Exporter Word (.docx)** : exporte une liste Word annotable.

## 4. RGPD et purge

- L'application conserve uniquement les données opérationnelles nécessaires à l'impression.
- Les données restent sur le poste utilisateur dans une base SQLite locale.
- Menu **Application → Purger les données importées** supprime toutes les arrivées stockées localement.
