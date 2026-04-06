from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn
from rich.syntax import Syntax
from pathlib import Path

console = Console()

def print_tools_table(tools_info: list[dict]) -> None:
    """Rich Table: Name | Category | Installed Version | Latest | Status"""
    table = Table(title="eSim Automated Tool Manager")
    table.add_column("Name", style="cyan")
    table.add_column("Category", style="magenta")
    table.add_column("Installed Version", style="green")
    table.add_column("Latest Version", style="blue")
    table.add_column("Status", style="yellow")
    
    for tool in tools_info:
        status = tool.get("status", "Unknown")
        status_style = "green" if status == "Installed" else "red"
        if status == "Update Available":
            status_style = "yellow"
            
        table.add_row(
            tool.get("display_name", tool["name"]),
            tool.get("category", "N/A"),
            str(tool.get("installed_version", "None")),
            str(tool.get("latest_version", "N/A")),
            f"[{status_style}]{status}[/]"
        )
        
    console.print(table)

def print_dependency_table(tool_name: str, deps: dict) -> None:
    """Columns: Dependency | Installed Version | Required Min | Status | Resolution"""
    table = Table(title=f"Dependencies for {tool_name}")
    table.add_column("Dependency", style="cyan")
    table.add_column("Installed Version", style="green")
    table.add_column("Required Min", style="blue")
    table.add_column("Status", style="yellow")
    table.add_column("Resolution", style="magenta")
    
    for dep_name, info in deps.items():
        status_icon = "✓ ok" if info["status"] == "ok" else ("✗ missing" if info["status"] == "missing" else "⚠ incompatible")
        status_style = "green" if info["status"] == "ok" else ("red" if info["status"] == "missing" else "yellow")
        
        resolution = "None needed" if info["status"] == "ok" else (f"Install {dep_name}" if info["status"] == "missing" else f"Upgrade {dep_name}")
        
        table.add_row(
            dep_name,
            str(info.get("installed_version", "None")),
            str(info.get("required_min_version", "N/A")),
            f"[{status_style}]{status_icon}[/]",
            resolution
        )
        
    console.print(table)

def print_update_summary(updates: dict) -> None:
    """Columns: Tool | Installed | Latest | Update Available"""
    table = Table(title="Update Summary")
    table.add_column("Tool", style="cyan")
    table.add_column("Installed", style="green")
    table.add_column("Latest", style="blue")
    table.add_column("Update Available", style="yellow")
    
    for tool_name, info in updates.items():
        table.add_row(
            tool_name,
            str(info.get("installed", "None")),
            str(info.get("latest", "N/A")),
            "Yes" if info.get("update_available") else "No"
        )
        
    console.print(table)

def print_log_tail(n: int = 20) -> None:
    """Opens logs/esim_tool_manager.log, reads last N lines."""
    log_file = Path("logs/esim_tool_manager.log")
    if not log_file.exists():
        console.print("[red]Log file not found.[/]")
        return
        
    try:
        lines = log_file.read_text().splitlines()
        tail_lines = lines[-n:]
        content = "\n".join(tail_lines)
        
        syntax = Syntax(content, "log", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title=f"Last {n} Log Lines"))
    except Exception as e:
        console.print(f"[red]Error reading logs: {e}[/]")

def show_progress():
    """Returns a Rich Progress context manager."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
    )

def print_success(msg: str) -> None:
    console.print(Panel(msg, style="green", title="Success"))

def print_error(msg: str) -> None:
    console.print(Panel(msg, style="red", title="Error"))

def print_warning(msg: str) -> None:
    console.print(Panel(msg, style="yellow", title="Warning"))

def print_info(msg: str) -> None:
    console.print(Panel(msg, style="blue", title="Info"))
