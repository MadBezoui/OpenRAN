import unittest
from src.model.domains import Domain, FilteredDomain
from src.model.relations import Variable, Relation, ActiveRelation
from src.propagation.gac import GAC

class TestGAC(unittest.TestCase):
    def test_simple_arc_consistency(self):
        # Two variables D1 = {0, 1}, D2 = {0, 1}
        v1 = Variable(id=1, name="v1")
        v2 = Variable(id=2, name="v2")
        
        d1 = FilteredDomain(Domain([0, 1]))
        d2 = FilteredDomain(Domain([0, 1]))
        
        # Relation R = {(0, 1), (1, 0)} (not equal)
        rel = Relation(id=1, name="r1", scope=[1, 2], allowed_tuples={(0, 1), (1, 0)})
        active_rel = ActiveRelation(rel)
        
        gac = GAC([v1, v2], {1: d1, 2: d2}, [active_rel])
        success = gac.enforce()
        
        self.assertTrue(success)
        self.assertEqual(len(d1), 2)
        self.assertEqual(len(d2), 2)
        
    def test_value_removal(self):
        # D1 = {0, 1, 2}, D2 = {0, 1}
        # R = {(0, 1), (1, 0)}
        v1 = Variable(id=1, name="v1")
        v2 = Variable(id=2, name="v2")
        
        d1 = FilteredDomain(Domain([0, 1, 2]))
        d2 = FilteredDomain(Domain([0, 1]))
        
        rel = Relation(id=1, name="r1", scope=[1, 2], allowed_tuples={(0, 1), (1, 0)})
        active_rel = ActiveRelation(rel)
        
        gac = GAC([v1, v2], {1: d1, 2: d2}, [active_rel])
        success = gac.enforce()
        
        self.assertTrue(success)
        # 2 should be removed from D1
        self.assertEqual(len(d1), 2)
        self.assertFalse(d1.contains(2))
        self.assertTrue(d1.contains(0))
        self.assertTrue(d1.contains(1))
        
    def test_wipeout(self):
        # D1 = {2}, D2 = {0, 1}
        # R = {(0, 1), (1, 0)}
        v1 = Variable(id=1, name="v1")
        v2 = Variable(id=2, name="v2")
        
        d1 = FilteredDomain(Domain([2]))
        d2 = FilteredDomain(Domain([0, 1]))
        
        rel = Relation(id=1, name="r1", scope=[1, 2], allowed_tuples={(0, 1), (1, 0)})
        active_rel = ActiveRelation(rel)
        
        gac = GAC([v1, v2], {1: d1, 2: d2}, [active_rel])
        success = gac.enforce()
        
        self.assertFalse(success)
        self.assertTrue(d1.is_empty())

if __name__ == '__main__':
    unittest.main()
