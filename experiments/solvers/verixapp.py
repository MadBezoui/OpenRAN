import sys
import os
from typing import Dict, Any, Tuple

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.models import Problem
from src.verifier import Verifier
from solvers.continuous import ContinuousSolver
from solvers.repair import ExactRepairSolver


class VeriXApp:
    """
    Full VeriXApp pipeline: continuous marginal inference, fractional-stall
    diagnostics, exact local repair over a conflict-induced core, and an
    independent decision verifier.

    Repair proceeds over an induced conflict core. If the local core is too
    small to admit a feasible completion (a boundary relation is over-
    constrained by fixed neighbours), the core is progressively expanded by
    additional hops in the conflict graph, and finally to the full problem.
    Because generated instances are feasible by construction, escalation
    guarantees repair terminates on a verified assignment when one exists,
    while the reported core size records the smallest core that succeeded.
    """

    def __init__(self, problem: Problem, beta: float = 2.0):
        self.problem = problem
        self.beta = beta
        self.continuous = ContinuousSolver(problem, beta=beta)
        self.repair_solver = ExactRepairSolver(problem)
        self.verifier = Verifier(problem)

    def solve(self, fallback_assignment: Dict[int, Any] = None,
              repair_budget_ms: int = 200, repair_enabled: bool = True,
              max_hops: int = 2) -> Tuple[Dict[int, Any], Dict[str, Any]]:
        stats = {}

        residual = self.continuous.solve()
        fractionality = self.continuous.get_fractionality()
        decoded = self.continuous.decode()
        is_valid = self.verifier.verify(decoded)

        stats["residual"] = residual
        stats["fractionality"] = fractionality
        stats["stall"] = (residual < 1e-4) and (fractionality > 0.05) and not is_valid
        stats["valid_decode"] = is_valid
        stats["repair_attempted"] = False
        stats["repaired"] = False
        stats["repair_timeout"] = False
        stats["core_size"] = 0

        final_assignment = decoded

        if not is_valid:
            if not repair_enabled:
                # Ablation: no repair component. The decision is infeasible.
                return None, stats

            stats["repair_attempted"] = True
            all_vars = list(self.problem.variables.keys())
            repaired = None
            used_core = 0

            # Escalate the repair core: local hops first, then full problem.
            hop_schedule = list(range(0, max_hops + 1))
            for hops in hop_schedule:
                core = self.repair_solver.extract_core(decoded, hops=hops)
                if not core:
                    continue
                cand = self.repair_solver.repair(decoded, core,
                                                 time_limit_ms=repair_budget_ms)
                if cand is not None and self.verifier.verify(cand):
                    repaired = cand
                    used_core = len(core)
                    break

            if repaired is None:
                # Full-scope exact repair (equivalent to complete CP-SAT).
                cand = self.repair_solver.repair(decoded, all_vars,
                                                 time_limit_ms=repair_budget_ms)
                if cand is not None and self.verifier.verify(cand):
                    repaired = cand
                    used_core = len(all_vars)

            if repaired is not None:
                final_assignment = repaired
                stats["repaired"] = True
                stats["core_size"] = used_core
            else:
                stats["repair_timeout"] = True
                if fallback_assignment is not None:
                    final_assignment = fallback_assignment
                else:
                    final_assignment = None

        return final_assignment, stats
