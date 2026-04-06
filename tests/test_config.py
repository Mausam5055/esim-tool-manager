import pytest
import json
import os
from unittest.mock import MagicMock, patch
from tool_manager.config import load_config, save_config, get, set

@patch("tool_manager.config.CONFIG_FILE")
def test_load_config_default(mock_config_file, tmp_path):
    mock_config_file.exists.return_value = False
    config_data = load_config()
    assert config_data["esim_home"].endswith("eSim")

def test_save_and_load_config(tmp_path):
    config_file = tmp_path / "config.json"
    data = {"test_key": "test_value"}
    
    with patch("tool_manager.config.CONFIG_FILE", config_file), \
         patch("tool_manager.config.CONFIG_DIR", tmp_path):
        save_config(data)
        assert config_file.exists()
        loaded_data = load_config()
        assert loaded_data["test_key"] == "test_value"

def test_get_and_set(tmp_path):
    config_file = tmp_path / "config.json"
    with patch("tool_manager.config.CONFIG_FILE", config_file), \
         patch("tool_manager.config.CONFIG_DIR", tmp_path):
        # Set top-level key
        set("test_key", "test_value")
        assert get("test_key") == "test_value"
        
        # Set nested key
        set("installed_tools.ngspice.version", "41")
        assert get("installed_tools")["ngspice"]["version"] == "41"
