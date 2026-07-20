# Auto-Review of the revised manuscript, no need to  letter of response, check each recommandation before correcting on main6.tex


# Reviewer Report

## 1. Overall assessment

This manuscript presents **ConsistXApp**, a multi-xApp arbitration architecture for the O-RAN Near-RT RIC. Its main contribution is not a new constraint-programming algorithm, but the integration of:

1. incremental generalized arc consistency;
2. explanation-guided expanding repair cores;
3. CP-SAT-based repair and lexicographic optimization;
4. an independently implemented forwarding verifier;
5. model-version binding; and
6. replayable audit certificates.

The topic is relevant to *Annals of Telecommunications*, which publishes original telecommunications research, and the manuscript addresses an important problem in programmable O-RAN control. The paper is technically substantial, unusually explicit about limitations, and supported by an extensive synthetic evaluation.

However, the current version does not yet provide sufficiently strong evidence for several of its central systems claims. In particular:

- the sequential latency comparison is limited to a Python rebuild-and-resolve CP-SAT baseline;
- verification, certificate construction, serialization, and E2 transport are excluded from the principal latency figures;
- the version-bound atomic forwarding mechanism is specified but not implemented or experimentally tested;
- the audit certificate is replayable but not demonstrably tamper-evident;
- the evaluation is entirely synthetic and structurally favourable to local repair;
- the currently accessible artifact does not clearly contain all the material claimed in the data-availability statement;
- there is at least one serious contradiction concerning solver determinism and worker count.

The paper is potentially publishable after substantial correction and strengthening.

---

## 2. Main strengths

### 2.1 Clear separation of guarantees

The manuscript correctly distinguishes:

- registered-model feasibility;
- physical-RAN safety;
- availability;
- timeliness;
- solver feasibility;
- solver optimality; and
- formal verification versus empirical verifier validation.

This is a major strength. The repeated statement that acceptance only means compliance with the registered finite-domain model is scientifically responsible.

### 2.2 Sound architectural principle

Treating every optimizer output as an untrusted proposal until it passes an independent full-model verifier is a sensible and practically relevant design principle.

Proposition 1 is mathematically straightforward, but it clearly states the conditions required for forwarding soundness: verifier correctness, exclusive gating, and atomic model-version handling.

### 2.3 Strong negative-result reporting

The manuscript openly reports that:

- there is no cold-start advantage;
- local repair reduces objective quality;
- the continuous-relaxation stage is counterproductive;
- the median advantage disappears near the tail;
- no hard real-time guarantee is established; and
- the baseline does not represent every possible incremental solver architecture.

This considerably increases confidence in the authors’ scientific judgement.

### 2.4 Useful ablations

The comparison among fixed violated-scope, radius-based, frontier, explanation-guided, assumption-core, and full-scope repair is informative. The result that expanding cores recover 21 instances missed by fixed-scope repair is relevant, even though it demonstrates the benefit of expansion more strongly than the specific benefit of explanations.

### 2.5 Appropriate statistical caution

Using episodes rather than individual epochs as the inferential unit in the sequential campaign is appropriate. The manuscript also correctly treats p95 and especially p99 results as descriptive because of temporal dependence and the small number of extreme observations.

---

# 3. Major comments

## Major Comment 1 — The central sequential baseline is too limited

The main performance conclusion compares ConsistXApp against CP-SAT models rebuilt in Python at every epoch. The manuscript acknowledges this limitation, but the sequential latency advantage is still prominent in the title, abstract, contributions, results, and conclusion.

The comparison does not isolate the benefit of explanation-guided repair from the cost of repeatedly constructing a complete Python CP-SAT model. At \(n=1000\), the manuscript reports approximately 6.9 ms for model construction and 18.4 ms for solver search. Thus, a substantial part of the reported advantage comes from avoiding Python reconstruction.

At minimum, the authors should add one stronger baseline:

1. solver-native large-neighbourhood search centred on the previous accepted decision;
2. a full CP-SAT model built once with activation literals for relations, allowing version-specific changes through assumptions;
3. a persistent alternative solver that supports incremental modification; or
4. a complete CP-SAT solve restricted by an adaptive neighbourhood chosen without propagation explanations.

Without such a baseline, the conclusion must be narrowed to:

> ConsistXApp outperformed the evaluated Python rebuild-and-resolve CP-SAT implementations on the generated sequential workloads.

It should not be presented as a general advantage over “complete CP-SAT” or complete solving.

---

## Major Comment 2 — End-to-end latency excludes central components

The reported latency excludes:

- independent verification;
- certificate construction and serialization;
- certificate persistence;
- model-registry access;
- atomic version comparison;
- forwarding authorization;
- E2 transport; and
- Near-RT RIC scheduling effects.

This is particularly problematic because the verifier and audit certificate are presented as the paper’s central contributions. A system cannot claim low-latency auditable arbitration while excluding the cost of producing and storing the audit object.

The authors should report at least:

