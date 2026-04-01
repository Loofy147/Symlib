"""
symlib.kernel.weights
=====================
Algebraic weights for symmetric combinatorial systems.
"""

from __future__ import annotations
from math import gcd, log2
from itertools import product as iprod
from typing import Optional, Tuple
from dataclasses import dataclass
from functools import lru_cache

def fast_phi(n: int) -> int:
    """Euler totient function via prime factorization."""
    if n < 1: return 0
    if n == 1: return 0
    res = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            res -= res // p
        p += 1
    if temp > 1:
        res -= res // temp
    return res

@dataclass(frozen=True)
class Weights:
    m: int
    k: int
    h2_blocks:      bool
    r_count:        int
    canonical:      Optional[tuple]
    h1_exact:       int
    search_exp:     float
    compression:    float
    sol_lb:         int
    orbit_size:     int
    coprime_elems:  tuple

    @property
    def strategy(self) -> str:
        if self.h2_blocks:   return "S4_prove_impossible"
        if self.r_count != 0: return "S1_column_uniform"
        return                      "S2_structured_SA"

    @property
    def solvable(self) -> bool:
        return not self.h2_blocks and self.r_count != 0

    @property
    def phi_m(self) -> int:
        return self.h1_exact

    def summary(self) -> str:
        status = "H²=0 SOLVABLE" if self.solvable else (
                 "H²≠0 IMPOSSIBLE" if self.h2_blocks else "H²=0 OPEN")
        return (
            f"({self.m},{self.k}) {status} | "
            f"W2={self.r_count} W3={self.canonical} "
            f"W4=φ={self.h1_exact} W6={self.compression:.4f}"
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
    if m < 2: raise ValueError(f"m must be ≥ 2, got {m}")
    if k < 1: raise ValueError(f"k must be ≥ 1, got {k}")

    phi_m = fast_phi(m)
    h2 = (m % 2 == 0) and (k % 2 == 1)

    r_count = 0
    canon = None

    if not h2:
        mid = m - (k - 1)
        if mid > 0 and gcd(mid, m) == 1:
            canon = (1,) * (k - 1) + (mid,)
            r_count = -1

    # VERY strict limit on enumeration
    if not h2 and k <= 6 and phi_m < 100:
        cp = tuple(r for r in range(1, m) if gcd(r, m) == 1)
        if len(cp) ** k < 100_000:
            r_tuples = [t for t in iprod(cp, repeat=k) if sum(t) == m]
            r_count = len(r_tuples)
            if r_tuples:
                canon = r_tuples[0]

    h1 = phi_m
    try:
        # Avoid huge numbers in search_exp for massive m
        if m < 10**6:
            search_exp = m * log2(max(2, h1 * 6))
            full_exp   = m ** 3 * log2(6) if m < 1000 else 1e18
            compression = round(search_exp / full_exp, 6)
        else:
            search_exp = 0.0
            compression = 0.0
    except:
        search_exp = 0.0
        compression = 0.0

    if m < 15:
        coprime_b = (m ** (m - 1) * h1)
        sol_lb = h1 * coprime_b ** (k - 1) if r_count != 0 else 0
        orbit_size = m ** (m - 1)
    else:
        sol_lb = -1
        orbit_size = -1

    cp_sample = (1, m-1) if m > 100 else tuple(r for r in range(1, m) if gcd(r, m) == 1)

    return Weights(
        m=m, k=k,
        h2_blocks=h2, r_count=r_count, canonical=canon,
        h1_exact=h1,
        search_exp=round(float(search_exp), 3),
        compression=float(compression),
        sol_lb=int(sol_lb), orbit_size=int(orbit_size),
        coprime_elems=cp_sample,
    )

def phi(m: int) -> int:
    return fast_phi(m)

def coprime_elements(m: int) -> tuple[int, ...]:
    if m > 100: return (1, m-1)
    return tuple(r for r in range(1, m) if gcd(r, m) == 1)
