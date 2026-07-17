# Audit critique et plan d'expérimentation — ConsistXApp (main3)

*Généré le 2026-07-16. Basé sur l'analyse de `main3.tex`, `Protocole.md`, `src/`, `experiments/` et des données réelles dans `artifacts/`.*

---

## 1. Verdict d'ensemble

Le projet est **méthodologiquement sérieux** (manifests, seeds, CIs bootstrap, comptages entiers, vérificateur, honnêteté sur les limites) mais souffre d'un **problème de positionnement fatal pour un reviewer exigeant** : *vos propres données montrent que la méthode proposée est dominée par une baseline triviale sur le benchmark actuel.*

Extrait de `artifacts/tables/summary.json` (suite statique, N=250) :

| Méthode | Faisabilité vérifiée | Deadline 100 ms | Latence méd. | p95 |
|---|---:|---:|---:|---:|
| CP-SAT complet | **100 %** | **100 %** | 2.8 ms | 4.8 ms |
| GAC + CP-SAT | 100 % | 100 % | 2.6 ms | 4.7 ms |
| GAC + expl-repair | 100 % | 100 % | **1.8 ms** | 3.8 ms |
| ConsistXApp (expl/radius/assume) | 97.2–97.6 % | 57 % | ~80 ms | ~253 ms |
| Continuous only | 75.6 % | 23.6 % | 180 ms | 366 ms |

Et `scalability_results.csv` confirme : CP-SAT résout n=100 en **12 ms**, tandis que le pipeline continu prend 295 ms (médiane) à n=50.

**Conséquences :**

