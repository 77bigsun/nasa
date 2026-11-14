"""Validated file repository; replace this boundary with PostGIS later."""
import json
import os
from pathlib import Path
from typing import Protocol
import yaml
from .models import Mission, Task, Site, EarthLimit, Constraint, DataSource, Facts

class Repository(Protocol):
    def missions(self) -> list[Mission]: ...
    def tasks(self, mission: str) -> list[Task]: ...
    def sites(self, mission: str) -> list[Site]: ...

class FileRepository:
    def __init__(self, data_dir: Path | None = None):
        root=Path(__file__).resolve().parents[3]
        self.directory=(data_dir or Path(os.getenv('DATA_DIR',root/'data')))/'seed'
        self.docs=Path(os.getenv('DOCS_DIR',root/'docs'))
        self._missions=[Mission.model_validate(x) for x in self.read('missions.yaml')]
        self._tasks={m.id:[Task.model_validate(x) for x in self.read(f'tasks_{m.id}.yaml')] for m in self._missions}
        self._sites=[Site.model_validate(x) for x in self.read('target_sites.yaml')]
        self.sources=[DataSource.model_validate(x) for x in self.read('data_sources.yaml')]
        self.facts=Facts.model_validate(self.read('earth_facts.yaml'))
        self.settings=self.read('method.yaml')
        self.tables=self.read('categorical_tables.yaml')
        self.limits={k:[EarthLimit.model_validate(x) for x in v] for k,v in self.read('earth_limits.yaml').items()}
        self.constraints={k:[Constraint.model_validate(x) for x in v] for k,v in self.read('constraints.yaml').items()}
        from services.shared.contracts import DatasetProduct, ResearchSection
        self.data_root=self.directory.parent
        self.products=[DatasetProduct.model_validate(x) for x in json.loads((self.data_root/'catalog/datasets.json').read_text(encoding='utf-8'))]
        self.research=[ResearchSection.model_validate(x) for x in json.loads((self.data_root/'catalog/research.json').read_text(encoding='utf-8'))]
        self.translations=json.loads((self.data_root/'locales/zh-TW.json').read_text(encoding='utf-8'))
        lunar_locale=self.data_root/'locales/lunar-method.zh-TW.json'
        if lunar_locale.exists():self.translations.update(json.loads(lunar_locale.read_text(encoding='utf-8')))
        for name in ['lunar-handoff-source.zh-TW.json','lunar-handoff.zh-TW.json']:
            path=self.data_root/'locales'/name
            if path.exists():self.translations.update(json.loads(path.read_text(encoding='utf-8')))
        self.validate_links()

    def read(self,name):
        raw=(self.directory/name).read_text(encoding='utf-8')
        return json.loads(raw) if name.endswith('.json') else yaml.safe_load(raw)

    def missions(self):return self._missions
    def mission(self,mission):return next((m for m in self._missions if m.id==mission),None)
    def tasks(self,mission):return self._tasks[mission]
    def sites(self,mission):return [s for s in self._sites if s.mission==mission]

    def validate_links(self):
        feature_ids=[]
        task_ids=[]
        source_ids={s.id for s in self.sources}
        for mission,tasks in self._tasks.items():
            assert len(set(t.order for t in tasks))==len(tasks),'Duplicate task order'
            for task in tasks:
                assert task.mission==mission,'Task mission mismatch'
                task_ids.append(task.id)
                for f in task.features:
                    feature_ids.append(f.id)
                    assert all(s.source_id in source_ids for s in f.planet_data+f.earth_data),'Unknown source'
                    if f.type=='categorical':assert f.id in self.tables,'Missing category table'
        assert len(feature_ids)==len(set(feature_ids)),'Duplicate feature ID'
        assert len(task_ids)==len(set(task_ids)),'Duplicate task ID'
        assert all(set(s.used_by)<=set(feature_ids) for s in self.sources),'Unknown source feature'