\[
T_{\text{total}} =
T_{\text{update}}+
T_{\text{prop}}+
T_{\text{decode}}+
T_{\text{repair}}+
T_{\text{verify}}+
T_{\text{certificate}}+
T_{\text{version-commit}}.
\]

Certificate size and replay latency should also be measured as functions of:

- number of variables;
- number of constraints;
- initial violation count;
- number of core expansions; and
- explanation/core size.

If E2 transport cannot be evaluated, “end-to-end” should be removed from table and figure captions. “Coordination-computation latency” would be more accurate.

---

## Major Comment 3 — Version binding is assumed rather than validated

Atomic model-version handling is essential to Proposition 1. However, the manuscript appears to provide an architectural sequence rather than an implemented transaction evaluated under concurrency.

The authors should clarify:

- whether model lookup, verification, acceptance logging, and forwarding authorization are actually implemented as one transaction;
- what concurrency-control mechanism is used;
- whether model versions are immutable;
- how authorization tokens are invalidated;
- what happens if the registry is unavailable; and
- whether forwarding and audit persistence are atomic or only ordered.

A targeted race-condition campaign should repeatedly change the active model between verification and forwarding. The expected result is zero stale-version forwardings.

Without such evidence, the claim should be described as a **required deployment protocol**, not as an experimentally validated property of the current implementation.

---

## Major Comment 4 — “Auditable certificate” needs integrity and provenance guarantees

Definition 1 establishes replayable trace consistency and final feasibility. It does not establish that the certificate:

- has not been modified;
- corresponds to the action actually forwarded;
- refers to an immutable model snapshot;
- was emitted by an authorized verifier; or
- is complete.

A model-version string such as `nu17` is insufficient unless it is cryptographically bound to a canonical model representation.

The certificate should contain, or the paper should discuss:

- a cryptographic hash of the canonical registered model;
- a hash of the context snapshot;
- a hash of the exact forwarded assignment;
- verifier implementation/version identifier;
- canonical serialization rules;
- timestamp or monotonic sequence number;
- digital signature or message authentication code; and
- append-only or tamper-evident storage.

Otherwise, “replayable certificate” is justified, but “auditable” should be qualified as **logical replayability without tamper-evidence**.

---

## Major Comment 5 — The verifier-validation evidence needs fuller characterization

The 680,450 checks are encouraging, but the absolute number alone is not sufficient. Approximately 602,000 checks come from property-based testing; the paper should report:

- number of independently generated models;
- distribution of variable counts, domain sizes, arities, and relation tightness;
- number of malformed versus well-formed candidates;
- number of accepted and rejected cases;
- treatment of duplicate generated tests;
- shrinking strategy used by the property-testing framework;
- coverage of context/version errors; and
- code coverage or mutation score, if available.

The manuscript correctly states that input mutation is not code-mutation testing. Adding implementation mutation testing would materially strengthen the verifier claim: deliberately inject faults such as omitted constraints, incorrect tuple indexing, stale-context acceptance, missing-variable acceptance, and off-by-one domain errors, then report which tests detect them.

The term “independently implemented” should also be operationally defined. Separate functions are not necessarily independent if they share model normalization, generated relation objects, or utility routines.

---

## Major Comment 6 — Synthetic O-RAN validity remains weak

The five scenarios are described using O-RAN terminology, but the actual workloads are generated finite-domain positive-table CSPs with planted feasible assignments. The pseudo-physical model is not validated against an O-RAN emulator, system-level simulator, or measured RAN data.

The manuscript already acknowledges this limitation, but stronger evidence is necessary for a telecommunications journal. Ideally, the authors should provide at least one closed-loop case study using:

- ColO-RAN;
- OpenRAN Gym;
- FlexRIC;
- ns-O-RAN/ns-3;
- an O-RAN Software Community Near-RT RIC; or
- another reproducible RIC/E2 environment.

If this is not feasible, the paper should provide a detailed transformation from a realistic xApp conflict scenario to the registered table constraints, including actual parameter ranges, SLA thresholds, context updates, and E2 control semantics.

The current results establish performance on structured dynamic CSPs inspired by O-RAN, not deployment effectiveness in an O-RAN system.

---

## Major Comment 7 — The evaluated graph structure favours localization

The manuscript reports a mean constraint-graph degree of 3.4, maximum degree 8, and arity 2–3. This structure is favourable to local propagation and repair.

A systematic sensitivity study is needed over:

- graph degree and density;
- clustering coefficient;
- relation arity;
- domain size;
- table tightness;
- connected-component size;
- feasible-region fragmentation;
- update locality; and
- distance between consecutive feasible assignments.

The most important response variables are:

- probability of expansion to full scope;
- final core fraction \(|A_r|/|A_t|\);
- median and tail latency;
- certificate size;
- repair success; and
- objective-quality loss.

This would identify the actual structural regime in which incremental repair is beneficial.

---

## Major Comment 8 — Candidate-generator dependence should be integrated into the main pipeline

The headline static result—248 repaired candidates out of 250—is produced by a deliberately conflict-unaware decoder. Forward checking reduces the number requiring repair to 35.

