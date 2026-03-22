"""
symlib.search.equivariant
=========================
Equivariant simulated annealing — SA that knows the group structure.

THE KEY INSIGHT (from the m=6 depth-3 barrier finding)
-------------------------------------------------------
When SA stalls, the stuck configuration often has group structure.
For m=6 = Z_2 × Z_3, the Z_3 warm-start reaches score=9 and stalls
because single-vertex flips can't escape the Z_3 periodic structure.

The escape requires moves that span a subgroup orbit — flipping all
vertices in a Z_2-orbit simultaneously, or all vertices in a Z_3-orbit.

EQUIVARIANT MOVES
-----------------
Instead of: flip random vertex v
We add:     flip all vertices in a randomly chosen subgroup orbit of v

For m=6 (Z_2 × Z_3):
  Z_2-orbits: pairs {v, v+108}   (period-2 subgroup)
  Z_3-orbits: triples {v, v+36, v+72}  (period-3 subgroup)
  Full orbit: sets of 6 vertices related by all subgroup symmetries

The orbit size determines the move cost — a 6-vertex flip is harder
to accept but escapes barriers that 1-vertex flips cannot.

GENERALISATION
--------------
For any G_m where m = p · q (composite):
  Subgroup orbits come from the factor decomposition of Z_m.
  Each prime factor p of m generates a family of p-orbits.
  The barrier depth = number of prime factors in the stuck structure.

This is the algebraic content of the "depth-3 barrier" finding —
it's not depth-3 by accident, it's depth-3 because Z_6 = Z_2 × Z_3
has 2 prime factors, and escaping requires breaking both simultaneously.
"""

from __future__ import annotations
import math
import random
import time
from math import gcd
from itertools import permutations
from typing import Optional, Dict, Tuple, List

from symlib.kernel.verify import score_sigma


Sigma = Dict[Tuple[int,...], Tuple[int,...]]
_ALL_P3 = [list(p) for p in permutations(range(3))]


def prime_factors(n: int) -> List[int]:
    """Return distinct prime factors of n."""
    factors = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            factors.append(d)
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors


def build_subgroup_orbits(m: int) -> Dict[int, List[List[int]]]:
    """
    Build subgroup orbits for G_m (m³ vertices).

    For each prime factor p of m, the p-orbit of vertex v consists of
    all vertices reachable from v by the period-p subgroup action.

    Returns
    -------
    dict: prime_factor → list of orbits (each orbit = list of vertex indices)

    For m=6: {2: [[0,108], [1,109], ...], 3: [[0,36,72], [1,37,73], ...]}
    """
    n = m ** 3
    primes = prime_factors(m)
    orbits: Dict[int, List[List[int]]] = {}

    for p in primes:
        step = n // p          # orbit size = p, step between orbit members
        period = m // p        # period in each coordinate
        p_orbits: List[List[int]] = []
        seen = set()

        for v in range(n):
            if v in seen:
                continue
            orbit = []
            cur = v
            for _ in range(p):
                orbit.append(cur)
                seen.add(cur)
                # Advance by step (wraps through the period-p subgroup)
                i, rem = divmod(cur, m*m)
                j, k = divmod(rem, m)
                # Shift i-coordinate by period (one subgroup step)
                cur = ((i + period) % m) * m*m + j*m + k
            if len(orbit) == p:
                p_orbits.append(orbit)

        orbits[p] = p_orbits

    return orbits


def _build_sa_tables(m: int):
    """Build arc-successor and permutation-arc tables for G_m (k=3)."""
    n = m ** 3
    arc_s = [[0]*3 for _ in range(n)]
    for idx in range(n):
        i, rem = divmod(idx, m*m)
        j, k = divmod(rem, m)
        arc_s[idx][0] = ((i+1)%m)*m*m + j*m + k
        arc_s[idx][1] = i*m*m + ((j+1)%m)*m + k
        arc_s[idx][2] = i*m*m + j*m + (k+1)%m
    pa = [[None]*3 for _ in range(6)]
    for pi, p in enumerate(_ALL_P3):
        for at, c in enumerate(p):
            pa[pi][c] = at
    return n, arc_s, pa


