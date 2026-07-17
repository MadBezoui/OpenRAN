
# Second-Round Review (autoreview)


## 1. Overall assessment

This revision addresses several important weaknesses identified previously. In particular, it now:

- qualifies the comparison as applying to the **two evaluated re-solve strategies**;
- describes the repair certificate more accurately as an **auditable trace** that does not prove minimality or optimality;
- defines \(C_{r+1}\) in Equation (8);
- clarifies the status of failures in the fixed-core ablation;
- corrects the cold-start seed count to twenty;
- states that 20 variables is the **median** full-model size;
- explains why mixed transitions dominate the dynamic schedule;
- improves the description of local exactness;
- adds the XAI4C DOI;
- clarifies Algorithm 2’s full-scope iteration.

These are meaningful improvements. The paper is technically strong, unusually transparent about negative results, and potentially valuable to both the O-RAN and constraint-programming communities.

Nevertheless, several issues remain before acceptance. The most important are:

1. fallback behaviour is logically inconsistent with full-model infeasibility;
2. the 100 ms deadline remains post-hoc rather than operationally enforced;
3. baseline and objective definitions remain ambiguous;
4. the central experimental evidence remains strongly dependent on planted-feasible synthetic models;
5. the repair decoder is still compared mainly against weak per-variable proposals;
6. some sequential latency results do not fully support the stated scaling explanation.

---

# 2. Important improvements in this revision

## 2.1 Better qualification of the re-solve comparison

The new wording:

> “five times faster in the median than either evaluated re-solve strategy”

is appropriately precise. It avoids implying that all possible incremental or persistent solver strategies were evaluated.

## 2.2 Better characterization of the repair certificate

The added statement on page 6 is excellent:

> “Replaying the record establishes that the decoded candidate violated the listed relations, that each expansion was justified by its recorded source, and that the final assignment satisfies every registered hard constraint; it is an auditable trace and does not by itself certify core minimality or objective optimality.”

This resolves the earlier overstatement. I recommend using **“audit certificate”** or **“replayable repair trace”** consistently, but the present explanation is scientifically acceptable.

## 2.3 Improved local-repair terminology

The revised sentence:

> “Local repair exactly determines feasibility under its current boundary but does not optimize the full model”

is much more precise than the previous formulation. The conditional-completeness discussion is also clear.

## 2.4 Repair-ablation semantics are now clearer

The explanation that fixed-core failures are infeasible boundary-conditioned subproblems—not globally infeasible instances—is important and should remain.

## 2.5 Reproducibility inconsistencies corrected

The cold-start suite and Figure 4 now consistently report twenty seeds per size. Similarly, “a median of 20 variables” correctly replaces the earlier implication that all full models had exactly 20 variables.

---

# 3. Remaining major issues

## 3.1 Full-model infeasibility cannot lead to a verified fallback

This is now the most important logical issue.

Algorithm 2, line 6 states:

> “if \(A_r=A\) (the last solve was the complete model) or the deadline has passed then return fallback”

This is incorrect if the complete model has been proved infeasible. A registered fallback is itself an assignment in the current model and must satisfy the same hard constraints. Therefore:

- if the complete hard model is infeasible, no fallback can pass the verifier;
- if a fallback passes the verifier, then the complete model was feasible;
- fallback is meaningful after a timeout or incomplete local search, but not after a conclusive proof that the full registered model is infeasible.

The current algorithm conflicts with the definition of blocked decisions in Table 2 and with Proposition 3.

### Required correction

Algorithm 2 must distinguish at least four statuses:

1. **FEASIBLE/OPTIMAL:** verify and return the solution;
2. **INFEASIBLE on a proper core:** expand the core;
3. **INFEASIBLE on the full model:** report the registered model as infeasible and return **blocked**;
4. **UNKNOWN/deadline:** attempt a registered fallback, verify it, and return either:
   - verified fallback, or
   - blocked if the fallback fails verification.

