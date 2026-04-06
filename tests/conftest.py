import pytest
import json
from pathlib import Path

@pytest.fixture
def sample_tool_registry():
    return {
        "tools": [{
            "name": "ngspice",
            "display_name": "Ngspice",
            "version": "41",
            "platforms": {
                "linux": {"package_manager": "apt", "package_name": "ngspice", "fallback_url": None},
                "windows": {"package_manager": "chocolatey", "package_name": "ngspice", "fallback_url": None}
            },
            "dependencies": ["libxaw7-dev"],
            "min_dep_versions": {"libxaw7-dev": "2:1.0.13"},
            "verify_command": "ngspice --version",
            "config_paths": {"linux": "~/.ngspice/", "windows": "%APPDATA%\\ngspice\\"},
            "env_vars": {"NGSPICE_HOME": "/usr/share/ngspice"}
        }]
    }

@pytest.fixture
def temp_config(tmp_path):
    config_file = tmp_path / "config.json"
    config_data = {
        "esim_home": "~/eSim",
        "auto_update_check": True,
        "preferred_install_method": "package_manager",
        "log_level": "INFO",
        "installed_tools": {
            "ngspice": {"version": "40", "install_method": "apt", "platform": "linux"}
        }
    }
    config_file.write_text(json.dumps(config_data))
    return config_file
