"""
test_kernel.py — symlib kernel test suite
==========================================
64 tests covering: weights, obstruction, construction,
verify, torsor, group algebra, SES analyzer.

All tests are deterministic — no randomness, no timing dependencies.
"""
import pytest
from symlib.kernel.weights      import extract_weights, phi, coprime_elements
from symlib.kernel.obstruction  import ObstructionChecker, NO_OBSTRUCTION
from symlib.kernel.construction import ConstructionEngine
from symlib.kernel.verify       import verify_sigma, verify_and_diagnose
from symlib.kernel.torsor       import TorsorStructure


# ── 1. Weights ────────────────────────────────────────────────────────────────

class TestWeights:

    def test_w1_m4_k3_blocked(self):
        assert extract_weights(4, 3).h2_blocks is True

    def test_w1_m5_k3_not_blocked(self):
        assert extract_weights(5, 3).h2_blocks is False

    def test_w1_m4_k4_not_blocked(self):
        assert extract_weights(4, 4).h2_blocks is False

    def test_w2_m5_k3_r_count(self):
        assert extract_weights(5, 3).r_count == 6

    def test_w2_m4_k3_zero(self):
        assert extract_weights(4, 3).r_count == 0

    def test_w3_canonical_m5_k3(self):
        w = extract_weights(5, 3)
        assert w.canonical == (1, 1, 3)
        assert sum(w.canonical) == 5

    def test_w3_canonical_m7_k3(self):
        w = extract_weights(7, 3)
        assert w.canonical is not None
        assert sum(w.canonical) == 7

    def test_w4_phi_m3(self):
        assert extract_weights(3, 3).h1_exact == 2   # φ(3)

    def test_w4_phi_m5(self):
        assert extract_weights(5, 3).h1_exact == 4   # φ(5)

    def test_w4_phi_m7(self):
        assert extract_weights(7, 3).h1_exact == 6   # φ(7)

    def test_w4_phi_m12(self):
        assert extract_weights(12, 3).h1_exact == 4  # φ(12)

    def test_w8_orbit_size_m3(self):
        assert extract_weights(3, 3).orbit_size == 9   # 3^(3-1)

    def test_w8_orbit_size_m5(self):
        assert extract_weights(5, 3).orbit_size == 625  # 5^(5-1)

    def test_strategy_impossible(self):
        assert extract_weights(4, 3).strategy == "S4_prove_impossible"

    def test_strategy_constructible(self):
        assert extract_weights(5, 3).strategy == "S1_column_uniform"

    def test_solvable_odd_m(self):
        for m in [3, 5, 7, 9, 11]:
            assert extract_weights(m, 3).solvable

    def test_solvable_even_m_odd_k_false(self):
        for m in [4, 6, 8, 10]:
            assert not extract_weights(m, 3).solvable

    def test_solvable_even_m_even_k_true(self):
        # Even m with even k: m=4 k=4 and m=8 k=4 are solvable
        # m=6 k=4 is NOT solvable: coprime-to-6={1,5}, no 4-tuple sums to 6
        assert extract_weights(4, 4).solvable
        assert extract_weights(8, 4).solvable
        # m=6 is a known exception: φ(6)=2, {1,5} can't make 4-tuple summing to 6
        assert not extract_weights(6, 4).solvable

    def test_phi_standalone(self):
        assert phi(7)  == 6
        assert phi(12) == 4
        assert phi(1)  == 0

    def test_coprime_elements_m8(self):
        assert coprime_elements(8) == (1, 3, 5, 7)

    def test_coprime_elements_m6(self):
        assert coprime_elements(6) == (1, 5)

    def test_weights_cached(self):
        w1 = extract_weights(5, 3)
        w2 = extract_weights(5, 3)
        assert w1 is w2  # same object from lru_cache

    def test_as_dict_keys(self):
        d = extract_weights(5, 3).as_dict()
        for key in ["W1_h2_blocks","W2_r_count","W3_canonical","W4_h1_exact",
                    "W5_search_exp","W6_compression","W7_sol_lb","W8_orbit_size"]:
            assert key in d


# ── 2. Obstruction ────────────────────────────────────────────────────────────