A better line 6 would be:

> If \(A_r=A\) and the complete model is proven infeasible, return blocked; if the deadline expires or the solver returns UNKNOWN, verify the registered fallback and return it if accepted, otherwise return blocked.

This distinction should also be reflected in Sections 4.3, 6.2, and 8.

---

## 3.2 Deadline handling is still not operational

The manuscript explicitly states that the 100 ms threshold is post-hoc and non-preemptive. This is honest, but it means the system is not currently a deadline-enforcing coordination pipeline.

The inconsistency appears in several places:

- Section 4.3 says repair terminates “at the deadline”;
- Algorithm 2 checks whether “the deadline has passed”;
- Section 6.2 says that an overrunning stage is allowed to complete;
- Table 9 reports \(p_{99}=137.8\) ms in one configuration;
- no sequential deadline-compliance or fallback count is reported.

Thus, the implementation detects an exceeded budget only after an indivisible stage finishes. That is not equivalent to producing a verified decision within the deadline.

### Required correction

Either:

#### Option A — Implement actual deadline handling

- pass the remaining budget to CP-SAT;
- check the budget before every expansion;
- reserve time for verification and fallback;
- stop before the deadline;
- verify the fallback;
- report optimized/fallback/blocked counts.

This is the preferred solution.

#### Option B — Narrow the claims

If operational deadline enforcement is left for future work, replace terms such as:

- “budget-aware coordination loop”;
- “repair terminates at the deadline”;
- “under the control budget”;

with:

- “latency-measured coordination loop”;
- “post-hoc deadline-compliance evaluation”;
- “repair checks the budget at stage boundaries.”

The abstract should also avoid implying a hard deadline guarantee.

### Additional reporting needed

For the sequential suite, add:

- percentage completed within 100 ms;
- number of verified fallbacks;
- number blocked;
- maximum latency;
- latency including fallback verification.

At present, “100% verified feasibility” does not imply “100% deadline compliance.”

---

## 3.3 Algorithm 2 is inconsistent with the default explanation variant

Algorithm 2, line 4 states:

> “solve the induced subproblem with CP-SAT (boundary fixings as assumptions)”

However, Section 4.3 states that the default explanation variant fixes boundary variables using **plain equality constraints**, while only the assumption-core variant uses assumptions.

Therefore, Algorithm 2 describes the assumption-core variant, not the general or default ConsistXApp method.

### Required correction

Write:

> Solve the induced subproblem with CP-SAT, using plain boundary equalities in the explanation-guided variant and reified assumptions in the assumption-core variant.

Alternatively, provide two explicit algorithm branches.

This matters because the source of expansion and the measured runtime differ substantially between variants. Table 7 shows the assumption variant is much slower than the explanation-guided variant.

---

## 3.4 Solver outcomes and lexicographic optimality remain underspecified

Algorithm 2 uses the word **“solved”**, which is ambiguous. CP-SAT may return:

- `OPTIMAL`;
- `FEASIBLE`;
- `INFEASIBLE`;
- `UNKNOWN`;
- `MODEL_INVALID`.

For feasibility-only core extraction, `FEASIBLE` may be sufficient. For lexicographic optimization, however, `FEASIBLE` does not certify that the boundary-conditioned objective was optimized.

The manuscript states that the repair objective is lexicographic but does not explain how it is implemented.

### Required details

Specify:

1. whether the lexicographic objective is implemented through:
   - repeated solves;
   - hierarchical optimization;
   - or weighted scalarization;
2. how coefficient domination is guaranteed if scalarization is used;
3. what happens at cold start when no previous verified decision exists;
4. how ties are resolved;
5. whether utilities are integer-valued or scaled;
6. which CP-SAT status is accepted at each stage;
7. whether “exact optimum” means `OPTIMAL` was returned on every instance;
8. solver time limits and worker count;
9. random seed and deterministic-search settings;
10. treatment of `MODEL_INVALID`.

