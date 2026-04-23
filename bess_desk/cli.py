"""Command-line interface for bess-desk."""

from __future__ import annotations

import typer
from rich.console import Console

app = typer.Typer(help="Agent-orchestrated BESS trading desk.")
console = Console()


@app.command()
def init(mandate: str = "nl-10mw") -> None:
    """Scaffold a new desk with the given mandate."""
    console.print(f"[cyan]Initializing desk with mandate: {mandate}[/cyan]")
    console.print("[yellow]TODO: write config files, create audit dir[/yellow]")


@app.command()
def run(
    mode: str = typer.Option("replay", help="Market mode: replay | live | sim"),
    data: str = typer.Option("", help="Path to data (for replay mode)"),
    auto_approve: bool = typer.Option(False, help="Auto-approve all proposals (backtest only)"),
) -> None:
    """Run the desk."""
    console.print(f"[cyan]Running desk in [bold]{mode}[/bold] mode[/cyan]")
    if auto_approve:
        console.print("[red]⚠ AUTO-APPROVE enabled — backtest use only[/red]")
    console.print("[yellow]TODO: wire up scheduler + agents + market adapter[/yellow]")


@app.command()
def dashboard(port: int = 8501) -> None:
    """Launch the Streamlit dashboard."""
    import subprocess
    import sys

    cmd = [sys.executable, "-m", "streamlit", "run", "dashboard/app.py", "--server.port", str(port)]
    subprocess.run(cmd, check=False)


if __name__ == "__main__":
    app()
