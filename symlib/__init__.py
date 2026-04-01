"""
symlib
======
Finding global structure in combinatorial problems.
"""

__version__ = "2.2.0"

from symlib.engine import DecisionEngine
from symlib.domain import Problem
from symlib.autodetect import detect, AutoDetector
from symlib.theorems import (
    ParityObstruction,
    CoprimeCoverage,
    QuotientCounter,
    FunctionCounter,
    SpikeTheorem,
    CanonicalSeed,
)

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
]