The claims of “deterministic” expansion also require clarification when an assumption core is returned by CP-SAT. Unless the solver is configured deterministically, repeated runs may return different sufficient cores.

---

## 3.5 Baseline definitions remain ambiguous

Section 6.2 says:

> “ConsistXApp and the solver baselines use the deterministic utility decode”

This is unclear for complete CP-SAT. A complete solver generally does not need a utility decode unless that vector is:

- used as a solution hint;
- used as a preferred-request objective;
- used to classify the result;
- or used as the initial candidate before full repair.

The output counts in Table 5 are also difficult to interpret. For example, complete CP-SAT appears to have no direct decode or repair category, which is reasonable, but then the statement that it “uses” the utility decode needs explanation.

### Required correction

Provide a compact method-definition table with columns such as:

| Method | Initial candidate | GAC | Search scope | Boundary | Objective | Hint | Verifier |
| ------ | ----------------- | --: | ------------ | -------- | --------- | ---- | -------: |

In particular, distinguish:

- feasibility-only complete CP-SAT;
- lexicographic complete CP-SAT;
- kept-request optimizing CP-SAT;
- GAC + CP-SAT;
- explanation-guided repair;
- assumption-core repair;
- QACM-inspired objective;
- bargaining-inspired objective.

It must be clear whether the 1.8 ms versus 2.8 ms comparison involves methods solving the same objective or only producing any verified feasible solution.

If they solve different objectives, the paper should say that the latency comparison concerns **verified feasibility generation**, not equivalent optimization.

---

## 3.6 Candidate-generation baselines remain too weak

The main decoder independently selects the best value for each variable and achieves only 2 feasible assignments out of 250. This demonstrates the need for coordination, but it is a weak computational baseline.

A simple conflict-aware greedy procedure could potentially improve direct feasibility and reduce the need for repair. Examples include:

- sequential assignment with forward checking;
- greedy utility selection with immediate hard-constraint checks;
- min-conflicts;
- bounded local search;
- greedy repair by lowest utility loss.

Without such a baseline, the paper shows convincingly that repair beats independent decoding, but not necessarily that the proposed repair pipeline beats inexpensive conflict-aware heuristics.

### Required experiment

Add at least one lightweight conflict-aware decoder under the same timing and verification harness. Report:

- direct verified feasibility;
- repair frequency;
- total latency;
- kept-request rate;
- number of modified variables;
- final core size.

This would substantially strengthen the operational contribution.

---

## 3.7 External validity remains limited

The paper’s principal experiments still use planted-feasible synthetic table constraints. The drift variant is useful, but it remains planted by construction.

The limitations section acknowledges this appropriately, but the central claims should be interpreted within that setting.

### Preferred additional experiment

Add at least one of:

1. non-planted satisfiable instances generated independently and filtered after generation;
2. a mixed feasible/infeasible benchmark near a phase transition;
3. trace-driven relation generation;
4. one closed-loop emulated O-RAN scenario;
5. a systematic sensitivity study over:
   - tightness;
   - arity;
   - graph density;
   - domain size;
   - clustering;
   - feasible-region size.

At minimum, quantify how the planted structure affects difficulty:

- number of feasible assignments for small instances;
- Hamming distance from the candidate to the nearest feasible solution;
- Hamming distance between consecutive planted anchors;
- Hamming distance from the previous verified decision to the new feasible region.

---

## 3.8 Sequential results need deeper explanation

The narrative says full re-solve cost does not depend on the change fraction. However, Table 9 reports:

- 25.6 ms for CP-SAT at \(2\%\), \(n=1000\);
- 18.3 ms for CP-SAT at \(10\%\), \(n=1000\).

Likewise, incremental median repair is:

- 4.9 ms at \(2\%\);
- 4.5 ms at \(10\%\),

