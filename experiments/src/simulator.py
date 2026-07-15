import numpy as np
import random
import math
from .models import Variable, Constraint, Problem


class NetworkSimulator:
    """
    Synthetic O-RAN network simulator for evaluating physical KPMs.

    The simulator maps a discrete coordination decision (an assignment of
    xApp actions) onto pseudo-physical cell parameters (transmit power,
    radio-resource fraction, handover offset) and derives SINR, throughput,
    energy, fairness and handover-failure indicators. KPMs therefore depend
    on the chosen assignment, so different coordination methods yield
    different network-level performance.
    """

    def __init__(self, num_cells=10, num_users=100, traffic_load=0.6,
                 mobility_speed=3.0, seed=42):
        self.num_cells = num_cells
        self.num_users = num_users
        self.traffic_load = traffic_load
        self.mobility_speed = mobility_speed
        self.seed = seed
        rng = np.random.RandomState(seed)

        # Grid placement 1 km x 1 km
        self.cell_positions = rng.rand(num_cells, 2) * 1000.0
        self.user_positions = rng.rand(num_users, 2) * 1000.0

        # Channel / system parameters
        self.N0 = 1e-13            # thermal noise
        self.bandwidth = 10e6      # 10 MHz
        self.P0 = 20.0             # static power per cell (W)
        self.P_tx_max = 40.0       # maximum transmit power (W)

    def path_loss(self, dist):
        return np.maximum(1.0, dist ** 2.5)

    def _decode_cell_actions(self, assignment, problem):
        """
        Aggregate the assignment into per-cell physical settings.
        Returns normalized power, resource-block and handover-offset arrays.
        Each is derived from the mean of the relevant action variables that
        target a given cell, so the settings genuinely depend on the decision.
        """
        pow_acc = [[] for _ in range(self.num_cells)]
        rb_acc = [[] for _ in range(self.num_cells)]
        ho_acc = [[] for _ in range(self.num_cells)]

        for v_id, val in assignment.items():
            var = problem.get_var(v_id)
            parts = var.name.split('_')
            if len(parts) < 3 or parts[0] != "cell":
                continue
            try:
                cell_idx = int(parts[1]) % self.num_cells
            except ValueError:
                continue
            atype = parts[2]
            dsize = max(1, len(var.domain) - 1)
            norm = val / dsize  # in [0, 1]
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
                ho_offsets[c] = (float(np.mean(ho_acc[c])) - 0.5) * 12.0  # dB
        return powers, rbs, ho_offsets

    def compute_kpis(self, assignment, problem):
        if not assignment:
            return {"throughput_mbps": 0.0, "energy_per_bit": float('inf'),
                    "hof_rate": 1.0, "jain_fairness": 0.0}

        powers, rbs, ho_offsets = self._decode_cell_actions(assignment, problem)

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
            user_throughputs.append(actual / 1e6)  # Mbps

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


# ------------------------------------------------------------------
# Instance generation
# ------------------------------------------------------------------
# Action-type tokens are embedded in variable names so that the network
# simulator can map decisions to physical cell parameters.
_ACTION_TYPES = ["pc", "ra", "mob", "slot"]

# Scenario presets reflecting the five conflict regimes of the paper.
# Each preset controls the number of xApp action variables, the action-domain
# size, the number of conflict relations, and the fraction of symmetric
# (disequality / "separation") relations that induce fractional stalls.
SCENARIO_PRESETS = {
    "S1": dict(num_vars=12, domain_size=3, num_constraints=10, sym_frac=0.7),
    "S2": dict(num_vars=18, domain_size=4, num_constraints=16, sym_frac=0.3),
    "S3": dict(num_vars=16, domain_size=4, num_constraints=14, sym_frac=0.5),
    "S4": dict(num_vars=18, domain_size=4, num_constraints=18, sym_frac=0.6),
    "S5": dict(num_vars=30, domain_size=4, num_constraints=32, sym_frac=0.5),
}


def generate_instance(num_vars, domain_size, num_constraints, seed=0,
                      sym_frac=0.5, num_cells=10):
    """
    Generate a synthetic, guaranteed-feasible xApp coordination instance.

    A hidden feasible target assignment is planted first; every generated
    hard relation is constructed so that the target satisfies it. This
    guarantees at least one conflict-free decision exists (so a complete
    solver reaches ~100% feasibility), while a controllable fraction of
    symmetric disequality relations induces fractional stalls in the
    continuous relaxation.
    """
    rng = random.Random(seed)
    problem = Problem()

    target = {}
    for i in range(num_vars):
        domain = list(range(domain_size))
        atype = _ACTION_TYPES[i % len(_ACTION_TYPES)]
        cell = i % num_cells
        var = Variable(id=i, name=f"cell_{cell}_{atype}_{i}", domain=domain)
        for a in domain:
            var.utilities[a] = rng.random()
        var.priority = rng.random()
        problem.add_variable(var)
        target[i] = rng.choice(domain)

    for c_id in range(num_constraints):
        if num_vars < 2:
            break
        scope = rng.sample(range(num_vars), 2)
        d0 = problem.get_var(scope[0]).domain
        d1 = problem.get_var(scope[1]).domain
        ta, tb = target[scope[0]], target[scope[1]]

        if rng.random() < sym_frac and ta != tb:
            # Symmetric separation relation: the two actions must differ.
            # The planted target already satisfies it (ta != tb).
            allowed = {(a, b) for a in d0 for b in d1 if a != b}
        else:
            # General random relation (~35% tightness); force target in.
            allowed = {(a, b) for a in d0 for b in d1 if rng.random() < 0.35}
            allowed.add((ta, tb))

        cons = Constraint(id=c_id, name=f"c_{c_id}", scope=list(scope),
                          allowed_tuples=allowed)
        problem.add_constraint(cons)

    return problem


# Backwards-compatible alias used by older callers.
def generate_random_problem(num_vars, domain_size, num_constraints, seed=0):
    return generate_instance(num_vars, domain_size, num_constraints, seed=seed)
