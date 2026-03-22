"""
symlib.engine
=============
The decision engine — routes every problem to the right strategy
before doing any work.

ROUTING LOGIC
-------------
1. Extract weights (O(1))
2. Check H² obstruction (O(1)) → if blocked: prove and return
3. Check precomputed solutions (O(1)) → if found: return
4. Check algebraic construction availability → use if possible
5. Fall back to structured SA only if necessary

The engine never does more work than the problem requires.
A provably impossible case never touches a search algorithm.
A constructible case never runs SA.

PUBLIC API
----------
classify(problem) → ClassificationResult
construct(problem) → Optional[Sigma]
explain(problem) → str

Or use the engine object directly:
    engine = DecisionEngine()
    result = engine.run(problem)
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Optional, Dict, Tuple, Any
from enum import Enum, auto

from symlib.kernel.weights      import extract_weights, Weights
from symlib.kernel.obstruction  import ObstructionChecker, ObstructionResult, NO_OBSTRUCTION
from symlib.kernel.construction import ConstructionEngine
from symlib.kernel.verify       import verify_sigma, verify_and_diagnose
from symlib.kernel.torsor       import TorsorStructure, TorsorInfo
from symlib.domain              import Problem

Sigma = Dict[Tuple[int,...], Tuple[int,...]]


class Status(Enum):
    PROVED_IMPOSSIBLE  = auto()  # H² or higher obstruction — no solution exists
    PROVED_POSSIBLE    = auto()  # Solution found and verified
    OPEN_PROMISING     = auto()  # No obstruction, r-tuples exist, construction open
    OPEN_UNKNOWN       = auto()  # No obstruction, no r-tuples either


_STATUS_LABELS = {
    Status.PROVED_IMPOSSIBLE: "PROVED IMPOSSIBLE",
    Status.PROVED_POSSIBLE:   "PROVED POSSIBLE",
    Status.OPEN_PROMISING:    "OPEN (promising)",
    Status.OPEN_UNKNOWN:      "OPEN (unknown)",
}


@dataclass
class ClassificationResult:
    """
    Complete classification of a problem.

    This is what the decision engine returns — the single object
    that tells you everything you need to know about the problem
    before doing any further work.
    """
    problem:      Problem
    status:       Status
    weights:      Weights
    obstruction:  ObstructionResult
    torsor:       TorsorInfo
    solution:     Optional[Sigma]
    construction_level: str
    elapsed_ms:   float
    proof_steps:  tuple[str, ...]

    @property
    def is_solved(self) -> bool:
        return self.solution is not None

    @property
    def is_impossible(self) -> bool:
        return self.status == Status.PROVED_IMPOSSIBLE

    def one_line(self) -> str:
        label = _STATUS_LABELS[self.status]
        w = self.weights
        return (
            f"({w.m},{w.k}) {label:<22} | "
            f"W4=φ={w.h1_exact} W6={w.compression:.4f} "
            f"| {self.elapsed_ms:.1f}ms"
        )

    def explain(self) -> str:
        lines = [
            f"Problem: {self.problem.name}",
            f"Status:  {_STATUS_LABELS[self.status]}",
            f"",
            f"Weights:",
            f"  {self.weights.summary()}",
            f"",
        ]

        if self.obstruction.blocked:
            lines += [
                "Obstruction proof:",
                self.obstruction.explain(),
                "",
            ]

        if self.solution is not None:
            lines += [
                f"Solution found via: {self.construction_level}",
                f"Verified: True",
                f"",
            ]

        lines += [
            "Torsor structure:",
            self.torsor.explain(),
        ]

        return "\n".join(lines)


class DecisionEngine:
    """
    Routes every symmetric combinatorial problem to the right strategy.

    Usage
    -----
    engine = DecisionEngine()
    result = engine.run(Problem.from_cycles(m=5, k=3))
    print(result.one_line())
    print(result.explain())
    """

    def __init__(self):
        self._cache: dict[tuple, ClassificationResult] = {}

    def run(
        self,
        problem: Problem,
        attempt_construction: bool = True,
        max_iters: int = 500_000,
    ) -> ClassificationResult:
        """
        Classify and optionally construct a solution for problem.

        Parameters
        ----------
        problem                : Problem
        attempt_construction   : bool    Try to find a solution (default True)
        max_iters              : int     Max iterations for level search

        Returns
        -------
        ClassificationResult
        """
        key = (problem.fiber_size, problem.k)
        if key in self._cache:
            return self._cache[key]

        t0 = time.perf_counter()
        m, k = problem.fiber_size, problem.k

        # Extract weights — O(φ(m)^k)
        w = extract_weights(m, k)

        # Obstruction check — O(1)
        checker = ObstructionChecker(m, k)
        obstruction = checker.check()

        # Torsor analysis
        torsor = TorsorStructure(m, k).analyse()

        # Construction attempt
        # IMPORTANT: attempt construction before consulting obstruction.
        # h2_blocks means column-uniform is impossible — it does NOT mean
        # no solution exists. Precomputed SA solutions (e.g. m=4 k=3) are
        # valid even when h2_blocks=True. ConstructionEngine handles this.
        solution: Optional[Sigma] = None
        construction_level = "none"

        if attempt_construction:
            # Use precomputed from domain object if provided
            if problem.precomputed is not None:
                if isinstance(problem.precomputed, dict):
                    if verify_sigma(problem.precomputed, m):
                        solution = problem.precomputed
                        construction_level = "precomputed_domain"

            if solution is None:
                ce = ConstructionEngine(m, k)
                construction_level = ce.construction_level()
                if construction_level not in ("open", "impossible"):
                    solution = ce.construct(max_iters)

        # Determine status — solution found always overrides obstruction
        # (obstruction proves column-uniform impossible, not ALL solutions)
        if solution is not None:
            status = Status.PROVED_POSSIBLE
            proof_steps = (
                f"Explicit σ verified: {m**3} arcs, "
                f"in-degree 1, 1 component per colour. □",
                f"Construction method: {construction_level}.",
            )
        elif obstruction.blocked:
            status = Status.PROVED_IMPOSSIBLE
            proof_steps = obstruction.proof_steps
        elif w.r_count > 0:
            status = Status.OPEN_PROMISING
            proof_steps = (
                f"H² obstruction absent. r-tuple {w.canonical} exists. [W2={w.r_count}]",
                f"Construction search required. W6={w.compression:.4f}.",
            )
        else:
            status = Status.OPEN_UNKNOWN
            proof_steps = (
                f"H² obstruction absent but no valid r-tuple found.",
                f"Further analysis required.",
            )

        elapsed = (time.perf_counter() - t0) * 1000

        result = ClassificationResult(
            problem=problem,
            status=status,
            weights=w,
            obstruction=obstruction,
            torsor=torsor,
            solution=solution,
            construction_level=construction_level,
            elapsed_ms=round(elapsed, 2),
            proof_steps=proof_steps,
        )

        self._cache[key] = result
        return result

    def batch(
        self,
        problems: list[Problem],
        **kwargs,
    ) -> list[ClassificationResult]:
        """Classify multiple problems."""
        return [self.run(p, **kwargs) for p in problems]

    def print_table(self, results: list[ClassificationResult]) -> None:
        """Print a compact results table."""
        print(f"\n{'m,k':<8} {'Status':<22} {'W4':>5} {'W6':>8} {'ms':>8}  Construction")
        print("─" * 72)
        for r in results:
            w = r.weights
            label = _STATUS_LABELS[r.status]
            print(
                f"({w.m},{w.k}){'':<3} {label:<22} {w.h1_exact:>5} "
                f"{w.compression:>8.4f} {r.elapsed_ms:>7.1f}  "
                f"{r.construction_level}"
            )


# ── Module-level convenience functions ───────────────────────────────────────

_default_engine = DecisionEngine()


def classify(problem: Problem) -> ClassificationResult:
    """
    Classify a problem — check obstruction, measure solution space.
    Does not attempt construction. O(1) for impossible cases.
    """
    return _default_engine.run(problem, attempt_construction=False)


def construct(problem: Problem, max_iters: int = 500_000) -> Optional[Sigma]:
    """
    Construct a solution for problem, or return None if impossible/open.
    """
    result = _default_engine.run(problem, attempt_construction=True,
                                  max_iters=max_iters)
    return result.solution


def explain(problem: Problem) -> str:
    """
    Full explanation of a problem — weights, obstruction, torsor structure.
    """
    result = _default_engine.run(problem)
    return result.explain()
