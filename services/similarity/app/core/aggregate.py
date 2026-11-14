"""Task-level geometric aggregation and weighted mission totals."""
import numpy as np

def geometric_mean(scores, weights=None, epsilon=1e-6):
    if not scores:return None
    s=np.asarray(scores,dtype=float)
    w=np.ones(len(s)) if weights is None else np.asarray(weights,dtype=float)
    if not np.isfinite(s).all() or not np.isfinite(w).all() or np.any(w<0) or w.sum()<=0:raise ValueError('Invalid scores or weights')
    return float(np.exp(np.dot(w/w.sum(),np.log(np.maximum(s,epsilon)))))

def aggregate_features(features, epsilon=1e-6):
    scored=[f for f in features if f.get('score') is not None and not f.get('out_of_earth_range')]
    return geometric_mean([f['score'] for f in scored],[f.get('weight',1) for f in scored],epsilon)

def overall(task_scores, weights):
    # Missing task evidence cannot improve rank through renormalization.
    return sum(weights[k]*(task_scores.get(k) or 0.) for k in weights)

