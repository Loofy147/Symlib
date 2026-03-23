# symlib — Global Structure in Highly Symmetric Systems

**v2.1.0 · March 2026**

Finding global structure in combinatorial problems via the short exact sequence **0 → H → G → G/H → 0**.

---

## The core idea

Every highly symmetric combinatorial problem has a group G with a normal subgroup H. The quotient G/H is the *fiber* — a single modulus m that governs solvability, construction strategy, and solution space size. The library extracts 8 algebraic weights from this structure and uses them to:

- **Prove impossibility in O(1)** — before any search, before any construction attempt
- **Construct solutions algebraically** — not by search, wherever the algebra supports it  
- **Measure the solution space exactly** — |M_k(G_m)| = φ(m) × coprime_b(m)^(k−1), exact for m=3
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
r = detect("dihedral",  n=5, k=2)
print(r.is_constructible)  # True
```

## Standalone theorem utilities

```python
from symlib.theorems import ParityObstruction, CoprimeCoverage, QuotientCounter

# O(1) impossibility — applies to any symmetric system
ParityObstruction.check(m=8, k=3).blocked    # True — 3 odd tasks can't fill 8 slots

# Step-and-wrap coverage (hash tables, buffers, schedulers)
CoprimeCoverage.check(step=4, space=12).covers_all   # False — gcd(4,12)=4

# Count distinct states in symmetric system
QuotientCounter.distinct_states(12)   # 4 = φ(12)
```

## Benchmark

| Solver | Correct | Proves ⊘ | Avg ms | Timeouts |
|--------|---------|----------|--------|----------|
| **symlib v2.1** | **8/8** | **5** | **<1** | **0** |
| Pure SA | 3/8 | 0 | 6,900 | 5 |
| Brute random | 0/8 | 0 | — | 8 |

Impossible cases proved in <0.03ms. Random search times out on all of them.

## Repository layout

```
symlib/
  kernel/          Frozen mathematical kernel — theorems, no randomness
    weights.py     The 8 weights: W1-W8, all exact or O(1)
    obstruction.py H² and H³ obstruction checkers
    construction.py Algebraic construction: precomputed → formula → search
    verify.py      Hamiltonian cycle verifier, O(m³)
    torsor.py      Moduli theorem, H¹ classes, solution space geometry
    group_algebra.py Finite group representation, subgroup detection
    ses_analyzer.py SES candidate scoring and ranking
  autodetect.py    Auto-detect best SES for any group
  domain.py        Problem representation and registry
  engine.py        Decision engine: classify → construct → prove
  theorems.py      Standalone theorem utilities
  search/
    equivariant.py Group-equivariant SA with orbit moves
  proof/
    builder.py     Formal proof objects, versioned
    lean4.py       Lean 4 export (machine-verifiable)
tests/
  test_kernel.py   64 kernel tests
  test_autodetect.py  77 auto-detection tests
docs/
  DOCUMENTATION.md Full API reference (1,600+ lines)
showcase.py        85-check live implementation study
```

## Tests

```bash
python -m pytest tests/           # 180 tests
python showcase.py                # 85 live checks with real data
```


## Roadmap

- [x] v2.1.0 core mathematical kernel
- [x] Auto-detection for arbitrary finite groups
- [x] H² and H³ obstruction tower
- [x] Algebraic construction for all odd m, k=3 (`direct_formula`)
- [x] Equivariant SA with multi-orbit super-moves
- [x] Search checkpoints and CLI (v2.1.0)
- [x] Lean 4 export for specific obstructions
- [ ] General algebraic proof for Closure Lemma (any odd m)
- [ ] Formal verification of all 10 theorems in Lean 4
- [ ] Distributed search for P1 and P3 open problems
- [ ] Web-based visualization of functional graphs
## Open problems

| Problem | Status | Best known |
|---------|--------|-----------|
| P1: k=4, m=4 | OPEN | Score 230 |
| P2: m=6, k=3 | OPEN | Score 9 (depth-3 barrier confirmed) |
| P3: m=8, k=3 | OPEN | Not yet attempted at scale |
| Closure Lemma (general m) | PARTIAL | Proved for m=3, algebraic fallback for all odd m |

## Cross-domain applications

The framework governs: Cayley digraphs, Latin squares, Hamming codes,
magic squares, difference sets, non-abelian groups (S_3), product groups (ℤ_m×ℤ_n),
hash functions, circular buffers, symmetric schedulers, and configuration spaces.

See `docs/DOCUMENTATION.md` for full API reference.
