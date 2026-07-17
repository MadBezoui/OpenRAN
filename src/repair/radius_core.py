from typing import Set, Tuple, List
from src.model.relations import Relation


class RadiusCoreBuilder:
    """
    Builds a repair core by expanding radially, in the constraint (hyper)graph,
    from a set of seed variables.

    IMPORTANT (review fix): the seed must be the variables of the *violated*
    constraints, not an arbitrary variable. Seeding from the violated scope
    guarantees that, for radii 0 <= h0 <= h1, the resulting cores are nested
    (A_{h0} subseteq A_{h1}), which is required for a sound comparison against
    the violated-scope and explanation-guided cores.
    """

    def __init__(self, relations: List[Relation]):
        self.relations = relations
        self.rel_map = {r.id: r for r in relations}

    def _incident_rels(self, core_vars: Set[int]) -> Set[int]:
        """Relations sharing at least one variable with the core."""
        return {r.id for r in self.relations
                if any(vid in core_vars for vid in r.scope)}

    def _internal_rels(self, core_vars: Set[int]) -> Set[int]:
        """Relations whose whole scope is inside the core."""
        return {r.id for r in self.relations
                if all(vid in core_vars for vid in r.scope)}

    def build_core_from_vars(self, seed_vars: Set[int], radius: int
                             ) -> Tuple[Set[int], Set[int]]:
        """
        h=0 : exactly the seed variables; relations internal to the seed.
        h>=1: add all variables within `radius` hops of the seed, and every
              relation incident to the resulting variable set.
        """
        core_vars = set(seed_vars)
        for _ in range(radius):
            grown = set(core_vars)
            for r in self.relations:
                if any(vid in core_vars for vid in r.scope):
                    grown.update(r.scope)
            if grown == core_vars:
                break
            core_vars = grown
        if radius == 0:
            core_rels = self._internal_rels(core_vars)
        else:
            core_rels = self._incident_rels(core_vars)
        return core_vars, core_rels