def run_equivariant_sa(
    m:            int,
    seed:         int   = 0,
    max_iter:     int   = 5_000_000,
    T_init:       float = 3.0,
    T_min:        float = 0.003,
    p_orbit:      float = 0.15,    # probability of using an orbit move
    p_orbit_full: float = 0.05,    # probability of using full m-orbit move
    verbose:      bool  = False,
    report_n:     int   = 500_000,
) -> Tuple[Optional[Sigma], dict]:
    """
    Equivariant SA for G_m (k=3).

    Adds subgroup-orbit moves to standard SA to escape depth barriers
    caused by product structure in m (e.g., m=6 = Z_2 × Z_3).

    Parameters
    ----------
    m            : int    Fiber size
    seed         : int    Random seed
    max_iter     : int    Maximum SA iterations
    T_init       : float  Initial temperature
    T_min        : float  Final temperature
    p_orbit      : float  Probability of orbit move (vs single-vertex flip)
    p_orbit_full : float  Probability of full-orbit move
    verbose      : bool   Print progress
    report_n     : int    Report interval if verbose

    Returns
    -------
    (sigma | None, stats_dict)

    Key improvement over standard SA
    ---------------------------------
    Standard SA stalls at score=9 for m=6 because Z_3-structure creates
    a depth-3 local minimum.

    Equivariant SA escapes by flipping entire Z_2 or Z_3 subgroup orbits,
    which breaks the periodic structure directly. The orbit move is larger
    (higher cost to accept) but targets the exact structure causing the barrier.
    """
    n, arc_s, pa = _build_sa_tables(m)
    nP = 6
    rng = random.Random(seed)

    # Build subgroup orbits for group-aware moves
    subgroup_orbits = build_subgroup_orbits(m)
    all_orbit_lists = [
        orbit for orbits in subgroup_orbits.values()
        for orbit in orbits
    ]

    # Initialize sigma
    sigma = [rng.randrange(nP) for _ in range(n)]
    cs = score_sigma(sigma, arc_s, pa, n)
    bs = cs
    best = sigma[:]

    cool = (T_min / T_init) ** (1.0 / max_iter)
    T = T_init
    stall = 0
    reheats = 0
    orbit_moves = 0
    orbit_successes = 0
    t0 = time.perf_counter()

    for it in range(max_iter):
        if cs == 0:
            break

        move_type = rng.random()

        if move_type < p_orbit_full and all_orbit_lists:
            # Full-orbit move: flip all vertices in a subgroup orbit
            orbit = rng.choice(all_orbit_lists)
            old_vals = [sigma[v] for v in orbit]
            new_perm = rng.randrange(nP)
            for v in orbit:
                sigma[v] = new_perm
            ns = score_sigma(sigma, arc_s, pa, n)
            d = ns - cs
            orbit_moves += 1
            if d < 0 or (T > 1e-9 and rng.random() < math.exp(-d / T)):
                cs = ns
                if cs < bs:
                    bs = cs; best = sigma[:]; stall = 0
                    orbit_successes += 1
                else:
                    stall += 1
            else:
                for i, v in enumerate(orbit):
                    sigma[v] = old_vals[i]
                stall += 1

        elif move_type < p_orbit and all_orbit_lists:
            # Partial-orbit move: flip an orbit with independent new values
            orbit = rng.choice(all_orbit_lists)
            old_vals = [sigma[v] for v in orbit]
            new_vals = [rng.randrange(nP) for _ in orbit]
            for i, v in enumerate(orbit):
                sigma[v] = new_vals[i]
            ns = score_sigma(sigma, arc_s, pa, n)
            d = ns - cs
            orbit_moves += 1
            if d < 0 or (T > 1e-9 and rng.random() < math.exp(-d / T)):
                cs = ns
                if cs < bs:
                    bs = cs; best = sigma[:]; stall = 0
                    orbit_successes += 1
                else:
                    stall += 1
            else:
                for i, v in enumerate(orbit):
                    sigma[v] = old_vals[i]
                stall += 1

        else:
            # Standard single-vertex flip
            v = rng.randrange(n)
            old = sigma[v]
            new = rng.randrange(nP)
            if new == old:
                T *= cool
                continue
            sigma[v] = new
            ns = score_sigma(sigma, arc_s, pa, n)
            d = ns - cs
            if d < 0 or (T > 1e-9 and rng.random() < math.exp(-d / T)):
                cs = ns
                if cs < bs:
                    bs = cs; best = sigma[:]; stall = 0
                else:
                    stall += 1
            else:
                sigma[v] = old
                stall += 1

        # Reheat on stall — temperature guided by group structure
        if stall > 80_000:
            T = T_init / (2 ** reheats)
            reheats += 1
            stall = 0
            sigma = best[:]
            cs = bs

        T *= cool

        if verbose and (it + 1) % report_n == 0:
            elapsed = time.perf_counter() - t0
            print(
                f"  it={it+1:>8,} T={T:.5f} score={cs} best={bs} "
                f"reheats={reheats} orbit_moves={orbit_moves} "
                f"orbit_hits={orbit_successes} {elapsed:.1f}s"
            )

    elapsed = time.perf_counter() - t0
    sol = None
    if bs == 0:
        sol = {}
        for idx, pi in enumerate(best):
            i, rem = divmod(idx, m*m)
            j, k = divmod(rem, m)
            sol[(i,j,k)] = tuple(_ALL_P3[pi])

    return sol, {
        "best":             bs,
        "iters":            it + 1,
        "elapsed":          elapsed,
        "reheats":          reheats,
        "orbit_moves":      orbit_moves,
        "orbit_successes":  orbit_successes,
        "orbit_hit_rate":   (
            orbit_successes / orbit_moves if orbit_moves > 0 else 0.0
        ),
        "subgroup_primes":  list(subgroup_orbits.keys()),
    }


def run_parallel_equivariant_sa(
    m:        int,
    seeds:    List[int],
    max_iter: int   = 5_000_000,
    T_init:   float = 3.0,
    T_min:    float = 0.003,
    p_orbit:  float = 0.15,
) -> Tuple[Optional[Sigma], List[dict]]:
    """
    Run equivariant SA across multiple seeds in parallel.

    Returns (first_solution | None, all_stats).
    """
    from multiprocessing import Pool, cpu_count

    n_procs = min(len(seeds), cpu_count())

    def worker(args):
        m_, seed_, max_iter_, T_init_, T_min_, p_orbit_ = args
        return run_equivariant_sa(
            m_, seed=seed_, max_iter=max_iter_,
            T_init=T_init_, T_min=T_min_, p_orbit=p_orbit_,
        )

    args = [(m, s, max_iter, T_init, T_min, p_orbit) for s in seeds]
    all_stats = []
    best_sol = None

    with Pool(processes=n_procs) as pool:
        for sol, stats in pool.imap_unordered(worker, args):
            all_stats.append(stats)
            if sol and not best_sol:
                best_sol = sol

    return best_sol, all_stats
