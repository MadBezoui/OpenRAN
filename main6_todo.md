
# Detailed revision plan to revise `main6`

## Executive assessment

`main6` already has a strong scientific foundation. Its principal strengths are:

- a clearly scoped registered-model guarantee;
- an independently implemented forwarding verifier;
- replayable repair traces;
- honest negative results;
- strong experimental breadth;
- appropriate separation between feasibility and optimality;
- explicit limitations concerning physical-RAN safety and real-time guarantees.

the manuscript needs improvement in four areas:

1. **Eliminate all visible production and notation defects.**
2. **Make the central contribution unmistakable and avoid potentially overstated terminology.**
3. **Strengthen experimental fairness, reproducibility, and statistical presentation.**
4. **Reduce secondary material and sharpen the verifier–auditability narrative.**

The following plan is ordered by priority.

---

# Phase 1 — Correct all submission-blocking defects

These corrections are mandatory. The manuscript should not be submitted before they are fixed.

## 1.1 Repair the broken Related Work paragraph

### Current problem

On page 3, the phrase “Dynamic constraint satisfaction” has been separated from its sentence:

> studies sequences of related problems and the incremental maintenance of consistency.

The rendered result appears grammatically incomplete.

### Required replacement

Use one continuous paragraph:

> **Dynamic constraint satisfaction studies sequences of related problems and the incremental maintenance of consistency. A line of work descending from DnAC-4 [16] maintains per-value justifications so that, after a constraint retraction, only a limited set of previously removed values must be reconsidered. AC|DC [17] and DnAC-6 [18] refine this approach with reduced space or time overheads.**

I recommend “a limited set” rather than “only a minimal set” unless reference [16] formally establishes set minimality under the exact meaning intended.

### Verification

Check the final PDF visually, not only the LaTeX source, because this may result from a floating heading or malformed command.

---

## 1.2 Remove the duplicated method list

### Current problem

On page 12, the following methods are listed twice:

- continuous-relaxation variants;
- fixed violated-scope repair;
- radius-based repair;
- frontier repair;
- explanation-guided repair;
- assumption-core repair;
- full-scope repair;
- QoS and bargaining baselines;
- candidate generators.

The second list also ends with an incomplete “and”.

### Required action

Retain one clean list only. Group the methods by role:

> The evaluation includes four groups of methods:
>
> 1. **Sanity-check policies:** uncoordinated proposals and static priority;
> 2. **Complete coordination baselines:** complete CP-SAT and GAC followed by complete CP-SAT;
> 3. **Repair variants:** fixed violated-scope, radius-based, frontier, explanation-guided, assumption-core, and full-scope repair;
> 4. **Alternative candidate and objective mechanisms:** continuous relaxation, QoS-inspired optimization, Nash-social-welfare optimization, greedy checking, min-conflicts, and forward checking.

This grouped presentation is easier to understand than a long flat list.

---

## 1.3 Correct the broken conclusion

### Current problem

The conclusion contains:

> “several operational boundaries remain.”
> “However,”

in the wrong order.

### Required replacement

> **However, several operational boundaries remain. Cold-start instances are better served by complete solving; local repair trades objective quality for speed; and the observed median advantages do not constitute hard real-time guarantees.**

Also replace:

> “physical O-RAN emulation platforms”

with:

> **O-RAN emulators and experimental testbeds**

or:

> **closed-loop O-RAN emulation platforms and physical testbeds.**

---

## 1.4 Correct the Proposition 1 signature

### Current problem

The verifier’s type is rendered incorrectly:

> \(V_t : \prod_i \to \{accept,reject\}_i D_i^t\)

### Required notation

Use:

\[
V_t:\prod_{i\in A_t}D_i^t\rightarrow
\{\mathrm{accept},\mathrm{reject}\}.
\]

If the verifier can also reject malformed or incomplete assignments, its actual input space is broader than the product of the domains. In that case, define an input representation space \(\mathcal{X}_t\):

\[
V_t:\mathcal{X}_t\rightarrow
\{\mathrm{accept},\mathrm{reject}\},
\]

where valid complete assignments form a subset of \(\mathcal{X}_t\).

This second definition better accommodates tests for:

- missing variables;
- out-of-domain values;
- stale contexts;
- malformed representations.

---

## 1.5 Correct Algorithm 2, Step 11

### Current problem

Step 11 states:

> “If the budget expires with a verified feasible incumbent…”

However, the independent verification phase occurs only in Step 12. At Step 11, the incumbent has not yet been independently verified.

### Required replacement

> **If the remaining optimization budget expires after the solver has produced a feasible incumbent but before all lexicographic levels are certified, mark the result as `FEASIBLE-NOT-CERTIFIED` and submit the incumbent to the independent verifier.**

This is a small but scientifically important correction.

---

## 1.6 Fix bullet and heading collisions

Visually inspect and correct:

