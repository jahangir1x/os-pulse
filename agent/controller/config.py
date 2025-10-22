"""
Configuration settings for the OS-Pulse Controller
"""
import os
from typing import Dict, Any
from pathlib import Path

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    # Load .env file from the agent directory (parent of controller)
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"[CONFIG] Loaded environment variables from {env_path}")
    else:
        print(f"[CONFIG] No .env file found at {env_path}")
except ImportError:
    print("[CONFIG] python-dotenv not installed, using system environment variables only")


class Config:
    """Configuration management for the controller"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.injector_dir = self.base_dir.parent / "injector"
        
        # Frida settings
        self.agent_script_path = self.injector_dir / "_agent.js"
        
        # Display settings
        self.colored_output = True
        self.max_content_display = 100  # Maximum characters to display for file content
        
        # API settings (for external API integration)
        self.api_enabled = os.getenv('OSPULSE_API_ENABLED', 'true').lower() == 'true'
        self.api_endpoint = os.getenv('OSPULSE_API_ENDPOINT', 'http://localhost:8080/api')
        self.api_key = os.getenv('OSPULSE_API_KEY', '')
        self.api_timeout = int(os.getenv('OSPULSE_API_TIMEOUT', '30'))
        self.api_retry_count = int(os.getenv('OSPULSE_API_RETRY_COUNT', '3'))
        self.api_retry_delay = int(os.getenv('OSPULSE_API_RETRY_DELAY', '1'))
        self.api_batch_size = int(os.getenv('OSPULSE_API_BATCH_SIZE', '10'))
        self.api_batch_timeout = int(os.getenv('OSPULSE_API_BATCH_TIMEOUT', '5'))
        
        # Logging settings
        self.log_level = os.getenv('OSPULSE_LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('OSPULSE_LOG_FILE', '')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'agent_script_path': str(self.agent_script_path),
            'colored_output': self.colored_output,
            'max_content_display': self.max_content_display,
            'api_enabled': self.api_enabled,
            'api_endpoint': self.api_endpoint,
            'api_timeout': self.api_timeout,
            'api_batch_size': self.api_batch_size,
            'log_level': self.log_level,
            'log_file': self.log_file
        }
    
    def validate(self) -> bool:
        """Validate configuration"""
        if not self.agent_script_path.exists():
            raise FileNotFoundError(f"Agent script not found: {self.agent_script_path}")
        
        return True


# Global configuration instance
config = Config()
