
# Protocole expérimental complet — MIRAGE-R pour la coordination des xApps O-RAN

## 0. Principe éthique et limite de la « validation à 100 % »

Aucun protocole empirique ne peut prouver à **100 %** qu’une méthode fonctionnera sur tous les réseaux O-RAN possibles. En revanche, il est possible d’établir rigoureusement trois niveaux de garantie :

1. **Garantie logique conditionnelle**Toute décision annoncée comme faisable est acceptée par un vérificateur indépendant relativement au modèle formel enregistré.
2. **Validation empirique sans faux positif observé**Zéro décision invalide acceptée sur l’intégralité des campagnes, tests exhaustifs, tests différentiels et tests par mutation.
3. **Validation télécom**
   Les décisions formellement valides améliorent effectivement les KPI mesurés dans un simulateur, un émulateur ou un testbed O-RAN.

La formulation scientifiquement défendable sera donc :

> “The proposed solve-and-verify architecture is sound relative to the registered finite-domain conflict model. Across the complete evaluation campaign, no false positive was observed.”

Il ne faudra pas écrire :

> “The method is universally 100% sound for every physical O-RAN deployment.”

---

# 1. Objectifs scientifiques

Le protocole doit valider six affirmations.

## C1 — Correction du pipeline de vérification

Toute décision envoyée au réseau satisfait :

- les domaines des variables ;
- les contraintes directes ;
- les contraintes de capacité ;
- les contraintes de précédence et de sérialisation ;
- les politiques opérateur ;
- les contraintes SLA modélisées.

## C2 — Existence et détection de points fixes fractionnaires

MIRAGE-R peut atteindre des configurations telles que :

\[
\lVert T(p)-p\rVert \leq \delta_\rho,
\qquad
\phi(p)\geq\delta_\phi,
\qquad
V(\operatorname{decode}(p))>0.
\]

Le protocole doit démontrer que ces configurations apparaissent dans des scénarios O-RAN réalistes, et pas uniquement dans des CSP artificiels.

## C3 — Efficacité de la réparation exacte locale

L’extraction et la résolution exacte du noyau conflictuel doivent augmenter le taux de décisions vérifiées par rapport à :

- MIRAGE-R seul ;
- MIRAGE-R avec régions dynamiques ;
- l’arrondi simple ;
- une politique de priorité statique.

## C4 — Utilité télécom

Une décision formellement faisable doit produire des performances acceptables sur :

- débit ;
- énergie ;
- latence ;
- équité ;
- taux d’échec des handovers ;
- violations de SLA ;
- oscillations des paramètres.

## C5 — Compatibilité avec le budget de contrôle

La coordination, la réparation et la vérification doivent terminer dans le budget temporel du scénario xApp.

## C6 — Reproductibilité

Toutes les conclusions doivent pouvoir être régénérées à partir :

- des manifests figés ;
- des seeds ;
- des fichiers de configuration ;
- des logs bruts ;
- des scripts d’agrégation ;
- d’une image Docker ou d’un environnement documenté.

---

# 2. Architecture expérimentale

La validation est organisée en trois niveaux complémentaires.

## Niveau A — Validation formelle et exhaustive

Ce niveau teste le modèle CSP et le vérificateur indépendamment du réseau.

Il couvre :

- les petits graphes de conflits ;
- toutes les affectations possibles ;
- les cas SAT et UNSAT ;
- les relations directes, indirectes et contextuelles ;
- les sorties volontairement corrompues.

## Niveau B — Benchmark synthétique de coordination xApps

Ce niveau teste la capacité algorithmique sur des instances O-RAN générées :

- plusieurs xApps ;
- plusieurs cellules ;
- domaines d’actions variables ;
- densités de conflits variables ;
- contraintes de capacité ;
- SLA discrétisés.

Il permet des comparaisons à grande échelle avec CP-SAT.

## Niveau C — Validation télécom en boucle fermée

Ce niveau connecte le coordonnateur à un environnement RAN :

- ns-3 avec extension O-RAN ;
- OpenRAN Gym/ColO-RAN ;
- FlexRIC avec srsRAN/OpenAirInterface ;
- ou une combinaison simulation + émulation.

La documentation srsRAN fournit actuellement un exemple d’interopérabilité entre le gNB, l’interface E2 et un Near-RT RIC tiers : [srsRAN NearRT-RIC and xApp](https://docs.srsran.com/projects/project/en/latest/tutorials/source/near-rt-ric/source/index.html). OpenRAN Gym fournit également une infrastructure expérimentale ouverte pour les xApps et la collecte de données.

Pour *Annals of Telecommunications*, la meilleure combinaison serait :

- **simulation reproductible comme évaluation principale** ;
- **émulation O-RAN sur un sous-ensemble représentatif** ;
- testbed radio matériel seulement si disponible.

---

# 3. Réorganisation recommandée du dépôt

Créer une branche séparée :

```text
oran-conflict
```

et ajouter la structure suivante :

```text
MIRAGE-R/
├── src/
│   ├── mirage_solver.py
│   ├── csp_core.py
│   ├── local_projectors.py
│   ├── annealing.py
│   ├── adaptive_regions.py
│   ├── hybrid.py
│   ├── verifier.py
│   │
│   └── oran/
│       ├── action_model.py
│       ├── context_model.py
│       ├── conflict_model.py
│       ├── direct_conflicts.py
│       ├── indirect_conflicts.py
│       ├── implicit_conflicts.py
│       ├── conflict_graph.py
│       ├── oran_to_csp.py
│       ├── exact_local_repair.py
│       ├── safe_fallback.py
│       ├── oran_verifier.py
│       └── log_schema.py
│
├── experiments/
│   └── oran_validation/
│       ├── manifests/
│       ├── configs/
│       ├── generators/
│       ├── adapters/
│       ├── sanity/
│       ├── exhaustive/
│       ├── synthetic/
│       ├── closed_loop/
│       ├── ablations/
│       ├── statistics/
│       └── aggregation/
│
├── baselines/
│   └── oran/
│       ├── uncoordinated/
│       ├── static_priority/
│       ├── random_feasible/
│       ├── cpsat_full/
│       ├── cpsat_local_repair/
│       └── qacm_like/
│
├── results/
│   └── oran/
│       ├── raw/
│       ├── aggregated/
│       ├── figures/
│       ├── tables/
│       └── integrity/
│
├── data/
│   └── oran/
│       ├── normalized/
│       ├── traces/
│       ├── scenarios/
│       └── checksums/
│
└── paper/
    └── annals_oran/
        ├── main.tex
        ├── references.bib
        ├── numbers.tex
        ├── figures/
        └── tables/
```

Le projet IJOC doit rester intact. La branche O-RAN doit réutiliser le cœur de MIRAGE-R sans modifier rétroactivement les résultats XCSP3.

---

# 4. Modèle expérimental des xApps

## 4.1 Variable de décision

Pour chaque xApp \(i\), cellule \(b\) et époque \(t\), on définit :

\[
x_{i,b,t}\in D_{i,b,t}.
\]

Une valeur peut représenter :

- accepter la recommandation ;
- rejeter la recommandation ;
- appliquer un no-op ;
- choisir un niveau de puissance ;
- activer ou désactiver une cellule ;
- choisir un offset de handover ;
- choisir un profil de ressources radio ;
- différer l’exécution à un autre créneau.

Chaque domaine doit toujours contenir une action sûre :

\[
a^{\mathrm{safe}}_{i,b,t}\in D_{i,b,t}.
\]

## 4.2 Séparation hard/soft

Les contraintes doivent être classées avant les expériences.

### Contraintes dures

- une seule valeur par paramètre ;
- limites physiques ;
- valeurs autorisées ;
- capacité maximale ;
- incompatibilités directes ;
- règles opérateur ;
- actions interdites ;
- précédences impératives ;
- couverture minimale formalisée.

### Contraintes souples

- préférence de débit ;
- préférence énergétique ;
- équité ;
- limitation des changements ;
- objectifs propres aux xApps ;
- SLA tolérant une pénalité.

Une contrainte souple ne doit jamais être utilisée pour soutenir une affirmation de « soundness ».

---

# 5. Scénarios O-RAN

Le benchmark doit contenir au moins cinq familles.

## S1 — Conflit direct de puissance

### xApps

- Coverage xApp ;
- Energy-Saving xApp.

### Actions

\[
D_}
===

\{P_1,\ldots,P_q\}.
\]

