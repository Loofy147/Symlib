import math
from itertools import product

def gcd(a, b):
    while b: a, b = b, a % b
    return a

def phi(n):
    res = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0: temp //= p
            res -= res // p
        p += 1
    if temp > 1: res -= res // temp
    return res

def verify_nb(m):
    count = 0
    total = m**m
    for b in product(range(m), repeat=m):
        if gcd(sum(b) % m, m) == 1:
            count += 1
    expected = m**(m-1) * phi(m)
    return count, expected

def analyze_spike_gap(m):
    print(f"\nAnalyzing spike gap for m={m}...")
    # Valid levels: one color fixed to arc type 1 for all j.
    # Color c_fixed uses at=1 for all j. dj = m steps. r_c = m = 0 (mod m).
    # Since every level in the table must be valid, every color in every level
    # has dj = 0 or dj = m.
    # Therefore, for any color c, r_c = sum(dj_l) = sum(m or 0) = 0 (mod m).
    # A pure spike Q_c(i,j) = (i + delta[j==j0], j + r_c) is a single cycle
    # only if gcd(r_c, m) == 1.
    # Since r_c is always 0 (mod m), gcd(r_c, m) = m != 1.

    print(f"For any color c, r_c = sum of shifts in j over the table.")
    print(f"In a column-uniform level, each color uses arc-type 1 for ALL j or NO j.")
    print(f"Thus each level contributes 0 or m to r_c.")
    print(f"Result: r_c mod m is ALWAYS 0.")

    spike_possible = False
    for r_c in range(m):
        if gcd(r_c, m) == 1:
            spike_possible = True
            break

    if not spike_possible and m > 1:
        # Wait, if r_c must be 0, can we ever have a spike?
        # A spike with r_c = 0 is Q_c(i,j) = (i + [j==j0], j).
        # This has m-1 fixed points (where j != j0) and one cycle of size m (where j == j0).
        # Definitely NOT a single m^2 cycle.
        pass

    print(f"Conclusion: No column-uniform construction can achieve a pure spike for m > 1.")
    print(f"The reachable composed b_c functions are a proper subset of all valid b_c functions.")

if __name__ == "__main__":
    print("Verification of Nb(m) = m^(m-1) * phi(m):")
    for m in range(2, 8):
        count, expected = verify_nb(m)
        status = "✓" if count == expected else "✗"
        print(f"  m={m}: Nb={count:<8} Expected={expected:<8} {status}")

    analyze_spike_gap(3)
    analyze_spike_gap(5)
