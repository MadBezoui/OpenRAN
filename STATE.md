# État du Projet OpenRAN (ConsistXApp)

Ce document décrit de A à Z le projet **OpenRAN** (dont la méthode principale est nommée **ConsistXApp**). Il vise à fournir une vue d'ensemble exhaustive du contexte, des objectifs scientifiques, de l'architecture du code, et de l'état actuel de l'avancement.

---

## 1. Contexte et Objectif Principal

Le projet s'inscrit dans le domaine des réseaux **O-RAN (Open Radio Access Network)** et se concentre sur la gestion des conflits entre **xApps** fonctionnant sur le contrôleur intelligent (near-real-time RIC).
L'objectif est d'arbitrer les requêtes concurrentes de différentes xApps qui pourraient être mutuellement incompatibles, en compétition pour des ressources partagées, ou en violation des SLA (Service-Level Agreements).

Pour ce faire, le projet modélise la coordination multi-xApp comme un problème dynamique d'optimisation sous contraintes à domaines finis (Dynamic Constraint Satisfaction/Optimization Problem).

## 2. La Méthodologie ConsistXApp

La solution développée, **ConsistXApp**, est un framework de coordination basé sur la cohérence (consistency-guided framework) organisé en cinq étapes :

1. **Modélisation dynamique à domaines finis** des actions candidates des xApps.
2. **Propagation incrémentale (GAC - Generalized Arc Consistency)** pour éliminer de manière sûre les actions qui violent les contraintes dures.
3. **Inférence continue conditionnée par les relations** sur les domaines filtrés.
4. **Diagnostic des blocages fractionnaires** et **réparation exacte guidée par les explications** (lorsqu'une assignation reste invalide malgré un point fixe non vide de la propagation).
5. **Vérification indépendante** avant d'envoyer toute décision à l'interface E2.

## 3. Architecture du Dépôt

Le dépôt est structuré pour séparer la rédaction scientifique, le code métier, les protocoles de test et les résultats :

*   **Livrable Scientifique (Manuscrit)** :
    *   `main3.tex`, `main3.pdf` : L'article de recherche (version 3) ciblant les *Annals of Telecommunications*.
    *   `references.bib`, `sn-jnl.cls`, `sn-mathphys-num.bst` : Dépendances et bibliographie LaTeX (format Springer Nature).
*   **`src/` (Code Source de la Méthode)** :
    *   Contient les modules d'optimisation, de modèles réseaux, de propagation, de réparation, et le vérificateur formel indépendant.
*   **`experiments/` (Bancs d'essais)** :
    *   Définition des scénarios (statiques et dynamiques), solveurs de référence, et données d'évaluation. C'est ici que sont évaluées les performances temporelles (sous une contrainte stricte de 100ms) et l'utilité télécom.
*   **`scripts/` (Automatisation et Traitement)** :
    *   Nombreux scripts Python (`generate_figures.py`, `check_metrics.py`, `run_dynamic.py`, `inject_latex.py`, etc.) servant à lancer les expériences, extraire les métriques, générer les graphiques, et les injecter directement dans le code LaTeX.
*   **`artifacts/` (Ressources Générées)** :
    *   Stocke les figures, tables et données brutes produites par les scripts et intégrées dans le PDF final.
*   **`Protocole.md`** :
    *   Un document critique définissant le protocole expérimental complet (MIRAGE-R), les limites éthiques de validation, et les six garanties scientifiques évaluées (correction, utilité, respect du budget temps, reproductibilité, etc.).

## 4. Résultats et État d'Avancement

*   **Campagne d'évaluation** : Le framework a été validé sur 15 000 époques de décision uniques pour dix méthodes, produisant 150 000 observations.
*   **Performances** : La propagation GAC réduit l'espace de recherche (réduction de 21.7% des valeurs et 34.1% des tuples), ce qui diminue significativement la taille du cœur de réparation exacte. ConsistXApp atteint une faisabilité de 74.4% et respecte les délais stricts (deadline compliance) dans 56.8% des cas sous 100ms.
*   **Prochaines Étapes** : Le manuscrit `main3` (intégrant la méthode ConsistXApp par rapport à l'ancienne legacy VeriXApp) est la version la plus récente et constitue le livrable final attendu de ce dépôt.

---
*Ce document sert de point de repère pour comprendre l'écosystème global du projet, des aspects théoriques jusqu'à l'implémentation et la rédaction de l'article de recherche.*
