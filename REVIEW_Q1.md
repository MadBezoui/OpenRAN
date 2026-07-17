# Rapport de review (standard Q1) — main3.tex « Consistency-Guided xApp Coordination »

*Rédigé le 2026-07-16. Style : rapport de referee complet, suivi de la liste des corrections effectivement appliquées au manuscrit et des nouvelles preuves expérimentales produites (E1–E4, E6).*

---

## Recommendation: Major revision

**Summary.** The paper formulates multi-xApp coordination in the O-RAN near-RT RIC as a dynamic finite-domain CSP/COP and proposes ConsistXApp: incremental GAC with explanations, a continuous relation-conditioned inference stage, explanation-guided exact local repair, and an independent verifier. Evaluation on five synthetic O-RAN scenarios (250 static instances, 15,000 dynamic epochs) shows sound propagation, 100% incremental/recompute agreement, and — reported honestly — that the continuous stage is counterproductive while GAC + explanation repair matches full CP-SAT at lower latency.

**Significance.** The problem is timely and the solve-and-verify architecture with auditable explanations is a genuine differentiator w.r.t. QACM, CMF, COMIX and XAI-based approaches. The candour about negative results is commendable. However, in its current form the paper's headline architecture is empirically dominated by its own baselines on the tested workload, several methodological promises are not kept in the results, and key claims rest on statistically insignificant differences.

### Major concerns

**M1 — The evaluated regime cannot support the claims (fatal as-is).**
All static scenarios have only 12–30 variables; full CP-SAT solves them in 2.8 ms — 36× under the 100 ms budget. In this regime no coordination architecture is needed beyond calling CP-SAT, so neither feasibility nor latency can motivate the proposed pipeline. The methodology (§ Static instance suite) even announces n ∈ {12,…,500} and deadlines {10,50,100,500,1000} ms, which the results never deliver. *Required:* either evaluate at scales/densities where the from-scratch solver becomes budget-critical, or reframe the contribution around a regime where the architecture demonstrably matters (see M2).

**M2 — The genuinely promising result is under-exploited.**
The paper's real asset is the *sequential* setting: incremental propagation reuses work across epochs (−96% propagation time) and local repair scales with the size of the change, not of the model. Yet the dynamic suite only measures propagation time, never end-to-end epoch cost against a re-solve baseline, and no warm-start CP-SAT (solution hints) baseline is included — the one competitor a CP practitioner would demand.

