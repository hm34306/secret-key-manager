"""Environment variable key provider."""

import os
from typing import Optional

from secret_key_manager.core import KeyProvider


@KeyProvider(priority=10, name="environment")
class EnvKeyProvider:
    """Key provider that retrieves keys from environment variables."""
        
    def get_key(self, key_name: str, **kwargs) -> Optional[str]:
        """
        Get a key from environment variables.
        
        Args:
            key_name: Name of the key to retrieve
            **kwargs: Ignored
            
        Returns:
            The key value if found in environment, or None if not found
        """
        key_value = os.getenv(key_name)
        if key_value and len(key_value) > 0:
            return key_value
        return None
