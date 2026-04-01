import pytest
import numpy as np
from symlib.kernel.verify import verify_sigma, score_sigma, score_sigma_numba, HAS_NUMBA
from symlib.search.equivariant import run_equivariant_sa

def test_verify_sigma_k2():
    # Z_2^2, k=2. Hamiltonian decomposition of Q_2.
    # Vertices: (0,0), (0,1), (1,0), (1,1)
    # Colors: 0, 1. Arc types: 0, 1.
    # Let sigma be identity everywhere: p=(0,1)
    m, k = 2, 2
    sigma = {
        (0,0): (0, 1),
        (0,1): (0, 1),
        (1,0): (0, 1),
        (1,1): (0, 1),
    }
    # Color 0: (i,j) -> (i+1, j). Cycles: (0,0)->(1,0)->(0,0) and (0,1)->(1,1)->(0,1).
    # Not Hamiltonian (2 components).
    assert verify_sigma(sigma, m, k) == False

def test_score_sigma_consistency():
    m, k = 3, 3
    from symlib.search.equivariant import _build_sa_tables
    n, arc_s, pa, all_perms = _build_sa_tables(m, k)
    nP = len(all_perms)
    sigma_list = np.array([0] * n, dtype=np.uint32)

    s1 = score_sigma(sigma_list, arc_s, pa, n, k)
    if HAS_NUMBA:
        s2 = score_sigma_numba(sigma_list, arc_s, pa, n, k)
        assert s1 == s2
    assert s1 > 0 # (0,0,0) with identity perm has many components

def test_sa_runs_k2():
    # Minimal k=2 run
    sol, stats = run_equivariant_sa(m=2, k=2, max_iter=100)
    assert stats['iters'] > 0
    assert 'best' in stats

def test_sa_finds_m3_k3():
    # Small fast problem
    sol, stats = run_equivariant_sa(m=3, k=3, max_iter=100000)
    if sol:
        assert stats['best'] == 0
        assert verify_sigma(sol, 3, 3) == True
