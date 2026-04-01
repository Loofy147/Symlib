"""
symlib
======
Finding global structure in combinatorial problems.
"""

__version__ = "2.2.0"

from symlib.engine import DecisionEngine
from symlib.domain import Problem, default_registry
from symlib.autodetect import detect, AutoDetector
from symlib.theorems import (
    ParityObstruction,
    CoprimeCoverage,
    QuotientCounter,
    FunctionCounter,
    SpikeTheorem,
    CanonicalSeed,
)
from symlib.kernel.manifold import UniversalG3Manifold, g3_kernel

__all__ = [
    "DecisionEngine",
    "Problem",
    "detect",
    "AutoDetector",
    "ParityObstruction",
    "CoprimeCoverage",
    "QuotientCounter",
    "FunctionCounter",
    "SpikeTheorem",
    "CanonicalSeed",
    "UniversalG3Manifold",
    "g3_kernel",
    "default_registry",
]

# Deferred initialization to avoid circular dependency and ensure all components are ready
def initialize_manifold():
    reg = default_registry()
    g3_kernel.populate_from_registry(reg)

initialize_manifold()
