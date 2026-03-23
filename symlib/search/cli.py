"""
symlib.search.cli
=================
Command-line interface for running equivariant SA search.
"""

import argparse
import sys
import os
from symlib.search.equivariant import run_equivariant_sa, load_checkpoint
from symlib.search.viz import save_viz

def main():
    parser = argparse.ArgumentParser(description="Run equivariant SA search for symlib.")
    parser.add_argument("--m", type=int, required=True, help="Fiber size")
    parser.add_argument("--iters", type=int, default=5000000, help="Maximum iterations")
    parser.add_argument("--seed", type=int, default=0, help="Random seed")
    parser.add_argument("--checkpoint", type=str, help="Path to checkpoint file")
    parser.add_argument("--save-every", type=int, default=1000000, help="Save checkpoint every N iterations")
    parser.add_argument("--export-viz", type=str, help="Path to export visualization (JSON or DOT)")
    parser.add_argument("--verbose", action="store_true", help="Print progress")

    args = parser.parse_args()

    initial_sigma = None
    if args.checkpoint and os.path.exists(args.checkpoint):
        print(f"Loading checkpoint from {args.checkpoint}...")
        cp = load_checkpoint(args.checkpoint)
        if cp:
            if cp['m'] != args.m:
                print(f"Error: Checkpoint fiber size {cp['m']} does not match requested {args.m}")
                sys.exit(1)
            initial_sigma = cp['sigma_list']
            print(f"Resuming search with start score {cp['stats']['best']}...")

    print(f"Starting equivariant SA for m={args.m}, max_iter={args.iters}, seed={args.seed}...")

    sol, stats = run_equivariant_sa(
        m=args.m,
        seed=args.seed,
        max_iter=args.iters,
        initial_sigma=initial_sigma,
        verbose=args.verbose,
        checkpoint_path=args.checkpoint,
        checkpoint_n=args.save_every
    )

    print("\nSearch finished.")
    print(f"Best score: {stats['best']}")
    print(f"Iterations: {stats['iters']}")

    if sol:
        print("SOLUTION FOUND!")
        if args.export_viz:
            save_viz(sol, args.m, args.export_viz)
    else:
        print("No solution found in this run.")

if __name__ == "__main__":
    main()
