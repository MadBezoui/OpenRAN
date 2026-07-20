The manuscript presents a potentially valuable systems-integration idea: using observable generalized arc consistency, propagation explanations, continuous coordination, localized exact repair, and independent verification for xApp conflict management. The conceptual architecture is interesting, and several theoretical statements are sound.

However, the current version is **not publication-ready**. The principal problem is not the basic idea but the reliability and internal consistency of the experimental evidence. Several central numerical claims contradict the tables, the statistical protocol is not actually reflected in the results, some baselines are not compared fairly or are ambiguously defined, and the final section contains incomplete or corrupted sentences. These problems prevent a reviewer from validating the main claims.

A substantially revised paper could become publishable, but the results section must be regenerated from an auditable experiment pipeline rather than edited locally.

---

## 1. Summary of the contribution

The paper models multi-xApp coordination as a dynamic finite-domain constraint optimization problem. The proposed framework, ConsistXApp, combines:

1. incremental GAC over positive table constraints;
2. restoration after domain or relation relaxations;
3. propagation explanations;
4. continuous relation-conditioned marginal updates;
5. diagnosis of fractional stalls and invalid decodes;
6. explanation-guided construction of an exact repair core;
7. full-scope CP-SAT escalation;
8. an independent verifier before execution.

The manuscript also establishes several elementary but relevant results:

- GAC filtering preserves globally feasible assignments;
- non-empty GAC domains do not imply global feasibility;
- GAC does not remove the symmetric fractional state in a two-variable disequality example;
- repair becomes conditionally complete after full-scope expansion;
- values deleted under a previous context must be reconsidered after relaxation.

These are useful correctness boundaries, particularly in an O-RAN setting where unsafe overinterpretation of local consistency would be problematic.

---

# 2. Strengths

## 2.1 Clear separation of reasoning failure modes

One of the strongest aspects is the distinction between:

- unsupported individual actions;
- propagation domain wipeouts;
- non-empty but globally incompatible local supports;
- invalid fractional stalls;
- invalid non-stalled decodes;
- boundary-induced local repair infeasibility;
- global infeasibility;
- deadline failure.

This taxonomy is appropriate and more careful than many heuristic xApp-coordination papers.

## 2.2 Correct emphasis on an independent verifier

The principle that no action is forwarded unless checked independently against current domains and every registered hard relation is sound. Proposition 1 is nearly tautological, but it communicates an important engineering requirement.

The paper also correctly limits its safety claim to the **registered model**, rather than claiming physical RAN safety.

## 2.3 Proper treatment of dynamic relaxations

Maintaining separate base and filtered domains is essential. Proposition 8 correctly explains why deleted values may need to be restored when constraints or relations are relaxed. This is aligned with established dynamic-CSP work, in which justifications can be used to restore values after relaxation.

## 2.4 The GAC limitation is correctly acknowledged

The manuscript does not claim that GAC solves the complete coordination problem. The two-variable disequality example correctly demonstrates that all values can have local support while deterministic decoding remains invalid.

