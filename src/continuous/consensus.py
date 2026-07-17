import numpy as np
from typing import Dict, Any, List

from src.model.domains import FilteredDomain
from src.model.relations import ActiveRelation, Variable

class ContinuousConsensus:
    """
    Continuous coordination stage that operates over the filtered domains and active tuples.
    """
    def __init__(self, variables: List[Variable], domains: Dict[int, FilteredDomain], relations: List[ActiveRelation],
                 tau=1.0, alpha=0.0, beta=1.0, epsilon=1e-12):
        self.variables = variables
        self.domains = domains
        self.relations = relations
        
        self.tau = tau
        self.alpha = alpha
        self.beta = beta
        self.epsilon = epsilon
        
        self.marginals = {}
        
        # Init uniform marginals over the FILTERED domain
        for var in self.variables:
            domain = self.domains[var.id]
            n = len(domain)
            if n > 0:
                p = 1.0 / n
                self.marginals[var.id] = {a: p for a in domain.active_values}
            else:
                self.marginals[var.id] = {}
                
        # Build index mapping
        self.var_to_relations = {v.id: [] for v in self.variables}
        for rel in self.relations:
            for v_id in rel.relation.scope:
                self.var_to_relations[v_id].append(rel)
                
    def step(self):
        new_marginals = {}
        for var in self.variables:
            var_id = var.id
            active_vals = self.domains[var_id].active_values
            if not active_vals:
                new_marginals[var_id] = {}
                continue
                
            constraints = self.var_to_relations[var_id]
            if not constraints:
                new_marginals[var_id] = self.marginals[var_id].copy()
                continue
                
            eta = 1.0 / len(constraints)
            ell = {}
            for a in active_vals:
                term1 = self.alpha * np.log(max(self.marginals[var_id][a], self.epsilon))
                term2 = 0.0
                
                for active_rel in constraints:
                    w_sum = 0.0
                    w_a_sum = 0.0
                    
                    var_idx_in_scope = active_rel.var_indices[var_id]
                    
                    # Only iterate over ACTIVE tuples (this incorporates GAC filtering directly into the continuous inference)
                    for z in active_rel.active_tuples:
                        log_p_sum = 0.0
                        for j_id, j_idx in active_rel.var_indices.items():
                            val = z[j_idx]
                            # If for some reason a tuple references a removed value (shouldn't happen after GAC), probability is epsilon
                            p_val = self.marginals[j_id].get(val, self.epsilon)
                            log_p_sum += np.log(max(p_val, self.epsilon))
                            
                        # Here we assume utility is 0 for simplicity, in a real implementation we'd read it from the model
                        u_c = 0.0 
                        
                        w_z = np.exp((1.0 / self.tau) * log_p_sum)
                        w_sum += w_z
                        if z[var_idx_in_scope] == a:
                            w_a_sum += w_z
                            
                    pi = w_a_sum / w_sum if w_sum > 0 else 0.0
                    term2 += eta * np.log(max(pi, self.epsilon))
                ell[a] = term1 + term2
                
            max_ell = max(ell.values())
            exp_ell = {a: np.exp(ell[a] - max_ell) for a in active_vals}
            sum_exp = sum(exp_ell.values())
            p_hat = {a: exp_ell[a] / sum_exp for a in active_vals}
            
            q = {a: p_hat[a] ** self.beta for a in active_vals}
            sum_q = sum(q.values())
            q_norm = {a: max(q[a] / sum_q, self.epsilon) for a in active_vals}
            
            sum_q_norm = sum(q_norm.values())
            new_marginals[var_id] = {a: q_norm[a] / sum_q_norm for a in active_vals}
            
        return new_marginals
        
    def solve(self, max_iter=100, tol=1e-4):
        """Run the consensus update to a stopping condition.

        Returns (residual, iterations) so the caller can record the actual
        number of iterations executed before convergence or the iteration cap.
        """
        residual = 0.0
        iterations = 0
        for _ in range(max_iter):
            iterations += 1
            new_marginals = self.step()

            residual = 0.0
            for var_id in self.variables:
                diff = sum(abs(new_marginals[var_id.id].get(a, 0) - self.marginals[var_id.id].get(a, 0))
                           for a in self.domains[var_id.id].active_values)
                residual = max(residual, diff)

            self.marginals = new_marginals
            if residual < tol:
                break
        self.iterations = iterations
        return residual, iterations