Therefore, the principal end-to-end evaluation should use the strongest practical pipeline, not only the weakest decoder used for ablation. The authors should evaluate:

> conflict-aware candidate generation + expanding repair + verifier + certificate.

This combined pipeline should be used in the sequential campaign as well. Otherwise, the paper separately demonstrates that:

- a weak decoder creates many repair opportunities; and
- stronger decoders reduce repair frequency;

but does not establish the performance of the recommended operational configuration.

---

## Major Comment 9 — Correct the internal contradiction about determinism

The conclusion states:

> “On 250 generated static instances in a multi-worker non-deterministic environment…”

This directly contradicts Table 5 and Section 6.2, which state:

- one experiment process;
- `num_search_workers = 1`;
- deterministic instance seeds; and
- no process-level parallelism.

This is not a minor stylistic issue because experimental determinism is part of the reproducibility argument. The conclusion must be corrected, and the authors should verify whether the table, methods section, or conclusion reflects the actual run configuration.

---

## Major Comment 10 — The public artifact does not yet clearly match the availability statement

The manuscript claims availability of:

- code;
- generated instances;
- raw logs;
- explanation traces;
- verifier-validation reports;
- reproducibility manifests;
- seed hierarchy;
- command lines; and
- scripts reproducing all tables and tests.

The repository is accessible and contains source code, tests, scripts, and result CSV files. However, in its currently visible state, it does not clearly expose a complete reproducibility manifest, pinned dependency file, formal release, or license file, despite the README stating an MIT licence.

Before publication, the authors should provide:

1. a tagged immutable release;
2. a DOI, preferably through Zenodo;
3. `requirements.txt`, `environment.yml`, or equivalent lock file;
4. an actual `LICENSE` file;
5. one-command reproduction instructions;
6. machine-readable campaign manifests;
7. checksums for raw result files;
8. the exact manuscript-to-artifact version mapping; and
9. removal of committed `.DS_Store` and `__pycache__` files.

The data-availability statement should be checked against the contents of the archived release, not the mutable default branch.

---

# 4. Minor comments

1. The manuscript is long and repetitive. The limitations are commendable but are restated in the abstract, introduction, results, limitations, and conclusion. A reduction of approximately 15–20% would improve readability.
2. The sentence in the introduction beginning “The scope of this comparison an evaluated Python rebuild-and-resolve baseline…” is grammatically incomplete.
3. Table 1 should be supported more carefully. “n/r” avoids asserting absence, but each classification should be traceable to specific passages in the cited work.
4. Define precisely whether all explicit relations are positive tables. If other relation types are supported, describe their exact verifier and CP-SAT encodings.
5. Report the number and proportion of explanation-, assumption-core-, and frontier-driven expansions per dataset, not only aggregate “used” counts.
6. Explain why an `UNKNOWN` status immediately invokes fallback rather than expanding the core or trying a lower-cost feasibility-only strategy with the remaining deadline.
7. Clarify whether certificates are emitted for direct decodes, fallbacks, and blocked outcomes, or only for repaired decisions. Operational auditability arguably requires records for every forwarding decision and every blocked decision.
8. Table 12’s “completed repair sequences” terminology is confusing for episode-level sequential results. Distinguish repair calls, repaired epochs, and episodes.
9. Report confidence intervals for the objective-quality gap, not only a p-value and effect size.
10. “Certified optimum” should always be qualified by the encoded model, integer scaling, and active lexicographic levels.
11. Check author-affiliation formatting and use consistent superscripts.
12. The journal name is **Annals of Telecommunications**, not “Anals of Communications.”

---

# 5. Required revision priorities

Before acceptance, I consider the following essential:

1. Correct the worker-count/determinism contradiction.
2. Narrow all performance claims to the evaluated rebuild-and-resolve baseline.
3. Include verification and certificate overhead in the reported pipeline latency.
4. Measure certificate size and replay time.
5. Validate or clearly reclassify atomic version binding as a non-implemented deployment requirement.
6. Add at least one stronger incremental or neighbourhood-based baseline.
7. Evaluate the recommended conflict-aware decoder plus verified repair pipeline.
8. Strengthen structural sensitivity experiments beyond sparse arity-2/3 instances.
9. Complete and archive the reproducibility artifact.
10. Clarify that the certificate is replayable but not tamper-evident unless cryptographic binding is added.

---

# 6. Final recommendation

The manuscript has a credible conceptual contribution and demonstrates commendable scientific restraint. The verifier-gated architecture, version-aware forwarding rule, and replayable repair traces form a potentially useful contribution to O-RAN conflict management. Nevertheless, the present evidence is not yet sufficient to support the complete systems narrative, particularly regarding end-to-end latency, auditability, atomic version binding, baseline fairness, and O-RAN deployment relevance.

If the authors address the major issues above—especially the baseline, full-pipeline measurements, artifact completeness, and internal inconsistency—the paper could become suitable for publication.
