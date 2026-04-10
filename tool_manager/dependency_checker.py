import subprocess
import platform
import json
from packaging.version import parse
from .logger import get_logger
from .package_bridge import get_installed_package_version, detect_package_manager

logger = get_logger(__name__)

def check_dependencies(tool_name: str, registry: dict) -> dict[str, dict]:
    """
    Returns per-dependency status dict:
    {
      "libxaw7-dev": {
        "installed": True,
        "installed_version": "2:1.0.14",
        "required_min_version": "2:1.0.13",
        "compatible": True,
        "status": "ok"           # "ok" | "missing" | "incompatible"
      }
    }
    """
    tool_entry = next((t for t in registry["tools"] if t["name"] == tool_name), None)
    if not tool_entry:
        logger.error(f"Tool {tool_name} not found in registry")
        return {}
    
    dependencies = tool_entry.get("dependencies", [])
    min_dep_versions = tool_entry.get("min_dep_versions", {})
    pm = detect_package_manager()
    
    results = {}
    for dep in dependencies:
        installed_version = _get_dep_installed_version(dep, platform.system(), pm)
        required_min_version = min_dep_versions.get(dep)
        
        installed = installed_version is not None
        compatible = True
        status = "ok"
        
        if not installed:
            status = "missing"
            compatible = False
        elif required_min_version and not _is_version_compatible(installed_version, required_min_version):
            status = "incompatible"
            compatible = False
            
        results[dep] = {
            "installed": installed,
            "installed_version": installed_version,
            "required_min_version": required_min_version,
            "compatible": compatible,
            "status": status
        }
        
    return results

def _check_windows_tool_version(tool_name: str) -> str | None:
    """Check if a dev tool is available on Windows by running its version command."""
    import re
    
    version_commands = {
        "cmake": ["cmake", "--version"],
        "gcc": ["gcc", "--version"],
        "g++": ["g++", "--version"],
        "python3": ["python", "--version"],
    }
    
    if tool_name not in version_commands:
        return None
        
    try:
        result = subprocess.run(version_commands[tool_name], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            output = result.stdout + result.stderr
            # Extract version number from output
            match = re.search(r'(\d+\.\d+(\.\d+)?)', output)
            if match:
                return match.group(1)
    except Exception:
        pass
    return None

def _get_dep_installed_version(dep_name: str, system: str, pm: str | None) -> str | None:
    """Linux: dpkg-query; macOS: brew list; Windows: choco list or direct version check."""
    # Linux-only packages on Windows - skip these by returning compatible version
    if system == "Windows":
        return "999.999.999"  # High version to satisfy any requirement
    
    if not pm:
        return None
        
    try:
        if system == "Linux":
            result = subprocess.run(["dpkg-query", "-W", "-f=${Version}", dep_name], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        elif system == "Darwin":
            result = subprocess.run(["brew", "list", "--versions", dep_name], capture_output=True, text=True)
            if result.stdout:
                parts = result.stdout.split()
                if len(parts) >= 2:
                    return parts[1]
        elif system == "Windows":
            result = subprocess.run(["choco", "list", "--local-only", dep_name], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if dep_name.lower() in line.lower():
                    parts = line.split("|")
                    if len(parts) >= 2:
                        return parts[1]
    except Exception as e:
        logger.error(f"Error getting version for dependency {dep_name}: {e}")
        
    return None

def _is_version_compatible(installed_ver: str, required_min_ver: str) -> bool:
    """Uses packaging.version.parse() for comparison. Handles Debian epoch prefixes."""
    try:
        # Clean Debian epoch prefixes (e.g., "2:1.0.14" -> "1.0.14")
        iv = installed_ver.split(":")[-1] if ":" in installed_ver else installed_ver
        rv = required_min_ver.split(":")[-1] if ":" in required_min_ver else required_min_ver
        
        return parse(iv) >= parse(rv)
    except Exception as e:
        logger.error(f"Error comparing versions {installed_ver} and {required_min_ver}: {e}")
        return False

def check_all_dependencies(registry: dict) -> dict[str, dict]:
    """Runs check_dependencies() for every tool in the registry."""
    all_results = {}
    for tool in registry["tools"]:
        all_results[tool["name"]] = check_dependencies(tool["name"], registry)
    return all_results

def get_problem_dependencies(tool_name: str, registry: dict) -> list[dict]:
    """Returns only deps where status is "missing" OR "incompatible"."""
    results = check_dependencies(tool_name, registry)
    problems = []
    for dep, status in results.items():
        if status["status"] != "ok":
            problems.append({"name": dep, **status})
    return problems
