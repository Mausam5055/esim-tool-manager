import json
import os
from pathlib import Path
from .logger import get_logger

logger = get_logger(__name__)

CONFIG_DIR = Path.home() / ".esim_tool_manager"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "esim_home": str(Path.home() / "eSim"),
    "auto_update_check": True,
    "preferred_install_method": "package_manager",
    "log_level": "INFO",
    "installed_tools": {}
}

def load_config() -> dict:
    """Reads config; creates default if absent."""
    if not CONFIG_FILE.exists():
        logger.info(f"Config file not found. Creating default config at {CONFIG_FILE}")
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return DEFAULT_CONFIG

def save_config(data: dict) -> None:
    """Writes config to disk atomically."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        # Atomic write (write to temp file then rename)
        temp_file = CONFIG_FILE.with_suffix(".tmp")
        with open(temp_file, 'w') as f:
            json.dump(data, f, indent=2)
        os.replace(temp_file, CONFIG_FILE)
    except Exception as e:
        logger.error(f"Failed to save config: {e}")

def get(key: str, default=None):
    """Safe key access."""
    config = load_config()
    return config.get(key, default)

def set(key: str, value) -> None:
    """Updates a key and persists immediately."""
    config = load_config()
    
    # Handle nested keys if necessary (simple implementation for now)
    if "." in key:
        parts = key.split(".")
        current = config
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    else:
        config[key] = value
        
    save_config(config)
    logger.debug(f"Config updated: {key} = {value}")
