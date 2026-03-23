"""
symlib.kernel.obstruction
=========================
Obstruction theory — check structural impossibility before any search.

THEOREMS IMPLEMENTED
--------------------
Thm 6.1  Parity Obstruction
    Even fiber size m, odd k → H² obstruction → any column-uniform construction (r-tuple) is impossible.
    The sum of k odd numbers (coprime-to-even) cannot equal m (even).
    O(1). Returns a formal proof object.

Thm 5.1  Single-Cycle Condition
    A twisted translation Q_c is an m²-cycle iff:
        gcd(r, m) = 1  AND  gcd(Σb, m) = 1
    O(log m) per check.

Fiber-Uniform Obstruction (Thm 10.1)
    For k=4, m=4: no fiber-uniform σ works.
    24^4 = 331,776 cases exhaustively checked.
    Higher-level obstruction — absent at H² level but present at H³.

STANDALONE USAGE
----------------
These checkers work for ANY symmetric system where:
- You have a set of elements that must be coprime to a modulus
- You need a k-tuple of those elements summing to the modulus

Examples beyond Cayley digraphs:
- Thread scheduler: can k task types with odd durations fill m time slots?
- Network flow: can k arc capacities (coprime to network size) sum to m?
- Hash coverage: does a step of size r in a table of size m cover all slots?
- Key schedule: does k-round schedule cover all bit positions in m-bit register?
"""

from __future__ import annotations
from math import gcd
from dataclasses import dataclass, field
from typing import Optional
from itertools import product as iprod

from symlib.kernel.weights import extract_weights, Weights, coprime_elements


@dataclass(frozen=True)
class ObstructionResult:
    """
    Result of an obstruction check.

    Attributes
    ----------
    blocked : bool
        True means proved impossible — no solution exists.
    obstruction_type : str
        Which theorem triggered. Empty string if no obstruction.
    proof_steps : tuple[str, ...]
        Formal proof steps, human and machine readable.
    level : int
        Which cohomology level (H², H³, ...) the obstruction lives in.
    """
    blocked:          bool
    obstruction_type: str
    proof_steps:      tuple[str, ...]
    level:            int = 2
    evidence:         str = ""

    def __bool__(self) -> bool:
        return self.blocked

    def explain(self) -> str:
        if not self.blocked:
            return f"No obstruction found at H{self.level}."
        lines = [f"OBSTRUCTION [{self.obstruction_type}] at H{self.level}:"]
        for i, step in enumerate(self.proof_steps, 1):
            lines.append(f"  ({i}) {step}")
        if self.evidence:
            lines.append(f"  Evidence: {self.evidence}")
        return "\n".join(lines)


# Sentinel for "no obstruction"
NO_OBSTRUCTION = ObstructionResult(
    blocked=False,
    obstruction_type="",
    proof_steps=(),
    level=2,
)


