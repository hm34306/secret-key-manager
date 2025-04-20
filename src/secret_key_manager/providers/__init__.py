"""Built-in key providers for the Secret Key Manager."""

import importlib.util
from secret_key_manager.providers.env import EnvKeyProvider
from secret_key_manager.providers.vault import VaultKeyProvider
from secret_key_manager.providers.file import JsonFileKeyProvider, YamlFileKeyProvider

# Import DotEnv provider
if importlib.util.find_spec("secret_key_manager.providers.dotenv"):
    from secret_key_manager.providers.dotenv import DotEnvProvider  # noqa: F401

    HAS_DOTENV = True
else:
    HAS_DOTENV = False

# Import 1Password provider
if importlib.util.find_spec("secret_key_manager.providers.onepassword"):
    from secret_key_manager.providers.onepassword import OnePasswordKeyProvider  # noqa: F401

    HAS_1PASSWORD = True
else:
    HAS_1PASSWORD = False

# Import LastPass provider
if importlib.util.find_spec("secret_key_manager.providers.lastpass"):
    from secret_key_manager.providers.lastpass import LastPassKeyProvider  # noqa: F401

    HAS_LASTPASS = True
else:
    HAS_LASTPASS = False

# Conditionally import keyring provider
if importlib.util.find_spec("secret_key_manager.providers.keyring_provider"):
    from secret_key_manager.providers.keyring_provider import KeyringProvider  # noqa: F401

    HAS_KEYRING = True
else:
    HAS_KEYRING = False

# Build __all__ based on available providers
__all__ = [
    "EnvKeyProvider",
    "VaultKeyProvider",
    "JsonFileKeyProvider",
    "YamlFileKeyProvider",
]

if HAS_DOTENV:
    __all__.append("DotEnvProvider")

if HAS_1PASSWORD:
    __all__.append("OnePasswordKeyProvider")

if HAS_LASTPASS:
    __all__.append("LastPassKeyProvider")

if HAS_KEYRING:
    __all__.append("KeyringProvider")
