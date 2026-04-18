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

### `symlib.autodetect`

#### class `AutoDetector`

- `compare_all_k(self, group: 'FiniteGroup', k_range: 'range' = range(2, 6)) -> 'Dict[int, DetectionResult]'`
  _Run auto-detect for multiple k values on the same group.
  Returns dict k → DetectionResult.
  Useful for finding which k is most favorable for a given group._

- `detect(self, group: 'FiniteGroup', k: 'int', hint_m: 'Optional[int]' = None) -> 'DetectionResult'`
  _Core detection method — works for any FiniteGroup.

  Parameters
  ----------
  group   : FiniteGroup   The group to analyze
  k       : int           Number of arc colors
  hint_m  : int, optional  If provided, only consider SES with this fiber size

  Returns
  -------
  DetectionResult with ranked SES candidates and best choice_

- `from_cyclic(self, n: 'int', k: 'int') -> 'DetectionResult'`
  _Auto-detect SES for cyclic group Z_n.

  For prime n: Z_n has no non-trivial proper normal subgroups,
  so no internal SES decomposition exists. In this case the detector
  returns a result explaining that Z_n should be used as the FIBER
  (quotient) of a larger group, not as G itself.
  For composite n: enumerate all subgroups (all are normal)._

- `from_description(self, group_order: 'int', k: 'int', group_type: 'str' = 'cyclic', **kwargs) -> 'DetectionResult'`
  _Auto-detect from a high-level description.

  Parameters
  ----------
  group_order : int    |G|
  k           : int    Number of arc colors
  group_type  : str    "cyclic", "product", "dihedral", "symmetric"
  **kwargs           Additional parameters for specific group types

  Examples
  --------
  from_description(12, k=3, group_type="product", m=4, n=3)
  from_description(10, k=3, group_type="dihedral", n=5)
  from_description(6,  k=2, group_type="symmetric", n=3)_

- `from_dihedral(self, n: 'int', k: 'int') -> 'DetectionResult'`
  _Auto-detect SES for dihedral group D_n (order 2n)._

- `from_product(self, m: 'int', n: 'int', k: 'int') -> 'DetectionResult'`
  _Auto-detect SES for Z_m × Z_n._

- `from_symmetric(self, n: 'int', k: 'int') -> 'DetectionResult'`
  _Auto-detect SES for symmetric group S_n._

- `from_table(self, table: 'List[List[int]]', k: 'int', name: 'str' = 'custom') -> 'DetectionResult'`
  _Auto-detect SES from a raw Cayley table.

  Parameters
  ----------
  table : list[list[int]]   Multiplication table. table[a][b] = a*b.
  k     : int               Number of arc colors.
  name  : str               Optional group name._

- `from_triple_product(self, m: 'int', k: 'int') -> 'DetectionResult'`
  _Auto-detect SES for Z_m³ (the Cayley digraph group)._

- `scan_cyclic_range(self, n_range: 'range', k: 'int') -> 'List[DetectionResult]'`
  _Run auto-detect on Z_n for n in n_range.
  Returns results sorted by quality (best first)._


#### class `DetectionResult`

- `classify(self)`
  _Run the full engine on the detected problem._

- `explain(self) -> 'str'`
- `to_problem(self) -> 'Problem'`

#### function `detect(group_type: 'str', k: 'int', **kwargs) -> 'DetectionResult'`
_Convenience function for auto-detection.

Parameters
----------
group_type : str   "cyclic", "product", "dihedral", "symmetric",
                   "triple_product", "table", "description"
k          : int   Number of arc colors
**kwargs          Group-specific parameters

Examples
--------
detect("cyclic", n=7, k=3)
detect("product", m=4, n=6, k=3)
detect("dihedral", n=5, k=3)
detect("symmetric", n=3, k=2)
detect("triple_product", m=5, k=3)
detect("table", table=[[0,1,2],[1,2,0],[2,0,1]], k=3)_

### `symlib.domain`

#### class `Domain`

