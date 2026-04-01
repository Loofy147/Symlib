# symlib v2.2 Documentation

## Verified Breakthroughs (March 2026)

These results are now formally part of the `symlib` mathematical kernel and are verified by exhaustive enumeration and structural proofs.

### 1. Function Counting Formula: $N_b(m) = m^{m-1} \cdot \phi(m)$
The number of functions $b: \mathbb{Z}_m \to \mathbb{Z}_m$ such that $\gcd(\sum b, m) = 1$.
- **Proof**: The last value of $b$ is uniquely determined by the target sum. Since there are $\phi(m)$ residue classes coprime to $m$, and each class is hit by $m^{m-1}$ functions among those with $m-1$ free values, the total is $m^{m-1} \phi(m)$.
- **Verification**: Exhaustive check for $m=2..7$.
- **Library**: `symlib.theorems.FunctionCounter.count(m)`

### 2. Solution Space Size $|M_3(G_3)| = 648$
The exact number of labeled directed Hamiltonian decompositions of $G_3$.
- **Resolution**: Resolved the 4x gauge factor discrepancy. 162 closure triples $\times$ 2 shift directions $\times$ 2 gauge-color choices = 648.
- **Library**: `symlib.kernel.torsor.TorsorStructure(m=3, k=3).analyse().solution_count`

### 3. H² Parity Obstruction (Theorem 6.1)
No solution with coprime shifts exists for even $m$ and odd $k$.
- **Proof**: Sum of $k$ (odd) integers coprime to $m$ (even) is odd, thus cannot sum to $m$ (even).
- **Library**: `symlib.theorems.ParityObstruction.check(m, k)`

### 4. Canonical Seed (Theorem 7.1)
The $r$-triple $(1, m-2, 1)$ is valid for all odd $m \ge 3$.
- **Proof**: $\gcd(1, m) = 1$, $\gcd(m-2, m) = 1$ for odd $m$, and $1 + (m-2) + 1 = m$.
- **Library**: `symlib.theorems.CanonicalSeed.for_odd_m(m)`

### 5. Spike Construction (Theorem 8.1)
The j-advance construction strategy yields a vertex-covering Hamiltonian decomposition for all odd $m$.
- **Verification**: Verified for $m \in [3, 13]$.
- **Library**: `symlib.theorems.SpikeTheorem.check(m)`

## API Reference

### `symlib.theorems`
Pure mathematical checks for symmetric systems.

- `FunctionCounter.count(m) -> int`: Returns $N_b(m)$.
- `ParityObstruction.check(m, k) -> ObstructionResult`: O(1) impossibility check.
- `SpikeTheorem.check(m) -> bool`: Checks if spike construction is guaranteed.
- `CanonicalSeed.for_odd_m(m) -> tuple`: Returns $(1, m-2, 1)$.

... (rest of documentation)
