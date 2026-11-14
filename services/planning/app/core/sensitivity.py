"""Seeded Dirichlet weight acceptability, inspired by SMAA (1998)."""
import numpy as np
from .optimize import fixed_k_options, maximum_cover

def analyze(scores,k,tau=.7,n_samples=500,alpha=1.,seed=42):
    a=np.asarray(scores,dtype=float)
    rng=np.random.default_rng(seed)
    draws=rng.dirichlet(np.full(a.shape[1],alpha),size=n_samples)
    counts=np.zeros(len(a))
    options=fixed_k_options(a,k,tau)
    for weights in draws:
        chosen=maximum_cover(a,weights,k,tau,options)['selected']
        counts[chosen]+=1
    return (counts/n_samples).tolist()
