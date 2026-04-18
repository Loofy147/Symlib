with open('symlib/proof/lean4.py', 'r') as f:
    lines = f.readlines()

with open('symlib/proof/lean4.py', 'w') as f:
    for line in lines:
        if line.strip() == "def export_moduli_theorem(self) -> str:":
            f.write("    def export_moduli_theorem(self) -> str:\n")
        elif line.strip() == "def export_spike_theorem(self) -> str:":
            f.write("    def export_spike_theorem(self) -> str:\n")
        else:
            f.write(line)
