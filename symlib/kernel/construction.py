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
        {0:(2,0,1),1:(1,0,2),2:(2,0,1)},
        {0:(0,2,1),1:(1,2,0),2:(0,2,1)},
        {0:(0,1,2),1:(0,1,2),2:(0,1,2)},
    ]
    _TABLE_M5: List[Dict] = [
        {0:(0,2,1),1:(1,2,0),2:(0,2,1),3:(0,2,1),4:(1,2,0)},
        {0:(2,1,0),1:(2,1,0),2:(0,1,2),3:(2,1,0),4:(2,1,0)},
        {0:(2,1,0),1:(0,1,2),2:(0,1,2),3:(2,1,0),4:(2,1,0)},
        {0:(2,1,0),1:(2,1,0),2:(0,1,2),3:(0,1,2),4:(2,1,0)},
        {0:(2,0,1),1:(1,0,2),2:(2,0,1),3:(1,0,2),4:(2,0,1)},
    ]

    def __init__(self, m: int, k: int):
        self.m = m
        self.k = k
        self._weights = extract_weights(m, k)
        self._precomputed = self._load_precomputed()

    def _load_precomputed(self) -> dict:
        pre = {}
        pre[(3,3)] = self._table_to_sigma(self._TABLE_M3, 3)
        pre[(5,3)] = self._table_to_sigma(self._TABLE_M5, 5)
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

        w = self._weights
        if w.h2_blocks: return None

        if self.k == 2 and w.r_count > 0:
            return self._construct_k2()

        if w.r_count > 0 and self.k == 3:
            return self._construct_via_levels(max_level_iters)

        return None

    def _construct_k2(self) -> Optional[Sigma]:
        from itertools import permutations as iperms
        import random
        m = self.m
        ALL_P2 = list(iperms(range(2)))
        n = m * m
        arc_s = [[0]*2 for _ in range(n)]
        for idx in range(n):
            i, j = divmod(idx, m)
            arc_s[idx][0] = ((i+1)%m)*m + j
            arc_s[idx][1] = i*m + (j+1)%m
        pa = [[None]*2 for _ in range(2)]
        for pi, p in enumerate(ALL_P2):
            for at, c in enumerate(p): pa[pi][c] = at
        def score_k2(sigma):
            f0 = [0]*n; f1 = [0]*n
            for v in range(n):
                pi = sigma[v]; p = pa[pi]
                f0[v] = arc_s[v][p[0]]
                f1[v] = arc_s[v][p[1]]
            def cc(f):
                vis = bytearray(n); c = 0
                for s in range(n):
                    if not vis[s]:
                        c += 1; cur = s
                        while not vis[cur]: vis[cur]=1; cur=f[cur]
                return c
            return cc(f0)-1 + cc(f1)-1
        rng = random.Random(42)
        for _ in range(200_000):
            sigma = [rng.randrange(2) for _ in range(n)]
            if score_k2(sigma) == 0:
                result = {}
                for idx in range(n):
                    i, j = divmod(idx, m)
                    result[(i,j)] = tuple(ALL_P2[sigma[idx]])
                return result
        return None

    def _construct_via_levels(self, max_iters: int) -> Optional[Sigma]:
        """Level 4: structured level search with O(1) condition hit-check."""
        import random
        m = self.m
        metas = _valid_levels_cached_meta(m)
        w = self._weights

        # Guide search with valid r-tuples
        from itertools import product as iprod
        r_tuples = [t for t in iprod(range(1, m), repeat=3) if sum(t) == m and all(gcd(x, m) == 1 for x in t)]
        if not r_tuples: r_tuples = [(1, 1, m-2)] # fallback

        metas_by_color = [[met for met in metas if met.fixed_color == c] for c in range(3)]
        rng = random.Random(42)

        # Inner loop optimization: last-level-sweep
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

def _level_valid(lv: Dict[int,list], m: int) -> bool:
    """O(m) check: a level is valid iff dj is uniform for each color."""
    for c in range(3):
        fixed = lv[0].index(c) == 1
        for j in range(1, m):
            if (lv[j].index(c) == 1) != fixed: return False
    return True


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


def _check_table_accurate_meta(table: List[LevelMeta], m: int) -> bool:
    """Legacy O(m²) verification using composed fiber map Q."""
    for c in range(3):
        j_map = [0]*m; di_map = [0]*m
        for j_start in range(m):
            cur_j = j_start; sum_di = 0
            for meta in table:
                at = meta.lv[cur_j].index(c)
                if at == 1: cur_j = (cur_j + 1) % m
                elif at == 0: sum_di += 1
            j_map[j_start] = cur_j; di_map[j_start] = sum_di % m

        vis = [False] * (m * m)
        ci, cj = 0, 0; count = 0
        while not vis[ci * m + cj]:
            vis[ci * m + cj] = True; count += 1
            ni = (ci + di_map[cj]) % m; nj = j_map[cj]
            ci, cj = ni, nj
        if count != m * m: return False
    return True

def _compose_Q(table: List[Dict], m: int) -> List[Dict]:
    """Legacy O(m²) Q-composition."""
    Qs: List[Dict] = [{}, {}, {}]
    for c in range(3):
        for j_start in range(m):
            cur_j = j_start; sum_di = 0
            for lv in table:
                at = lv[cur_j].index(c)
                sum_di += _FIBER_SHIFTS[at][0]
                cur_j = (cur_j + _FIBER_SHIFTS[at][1]) % m
            di_m = sum_di % m
            for i in range(m):
                Qs[c][(i, j_start)] = ((i + di_m) % m, cur_j)
    return Qs


def _is_single_cycle(Q: Dict, m: int) -> bool:
    """O(m²) single cycle check for a Z_m² permutation."""
    n = m*m; vis = [False]*(m*m); cur = (0, 0)
    count = 0
    while not vis[cur[0]*m + cur[1]]:
        vis[cur[0]*m + cur[1]] = True; count += 1
        cur = Q[cur]
    return count == n
