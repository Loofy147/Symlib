"""
symlib.domain
=============
Domain-agnostic problem representation for symmetric systems.
"""

from __future__ import annotations
from math import gcd
from dataclasses import dataclass, field
from typing import Optional, List, Any
from symlib.kernel.weights import extract_weights, Weights


@dataclass
class Problem:
    name:           str
    group_order:    int
    fiber_size:     int
    k:              int
    fiber_map_desc: str
    tags:           List[str] = field(default_factory=list)
    precomputed:    Any       = None
    notes:          str       = ""

    @property
    def m(self) -> int:
        return self.fiber_size

    @property
    def weights(self) -> Weights:
        return extract_weights(self.fiber_size, self.k)

    def is_feasible(self) -> bool:
        return not self.weights.h2_blocks

    def is_constructible(self) -> bool:
        return self.weights.solvable

    def summary(self) -> str:
        w = self.weights
        return (
            f"{self.name}\n"
            f"  |G|={self.group_order}  m={self.fiber_size}  k={self.k}\n"
            f"  φ: {self.fiber_map_desc}\n"
            f"  {w.summary()}"
        )

    @classmethod
    def from_cycles(cls, m: int, k: int) -> "Problem":
        return cls(
            name=f"Cycles G_{m} k={k}",
            group_order=m**3,
            fiber_size=m,
            k=k,
            fiber_map_desc=f"(i+j+k) mod {m}",
            tags=["cycles", "logic", "odd" if m % 2 == 1 else "even"],
        )

    @classmethod
    def from_product_group(cls, m: int, n: int, k: int) -> "Problem":
        g = gcd(m, n)
        return cls(
            name=f"Z_{m}×Z_{n} k={k}",
            group_order=m * n,
            fiber_size=g,
            k=k,
            fiber_map_desc=f"sum mod gcd({m},{n})",
            tags=["product", "logic", f"gcd{g}"],
        )

    @classmethod
    def from_nonabelian(
        cls, group_name: str, group_order: int,
        normal_subgroup_name: str, normal_subgroup_index: int, k: int
    ) -> "Problem":
        return cls(
            name=f"{group_name} / {normal_subgroup_name} k={k}",
            group_order=group_order,
            fiber_size=normal_subgroup_index,
            k=k,
            fiber_map_desc=f"sign map {group_name}",
            tags=["nonabelian", "semantics", group_name],
        )

    @classmethod
    def inject(cls, description: dict) -> "Problem":
        return cls(
            name=description.get("name", f"G_m{description['fiber_size']}_k{description['k']}"),
            group_order=description["group_order"],
            fiber_size=description["fiber_size"],
            k=description["k"],
            fiber_map_desc=description.get("fiber_map_desc", ""),
            tags=description.get("tags", []),
            precomputed=description.get("precomputed", None),
            notes=description.get("notes", ""),
        )


class DomainRegistry:
    def __init__(self):
        self._domains: dict[str, Problem] = {}

    def register(self, p: Problem) -> "DomainRegistry":
        self._domains[p.name] = p
        return self

    def get(self, name: str) -> Optional[Problem]:
        return self._domains.get(name)

    def all(self) -> list[Problem]:
        return list(self._domains.values())

    def by_tag(self, tag: str) -> list[Problem]:
        return [p for p in self._domains.values() if tag in p.tags]

    def by_fiber_size(self, m: int) -> list[Problem]:
        return [p for p in self._domains.values() if p.fiber_size == m]

    def find_similar(self, p: Problem) -> list[Problem]:
        w = p.weights
        fingerprint = (w.h2_blocks, w.r_count > 0, p.fiber_size % 2)
        return [
            q for q in self._domains.values()
            if q.name != p.name and (
                lambda qw: (qw.h2_blocks, qw.r_count > 0, q.fiber_size % 2)
            )(q.weights) == fingerprint
        ]

    def __len__(self) -> int:
        return len(self._domains)


