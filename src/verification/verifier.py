
import time
import json
import hashlib
from typing import Dict, List, Any, Tuple
from src.model.domains import Domain
from src.model.relations import Relation

class Verifier:
    """
    Independent decision verifier to ensure no unverified action is forwarded to the E2 interface.
    """
    def __init__(self, base_domains: Dict[int, Domain], hard_relations: List[Relation]):
        self.base_domains = base_domains
        self.hard_relations = hard_relations
        self.model_hash = "mh" + str(len(base_domains) + len(hard_relations)) # simplistic hash
        
    def verify(self, assignment: Dict[int, Any], context_id: str, expected_context_id: str, return_cert: bool = False) -> Any:
        """
        Verifies if an assignment satisfies all hard constraints and domains.
        """
        t0 = time.monotonic_ns()
        
        # 1. Verify context freshness
        if context_id != expected_context_id:
            if return_cert: return False, None
            return False
            
        # 2. Verify all variables are assigned and in their base domains
        for var_id, domain in self.base_domains.items():
            if var_id not in assignment:
                if return_cert: return False, None
                return False
            if not domain.contains(assignment[var_id]):
                if return_cert: return False, None
                return False
                
        # 3. Verify all hard relations
        for rel in self.hard_relations:
            if not rel.is_hard:
                continue
            try:
                tup = tuple(assignment[vid] for vid in rel.scope)
            except KeyError:
                if return_cert: return False, None
                return False
            if not rel.is_allowed(tup):
                if return_cert: return False, None
                return False
                
        verify_time = time.monotonic_ns() - t0
        
        if not return_cert:
            return True
            
        # Build Certificate
        cert = {
            "context_id": context_id,
            "model_hash": self.model_hash,
            "assignment": assignment,
            "timestamp": time.time(),
            "verify_time_ns": verify_time
        }
        
        t1 = time.monotonic_ns()
        cert_str = json.dumps(cert)
        build_time = time.monotonic_ns() - t1
        
        cert["size_bytes"] = len(cert_str)
        cert["overhead_ns"] = verify_time + build_time
        return True, cert
