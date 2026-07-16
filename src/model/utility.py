from typing import Dict

class UtilityMapper:
    """
    Maps physical network KPMs to a unified utility score.
    """
    def __init__(self, 
                 w_throughput: float = 1.0, 
                 w_energy: float = 1.0, 
                 w_handover: float = 1.0, 
                 w_sla: float = 2.0):
        self.w_throughput = w_throughput
        self.w_energy = w_energy
        self.w_handover = w_handover
        self.w_sla = w_sla

    def compute_utility(self, kpis: Dict[str, float]) -> float:
        """
        Computes the utility score based on KPIs.
        Higher is better.
        """
        # Normalize KPIs loosely (assuming max throughput ~ 100, energy_per_bit ~ 1e-6, hof_rate in [0, 1])
        # For a synthetic setup, we use these simple scaling factors
        norm_throughput = min(kpis.get("throughput_mbps", 0.0) / 100.0, 1.0)
        
        energy_per_bit = kpis.get("energy_per_bit", 0.0)
        norm_energy = min(energy_per_bit * 1e6, 1.0) if energy_per_bit != float('inf') else 1.0
        
        norm_hof = kpis.get("hof_rate", 1.0)
        
        utility = (self.w_throughput * norm_throughput 
                   - self.w_energy * norm_energy 
                   - self.w_handover * norm_hof)
                   
        return utility
