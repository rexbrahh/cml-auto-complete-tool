"""
Command-line interface for CML Auto-Complete Tool
"""
import os
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.prompt import Confirm

from .shell import InteractiveShell

console = Console()

@click.group()
@click.option(
    "--dir",
    "-d",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Working directory for command execution",
)
@click.pass_context
def cli(ctx: click.Context, dir: Optional[str]) -> None:
    """CML Auto-Complete Tool - Natural language to terminal command conversion"""
    if dir:
        os.chdir(dir)
        console.print(f"[green]Working directory set to: {dir}[/green]")

@cli.command()
@click.pass_context
def shell(ctx: click.Context) -> None:
    """Start the interactive shell"""
    try:
        shell = InteractiveShell()
        shell.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Shell terminated by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise click.Abort()

if __name__ == "__main__":
    cli() 