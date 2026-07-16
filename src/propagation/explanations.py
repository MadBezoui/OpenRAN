from typing import List, Set, Dict, Any, Tuple
from dataclasses import dataclass

from src.model.domains import FilteredDomain
from src.model.relations import Variable, Relation

@dataclass
class Explanation:
    """
    An explanation for a contradiction (e.g., domain wipeout) or value removal.
    It contains a set of constraint IDs and a set of variable assignments or domain restrictions
    that logically entail the contradiction.
    """
    constraints: Set[int]
    # For dynamic CSP, we might also need to record specific domain restrictions if the domains are dynamic.
    # For now, we will just record the set of constraints that were involved in the wipeout.
    
    def __post_init__(self):
        self.constraints = frozenset(self.constraints)
        
def extract_wipeout_explanation(domains: Dict[int, FilteredDomain], wipeout_var_id: int) -> Explanation:
    """
    Extracts an explanation for a domain wipeout of the given variable.
    This traces back the removal reasons for all values in the wipeout variable's domain.
    """
    constraints_involved = set()
    
    # Starting from the wipeout variable, trace back all removals.
    # Since GAC records the constraint responsible for removing each value:
    if wipeout_var_id not in domains:
        return Explanation(constraints=frozenset())
        
    filtered_domain = domains[wipeout_var_id]
    
    def trace_removal(var_id: int, val: Any):
        if val in domains[var_id].removal_reasons:
            reason = domains[var_id].removal_reasons[val]
            if reason["type"] == "GAC_REMOVAL":
                constraints_involved.add(reason["relation"])
                # Ideally, we should recursively trace why the supporting tuples were invalidated,
                # which requires knowing which values in other variables caused those tuples to be invalid.
                # For simplicity in this initial version, we just collect the immediate constraints.
                
    for val in filtered_domain.base_domain.base_values:
        trace_removal(wipeout_var_id, val)
        
    return Explanation(constraints=constraints_involved)
