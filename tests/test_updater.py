import pytest
from unittest.mock import MagicMock, patch
from tool_manager.updater import check_tool_update

@patch("tool_manager.updater.get_installed_version")
def test_check_tool_update(mock_get_ver, sample_tool_registry):
    # Update available (installed < latest)
    mock_get_ver.return_value = "40"
    result = check_tool_update("ngspice", sample_tool_registry)
    assert result["update_available"] is True
    assert result["installed"] == "40"
    assert result["latest"] == "41"
    
    # Already latest (installed == latest)
    mock_get_ver.return_value = "41"
    result = check_tool_update("ngspice", sample_tool_registry)
    assert result["update_available"] is False
    
    # Not installed
    mock_get_ver.return_value = None
    result = check_tool_update("ngspice", sample_tool_registry)
    assert result["update_available"] is False
    assert result["installed"] is None
    
    # Different version formats
    mock_get_ver.return_value = "1.2.3"
    # Registry says "41", so 1.2.3 < 41
    result = check_tool_update("ngspice", sample_tool_registry)
    assert result["update_available"] is True
