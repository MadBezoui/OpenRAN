from typing import Dict, List, Set, Any
import collections

from src.model.domains import FilteredDomain
from src.model.relations import ActiveRelation, Variable
from src.propagation.gac import GAC

class IncrementalGAC(GAC):
    """
    Incremental version of GAC.
    """
    def __init__(self, variables: List[Variable], domains: Dict[int, FilteredDomain], relations: List[ActiveRelation]):
        super().__init__(variables, domains, relations)
        
    def enforce_incremental(self, modified_vars: Set[int], modified_rels: Set[int]) -> bool:
        """
        Enforces GAC incrementally by only queuing variables whose domains changed or whose relations changed.
        """
        queue = collections.deque()
        in_queue = set()
        
        # Enqueue variables that were directly modified
        for v_id in modified_vars:
            var = next(v for v in self.variables if v.id == v_id)
            queue.append(var)
            in_queue.add(v_id)
            
        # Enqueue variables involved in modified relations
        for rel in self.relations:
            if rel.relation.id in modified_rels:
                for v_id in rel.relation.scope:
                    if v_id not in in_queue:
                        var = next(v for v in self.variables if v.id == v_id)
                        queue.append(var)
                        in_queue.add(v_id)
                        
        while queue:
            var = queue.popleft()
            in_queue.remove(var.id)
            
            for active_rel in self.var_to_relations[var.id]:
                revised_vars = self._revise(active_rel)
                for rev_v_id in revised_vars:
                    if self.domains[rev_v_id].is_empty():
                        return False # Domain wipeout
                    if rev_v_id not in in_queue:
                        in_queue.add(rev_v_id)
                        rev_var = next(v for v in self.variables if v.id == rev_v_id)
                        queue.append(rev_var)
                        
        return True
