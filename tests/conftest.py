"""
Shared test configuration for symlib test suite.
Sets up import path and provides common fixtures.
"""
import sys
import os
import pytest

# Ensure symlib is importable from the repo root
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from symlib.kernel.weights      import extract_weights
from symlib.kernel.construction import ConstructionEngine
from symlib.kernel.verify       import verify_sigma
from symlib.domain              import Problem
from symlib.engine              import DecisionEngine


@pytest.fixture(scope="session")
def engine():
    """Shared DecisionEngine instance — cached across all tests."""
    return DecisionEngine()


@pytest.fixture(scope="session")
def solved_m3():
    """Verified solution for m=3 k=3."""
    sigma = ConstructionEngine(3, 3).construct()
    assert verify_sigma(sigma, 3)
    return sigma


@pytest.fixture(scope="session")
def solved_m4():
    """Verified solution for m=4 k=3 (SA precomputed)."""
    sigma = ConstructionEngine(4, 3).construct()
    assert verify_sigma(sigma, 4)
    return sigma


@pytest.fixture(scope="session")
def solved_m5():
    """Verified solution for m=5 k=3."""
    sigma = ConstructionEngine(5, 3).construct()
    assert verify_sigma(sigma, 5)
    return sigma
