from typing import Set, Tuple, List
from src.propagation.explanations import Explanation
from src.model.relations import Relation

class ExplanationCoreBuilder:
    """
    Builds a repair core guided by propagation explanations.
    """
    def __init__(self, relations: List[Relation]):
        self.relations = relations
        self.rel_map = {r.id: r for r in relations}
        
    def build_core(self, explanation: Explanation) -> Tuple[Set[int], Set[int]]:
        """
        Returns (core_vars, core_rels) derived from the explanation.
        """
        core_rels = set(explanation.constraints)
        core_vars = set()
        
        for rel_id in core_rels:
            rel = self.rel_map[rel_id]
            core_vars.update(rel.scope)
            
        return core_vars, core_rels
        
    def expand_core(self, core_vars: Set[int], core_rels: Set[int]) -> Tuple[Set[int], Set[int]]:
        """
        Expands the core monotonically if the previous core was infeasible.
        Adds all relations incident to the current core_vars.
        """
        new_core_rels = set(core_rels)
        new_core_vars = set(core_vars)
        
        for rel in self.relations:
            # If the relation shares any variable with the core, add it to the core
            if any(vid in core_vars for vid in rel.scope):
                new_core_rels.add(rel.id)
                new_core_vars.update(rel.scope)
                
        return new_core_vars, new_core_rels
