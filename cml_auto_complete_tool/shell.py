"""
Interactive shell implementation for CML Auto-Complete Tool
"""
import os
import sys
from typing import Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory

from .ai import CommandGenerator
from .command import CommandExecutor

def print_color(text: str, color: str = None) -> None:
    """Print colored text if supported, otherwise plain text"""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'blue': '\033[94m',
        'yellow': '\033[93m',
        'bold': '\033[1m',
        'end': '\033[0m'
    }
    
    try:
        if color and color in colors and os.getenv('TERM') != 'dumb':
            print(f"{colors[color]}{text}{colors['end']}")
        else:
            print(text)
    except:
        print(text)

def ask_confirmation(prompt: str) -> bool:
    """Ask for user confirmation"""
    while True:
        response = input(f"{prompt} (y/n) ").lower().strip()
        if response in ['y', 'yes']:
            return True
        if response in ['n', 'no']:
            return False
        print("Please answer 'y' or 'n'")

class InteractiveShell:
    def __init__(self):
        self.history = InMemoryHistory()
        self.session = PromptSession(history=self.history)
        self.command_generator = CommandGenerator()
        self.command_executor = CommandExecutor()
        
        # Basic command completions
        self.completer = WordCompleter([
            "exit", "quit", "help", "clear", "pwd", "ls",
            "cd", "echo", "cat", "grep", "find", "mkdir",
            "rm", "cp", "mv", "chmod", "chown"
        ])

    def run(self) -> None:
        """Run the interactive shell"""
        print_color("Welcome to CML Auto-Complete Tool!", "green")
        print("Feel free to say hi or just tell me what command you're looking for.")
        print("Type 'exit' or 'quit' to end the session.\n")

        while True:
            try:
                # Get user input
                user_input = self.session.prompt(
                    "> ",
                    completer=self.completer
                ).strip()

                if user_input.lower() in ["exit", "quit"]:
                    break

                if not user_input:
                    continue

                # Generate command suggestion or handle casual conversation
                command, response = self.command_generator.generate_command(user_input)
                
                if not command and response:
                    # This is a casual conversation response
                    print_color(f"\n{response}", "blue")
                    continue
                
                # Handle follow-up questions
                while response and not command:
                    print_color(f"\n{response}", "blue")
                    follow_up = self.session.prompt("> ").strip()
                    if follow_up.lower() in ["exit", "quit"]:
                        break
                    command, response = self.command_generator.generate_command(follow_up)
                
                if not command and not response:
                    print_color("I couldn't understand that request. Feel free to rephrase it or ask for help!", "yellow")
                    continue

                # Show command and ask for confirmation
                print_color(f"\nSuggested command: {command}", "bold")
                    
                if ask_confirmation("Would you like me to execute this command?"):
                    try:
                        result = self.command_executor.execute(command)
                        print_color("\nCommand executed successfully!", "green")
                        if result:
                            print(f"\nOutput:\n{result}")
                    except ValueError as e:
                        print_color(f"Safety check failed: {str(e)}", "red")
                    except Exception as e:
                        print_color(f"Error executing command: {str(e)}", "red")

            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            except Exception as e:
                print_color(f"Error: {str(e)}", "red")

        print_color("\nThanks for chatting! Have a great day!", "green") 