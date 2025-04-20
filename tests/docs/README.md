# Secret Key Manager Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Basic Usage](#basic-usage)
4. [Command-Line Interface](#command-line-interface)
5. [Creating Custom Providers](#creating-custom-providers)
6. [Advanced Usage](#advanced-usage)

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

### Managing Providers

```bash
# List active providers
skm providers list

# Show provider status
skm providers status

# Enable a provider
skm providers enable json_file

# Disable a provider
skm providers disable vault
```

## Creating Custom Providers

### Basic Provider Template

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
    print(f"{name}: {enabled} (Priority: {info['priority']})")

# Enable a provider
keys.enable_provider("json_file")

# Disable a provider
keys.disable_provider("vault")
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