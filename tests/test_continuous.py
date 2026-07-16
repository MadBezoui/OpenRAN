import unittest
from src.model.domains import Domain, FilteredDomain
from src.model.relations import Variable, Relation, ActiveRelation
from src.continuous.consensus import ContinuousConsensus
from src.continuous.decoder import Decoder
from src.verification.verifier import Verifier
from src.continuous.diagnostics import Diagnostics

class TestContinuous(unittest.TestCase):
    def test_continuous_consensus(self):
        v1 = Variable(id=1, name="v1")
        v2 = Variable(id=2, name="v2")
        
        d1 = FilteredDomain(Domain([0, 1]))
        d2 = FilteredDomain(Domain([0, 1]))
        
        # We will create a relation that favors (0, 0) slightly over others, but for now we just use a hard relation
        rel = Relation(id=1, name="r1", scope=[1, 2], allowed_tuples={(0, 0), (1, 1)})
        active_rel = ActiveRelation(rel)
        
        consensus = ContinuousConsensus([v1, v2], {1: d1, 2: d2}, [active_rel])
        residual = consensus.solve(max_iter=10)
        
        decoder = Decoder(consensus)
        assignment = decoder.decode()
        
        self.assertIn(assignment[1], [0, 1])
        self.assertEqual(assignment[1], assignment[2])
        
        verifier = Verifier({1: Domain([0, 1]), 2: Domain([0, 1])}, [rel])
        diag = Diagnostics(consensus, verifier)
        result = diag.diagnose(assignment, "ctx")
        
        self.assertTrue(result["is_valid"])

if __name__ == '__main__':
    unittest.main()