- `from_cycles(m: 'int', k: 'int') -> "'Problem'"`
- `from_nonabelian(group_name: 'str', group_order: 'int', normal_subgroup_name: 'str', normal_subgroup_index: 'int', k: 'int') -> "'Problem'"`
- `from_product_group(m: 'int', n: 'int', k: 'int') -> "'Problem'"`
- `inject(description: 'dict') -> "'Problem'"`
- `is_constructible(self) -> 'bool'`
- `is_feasible(self) -> 'bool'`
- `summary(self) -> 'str'`

#### class `DomainRegistry`

- `all(self) -> 'list[Problem]'`
- `by_fiber_size(self, m: 'int') -> 'list[Problem]'`
- `by_tag(self, tag: 'str') -> 'list[Problem]'`
- `find_similar(self, p: 'Problem') -> 'list[Problem]'`
- `get(self, name: 'str') -> 'Optional[Problem]'`
- `register(self, p: 'Problem') -> "'DomainRegistry'"`

#### class `Problem`

- `from_cycles(m: 'int', k: 'int') -> "'Problem'"`
- `from_nonabelian(group_name: 'str', group_order: 'int', normal_subgroup_name: 'str', normal_subgroup_index: 'int', k: 'int') -> "'Problem'"`
- `from_product_group(m: 'int', n: 'int', k: 'int') -> "'Problem'"`
- `inject(description: 'dict') -> "'Problem'"`
- `is_constructible(self) -> 'bool'`
- `is_feasible(self) -> 'bool'`
- `summary(self) -> 'str'`

#### function `default_registry() -> 'DomainRegistry'`

### `symlib.engine`

#### class `ClassificationResult`

- `explain(self) -> 'str'`
- `one_line(self) -> 'str'`

#### class `DecisionEngine`

- `batch(self, problems: 'list[Problem]', **kwargs) -> 'list[ClassificationResult]'`
  _Classify multiple problems._

- `print_table(self, results: 'list[ClassificationResult]') -> 'None'`
  _Print a compact results table._

- `run(self, problem: 'Problem', attempt_construction: 'bool' = True, max_iters: 'int' = 500000) -> 'ClassificationResult'`
  _Classify and optionally construct a solution for problem.

  Parameters
  ----------
  problem                : Problem
  attempt_construction   : bool    Try to find a solution (default True)
  max_iters              : int     Max iterations for level search

  Returns
  -------
  ClassificationResult_


#### class `Status`


#### function `classify(problem: 'Problem') -> 'ClassificationResult'`
_Classify a problem — check obstruction, measure solution space.
Does not attempt construction. O(1) for impossible cases._

#### function `construct(problem: 'Problem', max_iters: 'int' = 500000) -> 'Optional[Sigma]'`
_Construct a solution for problem, or return None if impossible/open._

#### function `explain(problem: 'Problem') -> 'str'`
_Full explanation of a problem — weights, obstruction, torsor structure._

### `symlib.kernel.construction`

#### class `ConstructionEngine`

- `closure_lemma_b(self, b_funcs: 'List[Dict[int, int]]') -> 'Optional[Dict[int, int]]'`
  _Apply the Closure Lemma: given b_0,...,b_{k-2}, derive b_{k-1}._

- `construct(self, max_level_iters: 'int' = 500000) -> 'Optional[Sigma]'`
- `construction_level(self) -> 'str'`

#### class `LevelMeta`


### `symlib.kernel.group_algebra`

#### class `FiniteGroup`

- `all_subgroups(self) -> 'List[FrozenSet[int]]'`
  _Enumerate all subgroups of G using Lagrange's theorem.
  Only tests generating sets from cyclic subgroups (sufficient for
  groups of order ≤ 100 or so; exact for abelian groups of any order)._

- `conjugacy_classes(self) -> 'List[FrozenSet[int]]'`
  _Conjugacy classes of G._

- `conjugate(self, h: 'int', g: 'int') -> 'int'`
  _Conjugate h by g: g * h * g⁻¹._

- `cosets(self, subgroup: 'FrozenSet[int]') -> 'List[FrozenSet[int]]'`
  _Left cosets of subgroup H in G._

- `element_order(self, g: 'int') -> 'int'`
  _Multiplicative order of element g._

- `inv(self, a: 'int') -> 'int'`
  _Group inverse of a._

- `is_abelian(self) -> 'bool'`
  _Check if G is abelian._

