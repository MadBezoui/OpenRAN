from typing import List, Dict, Any
from src.model.domains import FilteredDomain, Domain
from src.model.relations import Variable, Relation, ActiveRelation
from src.propagation.gac import GAC
from src.propagation.explanations import Explanation

class ExplanationChecker:
    """
    Verifies that a given explanation (set of constraints) is actually sufficient to cause a domain wipeout.
    """
    def __init__(self, variables: List[Variable], base_domains: Dict[int, Domain], relations: List[Relation]):
        self.variables = variables
        self.base_domains = base_domains
        self.relations = relations
        
    def check_wipeout(self, explanation: Explanation, wipeout_var_id: int) -> bool:
        """
        Verifies if running GAC with ONLY the constraints in the explanation leads to a wipeout of wipeout_var_id.
        """
        filtered_domains = {vid: FilteredDomain(dom) for vid, dom in self.base_domains.items()}
        
        # Only activate constraints present in the explanation
        active_relations = []
        for rel in self.relations:
            if rel.id in explanation.constraints:
                active_relations.append(ActiveRelation(rel))
                
        gac = GAC(self.variables, filtered_domains, active_relations)
        success = gac.enforce()
        
        # If success is False, a wipeout occurred somewhere. 
        # We specifically check if wipeout_var_id was wiped out.
        if filtered_domains[wipeout_var_id].is_empty():
            return True
            
        return False
