import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import threading
import sys
import os
from pathlib import Path
import json

# Add parent directory to path so we can import tool_manager
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tool_manager.ui.cli import load_registry
from tool_manager import installer, updater, dependency_checker, config, docker_generator

# Set customtkinter appearance and theme
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class ESimToolManagerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.cancel_event = None
        
        self.title("eSim Automated Tool Manager")
        self.geometry("950x650")
        self.minsize(850, 550)
        
        # Configure grid layout (1 row, 2 columns)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Load data
        self.registry = load_registry()
        
        self.setup_ui()
        self.refresh_tools_list()

    def setup_ui(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="eSim Tools", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.btn_install = ctk.CTkButton(self.sidebar_frame, text="Install", command=self.install_selected, state="disabled")
        self.btn_install.grid(row=1, column=0, padx=20, pady=10)
        
        self.btn_update = ctk.CTkButton(self.sidebar_frame, text="Update", command=self.update_selected, state="disabled")
        self.btn_update.grid(row=2, column=0, padx=20, pady=10)
        
        self.btn_uninstall = ctk.CTkButton(self.sidebar_frame, text="Uninstall", command=self.uninstall_selected, fg_color="#D32F2F", hover_color="#B71C1C", state="disabled")
        self.btn_uninstall.grid(row=3, column=0, padx=20, pady=10)
        
        self.btn_check_deps = ctk.CTkButton(self.sidebar_frame, text="Check Deps", command=self.check_deps_selected, state="disabled")
        self.btn_check_deps.grid(row=4, column=0, padx=20, pady=10)
        
        self.btn_verify = ctk.CTkButton(self.sidebar_frame, text="Verify", command=self.verify_selected, state="disabled")
        self.btn_verify.grid(row=5, column=0, padx=20, pady=10)
        
        self.btn_docker = ctk.CTkButton(self.sidebar_frame, text="Docker Gen", command=self.generate_docker_selected)
        self.btn_docker.grid(row=6, column=0, padx=20, pady=10)

        self.btn_refresh = ctk.CTkButton(self.sidebar_frame, text="Refresh List", command=self.refresh_tools_list, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.btn_refresh.grid(row=7, column=0, padx=20, pady=10)

        self.btn_cancel = ctk.CTkButton(self.sidebar_frame, text="Cancel", command=self.cancel_operation, fg_color="#F44336", hover_color="#D32F2F", state="disabled")
        self.btn_cancel.grid(row=8, column=0, padx=20, pady=10)
        
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=9, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=10, column=0, padx=20, pady=(10, 20))
        self.appearance_mode_optionemenu.set("System")

        # --- Main Content Frame (Right) ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=2)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Tools Table Frame
        self.table_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.table_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="nsew")
        
        # We still use ttk.Treeview because CustomTkinter doesn't have a native table widget yet
        # But we style it to look more modern
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#2b2b2b",
                        foreground="white",
                        rowheight=35,
                        fieldbackground="#2b2b2b",
                        bordercolor="#343638",
                        borderwidth=0,
                        font=("Helvetica", 11))
        style.map('Treeview', background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading",
                        background="#565b5e",
                        foreground="white",
                        relief="flat",
                        font=("Helvetica", 11, "bold"))
        style.map("Treeview.Heading", background=[('active', '#343638')])

        columns = ("name", "category", "installed_version", "latest_version", "status")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("name", text="Tool Name")
        self.tree.heading("category", text="Category")
        self.tree.heading("installed_version", text="Installed Version")
        self.tree.heading("latest_version", text="Latest Version")
        self.tree.heading("status", text="Status")
        
        self.tree.column("name", width=150, anchor="w")
        self.tree.column("category", width=100, anchor="center")
        self.tree.column("installed_version", width=120, anchor="center")
        self.tree.column("latest_version", width=120, anchor="center")
        self.tree.column("status", width=150, anchor="center")
        
        scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_tool_select)
        
        # Console Output Frame
        self.console_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.console_frame.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="nsew")
        
        self.console_label = ctk.CTkLabel(self.console_frame, text="Console Output", font=ctk.CTkFont(weight="bold"))
        self.console_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        self.console = ctk.CTkTextbox(self.console_frame, wrap="word", font=ctk.CTkFont(family="Consolas", size=12))
        self.console.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
        self.console.configure(state="disabled")

        self.progress_frame = ctk.CTkFrame(self.console_frame, fg_color="transparent")
        self.progress_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="0%", width=40)
        self.progress_label.pack(side=tk.RIGHT)

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)
        # Update treeview colors based on mode
        style = ttk.Style()
        if new_appearance_mode == "Light":
            style.configure("Treeview", background="#ebebeb", foreground="black", fieldbackground="#ebebeb")
            style.configure("Treeview.Heading", background="#d3d3d3", foreground="black")
        else:
            style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b")
            style.configure("Treeview.Heading", background="#565b5e", foreground="white")
        
    def log(self, message, level="info"):
        self.console.configure(state="normal")
        
        # Determine prefix and color based on level (customtkinter textbox doesn't support tags yet like tk.Text, 
        # so we format the string cleanly)
        prefix = ""
        if level == "error":
            prefix = "[ERROR] "
        elif level == "success":
            prefix = "[SUCCESS] "
        elif level == "warning":
            prefix = "[WARNING] "
        else:
            prefix = "[INFO] "
            
        self.console.insert(tk.END, prefix + message + "\n")
        self.console.see(tk.END)
        self.console.configure(state="disabled")

    def refresh_tools_list(self):
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
            
        self.tree.tag_configure("installed", foreground="#4CAF50") # Green
        self.tree.tag_configure("warning", foreground="#FF9800") # Orange
        self.tree.tag_configure("not_installed", foreground="#9E9E9E") # Gray
        
        self.log("Tools list refreshed.")
        
    def on_tool_select(self, event):
        selected = self.tree.selection()
        if not selected:
            self.btn_install.configure(state="disabled")
            self.btn_update.configure(state="disabled")
            self.btn_uninstall.configure(state="disabled")
            self.btn_check_deps.configure(state="disabled")
            self.btn_verify.configure(state="disabled")
            return
            
        tool_id = selected[0]
        item = self.tree.item(tool_id)
        status = item['values'][4]
        
        self.btn_check_deps.configure(state="normal")
        
        if status == "Not Installed":
            self.btn_install.configure(state="normal")
            self.btn_update.configure(state="disabled")
            self.btn_uninstall.configure(state="disabled")
            self.btn_verify.configure(state="disabled")
        elif status == "Update Available":
            self.btn_install.configure(state="disabled")
            self.btn_update.configure(state="normal")
            self.btn_uninstall.configure(state="normal")
            self.btn_verify.configure(state="normal")
        else: # Installed
            self.btn_install.configure(state="disabled")
            self.btn_update.configure(state="disabled")
            self.btn_uninstall.configure(state="normal")
            self.btn_verify.configure(state="normal")

    def cancel_operation(self):
        if self.cancel_event:
            self.cancel_event.set()
            self.log("Cancellation signal sent! Aborting operation...", "warning")
            self.btn_cancel.configure(state="disabled")

    def run_in_thread(self, target_func, *args):
        self.btn_refresh.configure(state="disabled")
        
        def wrapper():
            try:
                target_func(*args)
            except Exception as e:
                self.log(f"{str(e)}", "error")
            finally:
                self.after(0, self.refresh_tools_list)
                self.after(0, lambda: self.btn_refresh.configure(state="normal"))
                
        threading.Thread(target=wrapper, daemon=True).start()

    def install_selected(self):
        selected = self.tree.selection()
        if not selected: return
        tool_name = selected[0]
        
        self.log(f"Starting installation for {tool_name}...")
        self.progress_bar.set(0)
        self.progress_label.configure(text="0%")
        self.cancel_event = threading.Event()
        self.btn_cancel.configure(state="normal")
        
        def update_progress(current, total):
            if total > 0:
                perc = float(current) / float(total)
                self.after(0, lambda p=perc: self.progress_bar.set(p))
                self.after(0, lambda p=perc: self.progress_label.configure(text=f"{int(p*100)}%"))
        
        def task():
            success = installer.install_tool(tool_name, self.registry, progress_callback=update_progress, cancel_event=self.cancel_event)
            self.after(0, lambda: self.btn_cancel.configure(state="disabled"))
            if success:
                self.log(f"Successfully installed {tool_name}", "success")
                self.after(0, lambda: self.progress_bar.set(1.0))
                self.after(0, lambda: self.progress_label.configure(text="100%"))
            else:
                self.log(f"Installer exited: {tool_name}.", "warning")
                
        self.run_in_thread(task)

    def uninstall_selected(self):
        selected = self.tree.selection()
        if not selected: return
        tool_name = selected[0]
        
        if not messagebox.askyesno("Confirm", f"Are you sure you want to uninstall {tool_name}?"):
            return
            
        self.log(f"Starting uninstallation for {tool_name}...")
        
        def task():
            success = installer.uninstall_tool(tool_name, self.registry)
            if success:
                self.log(f"Successfully uninstalled {tool_name}", "success")
            else:
                self.log(f"Failed to uninstall {tool_name}.", "error")
                
        self.run_in_thread(task)

    def update_selected(self):
        selected = self.tree.selection()
        if not selected: return
        tool_name = selected[0]
        
        self.log(f"Starting update for {tool_name}...")
        self.progress_bar.set(0)
        self.progress_label.configure(text="0%")
        self.cancel_event = threading.Event()
        self.btn_cancel.configure(state="normal")
        
        def update_progress(current, total):
            if total > 0:
                perc = float(current) / float(total)
                self.after(0, lambda p=perc: self.progress_bar.set(p))
                self.after(0, lambda p=perc: self.progress_label.configure(text=f"{int(p*100)}%"))
                
        def task():
            success = updater.update_tool(tool_name, self.registry, progress_callback=update_progress, cancel_event=self.cancel_event)
            self.after(0, lambda: self.btn_cancel.configure(state="disabled"))
            if success:
                self.log(f"Successfully updated {tool_name}", "success")
                self.after(0, lambda: self.progress_bar.set(1.0))
                self.after(0, lambda: self.progress_label.configure(text="100%"))
            else:
                self.log(f"Updater exited: {tool_name}.", "warning")
                
        self.run_in_thread(task)

    def check_deps_selected(self):
        selected = self.tree.selection()
        if not selected: return
        tool_name = selected[0]
        
        self.log(f"\nChecking dependencies for {tool_name}...")
        
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
                    self.log(f"  {dep_name} (Installed: {inst_ver} >= Required: {req_ver})", "success")
                elif status == "missing":
                    self.log(f"  {dep_name} (Required: {req_ver})", "error")
                elif status == "incompatible":
                    self.log(f"  {dep_name} (Installed: {inst_ver} < Required: {req_ver})", "warning")
                    
        self.run_in_thread(task)

    def verify_selected(self):
        selected = self.tree.selection()
        if not selected: return
        tool_name = selected[0]
        
        self.log(f"\nVerifying installation for {tool_name}...")
        
        def task():
            success, details = installer.verify_installation(tool_name, self.registry)
            if details:
                self.log(f"Output:\n{details}")
            if success:
                self.log(f"{tool_name} verification successful.", "success")
            else:
                self.log(f"{tool_name} verification failed.", "error")
                
        self.run_in_thread(task)

    def generate_docker_selected(self):
        self.log("\nGenerating Dockerfile...")
        
        def task():
            path = "Dockerfile"
            if docker_generator.generate_dockerfile(self.registry, path):
                self.log(f"Successfully generated {path} in current directory.", "success")
            else:
                self.log(f"Failed to generate {path}.", "error")
                
        self.run_in_thread(task)

def main():
    app = ESimToolManagerGUI()
    app.mainloop()

if __name__ == "__main__":
    main()
