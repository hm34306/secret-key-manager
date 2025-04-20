"""Tests for the core module."""

from unittest.mock import patch, MagicMock

from secret_key_manager.core import (
    KeyProvider,
    KeyManager,
    get_registered_providers,
    initialize_providers,
)
from secret_key_manager.protocol import KeyProviderProtocol


# Test key provider decorator
def test_key_provider_decorator():
    # Reset registry to ensure test isolation
    from secret_key_manager.core import _PROVIDER_REGISTRY

    _PROVIDER_REGISTRY.clear()

    @KeyProvider(enabled=True, priority=50, name="test_provider")
    class TestKeyProvider:
        def get_key(self, key_name):
            return f"test-{key_name}"

    # Check if registered properly
    providers = get_registered_providers()
    assert len(providers) == 1
    assert providers[0]["name"] == "test_provider"
    assert providers[0]["enabled"] is True
    assert providers[0]["priority"] == 50
    assert providers[0]["class"] == TestKeyProvider


# Test auto-naming of providers
def test_key_provider_auto_naming():
    # Reset registry to ensure test isolation
    from secret_key_manager.core import _PROVIDER_REGISTRY

    _PROVIDER_REGISTRY.clear()

    @KeyProvider()
    class CustomKeyProvider:
        pass

    providers = get_registered_providers()
    assert len(providers) == 1
    assert providers[0]["name"] == "custom"


# Test initialize_providers
def test_initialize_providers():
    # Reset registry to ensure test isolation
    from secret_key_manager.core import _PROVIDER_REGISTRY

    _PROVIDER_REGISTRY.clear()

    @KeyProvider(enabled=True)
    class Provider1:
        def get_key(self, key_name):
            return None

    @KeyProvider(enabled=False)
    class Provider2:
        def get_key(self, key_name):
            return None

    providers = initialize_providers()
    assert len(providers) == 1  # Only the enabled one


# Test KeyManager singleton
def test_key_manager_singleton():
    manager1 = KeyManager()
    manager2 = KeyManager()
    assert manager1 is manager2


# Test KeyManager.get_key
def test_key_manager_get_key():
    # Reset the singleton
    KeyManager._instance = None
    manager = KeyManager()

    # Create a mock provider
    mock_provider = MagicMock(spec=KeyProviderProtocol)
    mock_provider.name = "mock"
    mock_provider.get_key.return_value = "test-key-value"

    # Register the mock provider
    manager._providers = [mock_provider]
    manager._initialized = True

    # Test getting a key
    key = manager.get_key("TEST_API_KEY")
    assert key == "test-key-value"
    mock_provider.get_key.assert_called_once_with("TEST_API_KEY")

    # Test that key was cached
    assert manager._keys["TEST_API_KEY"] == "test-key-value"

    # Test cached key is returned on subsequent calls
    mock_provider.get_key.reset_mock()
    key = manager.get_key("TEST_API_KEY")
    assert key == "test-key-value"
    mock_provider.get_key.assert_not_called()


# Test KeyManager.set_key
def test_key_manager_set_key():
    # Reset the singleton
    KeyManager._instance = None
    manager = KeyManager()

    # Set a key manually
    manager.set_key("MANUAL_KEY", "manual-value")

    # Check direct retrieval
    assert manager._keys["MANUAL_KEY"] == "manual-value"

    # Check get_key retrieval
    assert manager.get_key("MANUAL_KEY") == "manual-value"


# Test KeyManager.ensure_key
@patch("secret_key_manager.core.logger")
def test_key_manager_ensure_key(mock_logger):
    # Reset the singleton
    KeyManager._instance = None
    manager = KeyManager()

    # Set up a provider that will return a key
    mock_provider_success = MagicMock(spec=KeyProviderProtocol)
    mock_provider_success.name = "success"
    mock_provider_success.get_key.return_value = "exists"

    # Set up a provider that will not return a key
    mock_provider_fail = MagicMock(spec=KeyProviderProtocol)
    mock_provider_fail.name = "fail"
    mock_provider_fail.get_key.return_value = None

    # Test successful case
    manager._providers = [mock_provider_success]
    manager._initialized = True
    assert manager.ensure_key("EXISTS") is True
    mock_logger.error.assert_not_called()

    # Test failure case
    manager._providers = [mock_provider_fail]
    assert manager.ensure_key("MISSING") is False
    mock_logger.error.assert_called()


# Test KeyManager provider filtering
def test_key_manager_provider_filtering():
    # Reset the singleton
    KeyManager._instance = None
    manager = KeyManager()

    # Create multiple mock providers
    provider1 = MagicMock(spec=KeyProviderProtocol)
    provider1.name = "provider1"
    provider1.get_key.return_value = "value1"

    provider2 = MagicMock(spec=KeyProviderProtocol)
    provider2.name = "provider2"
    provider2.get_key.return_value = "value2"

    # Register providers
    manager._providers = [provider1, provider2]
    manager._initialized = True

    # Test filtering to use only provider2
    key = manager.get_key("TEST_KEY", providers=["provider2"])
    assert key == "value2"
    provider1.get_key.assert_not_called()
    provider2.get_key.assert_called_once()
