"""Test fixtures for the Secret Key Manager tests."""

import pytest
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)


@pytest.fixture(autouse=True)
def reset_registry():
    """Reset the provider registry between tests to ensure isolation."""
    from secret_key_manager.core import _PROVIDER_REGISTRY

    # Store original registry
    original = dict(_PROVIDER_REGISTRY)

    # Clear registry for each test
    _PROVIDER_REGISTRY.clear()

    yield

    # Restore original registry after test
    _PROVIDER_REGISTRY.clear()
    _PROVIDER_REGISTRY.update(original)


@pytest.fixture(autouse=True)
def reset_key_manager():
    """Reset the KeyManager singleton between tests."""
    from secret_key_manager.core import KeyManager

    # Store original instance
    original_instance = KeyManager._instance
    original_keys = dict(KeyManager._keys) if KeyManager._instance else {}
    original_providers = list(KeyManager._providers) if KeyManager._instance else []
    original_initialized = KeyManager._initialized if KeyManager._instance else False

    # Reset for test
    KeyManager._instance = None
    KeyManager._keys = {}
    KeyManager._providers = []
    KeyManager._initialized = False

    yield

    # Restore original state
    KeyManager._instance = original_instance
    KeyManager._keys = original_keys
    KeyManager._providers = original_providers
    KeyManager._initialized = original_initialized
