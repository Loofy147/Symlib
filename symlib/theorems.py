"""
symlib.theorems
===============
Formal statements and O(1) checkers for the 10 core theorems.

These are the "laws of physics" for the symlib kernel. They are pure,
deterministic, and (mostly) verified in Lean 4.
"""

from __future__ import annotations
from math import gcd
from typing import List, Tuple, Optional
from dataclasses import dataclass
from symlib.kernel.weights import phi, extract_weights, coprime_elements

# ── Parity Obstruction (Theorem 6.1) ──────────────────────────────────────────

@dataclass(frozen=True)
class ObstructionResult:
    blocked: bool
    reason:  str
    fix:     str

    def __bool__(self): return self.blocked

    def to_lean4(self) -> str:
        """Export this result as a Lean 4 theorem claim."""
        if not self.blocked:
            return "-- No parity obstruction found for this (m, k) pair."
        return (
            f"-- THEOREM 6.1: m even, k odd -> impossible\n"
            f"theorem obstruction_m_even_k_odd : False := by sorry"
        )


class ParityObstruction:
    """
    Theorem 6.1 — The H² parity obstruction.

    A k-Hamiltonian decomposition of G_m with coprime shifts
    is impossible if m is even and k is odd.
    """

    @staticmethod
    def check(m: int, k: int) -> ObstructionResult:
        blocked = (m % 2 == 0) and (k % 2 == 1)
        return ObstructionResult(
            blocked=blocked,
            reason=(
                "" if not blocked else
                f"H² parity obstruction: m={m} (even) and k={k} (odd). "
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


# ── Function Counter (Theorem 4.1) ───────────────────────────────────────────

class FunctionCounter:
    """
    Theorem 4.1 — Number of coprime-sum functions b: Z_m -> Z_m.

    N_b(m) = m^(m-1) * phi(m).
    """
    @staticmethod
    def count(m: int) -> int:
        """Return N_b(m)."""
        return (m**(m-1)) * phi(m)


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
        """Return the smallest step giving full coverage."""
        return next(r for r in range(1, space) if gcd(r, space) == 1)


# ── Quotient Counter (W4) ─────────────────────────────────────────────────────

class QuotientCounter:
    """
    W4 Theorem — count distinct states via phi(m).
    """

    @staticmethod
    def distinct_states(m: int) -> int:
        return phi(m)

    @staticmethod
    def raw_vs_distinct(m: int) -> dict:
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

    |M_k(G_m)| = phi(m) * N_b(m)^(k-1)
    """

    @staticmethod
    def estimate(m: int, k: int) -> dict:
        w = extract_weights(m, k)
        nb = FunctionCounter.count(m)
        sol_lb = phi(m) * (nb**(k-1)) if w.r_count > 0 else 0
        return {
            "m":           m,
            "k":           k,
            "sol_lb":      sol_lb,
            "is_exact":    m == 3,
            "h1_order":    w.h1_exact,
            "orbit_size":  w.orbit_size,
            "formula":     (
                f"phi({m}) * N_b({m})^({k}-1) = "
                f"{w.h1_exact} * {nb}^{k-1}"
            ),
        }


# ── Canonical Seed (Theorem 7.1) ──────────────────────────────────────────────

class CanonicalSeed:
    """
    Theorem 7.1 — Direct construction seed for odd m.
    """

    @staticmethod
    def for_odd_m(m: int) -> Optional[Tuple[int,...]]:
        if m % 2 == 0:
            return None
        seed = (1, m-2, 1)
        assert all(gcd(r, m) == 1 for r in seed)
        assert sum(seed) == m
        return seed

    @staticmethod
    def verify(seed: Tuple[int,...], m: int) -> bool:
        """Verify a seed is valid for fiber size m."""
        return (
            all(gcd(r, m) == 1 for r in seed) and
            sum(seed) == m
        )


# ── Spike Theorem (Theorem 8.1) ───────────────────────────────────────────────

class SpikeTheorem:
    """
    Theorem 8.1 — Spike construction for odd m.
    """
    @staticmethod
    def check(m: int) -> bool:
        return m % 2 == 1 and m >= 3


# ── Depth Barrier Analyzer ────────────────────────────────────────────────────

class DepthBarrierAnalyzer:
    """
    Analyze the group structure of a stuck optimization state.
    """

    @staticmethod
    def analyze(m: int) -> dict:
        from symlib.search.equivariant import prime_factors
        primes = prime_factors(m)
        is_prime = len(primes) == 1 and primes[0] == m

        if is_prime:
            strategy = f"m={m} is prime. Standard SA should work."
        else:
            strategy = f"Z_{m} product structure found. Use equivariant moves."

        return {
            "m":              m,
            "primes":         primes,
            "barrier_depth":  len(primes),
            "orbit_sizes":    primes,
            "is_prime":       is_prime,
            "escape_strategy": strategy,
            "recommended_p_orbit": 0.1 * len(primes),
        }
