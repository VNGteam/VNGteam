import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import os
import sys
import json
import time
import platform
import logging
from typing import List, Dict, Optional
import asyncio
import aiohttp
import queue
from datetime import datetime

# Platform-specific imports
if platform.system() == "Windows":
    try:
        import winreg
    except ImportError:
        winreg = None
else:
    winreg = None

class LogHandler(logging.Handler):
    """Custom log handler để hiển thị logs trong text widget"""
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        
    def emit(self, record):
        msg = self.format(record)
        self.text_widget.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.text_widget.see(tk.END)

class CmdManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced CMD/Script Manager & Cloudflare DNS Updater")
        self.root.geometry("1200x800")
        
        # Initialize variables
        self.processes = []
        self.text_areas = []
        self.entries = []
        self.scripts = []
        self.cloudflare_accounts = []
        self.config_file = "config.json"
        self.current_ip = None
        self.ip_check_threads = {}
        self.log_queue = queue.Queue()
        
        # Setup logging
        self.setup_logging()
        
        # Load config
        self.load_config()
        
        # Create GUI
        self.create_gui()
        
        # Setup auto-save
        self.setup_auto_save()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start IP monitoring for Cloudflare accounts
        self.start_cloudflare_monitoring()

    def setup_logging(self):
        """Thiết lập logging system"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('cmd_manager.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def create_gui(self):
        """Tạo giao diện người dùng"""
        # Create menu bar
        self.create_menu_bar()
        
        # Create main notebook
        self.tab_control = ttk.Notebook(self.root)
        self.tab_control.pack(expand=1, fill="both", padx=5, pady=5)

        # Scripts Tab
        self.create_scripts_tab()
        
        # Cloudflare Tab
        self.create_cloudflare_tab()
        
        # Logs Tab
        self.create_logs_tab()
        
        # Status bar
        self.create_status_bar()

    def create_menu_bar(self):
        """Tạo menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import Config", command=self.import_config)
        file_menu.add_command(label="Export Config", command=self.export_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        if platform.system() == "Windows":
            tools_menu.add_command(label="Add to Startup", command=self.add_to_startup)
            tools_menu.add_command(label="Remove from Startup", command=self.remove_from_startup)
        tools_menu.add_command(label="Check All IPs", command=self.check_all_ips)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_scripts_tab(self):
        """Tạo tab quản lý scripts"""
        self.scripts_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.scripts_tab, text="Scripts")

        # Controls frame
        controls_frame = ttk.LabelFrame(self.scripts_tab, text="Script Controls")
        controls_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Add Script", command=self.add_script).pack(side="left", padx=5, pady=5)
        ttk.Button(controls_frame, text="Delete Script", command=self.delete_script).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Edit Script", command=self.edit_script).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Restart All", command=self.restart_all_scripts).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Stop All", command=self.stop_all_scripts).pack(side="left", padx=5)

        # Scripts list frame
        list_frame = ttk.LabelFrame(self.scripts_tab, text="Scripts")
        list_frame.pack(fill="x", padx=5, pady=5)
        
        # Create treeview for better script management
        columns = ('Name', 'File', 'Status', 'Auto Run')
        self.scripts_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=6)
        
        for col in columns:
            self.scripts_tree.heading(col, text=col)
            self.scripts_tree.column(col, width=150)
        
        # Add scrollbar
        scrollbar_scripts = ttk.Scrollbar(list_frame, orient="vertical", command=self.scripts_tree.yview)
        self.scripts_tree.configure(yscrollcommand=scrollbar_scripts.set)
        
        self.scripts_tree.pack(side="left", fill="both", expand=True)
        scrollbar_scripts.pack(side="right", fill="y")
        
        # Script outputs frame
        self.script_outputs_frame = ttk.LabelFrame(self.scripts_tab, text="Script Outputs")
        self.script_outputs_frame.pack(expand=1, fill="both", padx=5, pady=5)
        
        # Update scripts display
        self.update_scripts_display()
        
        # Create script frames
        for i, script_info in enumerate(self.scripts):
            self.create_script_frame(i, script_info)

    def create_cloudflare_tab(self):
        """Tạo tab quản lý Cloudflare"""
        self.cloudflare_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.cloudflare_tab, text="Cloudflare DNS")

        # Controls frame
        cf_controls_frame = ttk.LabelFrame(self.cloudflare_tab, text="Cloudflare Controls")
        cf_controls_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(cf_controls_frame, text="Add Account", command=self.add_cloudflare_account).pack(side="left", padx=5, pady=5)
        ttk.Button(cf_controls_frame, text="Delete Selected", command=self.delete_cloudflare_item).pack(side="left", padx=5)
        ttk.Button(cf_controls_frame, text="Test Connection", command=self.test_cloudflare_connection).pack(side="left", padx=5)
        ttk.Button(cf_controls_frame, text="Force Update", command=self.force_update_dns).pack(side="left", padx=5)

        # Current IP display
        ip_frame = ttk.LabelFrame(self.cloudflare_tab, text="Current Public IP")
        ip_frame.pack(fill="x", padx=5, pady=5)
        
        self.ip_label = ttk.Label(ip_frame, text="Checking IP...", font=("Arial", 12))
        self.ip_label.pack(pady=5)
        
        # Cloudflare accounts and domains list
        cf_list_frame = ttk.LabelFrame(self.cloudflare_tab, text="Accounts & Domains")
        cf_list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create treeview for Cloudflare management
        cf_columns = ('Type', 'Name', 'Value', 'Status', 'Last Update')
        self.cloudflare_tree = ttk.Treeview(cf_list_frame, columns=cf_columns, show='headings')
        
        for col in cf_columns:
            self.cloudflare_tree.heading(col, text=col)
            self.cloudflare_tree.column(col, width=120)
        
        scrollbar_cf = ttk.Scrollbar(cf_list_frame, orient="vertical", command=self.cloudflare_tree.yview)
        self.cloudflare_tree.configure(yscrollcommand=scrollbar_cf.set)
        
        self.cloudflare_tree.pack(side="left", fill="both", expand=True)
        scrollbar_cf.pack(side="right", fill="y")
        
        self.update_cloudflare_display()

    def create_logs_tab(self):
        """Tạo tab hiển thị logs"""
        self.logs_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.logs_tab, text="Logs")
        
        # Log controls
        log_controls = ttk.Frame(self.logs_tab)
        log_controls.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(log_controls, text="Clear Logs", command=self.clear_logs).pack(side="left", padx=5)
        ttk.Button(log_controls, text="Save Logs", command=self.save_logs).pack(side="left", padx=5)
        
        # Log text area
        log_frame = ttk.Frame(self.logs_tab)
        log_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, state=tk.DISABLED)
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")
        
        # Add log handler
        log_handler = LogHandler(self.log_text)
        log_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        self.logger.addHandler(log_handler)

    def create_status_bar(self):
        """Tạo status bar"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill="x", side="bottom")
        
        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side="left", padx=5)
        
        # Add separator
        ttk.Separator(self.status_bar, orient="vertical").pack(side="left", fill="y", padx=5)
        
        # Script count
        self.script_count_label = ttk.Label(self.status_bar, text="Scripts: 0")
        self.script_count_label.pack(side="left", padx=5)
        
        # IP status
        self.ip_status_label = ttk.Label(self.status_bar, text="IP: Unknown")
        self.ip_status_label.pack(side="right", padx=5)

    def load_config(self):
        """Tải cấu hình từ file JSON"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.scripts = config.get("scripts", [])
                    self.cloudflare_accounts = config.get("cloudflare_accounts", [])
                    self.logger.info(f"Loaded config: {len(self.scripts)} scripts, {len(self.cloudflare_accounts)} CF accounts")
            else:
                self.scripts = []
                self.cloudflare_accounts = []
                self.logger.info("No config file found, starting with empty configuration")
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            messagebox.showerror("Error", f"Failed to load config: {e}")
            self.scripts = []
            self.cloudflare_accounts = []

    def save_config(self):
        """Lưu cấu hình vào file JSON"""
        try:
            config = {
                "scripts": self.scripts,
                "cloudflare_accounts": self.cloudflare_accounts,
                "version": "2.0",
                "last_saved": datetime.now().isoformat()
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            self.logger.info("Configuration saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            messagebox.showerror("Error", f"Failed to save config: {e}")

    def setup_auto_save(self):
        """Thiết lập tự động lưu cấu hình"""
        def auto_save():
            self.save_config()
            self.root.after(300000, auto_save)  # Auto-save every 5 minutes
        
        self.root.after(300000, auto_save)

    def add_script(self):
        """Thêm script mới"""
        file_path = filedialog.askopenfilename(
            title="Select Script File",
            filetypes=[
                ("Python files", "*.py"),
                ("JavaScript files", "*.js"),
                ("Batch files", "*.bat"),
                ("Shell scripts", "*.sh"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
            
        # Dialog để nhập thông tin script
        dialog = ScriptConfigDialog(self.root, file_path)
        if dialog.result:
            script_info = dialog.result
            script_info["path"] = file_path
            script_info["created"] = datetime.now().isoformat()
            script_info["status"] = "stopped"
            
            self.scripts.append(script_info)
            self.save_config()
            self.update_scripts_display()
            
            # Create script frame
            index = len(self.scripts) - 1
            self.create_script_frame(index, script_info)
            
            self.logger.info(f"Added script: {script_info['name']}")

    def delete_script(self):
        """Xóa script được chọn"""
        selection = self.scripts_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a script to delete!")
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to delete the selected script?"):
            item = selection[0]
            index = int(self.scripts_tree.item(item)['values'][0]) if self.scripts_tree.item(item)['values'] else 0
            
            # Stop process if running
            if index < len(self.processes) and self.processes[index] and self.processes[index].poll() is None:
                self.processes[index].terminate()
                
            # Remove from lists
            if index < len(self.scripts):
                script_name = self.scripts[index]['name']
                self.scripts.pop(index)
                
            self.rebuild_gui()
            self.save_config()
            self.logger.info(f"Deleted script: {script_name}")

    def edit_script(self):
        """Chỉnh sửa script được chọn"""
        selection = self.scripts_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a script to edit!")
            return
            
        item = selection[0]
        # Get script index from treeview
        for i, script in enumerate(self.scripts):
            if self.scripts_tree.item(item)['values'][1] == script['name']:
                dialog = ScriptConfigDialog(self.root, script['path'], script)
                if dialog.result:
                    self.scripts[i].update(dialog.result)
                    self.save_config()
                    self.update_scripts_display()
                    self.logger.info(f"Updated script: {script['name']}")
                break

    def create_script_frame(self, index: int, script_info: Dict):
        """Tạo khung hiển thị cho script"""
        if index >= len(self.text_areas):
            # Extend lists if needed
            while len(self.text_areas) <= index:
                self.text_areas.append(None)
                self.entries.append(None)
                self.processes.append(None)
        
        frame = ttk.LabelFrame(self.script_outputs_frame, text=script_info['name'])
        row = index // 2
        col = index % 2
        frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew", ipadx=5, ipady=5)
        
        # Configure grid weights
        self.script_outputs_frame.grid_rowconfigure(row, weight=1)
        self.script_outputs_frame.grid_columnconfigure(col, weight=1)
        
        # Controls frame
        controls_frame = ttk.Frame(frame)
        controls_frame.pack(fill="x", padx=5, pady=2)
        
        # Status indicator
        status_label = ttk.Label(controls_frame, text="●", foreground="red")
        status_label.pack(side="left", padx=2)
        
        # Start/Stop button
        start_stop_btn = ttk.Button(controls_frame, text="Start", 
                                   command=lambda: self.toggle_script(index))
        start_stop_btn.pack(side="left", padx=5)
        
        # Auto-run checkbox
        auto_run_var = tk.BooleanVar(value=script_info.get('auto_run', False))
        auto_check = ttk.Checkbutton(controls_frame, text="Auto Run", variable=auto_run_var,
                                   command=lambda: self.toggle_auto_run(index, auto_run_var.get()))
        auto_check.pack(side="left", padx=5)
        
        # Text area for output
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill="both", expand=True, padx=5, pady=2)
        
        text_area = tk.Text(text_frame, height=8, width=50, wrap=tk.WORD)
        text_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_area.yview)
        text_area.configure(yscrollcommand=text_scrollbar.set)
        
        text_area.pack(side="left", fill="both", expand=True)
        text_scrollbar.pack(side="right", fill="y")
        
        self.text_areas[index] = text_area
        
        # Input frame
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill="x", padx=5, pady=2)
        
        entry = ttk.Entry(input_frame)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        entry.bind('<Return>', lambda e: self.send_command_to_script(index))
        
        send_btn = ttk.Button(input_frame, text="Send", command=lambda: self.send_command_to_script(index))
        send_btn.pack(side="right")
        
        self.entries[index] = entry
        
        # Auto-start if enabled
        if script_info.get('auto_run', False):
            self.root.after(1000, lambda: self.start_script(index))

    def toggle_script(self, index: int):
        """Bật/tắt script"""
        if index < len(self.processes) and self.processes[index] and self.processes[index].poll() is None:
            self.stop_script(index)
        else:
            self.start_script(index)

    def start_script(self, index: int):
        """Khởi động script"""
        if index >= len(self.scripts):
            return
            
        script_info = self.scripts[index]
        script_path = script_info['path']
        
        try:
            # Determine command based on file extension
            ext = os.path.splitext(script_path)[1].lower()
            
            if ext == '.py':
                cmd = [sys.executable, script_path]
            elif ext == '.js':
                cmd = ['node', script_path]
            elif ext == '.bat':
                if platform.system() == "Windows":
                    cmd = ['cmd', '/c', script_path]
                else:
                    cmd = ['wine', 'cmd', '/c', script_path]
            elif ext == '.sh':
                cmd = ['bash', script_path]
            else:
                raise ValueError(f"Unsupported script type: {ext}")
            
            # Start process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,
                cwd=os.path.dirname(script_path) if os.path.dirname(script_path) else None
            )
            
            # Store process
            while len(self.processes) <= index:
                self.processes.append(None)
            self.processes[index] = process
            
            # Update status
            self.scripts[index]['status'] = 'running'
            self.update_scripts_display()
            
            # Start output reading thread
            threading.Thread(target=self.read_script_output, args=(index, process), daemon=True).start()
            
            self.logger.info(f"Started script: {script_info['name']}")
            
        except Exception as e:
            self.logger.error(f"Failed to start script {script_info['name']}: {e}")
            if index < len(self.text_areas) and self.text_areas[index]:
                self.text_areas[index].insert(tk.END, f"Error starting script: {e}\n")

    def stop_script(self, index: int):
        """Dừng script"""
        if index < len(self.processes) and self.processes[index]:
            try:
                self.processes[index].terminate()
                # Wait a bit for graceful termination
                try:
                    self.processes[index].wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.processes[index].kill()
                
                self.scripts[index]['status'] = 'stopped'
                self.update_scripts_display()
                
                if index < len(self.text_areas) and self.text_areas[index]:
                    self.text_areas[index].insert(tk.END, "\n--- Script stopped ---\n")
                
                self.logger.info(f"Stopped script: {self.scripts[index]['name']}")
                
            except Exception as e:
                self.logger.error(f"Error stopping script: {e}")

    def read_script_output(self, index: int, process: subprocess.Popen):
        """Đọc output từ script"""
        try:
            while process.poll() is None:
                # Read stdout
                if process.stdout:
                    line = process.stdout.readline()
                    if line and index < len(self.text_areas) and self.text_areas[index]:
                        self.root.after(0, lambda l=line: self.append_to_text_area(index, l))
                
                # Read stderr
                if process.stderr:
                    line = process.stderr.readline()
                    if line and index < len(self.text_areas) and self.text_areas[index]:
                        self.root.after(0, lambda l=line: self.append_to_text_area(index, f"[ERROR] {l}"))
                        
        except Exception as e:
            self.logger.error(f"Error reading script output: {e}")
        finally:
            # Update status when process ends
            if index < len(self.scripts):
                self.scripts[index]['status'] = 'stopped'
                self.root.after(0, self.update_scripts_display)

    def append_to_text_area(self, index: int, text: str):
        """Thêm text vào text area (thread-safe)"""
        if index < len(self.text_areas) and self.text_areas[index]:
            self.text_areas[index].insert(tk.END, text)
            self.text_areas[index].see(tk.END)

    def send_command_to_script(self, index: int):
        """Gửi lệnh đến script"""
        if (index < len(self.processes) and self.processes[index] and 
            self.processes[index].poll() is None and index < len(self.entries) and self.entries[index]):
            
            command = self.entries[index].get()
            if command.strip():
                try:
                    self.processes[index].stdin.write(command + '\n')
                    self.processes[index].stdin.flush()
                    self.entries[index].delete(0, tk.END)
                    
                    # Echo command in text area
                    if index < len(self.text_areas) and self.text_areas[index]:
                        self.text_areas[index].insert(tk.END, f"> {command}\n")
                        
                except Exception as e:
                    self.logger.error(f"Error sending command to script: {e}")

    def toggle_auto_run(self, index: int, state: bool):
        """Bật/tắt auto run cho script"""
        if index < len(self.scripts):
            self.scripts[index]['auto_run'] = state
            self.save_config()
            self.update_scripts_display()

    def restart_all_scripts(self):
        """Khởi động lại tất cả scripts"""
        if messagebox.askyesno("Confirm", "Restart all scripts?"):
            self.stop_all_scripts()
            time.sleep(1)
            for i, script in enumerate(self.scripts):
                if script.get('auto_run', False):
                    self.start_script(i)

    def stop_all_scripts(self):
        """Dừng tất cả scripts"""
        for i in range(len(self.processes)):
            if self.processes[i] and self.processes[i].poll() is None:
                self.stop_script(i)

    def update_scripts_display(self):
        """Cập nhật hiển thị danh sách scripts"""
        # Clear treeview
        for item in self.scripts_tree.get_children():
            self.scripts_tree.delete(item)
        
        # Add scripts
        for i, script in enumerate(self.scripts):
            status = script.get('status', 'stopped')
            auto_run = "Yes" if script.get('auto_run', False) else "No"
            
            self.scripts_tree.insert('', 'end', values=(
                i, script['name'], os.path.basename(script['path']), status, auto_run
            ))
        
        # Update status bar
        if hasattr(self, 'script_count_label'):
            self.script_count_label.config(text=f"Scripts: {len(self.scripts)}")

    def rebuild_gui(self):
        """Xây dựng lại GUI cho scripts"""
        # Clear script outputs frame
        for widget in self.script_outputs_frame.winfo_children():
            widget.destroy()
        
        # Reset lists
        self.text_areas = []
        self.entries = []
        self.processes = []
        
        # Recreate script frames
        for i, script_info in enumerate(self.scripts):
            self.create_script_frame(i, script_info)
        
        self.update_scripts_display()

    # Cloudflare DNS methods
    def add_cloudflare_account(self):
        """Thêm tài khoản Cloudflare"""
        dialog = CloudflareConfigDialog(self.root)
        if dialog.result:
            self.cloudflare_accounts.append(dialog.result)
            self.save_config()
            self.update_cloudflare_display()
            self.start_ip_monitoring_for_account(dialog.result)
            self.logger.info("Added new Cloudflare account")

    def delete_cloudflare_item(self):
        """Xóa item Cloudflare được chọn"""
        selection = self.cloudflare_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to delete!")
            return
        
        if messagebox.askyesno("Confirm", "Delete selected Cloudflare item?"):
            # Implementation for deleting CF items
            # This would need more sophisticated logic to handle accounts vs domains
            pass

    def test_cloudflare_connection(self):
        """Test kết nối Cloudflare"""
        # Implementation for testing CF connection
        pass

    def force_update_dns(self):
        """Buộc cập nhật DNS"""
        self.current_ip = None  # Reset current IP to force update
        for account in self.cloudflare_accounts:
            threading.Thread(target=self.update_cloudflare_dns, args=(account,), daemon=True).start()

    def start_cloudflare_monitoring(self):
        """Bắt đầu giám sát IP cho tất cả tài khoản Cloudflare"""
        for account in self.cloudflare_accounts:
            self.start_ip_monitoring_for_account(account)

    def start_ip_monitoring_for_account(self, account: Dict):
        """Bắt đầu giám sát IP cho một tài khoản"""
        def monitor():
            while True:
                try:
                    self.update_cloudflare_dns(account)
                    time.sleep(account.get('check_interval', 300))
                except Exception as e:
                    self.logger.error(f"Error in IP monitoring: {e}")
                    time.sleep(60)  # Wait before retrying
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        
        # Store thread reference
        account_id = account.get('api_token', '')[:8]
        self.ip_check_threads[account_id] = thread

    async def get_public_ip_async(self) -> Optional[str]:
        """Lấy IP công cộng (async version)"""
        urls = [
            'https://api.ipify.org',
            'https://ipv4.icanhazip.com',
            'https://checkip.amazonaws.com'
        ]
        
        async with aiohttp.ClientSession() as session:
            for url in urls:
                try:
                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            ip = (await response.text()).strip()
                            return ip
                except Exception:
                    continue
        return None

    def get_public_ip(self) -> Optional[str]:
        """Lấy IP công cộng (sync version)"""
        import requests
        urls = [
            'https://api.ipify.org',
            'https://ipv4.icanhazip.com',
            'https://checkip.amazonaws.com'
        ]
        
        for url in urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    return response.text.strip()
            except Exception:
                continue
        return None

    def update_cloudflare_dns(self, account: Dict):
        """Cập nhật DNS Cloudflare"""
        try:
            new_ip = self.get_public_ip()
            if not new_ip:
                self.logger.warning("Could not retrieve public IP")
                return
            
            # Update IP display
            self.root.after(0, lambda: self.ip_label.config(text=f"Current IP: {new_ip}"))
            self.root.after(0, lambda: self.ip_status_label.config(text=f"IP: {new_ip}"))
            
            if new_ip == self.current_ip:
                return  # No change
            
            self.current_ip = new_ip
            self.logger.info(f"IP changed to: {new_ip}")
            
            # Update DNS records
            headers = {
                'Authorization': f'Bearer {account["api_token"]}',
                'Content-Type': 'application/json'
            }
            
            for domain in account.get('domains', []):
                try:
                    data = {
                        'type': 'A',
                        'name': domain['record_name'],
                        'content': new_ip,
                        'ttl': domain.get('ttl', 1),
                        'proxied': domain.get('proxied', True)
                    }
                    
                    url = f'https://api.cloudflare.com/client/v4/zones/{domain["zone_id"]}/dns_records/{domain["record_id"]}'
                    
                    import requests
                    response = requests.put(url, headers=headers, json=data, timeout=30)
                    
                    if response.status_code == 200:
                        self.logger.info(f"DNS updated successfully: {domain['record_name']} -> {new_ip}")
                        domain['last_update'] = datetime.now().isoformat()
                        domain['status'] = 'success'
                    else:
                        self.logger.error(f"DNS update failed for {domain['record_name']}: {response.text}")
                        domain['status'] = 'failed'
                        
                except Exception as e:
                    self.logger.error(f"Error updating DNS for {domain['record_name']}: {e}")
                    domain['status'] = 'error'
            
            # Update display
            self.root.after(0, self.update_cloudflare_display)
            
        except Exception as e:
            self.logger.error(f"Error in Cloudflare DNS update: {e}")

    def update_cloudflare_display(self):
        """Cập nhật hiển thị Cloudflare"""
        # Clear treeview
        for item in self.cloudflare_tree.get_children():
            self.cloudflare_tree.delete(item)
        
        # Add accounts and domains
        for account in self.cloudflare_accounts:
            api_token_display = account['api_token'][:8] + "..."
            interval_minutes = account.get('check_interval', 300) / 60
            
            # Add account
            account_item = self.cloudflare_tree.insert('', 'end', values=(
                'Account', api_token_display, f"{interval_minutes} min", 'Active', ''
            ))
            
            # Add domains
            for domain in account.get('domains', []):
                status = domain.get('status', 'unknown')
                last_update = domain.get('last_update', 'Never')
                if last_update != 'Never':
                    try:
                        last_update = datetime.fromisoformat(last_update).strftime('%H:%M:%S')
                    except:
                        pass
                
                self.cloudflare_tree.insert(account_item, 'end', values=(
                    'Domain', domain['record_name'], domain.get('domain', ''), status, last_update
                ))

    # Utility methods
    def check_all_ips(self):
        """Kiểm tra tất cả IPs"""
        current_ip = self.get_public_ip()
        if current_ip:
            self.ip_label.config(text=f"Current IP: {current_ip}")
            self.ip_status_label.config(text=f"IP: {current_ip}")
            self.logger.info(f"Current public IP: {current_ip}")
        else:
            self.logger.warning("Could not retrieve public IP")

    def import_config(self):
        """Import cấu hình từ file"""
        file_path = filedialog.askopenfilename(
            title="Import Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.scripts = config.get('scripts', [])
                self.cloudflare_accounts = config.get('cloudflare_accounts', [])
                
                self.save_config()
                self.rebuild_gui()
                self.update_cloudflare_display()
                
                messagebox.showinfo("Success", "Configuration imported successfully!")
                self.logger.info(f"Configuration imported from: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import configuration: {e}")
                self.logger.error(f"Import failed: {e}")

    def export_config(self):
        """Export cấu hình ra file"""
        file_path = filedialog.asksaveasfilename(
            title="Export Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                config = {
                    "scripts": self.scripts,
                    "cloudflare_accounts": self.cloudflare_accounts,
                    "version": "2.0",
                    "exported": datetime.now().isoformat()
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
                
                messagebox.showinfo("Success", "Configuration exported successfully!")
                self.logger.info(f"Configuration exported to: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export configuration: {e}")
                self.logger.error(f"Export failed: {e}")

    def clear_logs(self):
        """Xóa logs"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def save_logs(self):
        """Lưu logs ra file"""
        file_path = filedialog.asksaveasfilename(
            title="Save Logs",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                logs = self.log_text.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(logs)
                messagebox.showinfo("Success", "Logs saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save logs: {e}")

    def add_to_startup(self):
        """Thêm vào startup (Windows only)"""
        if platform.system() != "Windows" or not winreg:
            messagebox.showwarning("Warning", "Startup registration is only available on Windows!")
            return
        
        try:
            script_path = os.path.abspath(sys.argv[0])
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Microsoft\Windows\CurrentVersion\Run", 
                               0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "CmdManagerAdvanced", 0, winreg.REG_SZ, 
                            f'"{sys.executable}" "{script_path}"')
            winreg.CloseKey(key)
            
            messagebox.showinfo("Success", "Application added to startup!")
            self.logger.info("Added to Windows startup")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add to startup: {e}")
            self.logger.error(f"Startup registration failed: {e}")

    def remove_from_startup(self):
        """Xóa khỏi startup (Windows only)"""
        if platform.system() != "Windows" or not winreg:
            messagebox.showwarning("Warning", "Startup management is only available on Windows!")
            return
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Microsoft\Windows\CurrentVersion\Run", 
                               0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, "CmdManagerAdvanced")
            winreg.CloseKey(key)
            
            messagebox.showinfo("Success", "Application removed from startup!")
            self.logger.info("Removed from Windows startup")
            
        except FileNotFoundError:
            messagebox.showinfo("Info", "Application was not in startup!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove from startup: {e}")
            self.logger.error(f"Startup removal failed: {e}")

    def show_about(self):
        """Hiển thị thông tin về ứng dụng"""
        about_text = """
Advanced CMD/Script Manager & Cloudflare DNS Updater v2.0

Features:
• Multi-script management (Python, JavaScript, Batch, Shell)
• Real-time script output monitoring
• Interactive command sending to scripts
• Automatic Cloudflare DNS updates
• Cross-platform compatibility
• Enhanced error handling and logging
• Configuration import/export
• Auto-save functionality

Developed for advanced script management and DNS automation.
        """
        messagebox.showinfo("About", about_text)

    def on_closing(self):
        """Xử lý khi đóng ứng dụng"""
        if messagebox.askokcancel("Quit", "Do you want to quit? All running scripts will be stopped."):
            # Stop all scripts
            self.stop_all_scripts()
            
            # Save configuration
            self.save_config()
            
            # Close application
            self.root.destroy()


class ScriptConfigDialog:
    """Dialog để cấu hình script"""
    def __init__(self, parent, script_path, existing_config=None):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Script Configuration")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (300 // 2)
        self.dialog.geometry(f"400x300+{x}+{y}")
        
        self.create_widgets(script_path, existing_config)
        
        # Wait for dialog
        self.dialog.wait_window()

    def create_widgets(self, script_path, existing_config):
        """Tạo widgets cho dialog"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Script name
        ttk.Label(main_frame, text="Script Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_entry = ttk.Entry(main_frame, width=40)
        self.name_entry.grid(row=0, column=1, pady=5, padx=(5, 0))
        
        # Auto run
        self.auto_run_var = tk.BooleanVar()
        ttk.Checkbutton(main_frame, text="Auto Run on Startup", 
                       variable=self.auto_run_var).grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
        
        # Working directory
        ttk.Label(main_frame, text="Working Directory:").grid(row=2, column=0, sticky="w", pady=5)
        self.workdir_entry = ttk.Entry(main_frame, width=40)
        self.workdir_entry.grid(row=2, column=1, pady=5, padx=(5, 0))
        
        # Description
        ttk.Label(main_frame, text="Description:").grid(row=3, column=0, sticky="nw", pady=5)
        self.desc_text = tk.Text(main_frame, height=4, width=30)
        self.desc_text.grid(row=3, column=1, pady=5, padx=(5, 0))
        
        # Fill existing values
        if existing_config:
            self.name_entry.insert(0, existing_config.get('name', ''))
            self.auto_run_var.set(existing_config.get('auto_run', False))
            self.workdir_entry.insert(0, existing_config.get('working_dir', ''))
            self.desc_text.insert(1.0, existing_config.get('description', ''))
        else:
            # Default values for new script
            default_name = os.path.splitext(os.path.basename(script_path))[0]
            self.name_entry.insert(0, default_name)
            self.workdir_entry.insert(0, os.path.dirname(script_path))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side="left", padx=5)
        
        # Focus on name entry
        self.name_entry.focus_set()
        self.name_entry.select_range(0, tk.END)

    def save(self):
        """Lưu cấu hình"""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a script name!")
            return
        
        self.result = {
            'name': name,
            'auto_run': self.auto_run_var.get(),
            'working_dir': self.workdir_entry.get().strip(),
            'description': self.desc_text.get(1.0, tk.END).strip()
        }
        
        self.dialog.destroy()

    def cancel(self):
        """Hủy dialog"""
        self.dialog.destroy()


class CloudflareConfigDialog:
    """Dialog để cấu hình Cloudflare"""
    def __init__(self, parent):
        self.result = None
        self.domains = []
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Cloudflare Configuration")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
        
        self.create_widgets()
        
        # Wait for dialog
        self.dialog.wait_window()

    def create_widgets(self):
        """Tạo widgets cho dialog"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # API Token
        ttk.Label(main_frame, text="API Token:").grid(row=0, column=0, sticky="w", pady=5)
        self.api_token_entry = ttk.Entry(main_frame, width=50, show="*")
        self.api_token_entry.grid(row=0, column=1, pady=5, padx=(5, 0))
        
        # Check interval
        ttk.Label(main_frame, text="Check Interval (minutes):").grid(row=1, column=0, sticky="w", pady=5)
        self.interval_entry = ttk.Entry(main_frame, width=20)
        self.interval_entry.grid(row=1, column=1, sticky="w", pady=5, padx=(5, 0))
        self.interval_entry.insert(0, "5")
        
        # Domains section
        domains_frame = ttk.LabelFrame(main_frame, text="DNS Records")
        domains_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        domains_frame.grid_columnconfigure(0, weight=1)
        
        # Domain input
        input_frame = ttk.Frame(domains_frame)
        input_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(input_frame, text="Domain:").grid(row=0, column=0, sticky="w")
        self.domain_entry = ttk.Entry(input_frame, width=25)
        self.domain_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(input_frame, text="Zone ID:").grid(row=0, column=2, sticky="w", padx=(10, 0))
        self.zone_id_entry = ttk.Entry(input_frame, width=20)
        self.zone_id_entry.grid(row=0, column=3, padx=5)
        
        ttk.Label(input_frame, text="Record ID:").grid(row=1, column=0, sticky="w", pady=(5, 0))
        self.record_id_entry = ttk.Entry(input_frame, width=25)
        self.record_id_entry.grid(row=1, column=1, padx=5, pady=(5, 0))
        
        ttk.Label(input_frame, text="Record Name:").grid(row=1, column=2, sticky="w", padx=(10, 0), pady=(5, 0))
        self.record_name_entry = ttk.Entry(input_frame, width=20)
        self.record_name_entry.grid(row=1, column=3, padx=5, pady=(5, 0))
        
        ttk.Button(input_frame, text="Add Domain", command=self.add_domain).grid(row=2, column=0, columnspan=4, pady=10)
        
        # Domains list
        self.domains_listbox = tk.Listbox(domains_frame, height=8)
        self.domains_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        ttk.Button(domains_frame, text="Remove Selected", command=self.remove_domain).pack(pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side="left", padx=5)
        
        # Focus
        self.api_token_entry.focus_set()

    def add_domain(self):
        """Thêm domain vào danh sách"""
        domain = self.domain_entry.get().strip()
        zone_id = self.zone_id_entry.get().strip()
        record_id = self.record_id_entry.get().strip()
        record_name = self.record_name_entry.get().strip()
        
        if not all([domain, zone_id, record_id, record_name]):
            messagebox.showerror("Error", "Please fill all domain fields!")
            return
        
        domain_info = {
            'domain': domain,
            'zone_id': zone_id,
            'record_id': record_id,
            'record_name': record_name,
            'ttl': 1,
            'proxied': True
        }
        
        self.domains.append(domain_info)
        self.domains_listbox.insert(tk.END, f"{record_name} ({domain})")
        
        # Clear entries
        self.domain_entry.delete(0, tk.END)
        self.zone_id_entry.delete(0, tk.END)
        self.record_id_entry.delete(0, tk.END)
        self.record_name_entry.delete(0, tk.END)
        
        self.domain_entry.focus_set()

    def remove_domain(self):
        """Xóa domain được chọn"""
        selection = self.domains_listbox.curselection()
        if selection:
            index = selection[0]
            self.domains.pop(index)
            self.domains_listbox.delete(index)

    def save(self):
        """Lưu cấu hình Cloudflare"""
        api_token = self.api_token_entry.get().strip()
        
        try:
            interval = float(self.interval_entry.get()) * 60  # Convert to seconds
        except ValueError:
            messagebox.showerror("Error", "Check interval must be a number!")
            return
        
        if not api_token:
            messagebox.showerror("Error", "Please enter API Token!")
            return
        
        if not self.domains:
            messagebox.showerror("Error", "Please add at least one domain!")
            return
        
        self.result = {
            'api_token': api_token,
            'check_interval': interval,
            'domains': self.domains.copy()
        }
        
        self.dialog.destroy()

    def cancel(self):
        """Hủy dialog"""
        self.dialog.destroy()


def main():
    """Hàm chính"""
    # Create root window
    root = tk.Tk()
    
    # Set icon if available
    try:
        # You can add an icon file here
        # root.iconbitmap('icon.ico')
        pass
    except:
        pass
    
    # Create application
    app = CmdManagerApp(root)
    
    # Add to startup on Windows (if desired)
    if platform.system() == "Windows" and winreg and len(sys.argv) > 1 and sys.argv[1] == "--add-startup":
        app.add_to_startup()
    
    # Start GUI
    root.mainloop()


if __name__ == "__main__":
    main()