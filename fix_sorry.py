import sys

def replace_in_file(filepath, search_text, replace_text):
    with open(filepath, 'r') as f:
        content = f.read()
    if search_text not in content:
        print(f"Error: Search text not found in {filepath}")
        return False
    new_content = content.replace(search_text, replace_text)
    with open(filepath, 'w') as f:
        f.write(new_content)
    print(f"Successfully updated {filepath}")
    return True

# Fix symlib/kernel/obstruction.py
search1 = '''  have h_odd : ∀ i, (r i) % 2 = 1 := by
    intro i
    have h_gcd := h_coprime i
    -- Since {self.m} is even, gcd(r, {self.m})=1 implies r is odd
    sorry
  have h_sum_odd : (∑ i, r i) % 2 = 1 := by
    -- Sum of {self.k} (odd) integers is odd
    sorry
  rw [h_sum] at h_sum_odd
  -- contradiction: {self.m} % 2 = 1 but {self.m} is even
  norm_num at h_sum_odd'''

replace1 = '''  have h_odd : ∀ i, (r i) % 2 = 1 := by
    intro i
    have h_gcd := h_coprime i
    apply Nat.odd_iff_not_even.mpr
    intro h_even
    have : 2 ∣ Nat.gcd (r i) {self.m} := Nat.dvd_gcd (Nat.even_iff_two_dvd.mp h_even) (by norm_num)
    rw [h_gcd] at this
    norm_num at this
  have h_sum_odd : (Finset.univ.sum r) % 2 = {self.k} % 2 := by
    rw [← Finset.sum_nat_mod]
    have : ∑ i, r i % 2 = ∑ i, 1 := Finset.sum_congr rfl (λ i _ => h_odd i)
    rw [this, Finset.sum_const, Finset.card_univ, Fintype.card_fin]
    rfl
  rw [h_sum, (by norm_num : {self.k} % 2 = 1)] at h_sum_odd
  norm_num at h_sum_odd'''

replace_in_file('symlib/kernel/obstruction.py', search1, replace1)

# Fix symlib/proof/lean4.py
search2 = '''    def export_parity_obstruction(self) -> str:
        return \'''
/--
Theorem 6.1: Parity Obstruction for Cayley digraphs.
A k-Hamiltonian decomposition with coprime shifts is impossible
if m is even and k is odd.
-/
theorem parity_obstruction (m k : ℕ) (h_m_even : m % 2 = 0) (h_k_odd : k % 2 = 1) :
  ¬ (∃ (r : Fin k → ℕ), (∀ i, Nat.gcd (r i) m = 1) ∧ (∑ i, r i = m)) :=
by
  intro ⟨r, h_coprime, h_sum⟩
  -- Any r_i coprime to even m must be odd.
  have h_odd : ∀ i, (r i) % 2 = 1 := by
    intro i
    -- Nat.gcd x m = 1 and 2 | m implies ¬(2 | x)
    sorry
  -- Sum of odd number (k) of odd integers is odd.
  have h_sum_odd : (∑ i, r i) % 2 = 1 := by
    -- Induction on k using (a + b) % 2 = (a % 2 + b % 2) % 2
    sorry
  -- Contradiction: m is even, but sum(r) = m is odd.
  rw [h_sum] at h_sum_odd
  absurd h_m_even
  -- Nat.mod_two_eq_zero_iff_even.mpr ...
  sorry
\''' '''

replace2 = '''    def export_parity_obstruction(self) -> str:
        return \'''
/--
Theorem 6.1: Parity Obstruction for Cayley digraphs.
A k-Hamiltonian decomposition with coprime shifts is impossible
if m is even and k is odd.
-/
theorem parity_obstruction (m k : ℕ) (h_m_even : m % 2 = 0) (h_k_odd : k % 2 = 1) :
  ¬ (∃ (r : Fin k → ℕ), (∀ i, Nat.gcd (r i) m = 1) ∧ (∑ i, r i = m)) :=
by
  intro ⟨r, h_coprime, h_sum⟩
  have h_odd : ∀ i, (r i) % 2 = 1 := by
    intro i
    have h_gcd := h_coprime i
    apply Nat.odd_iff_not_even.mpr
    intro h_even
    have : 2 ∣ Nat.gcd (r i) m := Nat.dvd_gcd (Nat.even_iff_two_dvd.mp h_even) (Nat.even_iff_two_dvd.mpr h_m_even)
    rw [h_gcd] at this
    norm_num at this
  have h_sum_odd : (Finset.univ.sum r) % 2 = k % 2 := by
    rw [← Finset.sum_nat_mod]
    have : ∑ i, r i % 2 = ∑ i, 1 := Finset.sum_congr rfl (λ i _ => h_odd i)
    rw [this, Finset.sum_const, Finset.card_univ, Fintype.card_fin]
    rfl
  rw [h_sum, h_k_odd] at h_sum_odd
  norm_num at h_sum_odd
\''' '''

# Need to handle the triple quotes carefully in the search string
search2 = search2.replace("\\'''", "'''")
replace2 = replace2.replace("\\'''", "'''")

replace_in_file('symlib/proof/lean4.py', search2, replace2)
