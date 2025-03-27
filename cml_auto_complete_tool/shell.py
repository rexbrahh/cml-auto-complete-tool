"""
Interactive shell implementation for CML Auto-Complete Tool
"""
import os
from typing import Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.prompt import Confirm

from .ai import CommandGenerator
from .command import CommandExecutor

console = Console()

class InteractiveShell:
    def __init__(self):
        self.session = PromptSession()
        self.command_generator = CommandGenerator()
        self.command_executor = CommandExecutor()
        self.history: list[str] = []
        
        # Basic command completions
        self.completer = WordCompleter([
            "exit", "quit", "help", "clear", "pwd", "ls",
            "cd", "echo", "cat", "grep", "find", "mkdir",
            "rm", "cp", "mv", "chmod", "chown"
        ])

    def run(self) -> None:
        """Run the interactive shell"""
        console.print("[bold green]Welcome to CML Auto-Complete Tool![/bold green]")
        console.print("Type your request in natural language, and I'll help you find the right command.")
        console.print("Type 'exit' or 'quit' to end the session.\n")

        while True:
            try:
                # Get user input
                user_input = self.session.prompt(
                    "> ",
                    completer=self.completer,
                    history=self.history
                ).strip()

                if user_input.lower() in ["exit", "quit"]:
                    break

                if not user_input:
                    continue

                # Generate command suggestion
                command, question = self.command_generator.generate_command(user_input)
                
                # Handle follow-up questions
                while question:
                    console.print(f"\n[bold blue]Question:[/bold blue] {question}")
                    follow_up = self.session.prompt("> ").strip()
                    if follow_up.lower() in ["exit", "quit"]:
                        break
                    command, question = self.command_generator.generate_command(follow_up)
                
                if not command:
                    console.print("[yellow]I couldn't generate a command for your request. Please try rephrasing.[/yellow]")
                    continue

                # Show command and ask for confirmation
                console.print(f"\n[bold]Suggested command:[/bold] {command}")
                if Confirm.ask("Execute this command?"):
                    try:
                        result = self.command_executor.execute(command)
                        console.print(f"\n[green]Command executed successfully![/green]")
                        if result:
                            console.print(f"\nOutput:\n{result}")
                    except ValueError as e:
                        console.print(f"[red]Safety check failed: {str(e)}[/red]")
                    except Exception as e:
                        console.print(f"[red]Error executing command: {str(e)}[/red]")

                self.history.append(user_input)

            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")

        console.print("\n[bold green]Thank you for using CML Auto-Complete Tool![/bold green]") 