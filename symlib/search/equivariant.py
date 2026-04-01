"""
symlib.search.equivariant
=========================
Group-equivariant simulated annealing for finding Hamiltonian decompositions.
Includes subgroup-orbit moves to escape depth-3+ barriers.
"""

from __future__ import annotations
import time
import math
import random
import json
import os
from itertools import permutations
from typing import Dict, Tuple, List, Optional, Any
import numpy as np

from symlib.kernel.verify import score_sigma_numba, Sigma

def prime_factors(n: int) -> List[int]:
    """Return distinct prime factors of n."""
    factors = []
    d = 2
    temp = n
    while d * d <= temp:
        if temp % d == 0:
            factors.append(d)
            while temp % d == 0:
                temp //= d
        d += 1
    if temp > 1:
        factors.append(temp)
    return factors


def build_subgroup_orbits(m: int, k: int = 3) -> Dict[int, List[List[int]]]:
    """
    Find orbits of Z_m^k vertices under Z_p subgroup actions for p | m.
    Returns {p: [list_of_orbits]}.
    """
    n = m ** k
    primes = prime_factors(m)
    orbits = {}

    for p in primes:
        period = m // p
        vis = [False] * n
        p_orbits = []

        for s in range(n):
            if vis[s]: continue
            orbit = []
            cur = s
            # Subgroup action: i -> i + m/p
            while not vis[cur]:
                vis[cur] = True
                orbit.append(cur)
                # Advance by period (shift first coordinate)
                coords = []
                temp = cur
                for _ in range(k):
                    coords.append(temp % m)
                    temp //= m
                coords[k-1] = (coords[k-1] + period) % m
                new_v = 0
                for d in reversed(range(k)):
                    new_v = new_v * m + coords[d]
                cur = new_v
            if len(orbit) == p:
                p_orbits.append(orbit)

        orbits[p] = p_orbits

    return orbits


def _build_sa_tables(m: int, k: int = 3):
    """Build arc-successor and permutation-arc tables for G_m,k."""
    n = m ** k
    arc_s = np.zeros((n, k), dtype=np.uint32)
    for idx in range(n):
        coords = []
        temp = idx
        for _ in range(k):
            coords.append(temp % m)
            temp //= m
        for at in range(k):
            # Advance in dimension at
            new_coords = list(coords)
            new_coords[at] = (new_coords[at] + 1) % m
            new_v = 0
            for d in reversed(range(k)):
                new_v = new_v * m + new_coords[d]
            arc_s[idx, at] = new_v

    all_perms = [list(p) for p in permutations(range(k))]
    nP = len(all_perms)
    pa = np.zeros((nP, k), dtype=np.uint32)
    for pi, p in enumerate(all_perms):
        for at, c in enumerate(p):
            pa[pi, c] = at
    return n, arc_s, pa, all_perms


def save_checkpoint(path: str, m: int, k: int, sigma_list: List[int], stats: Dict[str, Any]):
    """Save search state to a JSON file."""
    data = {
        "m": m,
        "k": k,
        "sigma_list": sigma_list,
        "stats": stats,
        "timestamp": time.time()
    }
    with open(path, "w") as f:
        json.dump(data, f)


def load_checkpoint(path: str) -> Optional[Dict[str, Any]]:
    """Load search state from a JSON file."""
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


