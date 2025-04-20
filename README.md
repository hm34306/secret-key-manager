# Secret Key Manager

A flexible key management system with plugin support.

## Why?

I was storing keys in .bashrc and it dawned on me that I would rather make use of better, more sec ure storage such as the 1password cli or the lastpass cli. Other file formats came up and I felt it was all pretty similar. If I want ot find a kye, I really just want a quick entry point to get it. 

## Features

- Plugin-based architecture for key providers
- Decorator-based registration for easy extension
- Built-in providers for environment variables and command-line tools
- Priority-based key retrieval
- Enable/disable providers at runtime
- Command-line interface for management

## Installation

```bash
pip install -e .
```

## Usage in Kickapoo Summarize Tool

This package is now used manage API keys and Secrets. It provides a more flexible and extensible way to handle API keys from various sources.

## Available Key Providers

By default, the following key providers are available:

1. **Environment Variables** (priority: 10): Gets keys from environment variables
2. **Vault Command** (priority: 20): Gets keys from the `vault` command-line tool
3. **JSON File** (priority: 30): Gets keys from a JSON file located at `~/.config/secret_key_manager/keys.json`
4. **YAML File** (priority: 40): Gets keys from a YAML file located at `~/.config/secret_key_manager/keys.yaml`
5. **Keyring** (priority: 50): Gets keys from the system keyring (if available)

The providers are tried in order of priority (lower number = higher priority).

## Setting Up Keys

### Using Environment Variables

```bash
export SOME_KEY=your-api-key
```

### Using Vault Command

Make sure the `vault` command is available in your PATH and returns API keys when called with the key name:

```bash
vault SOME_KEY
```

### Using JSON File

Create a JSON file at `~/.config/secret_key_manager/keys.json`:

```json
{
  "SOME_KEY": "your-api-key"
}
```

### Using YAML File

Create a YAML file at `~/.config/secret_key_manager/keys.yaml`:

```yaml
SOME_KEY: your-api-key
```

### Using Keyring

If you have the `keyring` package installed, you can store your keys in the system keyring:

```python
import keyring
keyring.set_password("secret_key_manager", "SOME_KEY", "your-api-key")
```

## Command Line Interface

The package includes a command-line interface (CLI):

```bash
# Get a key (tries all enabled providers)
skm get SOME_KEY

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

You can create custom key providers using the decorator pattern:

```python
from secret_key_manager import KeyProvider

@KeyProvider(priority=60, name="my_custom")
class MyCustomProvider:
    def get_key(self, key_name, **kwargs):
        # Your implementation here
        return "your-api-key" if key_name == "SOME_KEY" else None
```

See the [full documentation](docs/README.md) for more details.

## License

MIT