1. L'étage d'inférence continue (consensus géométrique, stalls fractionnaires) — qui occupe ~40 % du manuscrit et la totalité de l'analyse théorique de la Section 5 — **dégrade** faisabilité et latence. L'abstract l'admet déjà (« The continuous inference stage is *not* justified... »). Un papier dont la contribution centrale est empiriquement contre-productive ne passe pas un round de review sévère, même en Q2.
2. La vraie pépite est ailleurs : **GAC + réparation locale guidée par explications bat CP-SAT complet (1.8 vs 2.8 ms) tout en produisant des cœurs auditables minimaux**. Mais un gain de 1 ms sur des instances résolues en 3 ms n'intéresse personne. Il faut un régime où CP-SAT complet **casse** le budget de 100 ms et où votre approche locale/incrémentale tient.
3. Les instances sont **trop petites** : 12–30 variables (S1–S5). Le Protocole prévoyait un palier « Stress » (501–2 000 variables, jusqu'à 20 000 contraintes) — jamais exécuté.

**La bonne nouvelle : le problème n'est pas la méthode, c'est le benchmark.** La réparation locale incrémentale a précisément son intérêt quand (i) les instances sont grandes, (ii) les époques s'enchaînent avec des changements localisés, (iii) résoudre from scratch dépasse le budget. Rien de tout cela n'est exercé aujourd'hui.

---

## 2. Défauts détaillés (par ordre de gravité)

### D1 — La méthode phare est dominée par ses baselines (bloquant)
Voir §1. Deux issues possibles, détaillées en §3.

### D2 — Ablation de réparation sous-puissante statistiquement
`repair_ablation.csv` : **n=114** cas déclencheurs seulement. Les écarts revendiqués (100 % vs 98.2 % pour radius/violated0) reposent sur **2 échecs sur 114**. Aucun test apparié, pas de correction de comparaisons multiples. Un reviewer statistique rejettera la conclusion « explanation > radius ». Il faut ≥ 1 000 cas déclencheurs stratifiés par échelle.

### D3 — Le « vérificateur indépendant » ne l'est pas vraiment
`src/verification/verifier.py` = **42 lignes**, même langage, même dépôt, mêmes structures de données que le solveur. Le Protocole (§6.2) exigeait une double implémentation sans code partagé (Python + CP-SAT déclaratif ou Java) + oracle exhaustif + property-based testing (100 k triplets) + mutation testing (critères G1–G4). **Rien de tout cela n'existe dans le dépôt.** C'est pourtant la partie la moins coûteuse et la plus différenciante à implémenter.

### D4 — Aucune baseline issue de la littérature
Les 10 méthodes comparées sont des ablations internes + CP-SAT générique. La littérature 2023–2026 sur les conflits xApps propose des méthodes concrètes reproduites facilement :
- **CMF standard** d'Adamczyk & Kliks (IEEE ComMag 2023) — détection/résolution par types de conflits O-RAN;
- **QACM** (Wadud et al., IEEE TGCN 2024) — mitigation QoS-aware, la baseline de référence du domaine;
- approche **théorie des jeux coopératifs** (NSWF / Eisenberg-Gale, Wadud et al. 2023);
- **COMIX** (Giannopoulos et al., IEEE Access 2025) — politiques de résolution + digital twin;
- **XAI4C** (Varshney et al., IEEE VTM 2025) — le concurrent direct sur le terrain « explicabilité ».
Sans au moins QACM et une politique CMF, l'affirmation « dépasse la littérature » est invérifiable.

### D5 — Niveau C (validation télécom en boucle fermée) absent
Le modèle réseau est « pseudo-physique » maison (`src/network/physical_model.py`). Le Protocole prévoyait ns-3 O-RAN / OpenRAN Gym / FlexRIC+srsRAN. Pour Annals of Telecommunications c'est acceptable *si bien justifié*, mais une validation même partielle en émulation (un scénario, une topologie) ferait passer le papier au niveau supérieur et neutraliserait l'objection « simulation jouet ».

### D6 — Statistiques incomplètes
Bootstrap CIs : bien. Manquent : tests appariés (Wilcoxon signé sur instances identiques), tailles d'effet (delta de Cliff), correction Holm–Bonferroni sur la famille de comparaisons, et une justification du nombre de seeds.

### D7 — Incohérences de présentation
- Le manifest indique OR-Tools 9.14 / Python 3.13 mais `EXPERIMENTS.md` et l'environnement de test diffèrent ; figer via Docker/conda-lock.
- `Protocole.md` contient des blocs LaTeX corrompus (`D_}\n===`, `\mathcal\n========`) — à nettoyer avant de le publier en annexe.
- Le titre promet « Fractional-Stall Diagnosis » comme contribution alors que les résultats la déjugent.
- Uncoordinated et Static priority affichent 0 % de faisabilité vérifiée — vérifier que ce n'est pas un artefact de sémantique d'exécution (0 % rend la baseline caricaturale ; un reviewer demandera pourquoi elles ne proposent jamais d'action valide).

---

## 3. Repositionnement scientifique recommandé

### Option A (recommandée) — « Coordination sous budget : là où le solveur complet casse »
Thèse : *dans le near-RT RIC, le budget de 10–100 ms est non négociable ; à l'échelle (centaines de cellules × xApps × paramètres, contraintes couplantes), un CP-SAT complet from scratch viole le budget, alors que propagation incrémentale + réparation locale guidée par explications maintient faisabilité vérifiée et latence bornée, avec un artefact d'auditabilité (cœurs minimaux, explications) qu'aucune baseline ne fournit.*

Contributions vendables :
1. Formulation DCSP de la coordination multi-xApp avec relations conditionnées par le contexte (déjà bien écrite) ;
2. GAC incrémental inter-époques avec garantie d'accord 100 % et gain amorti (déjà démontré : −96 % de temps de propagation) ;
3. Réparation exacte locale guidée par explications, **prouvée équivalente au recalcul complet mais sous-linéaire dans la taille du changement** — c'est le théorème utile à mettre en avant ;
4. Pipeline solve-and-verify avec vérificateur réellement indépendant + validation G1–G4 (unique dans la littérature xApp) ;
5. Domination empirique de CP-SAT complet et des baselines littérature **au-delà du point de rupture d'échelle** + boucle fermée télécom.

L'étage continu : le **retirer du chemin critique** et le reléguer en une sous-section « alternative explorée » ou le supprimer. Garder l'analyse des stalls fractionnaires seulement si elle sert la motivation du repair (elle peut : « pourquoi l'arrondi/le décodage échoue → nécessité du repair exact »).

### Option B — Pivot explicabilité (plus risqué)
Concurrencer XAI4C frontalement : métriques d'explication (taille de cœur, minimalité prouvée, temps de génération, fidélité), étude d'utilité des explications. Plus original mais demande une évaluation utilisateur/opérateur difficile. Non recommandé seul ; intégrable comme axe secondaire de l'Option A.

---

## 4. Campagne expérimentale lourde (« ce qu'il faut faire tourner »)

Toutes les campagnes ci-dessous sont dimensionnées pour votre machine (28 cœurs). Estimations de temps = ordre de grandeur, à recaler après un run `--quick`.

### E1 — Frontière d'échelle et point de rupture (CŒUR DU PAPIER)
**But :** localiser le régime où CP-SAT complet viole le budget et montrer que GAC+expl-repair tient.

- Générateur : étendre `src/generators/static_generator.py` aux paliers du Protocole §7 :
  n ∈ {50, 100, 200, 500, 1000, 2000} variables ; |cellules| ∈ {7, 21, 50} ; xApps ∈ {4, 6, 8, 12}.
- Stratification (Protocole §7.2) : d_max ∈ {2, 3–4, 5–8, >8} ; densité contraintes |C|/|X| ∈ {<1, 1–2, 2–4, >4} ; arité max ∈ {2, 3–4, 5–8} ; mix direct/indirect/implicite.
- **Contrôle de dureté** : générer près du seuil de satisfiabilité (calibrer la densité pour ~50–80 % SAT par strate, mesuré par CP-SAT sans limite de temps hors ligne). C'est LE point qui manque : vos instances actuelles sont trivialement SAT.
- Méthodes : CP-SAT complet, GAC+CP-SAT, GAC+expl-repair, GAC+radius-repair, + baselines D4.
- Budgets : 10 ms / 50 ms / 100 ms (le near-RT RIC couvre 10 ms–1 s ; montrer 10 ms est très vendeur).
- 30 seeds × ~600 instances du manifest gelé ; split dev/val/test 20/20/60 (Protocole §8) **réellement appliqué**.
- Sorties : courbes latence vs n (médiane, p95, p99), % deadline vs n, **n\*** (point de croisement) par budget et par strate ; taille de cœur vs n ; mémoire.
- Estimation : ~500 k résolutions bornées à 100 ms ⇒ 10–20 h sur 28 cœurs.

**Critère de succès :** il existe un régime (n ≥ n\*, réaliste pour un RIC de zone dense : ex. 50 cellules × 8 xApps) où CP-SAT complet < 50 % de deadline compliance et GAC+expl-repair > 95 % avec faisabilité vérifiée identique. Si ce régime n'existe pas, l'Option A tombe et il faut le savoir *avant* d'écrire.

### E2 — Régime dynamique longue durée et amortissement incrémental
**But :** montrer que l'avantage croît avec la localité temporelle des changements — l'argument décisif contre « recompute from scratch ».

- 100 000 époques (vs 15 000 actuellement), scénarios S1–S5 étendus aux tailles E1.
- Processus de changement : arrivées/départs d'UEs (Poisson), bursts corrélés (mobilité de groupe), défaillances de cellules, oscillation jour/nuit ; taux de changement δ ∈ {1 %, 5 %, 20 %, 50 %} des domaines/relations par époque.
- Comparer : (a) recompute complet CP-SAT, (b) GAC incrémental + repair local, (c) GAC recompute + repair, (d) warm-start CP-SAT (hint = solution précédente) — **baseline cruciale absente aujourd'hui**, car OR-Tools avec hints est fort ; si vous le battez, l'argument est en béton.
- Métriques : latence amortie par époque, % époques dans budget, distance de Hamming entre décisions successives (churn), stabilité des paramètres réseau (oscillations — KPI télécom apprécié).
- Estimation : ~4–8 h.

### E3 — Baselines de la littérature (obligatoire pour « dépasser la littérature »)
- Implémenter : QACM (optimisation QoS-aware — le papier donne la formulation), politique CMF par types de conflits (Adamczyk), négociation NSWF/Eisenberg-Gale, politique COMIX-like (priorités + évaluation d'impact).
- Les faire tourner sur les MÊMES instances E1/E2 (adapter leurs entrées : elles consomment des conflits pairwise → documenter la projection de votre modèle vers le leur, c'est en soi une contribution de comparabilité).
- Tableau final : faisabilité vérifiée, deadline, KPI réseau, churn, **et auditabilité** (produisent-elles une explication ? non — c'est votre différenciateur).
- Estimation : 3–5 jours d'implémentation, quelques heures de calcul.

### E4 — Validation du vérificateur (niveaux A, G1–G4 du Protocole) — coût faible, valeur énorme
1. **Oracle exhaustif** : n ∈ {2..8}, d ∈ {2,3,4}, énumération complète, 0 divergence exigée (G1).
2. **Second vérificateur sans code partagé** : modèle CP-SAT déclaratif pur (les contraintes re-déclarées depuis le JSON normalisé, jamais depuis les objets Python du solveur). G2 : accord triple oracle/V1/V2.
3. **Property-based testing** : Hypothesis, ≥ 100 000 triplets (instance, contexte, affectation) ; propriétés du Protocole §6.3 (déterminisme, invariances de renommage/permutation, rejets explicites). G3.
4. **Mutation testing** : 9 opérateurs de mutation du Protocole §6.4, invalidité prouvée par l'oracle, taux de rejet = 100 % (G4).
- Estimation : 2–3 jours d'implémentation, < 2 h de calcul. **Aucun papier xApp-conflict ne fait ça ; c'est votre section « Trust » unique.**

### E5 — Boucle fermée télécom (niveau C)
Par ordre coût/bénéfice pour Annals of Telecom :
1. **Minimum viable** : calibrer `physical_model.py` sur des traces publiques (datasets Colosseum/ColO-RAN, traces OpenRAN Gym) et le documenter — transforme « simulateur maison » en « simulateur calibré sur données réelles ».
2. **Recommandé** : ns-3 + module O-RAN (ns-O-RAN) : 1–2 scénarios (S1 puissance/couverture, S3 énergie/mobilité), 7–21 cellules, ~200 UEs, boucle E2 simulée ; comparer ConsistXApp vs QACM vs uncoordinated sur KPI 3GPP (débit, HOF, ping-pong, RLF, énergie). ~2–3 semaines d'intégration, quelques jours de simulation.
3. **Luxe (optionnel)** : OpenRAN Gym/Colosseum (accès sur demande académique) ou FlexRIC+srsRAN en émulation locale — un seul scénario suffit pour la crédibilité.

### E6 — Renforcement statistique
- Repasser l'ablation réparation avec ≥ 1 000 déclencheurs (générés en E1, strate « près du seuil »).
- Tests de Wilcoxon appariés par instance + Holm–Bonferroni sur chaque famille de comparaisons ; delta de Cliff pour les tailles d'effet ; rapporter N exacts partout (déjà fait — garder).
- Ajouter les intervalles sur TOUTES les valeurs du papier via `aggregate.py` (déjà en place, étendre aux nouvelles campagnes).

### E7 — Robustesse et sensibilité (différenciateur supplémentaire)
- Bruit de contexte : contexte observé ≠ contexte réel (probabilité ε de relation erronée) → mesurer la dégradation de la garantie (elle devient conditionnelle au modèle — l'assumer explicitement, cf. Protocole §0).
- xApp adversariale/byzantine : propositions volontairement conflictuelles à haute fréquence → le pipeline reste-t-il dans le budget ? le fallback est-il toujours sûr ?
- Sensibilité hyperparamètres du repair (rayon initial, politique d'expansion, time-limits CP-SAT).

### Ordre d'exécution conseillé
1. **E1 pilote** (1 strate, n ∈ {100, 500, 1000}, 5 seeds) → vérifier que le point de rupture existe. *Décision go/no-go de l'Option A.*
2. E4 (indépendant, faible coût, peut tourner en parallèle).
3. E1 complet gelé + E2 + E6.
4. E3, puis E5 (le plus long).
5. Geler → réécrire le manuscrit.

---

## 5. Révision du manuscrit (après les campagnes)

1. **Titre** : retirer « Fractional-Stall Diagnosis » du titre ; proposer p.ex. *« Budget-Constrained xApp Coordination in the Near-RT RIC: Incremental Consistency, Explanation-Guided Local Repair, and Independent Verification »*.
2. **Abstract/intro** : mener avec le point de rupture d'échelle (résultat E1), pas avec l'architecture.
3. **Section 5 (théorie)** : conserver soundness du filtrage + complétude conditionnelle du repair ; ajouter une borne sur la taille du cœur en fonction de la localité du changement (résultat probablement démontrable et aligné avec E2) ; réduire l'analyse des stalls fractionnaires à la motivation du repair.
4. **Étage continu** : le sortir du pipeline principal ; une sous-section honnête « Why not continuous relaxation? » avec vos chiffres actuels est en fait une force (negative result documenté).
5. **Related work** : intégrer QACM, CMF, COMIX, XAI4C, GNN conflict-graph learning, PACIFISTA et l'article TNSM 2026 AI-native — et positionner : *seule approche à garanties formelles + explications + vérification indépendante*.
6. **Reproductibilité** : Dockerfile + archive Zenodo (code + manifests + raw CSV) + badge « artifacts available ». Annals of Telecom y est sensible.
7. **Formulation des garanties** : garder strictement la formule du Protocole §0 (« sound relative to the registered model; no false positive observed ») — jamais « 100 % validé ».

## 6. Sur la « validation à 100 % »

Votre propre `Protocole.md` (§0) le dit correctement : aucune campagne empirique ne prouve une correction universelle. Ce qui est atteignable et défendable :
- **Correction logique conditionnelle** au modèle enregistré (preuves de la Section 5 + vérificateur) ;
- **Zéro faux positif observé** sur oracle exhaustif + 100 k property-tests + mutations (E4) ;
- **Utilité télécom** démontrée en boucle fermée (E5).
C'est exactement le trio que le plan ci-dessus opérationnalise — et c'est plus fort que tout ce qui existe dans la littérature xApp-conflict actuelle, où aucune méthode ne fournit vérification indépendante ni explications prouvées.

---

## 7. Récapitulatif des actions

| # | Action | Effort | Impact |
|---|---|---|---|
| 1 | E1 pilote : existence du point de rupture | 1 j | Go/no-go |
| 2 | E4 : validation G1–G4 du vérificateur | 2–3 j | Section « Trust » unique |
| 3 | E1 complet + E2 (warm-start CP-SAT inclus) | 1 sem calcul | Cœur des résultats |
| 4 | E3 : baselines QACM/CMF/jeux/COMIX | 3–5 j | Crédibilité comparaison |
| 5 | E6 : stats appariées + ablation ≥1000 cas | 1–2 j | Anti-rejet statistique |
| 6 | E5 : ns-3/calibration traces | 2–3 sem | Neutralise « simulation jouet » |
| 7 | E7 : robustesse | 2–3 j | Différenciateur |
| 8 | Réécriture manuscrit (repositionnement) | 1–2 sem | — |
