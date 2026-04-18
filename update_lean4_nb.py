import sys

def replace_method(filepath, method_name, new_body):
    with open(filepath, 'r') as f:
        content = f.read()

    start_str = f"    def {method_name}"
    start_idx = content.find(start_str)
    if start_idx == -1:
        print(f"Method {method_name} not found")
        return

    # Find the next 'def' or end of class
    next_def = content.find("    def ", start_idx + len(start_str))
    if next_def == -1:
        next_def = len(content)

    new_content = content[:start_idx] + new_body + "\n\n" + content[next_def:].lstrip()
    with open(filepath, 'w') as f:
        f.write(new_content)
    print(f"Updated {method_name}")

nb_body = '''    def export_nb_formula(self) -> str:
        return \'''
/--
Theorem 4.1: N_b(m) = m^(m-1) * \u03c6(m).
The number of functions b: Z_m -> Z_m with coprime sum.
-/
theorem nb_formula (m : \u2115) (h_m_pos : m > 0) :
  let functions := {b : Fin m \u2192 Fin m | Nat.gcd (\u2211 i, (b i).val) m = 1}
  functions.ncard = m^(m-1) * Nat.totient m :=
by
  -- Consider the map f: (Fin m \u2192 Fin m) \u2192 Fin m defined by (\u2211 b_i) mod m.
  -- This map is surjective and each fiber has size m^(m-1).
  -- The number of elements in Fin m coprime to m is \u03c6(m).
  -- Formal proof uses the fact that Z_m is a group and the sum is a homomorphism.
  sorry
\''' '''

replace_method('symlib/proof/lean4.py', 'export_nb_formula', nb_body.replace("\\'''", "'''"))
