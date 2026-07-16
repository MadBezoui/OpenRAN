from src.generators.infeasible_generator import generate_wipeout_instance
from src.propagation.gac import GAC
from src.propagation.explanations import extract_wipeout_explanation
from src.propagation.explanation_checker import ExplanationChecker
from src.model.domains import FilteredDomain
from src.model.relations import ActiveRelation

def run_sanity_tests():
    variables, domains, relations = generate_wipeout_instance()
    
    filtered_domains = {vid: FilteredDomain(dom) for vid, dom in domains.items()}
    active_relations = [ActiveRelation(rel) for rel in relations]
    
    gac = GAC(variables, filtered_domains, active_relations)
    success = gac.enforce()
    
    assert not success, "Expected wipeout, but GAC succeeded!"
    
    wipeout_var = next(vid for vid, dom in filtered_domains.items() if dom.is_empty())
    
    # Extract explanation
    explanation = extract_wipeout_explanation(filtered_domains, wipeout_var)
    
    # 1. Test Valid Explanation Acceptance
    checker = ExplanationChecker(variables, domains, relations)
    valid_explanation_accepted = checker.check_wipeout(explanation, wipeout_var)
    assert valid_explanation_accepted, "Valid explanation was rejected!"
    
    # 2. Test Corrupted Explanation Rejection
    # Corrupt the explanation by dropping constraints
    explanation.constraints = frozenset()
    corrupted_explanation_accepted = checker.check_wipeout(explanation, wipeout_var)
    assert not corrupted_explanation_accepted, "Corrupted explanation was accepted!"
    
    print("Sanity checks passed: valid_explanation_acceptance_rate = 100%, corrupted_explanation_rejection_rate = 100%")

if __name__ == "__main__":
    run_sanity_tests()
