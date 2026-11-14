"""Ordinal weights (Barron & Barrett 1996), recomputed on selected tasks."""
import numpy as np

def roc(n: int) -> list[float]:
    if n<1:raise ValueError('At least one task is required')
    return [sum(1/i for i in range(k,n+1))/n for k in range(1,n+1)]

def rank_sum(n: int) -> list[float]:
    if n<1:raise ValueError('At least one task is required')
    return [(n-k+1)/(n*(n+1)/2) for k in range(1,n+1)]

def task_weights(tasks, scheme='roc', custom=None):
    ordered=sorted(tasks,key=lambda t:t['order'])
    if not ordered:raise ValueError('Select at least one task')
    if scheme=='custom':
        if custom is None or set(custom)!=set(t['id'] for t in ordered):raise ValueError('Custom weights must match selected tasks')
        values=np.array([custom[t['id']] for t in ordered],dtype=float)
        if not np.isfinite(values).all() or np.any(values<0) or values.sum()<=0:raise ValueError('Custom weights must be finite, nonnegative, and have positive total')
        values=values/values.sum()
    elif scheme=='roc':values=roc(len(ordered))
    elif scheme=='rank_sum':values=rank_sum(len(ordered))
    else:raise ValueError('Unknown weight scheme')
    return dict(zip([t['id'] for t in ordered],map(float,values)))

