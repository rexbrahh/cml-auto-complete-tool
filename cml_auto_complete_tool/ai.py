"""
AI-powered command generation module using Claude
"""
import os
import logging
import sys
import re
from typing import Optional, Tuple, Dict, List, Any

try:
    import anthropic
    # Get the anthropic library version for debugging
    ANTHROPIC_VERSION = anthropic.__version__
except ImportError:
    anthropic = None
    ANTHROPIC_VERSION = "Not installed"
except Exception:
    ANTHROPIC_VERSION = "Error getting version"

from dotenv import load_dotenv

from .config import Config

# Load environment variables
load_dotenv()

# Set up logging to file
log_dir = os.path.expanduser("~/.cact-venv")
if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)
    
logging.basicConfig(
    level=logging.INFO,  # Changed to INFO to capture more details
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join(log_dir, 'cact.log')
)
logger = logging.getLogger('cact')

# Enable console output for critical errors
console = logging.StreamHandler()
console.setLevel(logging.CRITICAL)
logger.addHandler(console)

# Log system and library information for debugging
logger.info(f"Python version: {sys.version}")
logger.info(f"Anthropic library version: {ANTHROPIC_VERSION}")
logger.info(f"Operating system: {sys.platform}")

# Enable debug mode for offline development without API keys
DEBUG_MODE = os.environ.get("CACT_DEBUG", "").lower() in ["true", "1", "yes"]
if DEBUG_MODE:
    logger.info("Running in DEBUG_MODE - API calls will be simulated")

# Parse version numbers
def parse_version(version_str: str) -> tuple:
    """Parse version string into tuple for comparison"""
    if not version_str or version_str == "Not installed" or version_str == "Error getting version":
        return (0, 0, 0)
    
    # Extract version numbers
    match = re.match(r'(\d+)\.(\d+)\.(\d+)', version_str)
    if match:
        return tuple(map(int, match.groups()))
    return (0, 0, 0)

# Get version information
ANTHROPIC_VERSION_TUPLE = parse_version(ANTHROPIC_VERSION)
IS_ANTHROPIC_V0 = ANTHROPIC_VERSION_TUPLE[0] == 0
logger.info(f"Anthropic version tuple: {ANTHROPIC_VERSION_TUPLE}")
logger.info(f"Using V0 API: {IS_ANTHROPIC_V0}")

