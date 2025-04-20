"""File-based key providers."""

import os
import json
import yaml
import logging
import pathlib
from typing import Optional, Dict, Any

from secret_key_manager.core import KeyProvider

# Configure logging
logger = logging.getLogger(__name__)


@KeyProvider(priority=30, name="json_file")
class JsonFileKeyProvider:
    """Key provider that retrieves keys from a JSON file."""
    
    def __init__(self, file_path: str = "~/.config/secret_key_manager/keys.json"):
        self.file_path = os.path.expanduser(file_path)
        self._keys: Dict[str, str] = {}
        self._load_keys()
    
    def _load_keys(self) -> None:
        """Load keys from the file."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    self._keys = json.load(f)
                logger.debug(f"Loaded keys from JSON file: {self.file_path}")
            except Exception as e:
                logger.error(f"Error loading keys from JSON file: {e}")
        else:
            logger.debug(f"JSON keys file not found: {self.file_path}")
    
    def _save_keys(self) -> bool:
        """Save keys to the file."""
        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(self.file_path)
            if directory and not os.path.exists(directory):
                pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
                
            with open(self.file_path, 'w') as f:
                json.dump(self._keys, f, indent=2)
            logger.debug(f"Saved keys to JSON file: {self.file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving keys to JSON file: {e}")
            return False
    
    def get_key(self, key_name: str, **kwargs) -> Optional[str]:
        """Get a key from the loaded JSON file data."""
        return self._keys.get(key_name)
    
    def supports_write(self) -> bool:
        """Check if this provider supports writing keys."""
        return True
    
    def write_key(self, key_name: str, key_value: str, **kwargs) -> bool:
        """Write a key to the JSON file."""
        self._keys[key_name] = key_value
        return self._save_keys()
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about this provider."""
        return {
            "name": self.name,
            "supports_write": self.supports_write(),
            "file_path": self.file_path
        }


@KeyProvider(priority=40, name="yaml_file")
class YamlFileKeyProvider:
    """Key provider that retrieves keys from a YAML file."""
    
    def __init__(self, file_path: str = "~/.config/secret_key_manager/keys.yaml"):
        self.file_path = os.path.expanduser(file_path)
        self._keys: Dict[str, str] = {}
        self._load_keys()
    
    def _load_keys(self) -> None:
        """Load keys from the file."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    self._keys = yaml.safe_load(f)
                logger.debug(f"Loaded keys from YAML file: {self.file_path}")
            except Exception as e:
                logger.error(f"Error loading keys from YAML file: {e}")
        else:
            logger.debug(f"YAML keys file not found: {self.file_path}")
    
    def _save_keys(self) -> bool:
        """Save keys to the file."""
        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(self.file_path)
            if directory and not os.path.exists(directory):
                pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
                
            with open(self.file_path, 'w') as f:
                yaml.dump(self._keys, f, default_flow_style=False)
            logger.debug(f"Saved keys to YAML file: {self.file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving keys to YAML file: {e}")
            return False
    
    def get_key(self, key_name: str, **kwargs) -> Optional[str]:
        """Get a key from the loaded YAML file data."""
        return self._keys.get(key_name)
    
    def supports_write(self) -> bool:
        """Check if this provider supports writing keys."""
        return True
    
    def write_key(self, key_name: str, key_value: str, **kwargs) -> bool:
        """Write a key to the YAML file."""
        self._keys[key_name] = key_value
        return self._save_keys()
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about this provider."""
        return {
            "name": self.name,
            "supports_write": self.supports_write(),
            "file_path": self.file_path
        }