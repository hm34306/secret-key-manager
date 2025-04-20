"""Example of a custom key provider."""

from typing import Optional
from secret_key_manager import KeyProvider


@KeyProvider(priority=50, name="custom_example")
class CustomExampleProvider:
    """A custom example key provider that always returns a fixed value for a specific key."""
    
    def __init__(self):
        self.secrets = {
            "MY_API_KEY": "example-api-key-value",
            "MY_OTHER_KEY": "example-other-value"
        }
    
    def get_key(self, key_name: str, **kwargs) -> Optional[str]:
        """Get a key from the predefined secrets dictionary."""
        return self.secrets.get(key_name)
