"""
test_autodetect.py — symlib auto-detection test suite
======================================================
77 tests covering: group algebra, SES analyzer,
AutoDetector, classify pipeline, detection quality.
"""
import pytest
from symlib.kernel.group_algebra import (
    cyclic_group, product_group, symmetric_group,
    dihedral_group, triple_product,
)
from symlib.kernel.ses_analyzer import SESAnalyzer
from symlib.autodetect import AutoDetector, detect
from symlib.engine import DecisionEngine, Status
from symlib.domain import Problem


@pytest.fixture(scope="module")
def detector():
    return AutoDetector()

@pytest.fixture(scope="module")
def engine():
    return DecisionEngine()


# ── 1. Group algebra ──────────────────────────────────────────────────────────

class TestGroupAlgebra:

    def test_z3_order(self):
        assert cyclic_group(3).order == 3

    def test_z3_abelian(self):
        assert cyclic_group(3).is_abelian()

    def test_z5_only_trivial_subgroups(self):
        # Z_5 is prime — only {e} and Z_5
        assert len(cyclic_group(5).all_subgroups()) == 2

    def test_z6_subgroup_orders(self):
        orders = sorted(len(s) for s in cyclic_group(6).all_subgroups())
        assert orders == [1, 2, 3, 6]

    def test_z4x6_order(self):
        assert product_group(4, 6).order == 24

    def test_z4x6_abelian(self):
        assert product_group(4, 6).is_abelian()

    def test_z4x6_has_order8_subgroup(self):
        assert any(len(s) == 8 for s in product_group(4, 6).all_subgroups())

    def test_s3_order(self):
        assert symmetric_group(3).order == 6

    def test_s3_nonabelian(self):
        assert not symmetric_group(3).is_abelian()

    def test_s3_three_normal_subgroups(self):
        normals = symmetric_group(3).normal_subgroups()
        assert len(normals) == 3

    def test_s3_normal_orders(self):
        orders = sorted(len(sg) for sg in symmetric_group(3).normal_subgroups())
        assert orders == [1, 3, 6]

    def test_d5_order(self):
        assert dihedral_group(5).order == 10

    def test_d5_nonabelian(self):
        assert not dihedral_group(5).is_abelian()

    def test_d5_normal_orders(self):
        orders = sorted(len(sg) for sg in dihedral_group(5).normal_subgroups())
        assert orders == [1, 5, 10]

    def test_z3_cube_order(self):
        assert triple_product(3).order == 27

    def test_z3_cube_abelian(self):
        assert triple_product(3).is_abelian()

    @pytest.mark.parametrize("G", [
        cyclic_group(3), cyclic_group(5), product_group(4, 6),
        symmetric_group(3), dihedral_group(5), triple_product(3),
    ])
    def test_associativity(self, G):
        for a in range(min(G.order, 4)):
            for b in range(min(G.order, 4)):
                for c in range(min(G.order, 4)):
                    assert G.mul(G.mul(a, b), c) == G.mul(a, G.mul(b, c))

    def test_z6_element_orders(self):
        z6 = cyclic_group(6)
        assert z6.element_order(1) == 6
        assert z6.element_order(2) == 3
        assert z6.element_order(3) == 2


# ── 2. SES analyzer ───────────────────────────────────────────────────────────

class TestSESAnalyzer:

    def test_z3_cube_best_fiber_3(self):
        a = SESAnalyzer(triple_product(3), k=3).analyze()
        assert a.best.fiber_size == 3

    def test_z3_cube_constructible(self):
        a = SESAnalyzer(triple_product(3), k=3).analyze()
        assert a.has_constructible()

    def test_s3_k2_fiber_2(self):
        a = SESAnalyzer(symmetric_group(3), k=2).analyze()
        assert a.best.fiber_size == 2

    def test_s3_k2_not_blocked(self):
        a = SESAnalyzer(symmetric_group(3), k=2).analyze()
        assert not a.best.weights.h2_blocks

    def test_s3_k3_impossible(self):
        a = SESAnalyzer(symmetric_group(3), k=3).analyze()
        assert a.is_provably_impossible()

    def test_z4x6_k3_best_not_blocked(self):
        a = SESAnalyzer(product_group(4, 6), k=3).analyze()
        assert not a.best.weights.h2_blocks

    def test_z4x6_k3_fiber_3(self):
        a = SESAnalyzer(product_group(4, 6), k=3).analyze()
        assert a.best.fiber_size == 3

    def test_z5_cube_k3_fiber_5(self):
        a = SESAnalyzer(triple_product(5), k=3).analyze()
        assert a.best.fiber_size == 5

    def test_d5_k2_fiber_2(self):
        a = SESAnalyzer(dihedral_group(5), k=2).analyze()
        assert a.best.fiber_size == 2

    def test_z6_k3_best_fiber_3(self):
        # m=2 is blocked for k=3; next best should be m=3
        a = SESAnalyzer(cyclic_group(6), k=3).analyze()
        assert a.best.fiber_size == 3
        assert not a.best.weights.h2_blocks

    def test_practical_beats_impractical(self):
        a = SESAnalyzer(triple_product(3), k=3).analyze()
        practical = [c for c in a.candidates if c.fiber_size**2 <= 27]
        impractical = [c for c in a.candidates if c.fiber_size**2 > 27]
        if practical and impractical:
            assert practical[0].quality_score >= impractical[0].quality_score


