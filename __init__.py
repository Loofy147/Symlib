"""
symlib — Global Structure in Highly Symmetric Systems
======================================================
A library for finding global structure in combinatorial problems
via the short exact sequence  0 → H → G → G/H → 0.

Public API
----------
from symlib import Problem, classify, construct, explain

p = Problem.from_cycles(m=5, k=3)
result = classify(p)          # O(1) obstruction check
solution = construct(p)       # algebraic construction
proof = explain(p)            # human + machine-readable proof

Theorem utilities (standalone — apply to any symmetric system)
--------------------------------------------------------------
from symlib.theorems import (
    ParityObstruction,        # Thm 6.1 — check before any search
    TorsorSolutionSpace,      # Moduli theorem — solution space geometry
    CoprimeCoverage,          # Thm 5.1 — step/wrap coverage check
    QuotientCounter,          # W4 — count distinct states via phi(m)
    DepthBarrierAnalyzer,     # depth-k local minimum detector
)
"""

from symlib.kernel.weights   import extract_weights, Weights
from symlib.kernel.obstruction import ObstructionChecker
from symlib.kernel.construction import ConstructionEngine
from symlib.kernel.verify    import verify_sigma
from symlib.kernel.torsor    import TorsorStructure
from symlib.domain           import Problem, Domain
from symlib.engine           import DecisionEngine, classify, construct, explain
from symlib.proof.builder    import ProofBuilder
from symlib.proof.lean4      import Lean4Exporter

__version__ = "2.0.0"
__all__ = [
    "Problem", "Domain",
    "classify", "construct", "explain",
    "extract_weights", "Weights",
    "ObstructionChecker", "ConstructionEngine",
    "verify_sigma", "TorsorStructure",
    "ProofBuilder", "Lean4Exporter",
    "DecisionEngine",
]
