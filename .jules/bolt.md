
## 2024-05-15 - Structured Level Validity Optimization
**Learning:** Level validity in G_m (k=3) can be checked in O(m) because each color must have a uniform dj (either always 0 or always 1) across all columns in a single level. This restricts the number of valid levels to exactly 3 * 2^m.
**Action:** Use direct generation of valid levels and O(m) table verification (summing displacements) instead of O(m^3) full functional graph checks.
