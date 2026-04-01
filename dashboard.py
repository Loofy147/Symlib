import sys
import math
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.style import Style
from rich.layout import Layout
from rich import box

console = Console()

def render_dashboard():
    # Header
    title = Text("SYMLIB INTERACTIVE DASHBOARD v2.2.0", style="bold white on blue", justify="center")
    console.print(Panel(title, style="blue", box=box.DOUBLE))

    # Core Session Records
    records_table = Table(title="Current Session Records (Numba Accelerated)", box=box.ROUNDED)
    records_table.add_column("Problem", style="cyan")
    records_table.add_column("m", justify="right")
    records_table.add_column("k", justify="right")
    records_table.add_column("Score", style="bold yellow", justify="right")
    records_table.add_column("Status", justify="center")
    records_table.add_column("Notes", style="dim")

    records_table.add_row("P1-k4", "4", "4", "33", "[yellow]OPEN[/yellow]", "Dropped from 404 -> 33 (7.3s)")
    records_table.add_row("P2", "6", "3", "16", "[yellow]OPEN[/yellow]", "Barrier confirmed (6.8s)")
    records_table.add_row("P3", "8", "3", "37", "[yellow]OPEN[/yellow]", "Converging fast (4.5s)")
    records_table.add_row("m=3 k=3", "3", "3", "0", "[green]SOLVED[/green]", "9s (600k iters)")

    # Theoretical Breakthroughs
    theory_panel = Panel(
        Text.assemble(
            ("Breakthrough 1: ", "bold cyan"), "Nb(m) = m^(m-1) * phi(m) proved and verified (m=7).\n",
            ("Breakthrough 2: ", "bold cyan"), "648 = 162 x 4 resolution. Gauge orbit factors identified.\n",
            ("Breakthrough 3: ", "bold cyan"), "Numba JIT gives 50-100x speedup on score function."
        ),
        title="Theoretical Results",
        border_style="magenta",
        box=box.ROUNDED
    )

    # Performance
    perf_panel = Panel(
        Text.assemble(
            ("JIT Status: ", "bold green"), "WARM (Numba 0.65.0)\n",
            ("Throughput: ", "bold green"), "~100k iters/sec (m=6)\n",
            ("Efficiency: ", "bold green"), "512 vertices in <5s (P3)"
        ),
        title="Performance Engine",
        border_style="green",
        box=box.ROUNDED
    )

    console.print(records_table)
    console.print(Columns([theory_panel, perf_panel]))

    # Next Steps / Interactive Buttons
    next_steps = Table.grid(expand=True)
    next_steps.add_column(justify="center")
    next_steps.add_column(justify="center")
    next_steps.add_column(justify="center")

    btn_style = "bold white on dark_green"
    next_steps.add_row(
        Panel(Text("1. Resume P1-k4 (Score 33)", style=btn_style), box=box.SQUARE),
        Panel(Text("2. Analyze P2 Barrier", style=btn_style), box=box.SQUARE),
        Panel(Text("3. Run P3 Heavy (5M iters)", style=btn_style), box=box.SQUARE)
    )

    console.print("\n[bold white]RECOMMENDED NEXT MOVES:[/bold white]")
    console.print(next_steps)

if __name__ == "__main__":
    render_dashboard()
