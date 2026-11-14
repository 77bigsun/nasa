"""Explain data gaps separately from measured failures and feature coverage."""
from .core.optimize import set_cover, marginal_curve


def inspect_coverage(score):
    candidates = score['candidates']
    task_ids = list(score['weights'])
    tau = score['tau']
    definitions = [
        (tid, detail['feature'])
        for tid in task_ids
        for detail in candidates[0]['tasks'][tid]['features']
        if not detail['feature']['out_of_earth_range']
    ] if candidates else []
    details = [
        {detail['feature']['id']: detail
         for tid in task_ids for detail in candidate['tasks'][tid]['features']}
        for candidate in candidates
    ]
    matrix = [[row[f['id']]['score'] if row[f['id']]['score'] is not None else -1
               for _, f in definitions] for row in details]
    # Missing feature weights stay in the denominator; this is not full-task coverage.
    totals = {tid: sum(f['weight'] for t, f in definitions if t == tid) for tid in task_ids}
    weights = [score['weights'][tid] * f['weight'] / totals[tid] for tid, f in definitions]
    solution = set_cover(matrix, weights, tau) if candidates and definitions else {
        'selected': [], 'minimum_sites': 0, 'covered': []}
    selected = [candidates[j]['id'] for j in solution['selected']]
    feature_rows = []
    for i, (tid, feature) in enumerate(definitions):
        fid = feature['id']
        measured = [(row[fid]['score'], candidate['id'])
                    for row, candidate in zip(details, candidates) if row[fid]['score'] is not None]
        best = sorted(measured, key=lambda v: (-v[0], v[1]))[0] if measured else None
        state = ('met' if best and best[0] >= tau else 'below_threshold' if best else
                 'incomparable' if any(row[fid]['classification'] == 'incomparable' for row in details)
                 else 'missing_data')
        feature_rows.append({
            'task_id': tid, 'feature_id': fid, 'name': feature['name'], 'status': state,
            'best_score': best[0] if best else None, 'best_candidate_id': best[1] if best else None,
            'covered_by': [{'candidate_id': candidates[j]['id'], 'score': matrix[j][i]}
                           for j in solution['selected'] if matrix[j][i] >= tau],
        })
    diagnostics = []
    for tid in task_ids:
        rows = [row for row in feature_rows if row['task_id'] == tid]
        complete = [c['tasks'][tid]['score'] for c in candidates if c['tasks'][tid]['score'] is not None]
        partial = [c['tasks'][tid].get('partial_score') for c in candidates
                   if c['tasks'][tid].get('partial_score') is not None]
        met = [row['feature_id'] for row in rows if row['status'] == 'met']
        comparable = sum(row['best_score'] is not None for row in rows)
        best_complete = max(complete) if complete else None
        status = (
            'covered' if best_complete is not None and best_complete >= tau else
            'below_threshold' if candidates and len(complete) == len(candidates) else
            'partial' if met else 'insufficient_data' if comparable else 'no_comparable_data'
        )
        diagnostics.append({
            'task_id': tid, 'status': status, 'required_features': len(rows),
            'comparable_features': comparable, 'met_features': len(met),
            'best_complete_score': best_complete, 'best_partial_score': max(partial) if partial else None,
            'missing_features': [row['feature_id'] for row in rows if row['status'] == 'missing_data'],
            'incomparable_features': [row['feature_id'] for row in rows if row['status'] == 'incomparable'],
            'met_feature_ids': met,
        })
    network = {
        'minimum_sites': solution['minimum_sites'], 'selected': selected,
        'total_features': len(definitions),
        'comparable_features': sum(row['best_score'] is not None for row in feature_rows),
        'covered_features': len(solution['covered']), 'coverage': feature_rows,
        'marginal_curve': [
            dict(point, selected=[candidates[j]['id'] for j in point['selected']])
            for point in marginal_curve(matrix, weights, tau)
        ] if candidates and definitions else [],
    }
    return diagnostics, network
