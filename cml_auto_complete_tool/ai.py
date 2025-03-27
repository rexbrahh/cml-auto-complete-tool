"""
AI-powered command generation module using Claude
"""
import os
from typing import Optional, Tuple

import anthropic
from dotenv import load_dotenv

from .config import Config

# Load environment variables
load_dotenv()

class CommandGenerator:
    def __init__(self):
        """Initialize the command generator with Anthropic API"""
        self.config = Config()
        self.client = None
        self.model = "claude-3.7-sonnet"  # Latest Claude model
        self.conversation_history = []
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the Anthropic client with API key"""
        api_key = self.config.get_api_key()
        if not api_key:
            raise ValueError("API key not configured. Please run 'cact init' to set up your API key.")
        self.client = anthropic.Anthropic(api_key=api_key)

    def handle_casual_input(self, user_input: str) -> Optional[str]:
        """
        Handle casual conversation and greetings
        
        Args:
            user_input: User's casual input like greetings
            
        Returns:
            Optional[str]: A friendly response or None if not a casual input
        """
        try:
            # Add user input to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # Prepare the system message for casual conversation
            system_message = """You are a direct and efficient terminal command assistant. Be concise and get straight to the point.
            For questions about who you are or your capabilities, give brief, direct answers without unnecessary pleasantries.
            If the user greets you, respond with a simple greeting and ask what command they need.
            If the input is not a greeting or casual conversation, respond with an empty string.
            Format your response as:
            RESPONSE: <direct response or empty>"""
            
            # Get response from Claude
            message = self.client.messages.create(
                model=self.model,
                max_tokens=150,
                temperature=0.7,
                system=system_message,
                messages=self.conversation_history
            )
            
            # Parse the response
            response_text = message.content[0].text
            if response_text.startswith('RESPONSE:'):
                response = response_text.replace('RESPONSE:', '').strip()
                if response:
                    self.conversation_history.append({"role": "assistant", "content": response})
                    return response
            return None
            
        except Exception as e:
            print(f"Error handling casual input: {str(e)}")
            return None

    def generate_command(self, user_input: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate a terminal command from natural language input
        
        Args:
            user_input: Natural language description of the desired command
            
        Returns:
            Tuple[Optional[str], Optional[str]]: (command, follow_up_question)
                - command: The generated command or None if more information is needed
                - follow_up_question: A question to ask the user if more information is needed
        """
        try:
            # First, try to handle casual conversation
            casual_response = self.handle_casual_input(user_input)
            if casual_response:
                return None, casual_response

            # Add user input to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # Prepare the system message
            system_message = """You are a direct and efficient terminal command expert. Convert natural language requests into appropriate terminal commands.
            If you need more information, ask a direct question without unnecessary pleasantries.
            Only output the command itself and any necessary questions. The command should be safe and follow best practices.
            If the request is unclear or potentially dangerous, respond with an empty string and a direct clarifying question.
            Format your response as:
            COMMAND: <command or empty>
            QUESTION: <direct question or empty>"""
            
            # Get response from Claude
            message = self.client.messages.create(
                model=self.model,
                max_tokens=150,
                temperature=0.5,
                system=system_message,
                messages=self.conversation_history
            )
            
            # Parse the response
            response_text = message.content[0].text
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            # Extract command and question
            command = None
            question = None
            
            for line in response_text.split('\n'):
                if line.startswith('COMMAND:'):
                    command = line.replace('COMMAND:', '').strip()
                elif line.startswith('QUESTION:'):
                    question = line.replace('QUESTION:', '').strip()
            
            return command, question
            
        except Exception as e:
            print(f"Error generating command: {str(e)}")
            return None, None 