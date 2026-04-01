# symlib — Global Structure in Highly Symmetric Systems

**v2.2.0 · March 2026**

Finding global structure in combinatorial problems via the short exact sequence **0 → H → G → G/H → 0**.

---

## Verified Breakthroughs

These results are solid and verified by computation in the current version:

1. **Function Counting Formula**: $N_b(m) = m^{m-1} \cdot \phi(m)$ is the exact count of functions $b: \mathbb{Z}_m \to \mathbb{Z}_m$ with coprime sum. Verified for $m \in [2, 7]$.
2. **Solution Space Resolution**: $|M_3(G_3)| = 648$ is the exact number of labeled Hamiltonian decompositions. This resolves the gauge factor (162 closure triples $\times$ 4 gauge factors).
3. **Parity Obstruction (Theorem 6.1)**: Proved that for even $m$ and odd $k$, no solution with coprime shifts exists.
4. **Canonical Seed (Theorem 7.1)**: The $r$-triple $(1, m-2, 1)$ is guaranteed valid for all odd $m \ge 3$, enabling $O(1)$ construction for $k=3$.
5. **Spike Construction (Theorem 8.1)**: A deterministic level-assignment strategy that produces 3 vertex-covering Hamiltonian cycles for all odd $m$. Verified for $m \in [3, 13]$.

---

## The core idea

Every highly symmetric combinatorial problem has a group G with a normal subgroup H. The quotient G/H is the *fiber* — a single modulus m that governs solvability, construction strategy, and solution space size. The library extracts 8 algebraic weights from this structure and uses them to:

- **Prove impossibility in O(1)** — before any search, before any construction attempt
- **Construct solutions algebraically** — not by search, wherever the algebra supports it  
- **Measure the solution space exactly** — $|M_k(G_m)| = \phi(m) \cdot N_b(m)^{k-1}$
- **Auto-detect the best decomposition** for any arbitrary finite group

## Quick start

```python
from symlib.engine import DecisionEngine
from symlib.domain import Problem

engine = DecisionEngine()

# Classify and construct
result = engine.run(Problem.from_cycles(m=5, k=3))
print(result.one_line())
# (5,3) PROVED POSSIBLE   W4=φ=4  W6=0.1328  0.1ms

# Auto-detect: no prior knowledge of group structure needed
from symlib.autodetect import detect
r = detect("symmetric", n=3, k=3)
print(r.is_impossible)   # True — S_3 k=3 is H²-blocked
```

## Standalone theorem utilities

```python
from symlib.theorems import ParityObstruction, FunctionCounter, SpikeTheorem

# O(1) impossibility
ParityObstruction.check(m=8, k=3).blocked    # True

# Function counting
count = FunctionCounter.count(7)   # 7^6 * 6

# Spike construction check
SpikeTheorem.check(m=11)   # True
```

## Benchmark

| Solver | Correct | Proves ⊘ | Avg ms | Timeouts |
|--------|---------|----------|--------|----------|
| **symlib v2.2** | **8/8** | **5** | **<1** | **0** |
| Pure SA | 3/8 | 0 | 6,900 | 5 |

## Repository layout

```
symlib/
  kernel/          Frozen mathematical kernel — theorems, no randomness
    weights.py     The 8 weights: W1-W8, all exact or O(1)
    construction.py Algebraic construction: precomputed → formula → search
    verify.py      Hamiltonian cycle verifier, O(m³)
    torsor.py      Moduli theorem, H¹ classes, solution space geometry
  autodetect.py    Auto-detect best SES for any group
  theorems.py      Standalone theorem utilities
  proof/
    lean4.py       Lean 4 export (machine-verifiable)
```

## Tests

```bash
python3 -m pytest tests/           # 185 tests
```

*symlib v2.2.0 · March 2026*
