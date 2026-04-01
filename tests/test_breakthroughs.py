import pytest
from math import gcd
from symlib.kernel.weights import phi, extract_weights
from symlib.kernel.torsor import TorsorStructure
from symlib.theorems import ParityObstruction, CanonicalSeed

def test_nb_formula():
    """N_b(m) = m^(m-1) * phi(m)"""
    def count_nb(m):
        from itertools import product
        count = 0
        for b in product(range(m), repeat=m):
            if gcd(sum(b) % m, m) == 1:
                count += 1
        return count

    for m in range(2, 6):  # 6 is slow for brute force product
        expected = (m**(m-1)) * phi(m)
        assert count_nb(m) == expected

def test_m3_k3_count_648():
    """|M_3(G_3)| = 648"""
    ts = TorsorStructure(m=3, k=3)
    info = ts.analyse()
    assert info.solution_count == 648
    assert info.is_exact == True

def test_h2_parity_obstruction():
    """even m AND odd k is blocked"""
    # m=4, k=3 is blocked
    res = ParityObstruction.check(m=4, k=3)
    assert res.blocked == True

    # m=4, k=2 is NOT blocked
    res = ParityObstruction.check(m=4, k=2)
    assert res.blocked == False

    # m=3, k=3 is NOT blocked
    res = ParityObstruction.check(m=3, k=3)
    assert res.blocked == False

def test_canonical_seed_odd_m():
    """r = (1, m-2, 1) valid for all odd m"""
    for m in [3, 5, 7, 9, 11, 13]:
        seed = CanonicalSeed.for_odd_m(m)
        assert seed == (1, m-2, 1)
        assert sum(seed) == m
        assert all(gcd(r, m) == 1 for r in seed)

def test_spike_construction_odd_m():
    """Direct construction for odd m, k=3 succeeds"""
    from symlib.kernel.construction import ConstructionEngine
    from symlib.kernel.verify import verify_sigma

    for m in [3, 5, 7]:
        cons = ConstructionEngine(m=m, k=3)
        sigma = cons.construct()
        assert sigma is not None
        assert verify_sigma(sigma, m=m, k=3) == True
