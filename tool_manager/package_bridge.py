import shutil
import subprocess
import platform
from .logger import get_logger

logger = get_logger(__name__)

def detect_package_manager() -> str | None:
    """Returns 'apt', 'homebrew', 'chocolatey', or None."""
    system = platform.system()
    if system == "Linux":
        if shutil.which("apt"):
            return "apt"
    elif system == "Darwin":
        if shutil.which("brew"):
            return "homebrew"
    elif system == "Windows":
        if shutil.which("choco"):
            return "chocolatey"
    return None

def is_package_manager_available(pm: str) -> bool:
    """Checks if specified package manager is available."""
    return shutil.which(pm) is not None

def run_package_manager_install(pm: str, package: str) -> subprocess.CompletedProcess:
    """Runs apt/brew/choco install via subprocess.run() with proper flags."""
    command = []
    if pm == "apt":
        command = ["sudo", "apt", "install", "-y", package]
    elif pm == "homebrew":
        command = ["brew", "install", package]
    elif pm == "chocolatey":
        command = ["choco", "install", package, "-y"]
    else:
        raise ValueError(f"Unsupported package manager: {pm}")
    
    logger.info(f"Running install command: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode != 0:
        logger.error(f"Installation failed with code {result.returncode}")
        logger.debug(f"STDOUT: {result.stdout}")
        logger.debug(f"STDERR: {result.stderr}")
    else:
        logger.info(f"Successfully installed {package} via {pm}")
        
    return result

def get_installed_package_version(pm: str, package: str) -> str | None:
    """
    Returns installed version of a package.
    apt:   apt-cache policy <package>  → parse "Installed: X.Y.Z"
    brew:  brew list --versions <package>
    choco: choco list --local-only <package>
    """
    try:
        if pm == "apt":
            result = subprocess.run(["apt-cache", "policy", package], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if "Installed:" in line:
                    version = line.split("Installed:")[1].strip()
                    return version if version != "(none)" else None
        elif pm == "homebrew":
            result = subprocess.run(["brew", "list", "--versions", package], capture_output=True, text=True)
            if result.stdout:
                # Format: package version1 version2 ...
                parts = result.stdout.split()
                if len(parts) >= 2:
                    return parts[1]
        elif pm == "chocolatey":
            result = subprocess.run(["choco", "list", "--local-only", package], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if package.lower() in line.lower():
                    # Format: package|version
                    parts = line.split("|")
                    if len(parts) >= 2:
                        return parts[1]
    except Exception as e:
        logger.error(f"Error getting version for {package} via {pm}: {e}")
        
    return None
