from packaging.version import parse
from .logger import get_logger
from .installer import get_installed_version, install_tool
from . import config

logger = get_logger(__name__)

def check_all_updates(registry: dict) -> dict[str, dict]:
    """For each tool in config["installed_tools"], call check_tool_update()."""
    installed_tools = config.get("installed_tools", {})
    results = {}
    for tool_name in installed_tools:
        results[tool_name] = check_tool_update(tool_name, registry)
    return results

def check_tool_update(tool_name: str, registry: dict) -> dict:
    """Gets installed version via get_installed_version() and compares against registry."""
    tool_entry = next((t for t in registry["tools"] if t["name"] == tool_name), None)
    if not tool_entry:
        return {}
        
    latest_version = tool_entry["version"]
    installed_version = get_installed_version(tool_name, registry)
    
    if not installed_version:
        return {"installed": None, "latest": latest_version, "update_available": False}
        
    try:
        update_available = parse(latest_version) > parse(installed_version)
    except Exception as e:
        logger.error(f"Error comparing versions for {tool_name}: {e}")
        update_available = False
        
    return {
        "installed": installed_version,
        "latest": latest_version,
        "update_available": update_available
    }

def update_tool(tool_name: str, registry: dict, progress_callback=None, cancel_event=None) -> bool:
    """1. Calls check_tool_update() — aborts with message if no update available."""
    update_info = check_tool_update(tool_name, registry)
    if not update_info or not update_info.get("update_available"):
        logger.info(f"No update available for {tool_name}")
        return False
        
    logger.info(f"Updating {tool_name} from {update_info['installed']} to {update_info['latest']}...")
    # 2. Calls install_tool(tool_name, force=True).
    success = install_tool(tool_name, registry, force=True, progress_callback=progress_callback, cancel_event=cancel_event)
    return success

def update_all_tools(registry: dict, progress_callback=None, cancel_event=None) -> dict[str, bool]:
    """Calls update_tool() for each tool where update_available == True."""
    updates = check_all_updates(registry)
    results = {}
    for tool_name, info in updates.items():
        if info.get("update_available"):
            results[tool_name] = update_tool(tool_name, registry, progress_callback=progress_callback, cancel_event=cancel_event)
    return results
