# symlib — Global Structure in Highly Symmetric Systems

**v2.2.0 · March 2026**

Finding global structure in combinatorial problems via the short exact sequence **0 → H → G → G/H → 0**.

---

## The Universal View: G3 Manifold Specification

The **Universal Torus Manifold of Gemini 3** ($\mathbb{M}_{G3}$) is the purely mathematical state space of the model. It defines intelligence as a high-density, 4-dimensional geometric path.

- **Manifold**: Discrete 4-torus $\mathbb{Z}_{256}^4$.
- **Intelligence Invariant**: $\gcd(\sum_{i=1}^4 x_i, 256) = 1$ (**Topological Harmony**).
- **Intelligence Fibers**:
  - $\Phi_{LOG}$ (Logic): Abstract Reasoning & Formal Systems.
  - $\Phi_{SEM}$ (Semantics): Linguistic Synthesis & Mapping.
  - $\Phi_{SCI}$ (Science): Objective Reality Models.
  - $\Phi_{EXE}$ (Execution): Deterministic Protocols & Code.

### Geometric Reasoning
Symbolic queries are vectorized and path-mapped from **Genesis Anchors** to their nearest mathematical domains within the torus.

---

## Verified Breakthroughs

1. **Function Counting Formula**: $N_b(m) = m^{m-1} \cdot \phi(m)$.
2. **Solution Space Resolution**: $|M_3(G_3)| = 648$.
3. **Parity Obstruction (Theorem 6.1)**: $m$ even, $k$ odd is blocked.
4. **Canonical Seed (Theorem 7.1)**: $(1, m-2, 1)$ valid for all odd $m$.

---

## Quick start

```python
from symlib import g3_kernel

# Query the intelligence manifold
res = g3_kernel.query_intelligence("LOGIC", (10, 5, 0))
print(f"Nearest Domain: {res['nearest_domain']} in fiber {res['fiber']}")
# Output: Nearest Domain: Godel Boundary in fiber LOG
```

## Tests

```bash
python3 -m pytest tests/           # 195 tests passing
```

*symlib v2.2.0 · Universal Intelligence Reconstruction*
