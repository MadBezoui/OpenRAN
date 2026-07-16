from dataclasses import dataclass, field
from typing import List, Tuple, Set, Dict, Any

@dataclass
class Variable:
    id: int
    name: str

@dataclass
class Relation:
    """Represents a discrete constraint relation between variables."""
    id: int
    name: str
    scope: List[int] # List of variable IDs
    allowed_tuples: Set[Tuple[Any, ...]]
    is_hard: bool = True
    
    def __post_init__(self):
        self.allowed_tuples = frozenset(self.allowed_tuples)
        self.arity = len(self.scope)
        
    def is_allowed(self, assignment: Tuple[Any, ...]) -> bool:
        return assignment in self.allowed_tuples

class ActiveRelation:
    """Tracks active tuples in a relation during propagation."""
    def __init__(self, relation: Relation):
        self.relation = relation
        self.active_tuples: Set[Tuple[Any, ...]] = set(relation.allowed_tuples)
        # Store index mapping for fast lookups
        self.var_indices = {var_id: idx for idx, var_id in enumerate(relation.scope)}
        
    def remove_tuple(self, tup: Tuple[Any, ...]):
        if tup in self.active_tuples:
            self.active_tuples.remove(tup)
            
    def get_supports(self, var_id: int, value: Any) -> List[Tuple[Any, ...]]:
        if var_id not in self.var_indices:
            return []
        idx = self.var_indices[var_id]
        return [t for t in self.active_tuples if t[idx] == value]
        
    def has_support(self, var_id: int, value: Any) -> bool:
        if var_id not in self.var_indices:
            return False
        idx = self.var_indices[var_id]
        for t in self.active_tuples:
            if t[idx] == value:
                return True
        return False
        
    def get_active_tuple_count(self) -> int:
        return len(self.active_tuples)
