"""Select source-native Mars rankings; never mix them with legacy pilot scores."""
from services.shared.mars_handoff import MarsCatalog, MarsResults


def comparison(site_id, task_ids, catalog: MarsCatalog, data: MarsResults):
    if data.meta['version'] != catalog.meta['version'] or data.meta['generated'] != catalog.meta['generated']:
        raise RuntimeError('Mars catalog and measurement versions differ')
    site = next((s for s in catalog.mars_sites if s.id == site_id), None)
    if site is None:
        raise ValueError('Unknown Mars study target')
    if not task_ids or len(set(task_ids)) != len(task_ids) or any(t not in catalog.tasks for t in task_ids):
        raise ValueError('Select distinct Mars tests R1-R6')
    groups = []
    for task_id in task_ids:
        group = data.task_rankings.get(task_id, {}).get(site_id)
        task = catalog.tasks[task_id].model_dump()
        if group is not None:
            active_features = {f.feature for f in group.new_candidates[0].features}
            task['features'] = [f for f in task['features'] if f['id'] in active_features]
        groups.append({'task_id': task_id, 'status': site.test_status[task_id], 'task': task,
                       'ranking': group.model_dump() if group else None})
    return {'version': data.meta['version'], 'generated': data.meta['generated'], 'site': site.model_dump(),
            'groups': groups, 'profile': data.profile_rankings[site_id], 'validation': data.validation['summary']}
