"""Vault command-line key provider."""

import subprocess
import logging
from typing import Optional

from secret_key_manager.core import KeyProvider

# Configure logging
logger = logging.getLogger(__name__)


@KeyProvider(priority=20, name="vault")
class VaultKeyProvider:
    """Key provider that retrieves keys from the vault command."""
        
    def get_key(self, key_name: str, **kwargs) -> Optional[str]:
        """
        Get a key from the vault command.
        
        Args:
            key_name: Name of the key to retrieve
            **kwargs: Ignored
            
        Returns:
            The key value if successfully retrieved from vault, or None if not found
        """
        try:
            result = subprocess.run(
                ["vault", key_name],
                capture_output=True,
                text=True,
                check=True
            )
            key_value = result.stdout.strip()
            
            if key_value and len(key_value) > 0:
                return key_value
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            logger.debug(f"Failed to get {key_name} from vault: {e}")
        
        return None