- G2/G3 bullet collision on page 9;
- Section 7.7 and Section 7.8 heading placement;
- Section 8.7 heading formatting;
- Table 9’s “episodes” label;
- the ordering around Section 8.1, where the model-version paragraph appears separated;
- page 14 figure and table placement;
- mathematical equations split across columns.

These may partly be extraction artifacts, but the submitted PDF itself must be checked at 100%, 150%, and print scale.

---

# Phase 2 — Refine the title and central claim

## 2.1 Decide whether to retain “Verified”

The current title is strong:

> **Verified and Auditable Multi-xApp Arbitration in the Near-RT RIC: Registered-Model Guarantees and the Limits of Incremental Repair**

However, “Verified” may be interpreted as formal software verification. The manuscript provides:

- an architectural proposition conditional on verifier correctness;
- differential testing;
- exhaustive testing over small instances;
- property-based testing;
- mutation-based input testing.

It does not provide a machine-checked proof of the verifier implementation.

### Safest recommended title

> **Verifier-Gated and Auditable Multi-xApp Arbitration in the Near-RT RIC: Registered-Model Guarantees and the Limits of Incremental Repair**

### Alternative

> **Auditable Multi-xApp Arbitration in the Near-RT RIC with Registered-Model Verification and Incremental Repair**

### Recommendation

Use **“Verifier-Gated”** if the target venue is strict about formal verification terminology. Retain “Verified” only if the introduction immediately defines it as “accepted by the registered-model verifier,” not “formally verified software.”

---

## 2.2 Replace “repair certificate” or define it more carefully

The word “certificate” may suggest a proof object sufficient to establish correctness independently of trusted software. Your object appears to be primarily:

- a replayable audit trace;
- a record of violation witnesses;
- an expansion log;
- a final assignment;
- a verifier outcome.

### Recommended terminology

Use one of:

- **replayable repair certificate**, with an explicit definition;
- **replayable arbitration certificate**;
- **audit certificate**;
- **replayable repair trace**.

The safest formulation is:

> **Each non-trivial arbitration emits a replayable audit certificate containing sufficient information to reconstruct the initial violations, validate each recorded core expansion, and recheck final registered-model feasibility. The certificate does not prove minimum-core size, solver correctness, or global objective optimality.**

This preserves the strong auditability claim without implying more than the artifact contains.

---

## 2.3 Sharpen the paper’s one-sentence contribution

At the end of the first introductory paragraph, state the exact problem boundary:

> **This paper addresses the post-registration arbitration problem: given finite action domains and registered hard relations, construct and audit a joint action such that no assignment violating the current registered model version is admitted to the E2 control path.**

Then state the contribution in one sentence:

> **The central contribution is a verifier-gated arbitration architecture with model-version binding and replayable audit certificates; incremental GAC and expanding local repair are upstream mechanisms for generating acceptable candidates efficiently.**

This makes clear that:

- verification and auditability are central;
- GAC and CP-SAT repair are supporting mechanisms;
- the paper does not claim a new GAC algorithm.

---

# Phase 3 — Rewrite the abstract for maximum precision

## 3.1 Problems in the current abstract

The abstract is strong but can be improved in four ways:

1. “every forwarded outcome” may sound like deployment evidence;
2. “verified” remains potentially ambiguous;
3. the exact baseline scope should be explicit;
4. the objective-quality cost should be briefly acknowledged.

## 3.2 Recommended abstract

> **Independently developed xApps may issue concurrent control requests that are mutually incompatible or violate registered service-level constraints. We formulate multi-xApp arbitration in the Near-RT RIC as a dynamic finite-domain constraint problem and present ConsistXApp, a verifier-gated pipeline that binds each decision to a registered model version and emits a replayable audit certificate for every repair. Upstream, incremental generalized arc consistency removes unsupported values, while invalid candidates are repaired by solving expanding local subproblems guided by propagation explanations, solver infeasibility cores, or a deterministic graph frontier. Across four validation gates comprising 680,450 checks, the production verifier exhibited zero observed divergence from independently implemented references. On 250 generated static instances representing five O-RAN conflict scenarios, every verifier-accepted outcome satisfied all registered hard constraints. The latency benefit was amortized rather than absolute: under 2% sequential relation updates, repair of the previous accepted decision required median per-epoch latencies of 0.05–4.9 ms for 100–1,000 variables, compared with 2.8–25.6 ms for the evaluated Python CP-SAT rebuild-and-resolve baseline. The advantage narrowed near the pooled p95, reversed at the descriptive pooled p99, and disappeared on cold starts. Local repair also reduced objective quality relative to complete optimization. All guarantees are conditional on the correctness and completeness of the registered constraint model and do not establish physical-RAN safety or hard real-time schedulability.**

This version is more resistant to reviewer criticism.

---

# Phase 4 — Strengthen the formal section

## 4.1 Separate Proposition 2 into three results

The current Proposition 2 combines:

- solution preservation;
- monotone expansion and conditional completeness;
- restoration after relaxation.

These are logically distinct and deserve separate statements.

### Proposed structure

#### Proposition 2 — GAC solution preservation