- `is_normal(self, subgroup: 'FrozenSet[int]') -> 'bool'`
  _Check if subgroup H is normal in G._

- `mul(self, a: 'int', b: 'int') -> 'int'`
  _Group multiplication: a * b._

- `normal_subgroups(self) -> 'List[FrozenSet[int]]'`
  _All normal subgroups of G, sorted by order._

- `quotient_order(self, subgroup: 'FrozenSet[int]') -> 'int'`
  _Order of G/H = |G| / |H|._

- `subgroup_generated_by(self, generators: 'List[int]') -> 'FrozenSet[int]'`
  _Generate the subgroup from a list of generators._

- `summary(self) -> 'str'`

#### class `GroupElement`


#### function `alternating_group_3() -> 'FiniteGroup'`
_A_3 — alternating group on 3 elements (= Z_3)._

#### function `cyclic_group(n: 'int') -> 'FiniteGroup'`
_Z_n — the cyclic group of order n.
Elements: 0, 1, ..., n-1.  Multiplication: addition mod n._

#### function `dihedral_group(n: 'int') -> 'FiniteGroup'`
_D_n — dihedral group of order 2n (symmetries of regular n-gon).
Elements: r^i (rotations) for i=0..n-1, and s*r^i (reflections).
Encoding: rotation i → i, reflection i → n+i.
Multiplication: r^a * r^b = r^(a+b mod n)
                r^a * s*r^b = s * r^(b-a mod n)
                s*r^a * r^b = s * r^(a+b mod n)
                s*r^a * s*r^b = r^(b-a mod n)_

#### function `product_group(m: 'int', n: 'int') -> 'FiniteGroup'`
_Z_m × Z_n — direct product of cyclic groups.
Elements: (0,0), (0,1), ..., (m-1, n-1) indexed as i*n + j._

#### function `symmetric_group(n: 'int') -> 'FiniteGroup'`
_S_n — symmetric group on n elements.
Elements are permutations represented as tuples.
Only practical for n ≤ 5 (|S_5| = 120)._

#### function `triple_product(m: 'int') -> 'FiniteGroup'`
_Z_m³ — the group G_m used in Cayley digraph problems.
Elements: (i,j,k) for i,j,k ∈ Z_m.
Multiplication: componentwise addition mod m._

### `symlib.kernel.manifold`

#### class `UniversalG3Manifold`

- `find_nearest_domain(self, coords: 'Tuple[int, int, int, int]') -> 'Optional[Problem]'`
  _Finds the mathematical system closest to the given coordinate on the 4-torus._

- `generate_thought_vector(self, anchor_key: 'str', intent_delta: 'Tuple[int, int, int]') -> 'Tuple[int, int, int, int]'`
  _Maps a symbolic intent into a geometric transformation._

- `identify_fiber(self, x: 'int') -> 'str'`
  _Identify which intelligence fiber a coordinate belongs to._

- `populate_from_registry(self, registry: 'Any')`
  _Pre-calculates coordinates for all domains in a registry._

- `project_problem(self, p: 'Problem') -> 'Tuple[int, int, int, int]'`
  _Maps a Problem into the manifold based on its domain tags._

- `query_intelligence(self, anchor_key: 'str', intent_delta: 'Tuple[int, int, int]') -> 'dict'`
  _Runs the 5-step Topological Thinking pipeline._

- `solve_closure(self, x: 'int', y: 'int', z: 'int') -> 'int'`
  _Completes the 4th dimension for parity harmony._

- `thought_path(self, start_anchor: 'str', deltas: 'List[Tuple[int, int, int]]') -> 'List[Tuple[int, int, int, int]]'`
  _Generates a sequence of thoughts maintaining topological harmony._

- `verify_harmony(self, coords: 'Tuple[int, int, int, int]') -> 'bool'`
  _Verify the Coprimality Condition: gcd(sum, m) = 1._


### `symlib.kernel.obstruction`

#### class `ObstructionChecker`

- `check(self) -> 'ObstructionResult'`
  _Run full obstruction tower. Returns first obstruction found.
  Currently checks H² (parity) then H³ (fiber-uniform for k=4, m=4)._

