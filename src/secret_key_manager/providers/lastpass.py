"""LastPass CLI key provider."""

import subprocess
import logging
from typing import Optional

from secret_key_manager.core import KeyProvider

# Configure logging
logger = logging.getLogger(__name__)


@KeyProvider(priority=40, name="lastpass")
class LastPassKeyProvider:
    """Key provider that retrieves keys from LastPass CLI."""
    
    def __init__(self):
        """Initialize the LastPass CLI provider."""
        self._check_olp_installed()
    
    def _check_olp_installed(self) -> None:
        """Check if the LastPass CLI is installed and accessible."""
        try:
            subprocess.run(
                ["olp", "--help"],
                capture_output=True,
                text=True
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.error(
                "LastPass CLI not found. Please make sure it's installed and available in your PATH."
            )
            raise RuntimeError("LastPass CLI (olp) not installed")
        
    def get_key(self, key_name: str, **kwargs) -> Optional[str]:
        """
        Get a key from the LastPass CLI.
        
        Args:
            key_name: Name of the key to retrieve
            **kwargs: Ignored
            
        Returns:
            The key value if successfully retrieved from LastPass, or None if not found
        """
        try:
            result = subprocess.run(
                ["olp", key_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout:
                key_value = result.stdout.strip()
                if key_value:
                    return key_value
        except subprocess.SubprocessError as e:
            logger.debug(f"Failed to get {key_name} from LastPass: {e}")
        
        return None