from typing import Tuple, List, Dict
from src.model.domains import Domain
from src.model.relations import Variable, Relation

def generate_wipeout_instance() -> Tuple[List[Variable], Dict[int, Domain], List[Relation]]:
    """
    Generates a trivially infeasible instance to test wipeout explanations.
    D1 = {0}, D2 = {1}, R = { (a, b) | a == b } -> wipeout!
    """
    v1 = Variable(id=1, name="v1")
    v2 = Variable(id=2, name="v2")
    
    domains = {
        1: Domain([0]),
        2: Domain([1])
    }
    
    # Require v1 == v2
    rel = Relation(id=1, name="eq", scope=[1, 2], allowed_tuples={(0, 0), (1, 1)}, is_hard=True)
    
    return [v1, v2], domains, [rel]
