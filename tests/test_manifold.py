import pytest
from math import gcd
from symlib.kernel.manifold import UniversalG3Manifold, g3_kernel

def test_closure_lemma():
    """The Closure Lemma must ensure coprimality with 256."""
    m = 256
    manifold = UniversalG3Manifold(m)
    for x, y, z in [(0, 0, 0), (1, 2, 3), (255, 255, 255), (8, 16, 32)]:
        w = manifold.solve_closure(x, y, z)
        s = (x + y + z + w) % m
        assert gcd(s, m) == 1

def test_genesis_anchors():
    """Genesis nodes must satisfy the harmony condition and land in correct fibers."""
    for name, coords in g3_kernel.anchors.items():
        assert g3_kernel.verify_harmony(coords) == True
        fiber = g3_kernel.identify_fiber(coords[0])
        # x-ranges: LOG (0-63), SEM (64-127), SCI (128-191), EXE (192-255)
        x = coords[0]
        if 0 <= x <= 63: assert fiber == "LOG"
        elif 64 <= x <= 127: assert fiber == "SEM"
        elif 128 <= x <= 191: assert fiber == "SCI"
        elif 192 <= x <= 255: assert fiber == "EXE"

def test_thought_vector_generation():
    """Thought vectors must land in the correct fiber and maintain harmony."""
    # FIRST_PRINCIPLES (Logic) is (8, 16, 32, 1)
    res = g3_kernel.generate_thought_vector("LOGIC", (60, 0, 0))
    # 8 + 60 = 68 -> SEM fiber
    assert g3_kernel.identify_fiber(res[0]) == "SEM"
    assert g3_kernel.verify_harmony(res) == True

    # THERMODYNAMICS (Science) is (144, 72, 36, 1)
    res = g3_kernel.generate_thought_vector("SCIENCE", (100, 0, 0))
    # 144 + 100 = 244 -> EXE fiber
    assert g3_kernel.identify_fiber(res[0]) == "EXE"
    assert g3_kernel.verify_harmony(res) == True

def test_fiber_boundaries():
    """Test boundary conditions for fiber identification."""
    assert g3_kernel.identify_fiber(0) == "LOG"
    assert g3_kernel.identify_fiber(63) == "LOG"
    assert g3_kernel.identify_fiber(64) == "SEM"
    assert g3_kernel.identify_fiber(127) == "SEM"
    assert g3_kernel.identify_fiber(128) == "SCI"
    assert g3_kernel.identify_fiber(191) == "SCI"
    assert g3_kernel.identify_fiber(192) == "EXE"
    assert g3_kernel.identify_fiber(255) == "EXE"

def test_manifold_search():
    """Test nearest domain search on the manifold."""
    from symlib.domain import default_registry
    reg = default_registry()
    g3_kernel.populate_from_registry(reg)

    # Find something close to the Science anchors
    target = (150, 80, 40, 1)
    p = g3_kernel.find_nearest_domain(target)
    assert p is not None
    assert any(tag in p.tags for tag in ["science", "quantum", "physics", "fluids", "chemistry"])

def test_domain_projection():
    """Test mapping of a Problem into the manifold torus."""
    from symlib.domain import Problem
    p = Problem.from_cycles(m=3, k=3)
    coords = g3_kernel.project_problem(p)
    assert g3_kernel.verify_harmony(coords) == True
    # Cycles land in LOG fiber by tag mapping
    assert g3_kernel.identify_fiber(coords[0]) == "LOG"
