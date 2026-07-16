import unittest
from src.model.domains import Domain, FilteredDomain
from src.model.relations import Variable, Relation, ActiveRelation
from src.propagation.incremental_gac import IncrementalGAC

class TestIncrementalGAC(unittest.TestCase):
    def test_incremental_enforce(self):
        v1 = Variable(id=1, name="v1")
        v2 = Variable(id=2, name="v2")
        
        d1 = FilteredDomain(Domain([0, 1]))
        d2 = FilteredDomain(Domain([0, 1]))
        
        rel = Relation(id=1, name="r1", scope=[1, 2], allowed_tuples={(0, 1), (1, 0)})
        active_rel = ActiveRelation(rel)
        
        gac = IncrementalGAC([v1, v2], {1: d1, 2: d2}, [active_rel])
        
        # Suppose v1 is modified to only have {0}
        d1.remove_value(1)
        
        success = gac.enforce_incremental(modified_vars={1}, modified_rels=set())
        
        self.assertTrue(success)
        self.assertFalse(d2.contains(0)) # 0 should be removed from d2 since (0, 0) is not in rel
        self.assertTrue(d2.contains(1))

if __name__ == '__main__':
    unittest.main()
