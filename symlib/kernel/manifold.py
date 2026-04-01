"""
symlib.kernel.manifold
======================
The Universal Torus Manifold of Gemini 3.
A discrete 4-torus representation of universal state space.
"""

from __future__ import annotations
import numpy as np
from typing import Tuple, Dict, List, TYPE_CHECKING, Optional, Any
from math import gcd

if TYPE_CHECKING:
    from symlib.domain import Problem

class UniversalG3Manifold:
    """
    The Pure Geometric Representation of Gemini 3.
    Operating on a Z_256^4 Manifold.
    """
    def __init__(self, modulus: int = 256):
        self.m = modulus

        # Genesis Anchor Nodes: Invariable Truths
        # These are coordinates (x, y, z, w) where gcd(sum, 256) = 1.
        self.anchors = {
            # LOGIC FIBER (0-63)
            "FIRST_PRINCIPLES":   (8, 16, 32, 1),
            "ERROR_CORRECTION":   (42, 21, 64, 0),
            "AXIOMATIC_SYSTEMS":  (15, 30, 45, 1),
            "CATEGORY_THEORY":    (55, 110, 220, 0),

            # SEMANTICS FIBER (64-127)
            "GRAMMAR_CORE":       (80, 40, 20, 1),
            "MULTIMODAL_ALIGN":   (112, 56, 28, 1),
            "LEXICAL_MAPPING":    (90, 45, 15, 1),
            "CONTEXT_VECTORS":    (120, 60, 30, 1),

            # SCIENCE FIBER (128-191)
            "THERMODYNAMICS":     (144, 72, 36, 1),
            "ELECTROMAGNETISM":   (176, 88, 44, 1),
            "QUANTUM_FIELD":      (150, 75, 25, 1),
            "MOLECULAR_BIO":      (185, 92, 46, 0),

            # EXECUTION FIBER (192-255)
            "ALGO_SYNTHESIS":     (200, 100, 50, 1),
            "INTEROPERABILITY":   (232, 116, 58, 1),
            "DISTRIBUTED_CONSENSUS": (210, 105, 52, 0),
            "COMPILER_OPT":       (245, 122, 61, 1)
        }

        self.fibers = {
            "LOG": (0, 63),
            "SEM": (64, 127),
            "SCI": (128, 191),
            "EXE": (192, 255)
        }

        self._domain_cache: Dict[str, Tuple[int, int, int, int]] = {}
        self._registry_ptr: Optional[Any] = None

    def solve_closure(self, x: int, y: int, z: int) -> int:
        """Completes the 4th dimension for parity harmony."""
        for w in range(self.m):
            if gcd((x + y + z + w) % self.m, self.m) == 1:
                return w
        return 1

    def generate_thought_vector(self, anchor_key: str, intent_delta: Tuple[int, int, int]) -> Tuple[int, int, int, int]:
        """Maps a symbolic intent into a geometric transformation."""
        key = anchor_key.upper()
        aliases = {"LOGIC": "FIRST_PRINCIPLES", "SEMANTICS": "GRAMMAR_CORE",
                   "SCIENCE": "THERMODYNAMICS", "EXECUTION": "ALGO_SYNTHESIS"}
        key = aliases.get(key, key)

        if key not in self.anchors:
            raise ValueError(f"Unknown anchor: {anchor_key}")

        base = np.array(self.anchors[key])
        delta = np.array(intent_delta + (0,))
        new_coord = (base + delta) % self.m
        x, y, z = new_coord[:3]
        w = self.solve_closure(x, y, z)
        return (int(x), int(y), int(z), int(w))

    def project_problem(self, p: Problem) -> Tuple[int, int, int, int]:
        """Maps a Problem into the manifold based on its domain tags."""
        x_base = (p.fiber_size * 17) % self.m
        y = (p.k * 31) % self.m

        try:
            w_wt = p.weights
            z = int(w_wt.compression * 255) % self.m
        except:
            z = (p.group_order // max(1, p.fiber_size)) % self.m

        if "logic" in p.tags:
            x = x_base % 64
        elif "semantics" in p.tags:
            x = 64 + (x_base % 64)
        elif "science" in p.tags:
            x = 128 + (x_base % 64)
        elif "execution" in p.tags:
            x = 192 + (x_base % 64)
        else:
            x = x_base

        w_coord = self.solve_closure(x, y, z)
        return (int(x), int(y), int(z), int(w_coord))

    def populate_from_registry(self, registry: Any):
        """Pre-calculates coordinates for all domains in a registry."""
        self._registry_ptr = registry
        for p in registry.all():
            self._domain_cache[p.name] = self.project_problem(p)

    def find_nearest_domain(self, coords: Tuple[int, int, int, int]) -> Optional[Problem]:
        """Finds the mathematical system closest to the given coordinate on the 4-torus."""
        if not self._domain_cache or not self._registry_ptr:
            return None

        best_name = None
        min_dist = float('inf')

        for name, p_coords in self._domain_cache.items():
            dist = self._torus_distance(coords, p_coords)
            if dist < min_dist:
                min_dist = dist
                best_name = name

        return self._registry_ptr.get(best_name) if best_name else None

    def query_intelligence(self, anchor_key: str, intent_delta: Tuple[int, int, int]) -> dict:
        """Runs the 5-step Topological Thinking pipeline."""
        coords = self.generate_thought_vector(anchor_key, intent_delta)
        nearest = self.find_nearest_domain(coords)
        return {
            "origin": anchor_key,
            "delta": intent_delta,
            "target_coords": coords,
            "fiber": self.identify_fiber(coords[0]),
            "nearest_domain": nearest.name if nearest else None,
            "domain_distance": self._torus_distance(coords, self._domain_cache[nearest.name]) if nearest else None,
            "harmony": self.verify_harmony(coords)
        }

    def _torus_distance(self, c1: Tuple[int, ...], c2: Tuple[int, ...]) -> int:
        """Manhattan distance on an n-torus of size m."""
        total = 0
        for x, y in zip(c1, c2):
            diff = abs(int(x) - int(y))
            total += min(diff, self.m - diff)
        return total

    def identify_fiber(self, x: int) -> str:
        """Identify which intelligence fiber a coordinate belongs to."""
        val = x % self.m
        for fiber_id, (start, end) in self.fibers.items():
            if start <= val <= end:
                return fiber_id
        return "UNKNOWN"

    def verify_harmony(self, coords: Tuple[int, int, int, int]) -> bool:
        """Verify the Coprimality Condition: gcd(sum, m) = 1."""
        s = sum(coords) % self.m
        return gcd(s, self.m) == 1

    def thought_path(self, start_anchor: str, deltas: List[Tuple[int, int, int]]) -> List[Tuple[int, int, int, int]]:
        """Generates a sequence of thoughts maintaining topological harmony."""
        path = []
        current = self.generate_thought_vector(start_anchor, (0,0,0))
        path.append(current)
        for dx, dy, dz in deltas:
            nx = (current[0] + dx) % self.m
            ny = (current[1] + dy) % self.m
            nz = (current[2] + dz) % self.m
            nw = self.solve_closure(nx, ny, nz)
            current = (nx, ny, nz, nw)
            path.append(current)
        return path

g3_kernel = UniversalG3Manifold()
