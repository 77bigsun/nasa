"""Exact small-demand set cover on the supplied 3,317-cell Mars pool."""
from math import isfinite


def network(data, site_id, task_ids):
    if site_id == 'all':
        if task_ids:
            raise ValueError('Global reference uses all 27 scored demands')
        return {'version': data['version'], 'scope': 'global_reference', 'ratio': .9, 'source': 'supplied_global_solution', **data['set_cover']}
    target = data['set_cover']['target_id_to_site_id']
    target_id = next((k for k, v in target.items() if v == site_id), None)
    if target_id is None:
        raise ValueError('Unknown Mars target')
    valid = data['set_cover']['per_target'][target_id]['tests']
    if not task_ids or len(set(task_ids)) != len(task_ids) or any(t not in {'R1','R2','R3','R4','R5','R6'} for t in task_ids):
        raise ValueError('Select distinct Mars tests R1-R6')
    active = [t for t in task_ids if t in valid]
    skipped = [t for t in task_ids if t not in valid]
    pool = data['pool']
    keys = [f'S_{target_id}_{t}' for t in active]
    best = {t: max((r.get(k) for r in pool if r.get(k) is not None), default=None) for t,k in zip(active,keys)}
    thresholds = {t: .9 * best[t] for t in active if best[t] is not None}
    # Identical masks are interchangeable for minimum cardinality. Keep a
    # deterministic quality representative; this does not change the minimum.
    representatives = {}
    for row in pool:
        values = [row.get(k) for k in keys]
        mask = sum(1 << i for i,(t,v) in enumerate(zip(active,values)) if v is not None and isfinite(v) and v >= thresholds.get(t, float('inf')))
        if not mask:
            continue
        quality = sum(v or 0 for v in values)
        previous = representatives.get(mask)
        if previous is None or (quality,row['cell_id']) > (previous[0],previous[1]['cell_id']):
            representatives[mask] = (quality,row)
    # At most five target-specific demands => at most 32 states.
    states = {0: ([],0.)}
    for mask,(quality,row) in sorted(representatives.items()):
        for covered,(rows,q) in list(states.items()):
            union = covered | mask
            proposed = (rows+[row],q+quality)
            old = states.get(union)
            if old is None or (len(proposed[0]),-proposed[1]) < (len(old[0]),-old[1]):
                states[union] = proposed
    full = (1 << len(active))-1
    covered = full if full in states else max(states, key=lambda x: (x.bit_count(),-len(states[x][0])))
    rows = states[covered][0]
    sites = []
    for row in rows:
        assigned = [{'target': target_id, 'test': t, 'score': row[k]} for t,k in zip(active,keys) if row.get(k) is not None and row[k] >= thresholds[t]]
        sites.append({k: row.get(k) for k in ['cell_id','lat','lon','place','known_analog','nearest_known','nearest_known_km']} | {'assigned': assigned})
    return {'version': data['version'], 'scope': site_id, 'source': 'exact_cover_of_supplied_pool', 'ratio': .9,
            'n_requirements': len(active), 'requirements': [f'{target_id} {t}' for t in active],
            'k_star': len(rows), 'sites': sites, 'best_scores': best, 'thresholds': thresholds,
            'skipped': skipped, 'uncoverable': [t for i,t in enumerate(active) if not covered & (1<<i)],
            'pool_cells': len(pool), 'marginal_curve': [{'k': k, 'covered': max((mask.bit_count() for mask,(r,_) in states.items() if len(r)<=k), default=0)} for k in range(1,len(rows)+1)]}
