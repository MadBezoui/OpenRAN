import csv, os, sys, time, random
from src.model.domains import Domain, FilteredDomain
from src.model.relations import Variable, Relation, ActiveRelation
from src.propagation.gac import GAC
from src.generators.static_generator import generate_static_instance, SCENARIO_PRESETS

SCENARIOS = ["S1","S2","S3","S4","S5"]
EPOCHS = 100

def sched(e):
    if e == 0: return "base"
    if e <= 5: return "restrictive"
    if e <= 10: return "relaxed"
    if e <= 15: return "utility-only"
    return "mixed"

def main():
    scenario = sys.argv[1]; ep0, ep1 = int(sys.argv[2]), int(sys.argv[3])
    out = "artifacts/raw/dynamic_results.csv"
    new = not os.path.exists(out) or os.path.getsize(out) == 0
    f = open(out, "a", newline="")
    fields = ["scenario_id","episode_id","epoch_id","update_type","recompute_time_ns",
              "incremental_time_ns","restored","domain_agree","values_after","tuples_after","num_variables"]
    w = csv.DictWriter(f, fieldnames=fields)
    if new: w.writeheader()

    for episode in range(ep0, ep1):
        seed = 1000 + episode
        variables, domains, relations, planted = generate_static_instance(scenario, seed)
        d = SCENARIO_PRESETS[scenario]["domain_size"]
        maxdom = {v.id: set(range(d)) for v in variables}
        maxallow = {r.id: set(r.allowed_tuples) for r in relations}
        cur_dom = {v.id: set(domains[v.id].base_values) for v in variables}
        cur_allowed = {r.id: set(r.allowed_tuples) for r in relations}
        rel_scope = {r.id: list(r.scope) for r in relations}
        rel_ids = [r.id for r in relations]
        planted_tuple = {rid: tuple(planted[v] for v in rel_scope[rid]) for rid in rel_ids}

        # persistent incremental state, warm base fixpoint
        ifd = {vid: FilteredDomain(Domain(sorted(cur_dom[vid]))) for vid in cur_dom}
        iar = {rid: ActiveRelation(Relation(id=rid, name="c", scope=rel_scope[rid],
               allowed_tuples=set(cur_allowed[rid]), is_hard=True)) for rid in rel_ids}
        iars = list(iar.values())
        GAC(variables, ifd, iars).enforce()

        for epoch in range(EPOCHS):
            ut = sched(epoch); restored = 0
            seedset = set(); relax_v = set(); relax_r = set()
            if epoch > 0 and ut != "utility-only":
                trng = random.Random(seed * 131 + epoch)
                dorest = ut in ("restrictive", "mixed"); dorelax = ut in ("relaxed", "mixed")
                for vid in cur_dom:
                    if trng.random() < 0.1:
                        # never remove the planted value -> stays feasible
                        removable = sorted(cur_dom[vid] - {planted[vid]})
                        if dorest and removable and trng.random() < 0.5:
                            val = trng.choice(removable); cur_dom[vid].discard(val)
                            ifd[vid].base_domain._base_set.discard(val)
                            ifd[vid].base_domain.base_values = tuple(sorted(ifd[vid].base_domain._base_set))
                            ifd[vid].active_values.discard(val)
                            for r in iars:
                                if vid in r.relation.scope: seedset.add(r)
                        elif dorelax and cur_dom[vid] != maxdom[vid]:
                            val = trng.choice(sorted(maxdom[vid] - cur_dom[vid])); cur_dom[vid].add(val)
                            ifd[vid].base_domain._base_set.add(val)
                            ifd[vid].base_domain.base_values = tuple(sorted(ifd[vid].base_domain._base_set))
                            restored += 1; relax_v.add(vid)
                for rid in rel_ids:
                    if trng.random() < 0.1:
                        removable = sorted(cur_allowed[rid] - {planted_tuple[rid]})
                        if dorest and removable and trng.random() < 0.5:
                            t = trng.choice(removable); cur_allowed[rid].discard(t)
                            iar[rid].active_tuples.discard(t); seedset.add(iar[rid])
                        elif dorelax and cur_allowed[rid] != maxallow[rid]:
                            t = trng.choice(sorted(maxallow[rid] - cur_allowed[rid])); cur_allowed[rid].add(t)
                            relax_r.add(rid)
                if relax_v or relax_r:
                    comp = set(relax_v)
                    for rid in relax_r: comp.update(rel_scope[rid])
                    ch = True
                    while ch:
                        ch = False
                        for rid in rel_ids:
                            if any(v in comp for v in rel_scope[rid]):
                                for v in rel_scope[rid]:
                                    if v not in comp: comp.add(v); ch = True
                    for rid in rel_ids:
                        if any(v in comp for v in rel_scope[rid]):
                            iar[rid].active_tuples = set(cur_allowed[rid]); seedset.add(iar[rid])
                    for vid in comp:
                        ifd[vid].active_values = set(cur_dom[vid])

            # incremental (timed)
            t0 = time.perf_counter_ns()
            if epoch == 0:
                GAC(variables, ifd, iars).enforce()
            else:
                GAC(variables, ifd, iars).enforce(seed_relations=list(seedset) if seedset else [])
            inc_t = time.perf_counter_ns() - t0

            # full recompute (timed)
            rfd = {vid: FilteredDomain(Domain(sorted(cur_dom[vid]))) for vid in cur_dom}
            rars = [ActiveRelation(Relation(id=rid, name="c", scope=rel_scope[rid],
                    allowed_tuples=set(cur_allowed[rid]), is_hard=True)) for rid in rel_ids]
            t1 = time.perf_counter_ns()
            GAC(variables, rfd, rars).enforce()
            rc_t = time.perf_counter_ns() - t1

            agree = all(ifd[vid].active_values == rfd[vid].active_values for vid in cur_dom)
            va = sum(len(ifd[vid].active_values) for vid in cur_dom)
            ta = sum(len(a.active_tuples) for a in iars)
            w.writerow({"scenario_id": scenario, "episode_id": episode, "epoch_id": epoch,
                        "update_type": ut, "recompute_time_ns": rc_t, "incremental_time_ns": inc_t,
                        "restored": restored, "domain_agree": agree, "values_after": va,
                        "tuples_after": ta, "num_variables": len(variables)})
        f.flush()
    f.close(); print(f"done {scenario} {ep0}-{ep1}", flush=True)

if __name__ == "__main__":
    main()
