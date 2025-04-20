"""Core functionality for the Secret Key Manager."""

import os
import logging
from typing import Dict, Optional, List, Any, Type, TypeVar, Callable

from secret_key_manager.protocol import KeyProviderProtocol

# Configure logging
logger = logging.getLogger(__name__)

# Type for key provider classes
T = TypeVar("T")

# Registry to store provider classes with metadata
_PROVIDER_REGISTRY: Dict[str, Dict[str, Any]] = {}


def KeyProvider(
    enabled: bool = True, priority: int = 100, name: Optional[str] = None
) -> Callable[[Type[T]], Type[T]]:
    """
    Decorator to register a class as a key provider.

    Args:
        enabled: Whether this provider is enabled by default
        priority: Priority of this provider (lower numbers = higher priority)
        name: Custom name for this provider (defaults to class name)

    Returns:
        Decorator function for registering the provider
    """

    def decorator(cls: Type[T]) -> Type[T]:
        # Get the provider name (use custom name if provided, otherwise use class name)
        provider_name = name or cls.__name__
        if provider_name.endswith("KeyProvider"):
            provider_name = provider_name[:-11].lower()  # Remove 'KeyProvider' suffix

        # Store metadata in the registry
        _PROVIDER_REGISTRY[cls.__name__] = {
            "class": cls,
            "enabled": enabled,
            "priority": priority,
            "name": provider_name,
        }

        # Add name property if it doesn't exist
        if not hasattr(cls, "name"):
            setattr(cls, "name", property(lambda self: provider_name))

        logger.debug(
            f"Registered key provider: {cls.__name__} (enabled={enabled}, priority={priority})"
        )
        return cls

    return decorator


def get_registered_providers() -> List[Dict[str, Any]]:
    """
    Get all registered provider classes from the registry.

    Returns:
        List of provider metadata dictionaries, sorted by priority
    """
    providers = list(_PROVIDER_REGISTRY.values())
    # Sort by priority (lower number = higher priority)
    return sorted(providers, key=lambda p: p["priority"])


def initialize_providers() -> List[KeyProviderProtocol]:
    """
    Initialize all enabled provider classes.

    Returns:
        List of provider instances
    """
    provider_instances = []

    for provider_info in get_registered_providers():
        if provider_info["enabled"]:
            try:
                provider_class = provider_info["class"]
                provider_instance = provider_class()
                provider_instances.append(provider_instance)
                logger.debug(f"Initialized provider: {provider_info['name']}")
            except Exception as e:
                logger.warning(
                    f"Failed to initialize provider {provider_info['name']}: {e}"
                )

    return provider_instances