- `coverage_check(step: 'int', space_size: 'int') -> 'ObstructionResult'`
  _Simplified single-cycle check for common programming use.

  Is this step size valid for full coverage of a circular space?

  Examples
  --------
  # Hash table: does stride 7 cover all 16 buckets?
  coverage_check(7, 16)  # → blocked (gcd(7,16)=1, actually fine)
  coverage_check(4, 16)  # → blocked (gcd(4,16)=4 → only 4 buckets)

  # Scheduler: does worker step 3 cover 9 task slots?
  coverage_check(3, 9)   # → blocked (gcd(3,9)=3 → only 3 slots)
  coverage_check(2, 9)   # → no obstruction_

- `h2_parity(self) -> 'ObstructionResult'`
  _Theorem 6.1 — Parity Obstruction.

  H²(Z_2, Z/2) = Z/2. The obstruction class γ₂ is nontrivial
  when: m is even AND k is odd AND all coprime-to-m elements are odd.

  In that case, any k-tuple of coprime elements sums to an odd number, which means no column-uniform construction (r-tuple) can exist.
  which cannot equal m (even). Contradiction.

  O(1) — no search, no construction attempt needed._

- `h3_fiber_uniform(self) -> 'ObstructionResult'`
  _Theorem 10.1 — Fiber-Uniform Impossibility (k=4, m=4).

  Even though H² is absent for (m=4, k=4), no fiber-uniform σ works.
  This is a secondary obstruction living at H³ level.

  Currently proved only for (m=4, k=4) by exhaustive check of
  24^4 = 331,776 cases. General algebraic proof is open.

  Returns obstruction only for the proved case._

- `single_cycle_check(r: 'int', b_sum: 'int', m: 'int') -> 'ObstructionResult'`
  _Theorem 5.1 — Single-Cycle Condition (standalone).

  A twisted translation Q with step r and b-sum s over Z_m
  generates a full m²-cycle if and only if:
      gcd(r, m) = 1  AND  gcd(s mod m, m) = 1

  STANDALONE: applies to any step-and-wrap system.

  Parameters
  ----------
  r     : int   Step size (stride)
  b_sum : int   Sum of translation offsets mod m
  m     : int   Modulus (space size)

  Examples
  --------
  # Does circular buffer of size 12 with step 5 cover all slots?
  ObstructionChecker.single_cycle_check(r=5, b_sum=1, m=12)
  # → blocked=False (gcd(5,12)=1, gcd(1,12)=1 → full coverage)

  # Does step 4 cover all 12 slots?
  ObstructionChecker.single_cycle_check(r=4, b_sum=1, m=12)
  # → blocked=True (gcd(4,12)=4 ≠ 1 → stuck in sub-cycle of size 3)_


#### class `ObstructionResult`

- `explain(self) -> 'str'`
- `to_lean4(self) -> 'str'`
  _Export this specific obstruction as a Lean 4 proof skeleton._


### `symlib.kernel.ses_analyzer`

#### class `SESAnalysis`

- `explain(self) -> 'str'`
- `has_constructible(self) -> 'bool'`
- `is_provably_impossible(self) -> 'bool'`

#### class `SESAnalyzer`

- `analyze(self) -> 'SESAnalysis'`
- `best_for_construction(self) -> 'Optional[SESCandidate]'`
- `best_for_impossibility(self) -> 'Optional[SESCandidate]'`

#### class `SESCandidate`

- `is_trivial(self) -> 'bool'`
- `is_useful(self) -> 'bool'`
- `is_whole_group(self) -> 'bool'`
- `one_line(self) -> 'str'`

### `symlib.kernel.torsor`

#### class `TorsorInfo`

- `explain(self) -> 'str'`

#### class `TorsorStructure`

- `analyse(self) -> 'TorsorInfo'`
  _Return full torsor analysis for (m, k)._

- `coboundaries(self) -> 'set'`
  _Compute all coboundaries δf: Z_m → Z_m.
  These generate the gauge group acting on M_k(G_m).

  A coboundary is δf[j] = f[(j+1) % m] - f[j]  (mod m)
  for any function f: Z_m → Z_m.

  Returns
  -------
  set of tuples, each a coboundary δf._