def run_equivariant_sa(
    m:            int,
    k:            int   = 3,
    seed:         int   = 0,
    max_iter:     int   = 5_000_000,
    T_init:       float = 3.0,
    T_min:        float = 0.003,
    p_orbit:      float = 0.15,    # probability of using an orbit move
    p_orbit_full: float = 0.05,    # probability of using full m-orbit move
    p_super:      float = 0.02,    # probability of multi-orbit super-move
    initial_sigma: Optional[List[int]] = None,
    verbose:      bool  = False,
    report_n:     int   = 500_000,
    checkpoint_path: Optional[str] = None,
    checkpoint_n:    int = 1_000_000,
) -> Tuple[Optional[Sigma], dict]:
    """
    Equivariant SA for G_m,k.
    """
    n, arc_s, pa, all_perms = _build_sa_tables(m, k)
    nP = len(all_perms)
    rng = random.Random(seed)

    # Build subgroup orbits for group-aware moves
    subgroup_orbits = build_subgroup_orbits(m, k)
    all_orbit_lists = [
        orbit for orbits in subgroup_orbits.values()
        for orbit in orbits
    ]
    primes = list(subgroup_orbits.keys())

    # Initialize sigma
    if initial_sigma is not None and len(initial_sigma) == n:
        sigma = np.array(initial_sigma, dtype=np.uint32)
    else:
        sigma = np.array([rng.randrange(nP) for _ in range(n)], dtype=np.uint32)

    cs = score_sigma_numba(sigma, arc_s, pa, n, k)
    bs = cs
    best = sigma.copy()

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

        if move_type < p_super and len(primes) > 1:
            # SUPER-MOVE: Flip multiple orbits from different prime factors
            orbits_to_flip = []
            for p in primes:
                orbits_to_flip.append(rng.choice(subgroup_orbits[p]))

            affected_vertices = [v for orb in orbits_to_flip for v in orb]
            old_vals = [sigma[v] for v in affected_vertices]

            for orb in orbits_to_flip:
                new_p = rng.randrange(nP)
                for v in orb: sigma[v] = new_p

            ns = score_sigma_numba(sigma, arc_s, pa, n, k)
            d = ns - cs
            orbit_moves += 1
            if d < 0 or (T > 1e-9 and rng.random() < math.exp(-d / T)):
                cs = ns
                if cs < bs:
                    bs = cs; best = sigma.copy(); stall = 0; orbit_successes += 1
                else: stall += 1
            else:
                for i, v in enumerate(affected_vertices): sigma[v] = old_vals[i]
                stall += 1

        elif move_type < p_orbit_full and all_orbit_lists:
            orbit = rng.choice(all_orbit_lists)
            old_vals = [sigma[v] for v in orbit]
            new_perm = rng.randrange(nP)
            for v in orbit:
                sigma[v] = new_perm
            ns = score_sigma_numba(sigma, arc_s, pa, n, k)
            d = ns - cs
            orbit_moves += 1
            if d < 0 or (T > 1e-9 and rng.random() < math.exp(-d / T)):
                cs = ns
                if cs < bs:
                    bs = cs; best = sigma.copy(); stall = 0
                    orbit_successes += 1
                else:
                    stall += 1
            else:
                for i, v in enumerate(orbit):
                    sigma[v] = old_vals[i]
                stall += 1

        elif move_type < p_orbit and all_orbit_lists:
            orbit = rng.choice(all_orbit_lists)
            old_vals = [sigma[v] for v in orbit]
            new_vals = [rng.randrange(nP) for _ in orbit]
            for i, v in enumerate(orbit):
                sigma[v] = new_vals[i]
            ns = score_sigma_numba(sigma, arc_s, pa, n, k)
            d = ns - cs
            orbit_moves += 1
            if d < 0 or (T > 1e-9 and rng.random() < math.exp(-d / T)):
                cs = ns
                if cs < bs:
                    bs = cs; best = sigma.copy(); stall = 0
                    orbit_successes += 1
                else:
                    stall += 1
            else:
                for i, v in enumerate(orbit):
                    sigma[v] = old_vals[i]
                stall += 1

        else:
            v = rng.randrange(n)
            old = sigma[v]
            new = rng.randrange(nP)
            if new == old:
                T *= cool
                continue
            sigma[v] = new
            ns = score_sigma_numba(sigma, arc_s, pa, n, k)
            d = ns - cs
            if d < 0 or (T > 1e-9 and rng.random() < math.exp(-d / T)):
                cs = ns
                if cs < bs:
                    bs = cs; best = sigma.copy(); stall = 0
                else:
                    stall += 1
            else:
                sigma[v] = old
                stall += 1

        if stall > 100_000:
            T = T_init / (1.5 ** reheats)
            reheats += 1
            stall = 0
            sigma = best.copy()
            cs = bs

        T *= cool

        if verbose and (it + 1) % report_n == 0:
            elapsed = time.perf_counter() - t0
            print(
                f"  it={it+1:>8,} T={T:.5f} score={cs} best={bs} "
                f"reheats={reheats} orbit_moves={orbit_moves} "
                f"orbit_hits={orbit_successes} {elapsed:.1f}s"
            )

        if checkpoint_path and (it + 1) % checkpoint_n == 0:
            save_checkpoint(checkpoint_path, m, k, best.tolist(), {
                "best": bs, "iters": it + 1, "reheats": reheats
            })

    elapsed = time.perf_counter() - t0
    sol = None
    if bs == 0:
        sol = {}
        for idx, pi in enumerate(best):
            coords = []
            temp = idx
            for _ in range(k):
                coords.append(temp % m)
                temp //= m
            sol[tuple(coords)] = tuple(all_perms[pi])

    final_stats = {
        "best":             bs,
        "iters":            it + 1,
        "elapsed":          elapsed,
        "reheats":          reheats,
        "orbit_moves":      orbit_moves,
        "orbit_successes":  orbit_successes,
        "sigma_list":       best.tolist(),
    }

    if checkpoint_path:
        save_checkpoint(checkpoint_path, m, k, best.tolist(), final_stats)

    return sol, final_stats


def _parallel_worker(args):
    """Module-level worker for parallel SA."""
    m_, k_, seed_, max_iter_, T_init_, T_min_, p_orbit_ = args
    return run_equivariant_sa(
        m_, k=k_, seed=seed_, max_iter=max_iter_,
        T_init=T_init_, T_min=T_min_, p_orbit=p_orbit_,
    )


def run_parallel_equivariant_sa(
    m:        int,
    k:        int   = 3,
    seeds:    List[int] = [0],
    max_iter: int   = 5_000_000,
    T_init:   float = 3.0,
    T_min:    float = 0.003,
    p_orbit:  float = 0.15,
) -> Tuple[Optional[Sigma], List[dict]]:
    """
    Run equivariant SA across multiple seeds in parallel.
    """
    from multiprocessing import Pool, cpu_count

    n_procs = min(len(seeds), cpu_count())
    args = [(m, k, s, max_iter, T_init, T_min, p_orbit) for s in seeds]
    all_stats = []
    best_sol = None

    with Pool(processes=n_procs) as pool:
        for sol, stats in pool.imap_unordered(_parallel_worker, args):
            all_stats.append(stats)
            if sol and not best_sol:
                best_sol = sol

    return best_sol, all_stats