class KeyManager:
    """
    Singleton class for managing API keys with plugin providers.
    """

    _instance = None
    _keys: Dict[str, str] = {}
    _providers: List[KeyProviderProtocol] = []
    _initialized: bool = False

    def __new__(cls):
        """Ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super(KeyManager, cls).__new__(cls)
        return cls._instance

    def _initialize(self) -> None:
        """Initialize all providers if not already initialized."""
        if not self._initialized:
            self._providers = initialize_providers()
            self._initialized = True

    def register_provider(self, provider: KeyProviderProtocol) -> None:
        """
        Register a new key provider instance.

        Args:
            provider: The key provider to register
        """
        self._initialize()

        # Check if provider with the same name already exists
        for existing_provider in self._providers:
            if existing_provider.name == provider.name:
                logger.warning(
                    f"A provider with name '{provider.name}' is already registered. Skipping."
                )
                return

        # Add the provider
        self._providers.append(provider)
        logger.debug(f"Registered key provider instance: {provider.name}")

    def get_providers(self) -> List[str]:
        """
        Get a list of registered provider names.

        Returns:
            List of provider names
        """
        self._initialize()
        return [provider.name for provider in self._providers]

    def enable_provider(self, name: str) -> bool:
        """
        Enable a key provider by name.

        Args:
            name: Name of the provider to enable

        Returns:
            True if successful, False if provider not found
        """
        for provider_info in _PROVIDER_REGISTRY.values():
            if provider_info["name"] == name:
                provider_info["enabled"] = True
                # Re-initialize providers
                self._initialized = False
                self._initialize()
                return True
        return False

    def disable_provider(self, name: str) -> bool:
        """
        Disable a key provider by name.

        Args:
            name: Name of the provider to disable

        Returns:
            True if successful, False if provider not found
        """
        for provider_info in _PROVIDER_REGISTRY.values():
            if provider_info["name"] == name:
                provider_info["enabled"] = False
                # Re-initialize providers
                self._initialized = False
                self._initialize()
                return True
        return False

    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the status of all registered providers.

        Returns:
            Dictionary of provider names to status information
        """
        self._initialize()

        result = {}
        for provider_info in _PROVIDER_REGISTRY.values():
            provider_name = provider_info["name"]
            # Find the corresponding provider instance to get capabilities
            provider_instance = next(
                (p for p in self._providers if p.name == provider_name), None
            )

            status = {
                "enabled": provider_info["enabled"],
                "priority": provider_info["priority"],
                "class": provider_info["class"].__name__,
                "supports_write": False,
                "capabilities": {},
            }

            # Add capabilities information if the provider instance is available
            if provider_instance:
                # Check for supports_write method
                if hasattr(provider_instance, "supports_write"):
                    status["supports_write"] = provider_instance.supports_write()

                # Check for get_provider_info method
                if hasattr(provider_instance, "get_provider_info"):
                    try:
                        status["capabilities"] = provider_instance.get_provider_info()
                    except Exception as e:
                        logger.warning(
                            f"Error getting provider info for '{provider_name}': {e}"
                        )

            result[provider_name] = status

        return result

    def get_writable_providers(self) -> List[str]:
        """
        Get a list of provider names that support writing keys.

        Returns:
            List of provider names that support writing
        """
        self._initialize()

        writable_providers = []
        for provider in self._providers:
            if hasattr(provider, "supports_write") and provider.supports_write():
                writable_providers.append(provider.name)

        return writable_providers

    def get_key(
        self, key_name: str, providers: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Get an API key by name. If the key doesn't exist, attempt to load it.

        Args:
            key_name: The name of the key to get
            providers: Optional list of specific provider names to use

        Returns:
            The API key if found, or None if not found
        """
        self._initialize()

        # If the key is already loaded, return it
        if key_name in self._keys and self._keys[key_name]:
            return self._keys[key_name]

        # Filter providers if specified
        active_providers = self._providers
        if providers:
            active_providers = [p for p in self._providers if p.name in providers]

        # Try each provider in order
        for provider in active_providers:
            try:
                key_value = provider.get_key(key_name)
                if key_value:
                    # Set the key in our dictionary
                    self._keys[key_name] = key_value
                    # Optionally set it in the environment too for better compatibility
                    os.environ[key_name] = key_value
                    logger.debug(
                        f"Retrieved key '{key_name}' from provider '{provider.name}'"
                    )
                    return key_value
            except Exception as e:
                logger.warning(f"Error in provider '{provider.name}': {e}")

        # If we get here, the key could not be found
        return None

    def set_key(
        self,
        key_name: str,
        key_value: str,
        persist: bool = False,
        providers: Optional[List[str]] = None,
    ) -> bool:
        """
        Set an API key by name and optionally persist it to providers that support writing.

        Args:
            key_name: The name of the key to set
            key_value: The value to set the key to
            persist: Whether to persist the key to providers that support writing
            providers: Optional list of specific provider names to use for persistence

        Returns:
            True if the key was successfully persisted (or persistence was not requested),
            False if persistence was requested but failed
        """
        # Always set the key in memory
        self._keys[key_name] = key_value

        # If persistence is not requested, we're done
        if not persist:
            return True

        # Initialize providers if needed
        self._initialize()

        # Filter providers if specified
        active_providers = self._providers
        if providers:
            active_providers = [p for p in self._providers if p.name in providers]

        # Try to persist the key to each provider that supports writing
        success = False
        for provider in active_providers:
            # Skip providers that don't support writing
            if not hasattr(provider, "supports_write") or not provider.supports_write():
                continue

            # Validate the key before writing
            if hasattr(provider, "validate_key") and not provider.validate_key(
                key_name, key_value
            ):
                logger.warning(
                    f"Key '{key_name}' failed validation for provider '{provider.name}'"
                )
                continue

            # Try to write the key
            try:
                if provider.write_key(key_name, key_value):
                    logger.debug(
                        f"Successfully wrote key '{key_name}' to provider '{provider.name}'"
                    )
                    success = True
            except Exception as e:
                logger.warning(
                    f"Error writing key '{key_name}' to provider '{provider.name}': {e}"
                )

        return success

    def ensure_key(self, key_name: str, providers: Optional[List[str]] = None) -> bool:
        """
        Ensure that a key is available, printing an error if not.

        Args:
            key_name: The name of the key to ensure
            providers: Optional list of specific provider names to use

        Returns:
            True if the key is available, False otherwise
        """
        self._initialize()

        key = self.get_key(key_name, providers)
        if not key:
            logger.error(f"ERROR: {key_name} is not set.")

            # List the providers that were tried
            provider_names = self.get_providers() if providers is None else providers
            logger.error(f"Tried providers: {', '.join(provider_names)}")
            return False
        return True


# Singleton instance
keys = KeyManager()
