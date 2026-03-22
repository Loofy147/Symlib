"""
symlib.kernel.verify
====================
Verification of sigma maps — pure, deterministic, O(m³).

WHAT IT CHECKS
--------------
A sigma map σ: Z_m³ → S_3 is valid iff for each colour c ∈ {0,1,2}:
  1. Every vertex has exactly one outgoing arc of colour c  (well-defined)
  2. Every vertex has exactly one incoming arc of colour c  (in-degree 1)
  3. The induced functional graph has exactly 1 component   (Hamiltonian)

Equivalently: the three functions f_c: v → arc_c(v) are each a single
m³-cycle (permutation with one cycle covering all vertices).

This check is the ground truth. A solution is valid iff verify returns True.
No approximation. No heuristic. Exact.
"""

from __future__ import annotations
from typing import Dict, Tuple, Optional

Sigma = Dict[Tuple[int,...], Tuple[int,...]]
_SHIFTS = ((1,0,0), (0,1,0), (0,0,1))


def verify_sigma(sigma: Sigma, m: int) -> bool:
    """
    Verify σ: Z_m³ → S_3 yields three directed Hamiltonian cycles.

    Parameters
    ----------
    sigma : dict  {(i,j,k): (p0,p1,p2)} where (p0,p1,p2) ∈ S_3
    m     : int   Fiber size. Vertex set is Z_m³.

    Returns
    -------
    True iff sigma is a valid k=3 Hamiltonian decomposition of G_m.

    Complexity
    ----------
    O(m³) time, O(m³) space.
    """
    n = m ** 3
    funcs: list[dict] = [{}, {}, {}]

    for v, p in sigma.items():
        for at in range(3):
            nb = tuple((v[d] + _SHIFTS[at][d]) % m for d in range(3))
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


def verify_and_diagnose(sigma: Sigma, m: int) -> dict:
    """
    Verify sigma and return detailed diagnostics on failure.

    Mirrors verify_sigma: for arc type `at`, color is p[at] = sigma[v][at].
    Builds all three functional graphs simultaneously.

    Returns
    -------
    dict with keys:
        valid       : bool
        n_vertices  : int
        colours     : list of dicts, one per colour:
            colour      : int
            n_arcs      : int
            n_components: int
            is_hamilton : bool
    """
    n = m ** 3

    # Build all functional graphs at once — same logic as verify_sigma
    funcs: list[dict] = [{}, {}, {}]
    for v, p in sigma.items():
        for at in range(3):
            nb = tuple((v[d] + _SHIFTS[at][d]) % m for d in range(3))
            funcs[p[at]][v] = nb

    results = {"valid": True, "n_vertices": n, "colours": []}

    for c in range(3):
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


def score_sigma(sigma_list: list[int], arc_s: list, pa: list, n: int) -> int:
    """
    Compute the SA score for an integer-array sigma.
    Score = (components_c0 - 1) + (components_c1 - 1) + (components_c2 - 1).
    Score 0 means valid solution.

    Parameters
    ----------
    sigma_list : list[int]   Index into permutation table for each vertex
    arc_s      : list        arc_s[v][at] = successor of v via arc type at
    pa         : list        pa[pi][c] = arc type for colour c in perm pi
    n          : int         number of vertices

    Returns
    -------
    int  0 means valid, >0 means number of extra components across 3 colours
    """
    f0 = [0]*n; f1 = [0]*n; f2 = [0]*n
    for v in range(n):
        pi = sigma_list[v]; p = pa[pi]
        f0[v] = arc_s[v][p[0]]
        f1[v] = arc_s[v][p[1]]
        f2[v] = arc_s[v][p[2]]

    def cc(f: list) -> int:
        vis = bytearray(n); c = 0
        for s in range(n):
            if not vis[s]:
                c += 1; cur = s
                while not vis[cur]:
                    vis[cur] = 1; cur = f[cur]
        return c

    return cc(f0)-1 + cc(f1)-1 + cc(f2)-1
