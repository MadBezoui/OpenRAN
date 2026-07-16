import random
from typing import Dict, List, Tuple
from src.model.domains import Domain
from src.model.relations import Variable, Relation
from src.generators.static_generator import generate_static_instance, SCENARIO_PRESETS

def generate_dynamic_transition(variables: List[Variable], domains: Dict[int, Domain], relations: List[Relation], update_ratio: float, seed: int) -> Tuple[Dict[int, Domain], List[Relation]]:
    """
    Applies a random transition (restriction, relaxation, or mixed) to domains and relations.
    """
    rng = random.Random(seed)
    
    new_domains = {vid: Domain(list(d.base_values)) for vid, d in domains.items()}
    new_relations = []
    
    # Restrict/relax domains
    for vid, dom in new_domains.items():
        if rng.random() < update_ratio:
            if len(dom.base_values) > 1 and rng.random() < 0.5:
                # Restrict
                val_to_remove = rng.choice(dom.base_values)
                new_vals = list(dom.base_values)
                new_vals.remove(val_to_remove)
                dom.base_values = tuple(new_vals)
            else:
                # Relax (add a value up to some max, let's say domain_size + 1)
                # For simplicity in this mock transition, we'll just skip relaxation if we don't know the original full domain
                pass
                
    # Restrict/relax relations
    for rel in relations:
        if rng.random() < update_ratio:
            new_allowed = set(rel.allowed_tuples)
            if len(new_allowed) > 1 and rng.random() < 0.5:
                # Restrict
                tup_to_remove = rng.choice(list(new_allowed))
                new_allowed.remove(tup_to_remove)
            else:
                # Relax (add a random tuple)
                # Simplified for the mock
                pass
                
            new_rel = Relation(id=rel.id, name=rel.name, scope=rel.scope, allowed_tuples=new_allowed, is_hard=rel.is_hard)
            new_relations.append(new_rel)
        else:
            new_relations.append(rel)
            
    return new_domains, new_relations
