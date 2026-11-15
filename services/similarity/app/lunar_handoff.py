"""Serve reviewed, precomputed task rankings from the supplied source handoff."""
from services.shared.lunar_handoff import HandoffCatalog, HandoffRankings, RankingGroups


def task_comparison(task_id, site_id, catalog: HandoffCatalog, data: HandoffRankings):
    if task_id not in catalog.tasks:
        raise ValueError('Unknown retained lunar task')
    if catalog.version != data.version:
        raise RuntimeError('Lunar catalog and rankings have different versions')
    site = next((s for s in catalog.moon_sites if site_id in (s.id, s.legacy_id)), None)
    if site is None:
        raise ValueError('Unknown lunar reference site')
    task = catalog.tasks[task_id]
    groups = data.rankings[task_id]
    if task_id == 'M4':
        groups = groups[site.id]
    if not isinstance(groups, RankingGroups):
        raise RuntimeError('Invalid lunar ranking structure')
    status = ('primary' if task_id in site.suitable_tasks.primary else
              'secondary' if task_id in site.suitable_tasks.secondary else 'unassessed')
    return {'version': catalog.version, 'task_id': task_id, 'task': task.model_dump(),
        'selected_site': site.model_dump(by_alias=True), 'site_status': status,
        'most_similar': groups.new_candidates[:3], 'least_similar': groups.least_similar,
        'known_analogs_validation': groups.known_analogs_validation,
        'other_new_candidates': groups.new_candidates[3:],
        'ranking_scope': ('M4: 135 non-ice entries from the supplied 151-entry fine-terrain pool; the new-candidate subset has 130 entries.' if task_id == 'M4' else
            'M3/M6: 14706 non-ice MODIS-LST cells; 4881 ice cells and 12 no-LST coastal cells are excluded. Known analog regions remain separate.' if task_id in ['M3','M6'] and data.provenance.get('temperature_source') == 'MODIS_LST_2023' else
            'M2/M3/M6: supplied rankings from 19599 land cells, with 4881 ice cells excluded; new candidates also exclude known analog regions and use the supplied regional spacing rule.'),
        'anchor_note': ('M4 uses the selected lunar site\'s own 30 m slope distribution and 16 km relief. Its final rankings are separate from the relief-only global screen.' if task.depends_on_moon_site else
            'This task uses shared Earth-achievable anchors, so changing lunar sites does not change the Earth ranking. Lunar task suitability is assessed separately above.'),
        'provenance': data.provenance}