def default_registry() -> DomainRegistry:
    reg = DomainRegistry()

    # 1. Logic Fibers (Foundation & Meta)
    # ────────────────────────────────────────────────────────────────
    for m in [3, 5, 7, 11, 13]:
        reg.register(Problem.from_cycles(m, 3))

    reg.register(Problem(
        name="Lambda Calculus Core", group_order=256, fiber_size=16,
        k=2, fiber_map_desc="Church-Rosser parity",
        tags=["logic", "foundation"],
    ))
    reg.register(Problem(
        name="ZFC Axiom Matrix", group_order=1024, fiber_size=32,
        k=3, fiber_map_desc="Well-ordering projection",
        tags=["logic", "set-theory"],
    ))
    reg.register(Problem(
        name="Godel Boundary", group_order=10**6, fiber_size=1000,
        k=1, fiber_map_desc="unsolvability modulus",
        tags=["logic", "meta"],
    ))
    reg.register(Problem(
        name="Game Theory: Nash Equil", group_order=2**10, fiber_size=10,
        k=2, fiber_map_desc="strategy fixed point",
        tags=["logic", "economics"],
    ))

    # 2. Semantic Fibers (Representation & Language)
    # ────────────────────────────────────────────────────────────────
    reg.register(Problem.from_nonabelian("Transformer Attention", 512, "Head", 8, k=8))
    reg.register(Problem(
        name="Word2Vec Torus", group_order=300**2, fiber_size=300,
        k=1, fiber_map_desc="cosine similarity modulo",
        tags=["semantics", "nlp"],
    ))
    reg.register(Problem(
        name="BERT Encoding Space", group_order=768**2, fiber_size=768,
        k=12, fiber_map_desc="attention mask parity",
        tags=["semantics", "transformer"],
    ))
    reg.register(Problem.from_nonabelian("Universal Grammar", 120, "S5", 24, k=3))
    reg.register(Problem(
        name="DNA Codon Map", group_order=64, fiber_size=20,
        k=3, fiber_map_desc="amino acid redundancy",
        tags=["semantics", "biology"],
    ))

    # 3. Science Fibers (Physical Systems)
    # ────────────────────────────────────────────────────────────────
    reg.register(Problem(
        name="General Relativity Tensor", group_order=256, fiber_size=4,
        k=4, fiber_map_desc="Lorentz invariance",
        tags=["science", "physics"],
    ))
    reg.register(Problem(
        name="Schrodinger Waveform", group_order=256**2, fiber_size=256,
        k=2, fiber_map_desc="Hermitian adjoint",
        tags=["science", "quantum"],
    ))
    reg.register(Problem(
        name="Navier-Stokes Modulo", group_order=10**9, fiber_size=10**3,
        k=3, fiber_map_desc="viscosity flux",
        tags=["science", "fluids"],
    ))
    reg.register(Problem(
        name="Mendeleev Valence", group_order=118, fiber_size=18,
        k=2, fiber_map_desc="electron shell periodicity",
        tags=["science", "chemistry"],
    ))
    reg.register(Problem(
        name="Planck Constant Grid", group_order=10**34, fiber_size=64,
        k=4, fiber_map_desc="quantization scale",
        tags=["science", "physics"],
    ))

    # 4. Execution Fibers (Protocols & Systems)
    # ────────────────────────────────────────────────────────────────
    reg.register(Problem(
        name="Paxos Consensus", group_order=5, fiber_size=3,
        k=2, fiber_map_desc="quorum majority",
        tags=["execution", "distributed"],
    ))
    reg.register(Problem(
        name="Dijkstra Shortest Path", group_order=1000**2, fiber_size=1000,
        k=1, fiber_map_desc="priority queue ordering",
        tags=["execution", "graph"],
    ))
    reg.register(Problem(
        name="Quicksort Partition", group_order=1024, fiber_size=2,
        k=10, fiber_map_desc="recursive pivot",
        tags=["execution", "sorting"],
    ))
    reg.register(Problem(
        name="TCP Handshake Parity", group_order=2**32, fiber_size=2,
        k=3, fiber_map_desc="sequence number sync",
        tags=["execution", "network"],
    ))
    reg.register(Problem(
        name="RSA 2048 Modulus", group_order=2**2048, fiber_size=2048,
        k=1, fiber_map_desc="prime factorization symmetry",
        tags=["execution", "security"],
    ))

    # 5. Universal Anchor
    reg.register(Problem(
        name="Universal G3 Manifold", group_order=256**4, fiber_size=256,
        k=4, fiber_map_desc="Topological Harmony gcd(S, 256)=1",
        tags=["universal", "manifold", "g3"],
    ))

    return reg

Domain = Problem
