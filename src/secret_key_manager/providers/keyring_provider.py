"""Keyring-based key provider."""

import logging
import keyring
from typing import Optional, Dict, Any

from secret_key_manager.core import KeyProvider

# Configure logging
logger = logging.getLogger(__name__)


@KeyProvider(priority=50, name="keyring")
class KeyringProvider:
    """Key provider that retrieves keys from the system keyring."""

    def __init__(self, service_name: str = "secret_key_manager"):
        """
        Initialize the keyring provider.

        Args:
            service_name: The service name to use for keyring lookups
        """
        self.service_name = service_name

    def get_key(self, key_name: str, **kwargs) -> Optional[str]:
        """
        Get a key from the system keyring.

        Args:
            key_name: Name of the key to retrieve
            **kwargs: Optional arguments:
                - service_name: Override the service name

        Returns:
            The key value if found in the keyring, or None if not found
        """
        # Get the service name
        service_name = kwargs.get("service_name", self.service_name)

        try:
            # Get the key from the keyring
            key_value = keyring.get_password(service_name, key_name)

            # Return key if found
            if key_value is not None:
                return key_value
        except Exception as e:
            logger.warning(f"Error retrieving key '{key_name}' from keyring: {e}")

        return None

    def supports_write(self) -> bool:
        """Check if this provider supports writing keys."""
        return True

    def write_key(self, key_name: str, key_value: str, **kwargs) -> bool:
        """
        Write a key to the system keyring.

        Args:
            key_name: Name of the key to write
            key_value: Value to write to the keyring
            **kwargs: Optional arguments:
                - service_name: Override the service name

        Returns:
            True if the key was successfully written, False otherwise
        """
        # Get the service name
        service_name = kwargs.get("service_name", self.service_name)

        try:
            # Write the key to the keyring
            keyring.set_password(service_name, key_name, key_value)
            logger.debug(
                f"Successfully wrote key '{key_name}' to keyring service '{service_name}'"
            )
            return True
        except Exception as e:
            logger.error(f"Error writing key '{key_name}' to keyring: {e}")
            return False

    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about this provider."""
        return {
            "name": self.name,
            "supports_write": self.supports_write(),
            "service_name": self.service_name,
            "backend": str(keyring.get_keyring().__class__.__name__),
        }
