"""Regularized Mahalanobis cross-check (Mahalanobis 1936), not a replacement."""
import numpy as np
from scipy.stats import spearmanr

def cross_check(matrix,target,primary):
    x=np.asarray(matrix,dtype=float);target=np.asarray(target,dtype=float)
    if x.ndim!=2 or x.shape[1]<2 or len(x)<3:return {'status':'insufficient_profile_features','spearman':None,'distances':[]}
    scale=np.std(x,axis=0);scale[scale<1e-12]=1
    z=(x-x.mean(axis=0))/scale;t=(target-x.mean(axis=0))/scale
    cov=np.cov(z,rowvar=False)+np.eye(x.shape[1])*1e-3
    inv=np.linalg.pinv(cov)
    distances=np.sqrt(np.maximum(0,np.einsum('ij,jk,ik->i',z-t,inv,z-t)))
    correlation=None
    if np.ptp(distances)>1e-12 and np.ptp(primary)>1e-12:
        r=float(spearmanr(-distances,primary).statistic)
        correlation=r if np.isfinite(r) else None
    return {'status':'ok','spearman':correlation,'distances':distances.tolist()}