although its \(p_{95}\) becomes much worse.

These values are not necessarily contradictory—the generated relations may have different empirical difficulty—but they do not directly support a simple monotonic relationship between latency and change fraction.

Similarly, the statement:

> “incremental repair scales with the number of violated relations”

is plausible but not demonstrated by the reported aggregate table.

### Required analysis

Report, by size and change rate:

- number of changed relations;
- number of initially violated relations;
- initial core size;
- final core size;
- number of expansions;
- model-construction time;
- propagation time;
- repair-solver time;
- verifier time;
- previous-decision survival rate.

A regression or correlation analysis between latency and:

- number of violations;
- final core size;
- number of released variables;
- number of expansions

would provide direct evidence for the claimed mechanism.

A safer present formulation would be:

> Incremental repair is intended to scale with the affected neighbourhood and observed violations; empirically, it avoids rebuilding and searching the complete model.

---

# 4. Additional methodological concerns

## 4.1 Objective-quality results need fuller distributional reporting

The mean gap is 10.8 percentage points, with a maximum of 40 points. This is important and should not be summarized only by the mean.

Please add:

- median gap;
- interquartile range;
- per-scenario gap;
- \(p_{90}\) or \(p_{95}\);
- distribution plot;
- number of instances with gaps exceeding 5, 10, 20, and 30 points.

A 40-point worst case may be operationally significant.

## 4.2 End-to-end results should be reported per scenario

Table 4 reports propagation by scenario, but the principal feasibility, latency, and objective results are pooled over 250 instances.

Please report at least:

- median and \(p_{95}\) latency per scenario;
- repair rate per scenario;
- final core size per scenario;
- objective gap per scenario.

This would show whether S5 or another scenario dominates the aggregate results.

## 4.3 Tail estimates are based on relatively few episodes

Ten episodes per configuration are adequate for a preliminary paired test, but estimates such as \(p_{99}\) are sensitive with 300 temporally dependent epochs.

Consider:

- hierarchical bootstrap by episode;
- confidence intervals for tail percentiles;
- per-episode \(p_{95}\) and maximum;
- more episodes for \(n=1000\).

## 4.4 KPI comparison should avoid interpreting overlapping confidence intervals as “no difference”

The statement:

> “the intervals of ConsistXApp and complete CP-SAT overlap”

does not establish equivalence or absence of a difference. Overlapping separate confidence intervals are not a formal equivalence test.

Use:

> “The pooled KPI estimates are similar, and no inferential claim of superiority or equivalence is made.”

If “no material degradation” is intended, define a practical equivalence margin and perform a paired equivalence analysis.

## 4.5 KPI computation error requires diagnosis

One verified S5 decision caused a KPI-computation error. This is potentially important because the verifier accepted the decision.

Clarify:

- the cause of the error;
- whether it indicates an undefined pseudo-physical state;
- why the state was not excluded by a hard relation;
- whether the verifier should reject such states;
- whether the error can recur.

A verified assignment that cannot be evaluated by the network model may reveal a mismatch between the constraint model and KPI semantics.

---

# 5. Formal and terminology comments

## 5.1 “The verifier accepts exactly \(F(s^t)\)” is stronger than the evidence

Section 4.4 states that the verifier:

> “accepts exactly the set \(F(s^t)\).”

This is its intended specification. The validation gates provide strong empirical evidence but not a proof for all possible inputs.

Prefer:

> “The verifier is specified to accept exactly the set…”

or:

> “The verifier directly checks membership in the set…”

## 5.2 “Expansion order is deterministic”

This should be qualified:

- explanation-guided frontier expansion may be deterministic;
- solver assumption cores may vary unless solver execution is deterministic.

Suggested wording:

> “The frontier and explanation-based expansion rules use a deterministic tie-breaking order; reproducibility of solver-derived assumption cores additionally depends on the CP-SAT configuration.”

## 5.3 Positive-table scope

