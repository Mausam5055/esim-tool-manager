import pytest
from unittest.mock import MagicMock, patch
from tool_manager.dependency_checker import check_dependencies, _is_version_compatible

def test_is_version_compatible():
    assert _is_version_compatible("2:1.0.14", "2:1.0.13") is True
    assert _is_version_compatible("1.0.14", "1.0.13") is True
    assert _is_version_compatible("1.0.12", "1.0.13") is False
    assert _is_version_compatible("8.0", "7.9") is True
    assert _is_version_compatible("7.9", "8.0") is False

@patch("tool_manager.dependency_checker._get_dep_installed_version")
@patch("tool_manager.dependency_checker.detect_package_manager")
def test_check_dependencies(mock_detect_pm, mock_get_ver, sample_tool_registry):
    mock_detect_pm.return_value = "apt"
    
    # All OK
    mock_get_ver.return_value = "2:1.0.14"
    result = check_dependencies("ngspice", sample_tool_registry)
    assert result["libxaw7-dev"]["status"] == "ok"
    assert result["libxaw7-dev"]["compatible"] is True
    
    # Missing
    mock_get_ver.return_value = None
    result = check_dependencies("ngspice", sample_tool_registry)
    assert result["libxaw7-dev"]["status"] == "missing"
    assert result["libxaw7-dev"]["compatible"] is False
    
    # Incompatible
    mock_get_ver.return_value = "2:1.0.12"
    result = check_dependencies("ngspice", sample_tool_registry)
    assert result["libxaw7-dev"]["status"] == "incompatible"
    assert result["libxaw7-dev"]["compatible"] is False
