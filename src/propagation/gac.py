from typing import Dict, List, Set, Tuple, Any
import collections

from src.model.domains import FilteredDomain
from src.model.relations import ActiveRelation, Variable

class GAC:
    """
    Generalized Arc Consistency (GAC) for positive table constraints.
    Uses a constraint-based worklist and runs to the (unique) GAC fixpoint.
    """
    def __init__(self, variables: List[Variable], domains: Dict[int, FilteredDomain], relations: List[ActiveRelation]):
        self.variables = variables
        self.domains = domains
        self.relations = relations
        self.var_to_relations: Dict[int, List[ActiveRelation]] = collections.defaultdict(list)
        for r in self.relations:
            for v_id in r.relation.scope:
                self.var_to_relations[v_id].append(r)

    def enforce(self, seed_relations=None) -> bool:
        """
        Enforces GAC. Returns True if successful (no wipeout), False on wipeout.
        A constraint-based worklist guarantees the fixpoint is reached: whenever a
        variable domain shrinks, every incident constraint is re-queued. When
        ``seed_relations`` is given, only those constraints seed the worklist
        (incremental propagation from a warm, previously consistent state).
        """
        seed = self.relations if seed_relations is None else seed_relations
        queue = collections.deque(seed)
        in_queue = set(id(r) for r in seed)

        while queue:
            active_rel = queue.popleft()
            in_queue.discard(id(active_rel))

            revised_vars = self._revise(active_rel)
            if revised_vars is None:
                return False  # domain wipeout
            for rev_v_id in revised_vars:
                for r in self.var_to_relations[rev_v_id]:
                    if id(r) not in in_queue:
                        in_queue.add(id(r))
                        queue.append(r)
        return True

    def _revise(self, active_rel: ActiveRelation):
        """
        Revises one relation: prunes tuples inconsistent with current domains and
        removes unsupported values. Returns the list of variable ids whose domains
        shrank, or None if a wipeout occurred.
        """
        revised_vars = []

        invalid_tuples = []
        for tup in active_rel.active_tuples:
            for var_id, idx in active_rel.var_indices.items():
                if not self.domains[var_id].contains(tup[idx]):
                    invalid_tuples.append(tup)
                    break
        for tup in invalid_tuples:
            active_rel.remove_tuple(tup)

        for var_id in active_rel.relation.scope:
            invalid_values = []
            for val in self.domains[var_id].active_values:
                if not active_rel.has_support(var_id, val):
                    invalid_values.append(val)
            if invalid_values:
                for val in invalid_values:
                    self.domains[var_id].remove_value(val, reason={"type": "GAC_REMOVAL", "relation": active_rel.relation.id})
                if self.domains[var_id].is_empty():
                    return None
                revised_vars.append(var_id)
        return revised_vars