**M3 — Statistical support absent or contradicting the text.**
The Statistical-protocol subsection promises Holm-corrected tests and paired effect sizes; none appear. Re-analysis of the released raw logs shows: (i) the latency advantage of GAC+expl-repair over CP-SAT is real (Wilcoxon paired p≈7·10⁻³⁴, Cliff's δ=−0.45); but (ii) the success-rate differences in the repair ablation (100% vs 96.9–98.4%) rest on 1–2 discordant pairs out of 64 and are **not significant** (exact McNemar p≥0.5, Holm-adjusted p=1.0). The claim that explanation-guided cores "fail less" than radius cores must be withdrawn or re-powered; what *is* supported is the time/core-size advantage (fullscope vs explanation: δ=−0.96, p≈2·10⁻²⁰).

**M4 — "Independent verifier" independence is asserted, not demonstrated.**
The verifier is 42 lines of Python living in the same repository, same language, same data structures as the solver. The paper's own protocol (exhaustive oracle, second implementation without shared code, property-based testing, mutation testing) is described but never executed. For a paper whose central guarantee is "no false positive", this validation *is* the contribution and must be reported.

**M5 — No baseline from the O-RAN conflict-management literature.**
All ten methods are internal ablations plus generic CP-SAT. QACM, priority-based CMF, game-theoretic bargaining, COMIX-style policies are discussed in related work but never compared. At minimum, a QoS-aware optimizing baseline and a bargaining baseline on the same instances are needed to substantiate any claim of advancing the state of the art.

**M6 — Internal inconsistencies.**
(a) RQ5 promises a comparison against "the original VeriXApp pipeline" that never appears; (b) the scalability table's caption claims ten seeds but n=100 has one seed and two cells are blank, including the paper's preferred method; (c) the repair-ablation caption says 64 cases while the released CSV contains 114 (standard+stress pooled) — sample composition must be explicit; (d) the AI-use statement contains an unresolved editorial instruction ("This statement must be adapted…"); (e) data availability mixes an anonymized placeholder with a non-anonymized submission; (f) uncoordinated/static-priority baselines at exactly 0% verified feasibility require an explanation of execution semantics to avoid appearing strawmen.

### Minor

Fig. 4 caption ("cumulative network utility over time") does not match the static suite; part-file scaffolding comments and an unused TODO macro remain; XAI4C (Varshney et al., 2025) — the closest explainability-oriented competitor — is absent from related work; OR-Tools version differs between text and manifest.

---

# Corrections appliquées (avec preuves expérimentales nouvelles)

Toutes les expériences ci-dessous ont été exécutées dans un environnement Linux sandbox (2 vCPU, Python 3.10, OR-Tools 9.15) ; les scripts sont dans `scripts/` et les données dans `artifacts/raw/` + `artifacts/tables/`. Les latences absolues doivent être re-mesurées sur la machine de référence avant soumission (`scripts/run_breakpoint.py`, `run_dynamic_scale.py`, `run_verifier_validation.py`, `run_literature_baselines.py`, `stats_paired.py`), mais les ordres de grandeur et croisements sont robustes.

## R-M1/M2 — Nouveau régime d'évaluation (E1 + E2)

**E1 (one-shot, à froid)** — `breakpoint_results.csv`, n ∈ {30,…,1000}, d=6, |C|=2n, tightness 0.25, planted-SAT :
CP-SAT reste sous 100 ms jusqu'à n=1000 (43 ms méd.) ; GAC+expl-repair à froid le dépasse (83 ms méd., p95 105 ms). **Conclusion honnête : aucun point de rupture one-shot en faveur de la méthode ≤1000 variables.** Le papier ne doit PAS prétendre le contraire.

**E2 (séquentiel, amorti)** — `dynamic_scale_results.csv`, épisodes de 30 époques, δ ∈ {2%,10%} des relations modifiées par époque (solution plantée préservée), 3 baselines par époque sur épisodes identiques :

| n    | δ  | CP-SAT rebuild (méd.) | CP-SAT hint (méd.) | Réparation incrémentale (méd. / p95) |
| ---- | --- | ---------------------- | ------------------- | --------------------------------------- |
| 100  | 2%  | 3.3 ms                 | 3.4 ms              | **0.06 / 2.8 ms**                 |
| 300  | 2%  | 9.2 ms                 | 9.2 ms              | **1.4 / 3.0 ms**                  |
| 600  | 2%  | 16.6 ms                | 18.0 ms             | **2.6 / 9.4 ms**                  |
| 1000 | 2%  | 25.3 ms                | 27.4 ms             | **5.1 / 24.3 ms**                 |
| 1000 | 10% | 19.1 ms                | 20.5 ms             | **4.5 / 56.7 ms**                 |

100 % de faisabilité vérifiée partout. Le warm-start (hints) n'aide pas : le coût dominant du re-solve est la **reconstruction du modèle**, O(modèle), tandis que la réparation locale paie O(changement). L'avantage médian croît avec n (×5 à n=1000) ; la queue p95 se dégrade quand δ augmente (57 ms à δ=10 %) — compromis explicite rapporté. **C'est le repositionnement central du papier : l'argument est séquentiel/amorti, pas one-shot.**

## R-M3 — Statistiques appariées (E6) — `stats_paired.json`

Ajoutées au manuscrit : McNemar exact (faisabilité), Wilcoxon signé (latence), δ de Cliff, correction de Holm. Résultats clés : latence GAC+expl vs CP-SAT p≈7·10⁻³⁴, δ=−0.45 ; ablation succès explanation vs radius0 : 2 paires discordantes, p_Holm=1.0 → **revendication de succès retirée du texte**, remplacée par l'avantage temps/taille de cœur (p≈2·10⁻²⁰, δ=−0.96 vs fullscope). Déficit de faisabilité du pipeline continu : p_McNemar=0.016 (brut), 0.078 (Holm).

## R-M4 — Validation du vérificateur (E4) — `verifier_validation.json`

| Porte | Contenu                                                                                                                                             | Résultat     |
| ----- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| G1    | 500 instances, 60 650 affectations énumérées vs oracle indépendant                                                                              | 0 divergence  |
| G2    | Second vérificateur CP-SAT déclaratif (parseur JSON séparé), accord triple                                                                      | 1 800/1 800   |
| G3    | 602 000 vérifications de propriétés (déterminisme, invariances permutation/renommage, rejets hors-domaine/variable manquante/contexte périmé) | 0 échec      |
| G4    | 16 000 mutants (13 594 invalides selon l'oracle)                                                                                                    | 0 mal classé |

## R-M5 — Baselines littérature (E3) — `literature_baselines.csv`

QACM-like (maximisation des requêtes préférées satisfaites) et NSWF-like (bien-être social de Nash discrétisé) implémentées sur les mêmes instances S1–S5 : 100 % faisables, 2.2/3.5 ms méd., ~64 % de requêtes préférées conservées. Différenciateurs de ConsistXApp : explications auditables + réparation locale amortie (aucune des deux baselines ne le fait) ; en régime séquentiel elles repayent le rebuild complet (E2).

## R-M6 + mineurs — Corrections éditoriales appliquées à main3.tex

Titre (retrait de la promesse fractional-stall), abstract réécrit autour du résultat amorti, RQ5 sans VeriXApp, plage n du static suite alignée sur les données, captions scalabilité/ablation corrigées (seeds réels, composition 64+50), déclaration IA nettoyée, disponibilité des données unifiée, XAI4C ajouté au related work + bib, commentaires d'échafaudage supprimés, nouvelles sous-sections méthodo/résultats pour E1/E2/E3/E4/E6, section stats désormais conforme à ce qui est réellement rapporté.

## Reste à faire avant soumission (non exécutable dans cette session)

1. Re-mesurer E1/E2 sur la machine de référence (28 cœurs) et regénérer les tables (scripts fournis, ~1 h).
2. E5 : validation en boucle fermée ns-3/OpenRAN Gym sur S1 et S3 (2–3 semaines) — seul point restant du protocole niveau C.
3. Ablation de réparation re-puissancée (≥1 000 cas déclencheurs) si l'on veut réhabiliter la revendication de succès ; sinon la version corrigée (avantage temps/cœur uniquement) est défendable telle quelle.
4. Archive Zenodo + Dockerfile pour le badge artefacts.
