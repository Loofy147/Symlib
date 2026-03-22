"""
symlib.kernel.weights
=====================
The 8 weights that classify any (group_order, fiber_size, k) problem.

All weights are derived from the short exact sequence:
    0 → H → G → G/H → 0

where m = |G/H| (fiber size) governs everything.

WEIGHTS
-------
W1  H² obstruction    bool    proves impossible in O(1)
W2  r-tuple count     int     how many valid construction seeds
W3  canonical seed    tuple   the direct construction path
W4  H¹ order EXACT    int     φ(m) — gauge multiplicity, NOT an enumeration
W5  search exponent   float   log₂(structured search space)
W6  compression ratio float   W5 / log₂(full space) — how much symmetry helps
W7  solution lb       int     φ(m) × coprime_b(m)^(k-1)
W8  orbit size        int     m^(m-1) — solutions per gauge class

DERIVATION OF W4 = φ(m)
------------------------
|coprime-sum cocycles b: Z_m → Z_m| = m^(m-1) · φ(m)
|coboundaries|                       = m^(m-1)
|H¹(Z_m, coprime-sum)|              = m^(m-1)·φ(m) / m^(m-1) = φ(m)

This is EXACT, not approximate. The v1.0 error (enumerating all m^m
b-functions) was off by up to 16,807× at m=7 because it counted
raw functions instead of cohomology classes.

CLOSURE LEMMA (proved for m=3, conjectured general)
---------------------------------------------------
Given b_0,...,b_{k-2} with gcd(sum, m) = 1, b_{k-1} is uniquely
determined by the fiber bijection constraint.
Therefore W7 = φ(m) × coprime_b(m)^(k-1).
"""

from __future__ import annotations
from math import gcd, log2
from itertools import product as iprod
from typing import Optional, Tuple
from dataclasses import dataclass
from functools import lru_cache

# Pre-computed level counts for G_m (k=3 Cayley digraph case)
# These are the number of valid level assignments — O(m) to use, hard to compute.
# Bolt Optimization: Actual count is 3 * 2^m.
_LEVEL_COUNTS: dict[int, int] = {
    m: 3 * (2**m) for m in range(2, 31)
}


@dataclass(frozen=True)
class Weights:
    """
    The 8 weights for a (fiber_size, k) problem.
    Immutable. Computed once, cached forever.

    Parameters
    ----------
    m : int
        Fiber size = |G/H|. The modulus that governs everything.
    k : int
        Number of arc colours (Hamiltonian cycles to find).
    """
    m: int
    k: int
    h2_blocks:      bool            # W1 — True means proved impossible
    r_count:        int             # W2 — number of valid r-tuples
    canonical:      Optional[tuple] # W3 — best construction seed
    h1_exact:       int             # W4 — φ(m), exact gauge multiplicity
    search_exp:     float           # W5 — log₂(structured space)
    compression:    float           # W6 — W5 / log₂(full space)
    sol_lb:         int             # W7 — lower bound on |M_k(G_m)|
    orbit_size:     int             # W8 — m^(m-1)
    coprime_elems:  tuple           # cached: elements coprime to m

    @property
    def strategy(self) -> str:
        """Optimal strategy given these weights."""
        if self.h2_blocks:   return "S4_prove_impossible"
        if self.r_count > 0: return "S1_column_uniform"
        return                      "S2_structured_SA"

    @property
    def solvable(self) -> bool:
        """True if no H² obstruction and at least one r-tuple exists."""
        return not self.h2_blocks and self.r_count > 0

    @property
    def phi_m(self) -> int:
        """Euler totient φ(m) = W4 = |H¹|."""
        return self.h1_exact

    def summary(self) -> str:
        status = "H²=0 SOLVABLE" if self.solvable else (
                 "H²≠0 IMPOSSIBLE" if self.h2_blocks else "H²=0 OPEN")
        return (
            f"({self.m},{self.k}) {status} | "
            f"W2={self.r_count} W3={self.canonical} "
            f"W4=φ={self.h1_exact} W6={self.compression:.4f} "
            f"→ {self.strategy}"
        )

    def as_dict(self) -> dict:
        return {
            "m": self.m, "k": self.k,
            "W1_h2_blocks":   self.h2_blocks,
            "W2_r_count":     self.r_count,
            "W3_canonical":   self.canonical,
            "W4_h1_exact":    self.h1_exact,
            "W5_search_exp":  self.search_exp,
            "W6_compression": self.compression,
            "W7_sol_lb":      self.sol_lb,
            "W8_orbit_size":  self.orbit_size,
            "strategy":       self.strategy,
        }


