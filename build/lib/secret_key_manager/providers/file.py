"""File-based key providers."""

import os
import json
import yaml
import logging
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
    
    def get_key(self, key_name: str, **kwargs) -> Optional[str]:
        """Get a key from the loaded JSON file data."""
        return self._keys.get(key_name)


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
    
    def get_key(self, key_name: str, **kwargs) -> Optional[str]:
        """Get a key from the loaded YAML file data."""
        return self._keys.get(key_name)