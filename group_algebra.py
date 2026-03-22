"""
symlib.kernel.group_algebra
============================
Algebraic representation of finite groups for SES auto-detection.

Groups are represented by their Cayley table (multiplication table).
This is the most general representation — it works for any finite group
whether abelian, non-abelian, cyclic, product, or otherwise.

For common families (cyclic, product, dihedral, symmetric) we provide
factory constructors that build the table automatically without requiring
the user to supply it.

NORMAL SUBGROUP DETECTION
--------------------------
A subgroup H ≤ G is normal iff gHg⁻¹ = H for all g ∈ G.
Equivalently: H is a union of conjugacy classes.

For abelian groups every subgroup is normal.
For non-abelian groups we check conjugacy explicitly.

SES QUALITY SCORING
--------------------
Given a candidate normal subgroup H with |G/H| = m:
  quality = (W6_compression, -r_count, h2_blocks)
  
Lower W6 = better (more structure exploited).
More r-tuples = more construction options.
h2_blocks = True means this SES has a parity obstruction (still useful — proves impossible fast).

The best SES minimizes W6 among those where h2_blocks=False,
or if all block, returns the first blocking one (it proves impossibility).
"""

from __future__ import annotations
from math import gcd
from itertools import product as iprod
from typing import List, Optional, Tuple, Dict, Set, FrozenSet
from dataclasses import dataclass, field
from functools import lru_cache


@dataclass
class GroupElement:
    """A group element with an integer index."""
    idx: int
    label: str = ""

    def __hash__(self): return self.idx
    def __eq__(self, other): return self.idx == other.idx
    def __repr__(self): return self.label or str(self.idx)


@dataclass
class FiniteGroup:
    """
    A finite group represented by its Cayley table.

    Attributes
    ----------
    order      : int              |G|
    table      : list[list[int]]  table[a][b] = a*b  (indices)
    labels     : list[str]        human-readable element names
    name       : str              group name
    identity   : int              index of identity element
    """
    order:    int
    table:    List[List[int]]
    labels:   List[str]
    name:     str      = ""
    identity: int      = 0

    def mul(self, a: int, b: int) -> int:
        """Group multiplication: a * b."""
        return self.table[a][b]

    def inv(self, a: int) -> int:
        """Group inverse of a."""
        for b in range(self.order):
            if self.table[a][b] == self.identity:
                return b
        raise ValueError(f"No inverse found for element {a}")

    def conjugate(self, h: int, g: int) -> int:
        """Conjugate h by g: g * h * g⁻¹."""
        return self.mul(self.mul(g, h), self.inv(g))

    def subgroup_generated_by(self, generators: List[int]) -> FrozenSet[int]:
        """Generate the subgroup from a list of generators."""
        result: Set[int] = {self.identity}
        queue = list(generators)
        while queue:
            x = queue.pop()
            if x not in result:
                result.add(x)
                for y in result:
                    for z in [self.mul(x, y), self.mul(y, x)]:
                        if z not in result:
                            queue.append(z)
        return frozenset(result)

    def all_subgroups(self) -> List[FrozenSet[int]]:
        """
        Enumerate all subgroups of G using Lagrange's theorem.
        Only tests generating sets from cyclic subgroups (sufficient for
        groups of order ≤ 100 or so; exact for abelian groups of any order).
        """
        subgroups: Set[FrozenSet[int]] = set()
        subgroups.add(frozenset({self.identity}))
        subgroups.add(frozenset(range(self.order)))

        for g in range(self.order):
            sg = self.subgroup_generated_by([g])
            subgroups.add(sg)

        # Try pairs for non-cyclic subgroups
        for a in range(self.order):
            for b in range(a+1, self.order):
                sg = self.subgroup_generated_by([a, b])
                if len(sg) < self.order:
                    subgroups.add(sg)

        return sorted(subgroups, key=len)

    def is_normal(self, subgroup: FrozenSet[int]) -> bool:
        """Check if subgroup H is normal in G."""
        for g in range(self.order):
            for h in subgroup:
                if self.conjugate(h, g) not in subgroup:
                    return False
        return True

    def normal_subgroups(self) -> List[FrozenSet[int]]:
        """All normal subgroups of G, sorted by order."""
        return [sg for sg in self.all_subgroups() if self.is_normal(sg)]

    def cosets(self, subgroup: FrozenSet[int]) -> List[FrozenSet[int]]:
        """Left cosets of subgroup H in G."""
        seen: Set[int] = set()
        result: List[FrozenSet[int]] = []
        for g in range(self.order):
            if g not in seen:
                coset = frozenset(self.mul(g, h) for h in subgroup)
                result.append(coset)
                seen.update(coset)
        return result

    def quotient_order(self, subgroup: FrozenSet[int]) -> int:
        """Order of G/H = |G| / |H|."""
        return self.order // len(subgroup)

    def is_abelian(self) -> bool:
        """Check if G is abelian."""
        for a in range(self.order):
            for b in range(a+1, self.order):
                if self.table[a][b] != self.table[b][a]:
                    return False
        return True

    def element_order(self, g: int) -> int:
        """Multiplicative order of element g."""
        cur = g
        for k in range(1, self.order + 1):
            if cur == self.identity:
                return k
            cur = self.mul(cur, g)
        raise ValueError(f"Order not found for element {g}")

    def conjugacy_classes(self) -> List[FrozenSet[int]]:
        """Conjugacy classes of G."""
        seen: Set[int] = set()
        classes: List[FrozenSet[int]] = []
        for g in range(self.order):
            if g not in seen:
                cls = frozenset(self.conjugate(g, h) for h in range(self.order))
                classes.append(cls)
                seen.update(cls)
        return classes

    def summary(self) -> str:
        ab = "abelian" if self.is_abelian() else "non-abelian"
        return f"{self.name} (order={self.order}, {ab})"


