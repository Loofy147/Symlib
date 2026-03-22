"""
symlib.kernel.ses_analyzer
===========================
Short Exact Sequence analyzer — given a finite group G and a normal
subgroup H, determine the quality of  0 → H → G → G/H → 0  as a
decomposition for the framework's four coordinates.

SES QUALITY CRITERIA
--------------------
For a candidate SES with fiber size m = |G/H| and k arc colors:

1. Obstruction class (W1)
   Does the parity obstruction block this SES?
   If yes: this SES proves impossibility in O(1). Value: high for impossibility, zero for construction.

2. r-tuple count (W2)
   How many valid construction seeds exist?
   More seeds = more construction options = better SES.

3. Compression ratio (W6)
   How much does the structure reduce the search space?
   Lower W6 = better. Range [0,1]. W6=0 means purely algebraic construction.

4. Fiber size m
   Smaller m = simpler fiber = more structure exploited.
   But m=1 is trivial (no structure). Sweet spot: m=3..7.

SCORING FORMULA
---------------
score(SES) = (not h2_blocks, r_count, -W6, -m)
             sorted lexicographically, higher is better

This means:
  - Constructible SES always beats impossible SES
  - Among constructible: more r-tuples is better
  - Among equal r-tuples: lower compression is better
  - Among equal compression: smaller fiber is better

AUTO-DETECT ALGORITHM
---------------------
1. Enumerate all normal subgroups H of G
2. For each H: compute fiber size m = |G/H|
3. For each m and k: extract weights
4. Score each candidate
5. Return ranked list with explanation
"""

from __future__ import annotations
from math import gcd
from dataclasses import dataclass, field
from typing import List, Optional, FrozenSet, Tuple
import time

from symlib.kernel.group_algebra import FiniteGroup
from symlib.kernel.weights import extract_weights, Weights


@dataclass
class SESCandidate:
    """
    A candidate Short Exact Sequence  0 → H → G → G/H → 0.

    Attributes
    ----------
    subgroup        : FrozenSet[int]  Elements of H
    subgroup_order  : int             |H|
    fiber_size      : int             |G/H| = m
    k               : int             Number of arc colors
    weights         : Weights         All 8 weights for (m, k)
    quality_score   : tuple           Lexicographic quality (higher=better)
    explanation     : str             Human-readable rationale
    """
    subgroup:       FrozenSet[int]
    subgroup_order: int
    fiber_size:     int
    k:              int
    weights:        Weights
    quality_score:  tuple  = field(default_factory=tuple)
    explanation:    str    = ""

    def is_trivial(self) -> bool:
        """True if H = {e} (trivial subgroup, no structure exploited)."""
        return self.subgroup_order == 1

    def is_whole_group(self) -> bool:
        """True if H = G (quotient is trivial, degenerate SES)."""
        return self.fiber_size == 1

    def is_useful(self) -> bool:
        """True if this SES is neither trivial nor degenerate."""
        return not self.is_trivial() and not self.is_whole_group()

    def one_line(self) -> str:
        w = self.weights
        status = "BLOCKED" if w.h2_blocks else f"r={w.r_count}"
        return (
            f"|H|={self.subgroup_order:>4}  m={self.fiber_size:>3}  "
            f"{status:<12}  W6={w.compression:.4f}  "
            f"W4=φ={w.h1_exact}  → {w.strategy}"
        )


@dataclass
class SESAnalysis:
    """
    Complete SES analysis for a group G with k arc colors.

    Contains all candidate SES decompositions ranked by quality,
    with the best one identified and explained.
    """
    group:        FiniteGroup
    k:            int
    candidates:   List[SESCandidate]
    best:         Optional[SESCandidate]
    elapsed_ms:   float
    n_normal_sgs: int

    def has_constructible(self) -> bool:
        return self.best is not None and not self.best.weights.h2_blocks

    def is_provably_impossible(self) -> bool:
        """True if ALL non-trivial SES decompositions are blocked."""
        useful = [c for c in self.candidates if c.is_useful()]
        return bool(useful) and all(c.weights.h2_blocks for c in useful)

    def explain(self) -> str:
        lines = [
            f"Group: {self.group.summary()}",
            f"k = {self.k} arc colors",
            f"Normal subgroups found: {self.n_normal_sgs}",
            f"Useful SES candidates: {sum(1 for c in self.candidates if c.is_useful())}",
            f"Analysis time: {self.elapsed_ms:.1f}ms",
            "",
            "Candidates (ranked best→worst):",
        ]
        for i, c in enumerate(self.candidates[:8]):  # top 8
            marker = " ← BEST" if i == 0 and c == self.best else ""
            lines.append(f"  [{i+1}] {c.one_line()}{marker}")
        if self.best:
            lines += ["", f"Best SES explanation: {self.best.explanation}"]
        else:
            lines += ["", "No useful SES found."]
        return "\n".join(lines)


