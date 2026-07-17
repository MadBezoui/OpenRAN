# Réponse point par point à AUTO_review_main4.md

*Traitement du 2026-07-17. Chaque remarque a été vérifiée contre le code et les données avant décision. Manuscrit corrigé : `main4.tex` / `main4.pdf` (18 pages, 0 erreur, 0 débordement visible).*

## Préoccupations majeures

**2.1 Incohérence de décodeur (Table 5) — FONDÉE, corrigée + nouvelle expérience.**
Vérifié dans `scripts/run_static.py` : « GAC + decode » utilisait `decode="continuous"`, ConsistXApp `decode="utility"` — deux générateurs de candidats différents, mal étiquetés. Corrections : (i) la ligne est renommée « GAC + continuous decode » et déplacée dans le bloc continu du tableau ; (ii) une vraie ablation « GAC + utility decode (no repair) » a été exécutée : **2 direct / 248 bloqués** — identique aux candidats de ConsistXApp, la contribution de la réparation est désormais isolée proprement (0.8 % → 100 % sur les mêmes candidats) ; (iii) la règle de génération de candidat de chaque méthode est définie explicitement en §6.2.

**2.2 Ablation pas sur les vrais candidats — FONDÉE, ré-exécutée intégralement.**
Nouveau script `run_repair_ablation_utility.py` : les 8 stratégies sur les **248 candidats opérationnels** (+ 50 stress, strates séparées). Résultat plus fort qu'avant : violated0/radius0 échouent sur 8.5 % (21/248), stratégies expansives 100 %, et la différence est désormais **significative** (McNemar exact, Holm p=6·10⁻⁶ — 21 paires discordantes unilatérales). Cœurs : 11 (explanation) vs 16 (radius-2) vs 20 (full scope). Table 7, figure et texte entièrement refaits ; l'ancienne suite à 64 cas est retirée.

**2.3 Qualité d'objectif non comparée — FONDÉE, expérience ajoutée.**
`run_objective_gap.py` : réparation locale du vecteur de requêtes préférées vs optimum exact CP-SAT du même objectif. Résultat : 53.8 % vs 64.6 % de requêtes conservées (gap moyen 10.8 pts, p≈10⁻³⁷, gap nul sur 12.8 % des instances), à moitié du coût. Le papier distingue désormais explicitement « fast feasible repair » et « globally optimal coordination » (§7.4, abstract, limitations, conclusion).

**2.4 Encodage assumption-core ambigu — FONDÉE POUR LE TEXTE, infondée pour le code.**
`cpsat_adapter.solve_with_assumptions` utilise déjà les vrais littéraux (`NewBoolVar` + `OnlyEnforceIf` + `AddAssumptions` + `SufficientAssumptionsForInfeasibility` + mapping indices→variables + fallback si cœur vide). Le §4.3 décrit maintenant ce mécanisme exactement, précise que le modèle d'extraction n'a pas d'objectif, que UNKNOWN = timeout, que la variante par défaut (explanation) utilise wipeout-explanation puis frontière, et l'ordre d'expansion déterministe est documenté (répond aussi à 4.4). Versions OR-Tools dans les manifests et §6.2.