L’Energy-Saving xApp demande une réduction de puissance tandis que le Coverage xApp demande une augmentation.

### Contraintes

- un seul niveau final par cellule ;
- puissance minimale et maximale ;
- couverture minimale ;
- budget énergétique.

### KPI

- puissance consommée ;
- SINR ;
- utilisateurs couverts ;
- débit ;
- violations de couverture.

---

## S2 — Conflit puissance–allocation RBG

### xApps

- Power-Control xApp ;
- Resource-Allocation xApp.

### Actions

- niveau discret de puissance ;
- profil d’affectation des RBG ;
- priorité de service.

### Type de conflit

Indirect : les xApps contrôlent des paramètres différents mais influencent :

- débit ;
- interférence ;
- perte de paquets ;
- équité.

### KPI

- débit global ;
- cinquième percentile du débit ;
- interférence ;
- Jain fairness ;
- taux de SLA satisfaits.

---

## S3 — Conflit Energy Saving–Mobility Robustness

### xApps

- Energy-Saving xApp ;
- Mobility-Robustness xApp.

### Actions

- sleep/wake ;
- handover margin ;
- cell individual offset ;
- time-to-trigger discret.

### Risque

Une cellule mise en veille peut provoquer :

- handover tardif ;
- radio-link failure ;
- surcharge des cellules voisines ;
- ping-pong ;
- perte de couverture.

### KPI

- consommation énergétique ;
- handover failure rate ;
- ping-pong rate ;
- radio-link failures ;
- utilisateurs non servis.

---

## S4 — Conflit Load Balancing–Mobility Optimization

### xApps

- Load-Balancing xApp ;
- Mobility xApp.

### Actions

- offsets de cellules ;
- seuils de handover ;
- association préférée ;
- politiques de steering.

### KPI

- variance de charge ;
- débit en bordure ;
- handovers ;
- temps d’indisponibilité ;
- équité intercellulaire.

---

## S5 — Stress test multi-xApps

Combiner :

- énergie ;
- mobilité ;
- puissance ;
- load balancing ;
- allocation de ressources ;
- admission de services.

Faire varier :

\[
|\mathcal{A}|\in\{2,4,6,8,12\}.
\]

Ce scénario sert principalement à mesurer :

- passage à l’échelle ;
- densité de conflits ;
- taille des noyaux de réparation ;
- latence ;
- mémoire.

---

# 6. Validation exhaustive du vérificateur

## 6.1 Petites instances exhaustives

Pour chaque famille, générer des instances avec :

\[
n\in\{2,3,4,5,6,7,8\},
\qquad
d\in\{2,3,4\}.
\]

Pour chaque instance admissible, énumérer toutes les affectations :

\[
\mathcal
========

\prod_{i=1}^{n}D_i.
\]

L’oracle exhaustif calcule exactement :

\[
\mathcal
========

\left\{
x\in\mathcal{X}:
x_{S_c}\in R_c,\ \forall c
\right\}.
\]

Pour chaque affectation \(x\) :

```text
expected = (x in F)
observed = oran_verifier.verify(x)
assert expected == observed
```

### Critère de passage G1

\[
\boxed{\text{0 divergence sur 100 \% des affectations énumérées}}
\]

Une seule divergence bloque la campagne principale.

---

## 6.2 Double vérification indépendante

Implémenter deux vérificateurs sans code partagé :

1. vérificateur Python ;
2. vérificateur indépendant Java ou modèle CP-SAT déclaratif.

Les deux doivent consommer le même JSON normalisé mais avoir :

- des parseurs distincts ;
- des évaluateurs distincts ;
- aucun appel au solveur MIRAGE-R ;
- aucune réutilisation de `local_projectors.py`.

### Critère G2

Pour toutes les petites instances :

\[
V_}(x)
======

V_}(x)
======

V_{\mathrm{oracle}}(x).
\]

---

## 6.3 Property-based testing

Générer au moins :

\[
100\,000
\]

triplets aléatoires :

\[
(\text{instance},\text{contexte},\text{affectation}).
\]

Propriétés à vérifier :

- déterminisme ;
- invariance au renommage des variables ;
- invariance à la permutation des contraintes ;
- invariance à l’ordre des tuples ;
- rejet des valeurs hors domaine ;
- rejet des variables manquantes ;
- rejet des variables dupliquées ;
- rejet des contextes incompatibles ;
- cohérence Python/Java/CP-SAT.

### Critère G3

- zéro divergence ;
- zéro crash non classifié ;
- toute entrée invalide doit échouer explicitement.

---

## 6.4 Mutation testing

À partir d’une solution faisable, appliquer :

- modification d’une valeur ;
- suppression d’une action ;
- duplication d’un paramètre ;
- dépassement de capacité ;
- activation d’une cellule interdite ;
- collision temporelle ;
- violation volontaire d’une politique ;
- corruption du contexte ;
- modification d’un identifiant.

Attention : une mutation peut conserver la faisabilité. Elle ne doit être considérée comme invalide qu’après vérification par l’oracle exhaustif.

### Critère G4

Pour toutes les mutations prouvées invalides :

\[
\boxed{\text{taux de rejet}=100\%}
\]

---

# 7. Benchmark synthétique O-RAN

## 7.1 Taille du benchmark

Créer un manifest figé de :

\[
5\text
\times
4\text
\times
30\text
=======

600\text{ instances}.
\]

### Échelles proposées