The complexity discussion correctly refers to positive tables. The abstract and contributions could state more explicitly that the evaluated implementation is based on explicit positive-table relations.

## 5.4 “Approximately half” is now appropriate

The revised wording is correct: 11 variables compared with a median full scope of 20 is approximately half, not exactly half.

---

# 6. Presentation and typesetting

## 6.1 Equations are still visibly malformed

The extracted PDF shows serious notation problems in Sections 3 and 4, including:

- the domain definition on page 3;
- tuple projection notation on page 4;
- objective constraints in Equations (4)–(5);
- support-set notation in Equation (6);
- reduction-ratio definitions on page 9;
- misplaced proof-end symbols.

Some of these may result from text extraction, but the source PDF should be inspected carefully.

The intended notation should resemble:

\[
D_i^t=\{a_{i,1}^t,\ldots,a_{i,d_i}^t\},\qquad x_i^t\in D_i^t,
\]

\[
R_c(s^t)\subseteq \prod_{i\in S_c}D_i^t,
\]

\[
x_{S_c}^t\in R_c(s^t),
\]

and

\[
r_D=1-\frac{\sum_i |D_i^\ast|}{\sum_i |D_i|}.
\]

## 6.2 Table 5 is difficult to read

The column alignment is currently problematic. The table should be reformatted, possibly in landscape orientation or split into:

1. outcome counts;
2. latency and compliance.

## 6.3 Table 7 strategy labels

The extracted table makes it difficult to align:

- strategy;
- success;
- core size;
- expansion source;
- release count;
- latency.

Please visually verify the final typesetting.

## 6.4 Abstract grammar

The sentence:

> “expanding repair cores succeed where fixed cores fail”

is grammatically valid because the subject is plural. However, for consistency with the past-tense reporting of completed experiments, I recommend:

> “expanding repair cores succeeded where fixed cores failed in 8.5% of cases.”

More precise still:

> “expanding strategies repaired all 248 candidates, whereas fixed violated-scope cores failed on 21 cases (8.5%).”

## 6.5 “Input-mutation” line breaking

Avoid the awkward hyphenation “input- mutation” in the abstract.

---

# 7. References

The XAI4C DOI has been added correctly. The following still need attention:

- Reference [9] lacks DOI, pages, location, and full proceedings details.
- Reference [12] lacks pages and DOI.
- Reference [11] should include volume and page/article numbers if available.
- Reference [18] contains the unusual trailing phrase “Using OR-Tools v9.11,” which appears to be an annotation rather than part of the citation.
- Reference [19] uses an old access date despite experiments using OR-Tools 9.14 and 9.15. Update the documentation access date.
- Standardize capitalization:
  - xApps;
  - Open RAN;
  - AI/ML;
  - SDK;
  - SD-RANs;
  - PAWR.

---

# 8. Minimum revisions required for acceptance

I recommend requiring the following:

1. Correct Algorithm 2’s treatment of full-model infeasibility, timeout, fallback, and blocked outcomes.
2. Resolve the mismatch between assumption-based and equality-based boundary fixing in Algorithm 2.
3. Fully specify CP-SAT statuses, settings, determinism, time limits, and lexicographic-objective implementation.
4. Clarify all baseline objectives and initial candidates in a method-definition table.
5. Add at least one conflict-aware lightweight decoder or heuristic baseline.
6. Either enforce deadlines operationally or narrow the deadline-related claims.
7. Report sequential deadline compliance, fallback counts, and blocked counts.
8. Explain the non-monotonic latency results across \(2\%\) and \(10\%\) changes.
9. Add core/violation statistics supporting the claimed source of amortized scaling.
10. Report principal results per scenario.
11. Diagnose the verified assignment that caused a KPI-computation error.
12. Strengthen external validity or explicitly narrow the central claim to planted-feasible synthetic models.
13. Correct the remaining equation, table, and reference formatting issues.
