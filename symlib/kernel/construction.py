"""
symlib.kernel.construction
==========================
High-performance algebraic construction of sigma maps for G_m (k=3).
"""

from __future__ import annotations
from math import gcd
from itertools import permutations, product as iprod
from typing import Optional, Dict, Tuple, List, Any
from functools import lru_cache
from dataclasses import dataclass

from symlib.kernel.weights import extract_weights, Weights, coprime_elements


# Type aliases
Sigma     = Dict[Tuple[int,...], Tuple[int,...]]
_ALL_P3   = [list(p) for p in permutations(range(3))]
_FIBER_SHIFTS = ((1,0,0),(0,1,0),(0,0,1))


@dataclass(frozen=True)
class LevelMeta:
    """Precomputed properties of a valid level assignment."""
    lv: Dict[int, tuple]
    fixed_color: int  # color c that has dj=1 for all columns j
    at0_counts: Tuple[int, int, int] # Count of arc type 0 per color


class ConstructionEngine:
    """
    Algebraic construction of sigma maps for G_m (k=3).
    """

    # Precomputed verified solutions
    _TABLE_M3: List[Dict] = [
        {0: (1, 0, 2), 1: (1, 0, 2), 2: (1, 0, 2)},
        {0: (0, 1, 2), 1: (2, 1, 0), 2: (2, 1, 0)},
        {0: (0, 2, 1), 1: (1, 2, 0), 2: (1, 2, 0)},
    ]
    _TABLE_M5: List[Dict] = [
        {0:(1,0,2),1:(1,0,2),2:(1,0,2),3:(1,0,2),4:(1,0,2)},
        {0:(0,1,2),1:(2,1,0),2:(2,1,0),3:(2,1,0),4:(2,1,0)},
        {0:(1,2,0),1:(0,2,1),2:(0,2,1),3:(0,2,1),4:(0,2,1)},
        {0:(1,2,0),1:(0,2,1),2:(0,2,1),3:(0,2,1),4:(0,2,1)},
        {0:(1,2,0),1:(0,2,1),2:(0,2,1),3:(0,2,1),4:(0,2,1)},
    ]
    _TABLE_M7: List[Dict] = [
        {0:(1,0,2),1:(1,0,2),2:(1,0,2),3:(1,0,2),4:(1,0,2),5:(1,0,2),6:(1,0,2)},
        {0:(0,1,2),1:(2,1,0),2:(2,1,0),3:(2,1,0),4:(2,1,0),5:(2,1,0),6:(2,1,0)},
        {0:(1,2,0),1:(0,2,1),2:(0,2,1),3:(0,2,1),4:(0,2,1),5:(0,2,1),6:(0,2,1)},
        {0:(1,2,0),1:(0,2,1),2:(0,2,1),3:(0,2,1),4:(0,2,1),5:(0,2,1),6:(0,2,1)},
        {0:(1,2,0),1:(0,2,1),2:(0,2,1),3:(0,2,1),4:(0,2,1),5:(0,2,1),6:(0,2,1)},
        {0:(1,2,0),1:(0,2,1),2:(0,2,1),3:(0,2,1),4:(0,2,1),5:(0,2,1),6:(0,2,1)},
        {0:(1,2,0),1:(0,2,1),2:(0,2,1),3:(0,2,1),4:(0,2,1),5:(0,2,1),6:(0,2,1)},
    ]

    def __init__(self, m: int, k: int):
        self.m = m
        self.k = k
        self._weights = extract_weights(m, k)
        self._precomputed = self._load_precomputed()

    def _load_precomputed(self) -> dict:
        pre = {}
        if self.m == 3 and self.k == 3:
            pre[(3,3)] = self._table_to_sigma(self._TABLE_M3, 3)
        if self.m == 5 and self.k == 3:
            pre[(5,3)] = self._table_to_sigma(self._TABLE_M5, 5)
        if self.m == 7 and self.k == 3:
            pre[(7,3)] = self._table_to_sigma(self._TABLE_M7, 7)
        if self.m == 4 and self.k == 3:
            pre[(4,3)] = self._m4_solution()
        return pre

    def construction_level(self) -> str:
        if (self.m, self.k) in self._precomputed: return "precomputed"
        if self.m % 2 == 1 and self.k == 3:       return "direct_formula"
        if self.m == 3:                          return "closure_lemma"
        if self.k == 2:                          return "direct_k2"
        w = self._weights
        if w.h2_blocks:                           return "impossible"
        if w.r_count > 0 and self.k == 3:         return "level_enum"
        return "open"

    def construct(self, max_level_iters: int = 500_000) -> Optional[Sigma]:
        pre = self._precomputed.get((self.m, self.k))
        if pre is not None: return pre

        if self.m % 2 == 1 and self.k == 3:
            return self._construct_via_formula()

        w = self._weights
        if w.h2_blocks: return None

        if self.k == 2:
            return self._construct_k2()

        if w.r_count > 0 and self.k == 3:
            return self._construct_via_levels(max_level_iters)

        return None

    def _construct_via_formula(self) -> Optional[Sigma]:
        """Deterministic O(m^2) twisted construction for all odd m."""
        m = self.m
        levels = []
        levels.append([(1,0,2)] * m)
        l1 = [(2,1,0)] * m
        l1[0] = (0,1,2)
        levels.append(l1)
        for _ in range(2, m):
            ll = [(1,2,0)] * m
            ll[0] = (0,2,1)
            levels.append(ll)
        return self._table_to_sigma(levels, m)

    def _construct_k2(self) -> Optional[Sigma]:
        """Deterministic algebraic construction for k=2 (m x m grid)."""
        m = self.m
        sigma = {}
        for i in range(m):
            for j in range(m):
                if (i + j) % m == 0: sigma[(i, j)] = (1, 0)
                else:                sigma[(i, j)] = (0, 1)
        return sigma

    def _construct_via_levels(self, max_iters: int) -> Optional[Sigma]:
        """Level 4: structured level search with O(1) condition hit-check."""
        import random
        m = self.m
        metas = _valid_levels_cached_meta(m)
        w = self._weights

        from itertools import product as iprod
        r_tuples = [t for t in iprod(range(1, m), repeat=3) if sum(t) == m and all(gcd(x, m) == 1 for x in t)]
        if not r_tuples: r_tuples = [(1, 1, m-2)]

        metas_by_color = [[met for met in metas if met.fixed_color == c] for c in range(3)]
        rng = random.Random(42)

        for _ in range(max_iters // 100 + 2):
            target_r = rng.choice(r_tuples)
            roles = [c for c, count in enumerate(target_r) for _ in range(count)]
            random.shuffle(roles)

            prefix = [rng.choice(metas_by_color[fc]) for fc in roles[:-1]]
            S = [sum(mt.at0_counts[c] for mt in prefix) for c in range(3)]

            last_fc = roles[-1]
            for last_meta in metas_by_color[last_fc]:
                valid = True
                for c in range(3):
                    if gcd(S[c] + last_meta.at0_counts[c], m) != 1:
                        valid = False; break
                if valid:
                    full_table = prefix + [last_meta]
                    return self._table_to_sigma([mt.lv for mt in full_table], m)
        return None

    @staticmethod
    def _table_to_sigma(table: List[Dict], m: int) -> Sigma:
        """Convert level table to full sigma map."""
        sigma = {}
        for i in range(m):
            for j in range(m):
                for k in range(m):
                    sigma[(i,j,k)] = table[(i+j+k) % m][j]
        return sigma

    @staticmethod
    def _m4_solution() -> Sigma:
        """Hardcoded verified solution for m=4, k=3."""
        return {
            (0,0,0):(2,1,0),(0,0,1):(2,1,0),(0,0,2):(0,2,1),(0,0,3):(1,2,0),
            (0,1,0):(1,0,2),(0,1,1):(0,2,1),(0,1,2):(2,0,1),(0,1,3):(0,1,2),
            (0,2,0):(2,0,1),(0,2,1):(0,1,2),(0,2,2):(1,2,0),(0,2,3):(1,0,2),
            (0,3,0):(1,2,0),(0,3,1):(1,2,0),(0,3,2):(0,1,2),(0,3,3):(2,0,1),
            (1,0,0):(2,0,1),(1,0,1):(0,2,1),(1,0,2):(2,1,0),(1,0,3):(1,2,0),
            (1,1,0):(2,0,1),(1,1,1):(1,2,0),(1,1,2):(0,2,1),(1,1,3):(1,0,2),
            (1,2,0):(0,2,1),(1,2,1):(1,2,0),(1,2,2):(0,1,2),(1,2,3):(2,0,1),
            (1,3,0):(2,1,0),(1,3,1):(1,0,2),(1,3,2):(0,2,1),(1,3,3):(1,2,0),
            (2,0,0):(2,0,1),(2,0,1):(0,2,1),(2,0,2):(1,2,0),(2,0,3):(0,2,1),
            (2,1,0):(2,1,0),(2,1,1):(2,0,1),(2,1,2):(1,2,0),(2,1,3):(2,0,1),
            (2,2,0):(0,1,2),(2,2,1):(2,0,1),(2,2,2):(0,2,1),(2,2,3):(1,0,2),
            (2,3,0):(1,0,2),(2,3,1):(0,2,1),(2,3,2):(1,0,2),(2,3,3):(1,2,0),
            (3,0,0):(1,0,2),(3,0,1):(1,0,2),(3,0,2):(2,0,1),(3,0,3):(2,0,1),
            (3,1,0):(0,2,1),(3,1,1):(0,1,2),(3,1,2):(0,2,1),(3,1,3):(0,2,1),
            (3,2,0):(1,2,0),(3,2,1):(0,2,1),(3,2,2):(1,2,0),(3,2,3):(2,0,1),
            (3,3,0):(2,0,1),(3,3,1):(2,1,0),(3,3,2):(1,0,2),(3,3,3):(1,2,0),
        }

    def closure_lemma_b(self, b_funcs: List[Dict[int,int]]) -> Optional[Dict[int,int]]:
        """Apply the Closure Lemma: given b_0,...,b_{k-2}, derive b_{k-1}."""
        m = self.m
        if m != 3: return None
        b_last = {}
        for j in range(m):
            total = sum(b[j] for b in b_funcs) % m
            b_last[j] = (-total) % m
        s = sum(b_last.values()) % m
        if gcd(s, m) != 1: return None
        return b_last


# ── Optimized Level machinery ────────────────────────────────────────────────

@lru_cache(maxsize=32)
def _valid_levels_cached(m: int) -> List[Dict]:
    """O(m * 2^m) generation of valid levels."""
    metas = _valid_levels_cached_meta(m)
    return [meta.lv for meta in metas]


@lru_cache(maxsize=32)
def _valid_levels_cached_meta(m: int) -> List[LevelMeta]:
    """Generate valid levels and their metadata directly in O(m * 2^m)."""
    results = []
    for fixed_c in range(3):
        other_colors = [c for c in range(3) if c != fixed_c]
        c0, c2 = other_colors
        for bits in range(1 << m):
            lv = {}
            at0_counts = [0, 0, 0]
            for j in range(m):
                p = [None]*3
                p[1] = fixed_c
                if (bits >> j) & 1: p[0]=c0; p[2]=c2; at0_counts[c0]+=1
                else:              p[0]=c2; p[2]=c0; at0_counts[c2]+=1
                lv[j] = tuple(p)
            results.append(LevelMeta(lv=lv, fixed_color=fixed_c, at0_counts=tuple(at0_counts)))
    return results