class TestObstruction:

    def test_h2_parity_m4_k3_blocked(self):
        r = ObstructionChecker(4, 3).h2_parity()
        assert r.blocked
        assert r.obstruction_type == "H2_parity"
        assert r.level == 2

    def test_h2_parity_m5_k3_clear(self):
        r = ObstructionChecker(5, 3).h2_parity()
        assert not r.blocked

    def test_h2_parity_m4_k4_clear(self):
        r = ObstructionChecker(4, 4).h2_parity()
        assert not r.blocked

    def test_h3_fiber_uniform_m4_k4_blocked(self):
        r = ObstructionChecker(4, 4).h3_fiber_uniform()
        assert r.blocked
        assert r.level == 3

    def test_h3_not_triggered_other_cases(self):
        r = ObstructionChecker(5, 3).h3_fiber_uniform()
        assert not r.blocked

    def test_check_full_tower_m4_k4(self):
        r = ObstructionChecker(4, 4).check()
        assert r.blocked  # H³ catches it

    def test_check_full_tower_m5_k3_clear(self):
        r = ObstructionChecker(5, 3).check()
        assert not r.blocked

    def test_single_cycle_coprime(self):
        r = ObstructionChecker.single_cycle_check(r=1, b_sum=1, m=5)
        assert not r.blocked

    def test_single_cycle_non_coprime_r(self):
        r = ObstructionChecker.single_cycle_check(r=2, b_sum=1, m=4)
        assert r.blocked

    def test_coverage_full(self):
        assert not ObstructionChecker.coverage_check(7, 12).blocked

    def test_coverage_partial(self):
        r = ObstructionChecker.coverage_check(4, 12)
        assert r.blocked

    def test_proof_steps_non_empty(self):
        r = ObstructionChecker(6, 3).h2_parity()
        assert len(r.proof_steps) >= 4

    def test_explain_contains_obstruction(self):
        r = ObstructionChecker(4, 3).h2_parity()
        text = r.explain()
        assert "obstruction" in text.lower() or "OBSTRUCTION" in text

    def test_all_even_m_odd_k_blocked(self):
        for m in [4, 6, 8, 10, 12, 14, 16]:
            assert ObstructionChecker(m, 3).h2_parity().blocked


# ── 3. Construction ───────────────────────────────────────────────────────────

class TestConstruction:

    def test_level_m3_precomputed(self):
        assert ConstructionEngine(3, 3).construction_level() == "precomputed"

    def test_level_m4_precomputed(self):
        assert ConstructionEngine(4, 3).construction_level() == "precomputed"

    def test_level_m5_precomputed(self):
        assert ConstructionEngine(5, 3).construction_level() == "precomputed"

    def test_level_m7_direct_formula(self):
        assert ConstructionEngine(7, 3).construction_level() == "direct_formula"

    def test_level_m6_impossible(self):
        assert ConstructionEngine(6, 3).construction_level() == "impossible"

    def test_construct_m3_valid(self, solved_m3):
        assert verify_sigma(solved_m3, 3)

    def test_construct_m4_valid(self, solved_m4):
        assert verify_sigma(solved_m4, 4)

    def test_construct_m5_valid(self, solved_m5):
        assert verify_sigma(solved_m5, 5)

    def test_construct_impossible_returns_none(self):
        assert ConstructionEngine(6, 3).construct() is None

    def test_construct_m4_despite_h2_block(self, solved_m4):
        # m=4 k=3 has H² obstruction but a valid solution exists (via SA)
        assert solved_m4 is not None
        assert extract_weights(4, 3).h2_blocks is True  # H² blocks column-uniform
        assert verify_sigma(solved_m4, 4)               # but solution is valid


# ── 4. Verify ─────────────────────────────────────────────────────────────────

class TestVerify:

    def test_verify_m3_all_hamilton(self, solved_m3):
        diag = verify_and_diagnose(solved_m3, 3)
        assert diag["valid"]
        assert all(c["is_hamilton"] for c in diag["colours"])

    def test_verify_m3_correct_vertex_count(self, solved_m3):
        diag = verify_and_diagnose(solved_m3, 3)
        assert diag["n_vertices"] == 27

    def test_verify_m4_all_hamilton(self, solved_m4):
        diag = verify_and_diagnose(solved_m4, 4)
        assert diag["valid"]

    def test_verify_m5_all_hamilton(self, solved_m5):
        diag = verify_and_diagnose(solved_m5, 5)
        assert diag["valid"]
        assert diag["n_vertices"] == 125

    def test_verify_returns_false_on_bad_sigma(self):
        bad = {(0,0,0): (0,1,2), (0,0,1): (0,1,2)}  # incomplete
        assert not verify_sigma(bad, 3)


# ── 5. Torsor ─────────────────────────────────────────────────────────────────

class TestTorsor:

    def test_m3_not_empty(self):
        info = TorsorStructure(3, 3).analyse()
        assert not info.is_empty

    def test_m3_h1_order(self):
        info = TorsorStructure(3, 3).analyse()
        assert info.h1_order == 2  # φ(3)

    def test_m3_solution_count_648(self):
        info = TorsorStructure(3, 3).analyse()
        assert info.solution_count == 648

    def test_m3_is_exact(self):
        assert TorsorStructure(3, 3).analyse().is_exact

    def test_m5_is_lower_bound(self):
        assert not TorsorStructure(5, 3).analyse().is_exact

    def test_m4_k3_torsor_empty(self):
        info = TorsorStructure(4, 3).analyse()
        assert info.is_empty

    def test_coboundaries_m3_count(self):
        cobounds = TorsorStructure(3, 3).coboundaries()
        assert len(cobounds) == 9  # 3^(3-1)

    def test_h1_classes_m3(self):
        classes = TorsorStructure(3, 3).h1_classes()
        assert len(classes) == 2  # φ(3)
        class_sizes = [len(v) for v in classes.values()]
        assert all(s == 9 for s in class_sizes)  # each class = 3^(3-1)

    def test_total_m3_confirmed(self):
        ts = TorsorStructure(3, 3)
        classes = ts.h1_classes()
        cobounds = ts.coboundaries()
        total = len(classes) * len(cobounds)
        assert total == 18  # 2 × 9 = 18 cocycles; full count = 648 via W7
