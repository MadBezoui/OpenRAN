import numpy as np
import random
import math
from typing import Dict, Any, List
from src.model.relations import Variable

class NetworkSimulator:
    """
    Synthetic O-RAN network simulator for evaluating physical KPMs.
    """
    def __init__(self, num_cells=10, num_users=100, traffic_load=0.6, mobility_speed=3.0, seed=42):
        self.num_cells = num_cells
        self.num_users = num_users
        self.traffic_load = traffic_load
        self.mobility_speed = mobility_speed
        self.seed = seed
        rng = np.random.RandomState(seed)

        self.cell_positions = rng.rand(num_cells, 2) * 1000.0
        self.user_positions = rng.rand(num_users, 2) * 1000.0

        self.N0 = 1e-13
        self.bandwidth = 10e6
        self.P0 = 20.0
        self.P_tx_max = 40.0

    def path_loss(self, dist):
        return np.maximum(1.0, dist ** 2.5)

    def _decode_cell_actions(self, assignment: Dict[int, Any], variables: List[Variable], dsize_map: Dict[int, int]):
        pow_acc = [[] for _ in range(self.num_cells)]
        rb_acc = [[] for _ in range(self.num_cells)]
        ho_acc = [[] for _ in range(self.num_cells)]
        
        var_map = {v.id: v for v in variables}

        for v_id, val in assignment.items():
            if v_id not in var_map: continue
            var = var_map[v_id]
            parts = var.name.split('_')
            if len(parts) < 3 or parts[0] != "cell":
                continue
            try:
                cell_idx = int(parts[1]) % self.num_cells
            except ValueError:
                continue
                
            atype = parts[2]
            dsize = max(1, dsize_map.get(v_id, 1) - 1)
            
            # Use safe normalization in case value is non-numeric, but we assume domains are ranges of integers
            try:
                norm = float(val) / dsize
            except Exception:
                norm = 0.5
                
            if atype in ("pc", "power", "cov", "es"):
                pow_acc[cell_idx].append(norm)
            elif atype in ("ra", "resource", "rb"):
                rb_acc[cell_idx].append(norm)
            elif atype in ("mob", "ho", "lb"):
                ho_acc[cell_idx].append(norm)

        powers = np.full(self.num_cells, self.P_tx_max)
        rbs = np.ones(self.num_cells)
        ho_offsets = np.zeros(self.num_cells)
        for c in range(self.num_cells):
            if pow_acc[c]:
                powers[c] = self.P_tx_max * (0.4 + 0.6 * float(np.mean(pow_acc[c])))
            if rb_acc[c]:
                rbs[c] = 0.3 + 0.7 * float(np.mean(rb_acc[c]))
            if ho_acc[c]:
                ho_offsets[c] = (float(np.mean(ho_acc[c])) - 0.5) * 12.0
        return powers, rbs, ho_offsets

    def compute_kpis(self, assignment: Dict[int, Any], variables: List[Variable], dsize_map: Dict[int, int]):
        if not assignment:
            return {"throughput_mbps": 0.0, "energy_per_bit": float('inf'),
                    "hof_rate": 1.0, "jain_fairness": 0.0}

        powers, rbs, ho_offsets = self._decode_cell_actions(assignment, variables, dsize_map)

        user_throughputs = []
        for u in range(self.num_users):
            dists = np.linalg.norm(self.cell_positions - self.user_positions[u], axis=1)
            rx_powers = powers / self.path_loss(dists)
            perceived = rx_powers * (10.0 ** (ho_offsets / 10.0))
            best_cell = int(np.argmax(perceived))
            signal = rx_powers[best_cell]
            interference = np.sum(rx_powers) - signal
            sinr = signal / (self.N0 + interference)
            capacity = rbs[best_cell] * self.bandwidth * math.log2(1.0 + sinr)
            actual = min(capacity, 150e6 * self.traffic_load)
            user_throughputs.append(actual / 1e6)

        user_throughputs = np.array(user_throughputs)
        avg_throughput = float(np.mean(user_throughputs))
        denom = self.num_users * float(np.sum(np.square(user_throughputs)))
        jain = (float(np.sum(user_throughputs)) ** 2) / denom if denom > 0 else 0.0

        total_energy = float(np.sum(self.P0 + powers))
        energy_per_bit = (total_energy / (avg_throughput * 1e6)) if avg_throughput > 0 else float('inf')

        base_hof = 0.02 * (self.mobility_speed / 3.0 + 1e-9)
        offset_penalty = float(np.mean(np.abs(ho_offsets))) * 0.01
        hof_rate = float(min(1.0, base_hof + offset_penalty))

        return {
            "throughput_mbps": avg_throughput,
            "energy_per_bit": energy_per_bit,
            "hof_rate": hof_rate,
            "jain_fairness": jain,
        }
