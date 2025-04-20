"""Tests for built-in key providers."""

import os
import tempfile
import json
import pytest
from unittest.mock import patch, MagicMock, mock_open

# Conditionally import yaml for testing
try:
    import yaml  # noqa: F401 - needed for pytest.mark.skipif condition

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from secret_key_manager.providers.env import EnvKeyProvider
from secret_key_manager.providers.file import JsonFileKeyProvider, YamlFileKeyProvider
from secret_key_manager.providers.onepassword import OnePasswordKeyProvider
from secret_key_manager.providers.lastpass import LastPassKeyProvider

# Conditionally import DotEnvProvider for testing
try:
    from secret_key_manager.providers.dotenv import DotEnvProvider

    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False


# Test environment variable provider
def test_env_provider():
    provider = EnvKeyProvider()

    # Test key that doesn't exist
    assert provider.get_key("NONEXISTENT_KEY") is None

    # Test key that exists
    with patch.dict(os.environ, {"TEST_KEY": "test-value"}):
        assert provider.get_key("TEST_KEY") == "test-value"

    # Verify provider name
    assert provider.name == "environment"


# Test JSON file provider
def test_json_file_provider():
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(suffix=".json", mode="w+") as temp_file:
        # Write test data to the file
        test_data = {"TEST_KEY": "json-secret-value", "ANOTHER_KEY": "another-value"}
        json.dump(test_data, temp_file)
        temp_file.flush()

        # Create provider instance with the temporary file
        provider = JsonFileKeyProvider(file_path=temp_file.name)

        # Test key retrieval
        assert provider.get_key("TEST_KEY") == "json-secret-value"
        assert provider.get_key("ANOTHER_KEY") == "another-value"
        assert provider.get_key("NONEXISTENT_KEY") is None

        # Test writing a key
        assert provider.supports_write() is True
        result = provider.write_key("NEW_KEY", "new-value")
        assert result is True

        # Verify provider name
        assert provider.name == "json_file"


# Test YAML file provider
@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not installed")
def test_yaml_file_provider():
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as temp_file:
        # Write test data to the file
        test_data = """
TEST_KEY: yaml-secret-value
ANOTHER_KEY: another-value
"""
        temp_file.write(test_data)
        temp_file.flush()

        # Create provider instance with the temporary file
        provider = YamlFileKeyProvider(file_path=temp_file.name)

        # Test key retrieval
        assert provider.get_key("TEST_KEY") == "yaml-secret-value"
        assert provider.get_key("ANOTHER_KEY") == "another-value"
        assert provider.get_key("NONEXISTENT_KEY") is None

        # Test writing a key
        assert provider.supports_write() is True
        result = provider.write_key("NEW_KEY", "new-value")
        assert result is True

        # Verify provider name
        assert provider.name == "yaml_file"


# Test 1Password provider
@patch("subprocess.run")
@patch("os.path.expanduser")
@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"account": "test.1password.com", "env_file": "~/.local/.env"}',
)
def test_onepassword_provider(mock_file, mock_expanduser, mock_subprocess):
    # Mock expanduser to return a simple path
    mock_expanduser.return_value = "/tmp/.config"

    # Mock subprocess.run for version check
    version_process = MagicMock()
    version_process.returncode = 0

    # Mock subprocess.run for signin
    signin_process = MagicMock()
    signin_process.returncode = 0

    # Mock subprocess.run for key retrieval
    key_process = MagicMock()
    key_process.returncode = 0
    key_process.stdout = "secret-value"

    mock_subprocess.side_effect = [version_process, signin_process, key_process]

    # Create provider instance
    provider = OnePasswordKeyProvider()

    # Test key retrieval
    result = provider.get_key("TEST_KEY")
    assert result == "secret-value"

    # Verify provider name
    assert provider.name == "1password"

    # Verify subprocess calls
    assert mock_subprocess.call_count == 3

    # Check the calls were made correctly
    calls = mock_subprocess.call_args_list
    assert "op" in calls[0][0][0]
    assert "signin" in calls[1][0][0]
    assert "run" in calls[2][0][0]
    assert "TEST_KEY" in calls[2][0][0]


# Test LastPass provider
@patch("subprocess.run")
def test_lastpass_provider(mock_subprocess):
    # Mock subprocess.run for help check
    help_process = MagicMock()
    help_process.returncode = 0

    # Mock subprocess.run for key retrieval
    key_process = MagicMock()
    key_process.returncode = 0
    key_process.stdout = "lastpass-secret-value"

    mock_subprocess.side_effect = [help_process, key_process]

    # Create provider instance
    provider = LastPassKeyProvider()

    # Test key retrieval
    result = provider.get_key("LASTPASS_KEY")
    assert result == "lastpass-secret-value"

    # Verify provider name
    assert provider.name == "lastpass"

    # Verify subprocess calls
    assert mock_subprocess.call_count == 2

    # Check the calls were made correctly
    calls = mock_subprocess.call_args_list
    assert "olp" in calls[0][0][0]
    assert "LASTPASS_KEY" in calls[1][0][0]


# Test DotEnv provider if python-dotenv is installed
@pytest.mark.skipif(not HAS_DOTENV, reason="python-dotenv not installed")
def test_dotenv_provider():
    """Test the DotEnv provider if dotenv is available."""
    with tempfile.NamedTemporaryFile(suffix=".env", mode="w+") as temp_env:
        # Create a test .env file
        temp_env.write("DOTENV_TEST_KEY=dotenv-secret-value\n")
        temp_env.flush()

        # Create patches for dotenv functions
        with (
            patch("dotenv.load_dotenv", return_value=True),
            patch(
                "dotenv.dotenv_values",
                return_value={"DOTENV_TEST_KEY": "dotenv-secret-value"},
            ),
            patch("dotenv.set_key", return_value=None),
            patch.dict("os.environ", {"DOTENV_TEST_KEY": "dotenv-secret-value"}),
        ):
            # Create provider instance
            provider = DotEnvProvider(file_path=temp_env.name)

            # Test key retrieval
            result = provider.get_key("DOTENV_TEST_KEY")
            assert result == "dotenv-secret-value"

            # Test write support
            assert provider.supports_write() is True

            # Test writing a key
            write_result = provider.write_key("NEW_KEY", "new-value")
            assert write_result is True

            # Verify provider name
            assert provider.name == "dotenv"

            # Test provider info
            info = provider.get_provider_info()
            assert info["name"] == "dotenv"
            assert info["supports_write"] is True
            assert temp_env.name in info["file_path"]
