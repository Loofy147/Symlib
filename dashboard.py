import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
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

    records_table.add_row("P1-k4", "4", "4", "33", "[yellow]OPEN[/yellow]", "Color-3 cycles (153, 84) cover 93%")
    records_table.add_row("P2", "6", "3", "16", "[yellow]OPEN[/yellow]", "Color-1 dominant 174/216. 6 short cycles.")
    records_table.add_row("P3", "8", "3", "37", "[yellow]OPEN[/yellow]", "Converging: cycles 158, 267, 353 vertices")
    records_table.add_row("m=3 k=3", "3", "3", "0", "[green]SOLVED[/green]", "9s (600k iters). Fixed score bug.")

    # Theoretical Breakthroughs
    theory_panel = Panel(
        Text.assemble(
            ("Nb(m) = m^(m-1) * φ(m): ", "bold cyan"), "Sum coprime to m verified for m=7.\n",
            ("648 = 162 x 4 Resolution: ", "bold cyan"), "Labelled gauge orbit factor (2 shift x 2 color).\n",
            ("Score Bug Fix: ", "bold cyan"), "Used (n_components - 1) instead of length diffs.\n",
            ("Sigma Bug Fix: ", "bold cyan"), "Correct mapping of arc types to color permutations."
        ),
        title="Theoretical Results",
        border_style="magenta",
        box=box.ROUNDED
    )

    # Performance
    perf_panel = Panel(
        Text.assemble(
            ("JIT Status: ", "bold green"), "WARM (Numba 0.65.0)\n",
            ("Throughput: ", "bold green"), "~150k iters/sec (m=6)\n",
            ("Efficiency: ", "bold green"), "512 vertices in <5s (P3)\n",
            ("Gap Analysis: ", "bold green"), "Level-to-composition spike gap identified."
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
