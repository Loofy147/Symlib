"""
symlib.search.viz
=================
Visualization utilities for Hamiltonian cycles and functional graphs.
"""

from __future__ import annotations
import json
from typing import Dict, Tuple, List

Sigma = Dict[Tuple[int,...], Tuple[int,...]]
_SHIFTS = ((1,0,0), (0,1,0), (0,0,1))

def export_to_dot(sigma: Sigma, m: int, colors: List[int] = [0, 1, 2]) -> str:
    """
    Export the functional graphs of selected colors to DOT format.
    """
    lines = ["digraph G {", "  node [shape=circle];"]

    # Define colors for the edges
    edge_colors = {0: "red", 1: "green", 2: "blue"}

    for v, p in sigma.items():
        v_str = f"v_{v[0]}_{v[1]}_{v[2]}"
        for at in range(3):
            c = p[at]
            if c in colors:
                nb = tuple((v[d] + _SHIFTS[at][d]) % m for d in range(3))
                nb_str = f"v_{nb[0]}_{nb[1]}_{nb[2]}"
                lines.append(f'  {v_str} -> {nb_str} [color="{edge_colors.get(c, "black")}"];')

    lines.append("}")
    return "\n".join(lines)

def export_to_json(sigma: Sigma, m: int) -> str:
    """
    Export the solution structure to a simple JSON for web-based visualization.
    """
    nodes = []
    links = []

    edge_colors = {0: "red", 1: "green", 2: "blue"}

    for i in range(m):
        for j in range(m):
            for k in range(m):
                nodes.append({"id": f"{i}_{j}_{k}", "coords": [i, j, k]})

    for v, p in sigma.items():
        source = f"{v[0]}_{v[1]}_{v[2]}"
        for at in range(3):
            c = p[at]
            nb = tuple((v[d] + _SHIFTS[at][d]) % m for d in range(3))
            target = f"{nb[0]}_{nb[1]}_{nb[2]}"
            links.append({
                "source": source,
                "target": target,
                "color": edge_colors.get(c, "black"),
                "type": at
            })

    return json.dumps({"nodes": nodes, "links": links}, indent=2)

def save_viz(sigma: Sigma, m: int, path: str):
    """Save visualization data to file."""
    if path.endswith(".dot"):
        data = export_to_dot(sigma, m)
    else:
        data = export_to_json(sigma, m)

    with open(path, "w") as f:
        f.write(data)
    print(f"Visualization saved to {path}")
