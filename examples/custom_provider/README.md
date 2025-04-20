# Custom Provider Example

This example demonstrates how to create a custom key provider as a separate package.

## Package Structure

```
custom_provider/
  __init__.py
  provider.py
  setup.py
```

## Installation

```bash
pip install -e .
```

## Usage

Once installed, the provider will be automatically registered with the Secret Key Manager.

```python
from secret_key_manager import keys

# List all providers
print(keys.get_providers())  # Should include 'custom_example'

# Get a key using the custom provider
key = keys.get_key("MY_API_KEY", providers=["custom_example"])
```