"""Built-in key providers for the Secret Key Manager."""

from secret_key_manager.providers.env import EnvKeyProvider
from secret_key_manager.providers.vault import VaultKeyProvider
from secret_key_manager.providers.file import JsonFileKeyProvider, YamlFileKeyProvider

# Import DotEnv provider
try:
    from secret_key_manager.providers.dotenv import DotEnvProvider
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False

# Import 1Password provider
try:
    from secret_key_manager.providers.onepassword import OnePasswordKeyProvider
    HAS_1PASSWORD = True
except (ImportError, RuntimeError):
    HAS_1PASSWORD = False

# Import LastPass provider
try:
    from secret_key_manager.providers.lastpass import LastPassKeyProvider
    HAS_LASTPASS = True
except (ImportError, RuntimeError):
    HAS_LASTPASS = False

# Conditionally import keyring provider
try:
    from secret_key_manager.providers.keyring_provider import KeyringProvider
    HAS_KEYRING = True
except ImportError:
    HAS_KEYRING = False

# Build __all__ based on available providers
__all__ = ["EnvKeyProvider", "VaultKeyProvider", "JsonFileKeyProvider", "YamlFileKeyProvider"]

if HAS_DOTENV:
    __all__.append("DotEnvProvider")

if HAS_1PASSWORD:
    __all__.append("OnePasswordKeyProvider")

if HAS_LASTPASS:
    __all__.append("LastPassKeyProvider")

if HAS_KEYRING:
    __all__.append("KeyringProvider")