| Échelle | xApps | Cellules |  Variables |   Contraintes |
| -------- | ----: | -------: | ---------: | ------------: |
| Small    |  2–3 |     1–3 |      5–20 |         5–40 |
| Medium   |  4–6 |     3–7 |    21–100 |       41–300 |
| Large    | 6–10 |    7–21 |   101–500 |    301–2 000 |
| Stress   | 8–12 |   21–50 | 501–2 000 | 2 001–20 000 |

Les valeurs finales seront celles réellement générées et devront être enregistrées dans le manifest.

## 7.2 Facteurs structurels

Stratifier les instances selon :

### Taille maximale du domaine

\[
d_{\max}\in
\{2,\ 3\text{--}4,\ 5\text{--}8,\ >8\}.
\]

### Densité de contraintes

\[
\frac{|\mathcal C|}{|\mathcal X|}
\in
\{<1,\ 1\text{--}2,\ 2\text{--}4,\ >4\}.
\]

### Densité du graphe de conflits

\[
\delta_G
========

\frac{2|E|}
{|V|(|V|-1)}.
\]

Classes :

- faible ;
- moyenne ;
- élevée.

### Arity maximale

\[
a_{\max}
\in
\{2,\ 3\text{--}4,\ 5\text{--}8,\ >8\}.
\]

### Proportion de conflits

- direct uniquement ;
- direct + indirect ;
- mixte ;
- majorité implicite.

---

# 8. Séparation calibration–test

Les données doivent être divisées avant toute optimisation des paramètres.

| Ensemble    | Proportion | Usage                       |
| ----------- | ---------: | --------------------------- |
| Development |       20 % | débogage et développement |
| Validation  |       20 % | choix des hyperparamètres  |
| Test figé  |       60 % | résultats du papier        |

Les seeds doivent être disjointes.

Le test figé ne doit être lancé qu’après :

- gel de l’algorithme ;
- gel des paramètres ;
- gel du manifest ;
- gel des métriques ;
- gel des hypothèses statistiques.

Toute modification ultérieure crée une nouvelle version complète du protocole.

---

# 9. Méthodes comparées

## B0 — No-conflict upper reference

Exécuter chaque xApp seul. Ce n’est pas une méthode de résolution, mais une référence permettant de mesurer les pertes dues aux interactions.

## B1 — Uncoordinated/last-writer-wins

Les xApps agissent sans coordonnateur.

En cas d’écriture concurrente, la dernière requête reçue l’emporte.

## B2 — Static priority

Ordre de priorité fixe :

\[
\text{safety}

\text{coverage}

\text{mobility}

\text{SLA}

\text{energy}.
\]

Cet ordre doit être déclaré avant les expériences.

## B3 — Random feasible

Échantillonnage aléatoire jusqu’à :

- obtention d’une décision faisable ;
- ou expiration du budget.

## B4 — CP-SAT complet

Résolution exacte du problème complet avec :

- même modèle ;
- même temps limite ;
- même nombre de threads ;
- même vérificateur externe.

CP-SAT peut retourner :

- OPTIMAL ;
- FEASIBLE ;
- INFEASIBLE ;
- UNKNOWN.

Seuls OPTIMAL et FEASIBLE avec témoin vérifié comptent comme décisions valides.

## B5 — MIRAGE-R core

MIRAGE-R sans régions ni réparation.

## B6 — MIRAGE-R + régions

Version actuelle avec `adaptive_regions.py`.

Cette variante est importante, car elle permet de vérifier si le faible effet des régions observé sur XCSP3 se retrouve dans les conflits O-RAN.

## B7 — MIRAGE-R + exact local repair

Méthode principale :

1. relaxation continue ;
2. détection de stall ;
3. extraction du noyau conflictuel ;
4. CP-SAT local ;
5. vérification indépendante ;
6. fallback sûr en cas d’échec.

## B8 — QoS-aware baseline

Implémenter, si possible, une baseline inspirée de QACM :

\[
\max
\sum_i
\mathbf[\text_i\text]
---------------------

\lambda \,\text{cost}(x).
\]

Il n’est pas nécessaire de reproduire mot à mot le logiciel original si celui-ci n’est pas disponible. Dans ce cas, la méthode doit être appelée :

> “QACM-inspired QoS-aware optimization baseline”

et non « QACM ».

---

# 10. Budgets temporels

Il ne faut pas utiliser un budget unique pour tous les xApps.

Définir trois classes.

| Classe | Boucle de contrôle | Budget expérimental |
| ------ | ------------------: | -------------------: |
| Fast   |          10–100 ms |          20 ou 50 ms |
| Medium |         100–500 ms |        100 ou 250 ms |
| Slow   |       500–1 000 ms |               500 ms |

Le budget doit inclure :

\[
t_}
===

t_{\mathrm{parse}}
+
t_{\mathrm{MIRAGE}}
+
t_{\mathrm{repair}}
+
t_{\mathrm{verify}}.
\]

Le temps de génération hors ligne du modèle peut être mesuré séparément, mais il ne doit pas être mélangé avec la latence de décision en ligne.

---

# 11. Critères de détection des stalls

Utiliser simultanément trois indicateurs.

## Résidu du point fixe

\[
\rho_t
======

\max_i
\lVert p_i^{t+1}-p_i^t\rVert_1.
\]

## Fractionalité

\[
\phi_t
======

\frac{1}{n}
\sum_i
\left(
1-\max_a p_i^t(a)
\right).
\]

## Violations après décodage

\[
V_t
===

\sum_c
\mathbf 1
\left[
\widehat{x}_{S_c}^t\notin R_c
\right].
\]

Un stall opérationnel est déclaré si :

\[
\rho_t\leq 10^{-6},
\qquad
\phi_t\geq 10^{-2},
\qquad
V_t>0
\]

pendant au moins trois contrôles consécutifs.

Ces seuils doivent être confirmés sur l’ensemble de validation, puis figés.

Il faudra comparer ce détecteur à :

- plateau des violations seulement ;
- résidu seulement ;
- fractionalité seulement.

---

# 12. Extraction du noyau conflictuel

## 12.1 Noyau initial

\[
\mathcal C^0
============

\left\{
c:
\widehat{x}_{S_c}\notin R_c
\right\}.
\]

\[
\mathcal X^0
============

\bigcup_{c\in\mathcal C^0}S_c.
\]

## 12.2 Expansion

Tester :

\[
h\in\{0,1,2,3\}
\]

hops dans le graphe de conflits.

## 12.3 Objectif lexicographique

Le solveur local optimise :

1. satisfaction de toutes les contraintes dures ;
2. nombre minimal de changements ;
3. satisfaction maximale des SLA ;
4. utilité télécom maximale ;
5. énergie minimale.

Formellement :

\[
\min
\left(
V_{\mathrm{hard}},
\Delta(\widehat x,x),
-V_{\mathrm{SLA}},
-U(x),
E(x)
\right).
\]

## 12.4 Fallback sûr

Si aucune réparation n’est trouvée dans le budget :

