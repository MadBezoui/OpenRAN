from typing import Set, Tuple, List
from src.model.relations import Relation

class RadiusCoreBuilder:
    """
    Builds a repair core expanding radially from a set of conflicting variables or constraints.
    """
    def __init__(self, relations: List[Relation]):
        self.relations = relations
        self.rel_map = {r.id: r for r in relations}
        
    def build_core_from_vars(self, seed_vars: Set[int], radius: int) -> Tuple[Set[int], Set[int]]:
        """
        Builds a core including variables up to `radius` hops away in the constraint graph.
        h=0: only seed_vars and relations internal to seed_vars
        h=1: relations incident to seed_vars, and their variables
        """
        core_vars = set(seed_vars)
        core_rels = set()
        
        for r in range(radius + 1):
            next_vars = set(core_vars)
            
            for rel in self.relations:
                # If relation touches any variable currently in the core
                if any(vid in core_vars for vid in rel.scope):
                    core_rels.add(rel.id)
                    # If this is not the last step (h=0 means we don't expand vars from rels, wait! 
                    # If h=0, we only include relations fully subsumed by core_vars.)
                    pass
                    
            if r == 0:
                # Filter rels to only those FULLY in core_vars
                core_rels = {rel.id for rel in self.relations if all(vid in core_vars for vid in rel.scope)}
            else:
                # Expand vars for the next radius iteration
                for rel_id in core_rels:
                    next_vars.update(self.rel_map[rel_id].scope)
                core_vars = next_vars
                
        return core_vars, core_rels
