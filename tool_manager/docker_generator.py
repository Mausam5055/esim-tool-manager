import os
import time
from typing import Dict

def generate_dockerfile(registry: dict, output_path: str = "Dockerfile") -> bool:
    """
    Generates a Dockerfile setting up an Ubuntu-based environment with all
    tools and their dependencies defined in the registry.
    """
    try:
        lines = []
        lines.append("# Auto-generated Dockerfile for eSim Tool Manager")
        lines.append(f"# Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("FROM ubuntu:22.04")
        lines.append("")
        lines.append("# Set non-interactive to avoid timezone prompts during apt installs")
        lines.append("ENV DEBIAN_FRONTEND=noninteractive")
        lines.append("")
        
        packages = []
        env_vars = {}
        
        for tool in registry.get("tools", []):
            # Collect dependencies
            if "dependencies" in tool:
                packages.extend(tool["dependencies"])
                
            # Collect tool package if available via apt
            linux_platform = tool.get("platforms", {}).get("linux", {})
            if linux_platform.get("package_manager") == "apt" and linux_platform.get("package_name"):
                packages.append(linux_platform["package_name"])
                
            # Collect env vars
            if "env_vars" in tool:
                for k, v in tool["env_vars"].items():
                    env_vars[k] = v
                    
        # Remove duplicates while preserving order
        packages = list(dict.fromkeys(packages))
        
        if packages:
            lines.append("# Update system and install necessary packages")
            lines.append("RUN apt-get update && apt-get install -y \\")
            for i, pkg in enumerate(packages):
                if i < len(packages) - 1:
                    lines.append(f"    {pkg} \\")
                else:
                    lines.append(f"    {pkg} \\")
            lines.append("    && rm -rf /var/lib/apt/lists/*")
            lines.append("")
            
        if env_vars:
            lines.append("# Configure Tool Environment Variables")
            for k, v in env_vars.items():
                lines.append(f"ENV {k}=\"{v}\"")
                if k.endswith("HOME") or k.endswith("DIR"):
                    lines.append(f"ENV PATH=\"$PATH:${k}/bin\"")
            lines.append("")
            
        lines.append("# Set default working directory")
        lines.append("WORKDIR /workspace")
        lines.append("")
        lines.append("# Provide a default command")
        lines.append('CMD ["/bin/bash"]')
        
        with open(output_path, "w") as f:
            f.write("\n".join(lines) + "\n")
            
        return True
    except Exception as e:
        print(f"Error generating Dockerfile: {str(e)}")
        return False