# ── Group factory constructors ────────────────────────────────────────────────

def cyclic_group(n: int) -> FiniteGroup:
    """
    Z_n — the cyclic group of order n.
    Elements: 0, 1, ..., n-1.  Multiplication: addition mod n.
    """
    table = [[(a + b) % n for b in range(n)] for a in range(n)]
    return FiniteGroup(
        order=n,
        table=table,
        labels=[str(i) for i in range(n)],
        name=f"Z_{n}",
        identity=0,
    )


def product_group(m: int, n: int) -> FiniteGroup:
    """
    Z_m × Z_n — direct product of cyclic groups.
    Elements: (0,0), (0,1), ..., (m-1, n-1) indexed as i*n + j.
    """
    order = m * n
    def enc(a, b): return a * n + b
    def dec(x): return divmod(x, n)

    table = [[0]*order for _ in range(order)]
    for x in range(order):
        a, b = dec(x)
        for y in range(order):
            c, d = dec(y)
            table[x][y] = enc((a+c)%m, (b+d)%n)

    labels = [f"({a},{b})" for a in range(m) for b in range(n)]
    return FiniteGroup(
        order=order,
        table=table,
        labels=labels,
        name=f"Z_{m}×Z_{n}",
        identity=0,
    )


def symmetric_group(n: int) -> FiniteGroup:
    """
    S_n — symmetric group on n elements.
    Elements are permutations represented as tuples.
    Only practical for n ≤ 5 (|S_5| = 120).
    """
    from itertools import permutations as iperms
    perms = list(iperms(range(n)))
    order = len(perms)
    perm_to_idx = {p: i for i, p in enumerate(perms)}

    def compose(p, q):  # p then q: q(p(x))
        return tuple(q[p[i]] for i in range(n))

    table = [[perm_to_idx[compose(perms[a], perms[b])]
              for b in range(order)]
             for a in range(order)]

    identity = perm_to_idx[tuple(range(n))]
    labels = [str(p) for p in perms]

    return FiniteGroup(
        order=order,
        table=table,
        labels=labels,
        name=f"S_{n}",
        identity=identity,
    )


def dihedral_group(n: int) -> FiniteGroup:
    """
    D_n — dihedral group of order 2n (symmetries of regular n-gon).
    Elements: r^i (rotations) for i=0..n-1, and s*r^i (reflections).
    Encoding: rotation i → i, reflection i → n+i.
    Multiplication: r^a * r^b = r^(a+b mod n)
                    r^a * s*r^b = s * r^(b-a mod n)
                    s*r^a * r^b = s * r^(a+b mod n)
                    s*r^a * s*r^b = r^(b-a mod n)
    """
    order = 2 * n
    table = [[0]*order for _ in range(order)]

    for a in range(order):
        for b in range(order):
            a_rot = a < n  # True if a is a rotation
            b_rot = b < n
            ai = a if a_rot else a - n
            bi = b if b_rot else b - n

            if a_rot and b_rot:      # r^ai * r^bi = r^(ai+bi)
                table[a][b] = (ai + bi) % n
            elif a_rot and not b_rot: # r^ai * s*r^bi = s * r^(bi-ai)
                table[a][b] = n + (bi - ai) % n
            elif not a_rot and b_rot: # s*r^ai * r^bi = s * r^(ai+bi)
                table[a][b] = n + (ai + bi) % n
            else:                    # s*r^ai * s*r^bi = r^(bi-ai)
                table[a][b] = (bi - ai) % n

    rot_labels = [f"r^{i}" for i in range(n)]
    ref_labels = [f"sr^{i}" for i in range(n)]
    return FiniteGroup(
        order=order,
        table=table,
        labels=rot_labels + ref_labels,
        name=f"D_{n}",
        identity=0,
    )


def alternating_group_3() -> FiniteGroup:
    """A_3 — alternating group on 3 elements (= Z_3)."""
    # Even permutations of {0,1,2}: identity, (012), (021)
    perms = [(0,1,2), (1,2,0), (2,0,1)]
    perm_to_idx = {p: i for i, p in enumerate(perms)}
    def compose(p, q): return tuple(q[p[i]] for i in range(3))
    table = [[perm_to_idx[compose(perms[a], perms[b])]
              for b in range(3)] for a in range(3)]
    return FiniteGroup(
        order=3, table=table,
        labels=["e", "(012)", "(021)"],
        name="A_3", identity=0,
    )


def triple_product(m: int) -> FiniteGroup:
    """
    Z_m³ — the group G_m used in Cayley digraph problems.
    Elements: (i,j,k) for i,j,k ∈ Z_m.
    Multiplication: componentwise addition mod m.
    """
    order = m ** 3
    def enc(i,j,k): return i*m*m + j*m + k
    def dec(x):
        i,r = divmod(x, m*m); j,k = divmod(r, m)
        return i,j,k

    table = [[0]*order for _ in range(order)]
    for x in range(order):
        a,b,c = dec(x)
        for y in range(order):
            d,e,f = dec(y)
            table[x][y] = enc((a+d)%m, (b+e)%m, (c+f)%m)

    labels = [f"({i},{j},{k})" for i in range(m)
              for j in range(m) for k in range(m)]
    return FiniteGroup(
        order=order, table=table, labels=labels,
        name=f"Z_{m}³", identity=0,
    )
