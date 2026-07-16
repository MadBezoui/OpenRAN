from typing import Dict, Any

from src.continuous.consensus import ContinuousConsensus

class Decoder:
    """
    Decodes the marginal probabilities into a discrete assignment.
    """
    def __init__(self, consensus: ContinuousConsensus):
        self.consensus = consensus
        
    def decode(self) -> Dict[int, Any]:
        """
        Returns the assignment by taking the argmax of the marginals.
        """
        assignment = {}
        for var_id, probs in self.consensus.marginals.items():
            if not probs:
                continue
            best_a = max(probs.keys(), key=lambda a: probs[a])
            assignment[var_id] = best_a
        return assignment