\[
x\in F(s_t)\Longrightarrow
x_i\in D_i^*,\quad \forall i\in A_t.
\]

#### Proposition 3 — Monotone repair-core expansion

\[
A_0\subseteq A_1\subseteq\cdots\subseteq A_t.
\]

Include the expansion bound:

\[
\text{at most } |A_t|-|A_0|
\text{ strict expansions}.
\]

#### Proposition 4 — Conditional completeness at full scope

State the conditions explicitly:

- finite domains;
- exact relation encoding;
- no omitted active hard constraints;
- full core reached;
- solver complete for the encoded model;
- conclusive solver status before the limit.

#### Proposition 5 — Necessity of restoration after relaxation

Keep the short counterexample or proof.

### Benefit

This improves readability, citation precision, and reviewer confidence.

---

## 4.2 Define all operators used in core expansion

The manuscript uses terms such as:

- \(\operatorname{VarLit}\);
- \(E_\emptyset^r\);
- \(C_{r+1}\);
- boundary variables;
- frontier expansion.

Define each one before the equations.

For example:

> Let \(\operatorname{VarLit}(E)\) denote the set of variables appearing in temporary restriction literals or boundary decisions contained in explanation \(E\).

Define the deterministic frontier exactly:

- adjacency through a constraint graph;
- ordering of constraints;
- tie-breaking rule;
- whether one layer or one constraint is added per iteration.

Without this, certificate replay is not fully reproducible.

---

## 4.3 Make the model-version transaction explicit

Proposition 1 currently assumes that the model version does not change between verification and forwarding. Explain how this can be implemented.

Add a short operational requirement:

> **A production implementation must treat model lookup, verifier execution, acceptance recording, and forwarding authorization as a version-bound transaction. If the active version changes before forwarding, the authorization token is invalidated and the candidate is re-verified.**

A compact state machine would help:

1. load \(\nu_t\);
2. generate candidate under \(\nu_t\);
3. verify under \(\nu_t\);
4. atomically compare current version with \(\nu_t\);
5. forward or restart.

This makes the TOCTOU requirement operational rather than purely assumed.

---

## 4.4 Add a concise certificate validity definition

Define when a certificate is valid.

A certificate \(\pi\) is valid for \((M_t,\nu_t)\) if:

1. its model and context identifiers match \((M_t,\nu_t)\);
2. the listed initial violations are reproducible;
3. every expansion follows the declared explanation, assumption-core, or frontier rule;
4. all released variables are recorded;
5. the final assignment is complete and domain-valid;
6. every registered hard relation is satisfied;
7. the verifier outcome and forwarded assignment match.

Then explicitly state:

> Certificate validity establishes replayable registered-model feasibility and trace consistency. It does not establish solver optimality, physical-network safety, or completeness of the registered model.

---

## 4.5 Add one complete certificate example

Extend the worked example with a minimal certificate:

```text
model_version: ν17
candidate: (high, sleep)
violated_relation: R12
initial_core: {x1, x2}
expansion_trace: none
final_assignment: (high, on)
solver_status: OPTIMAL
verifier_status: ACCEPT
```

Then show how replay checks:

\[
(high,sleep)\notin R_{12},
\qquad
(high,on)\in R_{12}.
\]

This would make the auditability contribution concrete.

---

# Phase 5 — Clarify the algorithmic pipeline

## 5.1 Separate candidate generation, repair feasibility, optimization, and verification

The manuscript currently contains these stages, but their boundaries should be unmistakable.

Use the following four-stage formulation:

1. **Candidate generation:** GAC plus decoder or previous accepted decision.
2. **Repair feasibility:** expanding core with objective-free CP-SAT.
3. **Operational optimization:** sequential lexicographic optimization over the retained core.
4. **Independent verification:** full registered-model membership test.

This avoids confusion between:

- finding a feasible core;
- optimizing within that core;
- certifying optimality;
- verifying hard feasibility.

---

## 5.2 Clarify the meaning of solver statuses

Add a small table:

| Status         | Permitted conclusion                                                  |
| -------------- | --------------------------------------------------------------------- |
| `OPTIMAL`    | Feasible and optimal for the current encoded objective                |
| `FEASIBLE`   | Feasible incumbent; optimality not established                        |
| `INFEASIBLE` | Infeasible only for the current encoded model and boundary conditions |
| `UNKNOWN`    | No feasibility or infeasibility conclusion                            |

Also state:

> `INFEASIBLE` on a proper repair core does not imply that the complete registered model is infeasible.

This point already exists, but a status table will make it immediately visible.

---

## 5.3 Define fallback behaviour completely

Specify:

- whether a fallback is mandatory or optional;
- what happens if no fallback is registered;
- whether fallback lookup is version-specific;
- whether fallback validation can be cached;
- when cached validation becomes invalid;
- whether an already accepted fallback must be available before the deadline.

Recommended statement:

> **A fallback is a version-specific candidate policy, not an exemption from verification. If no fallback is registered, or if the registered fallback fails verification under the current model version, the outcome is `BLOCKED`.**

