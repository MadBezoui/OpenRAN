from typing import Dict, Any

from src.continuous.consensus import ContinuousConsensus
from src.continuous.decoder import Decoder
from src.verification.verifier import Verifier

class Diagnostics:
    """
    Identifies operational stalls and invalid decodes.
    """
    def __init__(self, consensus: ContinuousConsensus, verifier: Verifier):
        self.consensus = consensus
        self.verifier = verifier
        
    def get_fractionality(self) -> float:
        """
        Calculates the average fractionality across all active variables.
        Fractionality for a variable is 1.0 - max(probability).
        """
        n = len(self.consensus.variables)
        if n == 0: return 0.0
        
        score = 0.0
        for var_id in self.consensus.marginals:
            probs = self.consensus.marginals[var_id]
            if not probs:
                continue
            max_p = max(probs.values())
            score += (1.0 - max_p)
            
        return score / n
        
    def diagnose(self, assignment: Dict[int, Any], context_id: str, threshold: float = 0.1) -> Dict[str, bool]:
        """
        Diagnoses if the result is an operational stall or an invalid non-stalled decode.
        """
        is_valid = self.verifier.verify(assignment, context_id, context_id)
        frac = self.get_fractionality()
        is_stalled = frac > threshold
        
        return {
            "is_valid": is_valid,
            "is_stalled": is_stalled,
            "operational_stall": is_stalled and not is_valid,
            "invalid_non_stalled_decode": not is_stalled and not is_valid
        }
