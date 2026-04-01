"""
symlib.kernel.ses_analyzer
===========================
Short Exact Sequence analyzer — given a finite group G and a normal
subgroup H, determine the quality of  0 → H → G → G/H → 0  as a
decomposition for the framework's four coordinates.
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
    """
    subgroup:       FrozenSet[int]
    subgroup_order: int
    fiber_size:     int
    k:              int
    weights:        Weights
    quality_score:  tuple  = field(default_factory=tuple)
    explanation:    str    = ""

    def is_trivial(self) -> bool:
        return self.subgroup_order == 1

    def is_whole_group(self) -> bool:
        return self.fiber_size == 1

    def is_useful(self) -> bool:
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
        for i, c in enumerate(self.candidates[:8]):
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
    """

    def __init__(self, group: FiniteGroup, k: int):
        self.group = group
        self.k = k

    def analyze(self) -> SESAnalysis:
        t0 = time.perf_counter()
        G = self.group
        k = self.k

        normal_sgs = G.normal_subgroups()
        candidates: List[SESCandidate] = []

        for H in normal_sgs:
            h_order = len(H)
            m = G.order // h_order
            if m < 2 or h_order < 2: continue

            w = extract_weights(m, k)
            practical = (m * m <= G.order)

            # Breakthrough: deterministic construction available for odd m, k=3
            has_formula = (m % 2 == 1 and k == 3) or (k == 2)

            # Priority: constructible > practical size > algebraic formula > r-tuples > smaller m
            quality = (
                int(not w.h2_blocks),
                int(practical),
                int(has_formula),
                w.r_count,
                -round(w.compression * 10000),
                -m,
            )

            explanation = self._explain_candidate(H, m, w, practical, has_formula)

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
        has_formula: bool = False,
    ) -> str:
        h_order = len(H)
        parts = [f"0 → H(order={h_order}) → G(order={self.group.order}) → G/H(order={m}) → 0"]

        if not practical:
            parts.append(f"[Impractical: m²={m*m} > |G|={self.group.order}]")

        if w.h2_blocks:
            parts.append(f"H² obstruction (m={m} even, k={self.k} odd). Proves impossible in O(1).")
        elif has_formula:
            parts.append(f"ALGEBRAIC BREAKTHROUGH: Deterministic O(m²) formula available.")
        elif w.r_count > 0:
            parts.append(f"Constructible: {w.r_count} valid r-tuples. Canonical seed {w.canonical}.")
        else:
            parts.append(f"Open case: No H² obstruction but no valid r-tuples found.")

        parts.append(f"|H¹| = φ({m}) = {w.h1_exact} gauge classes.")
        return "  ".join(parts)

    def best_for_construction(self) -> Optional[SESCandidate]:
        analysis = self.analyze()
        for c in analysis.candidates:
            if not c.weights.h2_blocks and c.is_useful():
                return c
        return None

    def best_for_impossibility(self) -> Optional[SESCandidate]:
        analysis = self.analyze()
        for c in analysis.candidates:
            if c.weights.h2_blocks and c.is_useful():
                return c
        return None
