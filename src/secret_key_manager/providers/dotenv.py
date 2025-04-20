"""DotEnv file provider for loading keys from .env files."""

import os
import logging
import pathlib
from typing import Optional, Dict, Any

try:
    import dotenv
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False

from secret_key_manager.core import KeyProvider

# Configure logging
logger = logging.getLogger(__name__)


@KeyProvider(priority=25, name="dotenv")
class DotEnvProvider:
    """Key provider that retrieves and writes keys to a .env file."""
    
    def __init__(self, file_path: str = ".env"):
        """
        Initialize the .env file provider.
        
        Args:
            file_path: Path to the .env file (default: .env in the current directory)
        """
        if not HAS_DOTENV:
            logger.warning("python-dotenv package is not installed. DotEnv provider will not work.")
            raise ImportError("python-dotenv is required for DotEnvProvider")
            
        self.file_path = os.path.abspath(os.path.expanduser(file_path))
        self._env_values = {}
        self._load_dotenv()
    
    def _load_dotenv(self) -> None:
        """Load key-value pairs from the .env file."""
        if os.path.exists(self.file_path):
            try:
                # Load the .env file
                result = dotenv.load_dotenv(self.file_path)
                if result:
                    # Get all environment variables
                    self._env_values = dict(os.environ)
                    logger.debug(f"Loaded environment variables from {self.file_path}")
                else:
                    logger.warning(f"Failed to load .env file from {self.file_path}")
            except Exception as e:
                logger.error(f"Error loading .env file: {e}")
        else:
            logger.debug(f".env file not found at {self.file_path}")
    
    def get_key(self, key_name: str, **kwargs) -> Optional[str]:
        """
        Get a key from the .env file.
        
        Args:
            key_name: Name of the key to retrieve
            **kwargs: Additional parameters (file_path to override the default)
            
        Returns:
            The key value if found, None otherwise
        """
        # Check if file_path is provided in kwargs
        if "file_path" in kwargs and kwargs["file_path"] != self.file_path:
            file_path = os.path.abspath(os.path.expanduser(kwargs["file_path"]))
            # Load from the specified file
            try:
                values = dotenv.dotenv_values(file_path)
                return values.get(key_name)
            except Exception as e:
                logger.error(f"Error loading .env file {file_path}: {e}")
                return None
        
        # Reload the .env file to get the latest values
        self._load_dotenv()
        
        # Return the value from environment
        return self._env_values.get(key_name)
    
    def supports_write(self) -> bool:
        """Check if this provider supports writing keys."""
        return True
    
    def write_key(self, key_name: str, key_value: str, **kwargs) -> bool:
        """
        Write a key to the .env file.
        
        Args:
            key_name: Name of the key to write
            key_value: Value to write
            **kwargs: Additional parameters (file_path to override the default)
            
        Returns:
            True if successful, False otherwise
        """
        # Determine the file path
        file_path = os.path.abspath(os.path.expanduser(
            kwargs.get("file_path", self.file_path)
        ))
        
        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
            
            # Use dotenv.set_key to update the .env file
            dotenv.set_key(file_path, key_name, key_value, quote_mode="always")
            
            # Update the cached values
            self._load_dotenv()
            
            logger.debug(f"Successfully wrote key '{key_name}' to .env file {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing key '{key_name}' to .env file {file_path}: {e}")
            return False
    
    def validate_key(self, key_name: str, key_value: str, **kwargs) -> bool:
        """Validate a key before writing."""
        # Simple validation: key should not be empty, can add more validation as needed
        if not key_name or not key_name.strip():
            logger.warning("Key name cannot be empty")
            return False
        return True
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about this provider."""
        return {
            "name": self.name,
            "supports_write": self.supports_write(),
            "file_path": self.file_path
        }