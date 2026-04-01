"""
symlib.kernel.verify
====================
Verification of sigma maps — pure, deterministic, O(m³).

WHAT IT CHECKS
--------------
A sigma map σ: Z_m³ → S_k is valid iff for each colour c ∈ {0,1,...,k-1}:
  1. Every vertex has exactly one outgoing arc of colour c  (well-defined)
  2. Every vertex has exactly one incoming arc of colour c  (in-degree 1)
  3. The induced functional graph has exactly 1 component   (Hamiltonian)

Equivalently: the k functions f_c: v → arc_c(v) are each a single
m³-cycle (permutation with one cycle covering all vertices).

This check is the ground truth. A solution is valid iff verify returns True.
No approximation. No heuristic. Exact.
"""

from __future__ import annotations
from typing import Dict, Tuple, Optional, List
import numpy as np

try:
    from numba import njit, uint32, uint8
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False

Sigma = Dict[Tuple[int,...], Tuple[int,...]]

def get_shifts(k: int) -> Tuple[Tuple[int, ...], ...]:
    """Generate k standard basis shifts for Z_m^k (usually k=3)."""
    shifts = []
    for i in range(k):
        shift = [0] * k
        shift[i] = 1
        shifts.append(tuple(shift))
    return tuple(shifts)


def verify_sigma(sigma: Sigma, m: int, k: int = 3) -> bool:
    """
    Verify σ: Z_m^k → S_k yields k directed Hamiltonian cycles.

    Parameters
    ----------
    sigma : dict  {v: (p0,p1,...,pk-1)} where p is a permutation of {0,1,...,k-1}
    m     : int   Fiber size. Vertex set is Z_m^k.
    k     : int   Dimension and number of colors.

    Returns
    -------
    True iff sigma is a valid Hamiltonian decomposition of G_m,k.
    """
    n = m ** k
    shifts = get_shifts(k)
    funcs: List[Dict[Tuple[int, ...], Tuple[int, ...]]] = [{} for _ in range(k)]

    for v, p in sigma.items():
        for at in range(k):
            nb = tuple((v[d] + shifts[at][d]) % m for d in range(k))
            funcs[p[at]][v] = nb

    for fg in funcs:
        if len(fg) != n:
            return False
        vis: set = set()
        comps = 0
        for s in fg:
            if s not in vis:
                comps += 1
                cur = s
                while cur not in vis:
                    vis.add(cur)
                    cur = fg[cur]
        if comps != 1:
            return False

    return True


def verify_and_diagnose(sigma: Sigma, m: int, k: int = 3) -> dict:
    """
    Verify sigma and return detailed diagnostics on failure.
    """
    n = m ** k
    shifts = get_shifts(k)

    funcs: List[Dict[Tuple[int, ...], Tuple[int, ...]]] = [{} for _ in range(k)]
    for v, p in sigma.items():
        for at in range(k):
            nb = tuple((v[d] + shifts[at][d]) % m for d in range(k))
            funcs[p[at]][v] = nb

    results = {"valid": True, "n_vertices": n, "colours": []}

    for c in range(k):
        fg = funcs[c]

        n_arcs = len(fg)
        vis: set = set()
        comps = 0
        for s in fg:
            if s not in vis:
                comps += 1
                cur = s
                while cur not in vis:
                    vis.add(cur)
                    cur = fg[cur]

        is_h = (n_arcs == n) and (comps == 1)
        results["colours"].append({
            "colour":       c,
            "n_arcs":       n_arcs,
            "n_components": comps,
            "is_hamilton":  is_h,
        })
        if not is_h:
            results["valid"] = False

    return results


def score_sigma(sigma_list: list[int], arc_s: list, pa: list, n: int, k: int = 3) -> int:
    """
    Compute the SA score for an integer-array sigma.
    Score = sum(components_c - 1) for each color c.
    Score 0 means valid solution.
    """
    # Build functional graphs
    funcs = [np.zeros(n, dtype=np.uint32) for _ in range(k)]
    for v in range(n):
        pi = sigma_list[v]
        p = pa[pi]
        for c in range(k):
            funcs[c][v] = arc_s[v][p[c]]

    total_score = 0
    for c in range(k):
        f = funcs[c]
        vis = np.zeros(n, dtype=np.uint8)
        comps = 0
        for s in range(n):
            if not vis[s]:
                comps += 1
                cur = s
                while not vis[cur]:
                    vis[cur] = 1
                    cur = f[cur]
        total_score += (comps - 1)

    return int(total_score)

if HAS_NUMBA:
    @njit
    def _cc_numba(f, n, vis):
        vis[:] = 0
        c = 0
        for s in range(n):
            if not vis[s]:
                c += 1
                cur = s
                while not vis[cur]:
                    vis[cur] = 1
                    cur = f[cur]
        return c

    @njit
    def score_sigma_numba(sigma_list, arc_s, pa, n, k):
        total_score = 0
        vis = np.zeros(n, dtype=uint8)
        f = np.zeros(n, dtype=uint32)

        for c in range(k):
            # Extract functional graph for color c
            for v in range(n):
                pi = sigma_list[v]
                at = pa[pi, c]
                f[v] = arc_s[v, at]

            # Count components
            total_score += (_cc_numba(f, n, vis) - 1)

        return total_score
else:
    score_sigma_numba = score_sigma
