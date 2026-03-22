"""
symlib.domain
=============
Domain-agnostic problem representation.

Any highly symmetric combinatorial problem can be expressed as:
    0 → H → G → G/H → 0

The four coordinates that classify it are:
    C1  Fiber map     φ: G → G/H
    C2  Twisted translation  Q_c(h) = h + b_c(φ(h)) · r_c
    C3  Governing condition  gcd(r_c, |G/H|) = 1
    C4  Parity obstruction   from H²(Z_2, Z/2)

A Problem wraps these into a unified description that the engine
can classify, construct, and prove without knowing the domain.

INJECTION EXAMPLES
------------------
# Cayley digraph G_m
p = Problem.from_cycles(m=5, k=3)

# Any group with explicit SES
p = Problem(
    name="My System",
    group_order=729,
    fiber_size=9,        # |G/H|
    k=3,
    fiber_map_desc="sum mod 9",
    tags=["cayley"],
)

# Auto-detect best SES for a product group
p = Problem.from_product_group(m=6, n=9, k=3)
# → fiber_size = gcd(6,9) = 3, same parity law
"""

from __future__ import annotations
from math import gcd
from dataclasses import dataclass, field
from typing import Optional, List, Any
from symlib.kernel.weights import extract_weights, Weights, phi


@dataclass
class Problem:
    """
    A highly symmetric combinatorial problem.

    Parameters
    ----------
    name            : str   Human-readable name
    group_order     : int   |G|
    fiber_size      : int   |G/H|  — the modulus m
    k               : int   Number of colours / Hamiltonian cycles
    fiber_map_desc  : str   Description of φ: G → G/H
    tags            : list  Searchable tags
    precomputed     : Any   Known solution if available
    notes           : str   Additional information
    """
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
        """Alias: fiber_size = m = |G/H|."""
        return self.fiber_size

    @property
    def weights(self) -> Weights:
        """Extract all 8 weights. Cached."""
        return extract_weights(self.fiber_size, self.k)

    def is_feasible(self) -> bool:
        """True if no H² obstruction (solution may exist)."""
        return not self.weights.h2_blocks

    def is_constructible(self) -> bool:
        """True if solvable via column-uniform construction."""
        return self.weights.solvable

    def summary(self) -> str:
        w = self.weights
        return (
            f"{self.name}\n"
            f"  |G|={self.group_order}  m={self.fiber_size}  k={self.k}\n"
            f"  φ: {self.fiber_map_desc}\n"
            f"  {w.summary()}"
        )

    # ── Factory methods ──────────────────────────────────────────────────────

    @classmethod
    def from_cycles(cls, m: int, k: int) -> "Problem":
        """
        Standard Cayley digraph G_m with k colours.
        G = Z_m³, H = Z_m², G/H = Z_m.
        Fiber map: φ(i,j,k) = (i+j+k) mod m.
        """
        return cls(
            name=f"Cycles G_{m} k={k}",
            group_order=m**3,
            fiber_size=m,
            k=k,
            fiber_map_desc=f"(i+j+k) mod {m}",
            tags=["cycles", "odd" if m % 2 == 1 else "even"],
        )

    @classmethod
    def from_product_group(cls, m: int, n: int, k: int) -> "Problem":
        """
        Product group Z_m × Z_n.
        Fiber quotient = Z_{gcd(m,n)}.
        Same parity law with gcd(m,n) as modulus.
        """
        g = gcd(m, n)
        return cls(
            name=f"Z_{m}×Z_{n} k={k}",
            group_order=m * n,
            fiber_size=g,
            k=k,
            fiber_map_desc=f"(i+j) mod gcd({m},{n}) = mod {g}",
            tags=["product", f"gcd{g}"],
            notes=(
                f"Product group. Fiber quotient Z_{g}. "
                f"Same parity law as G_{g}."
            ),
        )

    @classmethod
    def from_nonabelian(
        cls,
        group_name: str,
        group_order: int,
        normal_subgroup_name: str,
        normal_subgroup_index: int,
        k: int,
    ) -> "Problem":
        """
        Non-abelian group with normal subgroup.
        fiber_size = index of normal subgroup = |G/H|.

        Example: S_3 with normal subgroup A_3 (index 2)
        Problem.from_nonabelian("S_3", 6, "A_3", 2, k=2)
        """
        return cls(
            name=f"{group_name} / {normal_subgroup_name} k={k}",
            group_order=group_order,
            fiber_size=normal_subgroup_index,
            k=k,
            fiber_map_desc=f"sign map {group_name} → Z_{normal_subgroup_index}",
            tags=["nonabelian", group_name],
            notes=(
                f"Non-abelian group. Twisted translation = conjugation. "
                f"Same parity law as abelian case with m={normal_subgroup_index}."
            ),
        )

    @classmethod
    def inject(cls, description: dict) -> "Problem":
        """
        Inject a new domain from a plain dict description.

        Minimal required keys:
            group_order : int
            fiber_size  : int   (= |G/H|)
            k           : int

        Optional:
            name, fiber_map_desc, tags, notes, precomputed

        The engine will auto-derive all 8 weights and determine
        which known theorems apply.

        Example
        -------
        p = Problem.inject({
            "group_order": 729,
            "fiber_size": 9,
            "k": 3,
            "fiber_map_desc": "sum mod 9",
        })
        """
        return cls(
            name=description.get(
                "name",
                f"G{description['group_order']}_m{description['fiber_size']}_k{description['k']}"
            ),
            group_order=description["group_order"],
            fiber_size=description["fiber_size"],
            k=description["k"],
            fiber_map_desc=description.get("fiber_map_desc", ""),
            tags=description.get("tags", []),
            precomputed=description.get("precomputed", None),
            notes=description.get("notes", ""),
        )


