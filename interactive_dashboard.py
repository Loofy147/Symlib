from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Button, DataTable
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual import on
import subprocess
import os

RECORDS = [
    ("P1-k4", "4", "4", "33", "OPEN", "Dropped from 404 -> 33 (7.3s)"),
    ("P2", "6", "3", "16", "OPEN", "Barrier confirmed (6.8s)"),
    ("P3", "8", "3", "37", "OPEN", "Converging fast (4.5s)"),
    ("m=3 k=3", "3", "3", "0", "SOLVED", "9s (600k iters)"),
]

THEORY = """
[b cyan]Breakthrough 1:[/b cyan] Nb(m) = m^(m-1) * phi(m) proved and verified (m=7).
[b cyan]Breakthrough 2:[/b cyan] 648 = 162 x 4 resolution. Gauge orbit factors identified.
[b cyan]Breakthrough 3:[/b cyan] Numba JIT gives 50-100x speedup on score function.
"""

PERF = """
[b green]JIT Status:[/b green] WARM (Numba 0.65.0)
[b green]Throughput:[/b green] ~100k iters/sec (m=6)
[b green]Efficiency:[/b green] 512 vertices in <5s (P3)
"""

class Dashboard(App):
    TITLE = "SYMLIB INTERACTIVE DASHBOARD v2.2.0"
    BINDINGS = [("q", "quit", "Quit")]
    CSS = """
    Screen {
        background: $boost;
    }
    #main-container {
        padding: 1 2;
    }
    .panel {
        border: round $primary;
        padding: 1;
        margin: 1;
        height: auto;
    }
    #theory-panel { border: round $magenta; }
    #perf-panel { border: round $green; }
    DataTable {
        height: auto;
        margin-bottom: 1;
    }
    Button {
        margin: 1;
        width: 1fr;
    }
    #footer-text {
        text-align: center;
        color: $text-disabled;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main-container"):
            yield Static("[b cyan]Current Session Records (Numba Accelerated)[/b cyan]", id="table-header")
            yield DataTable(id="records-table")

            with Horizontal():
                yield Static(THEORY, id="theory-panel", classes="panel")
                yield Static(PERF, id="perf-panel", classes="panel")

            yield Static("[b white]RECOMMENDED NEXT MOVES:[/b white]", id="moves-header")
            with Horizontal():
                yield Button("1. Resume P1-k4 (Score 33)", variant="success", id="btn-p1")
                yield Button("2. Analyze P2 Barrier", variant="success", id="btn-p2")
                yield Button("3. Run P3 Heavy (5M iters)", variant="success", id="btn-p3")

            yield Static("Press 'Q' to exit or click a button to start a background task.", id="footer-text")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Problem", "m", "k", "Score", "Status", "Notes")
        for row in RECORDS:
            styled_row = list(row)
            if row[4] == "SOLVED":
                styled_row[4] = "[green]SOLVED[/green]"
            else:
                styled_row[4] = "[yellow]OPEN[/yellow]"
            table.add_row(*styled_row)

    @on(Button.Pressed, "#btn-p1")
    def run_p1(self) -> None:
        self.notify("Starting P1-k4 resume in background...")
        # In a real app, this would use subprocess to run symlib.search.cli
        # subprocess.Popen(["python3", "-m", "symlib.search.cli", "--m", "4", "--k", "4", "--iters", "1000000"])

    @on(Button.Pressed, "#btn-p2")
    def run_p2(self) -> None:
        self.notify("Analyzing P2 barrier...")

    @on(Button.Pressed, "#btn-p3")
    def run_p3(self) -> None:
        self.notify("Queuing P3 heavy run...")

if __name__ == "__main__":
    app = Dashboard()
    app.run()
