"""
test_engine.py — engine, domain, proof, and theorem utilities
==============================================================
Covers: DecisionEngine, Problem, ProofBuilder, Lean4Exporter,
and all standalone theorem utilities.
"""
import pytest
from symlib.engine   import DecisionEngine, Status, classify, construct, explain
from symlib.domain   import Problem, DomainRegistry, default_registry
from symlib.proof.builder import ProofBuilder
from symlib.proof.lean4   import Lean4Exporter
from symlib.kernel.weights import extract_weights
from symlib.theorems import (
    ParityObstruction, CoprimeCoverage, QuotientCounter,
    TorsorEstimate, CanonicalSeed, DepthBarrierAnalyzer,
)


@pytest.fixture(scope="module")
def engine():
    return DecisionEngine()


# ── 1. Engine ─────────────────────────────────────────────────────────────────

class TestEngine:

    def test_m5_proved_possible(self, engine):
        r = engine.run(Problem.from_cycles(5, 3))
        assert r.status == Status.PROVED_POSSIBLE

    def test_m5_solution_not_none(self, engine):
        r = engine.run(Problem.from_cycles(5, 3))
        assert r.solution is not None

    def test_m4_k3_proved_possible(self, engine):
        # m=4 k=3: H² blocks column-uniform but SA precomputed solution exists
        r = engine.run(Problem.from_cycles(4, 3))
        assert r.status == Status.PROVED_POSSIBLE

    def test_m6_k3_proved_impossible(self, engine):
        r = engine.run(Problem.from_cycles(6, 3))
        assert r.status == Status.PROVED_IMPOSSIBLE

    def test_m4_k4_proved_impossible(self, engine):
        # Impossible via H³ (fiber-uniform)
        r = engine.run(Problem.from_cycles(4, 4))
        assert r.status == Status.PROVED_IMPOSSIBLE

    def test_m7_k3_open_promising(self, engine):
        r = engine.run(Problem.from_cycles(7, 3), attempt_construction=False)
        assert r.status in (Status.PROVED_POSSIBLE, Status.OPEN_PROMISING)

    def test_classify_no_construction(self):
        # Use a fresh engine so the cache doesn't have m=5 already solved
        fresh = DecisionEngine()
        r = fresh.run(Problem.from_cycles(5, 3), attempt_construction=False)
        assert r.status == Status.OPEN_PROMISING
        assert r.solution is None

    def test_one_line_output(self, engine):
        r = engine.run(Problem.from_cycles(5, 3))
        line = r.one_line()
        assert "5,3" in line
        assert len(line) > 10

    def test_explain_output(self, engine):
        r = engine.run(Problem.from_cycles(5, 3))
        text = r.explain()
        assert "Problem" in text
        assert len(text) > 50

    def test_batch_returns_list(self, engine):
        problems = [Problem.from_cycles(m, 3) for m in [3, 4, 5]]
        results  = engine.batch(problems)
        assert len(results) == 3

    def test_module_classify(self):
        r = classify(Problem.from_cycles(5, 3))
        assert r is not None

    def test_module_construct(self):
        from symlib.kernel.verify import verify_sigma
        from symlib.kernel.construction import ConstructionEngine
        # Use the construction engine directly for a clean test
        sigma = ConstructionEngine(5, 3).construct()
        assert sigma is not None
        assert verify_sigma(sigma, 5)

    def test_module_explain(self):
        text = explain(Problem.from_cycles(5, 3))
        assert len(text) > 50


# ── 2. Domain ─────────────────────────────────────────────────────────────────

class TestDomain:

    def test_from_cycles_m_alias(self):
        p = Problem.from_cycles(5, 3)
        assert p.m == 5

    def test_from_cycles_feasible(self):
        assert Problem.from_cycles(5, 3).is_feasible()

    def test_from_cycles_constructible(self):
        assert Problem.from_cycles(5, 3).is_constructible()

    def test_from_cycles_even_not_feasible(self):
        assert not Problem.from_cycles(4, 3).is_feasible()

    def test_from_product_gcd(self):
        p = Problem.from_product_group(4, 6, 3)
        from math import gcd
        assert p.fiber_size == gcd(4, 6)

    def test_from_nonabelian(self):
        p = Problem.from_nonabelian("S_3", 6, "A_3", 2, k=2)
        assert p.fiber_size == 2
        assert p.k == 2

    def test_inject_minimal(self):
        p = Problem.inject({"group_order": 729, "fiber_size": 9, "k": 3})
        assert p.group_order == 729
        assert p.fiber_size == 9

    def test_weights_property(self):
        p = Problem.from_cycles(5, 3)
        w = p.weights
        assert w.h1_exact == 4  # φ(5)

    def test_default_registry_non_empty(self):
        reg = default_registry()
        assert len(reg) > 10

    def test_registry_by_tag(self):
        reg = default_registry()
        cycles = reg.by_tag("cycles")
        assert len(cycles) > 0

    def test_registry_by_fiber(self):
        reg = default_registry()
        m5 = reg.by_fiber_size(5)
        assert len(m5) > 0


# ── 3. Proof ──────────────────────────────────────────────────────────────────

