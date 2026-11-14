"""Own candidate and target measurement files; definitions belong to catalog."""
import json
import os
from pathlib import Path
import yaml
from services.shared.contracts import Candidate, Measurements, ObservedPilot

class MeasurementRepository:
    def __init__(self, data_root=None):
        from services.shared.contracts import MeasurementSnapshot
        root=Path(__file__).resolve().parents[3]
        self.data_root=Path(data_root or os.getenv('DATA_DIR',root/'data'))
        path=self.data_root/'observed/mission-measurements.json'
        raw=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'mode':'observed','candidates':[],'targets':{}}
        snapshot=MeasurementSnapshot.model_validate(raw)
        self.candidates=[v.model_dump() for v in snapshot.candidates]
        self.targets={k:v.model_dump() for k,v in snapshot.targets.items()}
        ids=[candidate['id'] for candidate in self.candidates]
        if len(ids)!=len(set(ids)):raise ValueError('Duplicate candidate ID in observed measurements')

    def coverage(self):
        path=self.data_root/'observed/task-pairings.json'
        features=json.loads(path.read_text(encoding='utf-8')) if path.exists() else []
        return {'mode':'observed','features':features,'targets':{
            key:{'usable':[fid for fid,e in value['evidence'].items() if e['status']=='usable'],
                 'context':[fid for fid,e in value['evidence'].items() if e['status']=='context_only']}
            for key,value in self.targets.items()}}

    def observed(self):
        path=self.data_root/'observed/pilot.json'
        if not path.exists():return None
        return ObservedPilot.model_validate_json(path.read_text(encoding='utf-8'))