---

# Phase 6 — Improve experimental fairness and reproducibility

This phase is essential for reaching 9.5/10. The most likely substantive reviewer criticism concerns baseline fairness.

## 6.1 Resolve the “28 workers” ambiguity

Table 3 currently mixes:

- Windows multiprocessing processes;
- CP-SAT search workers;
- machine core count.

Replace “Workers” with two columns:

| Campaign        | Parallel experiment processes | CP-SAT`num_search_workers` | Seed policy               | Solver limit  |
| --------------- | ----------------------------: | ---------------------------: | ------------------------- | ------------- |
| Static          |                            28 |                  exact value | non-fixed or exact policy | exact value   |
| Dynamic         |                            28 |                  exact value | non-fixed or exact policy | exact value   |
| Repair ablation |                             1 |                            1 | deterministic             | 100 ms shared |
| Sequential      |                             1 |                            1 | deterministic             | 100 ms shared |

Do not use “default” if the actual value can be extracted from logs.

---

## 6.2 Define every latency boundary

For each reported latency, state whether it includes:

- instance update;
- model reconstruction;
- GAC propagation;
- candidate decoding;
- repair-core expansion;
- CP-SAT construction;
- CP-SAT search;
- solution extraction;
- certificate construction;
- independent verification;
- serialization;
- E2 communication.

A recommended decomposition is:

\[
T_{\mathrm{pipeline}} =
T_{\mathrm{update}}+
T_{\mathrm{prop}}+
T_{\mathrm{decode}}+
T_{\mathrm{repair}}+
T_{\mathrm{verify}}.
\]

Report separately:

\[
T_{\mathrm{repair}}=
T_{\mathrm{model-build}}+
T_{\mathrm{solve}}+
T_{\mathrm{extract}}.
\]

### Critical issue

The manuscript says that verification is measured separately, while some tables are called “end-to-end outcomes.” Clarify whether the stated 1.8 ms and 0.05–4.9 ms include verification.

If they exclude verification, do not call them end-to-end latency. Use:

> computational coordination latency, excluding certificate serialization and E2 transport.

---

## 6.3 Strengthen the complete-solver baseline

The current comparison is correctly limited to a Python rebuild-and-resolve baseline. Nevertheless, this remains the largest threat to the systems conclusion.

### Minimum improvement

Add a decomposition showing:

- Python model construction;
- solver execution;
- extraction;
- verification.

This is partly present for \(n=1000\), but it should be reported across all sizes.

### Strong improvement

Add at least one more competitive baseline:

- a carefully engineered cached model-construction baseline;
- an incremental or persistent solver if compatible with relation updates;
- a large-neighbourhood CP-SAT baseline centred on the previous decision;
- a CP-SAT neighbourhood model using assumptions without the custom GAC layer.

### Ideal comparison

Compare ConsistXApp against:

1. full rebuild;
2. full rebuild with hints;
3. solver-native neighbourhood repair;
4. persistent/incremental model handling, where technically available.

If a persistent CP-SAT model cannot support the required relation mutation, state this precisely rather than implying that no persistent approach exists.

---

## 6.4 Explain static-campaign nondeterminism more precisely

The manuscript says effective seeds varied by process. Clarify whether this affected:

- generated instances;
- CP-SAT search;
- process scheduling;
- only runtime variability.

The matched-pair design requires the methods to solve the same generated instances. State explicitly:

> **All methods within a static matched instance received the same domains, relations, utilities, and context. Non-fixed solver seeds and process scheduling affected search and timing but not instance identity.**

If this was not true, the paired statistical analysis must be reconsidered.

---

## 6.5 Explain the 1.19 ms versus 1.25 ms results

The manuscript reports:

- 1.19 ms for explanation-guided repair in Table 11;
- 1.25 ms for local repair in Section 7.5.

Add one sentence explaining the distinction. For example:

> **The 1.19 ms result concerns the repair-core strategy ablation, whereas the 1.25 ms result concerns the separate objective-quality campaign and includes the operational lexicographic optimization stages.**

Use the exact reason supported by the logs.

---

# Phase 7 — Strengthen the statistical analysis

## 7.1 State the estimand for each latency comparison

For every inferential comparison, specify whether the estimand is:

- median paired instance difference;
- difference in marginal medians;
- median episode-level difference;
- Hodges–Lehmann shift;
- success probability difference.

These are not interchangeable.

For example:

> **The primary sequential estimand is the paired difference between episode-level median per-epoch latencies.**

---

## 7.2 Clarify the BCa procedure

The phrase “paired median difference” can mean two different quantities:

\[
\operatorname{median}(A_i-B_i)
\]

or:

\[
\operatorname{median}(A_i)-\operatorname{median}(B_i).
\]

State which one is used. Prefer:

\[
\operatorname{median}_{i}(A_i-B_i)
\]

for a paired design.

Also describe the resampling unit:

- instance for static comparisons;
- episode for sequential inference;
- decision for descriptive KPM intervals.

---

## 7.3 Handle no-discordance McNemar cases transparently

When both methods succeed on every instance, there are no discordant pairs. Some software returns or is conventionally assigned \(p=1\).

Add a table note:

> **When \(b+c=0\), no discordant pairs exist; the McNemar comparison is reported as \(p=1\) by convention and carries no evidence of superiority.**

---

## 7.4 Improve tail-latency evidence

The current manuscript correctly says that pooled p99 is based on approximately three observations. To improve the score substantially:

### Preferred new experiment

Run at least:

- 30–50 independent episodes per configuration;
- 100–300 epochs per episode;
- deterministic single-threaded settings;
- hierarchical reporting by episode.

Report:

- pooled median;
- per-episode median distribution;
- per-episode p95 distribution;
- hierarchical bootstrap intervals for p95;
- maximum core size;
- relationship between core size and latency.

### Important diagnostic

Model the relationship:

\[
T_{\mathrm{repair}}
\quad\text{versus}\quad
|A_r|,
\]

and possibly:

\[
T_{\mathrm{repair}}
\quad\text{versus}\quad
\text{number of expansions}.
\]

This would support the claim that core growth explains tail degradation.

Do not claim a stable p99 distribution unless the experiment has enough independent tail observations.

---

## 7.5 Improve the KPM analysis

The current marginal intervals are appropriately described as descriptive, but they are less informative than paired differences.

Use the common valid instances to calculate:

\[
\Delta_,i}
==========

T_i^}
-----

T_i^{\mathrm{CP-SAT}},
\]

and similarly for energy and fairness.

Report:

- median or mean paired difference;
- paired bootstrap interval;
- number of complete pairs;
- no equivalence claim unless a practical margin was prespecified.

If margins were not prespecified, label any margin-based analysis as exploratory.

---

# Phase 8 — Expand structural robustness experiments

The current generated instances are sparse and favourable to local repair. This is acknowledged, but a 9.5/10 paper should provide at least a limited sensitivity analysis.

## 8.1 Vary structural factors

Add a controlled experiment varying:

- graph mean degree;
- maximum degree;
- relation arity;
- domain size;
- table tightness;
- update rate;
- proportion of relaxing updates;
- feasible-region fragmentation;
- distance between consecutive feasible assignments.

A reasonable reduced factorial design could use:

| Factor      | Levels           |
| ----------- | ---------------- |
| Mean degree | 3, 6, 10         |
| Arity       | 2, 3, 4          |
| Domain size | 4, 6, 10         |
| Tightness   | 0.15, 0.35, 0.60 |
| Update rate | 2%, 10%, 25%     |
| Variables   | 100, 300, 1000   |

It is not necessary to run the full Cartesian product. Use a balanced subset or Latin hypercube design.

---

## 8.2 Report the break-even regime

The paper’s most valuable systems result would be a clear answer to:

> Under what conditions does incremental repair cease to be beneficial?

Estimate the break-even point as a function of:

- update rate;
- core size;
- graph density;
- relation arity.

For example:

\[
T_{\mathrm{incremental}}
<
T_{\mathrm{rebuild}}
\quad\text{when}\quad
\frac{|A_r|}{|A_t|}<\rho.
\]

Even an empirical threshold with confidence intervals would improve the paper considerably.

---

## 8.3 Add infeasible dynamic models to the main evaluation

Most large-scale instances retain a planted solution. This isolates coordination failure but limits availability evaluation.

Add controlled cases where:

- the full model becomes infeasible;
- GAC detects infeasibility;
- GAC does not detect infeasibility but CP-SAT does;
- the registered fallback becomes invalid;
- the system correctly returns `BLOCKED`.

Report:

- false acceptance count;
- time to block;
- certificate contents;
- distinction between proper-core and full-model infeasibility.

This would strengthen the safety/availability discussion.

---

# Phase 9 — Improve figures and tables

## 9.1 Redesign Figure 1 around the actual contribution

The current figure emphasizes GAC and repair but does not fully expose:

- model registry;
- model-version binding;
- verification transaction;
- certificate log;
- fallback path;
- forwarding gate.

A stronger architecture figure should show:

1. xApp proposals;
2. registered model and version \(\nu_t\);
3. propagation and candidate generation;
4. repair;
5. independent verifier;
6. atomic version check;
7. E2 forwarding gate;
8. audit-certificate store;
9. registered fallback;
10. blocked outcome.

Use different arrow styles for:

- control proposals;
- model/context data;
- certificate/audit data;
- accepted actions.

---

## 9.2 Simplify Table 8

The “Uncoordinated” and “Static priority” rows are confusing because they have no verifier but are reported as blocked.

Do one of the following:

### Preferred

Move them to a separate sanity-check table:

| Raw policy      | Registered-model feasible outputs |
| --------------- | --------------------------------: |
| Uncoordinated   |                             0/250 |
| Static priority |                             0/250 |

### Alternative