class ObstructionChecker:
    """
    Check structural obstructions for any symmetric combinatorial problem.

    The checker runs through the obstruction tower in order — H² first,
    then higher levels if H² is clear. Returns the first obstruction found,
    or NO_OBSTRUCTION if none exists at any checked level.

    Parameters
    ----------
    m : int  Fiber size (modulus). |G/H| in the SES.
    k : int  Number of colours / arc types.

    Usage
    -----
    checker = ObstructionChecker(m=6, k=3)
    result = checker.check()
    if result:
        print(result.explain())
    else:
        print("No obstruction — solution may exist, proceed to construction.")

    Standalone (any symmetric system)
    ----------------------------------
    # Does a scheduler with m=8 time slots and k=3 odd-duration tasks work?
    checker = ObstructionChecker(m=8, k=3)
    result = checker.h2_parity()
    # Returns obstruction if sum of 3 odd numbers can't equal 8

    # Does step size r cover all n slots in a circular buffer?
    result = ObstructionChecker.single_cycle_check(r=3, b_sum=1, m=7)
    """

    def __init__(self, m: int, k: int):
        self.m = m
        self.k = k
        self._weights: Optional[Weights] = None

    @property
    def weights(self) -> Weights:
        if self._weights is None:
            self._weights = extract_weights(self.m, self.k)
        return self._weights

    def check(self) -> ObstructionResult:
        """
        Run full obstruction tower. Returns first obstruction found.
        Currently checks H² (parity) then H³ (fiber-uniform for k=4, m=4).
        """
        h2 = self.h2_parity()
        if h2.blocked:
            return h2
        h3 = self.h3_fiber_uniform()
        if h3.blocked:
            return h3
        return NO_OBSTRUCTION

    def h2_parity(self) -> ObstructionResult:
        """
        Theorem 6.1 — Parity Obstruction.

        H²(Z_2, Z/2) = Z/2. The obstruction class γ₂ is nontrivial
        when: m is even AND k is odd AND all coprime-to-m elements are odd.

        In that case, any k-tuple of coprime elements sums to an odd number, which means no column-uniform construction (r-tuple) can exist.
        which cannot equal m (even). Contradiction.

        O(1) — no search, no construction attempt needed.
        """
        m, k = self.m, self.k
        cp = coprime_elements(m)

        if not cp:
            return NO_OBSTRUCTION

        all_odd = all(r % 2 == 1 for r in cp)
        blocked = all_odd and (k % 2 == 1) and (m % 2 == 0)

        if not blocked:
            return NO_OBSTRUCTION

        return ObstructionResult(
            blocked=True,
            obstruction_type="H2_parity",
            level=2,
            proof_steps=(
                f"Need r₀+…+r_{{k-1}}={m}, each gcd(rᵢ,{m})=1.",
                f"Coprime-to-{m} = {list(cp)} — all odd (m even implies "
                f"only odd numbers are coprime to m).",
                f"Sum of k={k} odd integers is odd.",
                f"m={m} is even. Odd ≠ even. Contradiction. □",
            ),
            evidence=(
                f"Holds for ALL even m, ALL odd k. Proves no column-uniform r-tuple exists. "
                f"Class γ₂ ∈ H²(Z_2, Z/2) = Z/2 is nontrivial."
            ),
        )

    def h3_fiber_uniform(self) -> ObstructionResult:
        """
        Theorem 10.1 — Fiber-Uniform Impossibility (k=4, m=4).

        Even though H² is absent for (m=4, k=4), no fiber-uniform σ works.
        This is a secondary obstruction living at H³ level.

        Currently proved only for (m=4, k=4) by exhaustive check of
        24^4 = 331,776 cases. General algebraic proof is open.

        Returns obstruction only for the proved case.
        """
        if not (self.m == 4 and self.k == 4):
            return NO_OBSTRUCTION

        # We know the result — it was computed exhaustively
        # Don't re-run 331,776 cases on every check; return the proved result
        return ObstructionResult(
            blocked=True,
            obstruction_type="H3_fiber_uniform",
            level=3,
            proof_steps=(
                "H² obstruction absent: r-quad (1,1,1,1) has sum=4=m, "
                "all gcd(1,4)=1. Arithmetic feasible.",
                "However: fiber-uniform means σ(v) = f(fiber(v)) only.",
                "Exhaustive check: all 24^4 = 331,776 fiber-uniform σ "
                "yield score > 0 (no valid Hamiltonian decomposition).",
                "Secondary obstruction confirmed. □",
            ),
            evidence=(
                "331,776 cases checked. 0 solutions found. "
                "Algebraic proof of this secondary obstruction: OPEN."
            ),
        )

    @staticmethod
    def single_cycle_check(r: int, b_sum: int, m: int) -> ObstructionResult:
        """
        Theorem 5.1 — Single-Cycle Condition (standalone).

        A twisted translation Q with step r and b-sum s over Z_m
        generates a full m²-cycle if and only if:
            gcd(r, m) = 1  AND  gcd(s mod m, m) = 1

        STANDALONE: applies to any step-and-wrap system.

        Parameters
        ----------
        r     : int   Step size (stride)
        b_sum : int   Sum of translation offsets mod m
        m     : int   Modulus (space size)

        Examples
        --------
        # Does circular buffer of size 12 with step 5 cover all slots?
        ObstructionChecker.single_cycle_check(r=5, b_sum=1, m=12)
        # → blocked=False (gcd(5,12)=1, gcd(1,12)=1 → full coverage)

        # Does step 4 cover all 12 slots?
        ObstructionChecker.single_cycle_check(r=4, b_sum=1, m=12)
        # → blocked=True (gcd(4,12)=4 ≠ 1 → stuck in sub-cycle of size 3)
        """
        from math import gcd
        g_r = gcd(r, m)
        g_b = gcd(b_sum % m, m) if m > 0 else 1
        full_cycle = (g_r == 1) and (g_b == 1)

        if full_cycle:
            return NO_OBSTRUCTION

        steps = []
        if g_r != 1:
            steps.append(
                f"gcd(r={r}, m={m}) = {g_r} ≠ 1: step shares factor with "
                f"space size → sub-cycle of size {m // g_r} instead of {m}."
            )
        if g_b != 1:
            steps.append(
                f"gcd(b_sum={b_sum} mod {m}={b_sum % m}, m={m}) = {g_b} ≠ 1: "
                f"translation offset is not coprime → coverage gap."
            )

        return ObstructionResult(
            blocked=True,
            obstruction_type="single_cycle_violation",
            level=1,
            proof_steps=tuple(steps),
            evidence=f"Period = {m // max(g_r, g_b)}, expected {m}.",
        )

    @staticmethod
    def coverage_check(step: int, space_size: int) -> ObstructionResult:
        """
        Simplified single-cycle check for common programming use.

        Is this step size valid for full coverage of a circular space?

        Examples
        --------
        # Hash table: does stride 7 cover all 16 buckets?
        coverage_check(7, 16)  # → blocked (gcd(7,16)=1, actually fine)
        coverage_check(4, 16)  # → blocked (gcd(4,16)=4 → only 4 buckets)

        # Scheduler: does worker step 3 cover 9 task slots?
        coverage_check(3, 9)   # → blocked (gcd(3,9)=3 → only 3 slots)
        coverage_check(2, 9)   # → no obstruction
        """
        return ObstructionChecker.single_cycle_check(
            r=step, b_sum=1, m=space_size
        )
