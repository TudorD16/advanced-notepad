import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import stat
import time
import hashlib
from pathlib import Path
import mimetypes
import platform

class FileArcheologist:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("File Archeologist v1.0")
        self.root.geometry("800x600")
        self.root.configure(bg='#c0c0c0')
        
        # Windows 95 style configuration
        self.setup_styles()
        self.create_widgets()
        self.current_path = ""
        
    def setup_styles(self):
        """Configure Windows 95 retro styling"""
        style = ttk.Style()
        
        # Configure colors to match Windows 95
        self.colors = {
            'bg': '#c0c0c0',
            'button_bg': '#c0c0c0',
            'button_active': '#dfdfdf',
            'text_bg': 'white',
            'highlight': '#0078d4',
            'border': '#808080',
            'dark_border': '#404040'
        }
        
    def create_widgets(self):
        """Create the main interface"""
        # Menu bar
        menubar = tk.Menu(self.root, bg=self.colors['bg'])
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg'])
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open File...", command=self.select_file)
        file_menu.add_command(label="Open Folder...", command=self.select_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Toolbar
        toolbar = tk.Frame(self.root, bg=self.colors['bg'], relief='raised', bd=1)
        toolbar.pack(fill='x', padx=2, pady=2)
        
        tk.Button(toolbar, text="📁 Open File", command=self.select_file,
                 bg=self.colors['button_bg'], relief='raised', bd=2,
                 font=('MS Sans Serif', 8)).pack(side='left', padx=2)
        
        tk.Button(toolbar, text="📂 Open Folder", command=self.select_folder,
                 bg=self.colors['button_bg'], relief='raised', bd=2,
                 font=('MS Sans Serif', 8)).pack(side='left', padx=2)
        
        tk.Button(toolbar, text="🔍 Analyze", command=self.analyze_current,
                 bg=self.colors['button_bg'], relief='raised', bd=2,
                 font=('MS Sans Serif', 8)).pack(side='left', padx=2)
        
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Path display
        path_frame = tk.Frame(main_frame, bg=self.colors['bg'], relief='sunken', bd=2)
        path_frame.pack(fill='x', pady=(0, 5))
        
        tk.Label(path_frame, text="Path:", bg=self.colors['bg'], 
                font=('MS Sans Serif', 8, 'bold')).pack(side='left', padx=5)
        
        self.path_var = tk.StringVar()
        self.path_label = tk.Label(path_frame, textvariable=self.path_var,
                                  bg=self.colors['text_bg'], relief='sunken', bd=1,
                                  font=('MS Sans Serif', 8), anchor='w')
        self.path_label.pack(fill='x', padx=5, pady=2)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # General tab
        self.general_tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(self.general_tab, text="General")
        
        # Details tab
        self.details_tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(self.details_tab, text="Details")
        
        # Security tab
        self.security_tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(self.security_tab, text="Security")
        
        # Hash tab
        self.hash_tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(self.hash_tab, text="Hash")
        
        self.create_general_tab()
        self.create_details_tab()
        self.create_security_tab()
        self.create_hash_tab()
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bg=self.colors['bg'],
                                  relief='sunken', bd=1, anchor='w',
                                  font=('MS Sans Serif', 8))
        self.status_bar.pack(fill='x', side='bottom')
        
    def create_general_tab(self):
        """Create general information tab"""
        # Create scrollable frame
        canvas = tk.Canvas(self.general_tab, bg=self.colors['bg'])
        scrollbar = tk.Scrollbar(self.general_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # General info fields
        self.general_info = {}
        fields = [
            "Name", "Type", "Location", "Size", "Size on disk",
            "Created", "Modified", "Accessed", "Attributes"
        ]
        
        for i, field in enumerate(fields):
            frame = tk.Frame(scrollable_frame, bg=self.colors['bg'])
            frame.pack(fill='x', padx=10, pady=2)
            
            tk.Label(frame, text=f"{field}:", bg=self.colors['bg'],
                    font=('MS Sans Serif', 8, 'bold'), width=15, anchor='w').pack(side='left')
            
            var = tk.StringVar()
            self.general_info[field] = var
            tk.Label(frame, textvariable=var, bg=self.colors['text_bg'],
                    relief='sunken', bd=1, font=('MS Sans Serif', 8),
                    anchor='w').pack(fill='x', padx=(5, 0))
        
    def create_details_tab(self):
        """Create details tab with file content preview"""
        # Text widget for file content preview
        text_frame = tk.Frame(self.details_tab, bg=self.colors['bg'])
        text_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        tk.Label(text_frame, text="File Content Preview:", bg=self.colors['bg'],
                font=('MS Sans Serif', 8, 'bold')).pack(anchor='w')
        
        # Create text widget with scrollbars
        text_container = tk.Frame(text_frame, bg=self.colors['bg'], relief='sunken', bd=2)
        text_container.pack(fill='both', expand=True, pady=(5, 0))
        
        self.content_text = tk.Text(text_container, wrap='word', bg=self.colors['text_bg'],
                                   font=('Courier New', 9), state='disabled')
        
        v_scrollbar = tk.Scrollbar(text_container, orient='vertical', command=self.content_text.yview)
        h_scrollbar = tk.Scrollbar(text_container, orient='horizontal', command=self.content_text.xview)
        
        self.content_text.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.content_text.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        text_container.grid_rowconfigure(0, weight=1)
        text_container.grid_columnconfigure(0, weight=1)
        
    def create_security_tab(self):
        """Create security/permissions tab"""
        # Create scrollable frame
        canvas = tk.Canvas(self.security_tab, bg=self.colors['bg'])
        scrollbar = tk.Scrollbar(self.security_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Security info fields
        self.security_info = {}
        fields = [
            "Owner", "Group", "Permissions (Octal)", "Permissions (String)",
            "Read Permission", "Write Permission", "Execute Permission",
            "Hidden", "System", "Archive"
        ]
        
        for field in fields:
            frame = tk.Frame(scrollable_frame, bg=self.colors['bg'])
            frame.pack(fill='x', padx=10, pady=2)
            
            tk.Label(frame, text=f"{field}:", bg=self.colors['bg'],
                    font=('MS Sans Serif', 8, 'bold'), width=20, anchor='w').pack(side='left')
            
            var = tk.StringVar()
            self.security_info[field] = var
            tk.Label(frame, textvariable=var, bg=self.colors['text_bg'],
                    relief='sunken', bd=1, font=('MS Sans Serif', 8),
                    anchor='w').pack(fill='x', padx=(5, 0))
    
    def create_hash_tab(self):
        """Create hash calculation tab"""
        hash_frame = tk.Frame(self.hash_tab, bg=self.colors['bg'])
        hash_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Hash algorithms
        self.hash_info = {}
        algorithms = ["MD5", "SHA1", "SHA256", "SHA512"]
        
        for algo in algorithms:
            frame = tk.Frame(hash_frame, bg=self.colors['bg'])
            frame.pack(fill='x', pady=5)
            
            tk.Label(frame, text=f"{algo}:", bg=self.colors['bg'],
                    font=('MS Sans Serif', 8, 'bold'), width=10, anchor='w').pack(side='left')
            
            var = tk.StringVar()
            self.hash_info[algo] = var
            
            entry = tk.Entry(frame, textvariable=var, bg=self.colors['text_bg'],
                           relief='sunken', bd=1, font=('Courier New', 8),
                           state='readonly')
            entry.pack(fill='x', padx=(5, 0))
        
        # Calculate button
        calc_frame = tk.Frame(hash_frame, bg=self.colors['bg'])
        calc_frame.pack(fill='x', pady=(10, 0))
        
        tk.Button(calc_frame, text="Calculate Hashes", command=self.calculate_hashes,
                 bg=self.colors['button_bg'], relief='raised', bd=2,
                 font=('MS Sans Serif', 8)).pack()
        
    def select_file(self):
        """Select a file to analyze"""
        file_path = filedialog.askopenfilename(
            title="Select File to Analyze",
            filetypes=[("All Files", "*.*")]
        )
        if file_path:
            self.current_path = file_path
            self.analyze_path(file_path)
            
    def select_folder(self):
        """Select a folder to analyze"""
        folder_path = filedialog.askdirectory(title="Select Folder to Analyze")
        if folder_path:
            self.current_path = folder_path
            self.analyze_path(folder_path)
            
    def analyze_current(self):
        """Re-analyze current path"""
        if self.current_path:
            self.analyze_path(self.current_path)
        else:
            messagebox.showwarning("No Path", "Please select a file or folder first.")
            
    def analyze_path(self, path):
        """Analyze the selected path"""
        try:
            self.status_bar.config(text="Analyzing...")
            self.root.update()
            
            self.path_var.set(path)
            
            # Get basic file info
            stat_info = os.stat(path)
            is_file = os.path.isfile(path)
            
            # General information
            self.general_info["Name"].set(os.path.basename(path))
            self.general_info["Type"].set("File" if is_file else "Folder")
            self.general_info["Location"].set(os.path.dirname(path))
            
            # Size information
            if is_file:
                size = stat_info.st_size
                self.general_info["Size"].set(self.format_size(size))
                
                # Calculate size on disk (approximate)
                block_size = 4096  # Common block size
                size_on_disk = ((size + block_size - 1) // block_size) * block_size
                self.general_info["Size on disk"].set(self.format_size(size_on_disk))
            else:
                folder_size = self.get_folder_size(path)
                self.general_info["Size"].set(self.format_size(folder_size))
                self.general_info["Size on disk"].set(self.format_size(folder_size))
            
            # Time information
            self.general_info["Created"].set(time.ctime(stat_info.st_ctime))
            self.general_info["Modified"].set(time.ctime(stat_info.st_mtime))
            self.general_info["Accessed"].set(time.ctime(stat_info.st_atime))
            
            # Attributes
            attributes = self.get_attributes(stat_info, path)
            self.general_info["Attributes"].set(attributes)
            
            # Security information
            self.update_security_info(stat_info, path)
            
            # File content preview
            if is_file:
                self.preview_file_content(path)
            else:
                self.preview_folder_content(path)
                
            self.status_bar.config(text=f"Analysis complete: {os.path.basename(path)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error analyzing path: {str(e)}")
            self.status_bar.config(text="Error occurred")
            
    def get_folder_size(self, path):
        """Calculate total size of folder"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(file_path)
                    except (OSError, IOError):
                        pass
        except (OSError, IOError):
            pass
        return total_size
        
    def format_size(self, size):
        """Format file size in human readable format"""
        for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
        
    def get_attributes(self, stat_info, path):
        """Get file attributes"""
        attrs = []
        
        # Unix-style permissions
        if stat.S_ISDIR(stat_info.st_mode):
            attrs.append("Directory")
        if stat.S_ISREG(stat_info.st_mode):
            attrs.append("Regular File")
        if stat.S_ISLNK(stat_info.st_mode):
            attrs.append("Symbolic Link")
            
        # Check if hidden (starts with dot on Unix-like systems)
        if os.path.basename(path).startswith('.'):
            attrs.append("Hidden")
            
        return ", ".join(attrs) if attrs else "Normal"
        
    def update_security_info(self, stat_info, path):
        """Update security/permissions information"""
        try:
            # Basic permissions
            mode = stat_info.st_mode
            
            # Octal permissions
            octal_perms = oct(stat.S_IMODE(mode))
            self.security_info["Permissions (Octal)"].set(octal_perms)
            
            # String permissions
            perms = stat.filemode(mode)
            self.security_info["Permissions (String)"].set(perms)
            
            # Individual permissions
            self.security_info["Read Permission"].set("Yes" if os.access(path, os.R_OK) else "No")
            self.security_info["Write Permission"].set("Yes" if os.access(path, os.W_OK) else "No")
            self.security_info["Execute Permission"].set("Yes" if os.access(path, os.X_OK) else "No")
            
            # Owner information (Unix-like systems)
            try:
                import pwd
                owner = pwd.getpwuid(stat_info.st_uid).pw_name
                self.security_info["Owner"].set(owner)
            except (ImportError, KeyError):
                self.security_info["Owner"].set(f"UID: {stat_info.st_uid}")
                
            try:
                import grp
                group = grp.getgrgid(stat_info.st_gid).gr_name
                self.security_info["Group"].set(group)
            except (ImportError, KeyError):
                self.security_info["Group"].set(f"GID: {stat_info.st_gid}")
                
            # Windows-specific attributes
            if platform.system() == "Windows":
                import win32api
                attrs = win32api.GetFileAttributes(path)
                self.security_info["Hidden"].set("Yes" if attrs & 2 else "No")
                self.security_info["System"].set("Yes" if attrs & 4 else "No")
                self.security_info["Archive"].set("Yes" if attrs & 32 else "No")
            else:
                self.security_info["Hidden"].set("N/A")
                self.security_info["System"].set("N/A")
                self.security_info["Archive"].set("N/A")
                
        except Exception as e:
            for key in self.security_info:
                self.security_info[key].set("Error")
                
    def preview_file_content(self, path):
        """Preview file content"""
        try:
            self.content_text.config(state='normal')
            self.content_text.delete(1.0, tk.END)
            
            # Try to determine if file is text-based
            mime_type, _ = mimetypes.guess_type(path)
            
            max_size = 1024 * 1024  # 1MB limit for preview
            file_size = os.path.getsize(path)
            
            if file_size > max_size:
                self.content_text.insert(tk.END, f"File too large for preview ({self.format_size(file_size)})\n")
                self.content_text.insert(tk.END, "Only text files under 1MB can be previewed.")
            elif mime_type and mime_type.startswith('text'):
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(8192)  # Read first 8KB
                    self.content_text.insert(tk.END, content)
                    if file_size > 8192:
                        self.content_text.insert(tk.END, "\n\n... (truncated)")
            else:
                # Binary file - show hex preview
                with open(path, 'rb') as f:
                    data = f.read(256)  # Read first 256 bytes
                    hex_output = self.format_hex_dump(data)
                    self.content_text.insert(tk.END, "Binary file - Hex dump (first 256 bytes):\n\n")
                    self.content_text.insert(tk.END, hex_output)
                    
            self.content_text.config(state='disabled')
            
        except Exception as e:
            self.content_text.config(state='normal')
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(tk.END, f"Error reading file: {str(e)}")
            self.content_text.config(state='disabled')
            
    def preview_folder_content(self, path):
        """Preview folder content"""
        try:
            self.content_text.config(state='normal')
            self.content_text.delete(1.0, tk.END)
            
            items = os.listdir(path)
            items.sort()
            
            self.content_text.insert(tk.END, f"Folder Contents ({len(items)} items):\n\n")
            
            for item in items[:100]:  # Limit to first 100 items
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    self.content_text.insert(tk.END, f"📁 {item}\n")
                else:
                    size = os.path.getsize(item_path)
                    self.content_text.insert(tk.END, f"📄 {item} ({self.format_size(size)})\n")
                    
            if len(items) > 100:
                self.content_text.insert(tk.END, f"\n... and {len(items) - 100} more items")
                
            self.content_text.config(state='disabled')
            
        except Exception as e:
            self.content_text.config(state='normal')
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(tk.END, f"Error reading folder: {str(e)}")
            self.content_text.config(state='disabled')
            
    def format_hex_dump(self, data):
        """Format binary data as hex dump"""
        lines = []
        for i in range(0, len(data), 16):
            chunk = data[i:i+16]
            hex_part = ' '.join(f'{b:02x}' for b in chunk)
            ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
            lines.append(f'{i:08x}: {hex_part:<48} {ascii_part}')
        return '\n'.join(lines)
        
    def calculate_hashes(self):
        """Calculate file hashes"""
        if not self.current_path or not os.path.isfile(self.current_path):
            messagebox.showwarning("No File", "Please select a file first.")
            return
            
        try:
            self.status_bar.config(text="Calculating hashes...")
            self.root.update()
            
            # Clear previous values
            for algo in self.hash_info:
                self.hash_info[algo].set("Calculating...")
            self.root.update()
            
            algorithms = {
                'MD5': hashlib.md5(),
                'SHA1': hashlib.sha1(),
                'SHA256': hashlib.sha256(),
                'SHA512': hashlib.sha512()
            }
            
            with open(self.current_path, 'rb') as f:
                while chunk := f.read(8192):
                    for hasher in algorithms.values():
                        hasher.update(chunk)
                        
            for algo, hasher in algorithms.items():
                self.hash_info[algo].set(hasher.hexdigest())
                self.root.update()
                
            self.status_bar.config(text="Hash calculation complete")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error calculating hashes: {str(e)}")
            for algo in self.hash_info:
                self.hash_info[algo].set("Error")
            self.status_bar.config(text="Hash calculation failed")
            
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = FileArcheologist()
    app.run()