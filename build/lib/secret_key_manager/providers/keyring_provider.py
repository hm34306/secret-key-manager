"""Keyring key provider."""

import logging
from typing import Optional

try:
    import keyring
    HAS_KEYRING = True
except ImportError:
    HAS_KEYRING = False

from secret_key_manager.core import KeyProvider

# Configure logging
logger = logging.getLogger(__name__)


@KeyProvider(enabled=HAS_KEYRING, priority=50, name="keyring")
class KeyringProvider:
    """Key provider that retrieves keys from the system keyring."""
    
    def __init__(self, service_name: str = "secret_key_manager"):
        """
        Initialize the keyring provider.
        
        Args:
            service_name: The service name to use in the keyring
        """
        self.service_name = service_name
        
        if not HAS_KEYRING:
            logger.warning("Keyring package is not installed. KeyringProvider is disabled.")
    
    def get_key(self, key_name: str, **kwargs) -> Optional[str]:
        """
        Get a key from the system keyring.
        
        Args:
            key_name: Name of the key to retrieve
            **kwargs: Additional arguments (ignored)
            
        Returns:
            The key value if found, or None if not found
        """
        if not HAS_KEYRING:
            return None
            
        try:
            key_value = keyring.get_password(self.service_name, key_name)
            if key_value:
                return key_value
        except Exception as e:
            logger.debug(f"Failed to get {key_name} from keyring: {e}")
            
        return None