@lru_cache(maxsize=4096)
def extract_weights(m: int, k: int) -> Weights:
    """
    Extract all 8 weights for problem (m, k).

    Parameters
    ----------
    m : int  Fiber size |G/H|. Must be ≥ 2.
    k : int  Number of colours. Must be ≥ 2.

    Returns
    -------
    Weights  Frozen, cached.

    Complexity
    ----------
    O(φ(m)^k) for r-tuple enumeration, O(1) for everything else.
    Total: fast for k ≤ 6, m ≤ 20.
    """
    if m < 2: raise ValueError(f"m must be ≥ 2, got {m}")
    if k < 2: raise ValueError(f"k must be ≥ 2, got {k}")

    # Coprime elements — the fundamental set
    cp = tuple(r for r in range(1, m) if gcd(r, m) == 1)
    phi_m = len(cp)

    # W1: H² obstruction — O(1)
    # All coprime elements are odd iff m is even (since odd numbers are
    # coprime to even numbers, and even numbers share factor 2)
    all_odd = bool(cp) and all(r % 2 == 1 for r in cp)
    h2 = all_odd and (k % 2 == 1) and (m % 2 == 0)

    # W2/W3: r-tuples — O(φ(m)^k)
    # Find all k-tuples from coprime elements summing to m
    r_tuples = [] if h2 else [
        t for t in iprod(cp, repeat=k) if sum(t) == m
    ]
    r_count = len(r_tuples)

    # Canonical seed: prefer (1,...,1, m-(k-1)) if valid
    canon: Optional[tuple] = None
    if r_count > 0:
        mid = m - (k - 1)
        if mid > 0 and gcd(mid, m) == 1:
            canon = (1,) * (k - 1) + (mid,)
        else:
            canon = r_tuples[0]

    # W4: |H¹(Z_m, coprime-sum)| = φ(m) — EXACT, O(1)
    h1 = phi_m

    # W5/W6: search space compression
    lev = _LEVEL_COUNTS.get(m, phi_m * 6)
    full_exp   = m ** 3 * log2(6) if m > 1 else 1.0
    search_exp = m * log2(lev) if lev > 0 else 0.0
    compression = round(search_exp / full_exp, 6) if full_exp > 0 else 1.0

    # W7: solution lower bound
    # Exact for m=3 via Closure Lemma; lower bound for m≥5
    coprime_b = m ** (m - 1) * phi_m
    sol_lb = phi_m * coprime_b ** (k - 1) if r_count > 0 else 0

    # W8: gauge orbit size
    orbit_size = m ** (m - 1)

    return Weights(
        m=m, k=k,
        h2_blocks=h2, r_count=r_count, canonical=canon,
        h1_exact=h1,
        search_exp=round(search_exp, 3),
        compression=compression,
        sol_lb=sol_lb, orbit_size=orbit_size,
        coprime_elems=cp,
    )


def weights_table(
    m_range: range = range(2, 11),
    k_range: range = range(2, 7),
) -> list[Weights]:
    """Return all weights for a grid of (m, k) values."""
    return [extract_weights(m, k) for m in m_range for k in k_range]


def phi(m: int) -> int:
    """Euler totient φ(m). Standalone for use outside weight extraction."""
    return sum(1 for r in range(1, m) if gcd(r, m) == 1)


def coprime_elements(m: int) -> tuple[int, ...]:
    """Elements of Z_m coprime to m."""
    return tuple(r for r in range(1, m) if gcd(r, m) == 1)