This is consistent with the established interpretation of GAC as a local filtering mechanism rather than a complete decision procedure. The table-constraint literature likewise characterizes GAC as local filtering normally combined with search [Yap et al., 2020](https://ojs.aaai.org/index.php/AAAI/article/view/7086/6940).

## 2.5 Relevant O-RAN motivation

The paper is reasonably positioned relative to PACIFISTA, QACM, and conflict-mitigation architecture. PACIFISTA, for example, focuses primarily on profiling and predicting conflicts, whereas this paper targets finite-domain arbitration after relations have been registered [PACIFISTA](https://arxiv.org/abs/2405.04395).

That distinction is potentially publishable.

---

# 3. Major concerns

## 3.1 The main quantitative claims are internally contradictory

This is the most serious issue.

### 3.1.1 Tuple-reduction claim

The abstract states:

> “the pooled value- and tuple-reduction ratios are 21.7% and 34.1%”

Section 7.2 states:

> “21.7% of candidate values and 33.7% of relation tuples on average”

Table 2 reports per-scenario tuple reductions of:

- 28.7%
- 39.2%
- 34.5%
- 29.4%
- 36.3%

The unweighted scenario mean is:

\[
\frac{28.7+39.2+34.5+29.4+36.3}{5}=33.62\%.
\]

But the pooled ratio computed from the tuple totals is:

\[
1-\frac{1713+3697+4858+6846+7488}
{2403+6083+7419+9694+11747}
\approx 34.15\%.
\]

Thus:

- **34.1%** is a plausible pooled reduction;
- **33.7%** is approximately an unweighted scenario mean;
- these are different estimands and must not be used interchangeably.

The same distinction must be made for value reduction.

### Required correction

Define and report separately:

1. pooled micro-average;
2. unweighted scenario macro-average;
3. median per-instance reduction;
4. confidence intervals over independent instances or seeds.

---

## 3.2 The abstract’s “74.4% feasibility” is not consistent with the paper’s own feasibility definition

The abstract says ConsistXApp:

> “attains 74.4% feasibility”

Table 3 indicates for Full ConsistXApp:

- accepted without repair: 56.8%;
- local repair: 17.6%;
- fallback: 25.6%;
- blocked: 0%;
- timeout: 0%.

Apparently:

\[
56.8+17.6=74.4\%
\]

is being called “feasibility,” while the 25.6% verified fallback is excluded.

However, Equation (70) defines the verified-feasibility rate as:

\[
r_}
===

\frac{\text{verifier-accepted decisions}}
{\text{decision epochs}}.
\]

If fallback decisions are verifier-accepted, then according to this definition Full ConsistXApp has:

\[
56.8+17.6+25.6=100\%
\]

verified executable decisions.

Therefore, at least three distinct metrics are being conflated:

1. valid direct decode rate;
2. optimized non-fallback decision rate;
3. total verifier-accepted execution rate, including fallback.

### Required correction

Use explicit names such as:

- \(r_{\text{direct}}\): valid without repair;
- \(r_{\text{repair}}\): verified repaired decisions;
- \(r_{\text{optimized}}\): direct plus repaired;
- \(r_{\text{fallback}}\): verified fallback;
- \(r_{\text{executable}}\): optimized plus fallback;
- \(r_{\text{blocked}}\): no executable action.

The abstract should not call 74.4% simply “feasibility.”

---

## 3.3 The 100 ms deadline results are contradictory

The abstract claims:

> “56.8% deadline compliance under strict 100ms bounds.”

Table 4 reports **83.0%** at 100 ms for Full ConsistXApp.

Table 3 appears to report **56.8%** in a column labelled “P95 ≤ 100ms (%)”, but the formatting is severely damaged and the interpretation is unclear.

These cannot all describe the same metric and dataset.

### Required correction

For each dataset and method, report:

\[
\Pr(T \le B \land \text{verifier accepts optimized decision}),
\]

\[
\Pr(T \le B \land \text{verifier accepts any decision}),
\]

and, separately,

\[
\Pr(T \le B \mid \text{decision is optimized}).
\]

Do not mix:

- direct decode within deadline;
- any optimized result within deadline;
- fallback within deadline;
- all verifier-accepted outcomes.

Every deadline curve must specify its denominator.

---

## 3.4 Table 3 is not interpretable in its present form

The table headers and values are visibly misaligned. For example:

- the relationship between “Utility,” “Accepted without repair,” “Local Repair,” “Full-scope Repair,” “Fallback,” “Blocked,” “Timeout,” “Median,” “P95,” and “≤100ms” is not reliably recoverable;
- the uncoordinated method appears to have 100% “accepted without repair,” which conflicts with the statement that all methods use an independent verifier;
- CP-SAT appears to return 100% directly accepted decisions, but the solver status—`FEASIBLE` versus `OPTIMAL`—is not reported.

A core results table cannot require the reader to reconstruct column alignment from prose.

### Required correction

Regenerate the table directly from the analysis script, preferably with one row per method and unambiguous columns:

| Method | Direct valid | Local repair | Full repair | Fallback | Blocked | Timeout | Median latency | P95 latency | Utility |
| ------ | -----------: | -----------: | ----------: | -------: | ------: | ------: | -------------: | ----------: | ------: |

All mutually exclusive outcome columns should sum to 100%, with an automated assertion in the analysis code.

---

## 3.5 The uncoordinated baseline conflicts with the verification protocol

Section 6.6 says:

> “All methods use a common input model, timing harness, and independent verifier.”

Yet Table 3 apparently reports 100% accepted decisions for “Uncoordinated execution.”

If uncoordinated candidate requests can violate hard relations, they cannot all be verifier-accepted. If “accepted” means merely “forwarded without arbitration,” then the metric is not comparable with the other methods.

### Required correction

For uncoordinated execution, report at least:

- raw forwarded-request rate;
- verifier-valid rate;
- number of violated hard constraints;
- SLA violations;
- whether invalid requests would actually be blocked by the common execution gate.

A method bypassing the verifier cannot be evaluated under the same “accepted decision” semantics.

---

## 3.6 The explanation-guided contribution is not sufficiently isolated

The main novelty is claimed to be explanation-guided repair. However, the experimental evidence does not establish this clearly.

Table 6 reports only 64 repair-triggering epochs for radius-based and explanation-guided strategies. Both apparently have the same success rate of 68.8%. The main demonstrated improvement is a median initial core reduction from 3 to 2 variables.

This evidence is too limited for the prominence given to the contribution because:

- 64 repair attempts are a small effective sample;
- no confidence interval is reported;
- no paired latency difference is reported clearly;
- no number of expansions is reported;
- no final core size is reliably shown;
- solver work—branches, conflicts, propagations—is absent;
- explanation construction/checking overhead is not compared against savings;
- the manuscript alternates between initial, median, and final core size.

### Required correction

For identical repair-triggering epochs, report paired distributions of:

- initial core size;
- final core size;
- number of expansions;
- GAC time during repair;
- explanation-construction time;
- CP-SAT wall time;
- branches and conflicts;
- total repair latency;
- success within each deadline;
- escalation rate;
- fallback rate.

Include paired bootstrap confidence intervals.

---

## 3.7 The paper does not specify how CP-SAT conflict explanations are produced

Section 4.11 states that local solver infeasibility triggers expansion using:

> “an auditable solver conflict explanation when available.”

This is underspecified. CP-SAT does not automatically return an application-level explanation over arbitrary domain fixings unless the model is explicitly instrumented, typically through assumptions. The Python API exposes a sufficient set of assumptions for infeasibility, but this is not necessarily minimal and must be mapped carefully to boundary decisions.

The OR-Tools API supports `sufficient_assumptions_for_infeasibility`, but the paper must state exactly how assumptions are represented and translated into variable/constraint expansions [OR-Tools Python API](https://or-tools.github.io/docs/pdoc/ortools/sat/python/cp_model.html).

### Required correction

Specify:

1. which constraints or boundary fixings receive assumption literals;
2. whether every external fixing \(x_j=\hat{x}_j\) has its own literal;
3. how the returned sufficient assumption set is converted into `VarLit`;
4. how the explanation is validated;
5. what happens for `UNKNOWN`;
6. whether optimization is disabled during infeasibility-core extraction;
7. whether the core is minimized;
8. the exact deterministic fallback when no usable core is available.

Without this, “explanation-guided exact repair” is not reproducible.

---

## 3.8 The baseline called “complete CP-SAT” is terminologically misleading

A deadline-bounded CP-SAT run is not necessarily “complete” in the empirical sense. OR-Tools distinguishes:

- `OPTIMAL`;
- `FEASIBLE`;
- `INFEASIBLE`;
- `UNKNOWN`.

A `FEASIBLE` result is not proven optimal, and `UNKNOWN` does not establish either feasibility or infeasibility. This is explicit in the official documentation [OR-Tools CP-SAT documentation](https://developers.google.com/optimization/cp/cp_solver).

The theoretical Proposition 6 correctly adds the assumptions that:

- the solver is complete;
- the time limit is not reached.

But the experimental terminology repeatedly says “complete CP-SAT” under deadlines.

### Required correction

Use:

- “full-scope CP-SAT” for the model scope;
- “proved optimal” only for `OPTIMAL`;
- “feasible incumbent” for `FEASIBLE`;
- “proved infeasible” only for `INFEASIBLE`;
- “unresolved” for `UNKNOWN`.

Report solver statuses and objective gaps.

---

## 3.9 The comparison against CP-SAT is not demonstrably fair

The paper reports that CP-SAT is substantially faster than the full pipeline, which is an important negative result. However, a fair comparison requires clarity on whether methods optimize the same objective.

Full ConsistXApp immediately accepts a valid continuous decode, apparently without solving the lexicographic objective. Direct CP-SAT seems to optimize the complete objective. Therefore:

- latency comparisons may favor ConsistXApp by permitting non-optimal valid decisions;
- utility comparisons may favor CP-SAT because CP-SAT optimizes explicitly;
- “decision quality” is not equivalent across methods.

### Required correction

Provide two CP-SAT baselines:

1. **feasibility-first CP-SAT:** stop after the first verified feasible assignment;
2. **optimization CP-SAT:** optimize the same lexicographic objective within the deadline.

Also report ConsistXApp’s optimality gap or utility regret relative to the best known/full-scope solution.

---

## 3.10 The incremental experiment contains suspicious or unexplained timing values

Table 7 reports:

- relaxed full recomputation: 333.30 ms;
- relaxed incremental: 6.00 ms;
- mixed full recomputation: 1.11 ms;
- mixed incremental: 0.02 ms.

A relaxation is naturally more expensive than a restriction, but a roughly 300-fold difference between relaxed and mixed recomputation requires explanation, especially because “full recomputation” should restart from current base domains in both cases.

Also:

- “Base” has decision time 101.43 ms despite GAC time of 0.19 ms;
- utility-only incremental propagation takes 1.20 ms although no constraint update should require propagation;
- the counts are highly unbalanced: 12,600 mixed transitions versus 750 for most other classes.

### Required correction

Explain:

- instance-size distributions within each transition class;
- whether timings compare matched models of equal size;
- whether continuous and solver time are included in “Decision” but not propagation columns;
- why utility-only transitions invoke the propagation machinery;
- whether cache invalidation or Python allocation dominates;
- the number of tuple inspections and queue operations, not only wall time.

Stratify by update fraction: 1%, 5%, 10%, 25%, and 50%.

---

## 3.11 The statistical protocol is promised but not delivered

Section 6.11 promises:

- 50 independent seeds;
- paired bootstrap 95% confidence intervals;
- medians and IQRs;
- tail percentiles;
- paired effect sizes;
- Holm correction;
- right-censoring of timeouts.

Most reported results do not include these.

For example:

- Tables 2, 3, 5, 6, 8, and 9 have no uncertainty estimates;
- the explanation-guided comparison has no paired confidence interval;
- network metrics have no variability;
- no hypothesis tests or Holm-adjusted results appear;
- timeout censoring is not shown;
- the experimental unit is unclear for dynamic sequences with temporal dependence.

### Required correction

Either implement the stated protocol or remove unsupported promises. Because dynamic epochs within an episode are correlated, resampling should occur at the **episode or seed level**, not at the individual-epoch level.

---

## 3.12 The dataset accounting is unclear

The abstract says:

- 15,000 unique decision epochs;
- ten methods;
- 150,000 method–epoch observations.

Section 6.5 says the principal dynamic configuration uses:

- 30 episodes;
- 100 epochs each,

which gives 3,000 epochs. It may be that the five modification fractions produce:

\[
30 \times 100 \times 5 = 15{,}000,
\]

but this is not stated explicitly.

Table 7 totals:

\[
150+750+750+12600+750=15{,}000,
\]

but the origin of the strongly dominant 12,600 mixed transitions is unexplained.

### Required correction

Add a dataset-accounting table listing:

- suite;
- scenarios;
- configurations;
- seeds;
- episodes;
- epochs;
- unique instances;
- methods;
- total observations.

---

## 3.13 The safe-fallback semantics are logically inconsistent for an infeasible base model

Section 4.4 correctly states that a complete-base-model wipeout proves infeasibility of the unchanged model and that exact search cannot recover a feasible solution.

Section 4.12 then requires that fallback:

> “must be represented explicitly in the current action model”
> and “must satisfy the current domains and hard relations.”

But if the complete current model is infeasible, no such fallback exists.

The paper partially recognizes this by mentioning an emergency model, request retraction, or policy relaxation under a new context identifier. Nevertheless, the end-to-end procedure says that after an initial propagation wipeout the framework may execute a verified fallback.

### Required correction

Distinguish two cases:

1. **Boundary-induced repair wipeout:** expand the repair core.
2. **Complete base-model wipeout:** no feasible action exists in \(M_t\).

In the second case, an emergency action requires a formally defined transition:

\[
M_t \rightarrow M'_t,
\]

with authorized constraint retraction, changed priorities, or an emergency policy. Verification must then be performed against \(M'_t\), not \(M_t\).

Do not describe this as finding a fallback in the unchanged infeasible model.

---

## 3.14 The O-RAN model is mostly synthetic and remains weakly connected to operational RAN semantics

The paper presents explicit positive tables as registered relations, but it does not sufficiently explain how realistic O-RAN relations are generated.

Important missing details include:

- mapping E2 control requests to finite-domain values;
- relation construction from KPM thresholds;
- uncertainty in digital-twin predictions;
- stale KPMs;
- asynchronous xApp requests;
- delayed control effects;
- conflicting time horizons;
- relation-table growth with arity;
- SLA hysteresis;
- E2 and platform overhead.

The pseudo-physical network model is too briefly described to support the network-level claims.

### Required correction

Provide at least one fully specified scenario from:

1. xApp request;
2. action-domain construction;
3. parameter/KPM mapping;
4. hard-relation generation;
5. utility calculation;
6. selected action;
7. resulting network metric.

At least one emulated or trace-driven scenario is necessary for a strong O-RAN systems claim.

---

## 3.15 The network-level results are not credible enough in their current form

Table 9 reports energy per bit as **0.0 µJ** for all methods and nearly zero handover-failure rates. This suggests either:

- severe rounding;
- a scaling/unit error;
- a model that does not exercise the relevant behavior.

The table also lacks:

- sample sizes;
- uncertainty;
- load and mobility conditions;
- baseline normalization;
- SLA violation counts;
- action churn;
- the \(\mu\) values promised in Section 7.8.

### Required correction

Report sufficient significant digits, units, confidence intervals, and scenario conditions. If the metric is effectively zero, remove it or redesign the scenario so that it is informative.

---

## 3.16 The manuscript does not yet demonstrate the value of the continuous stage

The paper itself concludes that direct CP-SAT is much faster:

- CP-SAT median: 2.9 ms;
- Full ConsistXApp median: approximately 85.1 ms.

The claimed justification for the continuous stage is then “diagnostic utility.” But no quantitative diagnostic-utility metric is given.

A residual/fractionality scatter plot is not sufficient to justify approximately 80 ms of overhead in a near-real-time pipeline.

### Required correction

Either:

1. remove the continuous stage from the main method and make it an optional diagnostic module; or
2. demonstrate measurable value, such as:
   - improved warm starts;
   - reduced repair-core size;
   - fewer CP-SAT branches;
   - better utility under very short solver budgets;
   - predictive identification of conflict classes;
   - lower churn;
   - better performance on larger instances where full CP-SAT struggles.

The strongest current method may actually be **GAC + explanation-guided repair**, not the full continuous pipeline.

---

# 4. Theoretical and algorithmic comments

## 4.1 Propositions 1–3 are correct but elementary

Decision soundness by post-verification and solution preservation under GAC are standard. They are useful for completeness of exposition but should not be presented as major theoretical innovations.

The constraint-programming literature already establishes the local nature of GAC and its solution-preserving filtering semantics [Yap et al., 2020](https://ojs.aaai.org/index.php/AAAI/article/view/7086/6940).

## 4.2 Proposition 4 appears mathematically correct

For the two-variable disequality example, the fixed point at \((1/2,1/2)\), Jacobian

\[
J=
\begin{bmatrix}
1 & -1\\
-1 & 1
\end{bmatrix},
\]

and eigenvalues \(0\) and \(2\) are correct.

However, it is an **unstable saddle**, not generally an attracting stall. It persists only under exact symmetry or a symmetry-preserving implementation. With seeded perturbations, the trajectory may leave this point.

The experimental section should therefore report sensitivity to:

- initialization noise;
- floating-point precision;
- tie-breaking;
- \(\alpha,\beta,\tau,\varepsilon\);
- update scheduling.

## 4.3 “Fractional fixed point” and “operational stall” must remain distinct

The manuscript acknowledges this distinction, but Section 7.4 contains the phrase:

> “mathematically, we refer to the non-converging state as a symmetry-preserving fractional fixed point”

A fixed point is stationary under the map. Calling it “non-converging” is confusing. Better wording:

> “The exact symmetric state is a fractional fixed point. Finite-precision trajectories are classified operationally as stalls when the residual is below a prescribed tolerance.”

## 4.4 The complexity discussion is too coarse

Equation (66) gives the cost of one explicit table scan, not necessarily the cost of establishing a GAC fixed point. Repeated revisions, queue scheduling, and explanation construction can require additional work.

State clearly whether the expression describes:

- one relation scan;
- one queue pass;
- one complete propagation call;
- or an amortized bound under support caching.

## 4.5 Explanation validity needs a formal proposition

The paper requires explanations to be valid but does not formally state or prove the condition under which the constructed tuple-blocking explanation entails unsupportedness.

A useful statement would be:

> If, for every tuple \(z\in R_c(i=a)\), the explanation contains at least one valid premise implying \(z_j\notin D_j\) for some \(j\), then the conjunction of the premises entails that \(a\) has no support in \(c\).

This would better connect the implementation’s explanation checker to the semantics.

## 4.6 The repair-core monotonicity result is correct but weak

Proposition 7 proves only termination of monotone expansion under the assumption that each failed iteration adds a new variable. It says nothing about:

- explanation quality;
- minimality;
- runtime;
- deadline feasibility;
- success before full expansion.

This proposition should not be used as evidence that explanation-guided expansion is efficient.

---

# 5. Novelty and related work

The paper’s novelty is primarily **architectural integration**, not a new GAC algorithm, explanation formalism, or exact-repair theory. The manuscript eventually states this, but the contribution claims should consistently reflect it.

The related-work section should be expanded to include:

- conflict-directed search;
- assumption-based unsatisfiable cores;
- explanation-based constraint programming;
- dynamic backtracking;
- model-based diagnosis;
- large-neighborhood search;
- relaxation-induced neighborhood search;
- conflict-guided repair;
- incremental and dynamic CSP algorithms beyond the single 1991 reference.

The current explanation literature is represented almost entirely by one survey. The cited survey confirms that explanation methods have a long history across constraint programming, SAT, diagnosis, and truth-maintenance systems [Dev Gupta et al., 2021](https://www.ijcai.org/proceedings/2021/601).

The manuscript therefore needs to explain specifically what is new about its repair-core construction relative to established explanation-guided neighborhood selection.

---

# 6. Reproducibility concerns

The paper promises a comprehensive artifact, but the provided text contains only:

> “[ANONYMIZED FOR DOUBLE-BLIND REVIEW]”

That is acceptable only if an anonymous supplementary artifact was actually provided to reviewers. Without it, the quantitative results cannot be verified.

The artifact should include:

- exact Python version;
- exact OR-Tools version;
- CPU model;
- physical/logical core count;
- number of CP-SAT workers;
- solver random seed;
- deterministic/non-deterministic settings;
- garbage-collection policy;
- warm-up procedure;
- timing source;
- model-construction time;
- verification time;
- all configuration files;
- raw logs;
- generated instance identifiers;
- immutable commit hash;
- one-command reproduction script.

CP-SAT is a sophisticated portfolio solver combining SAT, propagation, presolve, LP reasoning, and multiple search workers, so worker count and solver configuration materially affect timing [Perron et al., 2023](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CP.2023.3).

---

# 7. Presentation and language problems

The manuscript requires extensive proofreading and re-typesetting.

## 7.1 Corrupted sentences

Examples include:

- Page 2: “Open Radio Access Network introduces disaggregation, open interfaces, and pro- into radio access networks. grammable control”
- Page 2: “Each variable an accepted xApp action”
- Page 18: “a extitsymmetry-preserving fractional fixed point”
- Page 22: “The evaluation shows that are based exclu-sively…”
- Page 22: “incremental propagation 15.4 explanation-guided repair median core size of 4 variables and median latency of 45ms, and the complete pipeline 100”

The conclusion is incomplete and cannot remain in a submitted paper.

## 7.2 Duplicate bullets and text

Examples:

- Page 5 repeats the complete action list;
- Page 14 repeats “incremental support cache” and “propagation-explanation checker.”

## 7.3 Figure-caption mismatches

Figure 6 is captioned:

> “Distribution of final exact-repair core sizes.”

But the visible axes indicate:

> “Repair Success Rate vs. Initial Core Size.”

This must be corrected.

## 7.4 Table inconsistencies

- Table 6 formatting is not recoverable.
- Table 3 headers are misaligned.
- Table 4 contains ten methods, while Table 3 appears to contain nine.
- “GAC + expl repair” appears in Table 4 but is not clearly defined in Section 6.6.
- “ConsistXApp-legacy” and “VeriXApp” appear to be used inconsistently.

## 7.5 Reference formatting

References [10], [15], and [17] are badly formatted. Reference [17] should list the authors correctly as Laurent Perron, Frédéric Didier, and Steven Gay, consistent with the published record.

Reference [7] needs complete publication details rather than only a title and year.

## 7.6 Title

The title is technically informative but too long. A more concise alternative would be:

> **Consistency-Guided xApp Coordination in O-RAN: Incremental Propagation and Explanation-Based Exact Repair**

“Fractional-stall diagnosis” can remain in the abstract.

---

# 8. Required revision plan

I recommend the following sequence rather than piecemeal editing.

## Phase 1: Rebuild the experiment outputs

1. Freeze the method definitions.
2. Define every outcome category formally.
3. Regenerate all tables from raw logs.
4. Add automated consistency checks:
   - outcome percentages sum to 100%;
   - pooled counts match tables;
   - all forwarded decisions pass verification;
   - incremental and recomputed domains agree;
   - solver statuses are valid.
5. Recompute the abstract only after all tables are final.

## Phase 2: Simplify the paper’s central claim

The defensible claim is:

> Observable incremental GAC and explanation-guided localization provide auditable filtering and diagnosis for finite-domain xApp coordination, although direct CP-SAT is faster on the evaluated small and medium instances.

This is a credible and useful result. The manuscript should not imply runtime superiority where none is shown.

## Phase 3: Strengthen the explanation-guided comparison

Use more repair-triggering instances and report paired:

- core-size reduction;
- latency;
- solver work;
- escalation;
- deadline success.

## Phase 4: Clarify the role of continuous inference

Treat it as either:

- an optional diagnostic component; or
- a quantitatively justified coordination stage.

At present, it dominates latency without demonstrating sufficient benefit.

## Phase 5: Add one realistic O-RAN validation case

A trace-driven or emulated case would substantially improve the paper. It should show how actual xApp outputs become finite-domain relations.

## Phase 6: Rewrite the results and conclusion

The conclusion must be reconstructed from verified numbers. Do not edit its current corrupted paragraph manually.

---

# 9. Final assessment

### Scientific idea

**Promising**

### Mathematical correctness

**Mostly sound, but largely based on standard CP properties**

### Experimental design

**Potentially adequate in scope, insufficiently documented**

### Experimental reporting

**Currently unreliable because of contradictions and formatting failures**

### O-RAN relevance

**Plausible, but validation remains predominantly synthetic**

### Reproducibility

**Cannot be judged without the promised artifact**