class CommandGenerator:
    def __init__(self):
        """Initialize the command generator with Anthropic API"""
        self.config = Config()
        self.client = None
        # Use correct model name format based on API version
        if IS_ANTHROPIC_V0:
            self.model = "claude-3-sonnet-20240229"  # Legacy format for v0 API
        else:
            self.model = "claude-3-sonnet"  # New format for v1+ API
        
        self.conversation_history = []
        self.auth_error = False
        
        # Initialize client only if not in debug mode
        if not DEBUG_MODE:
            self._initialize_client()
        else:
            logger.info("Skipping API client initialization in debug mode")

    def _initialize_client(self) -> None:
        """Initialize the Anthropic client with API key"""
        api_key = self.config.get_api_key()
        if not api_key:
            raise ValueError("API key not configured. Please run 'cact init' to set up your API key.")
        
        try:
            # Log API key format info for debugging (just first/last 4 chars)
            if len(api_key) > 8:
                logger.info(f"API key format: {api_key[:4]}...{api_key[-4:]} (length: {len(api_key)})")
                # Check for expected Anthropic key format
                if not api_key.startswith("sk-ant-") and not api_key.startswith("sk-"):
                    logger.warning("API key doesn't have expected 'sk-ant-' or 'sk-' prefix")
            else:
                logger.warning("API key too short")
            
            # Try initialization based on version
            if IS_ANTHROPIC_V0:
                # Legacy Anthropic client
                self.client = anthropic.Anthropic(api_key=api_key)
                logger.info("Initialized v0 Anthropic client")
            else:
                # Modern Anthropic client
                self.client = anthropic.Anthropic(api_key=api_key)
                logger.info("Initialized v1+ Anthropic client")
                
        except Exception as e:
            logger.error(f"Error initializing client: {str(e)}")
            self.auth_error = True

    def _mock_response(self, query: str, response_type: str = "command") -> str:
        """Generate mock responses for debug mode"""
        query = query.lower()
        
        if response_type == "casual":
            if "hi" in query or "hello" in query:
                return "Hello! How can I help you with terminal commands today?"
            if "who are you" in query:
                return "I'm an AI assistant that helps with terminal commands. I'm currently in debug mode."
            if "help" in query:
                return "I can help translate natural language to terminal commands. Just describe what you want to do."
            return None
            
        # Command responses
        if "list" in query and "file" in query:
            return "ls -la"
        if "current directory" in query:
            return "pwd"
        if "make directory" in query:
            parts = query.split("directory")
            if len(parts) > 1:
                dir_name = parts[1].strip()
                return f"mkdir {dir_name}"
            return "mkdir new_directory"
        if "search" in query or "find" in query:
            search_term = query.split("for")[-1].strip() if "for" in query else "pattern"
            return f"grep -r '{search_term}' ."
        
        # Default response
        return None

    def _call_anthropic_api(self, messages: List[Dict[str, str]], system_message: str) -> Dict[str, Any]:
        """Make API call with version-specific format"""
        try:
            if IS_ANTHROPIC_V0:
                # Legacy API format (v0)
                return self.client.messages.create(
                    model=self.model,
                    max_tokens=150,
                    temperature=0.7,
                    system=system_message,
                    messages=messages
                )
            else:
                # Modern API format (v1+)
                return self.client.messages.create(
                    model=self.model,
                    max_tokens=150,
                    temperature=0.7,
                    system=system_message,
                    messages=messages
                )
        except Exception as e:
            logger.error(f"API call error: {str(e)}")
            raise

    def handle_casual_input(self, user_input: str) -> Optional[str]:
        """
        Handle casual conversation and greetings
        
        Args:
            user_input: User's casual input like greetings
            
        Returns:
            Optional[str]: A friendly response or None if not a casual input
        """
        # Return quickly if we already know there's an auth error
        if self.auth_error:
            return "I'm having trouble with my API connection. Please try resetting your API key with 'cact reset' and then 'cact init'. If you're developing, set CACT_DEBUG=true for offline mode."
        
        # Use mock response in debug mode    
        if DEBUG_MODE:
            response = self._mock_response(user_input, "casual")
            if response:
                return response
            return None
            
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
            
            # Get response from Claude using version-specific call
            message = self._call_anthropic_api(self.conversation_history, system_message)
            
            # Parse the response
            response_text = message.content[0].text
            if response_text.startswith('RESPONSE:'):
                response = response_text.replace('RESPONSE:', '').strip()
                if response:
                    self.conversation_history.append({"role": "assistant", "content": response})
                    return response
            return None
            
        except anthropic.APIError as e:
            # Log error but don't show technical details to user
            logger.error(f"API error in casual input: {str(e)}")
            
            # Check if it's an authentication error
            if "authentication_error" in str(e) or "invalid" in str(e) and "api-key" in str(e):
                self.auth_error = True
                return "API authentication error: Please verify your API key is correct and has access to the Claude model. Try 'export CACT_DEBUG=true' for offline mode."
            
            # Generic error
            return "I'm having trouble processing your request right now."
            
        except Exception as e:
            # Log other errors
            logger.error(f"Error handling casual input: {str(e)}")
            return "I encountered an unexpected issue. Please try again."

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
        # Return quickly if we already know there's an auth error
        if self.auth_error:
            return None, "I'm having trouble with my API connection. Please try resetting your API key with 'cact reset' and then 'cact init'. If you're developing, set CACT_DEBUG=true for offline mode."
        
        # Use mock responses in debug mode
        if DEBUG_MODE:
            # First try casual handling
            casual_response = self._mock_response(user_input, "casual")
            if casual_response:
                return None, casual_response
                
            # Then try command generation
            command = self._mock_response(user_input, "command")
            if command:
                return command, None
            return None, "I couldn't understand that request in debug mode. Try 'list files' or 'current directory'."
            
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
            
            # Get response from Claude using version-specific call
            message = self._call_anthropic_api(self.conversation_history, system_message)
            
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
            
        except anthropic.APIError as e:
            # Log error but don't show technical details to user
            logger.error(f"API error in command generation: {str(e)}")
            
            # Check if it's an authentication error
            if "authentication_error" in str(e) or "invalid" in str(e) and "api-key" in str(e):
                self.auth_error = True
                return None, "API authentication error: Please verify your API key is correct and has access to the Claude model. Try 'export CACT_DEBUG=true' for offline mode."
            
            # Generic error
            return None, "I'm having trouble processing your request right now."
            
        except Exception as e:
            # Log other errors
            logger.error(f"Error generating command: {str(e)}")
            return None, "I encountered an unexpected issue. Please try the DEBUG_MODE." 