- conserver la dernière configuration vérifiée ;
- rejeter les nouvelles actions conflictuelles ;
- éventuellement appliquer un no-op.

Le fallback ne doit jamais être enregistré comme une réparation réussie.

---

# 13. Protocole closed-loop O-RAN

## 13.1 Topologies

Trois topologies :

| Topologie | Cellules |      UE |
| --------- | -------: | ------: |
| T1        |     1–3 |      10 |
| T2        |        7 |  30–42 |
| T3        |   19–21 | 60–100 |

## 13.2 Charges

\[
L\in\{0.3,\ 0.6,\ 0.9\}
\]

où \(L\) est la charge offerte normalisée.

## 13.3 Mobilité

- statique ;
- piéton : environ \(1\)–\(2\ \mathrm{m/s}\) ;
- véhiculaire modérée : environ \(10\)–\(15\ \mathrm{m/s}\).

Les valeurs exactes doivent dépendre du scénario et être documentées.

## 13.4 Durée

Pour chaque réplication :

- warm-up : 60 s ;
- mesure : 300 s ;
- cooldown éventuel : 30 s.

Les métriques du warm-up sont exclues.

## 13.5 Réplications

Au minimum :

\[
30\text{ seeds par configuration principale}.
\]

Si le coût est trop élevé, réaliser une analyse de puissance sur un pilote et justifier un minimum inférieur. L’unité statistique doit être la **réplication réseau complète**, pas chaque époque de contrôle, car les époques successives sont corrélées.

## 13.6 Plan factoriel raisonnable

Pour éviter une explosion combinatoire, sélectionner :

- 5 scénarios ;
- 3 charges ;
- 2 niveaux de mobilité pertinents ;
- 3 densités de conflits ;
- 30 seeds.

Cela donne :

\[
5\times3\times2\times3\times30
==============================

2700
\]

réplications par méthode.

Pour 6 méthodes principales :

\[
16\,200
\]

exécutions closed-loop.

Les analyses de sensibilité supplémentaires peuvent utiliser 10 seeds, mais elles ne doivent pas remplacer les 30 seeds du protocole principal.

---

# 14. Métriques principales

## 14.1 Primary endpoint

### Verified conflict-free decision rate

\[
\mathrm
=======

\frac{
N_{\mathrm{accepted\ by\ verifier}}
}{
N_{\mathrm{decision\ epochs}}
}.
\]

Une décision fallback peut être comptée comme faisable mais doit être distinguée d’une décision nouvellement coordonnée.

Rapporter séparément :

- décision proposée acceptée ;
- décision réparée acceptée ;
- fallback ;
- timeout ;
- décision rejetée ;
- erreur.

---

## 14.2 False-positive rate

\[
\mathrm
=======

\frac{
N_{\mathrm{invalid\ accepted}}
}{
N_{\mathrm{accepted}}
}.
\]

Critère impératif :

\[
\boxed{\mathrm{FPR}=0}
\]

sur toutes les campagnes.

L’intervalle supérieur doit néanmoins être rapporté. Si zéro faux positif est observé sur \(

\(N\) décisions acceptées, la « règle de trois » donne approximativement une borne supérieure à 95 % :

\[
\mathrm{FPR}_{95\%,\mathrm{upper}}
\approx
\frac{3}{N}.
\]

Par exemple, zéro faux positif sur \(100\,000\) décisions donne une borne supérieure approximative de :

\[
3\times10^{-5}.
\]

Il faut donc rapporter simultanément :

- le nombre de faux positifs observés ;
- le nombre total de décisions acceptées ;
- l’intervalle de confiance binomial exact ;
- la garantie conditionnelle apportée par le vérificateur.

---

## 14.3 SAT-witness recall

Sur les instances dont CP-SAT ou l’énumération établit la faisabilité :

\[
\mathrm_}
=========

\frac{
N_{\mathrm{witnesses\ vérifiés}}
}{
N_{\mathrm{instances\ faisables}}
}.
\]

Cette métrique est plus honnête que la simple couverture globale, car MIRAGE-R-CM ne doit pas déclarer `UNSAT` sans certificat exact.

Les statuts autorisés sont :

- `VERIFIED_FEASIBLE` ;
- `FALLBACK_FEASIBLE` ;
- `INFEASIBLE_CERTIFIED` — uniquement si CP-SAT ou l’énumération le prouve ;
- `UNKNOWN` ;
- `TIMEOUT` ;
- `ADAPTER_ERROR` ;
- `VERIFIER_REJECT`.

---

## 14.4 Repair success rate

\[
\mathrm
=======

\frac{
N_{\mathrm{réparations\ vérifiées}}
}{
N_{\mathrm{tentatives\ de\ réparation}}
}.
\]

Rapporter séparément :

- réparation trouvée ;
- noyau local déclaré infaisable ;
- timeout ;
- erreur ;
- réparation proposée mais rejetée ;
- fallback.

---

## 14.5 Gain de la réparation

La métrique principale comparant la méthode complète au cœur continu est :

\[
\Delta_}
========

\mathrm_R\textCM}}
------------------

\mathrm{VCF}_{\mathrm{MIRAGE\text{-}R\text{-}Core}}.
\]

L’article ne pourra revendiquer une amélioration que si :

1. la différence est positive ;
2. son intervalle de confiance à 95 % exclut zéro ;
3. l’effet est observé sur le jeu test figé ;
4. l’augmentation ne provient pas uniquement du fallback.

Il faut également calculer :

\[
\Delta_}
========

P(\text)
--------

P(\text{fallback}).
\]

Cela évite de présenter la conservation de l’état précédent comme une résolution réussie.

---

# 15. Métriques de qualité de la solution

## 15.1 Écart à l’optimum

Quand CP-SAT retourne `OPTIMAL` :

\[
\mathrm(x)
==========

\frac{
U^\star-U(x)
}{
\max\{|U^\star|,\varepsilon\}
}.
\]

Rapporter :

- médiane ;
- moyenne ;
- premier et troisième quartiles ;
- 90e et 95e percentiles ;
- proportion de solutions optimales ;
- proportion de gaps inférieurs à 1 %, 5 % et 10 %.

Ne pas calculer un gap optimal lorsque CP-SAT retourne seulement `FEASIBLE`.

Dans ce cas, utiliser :

\[
\mathrm
=======

\frac{
U_{\mathrm{CP-feasible}}-U_{\mathrm{MIRAGE}}
}{
\max\{|U_{\mathrm{CP-feasible}}|,\varepsilon\}
},
\]

en précisant qu’il ne s’agit pas d’un gap à l’optimum.

---

## 15.2 Satisfaction pondérée des xApps

Soit \(s_i(x)\in\{0,1\}\) l’indicateur de satisfaction de la xApp \(i\). Définir :

\[
\mathrm(x)
==========

\frac{
\sum_i \omega_i s_i(x)
}{
\sum_i\omega_i
}.
\]

Rapporter aussi le taux non pondéré afin de détecter une éventuelle domination des xApps prioritaires.

---

