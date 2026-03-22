"""
symlib.theorems
===============
Standalone theorem utilities — applicable to any symmetric system.

These are the library's theorems extracted as general-purpose tools.
Each one works without knowing anything about Cayley digraphs.
Import just what you need.

    from symlib.theorems import ParityObstruction
    result = ParityObstruction.check(m=8, k=3)
    if result.blocked:
        print(result.explain())

UTILITIES
---------
ParityObstruction     Thm 6.1 — O(1) impossibility for even m, odd k
CoprimeCoverage       Thm 5.1 — does step r cover all n positions?
QuotientCounter       W4      — count distinct states via φ(m)
TorsorEstimate        W7      — estimate solution space size
DepthBarrierAnalyzer  SA      — detect group-structure local minima
CanonicalSeed         Thm 7.1 — direct construction seed for odd m
"""

from __future__ import annotations
from math import gcd
from dataclasses import dataclass
from typing import Optional, List, Tuple

from symlib.kernel.weights import extract_weights, phi, coprime_elements


# ── Parity Obstruction ────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ParityResult:
    blocked:  bool
    reason:   str
    fix:      str   # How to fix if blocked

    def __bool__(self): return self.blocked
    def explain(self) -> str:
        lines = [f"ParityObstruction: {'BLOCKED' if self.blocked else 'clear'}"]
        if self.blocked:
            lines += [f"  Reason: {self.reason}", f"  Fix: {self.fix}"]
        return "\n".join(lines)


class ParityObstruction:
    """
    Theorem 6.1 — Parity check before any search.

    Applies to ANY system where:
    - You have k items that must each be coprime to m
    - Their sum must equal m

    If m is even and k is odd, this is IMPOSSIBLE — O(1) proof.

    Examples
    --------
    # Thread scheduler: 3 task types, 8 time slots
    # Each task duration must be coprime to 8 (so: 1, 3, 5, 7)
    # 3 odd durations summing to 8? Impossible.
    result = ParityObstruction.check(m=8, k=3)
    # → blocked=True

    # 2 task types, 8 time slots: possible (2 odds can sum to 8: 3+5=8)
    result = ParityObstruction.check(m=8, k=2)
    # → blocked=False

    # Network flow: 5 arc types, capacity 12
    result = ParityObstruction.check(m=12, k=5)
    # → blocked=True (5 odds can't sum to 12)
    """

    @staticmethod
    def check(m: int, k: int) -> ParityResult:
        """
        Check parity obstruction for (m, k).

        Parameters
        ----------
        m : int   Modulus (space size, number of slots, etc.)
        k : int   Number of items (colours, tasks, arc types, etc.)

        Returns
        -------
        ParityResult with blocked=True if impossible.
        """
        cp = coprime_elements(m)
        if not cp:
            return ParityResult(
                blocked=False, reason="", fix=""
            )

        all_odd = all(r % 2 == 1 for r in cp)
        blocked = all_odd and (k % 2 == 1) and (m % 2 == 0)

        if not blocked:
            return ParityResult(blocked=False, reason="", fix="")

        return ParityResult(
            blocked=True,
            reason=(
                f"m={m} is even → all coprime-to-{m} elements {list(cp)} are odd. "
                f"Sum of k={k} odd numbers is odd ≠ {m} (even)."
            ),
            fix=(
                f"Use even k (e.g., k={k+1}) or odd m. "
                f"Alternatively, relax the coprimality requirement."
            ),
        )

    @staticmethod
    def check_batch(problems: List[Tuple[int,int]]) -> dict:
        """Check multiple (m, k) pairs at once."""
        return {(m,k): ParityObstruction.check(m, k) for m, k in problems}


# ── Coprime Coverage ──────────────────────────────────────────────────────────

@dataclass(frozen=True)
class CoverageResult:
    covers_all:  bool
    period:      int   # actual period (= space_size if covers_all)
    space_size:  int
    reason:      str

    def __bool__(self): return self.covers_all
    def coverage_fraction(self) -> float:
        return self.period / self.space_size if self.space_size > 0 else 0.0


