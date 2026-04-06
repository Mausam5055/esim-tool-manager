import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
import os
from pathlib import Path
import json

# Add parent directory to path so we can import tool_manager
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tool_manager.ui.cli import load_registry
from tool_manager import installer, updater, dependency_checker, config

class TextRedirector:
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.configure(state="normal")
        self.widget.insert(tk.END, str, (self.tag,))
        self.widget.see(tk.END)
        self.widget.configure(state="disabled")

    def flush(self):
        pass

class ESimToolManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("eSim Automated Tool Manager")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)
        
        # Setup styling
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Load data
        self.registry = load_registry()
        
        self.setup_ui()
        self.refresh_tools_list()

    def setup_ui(self):
        # Main container
        main_frame = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top section: Tools Table
        top_frame = ttk.LabelFrame(main_frame, text="Available Tools")
        main_frame.add(top_frame, weight=2)
        
        # Treeview for tools
        columns = ("name", "category", "installed_version", "latest_version", "status")
        self.tree = ttk.Treeview(top_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("name", text="Tool Name")
        self.tree.heading("category", text="Category")
        self.tree.heading("installed_version", text="Installed Version")
        self.tree.heading("latest_version", text="Latest Version")
        self.tree.heading("status", text="Status")
        
        self.tree.column("name", width=150)
        self.tree.column("category", width=100)
        self.tree.column("installed_version", width=120)
        self.tree.column("latest_version", width=120)
        self.tree.column("status", width=150)
        
        # Scrollbar for Treeview
        scrollbar = ttk.Scrollbar(top_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_tool_select)
        
        # Action Buttons Frame
        action_frame = ttk.Frame(top_frame)
        action_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        self.btn_install = ttk.Button(action_frame, text="Install", command=self.install_selected, state=tk.DISABLED)
        self.btn_install.pack(fill=tk.X, pady=5)
        
        self.btn_update = ttk.Button(action_frame, text="Update", command=self.update_selected, state=tk.DISABLED)
        self.btn_update.pack(fill=tk.X, pady=5)
        
        self.btn_uninstall = ttk.Button(action_frame, text="Uninstall", command=self.uninstall_selected, state=tk.DISABLED)
        self.btn_uninstall.pack(fill=tk.X, pady=5)
        
        self.btn_check_deps = ttk.Button(action_frame, text="Check Deps", command=self.check_deps_selected, state=tk.DISABLED)
        self.btn_check_deps.pack(fill=tk.X, pady=5)
        
        ttk.Separator(action_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        self.btn_refresh = ttk.Button(action_frame, text="Refresh List", command=self.refresh_tools_list)
        self.btn_refresh.pack(fill=tk.X, pady=5)
        
        self.btn_update_all = ttk.Button(action_frame, text="Update All", command=self.update_all)
        self.btn_update_all.pack(fill=tk.X, pady=5)
        
        # Bottom section: Console Output
        bottom_frame = ttk.LabelFrame(main_frame, text="Console Output")
        main_frame.add(bottom_frame, weight=1)
        
        self.console = scrolledtext.ScrolledText(bottom_frame, wrap=tk.WORD, bg="black", fg="white", font=("Consolas", 10))
        self.console.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.console.configure(state="disabled")
        
        # Setup tags for colored output
        self.console.tag_config("stdout", foreground="white")
        self.console.tag_config("stderr", foreground="red")
        self.console.tag_config("success", foreground="green")
        self.console.tag_config("warning", foreground="yellow")
        
        # Redirect stdout/stderr (optional, for capturing print statements)
        # sys.stdout = TextRedirector(self.console, "stdout")
        # sys.stderr = TextRedirector(self.console, "stderr")
        
    def log(self, message, tag="stdout"):
        self.console.configure(state="normal")
        self.console.insert(tk.END, message + "\n", tag)
        self.console.see(tk.END)
        self.console.configure(state="disabled")

    def refresh_tools_list(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        installed_config = config.get("installed_tools", {})
        
        for tool in self.registry.get("tools", []):
            name = tool["name"]
            display_name = tool.get("display_name", name)
            category = tool.get("category", "N/A")
            latest_version = tool.get("version", "N/A")
            
            installed_info = installed_config.get(name)
            
            if installed_info:
                installed_version = installed_info.get("version", "Unknown")
                
                # Check for update (simplified for UI speed)
                try:
                    from packaging.version import parse
                    if parse(latest_version) > parse(installed_version):
                        status = "Update Available"
                        tags = ("warning",)
                    else:
                        status = "Installed"
                        tags = ("installed",)
                except:
                    status = "Installed"
                    tags = ("installed",)
            else:
                installed_version = "None"
                status = "Not Installed"
                tags = ("not_installed",)
                
            self.tree.insert("", tk.END, iid=name, values=(
                display_name, category, installed_version, latest_version, status
            ), tags=tags)
            
        # Configure tag colors
        self.tree.tag_configure("installed", foreground="green")
        self.tree.tag_configure("warning", foreground="orange")
        self.tree.tag_configure("not_installed", foreground="gray")
        
        self.log("Tools list refreshed.", "stdout")
        
    def on_tool_select(self, event):
        selected = self.tree.selection()
        if not selected:
            self.btn_install.config(state=tk.DISABLED)
            self.btn_update.config(state=tk.DISABLED)
            self.btn_uninstall.config(state=tk.DISABLED)
            self.btn_check_deps.config(state=tk.DISABLED)
            return
            
        tool_id = selected[0]
        item = self.tree.item(tool_id)
        status = item['values'][4]
        
        self.btn_check_deps.config(state=tk.NORMAL)
        
        if status == "Not Installed":
            self.btn_install.config(state=tk.NORMAL)
            self.btn_update.config(state=tk.DISABLED)
            self.btn_uninstall.config(state=tk.DISABLED)
        elif status == "Update Available":
            self.btn_install.config(state=tk.DISABLED)
            self.btn_update.config(state=tk.NORMAL)
            self.btn_uninstall.config(state=tk.NORMAL)
        else: # Installed
            self.btn_install.config(state=tk.DISABLED)
            self.btn_update.config(state=tk.DISABLED)
            self.btn_uninstall.config(state=tk.NORMAL)

    def run_in_thread(self, target_func, *args):
        """Helper to run long tasks without freezing GUI"""
        self.btn_refresh.config(state=tk.DISABLED)
        
        def wrapper():
            try:
                target_func(*args)
            except Exception as e:
                self.log(f"Error: {str(e)}", "stderr")
            finally:
                # Schedule GUI updates back on the main thread
                self.root.after(0, self.refresh_tools_list)
                self.root.after(0, lambda: self.btn_refresh.config(state=tk.NORMAL))
                
        threading.Thread(target=wrapper, daemon=True).start()

    def install_selected(self):
        selected = self.tree.selection()
        if not selected: return
        tool_name = selected[0]
        
        self.log(f"Starting installation for {tool_name}...", "stdout")
        
        def task():
            success = installer.install_tool(tool_name, self.registry)
            if success:
                self.log(f"Successfully installed {tool_name}", "success")
            else:
                self.log(f"Failed to install {tool_name}. Check dependencies or permissions.", "stderr")
                
        self.run_in_thread(task)

    def uninstall_selected(self):
        selected = self.tree.selection()
        if not selected: return
        tool_name = selected[0]
        
        if not messagebox.askyesno("Confirm", f"Are you sure you want to uninstall {tool_name}?"):
            return
            
        self.log(f"Starting uninstallation for {tool_name}...", "stdout")
        
        def task():
            success = installer.uninstall_tool(tool_name, self.registry)
            if success:
                self.log(f"Successfully uninstalled {tool_name}", "success")
            else:
                self.log(f"Failed to uninstall {tool_name}.", "stderr")
                
        self.run_in_thread(task)

    def update_selected(self):
        selected = self.tree.selection()
        if not selected: return
        tool_name = selected[0]
        
        self.log(f"Starting update for {tool_name}...", "stdout")
        
        def task():
            success = updater.update_tool(tool_name, self.registry)
            if success:
                self.log(f"Successfully updated {tool_name}", "success")
            else:
                self.log(f"Failed to update {tool_name}.", "stderr")
                
        self.run_in_thread(task)

    def update_all(self):
        if not messagebox.askyesno("Confirm", "Update all available tools?"):
            return
            
        self.log("Checking for updates for all tools...", "stdout")
        
        def task():
            results = updater.update_all_tools(self.registry)
            for name, success in results.items():
                if success:
                    self.log(f"Successfully updated {name}", "success")
                else:
                    self.log(f"Failed to update {name}.", "stderr")
            self.log("Batch update complete.", "stdout")
            
        self.run_in_thread(task)

    def check_deps_selected(self):
        selected = self.tree.selection()
        if not selected: return
        tool_name = selected[0]
        
        self.log(f"\nChecking dependencies for {tool_name}...", "stdout")
        
        def task():
            deps = dependency_checker.check_dependencies(tool_name, self.registry)
            
            if not deps:
                self.log("No dependencies found or tool not in registry.", "warning")
                return
                
            for dep_name, info in deps.items():
                status = info["status"]
                req_ver = info.get("required_min_version", "Any")
                inst_ver = info.get("installed_version", "None")
                
                if status == "ok":
                    self.log(f"  [OK] {dep_name} (Installed: {inst_ver} >= Required: {req_ver})", "success")
                elif status == "missing":
                    self.log(f"  [MISSING] {dep_name} (Required: {req_ver})", "stderr")
                elif status == "incompatible":
                    self.log(f"  [INCOMPATIBLE] {dep_name} (Installed: {inst_ver} < Required: {req_ver})", "warning")
                    
        self.run_in_thread(task)

def main():
    root = tk.Tk()
    app = ESimToolManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