## 15.3 Coût de reconfiguration

Une politique peut être faisable mais provoquer trop de changements. Définir :

\[
C_}(t)
======

\sum_i
\mathbf 1[x_i^t\neq x_i^{t-1}].
\]

La moyenne temporelle est :

\[
\overline C_}
=============

\frac{1}{T-1}
\sum_{t=2}^{T}
C_{\mathrm{switch}}(t).
\]

Rapporter :

- nombre de changements ;
- changements par minute ;
- nombre d’inversions successives ;
- durée moyenne de stabilité.

---

# 16. Métriques télécoms

## 16.1 Débit

Pour chaque réplication :

\[
R_}
===

\sum_{u\in\mathcal U}R_u.
\]

Rapporter :

- débit global ;
- débit moyen par UE ;
- débit médian ;
- cinquième percentile ;
- débit des utilisateurs en bordure de cellule.

---

## 16.2 Équité

Utiliser l’indice de Jain :

\[
J
=

\frac{
\left(\sum_{u\in\mathcal U}R_u\right)^2
}{
|\mathcal U|
\sum_{u\in\mathcal U}R_u^2
}.
\]

L’indice doit être calculé par réplication, puis agrégé. Il ne faut pas agréger les débits de toutes les réplications avant de calculer l’indice.

---

## 16.3 Énergie

Mesurer :

- énergie totale consommée ;
- puissance moyenne ;
- énergie par bit ;
- durée de veille ;
- nombre de transitions sleep/wake ;
- coût énergétique des reconfigurations.

L’énergie par bit est :

\[
E_}
===

\frac{
E_{\mathrm{total}}
}{
B_{\mathrm{delivered}}
}.
\]

Une réduction d’énergie n’est favorable que si elle n’est pas obtenue au prix d’une violation importante des SLA.

---

## 16.4 Mobilité

Mesurer :

\[
\mathrm
=======

\frac{
N_{\mathrm{handover\ failures}}
}{
N_{\mathrm{handover\ attempts}}
}.
\]

Mesurer aussi :

- handover success rate ;
- radio-link failures ;
- ping-pong rate ;
- temps d’interruption ;
- nombre de handovers par UE ;
- handovers tardifs ;
- handovers prématurés.

---

## 16.5 Violations SLA

Pour chaque SLA \(q\) :

\[
\mathrm_q
=========

\frac{
N_{\mathrm{epochs\ violant\ }q}
}{
N_{\mathrm{epochs\ où\ }q\text{ est applicable}}
}.
\]

Calculer également une sévérité :

\[
\mathrm_q
=========

\frac{1}{T}
\sum_{t=1}^{T}
\max\left\{
0,
\frac{
\theta_q-K_q(t)
}{
\max\{|\theta_q|,\varepsilon\}
}
\right\},
\]

pour un KPI devant rester supérieur au seuil \(\theta_q\).

Pour un KPI devant rester inférieur à une borne, inverser le sens de l’écart.

---

# 17. Métriques de latence et ressources

## 17.1 Décomposition de la latence

Mesurer séparément :

\[
t_}
===

t_{\mathrm{parse}}
+
t_{\mathrm{relation}}
+
t_{\mathrm{MIRAGE}}
+
t_{\mathrm{decode}}
+
t_{\mathrm{repair}}
+
t_{\mathrm{verify}}
+
t_{\mathrm{serialization}}.
\]

Sur le testbed, ajouter :

\[
t_{\mathrm{E2}}
\]

et rapporter :

\[
t_}
===

t_{\mathrm{total}}+t_{\mathrm{E2}}.
\]

---

## 17.2 Statistiques temporelles

Pour chaque méthode et scénario :

- médiane ;
- moyenne ;
- écart-type ;
- p90 ;
- p95 ;
- p99 ;
- maximum ;
- proportion de dépassements du deadline.

Le taux de respect du deadline est :

\[
\mathrm
=======

\frac{
N[t_{\mathrm{end-to-end}}\leq D]
}{
N_{\mathrm{decisions}}
}.
\]

---

## 17.3 Mémoire

Mesurer le peak RSS de l’arbre de processus avec une fréquence d’échantillonnage documentée, par exemple 25 ms.

Rapporter :

- peak RSS médian ;
- p95 ;
- maximum ;
- mémoire en fonction de la taille de l’instance ;
- mémoire en fonction du nombre de régions ;
- mémoire de CP-SAT local et global.

Le tuple cap ne constitue pas une borne globale de mémoire. Si des régions sont conservées, il faut aussi journaliser :

\[
N_{\mathrm{regions}},
\qquad
\sum_r |R_r|.
\]

---

# 18. Analyse des points fixes fractionnaires

## 18.1 Journalisation par epoch

Chaque epoch MIRAGE-R doit enregistrer :

```json
{
  "epoch": 135,
  "temperature": 0.35,
  "beta": 3.2,
  "residual_l1_max": 1.2e-7,
  "mean_fractionality": 0.14,
  "mean_entropy_normalized": 0.21,
  "decoded_hard_violations": 2,
  "decoded_soft_violations": 1,
  "best_hard_violations": 2,
  "utility": 0.83,
  "regions_active": 8,
  "regions_added": 0,
  "stall_detected": true
}
```

---

## 18.2 Catégories d’échec

Classer chaque run non résolu dans une catégorie exclusive.

### F1 — Fractional stall

\[
\rho\leq\delta_\rho,
\qquad
\phi\geq\delta_\phi,
\qquad
V>0.
\]

### F2 — Polarized infeasible state

\[
\phi<\delta_\phi,
\qquad
V>0.
\]

Les marges sont presque intégrales, mais correspondent à un sommet infaisable.

### F3 — Non-convergent oscillation

\[
\rho>\delta_\rho
\]

avec alternance persistante des actions ou marges.

### F4 — Deadline before diagnosis

Le budget expire avant qu’une catégorie stable puisse être attribuée.

### F5 — Unsupported or malformed model

Erreur de construction ou fonctionnalité non prise en charge.

### F6 — Repair failure

Le stall est correctement détecté, mais le noyau ne peut être réparé dans le budget.

Cette classification doit être produite automatiquement depuis les logs, puis vérifiée sur un échantillon manuel.

---

## 18.3 Pouvoir prédictif du diagnostic

Construire un modèle diagnostique sur le jeu validation :

\[
Y
=

\mathbf 1[
V(\operatorname{decode}(p))>0
].
\]

Variables explicatives :

\[
\log(\rho+\varepsilon),
\quad
\phi,
\quad
H,
\quad
\log n,
\quad
\delta_G,
\quad
d_{\max},
\quad
\text{charge}.
\]

Évaluer sur le test figé :

- ROC-AUC ;
- PR-AUC ;
- précision ;
- rappel ;
- F1 ;
- calibration ;
- matrice de confusion.

Le seuil du détecteur doit être choisi sur validation, jamais sur test.

---

# 19. Ablations complètes

## A1 — Sans annealing

Fixer :

