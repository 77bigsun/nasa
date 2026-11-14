"""Two-stage minimum set cover, then maximum quality (Toregas et al. 1971).

Exhaustive fixed-k options are used for repeated sensitivity solves on this
20-site prototype; they are exact and avoid hundreds of CBC process launches.
"""
from itertools import combinations
import numpy as np
import pulp

def solve_problem(problem):
    solver=pulp.COIN_CMD(msg=False,timeLimit=30,threads=1,randomSeed=42,gapRel=0,gapAbs=0)
    stats=problem.solve(solver)
    if stats.status_str!='Optimal':raise RuntimeError(f'CBC did not find an optimal solution: {stats.status_str}')

def set_cover(scores,weights,tau=.7,bonuses=None):
    a=np.asarray(scores,dtype=float) # candidates x tasks; missing scores use -1
    n,m=a.shape
    cover=a>=tau
    active=[i for i in range(m) if cover[:,i].any()]
    missing=[i for i in range(m) if i not in active]
    if not n or not active:return {'selected':[],'minimum_sites':0,'uncoverable':missing,'covered':[],'objective':0.}
    p=pulp.LpProblem('minimum_set_cover',pulp.LpMinimize)
    x=[p.add_variable(f'site_{j}',cat='Binary') for j in range(n)]
    for i in active:p+=pulp.lpSum(x[j] for j in range(n) if cover[j,i])>=1
    p+=pulp.lpSum(x)
    solve_problem(p)
    k=round(sum(v.value() for v in x))
    # Secondary objective uses best score per demand, not the sum of redundant
    # sites. Assignment variables select the best chosen qualifying site.
    q=pulp.LpProblem('best_minimum_cover',pulp.LpMaximize)
    x=[q.add_variable(f'site_{j}',cat='Binary') for j in range(n)]
    q+=pulp.lpSum(x)==k
    terms=[]
    for i in active:
        z=[]
        for j in range(n):
            if not cover[j,i]:continue
            v=q.add_variable(f'assign_{i}_{j}',cat='Binary')
            q+=v<=x[j];z.append(v);terms.append(weights[i]*a[j,i]*v)
        q+=pulp.lpSum(z)==1
    for rule in bonuses or []:
        indices=rule['indices']
        if not indices:continue
        for j in range(n):
            if all(cover[j,i] for i in indices):terms.append(rule['bonus']*x[j])
    q+=pulp.lpSum(terms)
    solve_problem(q)
    selected=[j for j,v in enumerate(x) if v.value()>.5]
    return {'selected':selected,'minimum_sites':k,'uncoverable':missing,'covered':active,'objective':float(pulp.value(q.objective) or 0)}

def fixed_k_options(scores,k,tau):
    a=np.asarray(scores,dtype=float)
    n,m=a.shape
    if k==0:return [()],np.zeros((1,m)),np.zeros((1,m))
    combos=list(combinations(range(n),min(k,n)))
    covers=np.array([np.any(a[list(c)]>=tau,axis=0) for c in combos],dtype=float)
    quality=np.array([np.maximum(a[list(c)],0).max(axis=0) for c in combos])
    return combos,covers,quality

def maximum_cover(scores,weights,k,tau=.7,options=None):
    combos,covers,quality=options or fixed_k_options(scores,k,tau)
    w=np.asarray(weights)
    objective=covers@w
    best=np.flatnonzero(np.isclose(objective,objective.max(),atol=1e-12,rtol=0))
    # Coverage is the primary objective; quality only breaks exact ties.
    index=int(best[np.argmax((quality@w)[best])])
    return {'selected':list(combos[index]),'weighted_coverage':float(objective[index])}

def marginal_curve(scores,weights,tau=.7):
    n,m=np.asarray(scores).shape
    return [{'k':k,**maximum_cover(scores,weights,k,tau)} for k in range(1,min(n,m)+1)]

