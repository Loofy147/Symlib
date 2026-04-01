import time
import numpy as np
import random
from symlib.kernel.verify import score_sigma, score_sigma_numba, HAS_NUMBA
from symlib.search.equivariant import _build_sa_tables

def benchmark():
    m, k = 6, 3
    n, arc_s, pa, all_perms = _build_sa_tables(m, k)
    nP = len(all_perms)

    sigma_list = np.array([random.randrange(nP) for _ in range(n)], dtype=np.uint32)

    print(f"Benchmarking m={m}, k={k}, n={n} vertices...")
    print(f"Numba available: {HAS_NUMBA}")

    # Warm up
    score_sigma(sigma_list, arc_s, pa, n, k)
    if HAS_NUMBA:
        score_sigma_numba(sigma_list, arc_s, pa, n, k)

    # Pure Python
    t0 = time.perf_counter()
    for _ in range(100):
        score_sigma(sigma_list, arc_s, pa, n, k)
    t1 = time.perf_counter()
    py_time = (t1 - t0) / 100
    print(f"Pure Python: {py_time*1000:.4f} ms per call")

    # Numba
    if HAS_NUMBA:
        t0 = time.perf_counter()
        for _ in range(1000):
            score_sigma_numba(sigma_list, arc_s, pa, n, k)
        t1 = time.perf_counter()
        numba_time = (t1 - t0) / 1000
        print(f"Numba:       {numba_time*1000:.4f} ms per call")
        print(f"Speedup:     {py_time / numba_time:.1f}x")
    else:
        print("Numba NOT available, skipping Numba benchmark.")

if __name__ == "__main__":
    benchmark()