# ── Domain Registry ──────────────────────────────────────────────────────────

class DomainRegistry:
    """
    Registry of known domains.
    Enables cross-domain comparison and theorem identification.
    """

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
        """
        Find domains with the same obstruction structure.
        Two domains are structurally similar if they have the same
        (h2_blocks, r_count > 0, fiber_size parity) triple.
        """
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


# Default registry with all known domains
Domain = Problem  # backwards-compatible alias

def default_registry() -> DomainRegistry:
    """Build the default registry with all known domains."""
    reg = DomainRegistry()

    # Cayley digraphs
    for m in [3, 4, 5, 6, 7, 8, 9]:
        reg.register(Problem.from_cycles(m, 3))
    for m in [4, 8]:
        reg.register(Problem.from_cycles(m, 4))

    # Product groups
    for mn in [(3,5), (6,9), (4,6), (2,4)]:
        reg.register(Problem.from_product_group(*mn, k=3))

    # Non-abelian
    reg.register(Problem.from_nonabelian("S_3", 6, "A_3", 2, k=2))
    reg.register(Problem.from_nonabelian("S_3", 6, "A_3", 2, k=3))

    # Classical domains
    reg.register(Problem(
        name="Latin Square n=5", group_order=5, fiber_size=5,
        k=1, fiber_map_desc="identity",
        tags=["latin"], notes="Cyclic: L[i][j]=(i+j)%n.",
    ))
    reg.register(Problem(
        name="Hamming(7,4)", group_order=128, fiber_size=2,
        k=8, fiber_map_desc="parity-check Z_2^7→Z_2^3",
        tags=["coding", "perfect"],
        notes="Perfect: |ball(1)|×|C|=8×16=128=2^7.",
    ))
    reg.register(Problem(
        name="Diff Set (7,3,1)", group_order=7, fiber_size=7,
        k=7, fiber_map_desc="difference a−b mod 7",
        tags=["design"],
        notes="k(k-1)=6=λ(n-1)=6.",
    ))

    return reg
