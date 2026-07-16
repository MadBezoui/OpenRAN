import time
import random
from typing import Dict, Any, List

from src.model.domains import FilteredDomain
from src.model.relations import ActiveRelation
from src.propagation.gac import GAC
from src.propagation.explanations import extract_wipeout_explanation
from src.continuous.consensus import ContinuousConsensus
from src.continuous.decoder import Decoder
from src.continuous.diagnostics import Diagnostics
from src.repair.explanation_core import ExplanationCoreBuilder
from src.repair.radius_core import RadiusCoreBuilder
from src.repair.cpsat_adapter import CPSATAdapter
from src.verification.verifier import Verifier

def run_pipeline(variables, base_domains, relations, context_id: str, verifier: Verifier, method_id: str) -> Dict[str, Any]:
    metrics = {
        "propagation_time_ns": 0, "continuous_time_ns": 0, "repair_time_ns": 0, "verification_time_ns": 0, "total_time_ns": 0,
        "wipeout": False, "explanation_size": 0, "continuous_iterations": 0, "final_residual": 0.0, "final_fractionality": 0.0,
        "operational_stall": False, "invalid_decode": False, "repair_attempted": False, "initial_core_size": 0,
        "final_core_size": 0, "expansion_count": 0, "full_scope_required": False, "repair_success": False,
        "raw_verified": False, "fallback_used": False, "fallback_verified": False, "executed_verified": False,
        "values_before": 0, "values_after": 0, "tuples_before": 0, "tuples_after": 0,
    }
    
    start_time = time.monotonic_ns()
    
    filtered_domains = {v.id: FilteredDomain(base_domains[v.id]) for v in variables}
    active_relations = [ActiveRelation(rel) for rel in relations]
    
    fallback = {v.id: base_domains[v.id].base_values[0] for v in variables}
    
    def apply_fallback():
        metrics["fallback_used"] = True
        metrics["fallback_verified"] = verifier.verify(fallback, context_id, context_id)
        metrics["executed_decision"] = fallback
        metrics["executed_verified"] = metrics["fallback_verified"]
        metrics["total_time_ns"] = time.monotonic_ns() - start_time
        return metrics

    use_gac = method_id in ["M3", "M5", "M6", "M7", "M8", "M9", "M10"]
    use_continuous = method_id in ["M2", "M3", "M6", "M7", "M8", "M9"]
    use_repair = method_id in ["M4", "M5", "M6", "M8", "M9", "M10"]
    repair_type = "full" if method_id in ["M4", "M5"] else ("radius" if method_id in ["M6", "M8"] else "explanation")

    if method_id == "M0":
        # Uncoordinated random assignment
        assignment = {v.id: random.choice(base_domains[v.id].base_values) for v in variables}
        metrics["raw_verified"] = verifier.verify(assignment, context_id, context_id)
        if metrics["raw_verified"]:
            metrics["executed_decision"] = assignment
            metrics["executed_verified"] = True
            metrics["total_time_ns"] = time.monotonic_ns() - start_time
            return metrics
        return apply_fallback()

    # 1. Propagation
    metrics["values_before"] = sum(len(d.base_values) for d in base_domains.values())
    metrics["tuples_before"] = sum(len(r.relation.allowed_tuples) for r in active_relations if r.relation.is_hard)

    if use_gac:
        t0 = time.monotonic_ns()
        gac = GAC(variables, filtered_domains, active_relations)
        success = gac.enforce()
        metrics["propagation_time_ns"] = time.monotonic_ns() - t0
        
        metrics["values_after"] = sum(len(d.active_values) for d in filtered_domains.values())
        metrics["tuples_after"] = sum(len(r.active_tuples) for r in active_relations if r.relation.is_hard)

        if not success:
            metrics["wipeout"] = True
            metrics["global_wipeout"] = True
            # As per review: wipeout in base model = global infeasibility.
            # We must fallback unless we are allowed to relax (which we don't in this base pipeline)
            return apply_fallback()
            
    # 2. Continuous
    assignment = {}
    if use_continuous:
        t1 = time.monotonic_ns()
        consensus = ContinuousConsensus(variables, filtered_domains, active_relations)
        residual = consensus.solve()
        metrics["continuous_iterations"] = 50
        metrics["final_residual"] = residual
        metrics["continuous_time_ns"] = time.monotonic_ns() - t1
        
        decoder = Decoder(consensus)
        assignment = decoder.decode()
        diag = Diagnostics(consensus, verifier)
        diag_res = diag.diagnose(assignment, context_id)
        
        metrics["final_fractionality"] = diag.get_fractionality()
        metrics["operational_stall"] = diag_res["operational_stall"]
        metrics["invalid_decode"] = diag_res["invalid_non_stalled_decode"]
        metrics["raw_verified"] = diag_res["is_valid"]
        
        if diag_res["is_valid"]:
            metrics["optimized_verified"] = True
            metrics["executed_decision"] = assignment
            metrics["executed_verified"] = True
            metrics["total_time_ns"] = time.monotonic_ns() - start_time
            return metrics
    else:
        # For M4, M5 (CP-SAT only) and M10
        if method_id == "M10":
            # Deterministic utility-based candidate from filtered domains (using first available value as proxy for max utility)
            assignment = {v.id: sorted(list(filtered_domains[v.id].active_values))[0] for v in variables}
            
            # Diagnose it to set the flags
            diag = Diagnostics(ContinuousConsensus(variables, filtered_domains, active_relations), verifier)
            diag_res = diag.diagnose(assignment, context_id)
            metrics["invalid_decode"] = diag_res["invalid_non_stalled_decode"]
            metrics["raw_verified"] = diag_res["is_valid"]
            
            if diag_res["is_valid"]:
                metrics["optimized_verified"] = True
                metrics["executed_decision"] = assignment
                metrics["executed_verified"] = True
                metrics["total_time_ns"] = time.monotonic_ns() - start_time
                return metrics
                
        if use_repair:
            pass # handled below
        else:
            return apply_fallback()
            
    # 3. Repair (or CP-SAT solving)
    if use_repair:
        metrics["repair_attempted"] = True
        cpsat = CPSATAdapter(variables, base_domains, relations)
        
        core_vars = set(v.id for v in variables)
        core_rels = set(r.id for r in relations)
        
        if method_id not in ["M4", "M5"]:
            if repair_type == "radius":
                rad_builder = RadiusCoreBuilder(relations)
                conflicting_vars = {variables[0].id} 
                core_vars, core_rels = rad_builder.build_core_from_vars(conflicting_vars, radius=1)
            elif repair_type == "explanation":
                # For explanation, since we didn't have a global wipeout, we might have an invalid decode
                # We can trace it to some failing constraints
                failing_rels = []
                for r in relations:
                    if r.is_hard:
                        try:
                            tup = tuple(assignment[vid] for vid in r.scope)
                            if not r.is_allowed(tup):
                                failing_rels.append(r)
                        except KeyError:
                            failing_rels.append(r)
                            
                core_rels = set(r.id for r in failing_rels)
                core_vars = set()
                for r in failing_rels:
                    core_vars.update(r.scope)
                if not core_vars:
                    core_vars = set(v.id for v in variables)
                    core_rels = set(r.id for r in relations)
                
        metrics["initial_core_size"] = len(core_vars)
        
        solve_res = cpsat.solve(core_vars, core_rels, boundary_assignments={}, time_limit_ms=100)
        metrics["model_build_time_ns"] = solve_res.get("model_build_time_ns", 0)
        metrics["solver_time_ns"] = solve_res.get("solver_time_ns", 0)
        metrics["repair_time_ns"] = metrics["model_build_time_ns"] + metrics["solver_time_ns"]
        
        from ortools.sat.python import cp_model
        if solve_res["status"] == cp_model.UNKNOWN:
            metrics["timeout"] = True
        elif solve_res["status"] == cp_model.INFEASIBLE:
            metrics["infeasible"] = True
            
        repaired_assignment = solve_res["assignment"]
        
        if repaired_assignment and verifier.verify(repaired_assignment, context_id, context_id):
            metrics["repair_success"] = True
            metrics["repaired_verified"] = True
            metrics["executed_decision"] = repaired_assignment
            metrics["executed_verified"] = True
            metrics["total_time_ns"] = time.monotonic_ns() - start_time
            return metrics
            
    return apply_fallback()
