"""Protocol definitions for the Secret Key Manager."""

from typing import Protocol, Optional, runtime_checkable


@runtime_checkable
class KeyProviderProtocol(Protocol):
    """Protocol for key provider plugins."""

    def get_key(self, key_name: str, **kwargs) -> Optional[str]:
        """
        Get a key from this provider.

        Args:
            key_name: The name of the key to retrieve
            **kwargs: Additional provider-specific arguments

        Returns:
            The key value if found, or None if not found
        """
        ...

    @property
    def name(self) -> str:
        """Get the name of this provider."""
        ...