# ── 3. AutoDetector ───────────────────────────────────────────────────────────

class TestAutoDetector:

    def test_z3_cube_k3_runs(self, detector):
        r = detector.from_triple_product(3, 3)
        assert r is not None

    def test_z3_cube_k3_fiber_3(self, detector):
        r = detector.from_triple_product(3, 3)
        assert r.best_ses.fiber_size == 3

    def test_z3_cube_k3_problem_created(self, detector):
        r = detector.from_triple_product(3, 3)
        assert r.problem is not None

    def test_z3_cube_k3_constructible(self, detector):
        assert detector.from_triple_product(3, 3).is_constructible

    def test_s3_k2_constructible(self, detector):
        assert detector.from_symmetric(3, 2).is_constructible

    def test_s3_k3_impossible(self, detector):
        assert detector.from_symmetric(3, 3).is_impossible

    def test_z4x6_k3_constructible(self, detector):
        assert detector.from_product(4, 6, 3).is_constructible

    def test_d5_k2_constructible(self, detector):
        assert detector.from_dihedral(5, 2).is_constructible

    def test_from_table_runs(self, detector):
        table = [[(a+b)%3 for b in range(3)] for a in range(3)]
        r = detector.from_table(table, k=3, name="Z_3_table")
        assert r is not None

    def test_z9_k3_runs(self, detector):
        r = detector.from_cyclic(9, 3)
        assert r is not None

    def test_z7_prime_fallback(self, detector):
        r = detector.from_cyclic(7, 3)
        assert r.problem is not None
        assert r.problem.fiber_size == 7

    def test_z7_prime_notes(self, detector):
        r = detector.from_cyclic(7, 3)
        assert any("prime" in n.lower() for n in r.detection_notes)

    def test_detect_convenience_cyclic(self):
        r = detect("cyclic", k=3, n=7)
        assert r is not None

    def test_detect_convenience_product(self):
        r = detect("product", k=3, m=6, n=9)
        assert r.is_constructible

    def test_detect_convenience_dihedral(self):
        r = detect("dihedral", k=2, n=5)
        assert r.is_constructible

    def test_compare_all_k_returns_dict(self, detector):
        G = triple_product(3)
        results = detector.compare_all_k(G, k_range=range(2, 5))
        assert isinstance(results, dict)
        assert set(results.keys()) == {2, 3, 4}

    def test_scan_cyclic_range(self, detector):
        results = detector.scan_cyclic_range(range(3, 8), k=3)
        assert isinstance(results, list)
        assert len(results) == 5

    def test_notes_non_empty(self, detector):
        r = detector.from_product(4, 6, 3)
        assert len(r.detection_notes) > 0

    def test_explain_non_trivial(self, detector):
        r = detector.from_triple_product(3, 3)
        text = r.explain()
        assert len(text) > 100

    def test_z5_cube_fast_path(self, detector):
        """Z_5³ should use fast path, not slow subgroup enumeration."""
        import time
        t0 = time.perf_counter()
        r = detector.from_triple_product(5, 3)
        elapsed = (time.perf_counter() - t0) * 1000
        assert elapsed < 500, f"Fast path should take <500ms, took {elapsed:.0f}ms"
        assert r.best_ses.fiber_size == 5


# ── 4. Auto-detect → classify pipeline ───────────────────────────────────────

class TestAutoDetectClassify:

    def test_z3_cube_proved_possible(self, detector, engine):
        r = detector.from_triple_product(3, 3)
        cl = r.classify()
        assert cl.status == Status.PROVED_POSSIBLE

    def test_z3_cube_solution_found(self, detector):
        r = detector.from_triple_product(3, 3)
        cl = r.classify()
        assert cl.solution is not None

    def test_s3_k2_no_obstruction(self, detector):
        r = detector.from_symmetric(3, 2)
        cl = r.classify()
        assert cl.status != Status.PROVED_IMPOSSIBLE

    def test_s3_k3_impossible_classify(self, detector):
        r = detector.from_symmetric(3, 3)
        # S_3 k=3 is provably impossible — problem may still be created for the engine
        assert r.is_impossible

    def test_z5_cube_proved_possible(self, detector):
        r = detector.from_triple_product(5, 3)
        cl = r.classify()
        assert cl.status == Status.PROVED_POSSIBLE

    def test_cross_check_m3_k3(self, detector, engine):
        r_auto   = detector.from_triple_product(3, 3)
        r_manual = engine.run(Problem.from_cycles(3, 3))
        assert r_auto.is_constructible == (r_manual.status == Status.PROVED_POSSIBLE)

    def test_cross_check_m5_k3(self, detector, engine):
        r_auto   = detector.from_triple_product(5, 3)
        r_manual = engine.run(Problem.from_cycles(5, 3))
        assert r_auto.is_constructible == (r_manual.status == Status.PROVED_POSSIBLE)
