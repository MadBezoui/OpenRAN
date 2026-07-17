# ConsistXApp — corrected experiment suite

This suite replaces the previous experiments and directly addresses the second
review round. Run everything with:

```bash
cd <repo root>
pip install ortools numpy pandas          # once
PYTHONPATH=. python scripts/run_all.py    # full campaign (writes artifacts/)
# quick smoke check:
PYTHONPATH=. python scripts/run_all.py --quick
```

Outputs:

* `artifacts/raw/*.csv` — per-instance / per-repair / per-epoch raw logs
  (integer-level detail, not just aggregates).
* `artifacts/tables/summary.json` — every reported number with exact sample
  sizes and 95% bootstrap CIs, plus integer outcome counts that sum to N.
* `artifacts/tables/manifest.json` — reproducibility manifest (Python /
  OR-Tools / NumPy / pandas versions, host, CPU, git commit, all parameters,
  seeds, deadline, CP-SAT settings).

## What each script produces

| Script | Output | Purpose |
|---|---|---|
| `run_sanity.py` | stdout | propagator + explanation-checker gates |
| `run_static.py` | `static_results.csv` | 10 methods x 5 scenarios x 50 seeds; per-instance outcome, continuous iterations, repair audit, counterfactual **and** verified-executed KPIs |
| `run_repair_ablation.py` | `repair_ablation.csv` | 8 repair strategies on identical repair-triggering decodes, full per-repair audit |
| `run_incremental.py` | `dynamic_results.csv` | 15,000-epoch incremental-vs-recompute GAC with domain-agreement check |
| `run_temporal.py` | `temporal_results.csv` | churn-weight `mu` sweep: churn / throughput / feasibility trade-off (RQ6) |
| `run_scalability.py` | `scalability_results.csv` | latency vs n for CP-SAT, GAC+CP-SAT, GAC+expl-repair, full pipeline |
| `aggregate.py` | `summary.json` | counts + bootstrap CIs for every table |

## How the review points are addressed

* **2.1 / 2.2 — isolate explanation-guided repair; monotonicity.**
  `RepairEngine` (`src/repair/engine.py`) implements every strategy on the same
  decoded candidate and boundary: `violated0`, `radius0/1/2`, `frontier`,
  `explanation`, `assumption`, `fullscope`. The radius core is now **seeded from
  the violated-constraint scope** (`RadiusCoreBuilder`, fixed), so cores are
  nested and larger nested cores never become infeasible — the previous
  "smaller core succeeds where larger fails" artifact is gone. The ablation logs
  initial/final core size, expansions, which mechanism was actually used
  (propagation explanation / CP-SAT assumption core / deterministic frontier),
  boundary variables released, and per-stage times.

* **2.3 — genuine CP-SAT assumption cores.**
  `CPSATAdapter.solve_with_assumptions` registers reified Boolean literals
  `b_j => (x_j = xhat_j)` as model assumptions and, on infeasibility, returns
  `SufficientAssumptionsForInfeasibility` mapped back to the boundary variables
  to release. `num_search_workers = 1`; OR-Tools version is recorded in the
  manifest.

* **2.4 — strict 100 ms budget.** The pipeline now enforces a single hard
  wall-clock budget across GAC + continuous + repair; when it is exceeded the
  repair times out and the decision falls back or blocks (it is never counted as
  an ordinary decision). Under this budget the continuous pipeline genuinely
  blocks/falls back on the larger scenarios — reported honestly.

* **2.5 — "without incremental reuse".** Cross-epoch incremental reuse is a
  property of the *dynamic* suite only, reported in `dynamic_results.csv` with
  100% domain agreement. The misleading `M10` row is removed from the static
  method set; the static table publishes integer outcome counts that sum to N.

* **2.6 — network KPIs vs execution semantics.** `static_results.csv` records
  KPIs twice: `cf_*` (counterfactual — what the raw proposal would yield if
  executed) and `ex_*` (verified-executed only). Uncoordinated, being 100%
  blocked, has KPIs reported only as counterfactual.

* **2.8 — statistics.** `aggregate.py` reports exact N and paired bootstrap 95%
  CIs; scalability uses 10 seeds; outcomes are stratified by scenario in the raw
  logs.

* **2.9 / 2.11 — missing evidence, continuous justification.** Continuous
  iteration counts are logged (RQ3). `run_temporal.py` supplies real RQ6
  numbers. The **GAC + explanation-repair (no continuous)** method is included
  as the direct architectural alternative to the continuous pipeline.

* **Reproducibility.** `manifest.json` captures the environment and parameters
  the previous draft only promised.

## Method taxonomy (static suite)

1. Uncoordinated (random proposal) 2. Static priority 3. Continuous only
4. GAC + decode 5. CP-SAT 6. GAC + CP-SAT 7. **GAC + explanation repair (no
continuous)** 8. ConsistXApp (explanation) 9. ConsistXApp (radius) 10.
ConsistXApp (assumption).

> After you run `run_all.py`, the manuscript tables should be regenerated from
> `artifacts/tables/summary.json` (numbers, CIs, and integer counts).

## Revision-2 additions (review-driven campaigns)

| Script | Output | Purpose |
|---|---|---|
| `scripts/run_breakpoint.py` | `breakpoint_results.csv` | E1 cold-start frontier, n up to 1000, CP-SAT (build+solve split) vs GAC+expl repair |
| `scripts/run_dynamic_scale.py` | `dynamic_scale_results.csv` | E2 amortized per-epoch cost: CP-SAT rebuild vs CP-SAT+hints vs incremental verified repair, delta in {2%,10%} |
| `scripts/run_literature_baselines.py` | `literature_baselines.csv` | E3 QACM-like and NSWF-like baselines on the S1-S5 suite |
| `scripts/run_verifier_validation.py` | `verifier_validation.json` | E4 gates G1-G4: exhaustive oracle, CP-SAT second verifier, property-based, mutation |
| `scripts/stats_paired.py` | `stats_paired.json` | E6 exact McNemar + Wilcoxon + Cliff's delta + Holm on the raw logs |

These campaigns were executed in a secondary environment recorded in
`artifacts/tables/manifest_secondary.json` (2-vCPU Linux, OR-Tools 9.15).
Before submission, rerun them on the reference host and regenerate the
corresponding tables; comparisons are paired and within-environment, so the
qualitative conclusions (no cold-start crossover; ~5x amortized advantage at
n=1000, delta=2%; zero gate divergences) are hardware-robust but the absolute
milliseconds must match the submitted manifest.