\[
\tau_t=\tau_0.
\]

## A2 — Sans polarisation

Fixer :

\[
\beta_t=1.
\]

## A3 — Sans clipping

Uniquement en environnement numérique contrôlé. Cette variante peut produire des logarithmes de zéro ; toute erreur doit être enregistrée.

## A4 — Sans régions

Désactiver `adaptive_regions.py`.

## A5 — Régions seules

Activer les régions sans réparation exacte.

## A6 — Réparation sans régions

Utiliser MIRAGE-R-Core puis la réparation locale.

## A7 — Méthode complète

Régions, diagnostic et réparation.

## A8 — Plateau uniquement

Détecteur historique basé sur le nombre de violations.

## A9 — Résidu uniquement

Déclenchement si :

\[
\rho\leq\delta_\rho.
\]

## A10 — Diagnostic complet

Déclenchement si :

\[
\rho\leq\delta_\rho,\quad
\phi\geq\delta_\phi,\quad
V>0.
\]

## A11 — Rayon de réparation

\[
h\in\{0,1,2,3,\text{global}\}.
\]

## A12 — Initialisation

Comparer :

- uniforme ;
- uniforme perturbée ;
- confiance xApp ;
- dernière décision vérifiée ;
- warm-start temporel.

---

# 20. Campagne de robustesse

## 20.1 Bruit sur les KPM

Pour chaque KPI :

\[
\widetilde K
============

K+\epsilon,
\qquad
\epsilon\sim\mathcal N(0,\sigma^2).
\]

Tester :

\[
\sigma
\in
\{0,\ 0.01s_K,\ 0.05s_K,\ 0.10s_K\},
\]

où \(s_K\) est l’échelle empirique du KPI.

---

## 20.2 Retard du contexte

Tester :

\[
\Delta_t
\in
\{0,\ 10,\ 50,\ 100,\ 500\}\text{ ms}.
\]

Une décision doit être rejetée si le contexte dépasse sa durée de validité déclarée.

---

## 20.3 Perte de télémétrie

Tester des taux de perte :

\[
p_{\mathrm{loss}}
\in
\{0,\ 0.01,\ 0.05,\ 0.10\}.
\]

Définir avant les essais le comportement en cas de KPM manquante :

- dernière valeur connue ;
- intervalle conservateur ;
- rejet de la décision ;
- fallback.

---

## 20.4 Erreur du modèle d’impact

Introduire une différence entre :

- le modèle utilisé pour construire les relations ;
- le simulateur utilisé pour mesurer les KPI.

Cette expérience évalue le risque de modèle.

Elle est fondamentale pour les conflits implicites.

---

## 20.5 Crash d’une xApp

Pendant une réplication :

- interrompre une xApp ;
- supprimer ses nouvelles propositions ;
- conserver ou expirer ses anciennes actions ;
- vérifier que le coordonnateur ne crash pas ;
- vérifier que le fallback reste admissible.

---

## 20.6 RIC overload

Injecter des lots de requêtes simultanées et mesurer :

- file d’attente ;
- temps d’attente ;
- décisions expirées ;
- deadline misses ;
- utilisation CPU ;
- stabilité.

---

# 21. Protocole statistique

## 21.1 Unité expérimentale

L’unité primaire est :

> une réplication complète définie par une topologie, une trace de trafic, une trace de mobilité et une graine.

Les epochs d’une même réplication sont corrélés. Ils ne doivent pas être traités comme des observations indépendantes dans les tests principaux.

---

## 21.2 Appariement

Pour chaque bloc expérimental \(b\), toutes les méthodes reçoivent exactement :

\[
(\text{topologie}_b,
\text{trafic}_b,
\text{mobilité}_b,
\text{contexte initial}_b,
\text{actions candidates}_b).
\]

L’effet apparié entre deux méthodes \(A\) et \(B\) est :

\[
d_b
===

M_{A,b}-M_{B,b}.
\]

Les intervalles de confiance sont calculés sur la distribution des \(d_b\).

---

## 21.3 Métriques binaires

Pour la faisabilité vérifiée :

- différence appariée de proportions ;
- bootstrap clusterisé par réplication ;
- test de McNemar lorsque chaque réplication donne un résultat binaire unique.

Pour des décisions répétées dans une trace :

- agrégation par trace ;
- ou modèle logistique avec effet aléatoire de trace.

---

## 21.4 Métriques continues

Pour débit, énergie, latence et utilité :

- médiane par trace ;
- différence appariée ;
- bootstrap à 95 % ;
- test de permutation apparié ;
- taille d’effet.

Le test de Wilcoxon peut être utilisé, mais il faut rapporter :

- traitement des égalités ;
- nombre de différences nulles ;
- effectif réel ;
- méthode de calcul de la p-value.

---

## 21.5 Comparaisons multiples

Définir quatre familles :

1. faisabilité ;
2. KPI radio ;
3. latence et mémoire ;
4. ablations.

Appliquer Holm séparément dans chaque famille.

Rapporter :

- p-value brute ;
- p-value corrigée ;
- intervalle de confiance ;
- taille d’effet ;
- effectif.

---

## 21.6 Analyse de puissance

Avant la campagne finale :

1. exécuter un pilote sur 10 seeds ;
2. estimer la variance inter-traces ;
3. choisir l’effet minimal pertinent ;
4. calculer le nombre de réplications requis ;
5. fixer l’effectif avant ouverture du test.

À défaut, conserver 30 seeds comme minimum, mais ne pas prétendre qu’il s’agit automatiquement d’un effectif optimal.

---

# 22. Intégrité des données

## 22.1 Identifiant canonique

Chaque run doit posséder un identifiant construit à partir de :

\[
\texttt{scenario/topology/load/mobility/instance/seed/method}.
\]

Exemple :

```text
S3/T2/L90/VEH/instance_0042/seed_0017/mirage_cm
```

Ne jamais agréger uniquement sur le nom court de l’instance.

---

## 22.2 Manifest figé

Le manifest doit contenir :

```json
{
  "protocol_version": "1.0.0",
  "campaign": "oran_main",
  "frozen_at": "YYYY-MM-DD",
  "git_commit": "...",
  "instances": [
    {
      "instance_id": "...",
      "scenario": "S3",
      "topology": "T2",
      "seed": 17,
      "sha256": "...",
      "expected_methods": [
        "static_priority",
        "cpsat",
        "mirage_core",
        "mirage_regions",
        "mirage_cm"
      ]
    }
  ]
}
```

---

## 22.3 Vérification d’alignement

Avant agrégation :

```text
For every instance:
    expected methods == observed methods
    expected seeds   == observed seeds
    trace hash       identical across methods
    context hash     identical at initial state
```

Une méthode manquante ne doit pas être remplacée par zéro.

Elle doit produire un statut explicite :

- `MISSING_RUN` ;
- `PREPROCESSING_ERROR` ;
- `ADAPTER_ERROR`.

---

## 22.4 Interdiction des modifications manuelles

