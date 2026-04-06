import os
import platform
import subprocess
import tempfile
import shutil
import requests
import zipfile
import tarfile
import re
from pathlib import Path
from .logger import get_logger
from .package_bridge import detect_package_manager, run_package_manager_install, get_installed_package_version
from .dependency_checker import check_dependencies
from .env_manager import apply_tool_env
from . import config

logger = get_logger(__name__)

def install_tool(tool_name: str, registry: dict, version: str = None, force: bool = False) -> bool:
    """Core installation engine."""
    tool_entry = next((t for t in registry["tools"] if t["name"] == tool_name), None)
    if not tool_entry:
        logger.error(f"Tool {tool_name} not found in registry")
        return False
        
    system = platform.system().lower()
    platform_config = tool_entry["platforms"].get(system)
    if not platform_config:
        logger.error(f"Platform {system} not supported for {tool_name}")
        return False
        
    # Check dependencies
    deps = check_dependencies(tool_name, registry)
    missing_deps = [d for d, s in deps.items() if s["status"] != "ok"]
    if missing_deps:
        logger.warning(f"Missing or incompatible dependencies for {tool_name}: {', '.join(missing_deps)}")
        # In a real scenario, we might want to try installing them automatically.
        # For now, we'll log it and proceed if requested, or abort.
        if not force:
            logger.error("Installation aborted due to missing dependencies. Use --force to proceed anyway.")
            return False
            
    # Resolve version
    resolved_version = _resolve_version(tool_entry, version)
    
    # Check if already installed
    current_version = get_installed_version(tool_name, registry)
    if current_version and not force:
        if current_version == resolved_version:
            logger.info(f"{tool_name} version {current_version} is already installed.")
            return True
        else:
            logger.info(f"{tool_name} version {current_version} is installed. Use --force to reinstall or update.")
            
    # Select install method
    pm = detect_package_manager()
    success = False
    
    if pm and platform_config.get("package_manager") == pm:
        package_name = platform_config.get("package_name")
        if package_name:
            result = run_package_manager_install(pm, package_name)
            success = result.returncode == 0
            
    if not success:
        fallback_url = platform_config.get("fallback_url")
        if fallback_url:
            logger.info(f"Attempting installation from fallback URL: {fallback_url}")
            success = _install_via_url(tool_name, fallback_url, system)
        else:
            logger.error(f"No installation method available for {tool_name} on {system}")
            return False
            
    if success:
        if verify_installation(tool_name, registry):
            apply_tool_env(tool_name, registry)
            # Record in config
            installed_tools = config.get("installed_tools", {})
            installed_tools[tool_name] = {
                "version": resolved_version,
                "installed_at": Path().cwd().name, # Placeholder or timestamp
                "install_method": pm if pm else "url",
                "platform": system
            }
            config.set("installed_tools", installed_tools)
            logger.info(f"Successfully installed and configured {tool_name}")
            return True
        else:
            logger.error(f"Installation of {tool_name} completed but verification failed.")
            return False
            
    return False

def _resolve_version(tool: dict, requested_version: str | None) -> str:
    """If requested_version is None → return registry version."""
    if requested_version is None:
        return tool["version"]
    if requested_version != tool["version"]:
        logger.warning(f"Requested version {requested_version} differs from registry default {tool['version']}")
    return requested_version

def _install_via_url(tool_name: str, url: str, system: str) -> bool:
    """Downloads and extracts tool from URL."""
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            file_name = url.split("/")[-1]
            download_path = tmp_path / file_name
            
            logger.info(f"Downloading {url}...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(download_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            logger.info(f"Extracting {file_name}...")
            if file_name.endswith(".zip"):
                with zipfile.ZipFile(download_path, 'r') as zip_ref:
                    zip_ref.extractall(tmp_path)
            elif file_name.endswith(".tar.gz") or file_name.endswith(".tgz"):
                with tarfile.open(download_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(tmp_path)
            elif file_name.endswith(".exe") and system == "windows":
                logger.info(f"Running silent installer: {file_name}")
                result = subprocess.run([str(download_path), "/S"], capture_output=True, text=True)
                return result.returncode == 0
            else:
                logger.error(f"Unsupported file format: {file_name}")
                return False
                
            # For extraction-based installs, we'd normally move the files to a permanent location.
            # For this prototype, we'll log the success.
            logger.info(f"Extraction successful for {tool_name}")
            return True
    except Exception as e:
        logger.error(f"Failed to install {tool_name} from URL: {e}")
        return False

def verify_installation(tool_name: str, registry: dict) -> bool:
    """Runs tool's verify_command."""
    tool_entry = next((t for t in registry["tools"] if t["name"] == tool_name), None)
    if not tool_entry:
        return False
        
    verify_cmd = tool_entry.get("verify_command")
    if not verify_cmd:
        return True # Assume OK if no verify command
        
    try:
        # Use shell=True for verify commands which might include flags
        result = subprocess.run(verify_cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Verification failed for {tool_name}: {e}")
        return False

def get_installed_version(tool_name: str, registry: dict) -> str | None:
    """Parses stdout for version string using regex."""
    tool_entry = next((t for t in registry["tools"] if t["name"] == tool_name), None)
    if not tool_entry:
        return None
        
    verify_cmd = tool_entry.get("verify_command")
    if not verify_cmd:
        return None
        
    try:
        result = subprocess.run(verify_cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            output = result.stdout + result.stderr
            # Regex patterns for version strings
            patterns = [
                r"(\d+\.\d+\.\d+)", # semver
                r"(\d+\.\d+)",       # X.Y
                r"(\d+)"            # integer
            ]
            for pattern in patterns:
                match = re.search(pattern, output)
                if match:
                    return match.group(1)
    except Exception as e:
        logger.debug(f"Could not determine version for {tool_name}: {e}")
        
    return None

def uninstall_tool(tool_name: str, registry: dict) -> bool:
    """Removes tool and cleans up."""
    pm = detect_package_manager()
    tool_entry = next((t for t in registry["tools"] if t["name"] == tool_name), None)
    if not tool_entry:
        return False
        
    system = platform.system().lower()
    platform_config = tool_entry["platforms"].get(system)
    
    success = False
    if pm and platform_config.get("package_manager") == pm:
        package_name = platform_config.get("package_name")
        if package_name:
            command = []
            if pm == "apt":
                command = ["sudo", "apt", "remove", "-y", package_name]
            elif pm == "homebrew":
                command = ["brew", "uninstall", package_name]
            elif pm == "chocolatey":
                command = ["choco", "uninstall", package_name, "-y"]
            
            if command:
                result = subprocess.run(command, capture_output=True, text=True)
                success = result.returncode == 0
                
    # Clean up environment
    from .env_manager import remove_tool_env
    remove_tool_env(tool_name, registry)
    
    # Update config
    installed_tools = config.get("installed_tools", {})
    if tool_name in installed_tools:
        del installed_tools[tool_name]
        config.set("installed_tools", installed_tools)
        
    if success:
        logger.info(f"Successfully uninstalled {tool_name}")
    else:
        logger.warning(f"Uninstall command for {tool_name} failed or was not available.")
        
    return success
