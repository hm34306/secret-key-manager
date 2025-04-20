# Secret Key Manager Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Basic Usage](#basic-usage)
4. [Command-Line Interface](#command-line-interface)
5. [Built-in Providers](#built-in-providers)
6. [Creating Custom Providers](#creating-custom-providers)
7. [Advanced Usage](#advanced-usage)

## Introduction

Secret Key Manager is a flexible key management system that allows you to retrieve API keys and other secrets from various sources through a plugin-based architecture.

### Key Features

- **Plugin-based architecture**: Easily extend with custom key providers
- **Decorator-based registration**: Register new providers with a simple decorator
- **Priority-based retrieval**: Configure which providers are tried first
- **Multiple built-in providers**: Environment variables, command-line tools, and file-based providers
- **Command-line interface**: Manage keys and providers from the terminal

## Installation

### Basic Installation

```bash
pip install secret-key-manager
```

### Installing Optional Dependencies

For YAML file support:
```bash
pip install secret-key-manager[yaml]
```

For all optional features:
```bash
pip install secret-key-manager[all]
```

## Basic Usage

### Getting a Key

```python
from secret_key_manager import keys

# Get a key (tries all enabled providers)
api_key = keys.get_key("MY_API_KEY")

# Use a specific provider
api_key = keys.get_key("MY_API_KEY", providers=["environment"])
```

### Setting a Key

```python
from secret_key_manager import keys

# Set a key in memory (doesn't persist to any provider)
keys.set_key("MY_API_KEY", "my-secret-value")

# Set a key and persist it to all writable providers
keys.set_key("MY_API_KEY", "my-secret-value", persist=True)

# Set a key and persist it to specific providers
keys.set_key("MY_API_KEY", "my-secret-value", persist=True, providers=["json_file"])

# Get a list of providers that support writing
writable_providers = keys.get_writable_providers()
print(f"Available writable providers: {writable_providers}")
```

### Checking if a Key is Available

```python
from secret_key_manager import keys

if keys.ensure_key("MY_API_KEY"):
    # Key is available
    pass
else:
    # Key is not available
    pass
```

## Command-Line Interface

Secret Key Manager includes a command-line interface called `skm`.

### Getting a Key

```bash
# Get a key (tries all enabled providers)
skm get MY_API_KEY

# Get a key from a specific provider
skm get MY_API_KEY --provider environment
```

### Setting a Key

```bash
# Set a key (persists to all writable providers)
skm set MY_API_KEY my-secret-value

# Set a key to a specific provider
skm set MY_API_KEY my-secret-value --provider json_file

# Set a key in memory only (no persistence)
skm set MY_API_KEY my-secret-value --no-persist
```

### Managing Providers

```bash
# List active providers
skm providers list

# Show provider status (including write capability)
skm providers status

# List providers that support writing
skm providers writable

# Enable a provider
skm providers enable json_file

# Disable a provider
skm providers disable vault
```

## Built-in Providers

### Environment Variables Provider

The simplest provider that gets keys from environment variables.

- **Priority**: 10 (highest priority)
- **Class**: `EnvKeyProvider`
- **Name**: `env`

Usage:
```bash
export MY_API_KEY=your-api-key-value
```

### Vault Command Provider

Provider that executes the `vault` command-line tool to retrieve keys.

- **Priority**: 20
- **Class**: `VaultKeyProvider`
- **Name**: `vault`

Usage:
```bash
# The vault command should output the key value when called with the key name
vault MY_API_KEY
```

### DotEnv Provider

Provider that reads from and writes to `.env` files using the python-dotenv package.

- **Priority**: 25
- **Class**: `DotEnvProvider`
- **Name**: `dotenv`
- **Write Support**: Yes
- **Required Package**: python-dotenv

Setup:
```bash
# Install python-dotenv support
pip install secret-key-manager[dotenv]
```

Create a `.env` file in your project directory:
```
# .env file
MY_API_KEY=your-api-key-value
DATABASE_URL=postgres://user:pass@localhost/dbname
```

By default, the provider looks for a `.env` file in the current directory, but you can specify a custom path:

```python
from secret_key_manager import keys

# Get a key with a specific .env file
keys.get_key("MY_API_KEY", providers=["dotenv"], file_path="/path/to/.env")

# Write a key to the .env file
keys.set_key("NEW_KEY", "new-value", persist=True, providers=["dotenv"])

# Write to a specific .env file
keys.set_key("NEW_KEY", "new-value", persist=True, providers=["dotenv"], 
            file_path="/path/to/.env")
```

Using the CLI:
```bash
# Get a key from the .env file
skm get MY_API_KEY --provider dotenv

# Set a key in the .env file
skm set NEW_KEY new-value --provider dotenv
```

### 1Password CLI Provider

Provider that integrates with the 1Password CLI (`op`) to retrieve secrets from 1Password.

- **Priority**: 30
- **Class**: `OnePasswordKeyProvider`
- **Name**: `1password`

Setup:
1. Install the 1Password CLI from: https://1password.com/downloads/command-line/
2. Create a configuration file at `~/.local/secret-key-manager/.config`:
   ```json
   {
     "account": "your-account.1password.com",
     "env_file": "~/.local/.env"
   }
   ```

The provider will:
1. Sign in to your 1Password account
2. Execute `op run --env-file=~/.local/.env --no-masking -- printenv MY_API_KEY`
3. Return the result if successful

### LastPass CLI Provider

Provider that integrates with a LastPass CLI (`olp`) to retrieve secrets.

- **Priority**: 40
- **Class**: `LastPassKeyProvider`
- **Name**: `lastpass`

Usage:
The provider assumes a command `olp` is available in your PATH and expects it to output the secret value when called with the key name:
```bash
olp MY_API_KEY
```

### JSON File Provider

Provider that retrieves and stores keys in a JSON file.

- **Priority**: 30
- **Class**: `JsonFileKeyProvider`
- **Name**: `json_file`
- **Write Support**: Yes

Setup:
Create a JSON file at `~/.config/secret_key_manager/keys.json`:
```json
{
  "MY_API_KEY": "your-api-key-value",
  "ANOTHER_KEY": "another-value"
}
```

Writing keys:
```python
# Using the KeyManager
from secret_key_manager import keys
keys.set_key("MY_API_KEY", "new-value", persist=True, providers=["json_file"])

# Using the CLI
skm set MY_API_KEY new-value --provider json_file
```

### YAML File Provider

Provider that retrieves and stores keys in a YAML file.

- **Priority**: 40
- **Class**: `YamlFileKeyProvider`
- **Name**: `yaml_file`
- **Write Support**: Yes

Setup:
Create a YAML file at `~/.config/secret_key_manager/keys.yaml`:
```yaml
MY_API_KEY: your-api-key-value
ANOTHER_KEY: another-value
```

Writing keys:
```python
# Using the KeyManager
from secret_key_manager import keys
keys.set_key("MY_API_KEY", "new-value", persist=True, providers=["yaml_file"])

# Using the CLI
skm set MY_API_KEY new-value --provider yaml_file
```

### Keyring Provider

Provider that uses the system keyring to store and retrieve keys securely.

- **Priority**: 50
- **Class**: `KeyringProvider`
- **Name**: `keyring`
- **Write Support**: Yes

Setup:
```python
import keyring
keyring.set_password("secret_key_manager", "MY_API_KEY", "your-api-key-value")
```

Writing keys:
```python
# Using the KeyManager
from secret_key_manager import keys
keys.set_key("MY_API_KEY", "new-value", persist=True, providers=["keyring"])

# Using the CLI
skm set MY_API_KEY new-value --provider keyring
```

## Creating Custom Providers

### Basic Provider Template

#### Read-Only Provider

```python
from typing import Optional
from secret_key_manager import KeyProvider

@KeyProvider(priority=30, name="my_provider")
class MyCustomProvider:
    def get_key(self, key_name: str, **kwargs) -> Optional[str]:
        # Your implementation here
        # Return the key value or None if not found
        return None
```

#### Provider with Write Support

```python
from typing import Optional, Dict, Any
from secret_key_manager import KeyProvider

@KeyProvider(priority=30, name="my_writable_provider")
class MyWritableProvider:
    def __init__(self):
        # Initialize your storage
        self._storage = {}
    
    def get_key(self, key_name: str, **kwargs) -> Optional[str]:
        # Read implementation
        return self._storage.get(key_name)
        
    def supports_write(self) -> bool:
        # Indicate this provider supports writing
        return True
        
    def write_key(self, key_name: str, key_value: str, **kwargs) -> bool:
        # Write implementation
        try:
            self._storage[key_name] = key_value
            return True
        except Exception:
            return False
            
    def validate_key(self, key_name: str, key_value: str, **kwargs) -> bool:
        # Optional: Validate key before writing
        return True  # Return False to reject invalid keys
        
    def get_provider_info(self) -> Dict[str, Any]:
        # Return additional provider metadata
        return {
            "name": self.name,
            "supports_write": self.supports_write(),
            "custom_info": "Additional provider metadata"
        }
```

### Provider Options

The `@KeyProvider` decorator accepts the following parameters:

- `enabled`: Whether the provider is enabled by default (default: True)
- `priority`: The priority of the provider (lower = higher priority) (default: 100)
- `name`: A custom name for the provider (default: class name with "KeyProvider" suffix removed)

### Example: Creating a Key Provider for AWS Secrets Manager

```python
import boto3
from typing import Optional
from secret_key_manager import KeyProvider

@KeyProvider(priority=50, name="aws_secrets")
class AWSSecretsManagerProvider:
    def __init__(self, region_name="us-east-1"):
        self.client = boto3.client('secretsmanager', region_name=region_name)
    
    def get_key(self, key_name: str, **kwargs) -> Optional[str]:
        try:
            response = self.client.get_secret_value(SecretId=key_name)
            return response['SecretString']
        except Exception as e:
            print(f"Error retrieving key from AWS Secrets Manager: {e}")
            return None
```

## Advanced Usage

### Managing Provider Status

```python
from secret_key_manager import keys

# Get status of all providers
provider_status = keys.get_provider_status()
for name, info in provider_status.items():
    enabled = "Enabled" if info["enabled"] else "Disabled"
    writable = "Yes" if info.get("supports_write", False) else "No"
    print(f"{name}: {enabled} (Priority: {info['priority']}, Writable: {writable})")

# Enable a provider
keys.enable_provider("json_file")

# Disable a provider
keys.disable_provider("vault")
```

### Working with Writable Providers

```python
from secret_key_manager import keys

# Get list of providers that support writing
writable_providers = keys.get_writable_providers()
print(f"Writable providers: {writable_providers}")

# Write a key to all writable providers
result = keys.set_key("MY_API_KEY", "secret-value", persist=True)
if result:
    print("Key was successfully written to at least one provider")
else:
    print("Failed to write key to any provider")

# Write a key to a specific provider
result = keys.set_key("MY_API_KEY", "secret-value", 
                      persist=True, providers=["json_file"])
if result:
    print("Key was successfully written to json_file provider")
else:
    print("Failed to write key to json_file provider")

# Get detailed provider information including capabilities
provider_info = keys.get_provider_status()
for name, info in provider_info.items():
    if name in writable_providers:
        capabilities = info.get("capabilities", {})
        print(f"Provider: {name}")
        print(f"  Capabilities: {capabilities}")
```

### Registering a Provider Manually

While the decorator is the preferred method, you can also register providers manually:

```python
from secret_key_manager import keys

class MyCustomProvider:
    @property
    def name(self):
        return "my_custom"
        
    def get_key(self, key_name, **kwargs):
        # Implementation
        return None

# Register the provider
keys.register_provider(MyCustomProvider())
```