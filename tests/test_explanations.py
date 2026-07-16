import unittest
from src.model.domains import Domain, FilteredDomain
from src.model.relations import Variable, Relation, ActiveRelation
from src.propagation.gac import GAC
from src.propagation.explanations import extract_wipeout_explanation
from src.propagation.explanation_checker import ExplanationChecker

class TestExplanations(unittest.TestCase):
    def test_wipeout_explanation(self):
        v1 = Variable(id=1, name="v1")
        v2 = Variable(id=2, name="v2")
        v3 = Variable(id=3, name="v3")
        
        d1 = FilteredDomain(Domain([0]))
        d2 = FilteredDomain(Domain([1]))
        d3 = FilteredDomain(Domain([0, 1]))
        
        # r1: v1 != v2 (always true here since 0 != 1)
        # r2: v1 == v3
        # r3: v2 == v3
        # This will wipe out v3, because v3 must be 0 (from r2) and 1 (from r3).
        rel1 = Relation(id=1, name="r1", scope=[1, 2], allowed_tuples={(0, 1)})
        rel2 = Relation(id=2, name="r2", scope=[1, 3], allowed_tuples={(0, 0), (1, 1)})
        rel3 = Relation(id=3, name="r3", scope=[2, 3], allowed_tuples={(0, 0), (1, 1)})
        
        gac = GAC([v1, v2, v3], {1: d1, 2: d2, 3: d3}, [ActiveRelation(rel1), ActiveRelation(rel2), ActiveRelation(rel3)])
        success = gac.enforce()
        self.assertFalse(success)
        
        explanation = extract_wipeout_explanation({1: d1, 2: d2, 3: d3}, 3)
        self.assertTrue(2 in explanation.constraints)
        self.assertTrue(3 in explanation.constraints)
        
        checker = ExplanationChecker([v1, v2, v3], {1: Domain([0]), 2: Domain([1]), 3: Domain([0, 1])}, [rel1, rel2, rel3])
        self.assertTrue(checker.check_wipeout(explanation, 3))
        
        # Corrupted explanation: only r2
        explanation.constraints = frozenset([2])
        self.assertFalse(checker.check_wipeout(explanation, 3))

if __name__ == '__main__':
    unittest.main()
