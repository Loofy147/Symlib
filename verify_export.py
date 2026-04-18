from symlib.kernel.obstruction import ObstructionChecker
from symlib.proof.lean4 import Lean4Exporter

# 1. Test specific obstruction export
checker = ObstructionChecker(m=4, k=3)
res = checker.h2_parity()
print("Obstruction Export (m=4, k=3):")
print(res.to_lean4())

# 2. Test global exporter
exporter = Lean4Exporter()
print("\nGlobal Exporter parity obstruction section:")
all_lean = exporter.export_all()
# Find parity_obstruction in the big string
start = all_lean.find("theorem parity_obstruction")
end = all_lean.find("'''", start) # wait it is not triple quoted in the output
print(all_lean[start:start+500])
