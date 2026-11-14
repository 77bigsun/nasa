"""Own candidate and target measurement files; definitions belong to catalog."""
import json
import os
from pathlib import Path
import yaml
from services.shared.contracts import Candidate, Measurements

class MeasurementRepository:
    def __init__(self):
        root=Path(__file__).resolve().parents[3]
        path=Path(os.getenv('DATA_DIR',root/'data'))/'seed'
        self.candidates=[Candidate.model_validate(v).model_dump() for v in json.loads((path/'earth_candidates.demo.json').read_text(encoding='utf-8'))]
        self.targets={k:Measurements.model_validate(v).model_dump() for k,v in yaml.safe_load((path/'target_values.demo.yaml').read_text(encoding='utf-8')).items()}
        ids=[candidate['id'] for candidate in self.candidates]
        if len(ids)!=len(set(ids)):raise ValueError('Duplicate candidate ID in measurement data')