class SESAnalyzer:
    """
    Analyze all SES decompositions of a group and rank them.

    Usage
    -----
    analyzer = SESAnalyzer(group, k=3)
    analysis = analyzer.analyze()
    print(analysis.explain())
    best = analysis.best

    # The best candidate gives you the fiber_size for Problem.inject()
    problem = Problem.inject({
        "group_order": group.order,
        "fiber_size":  best.fiber_size,
        "k":           k,
        "fiber_map_desc": f"quotient by H of order {best.subgroup_order}",
    })
    """

    def __init__(self, group: FiniteGroup, k: int):
        self.group = group
        self.k = k

    def analyze(self) -> SESAnalysis:
        """
        Enumerate all normal subgroups, score each as SES, return ranked analysis.
        """
        t0 = time.perf_counter()
        G = self.group
        k = self.k

        normal_sgs = G.normal_subgroups()
        candidates: List[SESCandidate] = []

        for H in normal_sgs:
            h_order = len(H)
            m = G.order // h_order

            # Skip trivial cases
            if m < 2 or h_order < 2:
                continue

            # Extract weights for this (m, k)
            w = extract_weights(m, k)

            # Practicality check: m² ≤ |G| means H is "large" enough
            # to provide meaningful structure. If m² > |G|, the fiber
            # is larger than the square root of the group — the SES is
            # theoretically valid but the construction machinery
            # (which was designed for |G| = m^k-type groups) is impractical.
            practical = (m * m <= G.order)

            # Compute quality score — lexicographic, higher is better
            # Priority: constructible > practical size > more r-tuples > smaller m
            quality = (
                int(not w.h2_blocks),   # constructible > blocked
                int(practical),          # m² ≤ |G| preferred
                w.r_count,              # more r-tuples = more construction options
                -round(w.compression * 10000),  # lower W6 = better
                -m,                     # smaller fiber = more tractable
            )

            # Build explanation
            explanation = self._explain_candidate(H, m, w, practical)

            c = SESCandidate(
                subgroup=H,
                subgroup_order=h_order,
                fiber_size=m,
                k=k,
                weights=w,
                quality_score=quality,
                explanation=explanation,
            )
            candidates.append(c)

        # Sort best first
        candidates.sort(key=lambda c: c.quality_score, reverse=True)

        best = candidates[0] if candidates else None
        elapsed = (time.perf_counter() - t0) * 1000

        return SESAnalysis(
            group=G,
            k=k,
            candidates=candidates,
            best=best,
            elapsed_ms=round(elapsed, 2),
            n_normal_sgs=len(normal_sgs),
        )

    def _explain_candidate(
        self,
        H: FrozenSet[int],
        m: int,
        w: Weights,
        practical: bool = True,
    ) -> str:
        """Generate a human-readable explanation for a candidate SES."""
        h_order = len(H)
        parts = [
            f"0 → H(order={h_order}) → G(order={self.group.order}) → G/H(order={m}) → 0"
        ]

        if not practical:
            parts.append(
                f"[Impractical: m²={m*m} > |G|={self.group.order} — "
                f"fiber larger than √|G|, construction machinery not calibrated.]"
            )

        if w.h2_blocks:
            parts.append(
                f"H² obstruction: all coprime-to-{m} = {list(w.coprime_elems)} "
                f"are odd, k={self.k} is odd, m={m} is even. "
                f"Proves impossible in O(1)."
            )
        elif w.r_count > 0:
            parts.append(
                f"Constructible: {w.r_count} valid r-tuples. "
                f"Canonical seed {w.canonical}. "
                f"W6={w.compression:.4f} (search space compressed to "
                f"{w.compression*100:.1f}% of naive)."
            )
        else:
            parts.append(
                f"No H² obstruction but no valid r-tuples. Open case. "
                f"W6={w.compression:.4f}."
            )

        parts.append(f"|H¹| = φ({m}) = {w.h1_exact} gauge classes.")
        return "  ".join(parts)

    def best_for_construction(self) -> Optional[SESCandidate]:
        """Return best constructible SES, or None if all are blocked."""
        analysis = self.analyze()
        for c in analysis.candidates:
            if not c.weights.h2_blocks and c.is_useful():
                return c
        return None

    def best_for_impossibility(self) -> Optional[SESCandidate]:
        """Return first blocking SES (proves impossibility), or None."""
        analysis = self.analyze()
        for c in analysis.candidates:
            if c.weights.h2_blocks and c.is_useful():
                return c
        return None
