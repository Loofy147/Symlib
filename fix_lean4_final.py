import re

with open('symlib/proof/lean4.py', 'r') as f:
    content = f.read()

# Replace those methods with correctly indented versions
methods = [
    "export_nb_formula",
    "export_parity_obstruction",
    "export_single_cycle",
    "export_moduli_theorem",
    "export_spike_theorem"
]

def get_method_body(name):
    if name == "export_nb_formula":
        return r'''    def export_nb_formula(self) -> str:
        return '''
/--
Theorem 4.1: N_b(m) = m^(m-1) * \phi(m).
The number of functions b: Z_m -> Z_m with coprime sum.
-/
theorem nb_formula (m : \mathbb{N}) (h_m_pos : m > 0) :
  let functions := {b : Fin m \to Fin m | Nat.gcd (\sum i, (b i).val) m = 1}
  functions.ncard = m^(m-1) * Nat.totient m :=
by
  -- Consider the map f: (Fin m \to Fin m) \to Fin m defined by (\sum b_i) mod m.
  -- This map is surjective and each fiber has size m^(m-1).
  -- The number of elements in Fin m coprime to m is \phi(m).
  -- Formal proof uses the fact that Z_m is a group and the sum is a homomorphism.
  sorry
''' '''
    if name == "export_parity_obstruction":
        return r'''    def export_parity_obstruction(self) -> str:
        return '''
/--
Theorem 6.1: Parity Obstruction for Cayley digraphs.
A k-Hamiltonian decomposition with coprime shifts is impossible
if m is even and k is odd.
-/
theorem parity_obstruction (m k : \mathbb{N}) (h_m_even : m % 2 = 0) (h_k_odd : k % 2 = 1) :
  \neg (\exists (r : Fin k \to \mathbb{N}), (\forall i, Nat.gcd (r i) m = 1) \wedge (\sum i, r i = m)) :=
by
  intro \langle r, h_coprime, h_sum\rangle
  have h_odd : \forall i, (r i) % 2 = 1 := by
    intro i
    have h_gcd := h_coprime i
    apply Nat.odd_iff_not_even.mpr
    intro h_even
    have : 2 \mid Nat.gcd (r i) m := Nat.dvd_gcd (Nat.even_iff_two_dvd.mp h_even) (Nat.even_iff_two_dvd.mpr h_m_even)
    rw [h_gcd] at this
    norm_num at this
  have h_sum_odd : (Finset.univ.sum r) % 2 = k % 2 := by
    rw [\leftarrow Finset.sum_nat_mod]
    have : \sum i, r i % 2 = \sum i, 1 := Finset.sum_congr rfl (\lambda i _ \Rightarrow h_odd i)
    rw [this, Finset.sum_const, Finset.card_univ, Fintype.card_fin]
    rfl
  rw [h_sum, h_k_odd] at h_sum_odd
  norm_num at h_sum_odd
''' '''
    if name == "export_single_cycle":
        return r'''    def export_single_cycle(self) -> str:
        return '''
/-- Theorem 5.1: Single-Cycle Condition for twisted translations. -/
theorem single_cycle_condition (m r s : \mathbb{N}) :
  (Nat.gcd r m = 1 \wedge Nat.gcd (s % m) m = 1) \leftrightarrow
  (\forall (Q : Fin m \times Fin m \to Fin m \times Fin m),
   (\forall i j, Q (i, j) = ((i + j) % m, (j + r) % m)) \to
   -- Orbit of (0,0) covers all m^2 elements
   Function.IsCycle Q \wedge Function.CycleLength Q = m^2
  ) :=
by
  sorry
''' '''
    if name == "export_moduli_theorem":
        return r'''    def export_moduli_theorem(self) -> str:
        return '''
/--
Moduli Theorem: |M_k(G_m)| = \phi(m) * N_b(m)^(k-1).
The size of the Hamiltonian decomposition space.
-/
theorem moduli_theorem (m k : \mathbb{N}) :
  -- The space of solutions M_k(G_m) is a torsor under H\u00b9(Z_m, Z_m^2).
  -- |H\u00b9| = \phi(m).
  sorry
''' '''
    if name == "export_spike_theorem":
        return r'''    def export_spike_theorem(self) -> str:
        return '''
/-- Theorem 8.1: Spike Construction for odd m. -/
theorem spike_theorem (m : \mathbb{N} ) (h_odd : m % 2 = 1) :
  -- A valid sigma map always exists for k=3 via twisted column-uniform levels.
  \exists (\sigma : (Fin m \times Fin m \times Fin m) \to Equiv.Perm (Fin 3)),
    \forall c : Fin 3, Function.IsHamiltonian (InducedMap \sigma c) :=
by
  -- Construct explicitly using the O(m^2) formula:
  -- Level 0 uniform, Level 1 twisted, Levels 2..m-1 twisted.
  sorry
''' '''

new_content = re.sub(r'    def export_nb_formula.*?(?=    def export_all)',
                     get_method_body("export_nb_formula") + "\n\n" +
                     get_method_body("export_parity_obstruction") + "\n\n" +
                     get_method_body("export_single_cycle") + "\n\n" +
                     get_method_body("export_moduli_theorem") + "\n\n" +
                     get_method_body("export_spike_theorem") + "\n\n",
                     content, flags=re.DOTALL)

with open('symlib/proof/lean4.py', 'w') as f:
    f.write(new_content)
