"""
AI-powered command generation module
"""
import os
from typing import Optional, Tuple

import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CommandGenerator:
    def __init__(self):
        """Initialize the command generator with OpenAI API"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        openai.api_key = api_key
        self.model = "gpt-3.5-turbo"
        self.conversation_history = []

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
            # Add user input to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # Prepare the system message
            system_message = """You are a terminal command expert. Convert natural language requests into appropriate terminal commands.
            If you need more information to generate a command, ask a follow-up question.
            Only output the command itself, no explanations. The command should be safe and follow best practices.
            If the request is unclear or potentially dangerous, respond with an empty string.
            Format your response as:
            COMMAND: <command or empty>
            QUESTION: <follow-up question or empty>"""
            
            # Get response from OpenAI
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    *self.conversation_history
                ],
                temperature=0.3,
                max_tokens=150
            )
            
            # Parse the response
            response_text = response.choices[0].message.content.strip()
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