import pytest
import subprocess
from unittest.mock import MagicMock, patch
from tool_manager.installer import install_tool, verify_installation, get_installed_version, _resolve_version

def test_resolve_version(sample_tool_registry):
    tool = sample_tool_registry["tools"][0]
    assert _resolve_version(tool, None) == "41"
    assert _resolve_version(tool, "40") == "40"

@patch("tool_manager.installer.subprocess.run")
def test_verify_installation(mock_run, sample_tool_registry):
    # Success case
    mock_run.return_value = MagicMock(returncode=0)
    assert verify_installation("ngspice", sample_tool_registry) is True
    
    # Failure case
    mock_run.return_value = MagicMock(returncode=1)
    assert verify_installation("ngspice", sample_tool_registry) is False

@patch("tool_manager.installer.subprocess.run")
def test_get_installed_version(mock_run, sample_tool_registry):
    # Successful match
    mock_run.return_value = MagicMock(returncode=0, stdout="ngspice-41", stderr="")
    assert get_installed_version("ngspice", sample_tool_registry) == "41"
    
    # Another format
    mock_run.return_value = MagicMock(returncode=0, stdout="Version: 1.2.3-alpha", stderr="")
    assert get_installed_version("ngspice", sample_tool_registry) == "1.2.3"
    
    # No version found
    mock_run.return_value = MagicMock(returncode=0, stdout="No version info", stderr="")
    assert get_installed_version("ngspice", sample_tool_registry) is None

@patch("tool_manager.installer.check_dependencies")
@patch("tool_manager.installer.detect_package_manager")
@patch("tool_manager.installer.run_package_manager_install")
@patch("tool_manager.installer.verify_installation")
@patch("tool_manager.installer.apply_tool_env")
@patch("tool_manager.config.get")
@patch("tool_manager.config.set")
def test_install_tool_success(mock_config_set, mock_config_get, mock_apply_env, mock_verify, mock_pm_install, mock_detect_pm, mock_check_deps, sample_tool_registry):
    # Mock successful setup
    mock_check_deps.return_value = {"libxaw7-dev": {"status": "ok"}}
    mock_detect_pm.return_value = "apt"
    mock_pm_install.return_value = MagicMock(returncode=0)
    mock_verify.return_value = True
    mock_config_get.return_value = {}
    
    with patch("platform.system", return_value="Linux"):
        assert install_tool("ngspice", sample_tool_registry) is True
        mock_pm_install.assert_called_once()
        mock_config_set.assert_called_once()