class CoprimeCoverage:
    """
    Theorem 5.1 — Coverage check for step-and-wrap systems.

    Does step size r cover all positions in a circular space of size n?
    Answer: yes iff gcd(r, n) = 1.

    Examples
    --------
    # Hash table: does stride 7 cover all 16 buckets?
    CoprimeCoverage.check(step=7, space=16)   # → True (gcd(7,16)=1)
    CoprimeCoverage.check(step=4, space=16)   # → False (gcd(4,16)=4)

    # Scheduler: does worker step 3 cover 9 task slots?
    CoprimeCoverage.check(step=3, space=9)    # → False (gcd(3,9)=3)
    CoprimeCoverage.check(step=2, space=9)    # → True (gcd(2,9)=1)

    # Encryption key schedule: does 3-bit rotation cover 8 positions?
    CoprimeCoverage.check(step=3, space=8)    # → False (gcd(3,8)=1 → True!)
    CoprimeCoverage.check(step=4, space=8)    # → False (gcd(4,8)=4)
    """

    @staticmethod
    def check(step: int, space: int) -> CoverageResult:
        g = gcd(step, space)
        period = space // g
        covers = (g == 1)
        return CoverageResult(
            covers_all=covers,
            period=period,
            space_size=space,
            reason=(
                "" if covers else
                f"gcd({step}, {space}) = {g} ≠ 1. "
                f"Covers only {period}/{space} positions. "
                f"Use step coprime to {space} (e.g., {next(r for r in range(1,space) if gcd(r,space)==1)})."
            ),
        )

    @staticmethod
    def valid_steps(space: int) -> List[int]:
        """Return all step sizes that give full coverage of space."""
        return [r for r in range(1, space) if gcd(r, space) == 1]

    @staticmethod
    def smallest_valid_step(space: int) -> int:
        """Return the smallest step giving full coverage (always 1, but useful for context)."""
        return next(r for r in range(1, space) if gcd(r, space) == 1)


# ── Quotient Counter (W4) ─────────────────────────────────────────────────────

class QuotientCounter:
    """
    W4 Theorem — count distinct states via φ(m).

    When a system of size m has a symmetry group acting on it,
    the number of DISTINCT states (up to symmetry) is φ(m),
    NOT the raw count m or m! or 2^m.

    The W4 error: counting raw states instead of equivalence classes
    gives wrong answers by factors of up to m^(m-1).

    Examples
    --------
    # How many distinct hash rotation strategies for a table of size 12?
    QuotientCounter.distinct_states(12)  # → φ(12) = 4

    # How many distinct build orderings for 7-step cyclic pipeline?
    QuotientCounter.distinct_states(7)   # → φ(7) = 6

    # Cache: how many distinct invalidation strategies for cache of size 9?
    QuotientCounter.distinct_states(9)   # → φ(9) = 6
    """

    @staticmethod
    def distinct_states(m: int) -> int:
        """
        Number of genuinely distinct states for a size-m cyclic system.
        = φ(m) (Euler totient).
        """
        return phi(m)

    @staticmethod
    def raw_vs_distinct(m: int) -> dict:
        """
        Compare raw state count vs distinct state count for size-m system.
        Shows the W4 correction factor.
        """
        phi_m = phi(m)
        return {
            "m":                 m,
            "raw_states":        m,
            "distinct_states":   phi_m,
            "correction_factor": m / phi_m if phi_m > 0 else float("inf"),
            "coprime_elements":  list(coprime_elements(m)),
        }

    @staticmethod
    def enumeration_warning(m: int, k: int) -> Optional[str]:
        """
        Return a warning if enumerating raw states instead of orbits
        would be wasteful for problem (m, k).

        Returns None if the problem is small enough that it doesn't matter.
        """
        raw = m ** k
        distinct = phi(m) ** k
        if raw > distinct * 10:
            return (
                f"Warning: enumerating {raw:,} raw states "
                f"when only {distinct:,} are distinct. "
                f"Use orbit representatives to reduce work by {raw//distinct:,}×."
            )
        return None


# ── Torsor Estimate (W7) ──────────────────────────────────────────────────────

class TorsorEstimate:
    """
    W7 — Estimate the size of the solution space.

    |M_k(G_m)| = φ(m) × coprime_b(m)^(k-1)
    where coprime_b(m) = m^(m-1) · φ(m).

    This is the number of valid solutions BEFORE any search.
    For m=3 it's exact. For m≥5 it's a lower bound.

    Use this to decide:
    - Is exhaustive enumeration feasible?
    - How many test cases cover the solution space?
    - Does finding one solution give you all of them (if torsor)?
    """

    @staticmethod
    def estimate(m: int, k: int) -> dict:
        w = extract_weights(m, k)
        return {
            "m":           m,
            "k":           k,
            "sol_lb":      w.sol_lb,
            "is_exact":    m == 3,
            "h1_order":    w.h1_exact,
            "orbit_size":  w.orbit_size,
            "formula":     (
                f"φ({m}) × coprime_b({m})^({k}-1) = "
                f"{w.h1_exact} × {m**(m-1)*w.h1_exact}^{k-1}"
            ),
        }