Les fichiers suivants doivent être générés automatiquement :

```text
paper/annals_oran/numbers.tex
paper/annals_oran/tables/*.tex
paper/annals_oran/figures/*.pdf
```

Le LaTeX doit utiliser des macros :

```latex
\newcommand{\MainVerifiedRate}{...}
\newcommand{\ObservedFalsePositives}{...}
\newcommand{\MedianRepairCore}{...}
```

Aucun résultat numérique principal ne doit être saisi directement dans le texte.

---

# 23. Schéma de log JSONL

Chaque run produit un enregistrement de synthèse :

```json
{
  "schema_version": "1.0.0",
  "run_id": "S3/T2/L90/VEH/i0042/s0017/mirage_cm",
  "instance_id": "i0042",
  "trace_id": "trace_...",
  "scenario": "S3",
  "method": "mirage_cm",
  "seed": 17,

  "num_cells": 7,
  "num_ues": 42,
  "num_xapps": 5,
  "num_variables": 73,
  "num_constraints": 214,
  "max_domain": 8,
  "max_arity": 4,
  "conflict_density": 0.16,

  "status": "VERIFIED_FEASIBLE",
  "solver_claimed_feasible": true,
  "verifier_accepted": true,
  "false_positive": false,

  "stall_detected": true,
  "stall_type": "FRACTIONAL",
  "final_residual": 1.4e-7,
  "final_fractionality": 0.12,
  "final_entropy": 0.18,
  "decoded_violations_before_repair": 2,

  "repair_triggered": true,
  "repair_status": "SUCCESS",
  "repair_radius": 1,
  "repair_variables": 6,
  "repair_constraints": 11,

  "parse_time_ms": 1.2,
  "relation_time_ms": 3.1,
  "mirage_time_ms": 37.4,
  "repair_time_ms": 18.7,
  "verify_time_ms": 0.9,
  "end_to_end_time_ms": 64.3,

  "utility": 0.91,
  "throughput_mbps": 182.6,
  "throughput_p05_mbps": 1.9,
  "jain_index": 0.86,
  "energy_joule": 314.1,
  "handover_attempts": 27,
  "handover_failures": 1,
  "ping_pongs": 2,
  "sla_violations": 0,

  "instance_sha256": "...",
  "trace_sha256": "...",
  "git_commit": "...",
  "container_digest": "..."
}
```

Les trajectoires d’epochs doivent être placées dans un fichier séparé afin de ne pas dupliquer les métadonnées.

---

# 24. Scripts à implémenter

```text
experiments/oran_validation/
├── run_sanity.py
├── run_exhaustive.py
├── run_synthetic_sweep.py
├── run_closed_loop.py
├── run_testbed.py
├── run_ablation.py
├── run_robustness.py
├── run_latency.py
├── run_memory.py
│
├── audit/
│   ├── validate_json_schema.py
│   ├── verify_manifest.py
│   ├── verify_alignment.py
│   ├── replay_witnesses.py
│   ├── compare_verifiers.py
│   ├── compare_exhaustive_cpsat.py
│   └── audit_false_positives.py
│
└── aggregation/
    ├── aggregate_primary.py
    ├── aggregate_stalls.py
    ├── aggregate_repair.py
    ├── aggregate_kpis.py
    ├── aggregate_latency.py
    ├── aggregate_robustness.py
    ├── statistical_tests.py
    ├── generate_numbers_tex.py
    ├── generate_tables.py
    └── generate_figures.py
```

---

# 25. Ordre d’exécution obligatoire

## Étape 1 — Tests unitaires

```bash
pytest -q tests/
pytest -q tests/oran/
```

## Étape 2 — Vérification exhaustive

```bash
python experiments/oran_validation/run_exhaustive.py \
  --config experiments/oran_validation/configs/exhaustive.yaml
```

## Étape 3 — Sanity gate

```bash
python experiments/oran_validation/run_sanity.py \
  --fail-fast
```

## Étape 4 — Validation du manifest

```bash
python experiments/oran_validation/audit/verify_manifest.py \
  data/oran/manifests/main_campaign.json
```

## Étape 5 — Campagne synthétique

```bash
python experiments/oran_validation/run_synthetic_sweep.py \
  --manifest data/oran/manifests/synthetic_test.json \
  --output results/oran/raw/synthetic/
```

## Étape 6 — Campagne closed-loop

```bash
python experiments/oran_validation/run_closed_loop.py \
  --manifest data/oran/manifests/closed_loop_test.json \
  --output results/oran/raw/closed_loop/
```

## Étape 7 — Ablations

```bash
python experiments/oran_validation/run_ablation.py \
  --manifest data/oran/manifests/ablation.json
```

## Étape 8 — Robustesse

```bash
python experiments/oran_validation/run_robustness.py \
  --manifest data/oran/manifests/robustness.json
```

## Étape 9 — Audit complet

```bash
python experiments/oran_validation/audit/validate_json_schema.py
python experiments/oran_validation/audit/verify_alignment.py
python experiments/oran_validation/audit/replay_witnesses.py
python experiments/oran_validation/audit/compare_verifiers.py
python experiments/oran_validation/audit/audit_false_positives.py
```

## Étape 10 — Agrégation

```bash
python experiments/oran_validation/aggregation/aggregate_primary.py
python experiments/oran_validation/aggregation/aggregate_stalls.py
python experiments/oran_validation/aggregation/aggregate_repair.py
python experiments/oran_validation/aggregation/aggregate_kpis.py
python experiments/oran_validation/aggregation/aggregate_latency.py
python experiments/oran_validation/aggregation/statistical_tests.py
python experiments/oran_validation/aggregation/generate_numbers_tex.py
python experiments/oran_validation/aggregation/generate_tables.py
python experiments/oran_validation/aggregation/generate_figures.py
```

## Étape 11 — Compilation