- `gauge_transform(self, sigma: 'Dict', coboundary: 'Tuple[int, ...]') -> 'Dict'`
  _Apply a gauge transformation to sigma, producing another valid solution.

  A coboundary δ acts on a level table by shifting b-functions:
      b_new[j] = b_old[j] + δ[j]  (mod m)

  This preserves the coprimality constraint and the fiber bijection,
  so the result is another valid solution in the same torsor.

  Parameters
  ----------
  sigma       : dict   A valid sigma map
  coboundary  : tuple  A coboundary δ: Z_m → Z_m

  Returns
  -------
  dict  Another valid sigma map (not verified here — caller should verify)_

- `h1_classes(self) -> 'dict'`
  _Compute H¹(Z_m, coprime-sum) by explicit orbit enumeration.

  Returns
  -------
  dict: representative → list of cohomologous cocycles
        len(result) == φ(m)  [verified for m=3,4,5]_

- `solution_count_estimate(self) -> 'Tuple[int, bool]'`
  _Return (count, is_exact) for the solution space size.
  is_exact is True only for m=3 (Closure Lemma proved)._


### `symlib.kernel.verify`

#### function `get_shifts(k: 'int') -> 'Tuple[Tuple[int, ...], ...]'`
_Generate k standard basis shifts for Z_m^k (usually k=3)._

#### function `score_sigma(sigma_list: 'list[int]', arc_s: 'list', pa: 'list', n: 'int', k: 'int' = 3) -> 'int'`
_Compute the SA score for an integer-array sigma.
Score = sum(components_c - 1) for each color c.
Score 0 means valid solution._

#### function `verify_and_diagnose(sigma: 'Sigma', m: 'int', k: 'int' = 3) -> 'dict'`
_Verify sigma and return detailed diagnostics on failure._

#### function `verify_sigma(sigma: 'Sigma', m: 'int', k: 'int' = 3) -> 'bool'`
_Verify σ: Z_m^k → S_k yields k directed Hamiltonian cycles.

Parameters
----------
sigma : dict  {v: (p0,p1,...,pk-1)} where p is a permutation of {0,1,...,k-1}
m     : int   Fiber size. Vertex set is Z_m^k.
k     : int   Dimension and number of colors.

Returns
-------
True iff sigma is a valid Hamiltonian decomposition of G_m,k._

### `symlib.kernel.weights`

#### class `Weights`

- `as_dict(self) -> 'dict'`
- `summary(self) -> 'str'`

#### function `coprime_elements(m: 'int') -> 'tuple[int, ...]'`

#### function `fast_phi(n: 'int') -> 'int'`
_Euler totient function via prime factorization._

#### function `phi(m: 'int') -> 'int'`

### `symlib.proof.builder`

#### class `Proof`

- `to_dict(self) -> 'dict'`
- `to_text(self) -> 'str'`
  _Human-readable proof text._


#### class `ProofBuilder`

- `from_weights(self, w: 'Weights', solution=None) -> 'Proof'`
  _Build the appropriate proof given weights and optionally a solution._

- `theorem_51(self) -> 'Proof'`
  _Standalone Theorem 5.1 — Single-Cycle Condition._

- `theorem_61(self) -> 'Proof'`
  _Standalone Theorem 6.1 — Parity Obstruction._

- `w4_correction(self) -> 'Proof'`
  _The W4 correction — φ(m) not m^m._


### `symlib.proof.lean4`

#### class `Lean4Exporter`

- `export_all(self) -> 'str'`
  _Export all theorems as a single Lean 4 file._

- `export_moduli_theorem(self) -> 'str'`
- `export_nb_formula(self) -> 'str'`
- `export_parity_obstruction(self) -> 'str'`
- `export_proof(self, p: 'Proof') -> 'str'`
  _Export a single Proof object to Lean 4 comment block and skeleton._

- `export_single_cycle(self) -> 'str'`
- `export_spike_theorem(self) -> 'str'`
- `save_all(self, path: 'str') -> 'None'`
  _Save all theorems to a Lean 4 file._


### `symlib.search.cli`

#### function `main()`

### `symlib.search.equivariant`

