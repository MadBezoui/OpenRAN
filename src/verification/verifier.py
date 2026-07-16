from typing import Dict, List, Any
from src.model.domains import Domain
from src.model.relations import Relation

class Verifier:
    """
    Independent decision verifier to ensure no unverified action is forwarded to the E2 interface.
    """
    def __init__(self, base_domains: Dict[int, Domain], hard_relations: List[Relation]):
        self.base_domains = base_domains
        self.hard_relations = hard_relations
        
    def verify(self, assignment: Dict[int, Any], context_id: str, expected_context_id: str) -> bool:
        """
        Verifies if an assignment satisfies all hard constraints and domains.
        """
        # 1. Verify context freshness
        if context_id != expected_context_id:
            return False
            
        # 2. Verify all variables are assigned and in their base domains
        for var_id, domain in self.base_domains.items():
            if var_id not in assignment:
                return False
            if not domain.contains(assignment[var_id]):
                return False
                
        # 3. Verify all hard relations
        for rel in self.hard_relations:
            if not rel.is_hard:
                continue
            
            # Extract assignment for the relation's scope
            try:
                tup = tuple(assignment[vid] for vid in rel.scope)
            except KeyError:
                return False # Missing variable assignment
                
            if not rel.is_allowed(tup):
                return False
                
        return True
