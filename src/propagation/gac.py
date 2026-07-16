from typing import Dict, List, Set, Tuple, Any
import collections

from src.model.domains import FilteredDomain
from src.model.relations import ActiveRelation, Variable

class GAC:
    """
    Generalized Arc Consistency (GAC) implementation for positive table constraints.
    """
    def __init__(self, variables: List[Variable], domains: Dict[int, FilteredDomain], relations: List[ActiveRelation]):
        self.variables = variables
        self.domains = domains
        self.relations = relations
        
        # Map var_id to the list of relations involving it
        self.var_to_relations: Dict[int, List[ActiveRelation]] = collections.defaultdict(list)
        for r in self.relations:
            for v_id in r.relation.scope:
                self.var_to_relations[v_id].append(r)
                
    def enforce(self) -> bool:
        """
        Enforces GAC. Returns True if successful (no wipeout), False if a wipeout occurred.
        """
        # Initialize queue with all variables
        queue = collections.deque(self.variables)
        in_queue = set(v.id for v in self.variables)
        
        while queue:
            var = queue.popleft()
            in_queue.remove(var.id)
            
            # For each constraint involving var, revise the domains of other variables in the constraint
            for active_rel in self.var_to_relations[var.id]:
                revised_vars = self._revise(active_rel)
                for rev_v_id in revised_vars:
                    if self.domains[rev_v_id].is_empty():
                        return False # Domain wipeout
                    if rev_v_id not in in_queue:
                        in_queue.add(rev_v_id)
                        # We need the Variable object
                        rev_var = next(v for v in self.variables if v.id == rev_v_id)
                        queue.append(rev_var)
                        
        return True
        
    def _revise(self, active_rel: ActiveRelation) -> List[int]:
        """
        Revises the active relation and the domains of variables in its scope.
        Returns a list of variable IDs whose domains were reduced.
        """
        revised_vars = []
        
        # 1. Filter active tuples in the relation: 
        # A tuple is valid only if all its values are in the current filtered domains.
        invalid_tuples = []
        for tup in active_rel.active_tuples:
            is_valid = True
            for var_id, idx in active_rel.var_indices.items():
                if not self.domains[var_id].contains(tup[idx]):
                    is_valid = False
                    break
            if not is_valid:
                invalid_tuples.append(tup)
                
        for tup in invalid_tuples:
            active_rel.remove_tuple(tup)
            
        # 2. Filter domains:
        # A value in a variable's domain is valid only if it has at least one support in the active tuples.
        for var_id in active_rel.relation.scope:
            invalid_values = []
            for val in self.domains[var_id].active_values:
                if not active_rel.has_support(var_id, val):
                    invalid_values.append(val)
                    
            if invalid_values:
                for val in invalid_values:
                    self.domains[var_id].remove_value(val, reason={"type": "GAC_REMOVAL", "relation": active_rel.relation.id})
                revised_vars.append(var_id)
                
        return revised_vars