Rename “Blocked” to “Not admitted by the forwarding gate” and explain that unverified outputs are denied by construction.

Do not imply that a method both “has no verifier” and produces a formal pipeline `BLOCKED` result unless the common external gate is explicitly described.

---

## 9.3 Repair Table 3

As discussed, distinguish process-level and solver-level parallelism.

---

## 9.4 Repair Table 5

The multiple-testing table is too dense and difficult to read.

Split it into:

- binary-outcome comparisons;
- continuous-outcome comparisons;
- sequential episode-level comparisons.

Ensure every row has clearly aligned:

- method A;
- method B;
- \(N\);
- \(b\);
- \(c\);
- raw \(p\);
- adjusted \(p\);
- effect size.

---

## 9.5 Clarify Table 9

Explicitly align:

| Campaign             | Inferential unit | Completed repair sequences | Fully lex-optimal | Feasible-not-certified |
| -------------------- | ---------------- | -------------------------: | ----------------: | ---------------------: |
| Static               | decision         |                        248 |               248 |                      0 |
| Dynamic              | epoch            |                     14,755 |            14,755 |                      0 |
| Sequential F5 subset | episode          |                         40 |                40 |                      0 |

Check whether “episode” is genuinely the correct unit for completed repair sequences. If individual repaired epochs were optimized, report epochs rather than episodes, and separately summarize episode-level all-optimal status.

---

# Phase 10 — Tighten the narrative

## 10.1 Reduce repeated caveats

The manuscript repeatedly states that:

- guarantees apply only to the registered model;
- physical safety is not established;
- the baseline is rebuild-and-resolve;
- p99 is descriptive;
- cold-start has no advantage.

These caveats are important, but excessive repetition weakens the flow.

### Recommended strategy

- State each limitation briefly where first relevant.
- Refer to Section 8 for the full treatment.
- Provide one authoritative detailed explanation in Section 8.
- Retain only the most important caveat in the abstract and conclusion.

Avoid the phrase:

> “is discussed once in Section 8.”

Replace it with:

> **The scope of this baseline is detailed in Section 8.7.**

---

## 10.2 Condense the continuous-relaxation material

The continuous-relaxation result is useful as a negative ablation, but it is not central.

Keep in the main text:

- feasibility;
- median latency;
- deadline compliance;
- conclusion that it was excluded.

Move detailed variant results and simulator failure accounting to an appendix or supplementary material.

This will free space for:

- certificate definition;
- model-version transaction;
- baseline timing decomposition;
- structural sensitivity.

---

## 10.3 Move secondary KPM material if space is limited

The primary contribution is registered-model arbitration, not KPM superiority. If the paper exceeds the venue’s natural length, move the full KPM table and numerical-error details to the appendix.

In the main text, retain:

> **The pseudo-physical KPM results are descriptive and do not establish equivalence, non-degradation, or physical-network safety.**

---

## 10.4 Make each contribution testable

Rewrite the contribution list so each contribution maps to a result:

1. **Verifier-gated architecture** → Proposition 1 and gates G1–G4.
2. **Replayable audit certificate** → certificate schema and replay checks.
3. **Expanding repair** → 248/248 versus 227/248.
4. **Sequential operating regime** → median latency and tail limitations.
5. **Negative boundaries** → cold start, objective gap, continuous relaxation.

This creates a clear contribution–evidence chain.

---

# Phase 11 — Improve Related Work and novelty positioning

## 11.1 Add a comparison matrix

A concise related-work table would be valuable:

| Work        | Conflict classes                         | Learned/registered model       | Hard-feasibility gate | Incremental repair | Audit trace | Model-version binding |
| ----------- | ---------------------------------------- | ------------------------------ | --------------------- | ------------------ | ----------- | --------------------- |
| QACM        | …                                       | …                             | …                    | …                 | …          | …                    |
| PACIFISTA   | …                                       | …                             | …                    | …                 | …          | …                    |
| COMIX       | …                                       | …                             | …                    | …                 | …          | …                    |
| XAI4C       | …                                       | …                             | …                    | …                 | …          | …                    |
| ConsistXApp | Direct/indirect/implicit when registered | Registered finite-domain model | Yes                   | Yes                | Yes         | Yes                   |

Only fill cells after checking the cited papers directly. Do not infer absent features from abstracts alone.

This would demonstrate the paper’s niche more efficiently than several prose paragraphs.

---

## 11.2 Avoid novelty claims for established mechanisms

Continue explicitly stating that the paper does not invent:

- GAC;
- explanation generation;
- assumption cores;
- neighbourhood repair;
- dynamic CSP maintenance.

The novelty claim should remain:

> integration into a version-bound, independently verified, auditable O-RAN arbitration pipeline, plus empirical characterization of its useful sequential regime.

That is a credible systems contribution.

---

# Phase 12 — Strengthen artifact and reproducibility claims

## 12.1 Include a reproducibility manifest

For every campaign, record:

- commit hash;
- Python version;
- OR-Tools version;
- OS;
- processor allocation;
- process count;
- `num_search_workers`;
- random seed hierarchy;
- presolve;
- solver limits;
- objective scaling;
- integer coefficient bounds;
- warm-up;
- garbage-collection policy;
- timing clock;
- number of repetitions;
- command line;
- expected output hash.

---

## 12.2 Include certificate replay as a one-command test

For example:

```text
reproduce verifier-gates
reproduce static-results
reproduce sequential-results
replay certificates
build tables
build figures
```

The artifact should allow reviewers to:

1. regenerate a subset quickly;
2. reproduce all tables with a longer command;
3. replay certificates independently;
4. verify that the manuscript values match generated CSV files.

---

## 12.3 Separate trusted components

Document the trusted computing base:

- model serializer;
- production verifier;
- certificate checker;
- forwarding gate;
- model-version store.

Also identify components that need not be trusted for forwarding soundness:

- decoder;
- GAC implementation;
- repair solver;
- utility optimizer.

This is an excellent way to sharpen the architecture:

> A bug in candidate generation may reduce availability or objective quality, but it should not cause registered-model-invalid forwarding if the independent verifier and gate are correct.

---

# Phase 13 — Final language and style pass

## 13.1 Standardize terminology

Use consistently:

- `xApp` / `xApps`, not `xapp` or `xapps`;
- `Near-RT RIC`;
- `registered-model feasibility`;
- `verifier-accepted`;
- `full-scope repair`;
- `proper-core repair`;
- `rebuild-and-resolve`;
- `hard real-time guarantee`;
- `descriptive pooled p99`.

Avoid alternating between:

- coordination/arbitration without definition;
- verification/validation;
- certificate/trace;
- decision/action/outcome.

Suggested distinction:

- **proposal:** individual xApp request;
- **candidate:** joint assignment before verification;
- **accepted decision:** assignment accepted by the verifier;
- **forwarded action:** accepted decision actually admitted to E2;
- **certificate:** audit object associated with repair.

---

## 13.2 Replace awkward formulations

Replace:

> “discussed once in Section 8”

with:

> “detailed in Section 8.7.”

Replace:

> “a modern constraint solver is a demanding baseline”

with:

> **A complete modern constraint solver provides a strong baseline for the generated instances considered here.**

Replace:

> “the operating regime honestly”

with:

> **the operating regime and its limitations.**

“Honestly” is admirable but unnecessary in formal scientific prose.

---

## 13.3 Correct affiliation typography

Use:

> Department of Computer Science, University of Bejaia, Bejaia, Algeria
> LINEACT, CESI, Nancy, France
> University of Sharjah, Sharjah, United Arab Emirates

Remove spaces before periods and check the official institutional naming convention.

---

# Proposed revised paper structure

A cleaner final structure would be:

## 1. Introduction

- problem;
- registered-model boundary;
- central architecture;
- contributions;
- headline findings.

## 2. Background and Related Work

- O-RAN conflicts;
- existing mitigation approaches;
- dynamic CSP and repair;
- comparison matrix.

## 3. Registered Arbitration Model

- epochs and variables;
- hard relations;
- model version;
- utility and temporal stability;
- worked example.

## 4. Verifier-Gated ConsistXApp Architecture

- complete pipeline;
- trust boundary;
- model-version transaction;
- independent verifier;
- certificate format.

## 5. Incremental Filtering and Repair

- GAC;
- restoration;
- explanations;
- repair-core expansion;
- fallback;
- lexicographic optimization.

## 6. Formal Properties

- forwarding soundness;
- GAC preservation;
- monotone expansion;
- conditional completeness;
- restoration necessity;
- complexity.

## 7. Experimental Method

- research questions;
- scenarios;
- environments;
- baselines;
- latency boundaries;
- statistical protocol.

## 8. Results

- verifier evidence;
- static feasibility;
- repair ablation;
- objective quality;
- incremental propagation;
- candidate generators;
- cold start;
- sequential operation;
- robustness/tail analysis.

## 9. Limitations

- registered-model validity;
- verifier evidence;
- baseline scope;
- synthetic structure;
- tail latency;
- physical deployment.

## 10. Conclusion

This structure puts verification and auditability before the supporting repair mechanisms.

---

# Recommended research questions

Explicit research questions would improve the experimental narrative:

### RQ1 — Forwarding correctness evidence

> Does the independently implemented verifier agree with independent references across exhaustive, differential, property-based, and mutation-based tests?

### RQ2 — Repair effectiveness

> Does expanding the repair core recover feasible decisions that fixed violated-scope repair misses?

### RQ3 — Localization benefit

> How do explanation-guided cores compare with frontier, assumption-core, and full-scope repair in success, core size, and latency?

### RQ4 — Operating regime

> Under what update rates and problem sizes does incremental repair outperform rebuild-and-resolve CP-SAT?

### RQ5 — Cost of localization

> What objective-quality loss results from restricting optimization to a local repair core?

### RQ6 — Boundary conditions

