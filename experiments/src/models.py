import numpy as np
from dataclasses import dataclass, field
from typing import List, Set, Tuple, Dict, Any

@dataclass
class Variable:
    id: int
    name: str
    domain: List[Any]
    priority: float = 1.0
    utilities: Dict[Any, float] = field(default_factory=dict)

@dataclass
class Constraint:
    id: int
    name: str
    scope: List[int]
    allowed_tuples: Set[Tuple[Any, ...]]
    is_hard: bool = True
    weight: float = 1.0
    tuple_utilities: Dict[Tuple[Any, ...], float] = field(default_factory=dict)
    gamma: float = 0.0

@dataclass
class Problem:
    variables: Dict[int, Variable] = field(default_factory=dict)
    constraints: Dict[int, Constraint] = field(default_factory=dict)
    
    def add_variable(self, var: Variable):
        self.variables[var.id] = var
        
    def add_constraint(self, cons: Constraint):
        self.constraints[cons.id] = cons
        
    def get_var(self, var_id: int) -> Variable:
        return self.variables[var_id]
        
    def get_incident_constraints(self, var_id: int) -> List[Constraint]:
        return [c for c in self.constraints.values() if var_id in c.scope]
