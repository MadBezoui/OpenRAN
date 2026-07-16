from dataclasses import dataclass, field
from typing import List, Any, Set, Dict

@dataclass
class Domain:
    """Represents the finite domain of a variable."""
    base_values: List[Any]
    
    def __post_init__(self):
        # The base values are immutable for a given epoch.
        # We store them as a tuple to ensure they aren't accidentally modified.
        self.base_values = tuple(self.base_values)
        self._base_set = set(self.base_values)
        
    def contains(self, value: Any) -> bool:
        return value in self._base_set
        
    def __len__(self) -> int:
        return len(self.base_values)
        
    def __iter__(self):
        return iter(self.base_values)

class FilteredDomain:
    """Represents the current filtered domain of a variable during propagation."""
    def __init__(self, base_domain: Domain):
        self.base_domain = base_domain
        # Active values are the ones not removed by propagation
        self.active_values: Set[Any] = set(base_domain.base_values)
        # Record reasons for removals for explanation generation
        self.removal_reasons: Dict[Any, Any] = {}
        
    def remove_value(self, value: Any, reason: Any = None) -> bool:
        """Removes a value and records the reason. Returns True if successfully removed (was present)."""
        if value in self.active_values:
            self.active_values.remove(value)
            if reason is not None:
                self.removal_reasons[value] = reason
            return True
        return False
        
    def restore_value(self, value: Any) -> bool:
        """Restores a value (e.g. after a relaxation). Returns True if successfully restored."""
        if value in self.base_domain._base_set and value not in self.active_values:
            self.active_values.add(value)
            if value in self.removal_reasons:
                del self.removal_reasons[value]
            return True
        return False
        
    def contains(self, value: Any) -> bool:
        return value in self.active_values
        
    def is_empty(self) -> bool:
        return len(self.active_values) == 0
        
    def __len__(self) -> int:
        return len(self.active_values)
        
    def __iter__(self):
        return iter(self.active_values)