> How do cold starts, dense instances, large repair cores, and tail events affect the advantage?

Each Results subsection should answer one RQ explicitly.

---

# Priority matrix

## Priority A — Must fix before any submission

- Repair page 3 sentence.
- Remove duplicated page 12 list.
- Repair conclusion ordering.
- Fix Proposition 1 notation.
- Correct Algorithm 2 Step 11.
- Clarify worker/process settings.
- Define whether latency includes verification.
- Fix headings, tables, bullets, and column flow.
- Explain 1.19 versus 1.25 ms.
- Verify all references and DOIs.

## Priority B — Strongly recommended for 9.0–9.3

- Refine title terminology.
- Rewrite abstract.
- Separate formal propositions.
- Define certificate validity.
- Add model-version transaction.
- Redesign Figure 1.
- Simplify Table 8.
- Restructure contribution list.
- Add research questions.
- Reduce repeated caveats.

## Priority C — Needed to approach 9.5 scientifically

- Add a stronger solver-native or persistent/incremental baseline.
- Run more independent sequential episodes.
- Add dependence-aware p95 analysis.
- Add structural sensitivity experiments.
- Add dynamic infeasible cases.
- Report certificate size and replay latency.
- Report latency decomposition at all scales.
- Add paired KPM differences.

## Priority D — Ideal extension

- Closed-loop evaluation on an O-RAN emulator or testbed.
- Public archival artifact with persistent identifier.
- Independent artifact evaluation.
- Fault-injection testing of model-version changes and verifier rejection.
- Comparative analysis under denser, higher-arity relations.

---

# Concrete acceptance checklist for the 9.5/10 version

Before submission, confirm all of the following.

## Scientific claims

- [ ] “Verified” is defined or replaced by “verifier-gated.”
- [ ] No physical-RAN safety claim is made.
- [ ] No hard real-time claim is made.
- [ ] No global optimality claim is based on `FEASIBLE`.
- [ ] Proper-core infeasibility is never treated as global infeasibility.
- [ ] The baseline scope is stated precisely.
- [ ] The verifier evidence is described as evidence, not proof.

## Formal definitions

- [ ] Verifier signature is correct.
- [ ] Model-version binding is operationally defined.
- [ ] `VarLit` and frontier expansion are defined.
- [ ] Certificate validity is defined.
- [ ] Solver statuses are interpreted correctly.
- [ ] Fallback behaviour is complete.
- [ ] Proposition assumptions are explicit.

## Experiments

- [ ] All methods receive matched instances.
- [ ] Process and CP-SAT worker counts are separated.
- [ ] Timing boundaries are defined.
- [ ] Verification inclusion/exclusion is stated.
- [ ] Timeout and blocked counts are reported.
- [ ] Random-seed policy is reproducible.
- [ ] Statistical resampling units are correct.
- [ ] Tail results remain appropriately qualified.
- [ ] Objective-quality and latency campaigns are distinguished.
- [ ] Certificate overhead is measured or clearly listed as unmeasured.

## Presentation

- [ ] No duplicated paragraphs or lists.
- [ ] No broken sentences.
- [ ] No malformed equations.
- [ ] No heading collisions.
- [ ] Tables are readable without reconstructing column order.
- [ ] Figures remain legible in print.
- [ ] All acronyms are defined once.
- [ ] Terminology is consistent.
- [ ] References and DOI links have been checked.

---

# Realistic revision sequence

## Revision round 1 — Editorial and logical corrections

Duration: approximately 1–2 focused days.

- fix all visible defects;
- correct notation;
- repair algorithms;
- standardize terminology;
- rewrite abstract and conclusion;
- clarify timing and worker settings.

Expected level: **8.8–9.0/10**.

## Revision round 2 — Structural and formal strengthening

Duration: approximately 2–4 days.

- reorganize Sections 4–6;
- separate propositions;
- define certificate validity;
- add model-version transaction;
- redesign Figure 1;
- simplify tables;
- introduce research questions.

Expected level: **9.1–9.3/10**.

## Revision round 3 — Additional experiments

Duration depends on runtime and artifact readiness.

- baseline timing decomposition;
- stronger incremental/neighbourhood baseline;
- additional independent episodes;
- structural sensitivity;
- infeasible dynamic cases;
- certificate size and replay latency.

Expected level: **9.4–9.5/10**.

## Revision round 4 — Independent audit

Ask a co-author who did not write the relevant section to verify:

- every numerical value against raw logs;
- every table against its generating script;
- every proposition against its assumptions;
- every claim against the presented evidence;
- every reference against the original source.

Expected final result: **submission-ready, approximately 9.5/10**.

---

## Final recommendation

The highest-value changes are not additional prose. They are:

1. **removing all production defects;**
2. **making the verifier-gated, version-bound architecture the unmistakable centre of the paper;**
3. **clarifying timing and parallelism;**
4. **strengthening baseline fairness;**
5. **adding certificate overhead and structural-sensitivity evidence;**
6. **improving the sequential tail experiment.**
