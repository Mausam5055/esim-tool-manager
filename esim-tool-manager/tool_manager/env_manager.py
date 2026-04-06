import os
import platform
import subprocess
from pathlib import Path
from .logger import get_logger

logger = get_logger(__name__)

def set_env_variable(key: str, value: str) -> bool:
    """
    Linux/Mac: appends `export KEY=VALUE` to ~/.bashrc AND ~/.zshrc (if exists).
    Windows: uses winreg to write to HKCU\Environment permanently.
    """
    system = platform.system()
    if system in ["Linux", "Darwin"]:
        rc_files = [Path.home() / ".bashrc", Path.home() / ".zshrc"]
        for rc_file in rc_files:
            if rc_file.exists():
                try:
                    content = rc_file.read_text()
                    if f"export {key}={value}" not in content:
                        with rc_file.open("a") as f:
                            f.write(f"\nexport {key}={value}\n")
                        logger.info(f"Updated {rc_file}: export {key}={value}")
                except Exception as e:
                    logger.error(f"Error updating {rc_file}: {e}")
                    return False
        return True
    elif system == "Windows":
        try:
            import winreg
            key_path = r"Environment"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, key, 0, winreg.REG_SZ, value)
            logger.info(f"Updated Registry (HKCU\\Environment): {key}={value}")
            return True
        except Exception as e:
            logger.error(f"Error updating Registry: {e}")
            return False
    return False

def add_to_path(directory: str) -> bool:
    """Appends directory to PATH. Checks for duplicates first."""
    system = platform.system()
    if system in ["Linux", "Darwin"]:
        rc_files = [Path.home() / ".bashrc", Path.home() / ".zshrc"]
        for rc_file in rc_files:
            if rc_file.exists():
                try:
                    content = rc_file.read_text()
                    if directory not in content:
                        with rc_file.open("a") as f:
                            f.write(f'\nexport PATH="$PATH:{directory}"\n')
                        logger.info(f"Added to PATH in {rc_file}: {directory}")
                except Exception as e:
                    logger.error(f"Error updating {rc_file}: {e}")
                    return False
        return True
    elif system == "Windows":
        try:
            import winreg
            key_path = r"Environment"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS) as reg_key:
                current_path, _ = winreg.QueryValueEx(reg_key, "Path")
                if directory not in current_path:
                    new_path = f"{current_path};{directory}"
                    winreg.SetValueEx(reg_key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            logger.info(f"Added to PATH (HKCU\\Environment): {directory}")
            return True
        except Exception as e:
            logger.error(f"Error updating PATH: {e}")
            return False
    return False

def apply_tool_env(tool_name: str, registry: dict) -> bool:
    """Reads env_vars from registry for the tool, calls set_env_variable() for each."""
    tool_entry = next((t for t in registry["tools"] if t["name"] == tool_name), None)
    if not tool_entry:
        logger.error(f"Tool {tool_name} not found in registry")
        return False
        
    env_vars = tool_entry.get("env_vars", {})
    success = True
    for key, value in env_vars.items():
        if not set_env_variable(key, value):
            success = False
    return success

def verify_env(tool_name: str, registry: dict) -> dict[str, bool]:
    """Checks that all required env_vars for a tool are set via os.environ.get()."""
    tool_entry = next((t for t in registry["tools"] if t["name"] == tool_name), None)
    if not tool_entry:
        return {}
        
    env_vars = tool_entry.get("env_vars", {})
    results = {}
    for key, value in env_vars.items():
        results[key] = os.environ.get(key) == value
    return results

def remove_tool_env(tool_name: str, registry: dict) -> bool:
    """Removes the tool's env_var lines from shell rc files (Linux/Mac)."""
    system = platform.system()
    tool_entry = next((t for t in registry["tools"] if t["name"] == tool_name), None)
    if not tool_entry:
        return False
        
    env_vars = tool_entry.get("env_vars", {})
    if system in ["Linux", "Darwin"]:
        rc_files = [Path.home() / ".bashrc", Path.home() / ".zshrc"]
        for rc_file in rc_files:
            if rc_file.exists():
                try:
                    lines = rc_file.read_text().splitlines()
                    new_lines = []
                    for line in lines:
                        should_keep = True
                        for key in env_vars:
                            if line.strip().startswith(f"export {key}="):
                                should_keep = False
                                break
                        if should_keep:
                            new_lines.append(line)
                    rc_file.write_text("\n".join(new_lines) + "\n")
                    logger.info(f"Removed env vars for {tool_name} from {rc_file}")
                except Exception as e:
                    logger.error(f"Error removing env vars from {rc_file}: {e}")
                    return False
        return True
    elif system == "Windows":
        try:
            import winreg
            key_path = r"Environment"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS) as reg_key:
                for key in env_vars:
                    try:
                        winreg.DeleteValue(reg_key, key)
                    except FileNotFoundError:
                        pass
            logger.info(f"Removed env vars for {tool_name} from HKCU\\Environment")
            return True
        except Exception as e:
            logger.error(f"Error removing env vars from registry: {e}")
            return False
    return False
