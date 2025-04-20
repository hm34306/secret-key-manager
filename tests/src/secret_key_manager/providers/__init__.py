"""Built-in key providers for the Secret Key Manager."""

from secret_key_manager.providers.env import EnvKeyProvider
from secret_key_manager.providers.vault import VaultKeyProvider
from secret_key_manager.providers.file import JsonFileKeyProvider, YamlFileKeyProvider

# Conditionally import keyring provider
try:
    from secret_key_manager.providers.keyring_provider import KeyringProvider

    __all__ = [
        "EnvKeyProvider",
        "VaultKeyProvider",
        "JsonFileKeyProvider",
        "YamlFileKeyProvider",
        "KeyringProvider",
    ]
except ImportError:
    __all__ = [
        "EnvKeyProvider",
        "VaultKeyProvider",
        "JsonFileKeyProvider",
        "YamlFileKeyProvider",
    ]
