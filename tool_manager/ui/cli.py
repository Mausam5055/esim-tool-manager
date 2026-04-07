import typer
import json
import os
from pathlib import Path
from typing import Optional
from rich.console import Console
from .. import config
from .. import installer
from .. import updater
from .. import dependency_checker
from .. import env_manager
from . import display

app = typer.Typer(help="eSim Automated Tool Manager")
console = Console()

REGISTRY_PATH = Path(__file__).parent.parent.parent / "data" / "tools_registry.json"

def load_registry() -> dict:
    """Loads tool registry."""
    if not REGISTRY_PATH.exists():
        display.print_error(f"Registry not found at {REGISTRY_PATH}")
        return {"tools": []}
        
    try:
        with open(REGISTRY_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        display.print_error(f"Failed to load registry: {e}")
        return {"tools": []}

@app.command()
def install(tool_name: str = typer.Argument(..., help="Name of the tool to install"), version: Optional[str] = None, force: bool = False):
    """Installs a specific tool."""
    registry = load_registry()
    success = installer.install_tool(tool_name, registry, version, force)
    if success:
        display.print_success(f"Installed {tool_name}")
    else:
        display.print_error(f"Failed to install {tool_name}")

@app.command()
def install_all(force: bool = False):
    """Installs all tools in registry."""
    registry = load_registry()
    for tool in registry["tools"]:
        display.print_info(f"Installing {tool['name']}...")
        installer.install_tool(tool["name"], registry, force=force)

@app.command()
def uninstall(tool_name: str = typer.Argument(..., help="Name of the tool to uninstall")):
    """Uninstalls a specific tool."""
    registry = load_registry()
    if installer.uninstall_tool(tool_name, registry):
        display.print_success(f"Uninstalled {tool_name}")
    else:
        display.print_error(f"Failed to uninstall {tool_name}")

@app.command()
def update(tool_name: Optional[str] = typer.Argument(None, help="Name of the tool to update (leave empty for all)")):
    """Updates a tool or all tools."""
    registry = load_registry()
    if tool_name:
        update_info = updater.check_tool_update(tool_name, registry)
        if not update_info or not update_info.get("update_available"):
            display.print_info(f"No updates available for {tool_name}")
        elif updater.update_tool(tool_name, registry):
            display.print_success(f"Updated {tool_name}")
        else:
            display.print_error(f"Failed to update {tool_name}")
    else:
        results = updater.update_all_tools(registry)
        if not results:
            display.print_info("No updates available for any installed tools.")
        for name, success in results.items():
            if success:
                display.print_success(f"Updated {name}")
            else:
                display.print_error(f"Failed to update {name}")

@app.command()
def check_updates():
    """Checks for tool updates."""
    registry = load_registry()
    updates = updater.check_all_updates(registry)
    display.print_update_summary(updates)

@app.command()
def list():
    """Lists all tools and their status."""
    registry = load_registry()
    installed_config = config.get("installed_tools", {})
    
    tools_info = []
    for tool in registry["tools"]:
        name = tool["name"]
        installed_info = installed_config.get(name)
        
        status = "Not Installed"
        installed_version = "None"
        
        if installed_info:
            status = "Installed"
            installed_version = installed_info.get("version", "Unknown")
            
            # Check for update availability
            update_info = updater.check_tool_update(name, registry)
            if update_info.get("update_available"):
                status = "Update Available"
                
        tools_info.append({
            "name": name,
            "display_name": tool.get("display_name", name),
            "category": tool.get("category", "N/A"),
            "installed_version": installed_version,
            "latest_version": tool.get("version", "N/A"),
            "status": status
        })
        
    display.print_tools_table(tools_info)

@app.command()
def verify(tool_name: str = typer.Argument(..., help="Name of the tool to verify")):
    """Verifies tool installation."""
    registry = load_registry()
    if installer.verify_installation(tool_name, registry):
        display.print_success(f"{tool_name} verification successful.")
    else:
        display.print_error(f"{tool_name} verification failed.")

@app.command()
def check_deps(tool_name: Optional[str] = typer.Argument(None, help="Name of the tool to check dependencies for (leave empty for all)")):
    """Checks dependencies for a tool or all tools."""
    registry = load_registry()
    if tool_name:
        deps = dependency_checker.check_dependencies(tool_name, registry)
        display.print_dependency_table(tool_name, deps)
    else:
        all_deps = dependency_checker.check_all_dependencies(registry)
        for name, deps in all_deps.items():
            display.print_dependency_table(name, deps)

@app.command()
def logs(tail: int = 20):
    """Shows last N lines of log file."""
    display.print_log_tail(tail)

@app.command()
def config_show():
    """Shows current configuration."""
    current_config = config.load_config()
    console.print_json(data=current_config)

@app.command()
def config_set(key: str, value: str):
    """Sets a configuration key."""
    # Simple type conversion
    if value.lower() == "true":
        value = True
    elif value.lower() == "false":
        value = False
        
    config.set(key, value)
    display.print_success(f"Config updated: {key} = {value}")

if __name__ == "__main__":
    app()
