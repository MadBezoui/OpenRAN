# État du Projet : Gestion des Conflits xApp O-RAN (VeriXApp)

Ce fichier offre une vue détaillée du contexte, de l'objectif, de l'architecture logicielle et du contenu exact du projet.

## 1. Contexte et Objectif du Projet
Ce projet implémente et évalue **VeriXApp**, un framework hybride conçu pour la gestion et la résolution des conflits entre les applications étendues (xApps) au sein du contrôleur intelligent (RIC) en quasi-temps réel (near-real-time) dans une architecture **O-RAN (Open Radio Access Network)**.

L'objectif principal est de diagnostiquer et réparer les *"stalls fractionnaires"* (blocages continus) qui surviennent lorsque plusieurs xApps formulent des requêtes de contrôle concurrentes sur le réseau (ex. contrôle de puissance, équilibrage de charge, économie d'énergie). L'approche combine :
1. **L'inférence marginale continue** : coordonne les xApps de manière continue.
2. **Détection de points fixes fractionnaires** : détecte quand la configuration devient instable lors de l'arrondi probabiliste.
3. **Réparation locale exacte (CP-SAT)** : extrait un sous-problème induit par le conflit et le résout de façon exacte à l'aide de Google OR-Tools.
4. **Vérification indépendante** : s'assure qu'aucune action conflictuelle ou violant un SLA n'est appliquée sur le réseau physique.

Ce travail a abouti à la rédaction d'un article scientifique destiné au journal *Annals of Telecommunications*.

**Mise à jour (audit et correction, juillet 2026).** Le pipeline expérimental et le manuscrit contenaient des incohérences majeures (résultats contredits par les données, valeurs physiquement impossibles, texte corrompu par un script d'injection regex). Les corrections apportées :
- **Générateur d'instances** (`simulator.py`) : plantation d'une solution faisable garantie (les instances étaient auparavant majoritairement infaisables, plafonnant CP-SAT lui-même à ~20%) + noms de variables encodant le type d'action.
- **Modèle KPI réseau** : `compute_kpis` répond désormais réellement à la décision choisie (les KPIs étaient identiques pour toutes les méthodes).
- **Réparation** (`verixapp.py`/`repair.py`) : réparation locale exacte avec escalade des hops (0 réparation réussissait avant ; 38/38 désormais).
- **Résultats honnêtes régénérés** : Continuous-only 74,7% faisable (25% de stalls), VeriXApp et CP-SAT 100%. VeriXApp n'améliore PAS la latence face à CP-SAT (rapide et complet à cette échelle) ; sa valeur est le diagnostic des stalls et la garantie de vérification. Intégrité : 0 violation sur 750 décisions.
- `fill_paper.py` (script regex qui corrompait `main.tex`) a été neutralisé ; il n'écrit plus que le fragment `main_results.tex`.

Toutes les tables/figures/abstract/conclusion ont été réalignées sur les CSV réels et le PDF recompile proprement.

## 2. Structure et Détails du Code

### `experiments/`
Ce dossier contient l'intégralité du simulateur Python conçu pour modéliser le contrôleur O-RAN et tester la méthode VeriXApp face à d'autres méthodes de référence.

#### Le Cœur du Framework (`experiments/src/`)
- `models.py` : Définit la modélisation mathématique du problème en tant que Problème d'Optimisation de Contraintes (COP). On y trouve les classes `Variable` (actions xApp) et `Constraint` (conflits directs, indirects et implicites).
- `simulator.py` : Un générateur d'instances synthétiques O-RAN permettant de créer des réseaux de cellules, d'utilisateurs et de xApps avec différentes densités de conflits.
- `verifier.py` : L'entité de vérification indépendante de bout en bout qui garantit que les règles strictes (SLA, contraintes matérielles) ne sont jamais violées par les décisions finales.

#### Les Solveurs (`experiments/solvers/`)
- `continuous.py` : L'algorithme central d'inférence continue. Il calcule les pondérations géométriques conditionnées, applique la polarisation, et inclut la logique pour détecter l'état de `Fractional Stall`.
- `repair.py` : L'adaptateur de réparation exacte via le solveur **OR-Tools CP-SAT**. Il extrait le cœur du conflit ("repair core") et génère une assignation valide minimisant l'impact sur l'état du réseau.
- `verixapp.py` : Le pipeline complet combinant `continuous.py`, `repair.py` et la vérification finale.
- `baselines.py` : Implémentations de comparaison :
  - **Uncoordinated** : Aucune coordination.
  - **Static Priority** : Coordination basée sur des priorités strictes fixées par l'opérateur.
  - **CP-SAT (pure)** : Résolution globale exacte (efficace mais parfois trop lente pour les contraintes en quasi-temps réel).

#### Les Scénarios Expérimentaux (`experiments/scenarios/`)
Ils reproduisent avec précision les 5 typologies de conflits définies dans l'étude :
- `s1_power_conflict.py` : Conflit Direct (Augmentation de couverture vs Économie d'énergie sur la puissance d'émission).
- `s2_resource_conflict.py` : Conflit Indirect sur l'allocation des blocs de ressources radio.
- `s3_mobility_energy.py` : Conflit de Mobilité et Énergie (Mise en veille d'une cellule avec un offset de handover agressif).
- `s4_load_balancing.py` : Conflit d'équilibrage de charge réseau.
- `s5_stress_test.py` : Un test d'effort extrême avec de multiples xApps (5 par cellule) et des densités de conflits massives.

#### Exécution et Évaluation (`experiments/evaluation/`)
- `runner.py` : Script principal qui exécute de manière automatisée tous les scénarios et toutes les baselines sur de multiples essais, afin d'en extraire la latence, la viabilité, et les occurrences de stall.
- `report.py` : Script d'agrégation qui compile les statistiques brutes (`raw_results.csv`) en tableaux formatés prêts pour LaTeX (`main_results.tex`).
- `fill_paper.py` : Un script Python sur mesure utilisant des expressions régulières pour injecter directement et proprement les résultats finaux dans le fichier source LaTeX de l'article (remplacement des blocs `\TODO`).

### Résultats de Simulation (`experiments/results/`)
- `raw_results.csv` : Base de données de simulation brute pour chaque méthode, chaque scénario et chaque essai.
- `main_results.csv` : Statistiques agglomérées (latence médiane, latence au 95ème centile, taux de blocage, taux de viabilité).
- `main_results.tex` : Code LaTeX généré reprenant les métriques à inclure directement dans le manuscrit.

## 3. Dossier Racine (Manuscrit LaTeX)
- `main.tex` : Le manuscrit source de l'article, formaté pour *Springer Nature* (`sn-jnl.cls`). Le code a été mis à jour par script et contient désormais toutes les métriques tirées des expérimentations.
- `main.pdf` : Le rendu final en PDF compilé avec succès et sans avertissements critiques.
- `references.bib` & `sn-mathphys-num.bst` : Les références bibliographiques et le style défini par l'éditeur.
- `Protocole.md` : Fichier de demande initiale (resté vierge).
- `STATE.md` : Ce présent document, qui décrit en détail l'organisation et la raison d'être de chaque module du projet.
