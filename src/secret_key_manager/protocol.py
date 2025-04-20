"""Protocol definitions for the Secret Key Manager."""

from typing import Protocol, Optional, Dict, Any, runtime_checkable


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
    
    def supports_write(self) -> bool:
        """
        Check if this provider supports writing keys.
        
        Returns:
            True if the provider supports writing keys, False otherwise
        """
        return False
    
    def write_key(self, key_name: str, key_value: str, **kwargs) -> bool:
        """
        Write a key to this provider.
        
        Args:
            key_name: The name of the key to write
            key_value: The value to write
            **kwargs: Additional provider-specific arguments
            
        Returns:
            True if the key was successfully written, False otherwise
        """
        return False
    
    def validate_key(self, key_name: str, key_value: str, **kwargs) -> bool:
        """
        Validate that a key value meets the requirements for this provider.
        
        Args:
            key_name: The name of the key to validate
            key_value: The value to validate
            **kwargs: Additional provider-specific arguments
            
        Returns:
            True if the key is valid, False otherwise
        """
        return True
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about this provider.
        
        Returns:
            Dictionary containing provider capabilities and metadata
        """
        return {
            "name": self.name,
            "supports_write": self.supports_write(),
        }