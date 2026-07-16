import unittest
from src.model.domains import Domain
from src.model.relations import Relation
from src.verification.verifier import Verifier

class TestVerifier(unittest.TestCase):
    def test_valid_assignment(self):
        d1 = Domain([0, 1])
        d2 = Domain([0, 1])
        rel = Relation(id=1, name="r1", scope=[1, 2], allowed_tuples={(0, 1), (1, 0)}, is_hard=True)
        
        verifier = Verifier({1: d1, 2: d2}, [rel])
        
        # Valid assignment
        self.assertTrue(verifier.verify({1: 0, 2: 1}, "ctx1", "ctx1"))
        
    def test_invalid_context(self):
        d1 = Domain([0, 1])
        rel = Relation(id=1, name="r1", scope=[1], allowed_tuples={(0,)}, is_hard=True)
        verifier = Verifier({1: d1}, [rel])
        
        self.assertFalse(verifier.verify({1: 0}, "ctx_old", "ctx_new"))
        
    def test_out_of_domain(self):
        d1 = Domain([0, 1])
        rel = Relation(id=1, name="r1", scope=[1], allowed_tuples={(0,), (1,)}, is_hard=True)
        verifier = Verifier({1: d1}, [rel])
        
        # 2 is not in domain
        self.assertFalse(verifier.verify({1: 2}, "ctx1", "ctx1"))
        
    def test_hard_constraint_violation(self):
        d1 = Domain([0, 1])
        d2 = Domain([0, 1])
        rel = Relation(id=1, name="r1", scope=[1, 2], allowed_tuples={(0, 1), (1, 0)}, is_hard=True)
        
        verifier = Verifier({1: d1, 2: d2}, [rel])
        
        # Invalid assignment (0, 0)
        self.assertFalse(verifier.verify({1: 0, 2: 0}, "ctx1", "ctx1"))

if __name__ == '__main__':
    unittest.main()
