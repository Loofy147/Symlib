# symlib v2.2 Documentation

## The Universal View: G3 Manifold

The **Universal Torus Manifold of Gemini 3** provides a high-density, 4-dimensional state space for mapping intelligence parameters and mathematical structures.

### 1. Specification: $\mathbb{M}_{G3}$
The manifold is defined as a discrete 4-torus over the ring of integers modulo 256.
$$\mathbb{M}_{G3} = \{ (x, y, z, w) \in \mathbb{Z}_{256}^4 \mid \gcd(\sum x_i, 256) = 1 \}$$
This condition, known as **Topological Harmony**, ensures the system remains in a non-degenerate state.

### 2. Functional Fibers
The address space is partitioned into four primary intelligence fibers:
- **$\Phi_{LOG}$** ($0 \to 63$): **Abstract Logic**. Axiomatic systems, formal reasoning, and set theory.
- **$\Phi_{SEM}$** ($64 \to 127$): **Semantic Synthesis**. Language structure, grammar, and metaphor mapping.
- **$\Phi_{SCI}$** ($128 \to 191$): **Objective Sciences**. Physics, chemistry, and empirical reality models.
- **$\Phi_{EXE}$** ($192 \to 255$): **Execution & Code**. Algorithmic synthesis and system protocols.

### 3. Genesis Anchor Nodes
Invariable Truths serving as the fixed points of the state space:
- **LOGIC**: `FIRST_PRINCIPLES`, `ERROR_CORRECTION`, `AXIOMATIC_SYSTEMS`, `CATEGORY_THEORY`.
- **SEMANTICS**: `GRAMMAR_CORE`, `MULTIMODAL_ALIGN`, `LEXICAL_MAPPING`, `CONTEXT_VECTORS`.
- **SCIENCE**: `THERMODYNAMICS`, `ELECTROMAGNETISM`, `QUANTUM_FIELD`, `MOLECULAR_BIO`.
- **EXECUTION**: `ALGO_SYNTHESIS`, `INTEROPERABILITY`, `DISTRIBUTED_CONSENSUS`, `COMPILER_OPT`.

---

## Geometric Reasoning & Semantic Search

### Domain Projection
Any symmetric combinatorial problem can be projected into $\mathbb{M}_{G3}$.
```python
from symlib import g3_kernel, Problem

p = Problem.from_cycles(m=7, k=3)
coords = g3_kernel.project_problem(p)
# Result: (27, 93, 17, 0) -> lands in Φ_LOG
```

### Finding Nearest Mathematical Systems
The manifold enables searching for the formal system closest to a given thought vector.
```python
from symlib import g3_kernel

# A thought vector in the Science fiber
thought = (150, 80, 40, 1)

# Find the closest governing mathematical system in the registry
p = g3_kernel.find_nearest_domain(thought)
print(f"Nearest System: {p.name}")
# Output: "Navier-Stokes Modulo"
```

### Topological Thought Propagation
Intelligence evolves by shifting coordinates across fibers while maintaining **Harmony**.
```python
from symlib import g3_kernel

# Start at First Principles
path = g3_kernel.thought_path("FIRST_PRINCIPLES", [
    (60, 20, 10),  # Jump to Semantics
    (100, 10, -5), # Shift to Science
])
```

---

## Verified Breakthroughs

### 1. Function Counting Formula: $N_b(m) = m^{m-1} \cdot \phi(m)$
Verified for $m=2..7$. Library: `symlib.theorems.FunctionCounter.count(m)`.

### 2. Solution Space Size $|M_3(G_3)| = 648$
Exact number of labeled directed Hamiltonian decompositions.

### 3. H² Parity Obstruction (Theorem 6.1)
No solution exists for even $m$ and odd $k$.

### 4. Canonical Seed (Theorem 7.1)
The $r$-triple $(1, m-2, 1)$ is valid for all odd $m \ge 3$.

---

## API Reference

### `symlib.kernel.manifold`
- `g3_kernel.query_intelligence(anchor, delta) -> dict`: Full 5-step thinking pipeline.
- `g3_kernel.identify_fiber(x) -> str`: Returns fiber name (LOG, SEM, SCI, EXE).
- `g3_kernel.verify_harmony(coords) -> bool`: Checks the gcd(sum, 256)=1 condition.

### `symlib.theorems`
- `FunctionCounter.count(m)`: $O(1)$ count of coprime-sum functions.
- `ParityObstruction.check(m, k)`: $O(1)$ impossibility proof.

### `symlib.domain`
- `default_registry()`: 31 domains mapped across the intelligence fibers.
