import numpy as np
from typing import Dict, Any, Tuple
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.models import Problem

class ContinuousSolver:
    def __init__(self, problem: Problem, tau=1.0, alpha=0.0, beta=1.0, epsilon=1e-12):
        self.problem = problem
        self.tau = tau
        self.alpha = alpha
        self.beta = beta
        self.epsilon = epsilon
        
        self.marginals = {}
        for var_id, var in self.problem.variables.items():
            # Init uniform
            n = len(var.domain)
            p = np.ones(n) / n
            self.marginals[var_id] = {a: p[idx] for idx, a in enumerate(var.domain)}
            
    def step(self):
        new_marginals = {}
        for var_id, var in self.problem.variables.items():
            constraints = self.problem.get_incident_constraints(var_id)
            if not constraints:
                new_marginals[var_id] = self.marginals[var_id].copy()
                continue
                
            eta = 1.0 / len(constraints)
            ell = {}
            for a in var.domain:
                term1 = self.alpha * np.log(max(self.marginals[var_id][a], self.epsilon))
                term2 = 0.0
                for cons in constraints:
                    w_sum = 0.0
                    w_a_sum = 0.0
                    var_idx_in_scope = cons.scope.index(var_id)
                    for z in cons.allowed_tuples:
                        log_p_sum = 0.0
                        for j_idx, j_id in enumerate(cons.scope):
                            log_p_sum += np.log(max(self.marginals[j_id][z[j_idx]], self.epsilon))
                        
                        u_c = cons.tuple_utilities.get(z, 0.0)
                        w_z = np.exp((1.0 / self.tau) * (log_p_sum + cons.gamma * u_c))
                        
                        w_sum += w_z
                        if z[var_idx_in_scope] == a:
                            w_a_sum += w_z
                            
                    pi = w_a_sum / w_sum if w_sum > 0 else 0.0
                    term2 += eta * np.log(max(pi, self.epsilon))
                ell[a] = term1 + term2
                
            max_ell = max(ell.values())
            exp_ell = {a: np.exp(ell[a] - max_ell) for a in var.domain}
            sum_exp = sum(exp_ell.values())
            p_hat = {a: exp_ell[a] / sum_exp for a in var.domain}
            
            q = {a: p_hat[a] ** self.beta for a in var.domain}
            sum_q = sum(q.values())
            q_norm = {a: max(q[a] / sum_q, self.epsilon) for a in var.domain}
            
            sum_q_norm = sum(q_norm.values())
            new_marginals[var_id] = {a: q_norm[a] / sum_q_norm for a in var.domain}
            
        return new_marginals
        
    def solve(self, max_iter=100, tol=1e-4) -> float:
        residual = 0.0
        for _ in range(max_iter):
            new_marginals = self.step()
            
            residual = 0.0
            for var_id in self.problem.variables:
                diff = sum(abs(new_marginals[var_id][a] - self.marginals[var_id][a]) 
                           for a in self.problem.variables[var_id].domain)
                residual = max(residual, diff)
                
            self.marginals = new_marginals
            if residual < tol:
                break
        return residual
                
    def decode(self) -> Dict[int, Any]:
        assignment = {}
        for var_id, var in self.problem.variables.items():
            best_a = None
            best_p = -1.0
            for a in var.domain:
                if self.marginals[var_id][a] > best_p:
                    best_p = self.marginals[var_id][a]
                    best_a = a
            assignment[var_id] = best_a
        return assignment
        
    def get_fractionality(self) -> float:
        n = len(self.problem.variables)
        if n == 0: return 0.0
        score = 0.0
        for var_id, var in self.problem.variables.items():
            max_p = max(self.marginals[var_id].values())
            score += (1.0 - max_p)
        return score / n
