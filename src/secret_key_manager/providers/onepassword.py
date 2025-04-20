"""1Password CLI key provider."""

import subprocess
import logging
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

from secret_key_manager.core import KeyProvider

# Configure logging
logger = logging.getLogger(__name__)

# Default config values
DEFAULT_CONFIG = {
    "account": "my.1password.com",
    "env_file": "~/.local/.env"
}


@KeyProvider(priority=30, name="1password")
class OnePasswordKeyProvider:
    """Key provider that retrieves keys from the 1Password CLI (op)."""
    
    def __init__(self):
        """Initialize the 1Password CLI provider."""
        self.config = self._load_config()
        self._check_op_installed()
    
    def _check_op_installed(self) -> None:
        """Check if the 1Password CLI is installed and accessible."""
        try:
            subprocess.run(
                ["op", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.error(
                "1Password CLI not found. Please install it from: "
                "https://1password.com/downloads/command-line/"
            )
            raise RuntimeError("1Password CLI (op) not installed")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from config file or use defaults."""
        config_dir = Path(os.path.expanduser("~/.local/secret-key-manager"))
        config_file = config_dir / ".config"
        
        if not config_dir.exists():
            os.makedirs(config_dir, exist_ok=True)
        
        config = DEFAULT_CONFIG.copy()
        
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    file_config = json.load(f)
                    config.update(file_config)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load 1Password config: {e}")
        else:
            # Create default config file
            try:
                with open(config_file, "w") as f:
                    json.dump(DEFAULT_CONFIG, f, indent=2)
            except IOError as e:
                logger.warning(f"Failed to create default 1Password config: {e}")
        
        return config
        
    def get_key(self, key_name: str, **kwargs) -> Optional[str]:
        """
        Get a key from the 1Password CLI.
        
        Args:
            key_name: Name of the key to retrieve
            **kwargs: Additional provider-specific arguments
            
        Returns:
            The key value if successfully retrieved from 1Password, or None if not found
        """
        account = kwargs.get("account", self.config.get("account"))
        env_file = os.path.expanduser(kwargs.get("env_file", self.config.get("env_file")))
        
        try:
            # First sign in to 1Password
            subprocess.run(
                ["op", "signin", "--account", account],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Then retrieve the key
            result = subprocess.run(
                ["op", "run", f"--env-file={env_file}", "--no-masking", "--", "printenv", key_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout:
                key_value = result.stdout.strip()
                if key_value:
                    return key_value
        except subprocess.SubprocessError as e:
            logger.debug(f"Failed to get {key_name} from 1Password: {e}")
        
        return None