"""
kaggle_search.py
================
Distributed search template for Kaggle / Remote Servers.
Uses symlib v2.1.0 CLI and Checkpoints.
"""

import os
import subprocess
import time

# Configuration
M = 6
ITERS_TOTAL = 100_000_000
ITERS_PER_STEP = 5_000_000
CHECKPOINT_FILE = f"checkpoint_m{M}.json"

def run_search_step():
    print(f"Running search step for m={M} ({ITERS_PER_STEP} iterations)...")

    cmd = [
        "python3", "-m", "symlib.search.cli",
        "--m", str(M),
        "--iters", str(ITERS_PER_STEP),
        "--checkpoint", CHECKPOINT_FILE,
        "--save-every", str(ITERS_PER_STEP),
        "--verbose"
    ]

    # Ensure symlib is in PYTHONPATH
    env = os.environ.copy()
    if "PYTHONPATH" not in env:
        env["PYTHONPATH"] = "."
    else:
        env["PYTHONPATH"] = ".:" + env["PYTHONPATH"]

    result = subprocess.run(cmd, env=env)
    return result.returncode == 0

def main():
    # If on Kaggle, you might want to install symlib first:
    # subprocess.run(["pip", "install", "symlib-core"])

    start_time = time.time()
    steps_done = 0
    total_steps = ITERS_TOTAL // ITERS_PER_STEP

    print(f"Starting distributed search for m={M}...")
    print(f"Target iterations: {ITERS_TOTAL}")

    while steps_done < total_steps:
        success = run_search_step()
        if not success:
            print("Search step failed. Retrying...")
            continue

        steps_done += 1
        elapsed = time.time() - start_time
        print(f"Step {steps_done}/{total_steps} complete. Elapsed: {elapsed:.1f}s")

        # Check if solution found (CLI prints it)
        # In a real script, you'd check the checkpoint file for best=0

    print("Search session finished.")

if __name__ == "__main__":
    main()