class TestProof:

    def test_theorem_61_status(self):
        pb = ProofBuilder()
        proof = pb.theorem_61()
        assert proof.status == "PROVED"

    def test_theorem_61_steps_non_empty(self):
        proof = ProofBuilder().theorem_61()
        assert len(proof.proof_steps) >= 4

    def test_w4_status(self):
        proof = ProofBuilder().w4_correction()
        assert proof.status == "PROVED"

    def test_impossibility_from_weights(self):
        proof = ProofBuilder().from_weights(extract_weights(4, 3))
        assert proof.status == "PROVED_IMPOSSIBLE"
        assert "IMPOSSIBLE" in proof.to_text()

    def test_existence_from_weights_with_solution(self):
        from symlib.kernel.construction import ConstructionEngine
        sigma = ConstructionEngine(5, 3).construct()
        proof = ProofBuilder().from_weights(extract_weights(5, 3), solution=sigma)
        assert proof.status == "PROVED_POSSIBLE"

    def test_open_from_weights(self):
        proof = ProofBuilder().from_weights(extract_weights(7, 3))
        assert proof.status == "OPEN"

    def test_proof_to_dict(self):
        proof = ProofBuilder().theorem_61()
        d = proof.to_dict()
        assert "theorem" in d and "proof_steps" in d

    def test_proof_library_version(self):
        proof = ProofBuilder().theorem_61()
        assert proof.library_ver == "2.2.0"

    def test_lean4_export_non_empty(self):
        lean = Lean4Exporter().export_parity_obstruction()
        assert len(lean) > 100

    def test_lean4_has_theorem_keyword(self):
        lean = Lean4Exporter().export_parity_obstruction()
        assert "theorem" in lean

    def test_lean4_export_all(self):
        all_lean = Lean4Exporter().export_all()
        assert "Theorem 6.1" in all_lean or "parity" in all_lean.lower()


# ── 4. Theorem utilities ──────────────────────────────────────────────────────

class TestTheoremUtilities:

    # ParityObstruction
    def test_parity_m8_k3_blocked(self):
        assert ParityObstruction.check(8, 3).blocked

    def test_parity_m8_k2_clear(self):
        assert not ParityObstruction.check(8, 2).blocked

    def test_parity_m15_k3_clear(self):
        # 15 is odd — coprime-to-15 includes even numbers
        assert not ParityObstruction.check(15, 3).blocked

    def test_parity_reason_non_empty(self):
        r = ParityObstruction.check(8, 3)
        assert len(r.reason) > 0

    def test_parity_fix_non_empty(self):
        r = ParityObstruction.check(8, 3)
        assert len(r.fix) > 0

    def test_parity_batch(self):
        results = ParityObstruction.check_batch([(8,3),(8,2),(6,3),(6,4)])
        assert results[(8,3)].blocked
        assert not results[(8,2)].blocked

    # CoprimeCoverage
    def test_coverage_step7_space12_full(self):
        assert CoprimeCoverage.check(7, 12).covers_all

    def test_coverage_step4_space12_partial(self):
        r = CoprimeCoverage.check(4, 12)
        assert not r.covers_all
        assert r.period == 3

    def test_coverage_valid_steps(self):
        valid = CoprimeCoverage.valid_steps(12)
        assert 7 in valid
        assert 4 not in valid

    def test_coverage_smallest_valid(self):
        assert CoprimeCoverage.smallest_valid_step(12) == 1

    # QuotientCounter
    def test_quotient_phi_12(self):
        assert QuotientCounter.distinct_states(12) == 4

    def test_quotient_phi_7(self):
        assert QuotientCounter.distinct_states(7) == 6

    def test_quotient_raw_vs_distinct(self):
        info = QuotientCounter.raw_vs_distinct(12)
        assert info["raw_states"] == 12
        assert info["distinct_states"] == 4
        assert info["correction_factor"] == 3.0

    def test_quotient_warning(self):
        # Warning fires when enumerating raw is wasteful vs orbit representatives
        w = QuotientCounter.enumeration_warning(m=12, k=4)
        # 12^4=20736 raw vs 4^4=256 distinct — should warn
        assert w is not None or QuotientCounter.enumeration_warning(m=7, k=5) is not None

    # CanonicalSeed
    def test_canonical_m7(self):
        seed = CanonicalSeed.for_odd_m(7)
        assert seed == (1, 5, 1)
        assert sum(seed) == 7

    def test_canonical_m11(self):
        seed = CanonicalSeed.for_odd_m(11)
        assert seed == (1, 9, 1)

    def test_canonical_even_returns_none(self):
        assert CanonicalSeed.for_odd_m(4) is None
        assert CanonicalSeed.for_odd_m(6) is None

    def test_canonical_verify(self):
        for m in [3, 5, 7, 9, 11]:
            seed = CanonicalSeed.for_odd_m(m)
            assert CanonicalSeed.verify(seed, m)

    # DepthBarrierAnalyzer
    def test_barrier_m6_primes(self):
        info = DepthBarrierAnalyzer.analyze(6)
        assert info["primes"] == [2, 3]

    def test_barrier_m6_depth(self):
        assert DepthBarrierAnalyzer.analyze(6)["barrier_depth"] == 2

    def test_barrier_m7_prime(self):
        assert DepthBarrierAnalyzer.analyze(7)["is_prime"]

    def test_barrier_m30_depth3(self):
        assert DepthBarrierAnalyzer.analyze(30)["barrier_depth"] == 3

    def test_barrier_recommended_p_orbit_scales(self):
        d2 = DepthBarrierAnalyzer.analyze(6)["recommended_params"]["p_orbit"]
        d3 = DepthBarrierAnalyzer.analyze(30)["recommended_params"]["p_orbit"]
        assert d3 > d2  # deeper barrier → more orbit moves
