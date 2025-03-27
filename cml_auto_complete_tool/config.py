"""
Configuration management module
"""
import json
import os
from pathlib import Path
from typing import Optional

class Config:
    def __init__(self):
        """Initialize configuration manager"""
        self.config_dir = Path.home() / ".cml-auto-complete-tool"
        self.config_file = self.config_dir / "config.json"
        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists"""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def get_api_key(self) -> Optional[str]:
        """Get the Anthropic API key from configuration"""
        if not self.config_file.exists():
            return None
            
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                return config.get('anthropic_api_key')
        except Exception:
            return None

    def set_api_key(self, api_key: str) -> bool:
        """
        Set the Anthropic API key in configuration
        
        Args:
            api_key: The API key to store
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            config = {}
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            
            config['anthropic_api_key'] = api_key
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
            return True
        except Exception:
            return False

    def clear_api_key(self) -> bool:
        """
        Clear the API key from configuration
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                if 'anthropic_api_key' in config:
                    del config['anthropic_api_key']
                    
                    with open(self.config_file, 'w') as f:
                        json.dump(config, f)
            return True
        except Exception:
            return False

    def validate_api_key(self) -> bool:
        """
        Validate if API key is configured and valid
        
        Returns:
            bool: True if API key is valid, False otherwise
        """
        api_key = self.get_api_key()
        return bool(api_key and len(api_key.strip()) > 0) 