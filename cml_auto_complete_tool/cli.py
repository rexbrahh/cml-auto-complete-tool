"""
Command-line interface for CML Auto-Complete Tool
"""
import os
import sys
from pathlib import Path
from typing import Optional

# Import msvcrt only on Windows
if os.name == 'nt':
    import msvcrt

import click

from .shell import InteractiveShell, print_color
from .config import Config
from .ai import CommandGenerator

def secure_input(prompt: str = "") -> str:
    """
    Get secure input with asterisk display
    
    Args:
        prompt: The prompt to display
        
    Returns:
        str: The input string
    """
    if prompt:
        print(prompt, end='', flush=True)
    
    password = []
    while True:
        if os.name == 'nt':  # Windows
            try:
                char = msvcrt.getch()
                if char == b'\r':  # Enter key
                    print()  # New line
                    break
                elif char == b'\b':  # Backspace
                    if password:
                        password.pop()
                        msvcrt.putch(b'\b')
                        msvcrt.putch(b' ')
                        msvcrt.putch(b'\b')
                else:
                    password.append(char.decode())
                    msvcrt.putch(b'*')
                    msvcrt.putch(b'\b')  # Move cursor back
                    msvcrt.putch(b'*')  # Write asterisk again to ensure visibility
            except Exception:
                # Fallback to regular input if there's an error
                return input("(Fallback mode) Enter your API key: ")
        else:  # Unix-like
            import termios
            import tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
                if ch == '\r' or ch == '\n':  # Enter key
                    print()  # New line
                    break
                elif ch == '\b' or ch == '\x7f':  # Backspace
                    if password:
                        password.pop()
                        sys.stdout.write('\b \b')
                        sys.stdout.flush()
                else:
                    password.append(ch)
                    sys.stdout.write('*')
                    sys.stdout.flush()
                    # Ensure the asterisk is visible
                    sys.stdout.write('\b*')
                    sys.stdout.flush()
            except Exception:
                # Fallback to regular input if there's an error
                return input("(Fallback mode) Enter your API key: ")
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    return ''.join(password)

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
        print_color(f"Working directory set to: {dir}", "green")

@cli.command()
@click.pass_context
def init(ctx: click.Context) -> None:
    """Initialize the tool with your Anthropic API key"""
    config = Config()
    
    if config.validate_api_key():
        print_color("API key is already configured.", "yellow")
        if input("Would you like to update it? (y/n): ").lower().strip() in ['y', 'yes']:
            print_color("\nEnter your Anthropic API key:", "blue")
            api_key = secure_input()
            if config.set_api_key(api_key):
                print_color("API key updated successfully!", "green")
                # Start shell after successful update
                try:
                    shell = InteractiveShell()
                    shell.run()
                except KeyboardInterrupt:
                    print_color("\nShell terminated by user", "yellow")
                except Exception as e:
                    print_color(f"Error: {str(e)}", "red")
                    raise click.Abort()
            else:
                print_color("Failed to update API key.", "red")
    else:
        print_color("Welcome to CML Auto-Complete Tool!", "green")
        print_color("Please enter your Anthropic API key to get started.", "blue")
        print_color("You can get your API key from: https://console.anthropic.com/", "blue")
        print_color("\nEnter your Anthropic API key:", "blue")
        api_key = secure_input()
        if config.set_api_key(api_key):
            print_color("API key configured successfully!", "green")
            # Start shell after successful configuration
            try:
                shell = InteractiveShell()
                shell.run()
            except KeyboardInterrupt:
                print_color("\nShell terminated by user", "yellow")
            except Exception as e:
                print_color(f"Error: {str(e)}", "red")
                raise click.Abort()
        else:
            print_color("Failed to configure API key.", "red")

@cli.command()
@click.pass_context
def shell(ctx: click.Context) -> None:
    """Start the interactive shell"""
    config = Config()
    if not config.validate_api_key():
        print_color("API key not configured. Please run 'cml-auto-complete-tool init' first.", "red")
        return
        
    try:
        shell = InteractiveShell()
        shell.run()
    except KeyboardInterrupt:
        print_color("\nShell terminated by user", "yellow")
    except Exception as e:
        print_color(f"Error: {str(e)}", "red")
        raise click.Abort()

@cli.command()
@click.option('--api-key', prompt=True, hide_input=True, help='Your Anthropic API key')
def configure(api_key: str):
    """Configure the tool with your Anthropic API key"""
    config = Config()
    if config.set_api_key(api_key):
        click.echo("API key configured successfully!")
    else:
        click.echo("Failed to configure API key. Please try again.")

@cli.command()
def reset():
    """Reset the tool's configuration by clearing the API key"""
    config = Config()
    if config.clear_api_key():
        click.echo("Configuration reset successfully!")
    else:
        click.echo("Failed to reset configuration. Please try again.")

@cli.command()
@click.argument('query')
def translate(query: str):
    """Translate natural language to terminal command"""
    config = Config()
    if not config.validate_api_key():
        click.echo("Please configure your Anthropic API key first using 'cml configure'")
        return

    generator = CommandGenerator()
    try:
        command, _ = generator.generate_command(query)
        if command:
            click.echo(f"Command: {command}")
        else:
            click.echo("Could not generate a command. Please try rephrasing your request.")
    except Exception as e:
        click.echo(f"Error: {str(e)}")

if __name__ == "__main__":
    cli() 