```bash
cd paper/annals_oran
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

La compilation doit terminer avec :

- zéro erreur ;
- zéro citation indéfinie ;
- zéro référence indéfinie ;
- zéro macro `TODO` ;
- zéro valeur manquante.

---

# 26. Conditions d’arrêt automatique

La campagne doit être interrompue immédiatement si :

1. un witness annoncé faisable est rejeté ;
2. les deux vérificateurs divergent ;
3. CP-SAT et l’énumération exhaustive divergent ;
4. un checksum d’instance change ;
5. deux méthodes n’utilisent pas la même trace ;
6. un run ID est dupliqué ;
7. un statut inconnu est rencontré ;
8. une erreur adaptateur est convertie en `UNSAT` ou `TIMEOUT` ;
9. un fichier d’agrégation contient des lignes dupliquées ;
10. le jeu test est utilisé pour régler un hyperparamètre.

Après correction, la campagne concernée doit être relancée avec :

- une nouvelle version du protocole ;
- un nouveau commit ;
- une note d’intégrité ;
- une explication de l’impact du bug.

---

# 27. Critères finaux d’acceptation du papier

## G1 — Vérificateur

\[
\boxed{\text{0 divergence exhaustive}}
\]

## G2 — Soundness empirique

\[
\boxed{\text{0 faux positif observé}}
\]

## G3 — Intégrité

\[
\boxed{\text{0 instance mal alignée}}
\]

## G4 — Réparation

Pour revendiquer une amélioration :

\[
\mathrm{CI}_{95\%}
\left(
\Delta_{\mathrm{repair}}
\right)
\subset(0,+\infty).
\]

## G5 — Qualité

Cible recommandée, à pré-enregistrer :

\[
\operatorname{median}(\mathrm{Gap})\leq5\%.
\]

Si cette cible n’est pas atteinte, rapporter la valeur observée sans modifier le seuil après coup.

## G6 — Deadline

Pour une revendication de boucle 100 ms :

\[
p_{99}(t_{\mathrm{end-to-end}})\leq100\text{ ms}.
\]

Pour une revendication de boucle 1 s :

\[
p_{99}(t_{\mathrm{end-to-end}})\leq1\text{ s}.
\]

## G7 — Effet télécom

Au moins un compromis KPI doit être favorable sans dégradation inacceptable des SLA. Par exemple :

- énergie réduite avec SLA maintenus ;
- handover failures réduits sans surcharge excessive ;
- débit amélioré sans dépassement énergétique majeur.

Il ne suffit pas de produire une solution CSP faisable.

## G8 — Reproductibilité

Un évaluateur externe doit pouvoir exécuter :

```bash
make reproduce-oran-fast
```

et reconstruire :

- les sanity gates ;
- un sous-ensemble des expériences ;
- les audits ;
- les tableaux ;
- les figures ;
- le PDF.

---

# 28. Structure des résultats dans l’article

## Tableau 1 — Protocole

Inclure :

- nombre d’instances ;
- nombre de seeds ;
- versions ;
- matériel ;
- budgets ;
- paramètres MIRAGE-R ;
- rayon de réparation ;
- seuils du détecteur.

## Tableau 2 — Sanity gate

Rapporter :

- tests ;
- succès ;
- divergences ;
- faux positifs ;
- erreurs.

## Tableau 3 — Comparaison principale

Colonnes :

- verified feasible ;
- repaired ;
- fallback ;
- unknown ;
- timeout ;
- error ;
- utility ;
- p50/p95/p99 latency.

## Tableau 4 — Par type de conflit

- direct ;
- indirect ;
- implicite ;
- mixte.

## Tableau 5 — KPI télécoms

- throughput ;
- p05 throughput ;
- energy/bit ;
- HOF ;
- fairness ;
- SLA violation.

## Tableau 6 — Noyaux de réparation

- fréquence ;
- taille médiane ;
- p95 ;
- maximum ;
- succès ;
- timeout.

## Tableau 7 — Ablations

- annealing ;
- polarisation ;
- régions ;
- diagnostic ;
- réparation.

## Tableau 8 — Statistiques

- différence appariée ;
- CI ;
- p-value ;
- p-value Holm ;
- taille d’effet.

---

# 29. Revendications conditionnelles

## Si MIRAGE-R-CM améliore significativement le cœur

Écrire :

> MIRAGE-R-CM significantly increased verified conflict-free decision coverage over the continuous core. The gain was primarily attributable to exact repair of small conflict-induced subproblems rather than to uncorrected dynamic region insertion.

## Si les régions restent quasi nulles

Écrire :

> Dynamic regions fired as designed but produced no material improvement. This result is consistent with the double-counting diagnosis inherited from the generic CSP study.

## Si la réparation est trop lente pour 100 ms

Écrire :

> The method is suitable for medium or slow near-real-time control loops, but the measured tail latency does not support deployment in a 100-ms loop.

## Si CP-SAT global gagne

Écrire :

> Global CP-SAT remained superior on small and medium instances. MIRAGE-R-CM became relevant only when conflict cores remained small relative to the complete coordination model.

## Si aucun avantage n’est observé

Écrire honnêtement :

> The continuous front end did not improve feasibility or latency over direct CP-SAT coordination under the tested conditions.

Ce résultat négatif invaliderait le positionnement « nouveau coordonnateur performant », mais pourrait encore soutenir un article centré sur le diagnostic des points fixes.

---

# 30. Formulation exacte de la garantie

La formulation finale recommandée est :

> MIRAGE-R-CM never forwards a candidate action without independent verification. Therefore, every action accepted by the framework satisfies the registered finite-domain conflict and SLA model. Across the complete frozen evaluation campaign, all accepted actions passed re-verification, yielding zero observed false positives. This guarantee is relative to the normalized model; it does not by itself prove that the model fully captures every physical interaction in a deployed O-RAN.

Cette phrase est rigoureuse, défendable et cohérente avec votre protocole IJOC.

---

# 31. Livrables finaux

Avant soumission, les éléments suivants doivent exister.

```text
O-RAN_ARTIFACT/
├── README.md
├── PROTOCOL.md
├── RUNBOOK.md
├── INTEGRITY.md
├── LICENSE
├── AUTHORS
├── CITATION.cff
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements-lock.txt
├── MANIFEST.sha256
├── configs/
├── manifests/
├── normalized_instances/
├── raw_logs/
├── aggregation/
├── figures/
├── tables/
└── paper/
```

Le fichier `INTEGRITY.md` doit contenir :

- tous les bugs détectés ;
- les campagnes affectées ;
- les corrections ;
- les commits ;
- les relances ;
- les résultats des audits ;
- le nombre exact de faux positifs ;
- les éventuelles exclusions et leur justification.

---

# 32. Décision go/no-go

## GO — Article complet

Soumettre l’article expérimental complet si :

- G1–G4 passent ;
- au moins un avantage significatif est observé ;
- les KPI télécoms sont mesurés ;
- la latence est compatible avec la classe revendiquée ;
- le testbed ou l’émulation confirme l’intégration.

## GO limité — Article diagnostic

Soumettre un article centré sur les points fixes si :

- la soundness passe ;
- les stalls sont bien caractérisés ;
- mais MIRAGE-R-CM ne surpasse pas CP-SAT ou les baselines.

Le titre doit alors devenir :

> **Fractional Stalls in Continuous xApp Coordination: A Verified O-RAN Conflict-Management Study**

## NO-GO temporaire

Ne pas soumettre si :

- un faux positif subsiste ;
- le vérificateur diverge de l’oracle ;
- les traces ne sont pas alignées ;
- les relations implicites sont construites et évaluées par le même modèle ;
- aucune mesure télécom n’est disponible ;
- les résultats ne sont pas reproductibles depuis les logs bruts.

---

Avec ce protocole, vous ne promettez pas une impossible « validation universelle à 100 % ». Vous obtenez quelque chose de plus solide : **une garantie logique conditionnelle, zéro faux positif observé sur une campagne gelée, une validation exhaustive sur les petites instances, une comparaison exacte avec CP-SAT, et une validation télécom en boucle fermée**.