**2.5 Trop peu de répétitions — FONDÉE, ré-exécuté.**
Cold-start : 20 seeds/taille (au lieu de 5). Séquentiel : **10 épisodes**/configuration (au lieu de 3), et l'épisode est désormais l'unité statistique : médianes par épisode, Wilcoxon apparié au niveau épisode (rank-biserial = −1.0, p=0.002 — valeur minimale atteignable à N=10, chaque épisode favorise l'incrémental), HL par épisode. p99 et max rapportés.

**2.6 Définition opérationnelle du séquentiel — FONDÉE, précisée.**
Le protocole est l'option A (candidat = décision vérifiée précédente, re-vérifiée puis réparée si violée) — désormais écrit noir sur blanc en §6.2 et §7.6, avec la statistique demandée : fraction d'époques sans violation = 69 % (n=100) mais **1.7 % seulement à n=1000, δ=2 %** — l'avantage ne vient pas de re-vérifications triviales. Décomposition build/search instrumentée pour les baselines.

**2.7 Générateur trop facile (ancre plantée statique) — FONDÉE, variante drift ajoutée.**
Nouveau mode `--replant` : 1 % des variables re-plantées par époque → la décision précédente est invalidée à **chaque** époque (0 % re-vérification), et la réparation incrémentale garde ×3 en médiane (9.8 vs 28.1 ms à n=1000). Rapporté (Table 9, §7.6) + limitation explicite (domaines/activations/utilités non déplacés conjointement).

**2.8 « Model-construction dominance » affirmée sans preuve — FONDÉE, corrigée par instrumentation.**
Mesuré : à n=1000 le re-solve passe 6.9 ms en build et 18.4 ms en search — le search domine, la formulation d'origine était fausse. Nouveau texte empirique : les deux composantes croissent avec le modèle et sont insensibles à δ et aux hints ; la réparation croît avec le nombre de relations violées. L'abstract et l'intro reformulés en conséquence.

**2.9 « Strict 100 ms » vs 365 ms — FONDÉE, terminologie corrigée.**
§6.2 : le budget est un *post-hoc compliance threshold* vérifié aux frontières d'étages, pas une préemption ; « deadline-bounded » remplacé par « budget-aware ».

**2.10 Incohérences 249/250 — FONDÉE, expliquée.**
Investigation données : une instance S5 erronée avant complétion pour les 3 variantes continues (N=249, complete-case, erreur liée à l'implémentation continue) ; un KPI manquant (S5/seed 91, décision vérifiée mais calcul KPI en erreur, rapporté manquant, non imputé). Colonne N ajoutée à la Table 5, captions de Tables 5/6/10 explicites (répond aussi à 3.3).

**2.11 Suite repair-stress non documentée — FONDÉE, définie.**
§6.1 : 50 instances, 24 variables, d=4, 34 relations (70 % égalités), candidat = solution plantée avec 3 variables inversées. Table 7 sépare les deux strates (plus de pooling silencieux).

**2.12 « Explanation for every repair » survendu — FONDÉE, taxonomie adoptée.**
§4.3 définit le **repair certificate** (candidat, témoins de violation, trajectoire du cœur avec source d'expansion, variables relâchées, affectation finale, verdict) ; les explications de propagation et les cœurs solveur en sont des composantes quand il y a expansion. Abstract et texte alignés ; les compteurs e/a/f de la Table 7 rendent l'usage réel transparent (16/21/29 expansions sur 248).

## Statistiques

**3.1 Cliff's delta non apparié — FONDÉE** : remplacé partout par rank-biserial apparié + Hodges–Lehmann + IC bootstrap (`stats_paired_v2.py`, Table 6). **3.2 — FONDÉE** : la marge d'1 ms est qualifiée de « statistically firm but operationally modest » (§7.3, conclusion). **3.3 — FONDÉE** : politique complete-case dans les captions. **3.4 — FONDÉE** : IC bootstrap ajoutés à la Table 10, énoncé affaibli (« no material KPI degradation was detected in this synthetic model »).

## Points mathématiques

**4.1 — FONDÉE** : Prop. 1 requalifiée d'invariant architectural dont la force vient des portes de validation. **4.2 — FONDÉE** : l'exemple précise requêtes = préférences souples, domaines multivalués. **4.3 — FONDÉE** : hypothèse d'encodage exact ajoutée à la complétude conditionnelle. **4.4 — FONDÉE** : ordre déterministe documenté (wipeout-explanation → cœur d'assomption [variante] → frontière ; UNKNOWN = timeout).

## Évaluation

**5.1 — FONDÉE** : distinction gain relatif (96 %) / absolu (~0.1 ms) explicite ; les gains séquentiels viennent d'éviter le re-solve. **5.2 — FONDÉE** : parité p95 et croisement p99 dans l'abstract, §7.6, limitations, conclusion ; p99 et max dans la Table 9. **5.3 — FONDÉE** : le seuil d'escalade est déclaré non évalué → future work. **5.4 — FONDÉE** : rebaptisées « objective-inspired baselines », reproduction d'objectif et non des systèmes. **5.5 — FONDÉE** : formulation exacte suggérée adoptée.

## Vérificateur

**6.1 — FONDÉE** : G4 renommé « oracle-labelled input mutation (fuzzing) » partout, avec la précision que cela borne la mauvaise classification, pas la couverture au sens mutation-testing du code. **6.2 — FONDÉE** : frontière d'indépendance documentée (pas de parseur/normalisation/indexation partagés ; entrées malformées couvertes par G3).

## Éditorial (7.1–7.13)

Fig. 3 régénérée sans labels M8/M9 (nouvelles données opérationnelles) ; Table 9 reformatée en pleine largeur ; références réparées (URLs dupliquant les DOI supprimées, Yedidia en incollection Morgan Kaufmann, wadud2025mobility complétée avec son venue réel INFOCOM WKSHPS 2025, booktitle wadud2023game développé, navarro2026 invérifiable supprimée) ; capitalisation protégée ({QoS}, {xApp}, {Open RAN}, {Near-RT} {RIC}, {6G}) ; « deadline-bounded » retiré ; « none of which had previously been applied » adouci en « to our knowledge » ; 680 450 exact ; matériel/versions/seeds dans §6.2 + deux manifests. La structure Q1/Q2/Q3 recommandée (§8) correspond déjà à l'ordre Trust → Repair → Scale de la section Résultats ; pas de restructuration supplémentaire.

## Non retenu

- **2.4 (volet code)** : l'implémentation des assumptions était déjà correcte — seul le texte a été précisé.
- **6.1 (mutation score du code)** : créer des mutants du code du vérificateur est une campagne distincte, notée comme travail futur — la formulation revendiquée a été affaiblie en conséquence, donc plus rien ne l'exige.
- **§8 restructuration complète** : déjà satisfaite dans l'esprit ; réorganiser davantage n'apporterait rien.

## Impact sur les chiffres clés du papier

| Avant | Après (corrigé) |
|---|---|
| Ablation : 100 % vs 96.9 %, non significatif (2/64) | 100 % vs 91.5 %, significatif (21/248, p=6·10⁻⁶) |
| Cœurs 2 vs 24, « 6× plus petit, 5× plus rapide » | Cœurs 11 vs 20, 1.5× plus rapide — honnête |
| Séquentiel : 3 épisodes, époques comme unités | 10 épisodes, épisode = unité, rb=−1.0, p=0.002 |
| « Model reconstruction dominates » | build 6.9 + search 18.4 ms, les deux ∝ modèle |
| Pas de gap d'objectif | 10.8 pts quantifiés vs optimum exact |
| Queue non discutée | p95 parité, p99 croisement, drift ×3 médian |