# ── Canonical Seed (Theorem 7.1) ──────────────────────────────────────────────

class CanonicalSeed:
    """
    Theorem 7.1 — Direct construction seed for odd m.

    For any odd m ≥ 3 and k=3:
    The r-triple (1, m-2, 1) is always valid:
        gcd(1, m) = 1  ✓
        gcd(m-2, m) = 1  (m odd → m-2 odd → coprime to m)  ✓
        1 + (m-2) + 1 = m  ✓

    This gives a direct construction path without search.

    Examples
    --------
    CanonicalSeed.for_odd_m(5)   # → (1, 3, 1)
    CanonicalSeed.for_odd_m(7)   # → (1, 5, 1)
    CanonicalSeed.for_odd_m(11)  # → (1, 9, 1)
    """

    @staticmethod
    def for_odd_m(m: int) -> Optional[Tuple[int,...]]:
        """
        Return the canonical r-triple for odd m.
        Returns None if m is even (no canonical triple guaranteed).
        """
        if m % 2 == 0:
            return None
        seed = (1, m-2, 1)
        # Verify
        assert all(gcd(r, m) == 1 for r in seed), f"Seed {seed} not coprime to {m}"
        assert sum(seed) == m, f"Seed {seed} doesn't sum to {m}"
        return seed

    @staticmethod
    def verify(seed: Tuple[int,...], m: int) -> bool:
        """Verify a seed is valid for fiber size m."""
        return (
            all(gcd(r, m) == 1 for r in seed) and
            sum(seed) == m
        )


# ── Depth Barrier Analyzer ────────────────────────────────────────────────────

class DepthBarrierAnalyzer:
    """
    Analyze the group structure of a stuck optimization state.

    When SA or any optimizer stalls, the stuck state often has
    group structure. Identifying that structure tells you exactly
    what kind of move escapes it.

    From the m=6 finding: Z_6 = Z_2 × Z_3 creates a depth-3 barrier
    because the stuck state is invariant under the Z_3 subgroup action.
    Escaping requires moves spanning Z_3-orbits.

    General rule: barrier depth = number of prime factors of m.

    Examples
    --------
    DepthBarrierAnalyzer.analyze(m=6)
    # → {primes: [2,3], barrier_depth: 2, orbit_sizes: [2,3],
    #    escape_strategy: "Use Z_2-orbit or Z_3-orbit flips"}

    DepthBarrierAnalyzer.analyze(m=12)
    # → {primes: [2,3], barrier_depth: 2, ...}
    # m=12=2²×3 has same prime factors as m=6, same depth

    DepthBarrierAnalyzer.analyze(m=30)
    # → {primes: [2,3,5], barrier_depth: 3, ...}
    # Three prime factors → depth-3 barrier → need 3-orbit coordinated moves
    """

    @staticmethod
    def analyze(m: int) -> dict:
        """
        Analyze the barrier structure for fiber size m.

        Returns
        -------
        dict with:
            primes          : List[int]  prime factors of m
            barrier_depth   : int        = len(primes)
            orbit_sizes     : List[int]  subgroup orbit sizes (= prime factors)
            escape_strategy : str        what kind of moves are needed
            is_prime        : bool       True if m is prime (no barrier)
        """
        from symlib.search.equivariant import prime_factors
        primes = prime_factors(m)
        is_prime = len(primes) == 1 and primes[0] == m

        if is_prime:
            strategy = (
                f"m={m} is prime — no product structure, no group-structure barrier. "
                f"Standard SA should work."
            )
        else:
            factor_str = " × ".join(f"Z_{p}" for p in primes)
            strategy = (
                f"Z_{m} = {factor_str}. "
                f"Depth-{len(primes)} barrier possible. "
                f"Use equivariant moves spanning {', '.join(str(p)+'-orbits' for p in primes)}. "
                f"Orbit sizes: {primes}."
            )

        return {
            "m":              m,
            "primes":         primes,
            "barrier_depth":  len(primes),
            "orbit_sizes":    primes,
            "is_prime":       is_prime,
            "escape_strategy": strategy,
            "recommended_p_orbit": 0.1 * len(primes),  # scale with complexity
        }
