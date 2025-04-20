#!/usr/bin/env python

"""
Example usage of the Secret Key Manager.

This script demonstrates different ways to use the Secret Key Manager.
"""

import os
import sys
import logging
import json
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the Secret Key Manager
from secret_key_manager import keys, KeyProvider
from secret_key_manager.providers import *


def setup_example_files():
    """Set up example configuration files for demonstration."""
    # Create config directory
    config_dir = Path.home() / ".local" / "secret_key_manager" / ".config"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Create example JSON file
    json_file = config_dir / "keys.json"
    json_data = {
        "EXAMPLE_JSON_KEY": "value-from-json-file",
        "COMMON_KEY": "json-value"
    }
    with open(json_file, 'w') as f:
        json.dump(json_data, f)
    logger.info(f"Created example JSON file: {json_file}")
    
    # Create example environment variable
    os.environ["EXAMPLE_ENV_KEY"] = "value-from-environment"
    os.environ["COMMON_KEY"] = "env-value"
    logger.info("Set example environment variables")


def demonstrate_basic_usage():
    """Demonstrate basic usage of the Secret Key Manager."""
    logger.info("\n=== Basic Usage ===")
    
    # Get a key - tries all providers in priority order
    value = keys.get_key("EXAMPLE_ENV_KEY")
    logger.info(f"EXAMPLE_ENV_KEY: {value}")
    
    value = keys.get_key("EXAMPLE_JSON_KEY")
    logger.info(f"EXAMPLE_JSON_KEY: {value}")
    
    # Use a specific provider
    value = keys.get_key("COMMON_KEY", providers=["environment"])
    logger.info(f"COMMON_KEY (from environment): {value}")
    
    value = keys.get_key("COMMON_KEY", providers=["json_file"])
    logger.info(f"COMMON_KEY (from json_file): {value}")
    
    # Set a key in memory
    keys.set_key("MEMORY_KEY", "value-in-memory")
    value = keys.get_key("MEMORY_KEY")
    logger.info(f"MEMORY_KEY: {value}")


def demonstrate_provider_management():
    """Demonstrate managing providers."""
    logger.info("\n=== Provider Management ===")
    
    # Get a list of active providers
    active_providers = keys.get_providers()
    logger.info(f"Active providers: {', '.join(active_providers)}")
    
    # Get detailed provider status
    status = keys.get_provider_status()
    for name, info in status.items():
        enabled = "Enabled" if info["enabled"] else "Disabled"
        logger.info(f"{name}: {enabled} (Priority: {info['priority']})")
    
    # Disable a provider
    if "json_file" in status:
        keys.disable_provider("json_file")
        logger.info("Disabled json_file provider")
        
        # Try to get a key that's only in the JSON file
        value = keys.get_key("EXAMPLE_JSON_KEY")
        logger.info(f"EXAMPLE_JSON_KEY after disabling json_file: {value}")
        
        # Re-enable the provider
        keys.enable_provider("json_file")
        logger.info("Re-enabled json_file provider")
        
        # Try to get the key again
        value = keys.get_key("EXAMPLE_JSON_KEY")
        logger.info(f"EXAMPLE_JSON_KEY after re-enabling json_file: {value}")


@KeyProvider(priority=5, name="example_inline")
class InlineProvider:
    """An example provider defined inline."""
    
    def get_key(self, key_name: str, **kwargs) -> str:
        if key_name == "INLINE_KEY":
            return "value-from-inline-provider"
        return None


def demonstrate_custom_provider():
    """Demonstrate creating and using a custom provider."""
    logger.info("\n=== Custom Provider ===")
    
    # The InlineProvider was registered by the decorator
    # Get a key from the inline provider
    value = keys.get_key("INLINE_KEY")
    logger.info(f"INLINE_KEY from inline provider: {value}")
    
    # Check if the provider is in the status list
    status = keys.get_provider_status()
    if "example_inline" in status:
        logger.info("Inline provider was successfully registered")


def main():
    """Run the example."""
    logger.info("Secret Key Manager Example")
    
    # Set up example files
    setup_example_files()
    
    # Run demonstrations
    demonstrate_basic_usage()
    demonstrate_provider_management()
    demonstrate_custom_provider()
    
    logger.info("\nExample completed successfully")


if __name__ == "__main__":
    main()