#### function `_build_sa_tables(m: 'int', k: 'int' = 3)`
_Build arc-successor and permutation-arc tables for G_m,k._

#### function `_parallel_worker(args)`
_Module-level worker for parallel SA._

#### function `build_subgroup_orbits(m: 'int', k: 'int' = 3) -> 'Dict[int, List[List[int]]]'`
_Find orbits of Z_m^k vertices under Z_p subgroup actions for p | m.
Returns {p: [list_of_orbits]}._

#### function `load_checkpoint(path: 'str') -> 'Optional[Dict[str, Any]]'`
_Load search state from a JSON file._

#### function `prime_factors(n: 'int') -> 'List[int]'`
_Return distinct prime factors of n._

#### function `run_equivariant_sa(m: 'int', k: 'int' = 3, seed: 'int' = 0, max_iter: 'int' = 5000000, T_init: 'float' = 3.0, T_min: 'float' = 0.003, p_orbit: 'float' = 0.15, p_orbit_full: 'float' = 0.05, p_super: 'float' = 0.02, initial_sigma: 'Optional[List[int]]' = None, verbose: 'bool' = False, report_n: 'int' = 500000, checkpoint_path: 'Optional[str]' = None, checkpoint_n: 'int' = 1000000) -> 'Tuple[Optional[Sigma], dict]'`
_Equivariant SA for G_m,k._

#### function `run_parallel_equivariant_sa(m: 'int', k: 'int' = 3, seeds: 'List[int]' = [0], max_iter: 'int' = 5000000, T_init: 'float' = 3.0, T_min: 'float' = 0.003, p_orbit: 'float' = 0.15) -> 'Tuple[Optional[Sigma], List[dict]]'`
_Run equivariant SA across multiple seeds in parallel._

#### function `save_checkpoint(path: 'str', m: 'int', k: 'int', sigma_list: 'List[int]', stats: 'Dict[str, Any]')`
_Save search state to a JSON file._

### `symlib.search.viz`

#### function `export_to_dot(sigma: 'Sigma', m: 'int', colors: 'List[int]' = [0, 1, 2]) -> 'str'`
_Export the functional graphs of selected colors to DOT format._

#### function `export_to_json(sigma: 'Sigma', m: 'int') -> 'str'`
_Export the solution structure to a simple JSON for web-based visualization._

#### function `save_viz(sigma: 'Sigma', m: 'int', path: 'str')`
_Save visualization data to file._

### `symlib.theorems`

#### class `CanonicalSeed`

- `for_odd_m(m: 'int') -> 'Optional[Tuple[int, ...]]'`
- `verify(seed: 'Tuple[int, ...]', m: 'int') -> 'bool'`
  _Verify a seed is valid for fiber size m._


#### class `CoprimeCoverage`

- `check(step: 'int', space: 'int') -> 'CoverageResult'`
- `smallest_valid_step(space: 'int') -> 'int'`
  _Return the smallest step giving full coverage._

- `valid_steps(space: 'int') -> 'List[int]'`
  _Return all step sizes that give full coverage of space._


#### class `CoverageResult`

- `coverage_fraction(self) -> 'float'`

#### class `DepthBarrierAnalyzer`

- `analyze(m: 'int') -> 'dict'`

#### class `FunctionCounter`

- `count(m: 'int') -> 'int'`
  _Return N_b(m)._


#### class `ObstructionResult`

- `to_lean4(self) -> 'str'`
  _Export this result as a Lean 4 theorem claim._


#### class `ParityObstruction`

- `check(m: 'int', k: 'int') -> 'ObstructionResult'`
- `check_batch(problems: 'List[Tuple[int, int]]') -> 'dict'`
  _Check multiple (m, k) pairs at once._


#### class `QuotientCounter`

- `distinct_states(m: 'int') -> 'int'`
- `enumeration_warning(m: 'int', k: 'int') -> 'Optional[str]'`
- `raw_vs_distinct(m: 'int') -> 'dict'`

#### class `SpikeTheorem`

- `check(m: 'int') -> 'bool'`

#### class `TorsorEstimate`

- `estimate(m: 'int', k: 'int') -> 'dict'`
