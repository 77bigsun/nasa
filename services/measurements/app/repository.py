"""Own candidate and target measurement files; definitions belong to catalog."""
import json
import os
from pathlib import Path
import yaml
from services.shared.contracts import Candidate, Measurements, ObservedPilot

class MeasurementRepository:
    def __init__(self):
        root=Path(__file__).resolve().parents[3]
        self.data_root=Path(os.getenv('DATA_DIR',root/'data'))
        path=self.data_root/'seed'
        self.candidates=[Candidate.model_validate(v).model_dump() for v in json.loads((path/'earth_candidates.demo.json').read_text(encoding='utf-8'))]
        self.targets={k:Measurements.model_validate(v).model_dump() for k,v in yaml.safe_load((path/'target_values.demo.yaml').read_text(encoding='utf-8')).items()}
        ids=[candidate['id'] for candidate in self.candidates]
        if len(ids)!=len(set(ids)):raise ValueError('Duplicate candidate ID in measurement data')


    def observed(self):
        path=self.data_root/'observed/pilot.json'
        if not path.exists():return None
        return ObservedPilot.model_validate_json(path.read_text(encoding='utf-8'))
