"""
symlib.autodetect
=================
Auto-detect the best SES decomposition for any finite group.

This is the capability that makes the framework general rather than
specific to Z_m³ Cayley digraphs. Given any finite group G and a
number of colors k, the detector:

  1. Enumerates all normal subgroups of G
  2. For each normal subgroup H, computes the SES 0 → H → G → G/H → 0
  3. Scores each SES by constructibility, r-tuple count, and compression
  4. Returns the best SES with full classification, proof, and explanation

After auto-detect, the result plugs directly into the existing engine —
the Problem object, classification, construction, and proof machinery
all work without modification.

PUBLIC API
----------
from symlib.autodetect import AutoDetector, detect

# From a known group type
result = detect("cyclic", n=7, k=3)
result = detect("product", m=4, n=6, k=3)
result = detect("dihedral", n=5, k=3)
result = detect("symmetric", n=3, k=2)

# From a Cayley table directly
result = detect("table", table=[[...]], k=3)

# From a description dict
result = detect("description", group_order=12, k=3,
                fiber_size_hint=4)   # optional hint

# Access results
print(result.explain())            # full analysis
print(result.best_ses.one_line())  # best SES summary
problem = result.to_problem()      # inject into engine
classified = result.classify()     # run the full engine
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import time

from symlib.kernel.group_algebra import (
    FiniteGroup, cyclic_group, product_group,
    symmetric_group, dihedral_group, triple_product,
)
from symlib.kernel.ses_analyzer import SESAnalyzer, SESAnalysis, SESCandidate
from symlib.kernel.weights import extract_weights
from symlib.domain import Problem


@dataclass
class DetectionResult:
    """
    Complete result of auto-detecting the best SES for a group.

    Attributes
    ----------
    group           : FiniteGroup     The input group G
    k               : int             Number of arc colors
    analysis        : SESAnalysis     Full ranked SES analysis
    best_ses        : SESCandidate    The recommended SES decomposition
    problem         : Problem         Ready-to-use Problem object
    elapsed_ms      : float           Total detection time
    detection_notes : list[str]       Observations and warnings
    """
    group:           FiniteGroup
    k:               int
    analysis:        SESAnalysis
    best_ses:        Optional[SESCandidate]
    problem:         Optional[Problem]
    elapsed_ms:      float
    detection_notes: List[str]

    def explain(self) -> str:
        lines = [
            "═" * 60,
            f"AUTO-DETECT RESULT",
            "─" * 60,
            self.analysis.explain(),
        ]
        if self.detection_notes:
            lines += ["", "Detection notes:"]
            for note in self.detection_notes:
                lines.append(f"  • {note}")
        if self.problem:
            lines += ["", "Generated problem:", f"  {self.problem.summary()}"]
        lines.append("═" * 60)
        return "\n".join(lines)

    def classify(self):
        """Run the full engine on the detected problem."""
        if self.problem is None:
            raise ValueError("No problem generated — no useful SES found.")
        from symlib.engine import DecisionEngine
        engine = DecisionEngine()
        return engine.run(self.problem)

    def to_problem(self) -> Problem:
        if self.problem is None:
            raise ValueError("No problem generated — no useful SES found.")
        return self.problem

    @property
    def is_constructible(self) -> bool:
        return (self.best_ses is not None and
                not self.best_ses.weights.h2_blocks)

    @property
    def is_impossible(self) -> bool:
        return self.analysis.is_provably_impossible()


class AutoDetector:
    """
    Automatically detect the best SES decomposition for a finite group.

    The detector finds the normal subgroup H that gives the most useful
    SES — the one with best construction prospects, lowest search space
    compression ratio, and most r-tuples.

    Usage
    -----
    detector = AutoDetector()

    # Standard cases
    result = detector.from_cyclic(n=7, k=3)
    result = detector.from_product(m=6, n=9, k=3)
    result = detector.from_dihedral(n=5, k=2)
    result = detector.from_symmetric(n=3, k=2)
    result = detector.from_triple_product(m=5, k=3)

    # From Cayley table
    table = [[0,1,2],[1,2,0],[2,0,1]]  # Z_3
    result = detector.from_table(table, k=3, name="Z_3 direct")

    # Access the result
    print(result.explain())
    problem = result.to_problem()
    classification = result.classify()
    """

    def detect(
        self,
        group:   FiniteGroup,
        k:       int,
        hint_m:  Optional[int] = None,
    ) -> DetectionResult:
        """
        Core detection method — works for any FiniteGroup.

        Parameters
        ----------
        group   : FiniteGroup   The group to analyze
        k       : int           Number of arc colors
        hint_m  : int, optional  If provided, only consider SES with this fiber size

        Returns
        -------
        DetectionResult with ranked SES candidates and best choice
        """
        t0 = time.perf_counter()
        notes: List[str] = []

        # Fast path: triple products Z_m^3 — known structure, no enumeration needed
        m_cube = self._is_triple_product(group)
        if m_cube is not None:
            notes.append(f"Fast path: detected Z_{m_cube}³ structure — "
                         f"using known SES 0 → Z_{m_cube}² → Z_{m_cube}³ → Z_{m_cube} → 0.")
            return self._detect_triple_product(group, m_cube, k, t0, notes)

        # Standard path: enumerate all normal subgroups
        analyzer = SESAnalyzer(group, k)
        analysis = analyzer.analyze()

        candidates = analysis.candidates

        # Prime-order fallback: if no useful SES found and group has prime order,
        # report that this group has no internal structure to exploit —
        # it should be used as the fiber quotient of a larger group.
        if not candidates and self._is_prime(group.order):
            notes.append(
                f"Group has prime order {group.order} — no non-trivial proper normal "
                f"subgroups exist. This group cannot be decomposed via a non-trivial SES. "
                f"If you want to analyze a problem with fiber Z_{group.order}, inject "
                f"a larger group G with a normal subgroup H where |G/H| = {group.order}."
            )

        # Apply hint filter if provided
        if hint_m is not None:
            filtered = [c for c in candidates if c.fiber_size == hint_m]
            if filtered:
                candidates = filtered
                notes.append(f"Hint m={hint_m} applied: filtered to {len(filtered)} candidates.")
            else:
                notes.append(f"Hint m={hint_m} not found — ignoring hint.")

        # Select best
        best = candidates[0] if candidates else None

        # Observations
        n_useful = sum(1 for c in analysis.candidates if c.is_useful())
        n_blocked = sum(1 for c in analysis.candidates if c.is_useful() and c.weights.h2_blocks)
        n_constructible = n_useful - n_blocked

        if n_useful == 0:
            notes.append("No useful SES found.")
        elif n_constructible == 0:
            notes.append(f"All {n_blocked} useful SES decompositions are H²-blocked. "
                         f"Problem is provably impossible.")
        elif n_blocked > 0:
            notes.append(f"{n_constructible} constructible and {n_blocked} blocked SES found.")

        if best and not best.weights.h2_blocks and best.weights.r_count > 1:
            notes.append(f"{best.weights.r_count} r-tuples available — "
                         f"multiple construction paths.")

        if best and best.weights.compression < 0.01:
            notes.append(f"W6={best.weights.compression:.4f} — exceptional compression, "
                         f"algebraic construction likely.")

        if group.is_abelian():
            notes.append("Group is abelian — all subgroups are normal, "
                         "full SES enumeration complete.")
        else:
            notes.append("Group is non-abelian — normal subgroup detection "
                         "uses conjugacy check.")

        # Build Problem
        problem: Optional[Problem] = None
        if best is not None:
            fiber_desc = self._infer_fiber_desc(group, best)
            problem = Problem.inject({
                "name": f"{group.name} k={k}",
                "group_order": group.order,
                "fiber_size": best.fiber_size,
                "k": k,
                "fiber_map_desc": fiber_desc,
                "tags": self._infer_tags(group, best),
                "notes": (f"Auto-detected. Best SES: "
                          f"|H|={best.subgroup_order}, m={best.fiber_size}."),
            })

        elapsed = (time.perf_counter() - t0) * 1000

        return DetectionResult(
            group=group,
            k=k,
            analysis=analysis,
            best_ses=best,
            problem=problem,
            elapsed_ms=round(elapsed, 2),
            detection_notes=notes,
        )

    def _is_prime(self, n: int) -> bool:
        """Check if n is prime."""
        if n < 2: return False
        if n == 2: return True
        if n % 2 == 0: return False
        for i in range(3, int(n**0.5) + 1, 2):
            if n % i == 0: return False
        return True

    def _is_triple_product(self, group: FiniteGroup) -> Optional[int]:
        """
        Detect if group is Z_m³ by checking order = m³ and abelian structure.
        Returns m if detected, None otherwise.
        Only checks small cubes (m=2..9) for performance.
        """
        for m in range(2, 10):
            if group.order == m ** 3:
                # Verify abelian and all elements have order dividing m
                if not group.is_abelian():
                    return None
                # Spot-check: every element should have order dividing m
                # (in Z_m³ every element satisfies g^m = e)
                sample = range(min(group.order, 20))
                if all(group.element_order(g) <= m or m % group.element_order(g) == 0
                       for g in sample if g != group.identity):
                    return m
        return None

    def _detect_triple_product(
        self,
        group: FiniteGroup,
        m: int,
        k: int,
        t0: float,
        notes: List[str],
    ) -> DetectionResult:
        """
        Fast path for Z_m³: directly construct the known-optimal SES
        0 → Z_m² → Z_m³ → Z_m → 0 without subgroup enumeration.
        """
        from symlib.kernel.weights import extract_weights
        from symlib.kernel.ses_analyzer import SESCandidate
        from symlib.kernel.ses_analyzer import SESAnalysis
        import math

        w = extract_weights(m, k)
        h_order = m * m
        practical = True  # m² = |H| ≤ |G| always for triple products

        quality = (
            int(not w.h2_blocks),
            int(practical),
            w.r_count,
            -round(w.compression * 10000),
            -m,
        )

        explanation = (
            f"0 → Z_{m}²(order={h_order}) → Z_{m}³(order={m**3}) → Z_{m}(order={m}) → 0  "
            f"[Known optimal SES for Z_{m}³ — fiber map φ(i,j,k)=(i+j+k) mod {m}]"
        )
        if w.h2_blocks:
            explanation += f"  H² obstruction: parity blocks k={k}, m={m}."
        else:
            explanation += f"  Constructible: {w.r_count} r-tuples, W6={w.compression:.4f}."

        best = SESCandidate(
            subgroup=frozenset(range(h_order)),  # placeholder
            subgroup_order=h_order,
            fiber_size=m,
            k=k,
            weights=w,
            quality_score=quality,
            explanation=explanation,
        )

        # Build a minimal SESAnalysis wrapping the single known-best candidate
        analysis = SESAnalysis(
            group=group,
            k=k,
            candidates=[best],
            best=best,
            elapsed_ms=0.0,
            n_normal_sgs=1,  # we only computed the known one
        )

        problem = Problem.inject({
            "name": f"Z_{m}³ k={k}",
            "group_order": m ** 3,
            "fiber_size": m,
            "k": k,
            "fiber_map_desc": f"(i+j+k) mod {m}",
            "tags": ["cycles", "odd" if m % 2 == 1 else "even",
                     "fast_detected"],
            "notes": f"Fast-detected Z_{m}³. Known SES used directly.",
        })

        elapsed = (time.perf_counter() - t0) * 1000
        if not w.h2_blocks:
            notes.append(f"Constructible: {w.r_count} r-tuples for m={m} k={k}.")
        else:
            notes.append(f"H² blocked: m={m} even, k={k} odd — proves impossible.")

        return DetectionResult(
            group=group,
            k=k,
            analysis=analysis,
            best_ses=best,
            problem=problem,
            elapsed_ms=round(elapsed, 2),
            detection_notes=notes,
        )
        """Infer a human-readable fiber map description."""
        m = ses.fiber_size
        if group.is_abelian():
            return f"quotient map G → G/H (order {m})"
        else:
            return f"sign/quotient map {group.name} → G/H (order {m})"

    def _infer_fiber_desc(self, group: FiniteGroup, ses: SESCandidate) -> str:
        """Infer a human-readable fiber map description."""
        m = ses.fiber_size
        if group.is_abelian():
            return f"quotient map G → G/H (order {m})"
        else:
            return f"sign/quotient map {group.name} → G/H (order {m})"

    def _infer_tags(self, group: FiniteGroup, ses: SESCandidate) -> List[str]:
        """Infer searchable tags from group structure."""
        tags = ["autodetected"]
        if group.is_abelian():
            tags.append("abelian")
        else:
            tags.append("nonabelian")
        if ses.fiber_size % 2 == 0:
            tags.append("even_fiber")
        else:
            tags.append("odd_fiber")
        if ses.weights.h2_blocks:
            tags.append("impossible")
        else:
            tags.append("constructible")
        return tags

    # ── Factory methods ──────────────────────────────────────────────────────

    def from_cyclic(self, n: int, k: int) -> DetectionResult:
        """
        Auto-detect SES for cyclic group Z_n.

        For prime n: Z_n has no non-trivial proper normal subgroups,
        so no internal SES decomposition exists. In this case the detector
        returns a result explaining that Z_n should be used as the FIBER
        (quotient) of a larger group, not as G itself.
        For composite n: enumerate all subgroups (all are normal).
        """
        g = cyclic_group(n)
        result = self.detect(g, k)

        # Prime fallback: if no candidates found, build a synthetic problem
        # treating Z_n itself as the fiber quotient
        if (result.best_ses is None and self._is_prime(n)):
            from symlib.kernel.weights import extract_weights
            w = extract_weights(n, k)
            problem = Problem.inject({
                "name": f"Z_{n} as fiber k={k}",
                "group_order": n ** 3,   # natural embedding in Z_n³
                "fiber_size": n,
                "k": k,
                "fiber_map_desc": f"sum mod {n} (canonical for Z_{n}³)",
                "tags": ["cyclic_prime", "fiber_direct"],
                "notes": (
                    f"Z_{n} is prime — no internal SES decomposition. "
                    f"Treating Z_{n} as fiber of Z_{n}³ directly. "
                    f"This is the standard G_m construction with m={n}."
                ),
            })
            result.problem = problem
            result.detection_notes.append(
                f"Z_{n} has prime order — no internal SES. "
                f"Generated Z_{n}³ problem with fiber m={n} directly."
            )
        return result

    def from_product(self, m: int, n: int, k: int) -> DetectionResult:
        """Auto-detect SES for Z_m × Z_n."""
        return self.detect(product_group(m, n), k)

    def from_dihedral(self, n: int, k: int) -> DetectionResult:
        """Auto-detect SES for dihedral group D_n (order 2n)."""
        return self.detect(dihedral_group(n), k)

    def from_symmetric(self, n: int, k: int) -> DetectionResult:
        """Auto-detect SES for symmetric group S_n."""
        return self.detect(symmetric_group(n), k)

    def from_triple_product(self, m: int, k: int) -> DetectionResult:
        """Auto-detect SES for Z_m³ (the Cayley digraph group)."""
        return self.detect(triple_product(m), k)

    def from_table(
        self,
        table: List[List[int]],
        k:     int,
        name:  str = "custom",
    ) -> DetectionResult:
        """
        Auto-detect SES from a raw Cayley table.

        Parameters
        ----------
        table : list[list[int]]   Multiplication table. table[a][b] = a*b.
        k     : int               Number of arc colors.
        name  : str               Optional group name.
        """
        n = len(table)
        # Find identity
        identity = next(
            (i for i in range(n) if all(table[i][j] == j for j in range(n))),
            0
        )
        group = FiniteGroup(
            order=n,
            table=table,
            labels=[str(i) for i in range(n)],
            name=name,
            identity=identity,
        )
        return self.detect(group, k)

    def from_description(
        self,
        group_order: int,
        k:           int,
        group_type:  str = "cyclic",
        **kwargs,
    ) -> DetectionResult:
        """
        Auto-detect from a high-level description.

        Parameters
        ----------
        group_order : int    |G|
        k           : int    Number of arc colors
        group_type  : str    "cyclic", "product", "dihedral", "symmetric"
        **kwargs           Additional parameters for specific group types

        Examples
        --------
        from_description(12, k=3, group_type="product", m=4, n=3)
        from_description(10, k=3, group_type="dihedral", n=5)
        from_description(6,  k=2, group_type="symmetric", n=3)
        """
        if group_type == "cyclic":
            return self.from_cyclic(group_order, k)
        elif group_type == "product":
            m = kwargs.get("m", 2)
            n = kwargs.get("n", group_order // m)
            return self.from_product(m, n, k)
        elif group_type == "dihedral":
            n = kwargs.get("n", group_order // 2)
            return self.from_dihedral(n, k)
        elif group_type == "symmetric":
            n = kwargs.get("n", 3)
            return self.from_symmetric(n, k)
        else:
            raise ValueError(f"Unknown group_type: {group_type}")

    def compare_all_k(
        self,
        group: FiniteGroup,
        k_range: range = range(2, 6),
    ) -> Dict[int, DetectionResult]:
        """
        Run auto-detect for multiple k values on the same group.
        Returns dict k → DetectionResult.
        Useful for finding which k is most favorable for a given group.
        """
        return {k: self.detect(group, k) for k in k_range}

    def scan_cyclic_range(
        self,
        n_range: range,
        k: int,
    ) -> List[DetectionResult]:
        """
        Run auto-detect on Z_n for n in n_range.
        Returns results sorted by quality (best first).
        """
        results = [self.from_cyclic(n, k) for n in n_range]
        results.sort(
            key=lambda r: r.best_ses.quality_score if r.best_ses else (0,),
            reverse=True,
        )
        return results


# Module-level convenience function
_default_detector = AutoDetector()


def detect(group_type: str, k: int, **kwargs) -> DetectionResult:
    """
    Convenience function for auto-detection.

    Parameters
    ----------
    group_type : str   "cyclic", "product", "dihedral", "symmetric",
                       "triple_product", "table", "description"
    k          : int   Number of arc colors
    **kwargs          Group-specific parameters

    Examples
    --------
    detect("cyclic", n=7, k=3)
    detect("product", m=4, n=6, k=3)
    detect("dihedral", n=5, k=3)
    detect("symmetric", n=3, k=2)
    detect("triple_product", m=5, k=3)
    detect("table", table=[[0,1,2],[1,2,0],[2,0,1]], k=3)
    """
    d = _default_detector
    if group_type == "cyclic":
        return d.from_cyclic(kwargs["n"], k)
    elif group_type == "product":
        return d.from_product(kwargs["m"], kwargs["n"], k)
    elif group_type == "dihedral":
        return d.from_dihedral(kwargs["n"], k)
    elif group_type == "symmetric":
        return d.from_symmetric(kwargs["n"], k)
    elif group_type == "triple_product":
        return d.from_triple_product(kwargs["m"], k)
    elif group_type == "table":
        return d.from_table(kwargs["table"], k, kwargs.get("name", "custom"))
    elif group_type == "description":
        return d.from_description(
            kwargs["group_order"], k,
            kwargs.get("group_type_inner", "cyclic"),
            **{kk: v for kk, v in kwargs.items()
               if kk not in ("group_order", "group_type_inner")}
        )
    else:
        raise ValueError(f"Unknown group_type: {group_type}")
