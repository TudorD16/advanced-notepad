import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog, colorchooser
import csv
import xml.etree.ElementTree as ET
import xml.dom.minidom
import json
import os
import re
from datetime import datetime
import subprocess
import sys

class CSVViewer:
    def __init__(self, parent, data):
        self.window = tk.Toplevel(parent)
        self.window.title("CSV Table Viewer")
        self.window.geometry("800x500")
        self.window.configure(bg="#c0c0c0")
        
        # Create treeview for table display
        frame = tk.Frame(self.window, bg="#c0c0c0")
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tree = ttk.Treeview(frame)
        
        if data:
            # Set up columns
            self.tree["columns"] = [f"col{i}" for i in range(len(data[0]))]
            self.tree["show"] = "headings"
            
            # Configure column headings
            for i, header in enumerate(data[0]):
                self.tree.heading(f"col{i}", text=header)
                self.tree.column(f"col{i}", width=100)
            
            # Insert data
            for row in data[1:]:
                self.tree.insert("", "end", values=row)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        h_scroll = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")

class FindReplaceDialog:
    def __init__(self, parent, text_widget):
        self.parent = parent
        self.text_widget = text_widget
        self.window = tk.Toplevel(parent)
        self.window.title("Find & Replace")
        self.window.geometry("400x200")
        self.window.configure(bg="#c0c0c0")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Find section
        find_frame = tk.Frame(self.window, bg="#c0c0c0")
        find_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(find_frame, text="Find:", bg="#c0c0c0").pack(anchor=tk.W)
        self.find_var = tk.StringVar()
        self.find_entry = tk.Entry(find_frame, textvariable=self.find_var, width=40)
        self.find_entry.pack(fill=tk.X, pady=2)
        
        # Replace section
        replace_frame = tk.Frame(self.window, bg="#c0c0c0")
        replace_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(replace_frame, text="Replace with:", bg="#c0c0c0").pack(anchor=tk.W)
        self.replace_var = tk.StringVar()
        self.replace_entry = tk.Entry(replace_frame, textvariable=self.replace_var, width=40)
        self.replace_entry.pack(fill=tk.X, pady=2)
        
        # Options
        options_frame = tk.Frame(self.window, bg="#c0c0c0")
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.case_sensitive = tk.BooleanVar()
        self.whole_word = tk.BooleanVar()
        
        tk.Checkbutton(options_frame, text="Case sensitive", variable=self.case_sensitive, bg="#c0c0c0").pack(anchor=tk.W)
        tk.Checkbutton(options_frame, text="Whole word only", variable=self.whole_word, bg="#c0c0c0").pack(anchor=tk.W)
        
        # Buttons
        btn_frame = tk.Frame(self.window, bg="#c0c0c0")
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        btn_style = {"bg": "#c0c0c0", "relief": tk.RAISED, "bd": 2, "padx": 10}
        
        tk.Button(btn_frame, text="Find Next", command=self.find_next, **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Replace", command=self.replace_current, **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Replace All", command=self.replace_all, **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Close", command=self.window.destroy, **btn_style).pack(side=tk.RIGHT, padx=2)
        
        self.find_entry.focus()
        
    def find_next(self):
        search_text = self.find_var.get()
        if not search_text:
            return
            
        # Get current cursor position
        start_pos = self.text_widget.index(tk.INSERT)
        
        # Search for text
        pos = self.text_widget.search(search_text, start_pos, tk.END, 
                                     nocase=not self.case_sensitive.get())
        
        if pos:
            # Select found text
            end_pos = f"{pos}+{len(search_text)}c"
            self.text_widget.tag_remove(tk.SEL, "1.0", tk.END)
            self.text_widget.tag_add(tk.SEL, pos, end_pos)
            self.text_widget.mark_set(tk.INSERT, end_pos)
            self.text_widget.see(pos)
        else:
            messagebox.showinfo("Find", "Text not found")
            
    def replace_current(self):
        if self.text_widget.tag_ranges(tk.SEL):
            self.text_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_widget.insert(tk.INSERT, self.replace_var.get())
            
    def replace_all(self):
        search_text = self.find_var.get()
        replace_text = self.replace_var.get()
        
        if not search_text:
            return
            
        content = self.text_widget.get("1.0", tk.END)
        if not self.case_sensitive.get():
            count = content.lower().count(search_text.lower())
            content = re.sub(re.escape(search_text), replace_text, content, flags=re.IGNORECASE)
        else:
            count = content.count(search_text)
            content = content.replace(search_text, replace_text)
            
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", content)
        
        messagebox.showinfo("Replace All", f"Replaced {count} occurrences")

class Win95FileEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Multi-Format File Editor - Windows 95 Style")
        self.root.geometry("1000x700")
        
        # Windows 95 color scheme
        self.bg_color = "#c0c0c0"
        self.button_color = "#c0c0c0"
        self.text_bg = "#ffffff"
        self.menu_bg = "#c0c0c0"
        
        self.root.configure(bg=self.bg_color)
        
        self.current_file = None
        self.current_format = None
        self.file_modified = False
        self.recent_files = []
        self.bookmarks = []
        self.find_dialog = None
        
        # Editor settings
        self.font_family = "Courier New"
        self.font_size = 10
        self.tab_size = 4
        self.show_line_numbers = True
        self.word_wrap = True
        self.syntax_highlighting = True
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        # Menu bar
        self.setup_menu()
        
        # Toolbar
        self.setup_toolbar()
        
        # Main content area with panels
        self.setup_main_area()
        
        # Status bar
        self.setup_status_bar()
        
        # Bind events
        self.bind_events()
        
    def setup_menu(self):
        menubar = tk.Menu(self.root, bg=self.menu_bg, fg="black")
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.menu_bg, fg="black")
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        
        # Recent files submenu
        self.recent_menu = tk.Menu(file_menu, tearoff=0, bg=self.menu_bg, fg="black")
        file_menu.add_cascade(label="Recent Files", menu=self.recent_menu)
        
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_command(label="Save All", command=self.save_all_files)
        file_menu.add_separator()
        file_menu.add_command(label="Print...", command=self.print_file, accelerator="Ctrl+P")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_application)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg=self.menu_bg, fg="black")
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut_text, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy_text, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste_text, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        edit_menu.add_command(label="Find & Replace...", command=self.show_find_replace, accelerator="Ctrl+H")
        edit_menu.add_separator()
        edit_menu.add_command(label="Go to Line...", command=self.goto_line, accelerator="Ctrl+G")
        edit_menu.add_command(label="Toggle Bookmark", command=self.toggle_bookmark, accelerator="Ctrl+B")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg=self.menu_bg, fg="black")
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_checkbutton(label="Line Numbers", command=self.toggle_line_numbers)
        view_menu.add_checkbutton(label="Word Wrap", command=self.toggle_word_wrap)
        view_menu.add_checkbutton(label="Syntax Highlighting", command=self.toggle_syntax_highlighting)
        view_menu.add_separator()
        view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Reset Zoom", command=self.reset_zoom, accelerator="Ctrl+0")
        
        # Format menu
        format_menu = tk.Menu(menubar, tearoff=0, bg=self.menu_bg, fg="black")
        menubar.add_cascade(label="Format", menu=format_menu)
        format_menu.add_command(label="Format JSON", command=self.format_json)
        format_menu.add_command(label="Format XML", command=self.format_xml)
        format_menu.add_command(label="Minify JSON", command=self.minify_json)
        format_menu.add_command(label="Escape JSON", command=self.escape_json)
        format_menu.add_separator()
        format_menu.add_command(label="Sort Lines", command=self.sort_lines)
        format_menu.add_command(label="Remove Duplicate Lines", command=self.remove_duplicates)
        format_menu.add_command(label="Convert to Uppercase", command=self.to_uppercase)
        format_menu.add_command(label="Convert to Lowercase", command=self.to_lowercase)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0, bg=self.menu_bg, fg="black")
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Validate JSON", command=self.validate_json)
        tools_menu.add_command(label="Validate XML", command=self.validate_xml)
        tools_menu.add_command(label="Validate CSV", command=self.validate_csv)
        tools_menu.add_separator()
        tools_menu.add_command(label="View CSV as Table", command=self.view_csv_table)
        tools_menu.add_command(label="JSON to CSV", command=self.json_to_csv)
        tools_menu.add_command(label="CSV to JSON", command=self.csv_to_json)
        tools_menu.add_separator()
        tools_menu.add_command(label="Count Words/Lines", command=self.count_stats)
        tools_menu.add_command(label="Encode/Decode", command=self.show_encode_decode)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0, bg=self.menu_bg, fg="black")
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Font...", command=self.change_font)
        settings_menu.add_command(label="Colors...", command=self.change_colors)
        settings_menu.add_command(label="Tab Size...", command=self.change_tab_size)
        settings_menu.add_command(label="Preferences...", command=self.show_preferences)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.menu_bg, fg="black")
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="About...", command=self.show_about)
        
    def setup_toolbar(self):
        # Main toolbar
        self.toolbar = tk.Frame(self.root, bg=self.bg_color, relief=tk.RAISED, bd=1)
        self.toolbar.pack(fill=tk.X, padx=2, pady=2)
        
        btn_style = {"bg": self.button_color, "fg": "black", "relief": tk.RAISED, 
                    "bd": 2, "font": ("MS Sans Serif", 8), "padx": 6, "pady": 2}
        
        # File operations
        tk.Button(self.toolbar, text="New", command=self.new_file, **btn_style).pack(side=tk.LEFT, padx=1)
        tk.Button(self.toolbar, text="Open", command=self.open_file, **btn_style).pack(side=tk.LEFT, padx=1)
        tk.Button(self.toolbar, text="Save", command=self.save_file, **btn_style).pack(side=tk.LEFT, padx=1)
        
        self.add_separator()
        
        # Edit operations
        tk.Button(self.toolbar, text="Cut", command=self.cut_text, **btn_style).pack(side=tk.LEFT, padx=1)
        tk.Button(self.toolbar, text="Copy", command=self.copy_text, **btn_style).pack(side=tk.LEFT, padx=1)
        tk.Button(self.toolbar, text="Paste", command=self.paste_text, **btn_style).pack(side=tk.LEFT, padx=1)
        
        self.add_separator()
        
        # Format operations
        tk.Button(self.toolbar, text="Format", command=self.format_current, **btn_style).pack(side=tk.LEFT, padx=1)
        tk.Button(self.toolbar, text="Validate", command=self.validate_current, **btn_style).pack(side=tk.LEFT, padx=1)
        
        self.add_separator()
        
        # View operations
        tk.Button(self.toolbar, text="Find", command=self.show_find_replace, **btn_style).pack(side=tk.LEFT, padx=1)
        tk.Button(self.toolbar, text="Zoom+", command=self.zoom_in, **btn_style).pack(side=tk.LEFT, padx=1)
        tk.Button(self.toolbar, text="Zoom-", command=self.zoom_out, **btn_style).pack(side=tk.LEFT, padx=1)
        
        # Format indicator
        self.format_label = tk.Label(self.toolbar, text="Format: Unknown", bg=self.bg_color, 
                                   font=("MS Sans Serif", 8), relief=tk.SUNKEN, bd=1)
        self.format_label.pack(side=tk.RIGHT, padx=5)
        
    def add_separator(self):
        tk.Frame(self.toolbar, width=2, bg="#808080", relief=tk.SUNKEN, bd=1).pack(
            side=tk.LEFT, fill=tk.Y, padx=3, pady=2)
        
    def setup_main_area(self):
        # Main paned window
        self.main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=self.bg_color, 
                                        relief=tk.SUNKEN, bd=2, sashwidth=5)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        # Left panel for file browser and bookmarks
        self.left_panel = tk.Frame(self.main_paned, bg=self.bg_color, width=200)
        self.main_paned.add(self.left_panel, minsize=150)
        
        # Notebook for left panel tabs
        self.left_notebook = ttk.Notebook(self.left_panel)
        self.left_notebook.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # File browser tab
        self.setup_file_browser()
        
        # Bookmarks tab
        self.setup_bookmarks_panel()
        
        # Right panel for editor
        self.editor_frame = tk.Frame(self.main_paned, bg=self.bg_color)
        self.main_paned.add(self.editor_frame, minsize=400)
        
        # Editor with line numbers
        self.setup_editor()
        
    def setup_file_browser(self):
        browser_frame = tk.Frame(self.left_notebook, bg=self.bg_color)
        self.left_notebook.add(browser_frame, text="Files")
        
        # Directory navigation
        nav_frame = tk.Frame(browser_frame, bg=self.bg_color)
        nav_frame.pack(fill=tk.X, padx=2, pady=2)
        
        tk.Label(nav_frame, text="Directory:", bg=self.bg_color, font=("MS Sans Serif", 8)).pack(anchor=tk.W)
        
        self.current_dir = tk.StringVar(value=os.getcwd())
        dir_frame = tk.Frame(nav_frame, bg=self.bg_color)
        dir_frame.pack(fill=tk.X, pady=2)
        
        self.dir_entry = tk.Entry(dir_frame, textvariable=self.current_dir, font=("MS Sans Serif", 8))
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(dir_frame, text="...", command=self.browse_directory, 
                 bg=self.button_color, relief=tk.RAISED, bd=1, padx=5).pack(side=tk.RIGHT)
        
        # File listbox
        list_frame = tk.Frame(browser_frame, bg=self.bg_color, relief=tk.SUNKEN, bd=1)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        self.file_listbox = tk.Listbox(list_frame, bg="white", font=("MS Sans Serif", 8))
        file_scroll = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=file_scroll.set)
        
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        file_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox.bind('<Double-Button-1>', self.open_from_browser)
        
        self.refresh_file_browser()
        
    def setup_bookmarks_panel(self):
        bookmarks_frame = tk.Frame(self.left_notebook, bg=self.bg_color)
        self.left_notebook.add(bookmarks_frame, text="Bookmarks")
        
        # Bookmarks listbox
        self.bookmarks_listbox = tk.Listbox(bookmarks_frame, bg="white", font=("MS Sans Serif", 8))
        self.bookmarks_listbox.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Bookmarks buttons
        btn_frame = tk.Frame(bookmarks_frame, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, padx=2, pady=2)
        
        btn_style = {"bg": self.button_color, "relief": tk.RAISED, "bd": 1, "font": ("MS Sans Serif", 8)}
        
        tk.Button(btn_frame, text="Go", command=self.goto_bookmark, **btn_style).pack(side=tk.LEFT, padx=1)
        tk.Button(btn_frame, text="Delete", command=self.delete_bookmark, **btn_style).pack(side=tk.LEFT, padx=1)
        
    def setup_editor(self):
        editor_container = tk.Frame(self.editor_frame, bg=self.bg_color, relief=tk.SUNKEN, bd=2)
        editor_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Line numbers and text editor frame
        text_frame = tk.Frame(editor_container, bg=self.bg_color)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Line numbers
        self.line_numbers = tk.Text(text_frame, width=4, padx=3, takefocus=0,
                                   border=0, state='disabled', wrap='none',
                                   bg="#f0f0f0", fg="#666666", font=(self.font_family, self.font_size))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Main text editor
        self.text_editor = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD if self.word_wrap else tk.NONE,
            bg=self.text_bg,
            fg="black",
            font=(self.font_family, self.font_size),
            relief=tk.FLAT,
            insertbackground="black",
            selectbackground="#0078d4",
            selectforeground="white",
            undo=True,
            maxundo=50
        )
        self.text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind events for line numbers
        self.text_editor.bind('<Key>', self.on_text_change)
        self.text_editor.bind('<Button-1>', self.update_line_numbers)
        self.text_editor.bind('<MouseWheel>', self.on_mousewheel)
        
        # Configure syntax highlighting tags
        self.setup_syntax_highlighting()
        
    def setup_syntax_highlighting(self):
        # JSON syntax highlighting
        self.text_editor.tag_configure("json_key", foreground="#0000FF")
        self.text_editor.tag_configure("json_string", foreground="#008000")
        self.text_editor.tag_configure("json_number", foreground="#FF0000")
        self.text_editor.tag_configure("json_keyword", foreground="#800080")
        
        # XML syntax highlighting
        self.text_editor.tag_configure("xml_tag", foreground="#0000FF")
        self.text_editor.tag_configure("xml_attribute", foreground="#FF0000")
        self.text_editor.tag_configure("xml_value", foreground="#008000")
        
    def setup_status_bar(self):
        status_frame = tk.Frame(self.root, bg=self.bg_color, relief=tk.RAISED, bd=1)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_bar = tk.Label(status_frame, text="Ready", relief=tk.SUNKEN, bd=1,
                                  bg=self.bg_color, fg="black", font=("MS Sans Serif", 8), anchor=tk.W)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Line/Column indicator
        self.line_col_label = tk.Label(status_frame, text="Ln 1, Col 1", relief=tk.SUNKEN, bd=1,
                                      bg=self.bg_color, fg="black", font=("MS Sans Serif", 8))
        self.line_col_label.pack(side=tk.RIGHT, padx=2)
        
        # File size indicator
        self.file_size_label = tk.Label(status_frame, text="0 bytes", relief=tk.SUNKEN, bd=1,
                                       bg=self.bg_color, fg="black", font=("MS Sans Serif", 8))
        self.file_size_label.pack(side=tk.RIGHT, padx=2)
        
    def bind_events(self):
        # Keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-Shift-S>', lambda e: self.save_as_file())
        self.root.bind('<Control-p>', lambda e: self.print_file())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-h>', lambda e: self.show_find_replace())
        self.root.bind('<Control-g>', lambda e: self.goto_line())
        self.root.bind('<Control-b>', lambda e: self.toggle_bookmark())
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.reset_zoom())
        
        # Text editor events
        self.text_editor.bind('<KeyRelease>', self.update_cursor_position)
        self.text_editor.bind('<ButtonRelease-1>', self.update_cursor_position)
        
        # Window events
        self.root.protocol("WM_DELETE_WINDOW", self.exit_application)
        
    # File operations
    def new_file(self):
        if self.file_modified and not self.ask_save_changes():
            return
        self.text_editor.delete(1.0, tk.END)
        self.current_file = None
        self.current_format = None
        self.file_modified = False
        self.update_title()
        self.update_format_display()
        self.status_bar.config(text="New file created")
        self.update_line_numbers()
        
    def open_file(self):
        if self.file_modified and not self.ask_save_changes():
            return
            
        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[
                ("All Supported", "*.csv;*.xml;*.json;*.md;*.txt"),
                ("CSV files", "*.csv"),
                ("XML files", "*.xml"),
                ("JSON files", "*.json"),
                ("Markdown files", "*.md"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.load_file(file_path)
            
    def load_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.text_editor.delete(1.0, tk.END)
                self.text_editor.insert(1.0, content)
                
            self.current_file = file_path
            self.current_format = self.detect_format(file_path)
            self.file_modified = False
            self.add_to_recent_files(file_path)
            self.update_title()
            self.update_format_display()
            self.update_line_numbers()
            self.apply_syntax_highlighting()
            self.status_bar.config(text=f"Opened: {os.path.basename(file_path)} ({self.current_format})")
            self.update_file_size()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\n{str(e)}")
            
    def save_file(self):
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_as_file()
            
    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(
            title="Save File As",
            filetypes=[
                ("CSV files", "*.csv"),
                ("XML files", "*.xml"),
                ("JSON files", "*.json"),
                ("Markdown files", "*.md"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.save_to_file(file_path)
            self.current_file = file_path
            self.current_format = self.detect_format(file_path)
            self.update_title()
            self.update_format_display()
            self.add_to_recent_files(file_path)
            
    def save_to_file(self, file_path):
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                content = self.text_editor.get(1.0, tk.END).rstrip('\n')
                file.write(content)
            self.file_modified = False
            self.update_title()
            self.status_bar.config(text=f"Saved: {os.path.basename(file_path)}")
            self.update_file_size()
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file:\n{str(e)}")
            
    def save_all_files(self):
        if self.current_file and self.file_modified:
            self.save_file()
            
    def print_file(self):
        try:
            if sys.platform.startswith('win'):
                os.startfile(self.current_file, "print")
            else:
                messagebox.showinfo("Print", "Print functionality not available on this platform")
        except Exception as e:
            messagebox.showerror("Print Error", f"Could not print file:\n{str(e)}")
            
    # Edit operations
    def undo(self):
        try:
            self.text_editor.edit_undo()
        except tk.TclError:
            pass
            
    def redo(self):
        try:
            self.text_editor.edit_redo()
        except tk.TclError:
            pass
            
    def cut_text(self):
        try:
            self.text_editor.event_generate("<<Cut>>")
        except tk.TclError:
            pass
            
    def copy_text(self):
        try:
            self.text_editor.event_generate("<<Copy>>")
        except tk.TclError:
            pass
            
    def paste_text(self):
        try:
            self.text_editor.event_generate("<<Paste>>")
        except tk.TclError:
            pass
            
    def select_all(self):
        self.text_editor.tag_add(tk.SEL, "1.0", tk.END)
        self.text_editor.mark_set(tk.INSERT, "1.0")
        self.text_editor.see(tk.INSERT)
        
    def show_find_replace(self):
        try:
            # Verificăm dacă dialogul există și fereastra nu a fost distrusă
            if self.find_dialog and self.find_dialog.window.winfo_exists():
                self.find_dialog.window.lift()
                self.find_dialog.window.focus_force()
            else:
                # Fereastra a fost închisă -> o recreăm
                self.find_dialog = FindReplaceDialog(self.root, self.text_editor)
        except AttributeError:
            # Dacă self.find_dialog nu e definit încă
            self.find_dialog = FindReplaceDialog(self.root, self.text_editor)
    '''
    def show_find_replace(self):
        if self.find_dialog:
            self.find_dialog.window.lift()
        else:
            self.find_dialog = FindReplaceDialog(self.root, self.text_editor)
    '''
            
    def goto_line(self):
        line_num = simpledialog.askinteger("Go to Line", "Enter line number:", 
                                          minvalue=1, maxvalue=int(self.text_editor.index('end').split('.')[0]))
        if line_num:
            self.text_editor.mark_set(tk.INSERT, f"{line_num}.0")
            self.text_editor.see(tk.INSERT)
            self.update_cursor_position()
            
    def toggle_bookmark(self):
        current_line = self.text_editor.index(tk.INSERT).split('.')[0]
        bookmark_text = f"Line {current_line}"
        
        if bookmark_text not in self.bookmarks:
            self.bookmarks.append(bookmark_text)
            self.bookmarks_listbox.insert(tk.END, bookmark_text)
            self.status_bar.config(text=f"Bookmark added at line {current_line}")
        else:
            self.bookmarks.remove(bookmark_text)
            for i in range(self.bookmarks_listbox.size()):
                if self.bookmarks_listbox.get(i) == bookmark_text:
                    self.bookmarks_listbox.delete(i)
                    break
            self.status_bar.config(text=f"Bookmark removed from line {current_line}")
            
    # View operations
    def toggle_line_numbers(self):
        self.show_line_numbers = not self.show_line_numbers
        if self.show_line_numbers:
            self.line_numbers.pack(side=tk.LEFT, fill=tk.Y, before=self.text_editor)
        else:
            self.line_numbers.pack_forget()
            
    def toggle_word_wrap(self):
        self.word_wrap = not self.word_wrap
        self.text_editor.config(wrap=tk.WORD if self.word_wrap else tk.NONE)
        
    def toggle_syntax_highlighting(self):
        self.syntax_highlighting = not self.syntax_highlighting
        if self.syntax_highlighting:
            self.apply_syntax_highlighting()
        else:
            self.clear_syntax_highlighting()
            
    def zoom_in(self):
        self.font_size = min(self.font_size + 1, 24)
        self.update_font()
        
    def zoom_out(self):
        self.font_size = max(self.font_size - 1, 6)
        self.update_font()
        
    def reset_zoom(self):
        self.font_size = 10
        self.update_font()
        
    def update_font(self):
        font = (self.font_family, self.font_size)
        self.text_editor.config(font=font)
        self.line_numbers.config(font=font)
        self.update_line_numbers()
        
    # Format operations
    def format_current(self):
        if not self.current_format:
            self.current_format = self.guess_format_from_content()
            
        if self.current_format == 'JSON':
            self.format_json()
        elif self.current_format == 'XML':
            self.format_xml()
        elif self.current_format == 'CSV':
            self.validate_csv()
        else:
            messagebox.showinfo("Format", "No formatting available for this file type")
            
    def validate_current(self):
        if not self.current_format:
            self.current_format = self.guess_format_from_content()
            
        if self.current_format == 'JSON':
            self.validate_json()
        elif self.current_format == 'XML':
            self.validate_xml()
        elif self.current_format == 'CSV':
            self.validate_csv()
        else:
            messagebox.showinfo("Validate", "No validation available for this file type")
            
    def format_json(self):
        try:
            content = self.text_editor.get(1.0, tk.END).strip()
            if content:
                parsed = json.loads(content)
                formatted = json.dumps(parsed, indent=2, ensure_ascii=False, sort_keys=True)
                self.text_editor.delete(1.0, tk.END)
                self.text_editor.insert(1.0, formatted)
                self.status_bar.config(text="JSON formatted successfully")
                self.file_modified = True
                self.update_title()
                self.apply_syntax_highlighting()
        except json.JSONDecodeError as e:
            messagebox.showerror("JSON Error", f"Invalid JSON:\n{str(e)}")
            
    def minify_json(self):
        try:
            content = self.text_editor.get(1.0, tk.END).strip()
            if content:
                parsed = json.loads(content)
                minified = json.dumps(parsed, separators=(',', ':'), ensure_ascii=False)
                self.text_editor.delete(1.0, tk.END)
                self.text_editor.insert(1.0, minified)
                self.status_bar.config(text="JSON minified successfully")
                self.file_modified = True
                self.update_title()
        except json.JSONDecodeError as e:
            messagebox.showerror("JSON Error", f"Invalid JSON:\n{str(e)}")
            
    def escape_json(self):
        content = self.text_editor.get(1.0, tk.END).strip()
        if content:
            escaped = json.dumps(content)
            self.text_editor.delete(1.0, tk.END)
            self.text_editor.insert(1.0, escaped)
            self.status_bar.config(text="Text escaped for JSON")
            self.file_modified = True
            self.update_title()
            
    def format_xml(self):
        try:
            content = self.text_editor.get(1.0, tk.END).strip()
            if content:
                root = ET.fromstring(content)
                rough_string = ET.tostring(root, encoding='unicode')
                reparsed = xml.dom.minidom.parseString(rough_string)
                formatted = reparsed.toprettyxml(indent="  ")
                # Remove empty lines
                formatted = '\n'.join([line for line in formatted.split('\n') if line.strip()])
                self.text_editor.delete(1.0, tk.END)
                self.text_editor.insert(1.0, formatted)
                self.status_bar.config(text="XML formatted successfully")
                self.file_modified = True
                self.update_title()
                self.apply_syntax_highlighting()
        except ET.ParseError as e:
            messagebox.showerror("XML Error", f"Invalid XML:\n{str(e)}")
            
    def sort_lines(self):
        content = self.text_editor.get(1.0, tk.END)
        lines = content.split('\n')
        lines.sort()
        sorted_content = '\n'.join(lines)
        self.text_editor.delete(1.0, tk.END)
        self.text_editor.insert(1.0, sorted_content)
        self.status_bar.config(text="Lines sorted")
        self.file_modified = True
        self.update_title()
        
    def remove_duplicates(self):
        content = self.text_editor.get(1.0, tk.END)
        lines = content.split('\n')
        unique_lines = list(dict.fromkeys(lines))  # Preserve order
        unique_content = '\n'.join(unique_lines)
        self.text_editor.delete(1.0, tk.END)
        self.text_editor.insert(1.0, unique_content)
        removed_count = len(lines) - len(unique_lines)
        self.status_bar.config(text=f"Removed {removed_count} duplicate lines")
        self.file_modified = True
        self.update_title()
        
    def to_uppercase(self):
        if self.text_editor.tag_ranges(tk.SEL):
            selected_text = self.text_editor.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_editor.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_editor.insert(tk.INSERT, selected_text.upper())
        else:
            content = self.text_editor.get(1.0, tk.END)
            self.text_editor.delete(1.0, tk.END)
            self.text_editor.insert(1.0, content.upper())
        self.file_modified = True
        self.update_title()
        
    def to_lowercase(self):
        if self.text_editor.tag_ranges(tk.SEL):
            selected_text = self.text_editor.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_editor.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_editor.insert(tk.INSERT, selected_text.lower())
        else:
            content = self.text_editor.get(1.0, tk.END)
            self.text_editor.delete(1.0, tk.END)
            self.text_editor.insert(1.0, content.lower())
        self.file_modified = True
        self.update_title()
        
    # Validation operations
    def validate_json(self):
        try:
            content = self.text_editor.get(1.0, tk.END).strip()
            if content:
                json.loads(content)
                messagebox.showinfo("Validation", "JSON is valid!")
                self.status_bar.config(text="JSON validation successful")
            else:
                messagebox.showwarning("Validation", "No content to validate")
        except json.JSONDecodeError as e:
            messagebox.showerror("JSON Error", f"Invalid JSON:\n{str(e)}")
            
    def validate_xml(self):
        try:
            content = self.text_editor.get(1.0, tk.END).strip()
            if content:
                ET.fromstring(content)
                messagebox.showinfo("Validation", "XML is valid!")
                self.status_bar.config(text="XML validation successful")
            else:
                messagebox.showwarning("Validation", "No content to validate")
        except ET.ParseError as e:
            messagebox.showerror("XML Error", f"Invalid XML:\n{str(e)}")
            
    def validate_csv(self):
        try:
            content = self.text_editor.get(1.0, tk.END).strip()
            if content:
                lines = content.split('\n')
                reader = csv.reader(lines)
                rows = list(reader)
                
                if rows:
                    col_count = len(rows[0]) if rows[0] else 0
                    inconsistent_rows = []
                    
                    for i, row in enumerate(rows):
                        if len(row) != col_count:
                            inconsistent_rows.append(i + 1)
                    
                    if inconsistent_rows:
                        messagebox.showwarning(
                            "CSV Validation", 
                            f"CSV has inconsistent column counts.\n"
                            f"Expected {col_count} columns.\n"
                            f"Inconsistent rows: {', '.join(map(str, inconsistent_rows[:10]))}"
                            + ("..." if len(inconsistent_rows) > 10 else "")
                        )
                    else:
                        messagebox.showinfo(
                            "CSV Validation", 
                            f"CSV is valid!\n"
                            f"Rows: {len(rows)}\n"
                            f"Columns: {col_count}"
                        )
                    self.status_bar.config(text=f"CSV validation complete - {len(rows)} rows, {col_count} columns")
                else:
                    messagebox.showwarning("Validation", "CSV appears to be empty")
            else:
                messagebox.showwarning("Validation", "No content to validate")
        except Exception as e:
            messagebox.showerror("CSV Error", f"Error parsing CSV:\n{str(e)}")
            
    # Tools operations
    def view_csv_table(self):
        try:
            content = self.text_editor.get(1.0, tk.END).strip()
            if content and self.current_format == 'CSV':
                lines = content.split('\n')
                reader = csv.reader(lines)
                data = list(reader)
                if data:
                    CSVViewer(self.root, data)
                else:
                    messagebox.showwarning("CSV Viewer", "No data to display")
            else:
                messagebox.showwarning("CSV Viewer", "Current file is not a CSV or is empty")
        except Exception as e:
            messagebox.showerror("CSV Viewer Error", f"Error displaying CSV:\n{str(e)}")
            
    def json_to_csv(self):
        try:
            content = self.text_editor.get(1.0, tk.END).strip()
            if content:
                data = json.loads(content)
                if isinstance(data, list) and data and isinstance(data[0], dict):
                    # Convert list of dictionaries to CSV
                    fieldnames = data[0].keys()
                    csv_content = []
                    csv_content.append(','.join(fieldnames))
                    
                    for item in data:
                        row = []
                        for field in fieldnames:
                            value = str(item.get(field, ''))
                            if ',' in value or '"' in value or '\n' in value:
                                value = '"' + value.replace('"', '""') + '"'
                            row.append(value)
                        csv_content.append(','.join(row))
                    
                    result = '\n'.join(csv_content)
                    self.text_editor.delete(1.0, tk.END)
                    self.text_editor.insert(1.0, result)
                    self.current_format = 'CSV'
                    self.update_format_display()
                    self.status_bar.config(text="JSON converted to CSV")
                    self.file_modified = True
                    self.update_title()
                else:
                    messagebox.showerror("Conversion Error", "JSON must be an array of objects to convert to CSV")
        except json.JSONDecodeError as e:
            messagebox.showerror("JSON Error", f"Invalid JSON:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Conversion Error", f"Error converting JSON to CSV:\n{str(e)}")
            
    def csv_to_json(self):
        try:
            content = self.text_editor.get(1.0, tk.END).strip()
            if content:
                lines = content.split('\n')
                reader = csv.DictReader(lines)
                data = list(reader)
                json_content = json.dumps(data, indent=2, ensure_ascii=False)
                
                self.text_editor.delete(1.0, tk.END)
                self.text_editor.insert(1.0, json_content)
                self.current_format = 'JSON'
                self.update_format_display()
                self.apply_syntax_highlighting()
                self.status_bar.config(text="CSV converted to JSON")
                self.file_modified = True
                self.update_title()
        except Exception as e:
            messagebox.showerror("Conversion Error", f"Error converting CSV to JSON:\n{str(e)}")
            
    def count_stats(self):
        content = self.text_editor.get(1.0, tk.END)
        
        # Count statistics
        char_count = len(content) - 1  # Subtract 1 for the automatic newline
        char_count_no_spaces = len(content.replace(' ', '').replace('\t', '').replace('\n', ''))
        word_count = len(content.split())
        line_count = content.count('\n')
        paragraph_count = len([p for p in content.split('\n\n') if p.strip()])
        
        stats_message = f"""Document Statistics:
        
Characters (with spaces): {char_count}
Characters (without spaces): {char_count_no_spaces}
Words: {word_count}
Lines: {line_count}
Paragraphs: {paragraph_count}"""
        
        messagebox.showinfo("Document Statistics", stats_message)
        
    def show_encode_decode(self):
        # Simple encode/decode dialog
        encode_window = tk.Toplevel(self.root)
        encode_window.title("Encode/Decode")
        encode_window.geometry("500x400")
        encode_window.configure(bg="#c0c0c0")
        encode_window.transient(self.root)
        
        # Input text
        tk.Label(encode_window, text="Input:", bg="#c0c0c0").pack(anchor=tk.W, padx=10, pady=5)
        input_text = scrolledtext.ScrolledText(encode_window, height=8, bg="white")
        input_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Buttons
        btn_frame = tk.Frame(encode_window, bg="#c0c0c0")
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        def base64_encode():
            import base64
            text = input_text.get(1.0, tk.END).strip()
            encoded = base64.b64encode(text.encode()).decode()
            output_text.delete(1.0, tk.END)
            output_text.insert(1.0, encoded)
            
        def base64_decode():
            import base64
            try:
                text = input_text.get(1.0, tk.END).strip()
                decoded = base64.b64decode(text.encode()).decode()
                output_text.delete(1.0, tk.END)
                output_text.insert(1.0, decoded)
            except Exception as e:
                messagebox.showerror("Decode Error", f"Could not decode: {str(e)}")
                
        def url_encode():
            import urllib.parse
            text = input_text.get(1.0, tk.END).strip()
            encoded = urllib.parse.quote(text)
            output_text.delete(1.0, tk.END)
            output_text.insert(1.0, encoded)
            
        def url_decode():
            import urllib.parse
            text = input_text.get(1.0, tk.END).strip()
            decoded = urllib.parse.unquote(text)
            output_text.delete(1.0, tk.END)
            output_text.insert(1.0, decoded)
        
        btn_style = {"bg": "#c0c0c0", "relief": tk.RAISED, "bd": 2, "padx": 8}
        
        tk.Button(btn_frame, text="Base64 Encode", command=base64_encode, **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Base64 Decode", command=base64_decode, **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="URL Encode", command=url_encode, **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="URL Decode", command=url_decode, **btn_style).pack(side=tk.LEFT, padx=2)
        
        # Output text
        tk.Label(encode_window, text="Output:", bg="#c0c0c0").pack(anchor=tk.W, padx=10, pady=(10,5))
        output_text = scrolledtext.ScrolledText(encode_window, height=8, bg="white")
        output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
    # Settings operations
    def change_font(self):
        # Simple font dialog
        fonts = ["Courier New", "Arial", "Times New Roman", "Consolas", "Monaco", "Lucida Console"]
        
        font_window = tk.Toplevel(self.root)
        font_window.title("Font Settings")
        font_window.geometry("300x250")
        font_window.configure(bg="#c0c0c0")
        font_window.transient(self.root)
        
        tk.Label(font_window, text="Font Family:", bg="#c0c0c0").pack(anchor=tk.W, padx=10, pady=5)
        font_var = tk.StringVar(value=self.font_family)
        font_listbox = tk.Listbox(font_window, height=6)
        for font in fonts:
            font_listbox.insert(tk.END, font)
            if font == self.font_family:
                font_listbox.selection_set(font_listbox.size()-1)
        font_listbox.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(font_window, text="Font Size:", bg="#c0c0c0").pack(anchor=tk.W, padx=10, pady=5)
        size_var = tk.IntVar(value=self.font_size)
        size_spinbox = tk.Spinbox(font_window, from_=6, to=24, textvariable=size_var, width=10)
        size_spinbox.pack(anchor=tk.W, padx=10, pady=5)
        
        def apply_font():
            selection = font_listbox.curselection()
            if selection:
                self.font_family = font_listbox.get(selection[0])
                self.font_size = size_var.get()
                self.update_font()
                font_window.destroy()
        
        btn_frame = tk.Frame(font_window, bg="#c0c0c0")
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        btn_style = {"bg": "#c0c0c0", "relief": tk.RAISED, "bd": 2, "padx": 10}
        tk.Button(btn_frame, text="Apply", command=apply_font, **btn_style).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=font_window.destroy, **btn_style).pack(side=tk.LEFT, padx=5)
        
    def change_colors(self):
        color = colorchooser.askcolor(title="Choose Background Color")
        if color[1]:
            self.text_editor.config(bg=color[1])
            
    def change_tab_size(self):
        new_size = simpledialog.askinteger("Tab Size", "Enter tab size (2-8):", 
                                          minvalue=2, maxvalue=8, initialvalue=self.tab_size)
        if new_size:
            self.tab_size = new_size
            
    def show_preferences(self):
        pref_window = tk.Toplevel(self.root)
        pref_window.title("Preferences")
        pref_window.geometry("400x300")
        pref_window.configure(bg="#c0c0c0")
        pref_window.transient(self.root)
        
        # Create notebook for preference categories
        notebook = ttk.Notebook(pref_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # General tab
        general_frame = tk.Frame(notebook, bg="#c0c0c0")
        notebook.add(general_frame, text="General")
        
        line_num_var = tk.BooleanVar(value=self.show_line_numbers)
        word_wrap_var = tk.BooleanVar(value=self.word_wrap)
        syntax_var = tk.BooleanVar(value=self.syntax_highlighting)
        
        tk.Checkbutton(general_frame, text="Show line numbers", variable=line_num_var, bg="#c0c0c0").pack(anchor=tk.W, padx=10, pady=5)
        tk.Checkbutton(general_frame, text="Word wrap", variable=word_wrap_var, bg="#c0c0c0").pack(anchor=tk.W, padx=10, pady=5)
        tk.Checkbutton(general_frame, text="Syntax highlighting", variable=syntax_var, bg="#c0c0c0").pack(anchor=tk.W, padx=10, pady=5)
        
        # Editor tab
        editor_frame = tk.Frame(notebook, bg="#c0c0c0")
        notebook.add(editor_frame, text="Editor")
        
        tk.Label(editor_frame, text="Tab size:", bg="#c0c0c0").pack(anchor=tk.W, padx=10, pady=5)
        tab_var = tk.IntVar(value=self.tab_size)
        tk.Spinbox(editor_frame, from_=2, to=8, textvariable=tab_var, width=10).pack(anchor=tk.W, padx=10, pady=5)
        
        def apply_preferences():
            self.show_line_numbers = line_num_var.get()
            self.word_wrap = word_wrap_var.get()
            self.syntax_highlighting = syntax_var.get()
            self.tab_size = tab_var.get()
            
            self.toggle_line_numbers() if self.show_line_numbers != bool(self.line_numbers.winfo_viewable()) else None
            self.text_editor.config(wrap=tk.WORD if self.word_wrap else tk.NONE)
            
            if self.syntax_highlighting:
                self.apply_syntax_highlighting()
            else:
                self.clear_syntax_highlighting()
                
            pref_window.destroy()
        
        btn_frame = tk.Frame(pref_window, bg="#c0c0c0")
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        btn_style = {"bg": "#c0c0c0", "relief": tk.RAISED, "bd": 2, "padx": 10}
        tk.Button(btn_frame, text="Apply", command=apply_preferences, **btn_style).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=pref_window.destroy, **btn_style).pack(side=tk.LEFT, padx=5)
        
    # Help operations
    def show_shortcuts(self):
        shortcuts_text = """Keyboard Shortcuts:

File Operations:
Ctrl+N - New File
Ctrl+O - Open File
Ctrl+S - Save File
Ctrl+Shift+S - Save As
Ctrl+P - Print

Edit Operations:
Ctrl+Z - Undo
Ctrl+Y - Redo
Ctrl+X - Cut
Ctrl+C - Copy
Ctrl+V - Paste
Ctrl+A - Select All
Ctrl+H - Find & Replace
Ctrl+G - Go to Line
Ctrl+B - Toggle Bookmark

View Operations:
Ctrl++ - Zoom In
Ctrl+- - Zoom Out
Ctrl+0 - Reset Zoom"""
        
        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)
        
    def show_about(self):
        about_text = """Advanced Multi-Format File Editor
Windows 95 Style

Version 2.0
Built with Python and Tkinter

Supports: CSV, XML, JSON, Markdown, and Text files

Features:
• Syntax highlighting
• File validation and formatting
• Find and replace
• Format conversion
• Line numbers and bookmarks
• Encoding/decoding tools

Built on: {datetime.now().strftime('%Y-%m-%d')}"""
        
        messagebox.showinfo("About", about_text)
        
    # Utility methods
    def detect_format(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        format_map = {
            '.csv': 'CSV',
            '.json': 'JSON',
            '.xml': 'XML',
            '.md': 'Markdown',
            '.txt': 'Text'
        }
        return format_map.get(ext, 'Unknown')
        
    def guess_format_from_content(self):
        content = self.text_editor.get(1.0, tk.END).strip()
        if not content:
            return 'Unknown'
            
        # Try JSON
        try:
            json.loads(content)
            return 'JSON'
        except:
            pass
            
        # Try XML
        try:
            ET.fromstring(content)
            return 'XML'
        except:
            pass
            
        # Check for CSV patterns
        lines = content.split('\n')
        if len(lines) > 1:
            first_line_commas = lines[0].count(',')
            if first_line_commas > 0:
                # Check if other lines have similar comma count
                similar_count = 0
                for line in lines[1:5]:  # Check first few lines
                    if abs(line.count(',') - first_line_commas) <= 1:
                        similar_count += 1
                if similar_count >= len(lines[1:5]) * 0.7:  # 70% similarity
                    return 'CSV'
                    
        return 'Text'
        
    def update_title(self):
        title = "Advanced Multi-Format File Editor"
        if self.current_file:
            title += f" - {os.path.basename(self.current_file)}"
        if self.file_modified:
            title += " *"
        self.root.title(title)
        
    def update_format_display(self):
        format_text = f"Format: {self.current_format or 'Unknown'}"
        self.format_label.config(text=format_text)
        
    def update_line_numbers(self, event=None):
        if not self.show_line_numbers:
            return
            
        line_count = int(self.text_editor.index('end-1c').split('.')[0])
        line_numbers_content = '\n'.join(str(i) for i in range(1, line_count + 1))
        
        self.line_numbers.config(state='normal')
        self.line_numbers.delete(1.0, tk.END)
        self.line_numbers.insert(1.0, line_numbers_content)
        self.line_numbers.config(state='disabled')
        
    def update_cursor_position(self, event=None):
        cursor_pos = self.text_editor.index(tk.INSERT)
        line, col = cursor_pos.split('.')
        self.line_col_label.config(text=f"Ln {line}, Col {int(col) + 1}")
        
    def update_file_size(self):
        content = self.text_editor.get(1.0, tk.END)
        size = len(content.encode('utf-8')) - 1  # Subtract 1 for automatic newline
        if size < 1024:
            size_text = f"{size} bytes"
        elif size < 1024 * 1024:
            size_text = f"{size / 1024:.1f} KB"
        else:
            size_text = f"{size / (1024 * 1024):.1f} MB"
        self.file_size_label.config(text=size_text)
        
    def on_text_change(self, event=None):
        self.file_modified = True
        self.update_title()
        self.update_line_numbers()
        self.update_cursor_position()
        self.update_file_size()
        
        # Apply syntax highlighting after a short delay
        if self.syntax_highlighting:
            self.root.after(100, self.apply_syntax_highlighting)
            
    def on_mousewheel(self, event):
        # Sync line numbers scrolling with text editor
        if self.show_line_numbers:
            self.line_numbers.yview_scroll(int(-1 * (event.delta / 120)), "units")
            
    def apply_syntax_highlighting(self):
        if not self.syntax_highlighting or not self.current_format:
            return
            
        content = self.text_editor.get(1.0, tk.END)
        
        # Clear existing tags
        self.clear_syntax_highlighting()
        
        if self.current_format == 'JSON':
            self.highlight_json(content)
        elif self.current_format == 'XML':
            self.highlight_xml(content)
            
    def clear_syntax_highlighting(self):
        for tag in ['json_key', 'json_string', 'json_number', 'json_keyword',
                   'xml_tag', 'xml_attribute', 'xml_value']:
            self.text_editor.tag_remove(tag, 1.0, tk.END)
            
    def highlight_json(self, content):
        # Simple JSON syntax highlighting using regex
        import re
        
        # Highlight strings (keys and values)
        for match in re.finditer(r'"([^"\\]|\\.)*"', content):
            start_pos = f"1.0+{match.start()}c"
            end_pos = f"1.0+{match.end()}c"
            # Check if it's a key (followed by :)
            if match.end() < len(content) and content[match.end():].lstrip().startswith(':'):
                self.text_editor.tag_add('json_key', start_pos, end_pos)
            else:
                self.text_editor.tag_add('json_string', start_pos, end_pos)
                
        # Highlight numbers
        for match in re.finditer(r'-?\d+\.?\d*', content):
            start_pos = f"1.0+{match.start()}c"
            end_pos = f"1.0+{match.end()}c"
            self.text_editor.tag_add('json_number', start_pos, end_pos)
            
        # Highlight keywords
        for match in re.finditer(r'\b(true|false|null)\b', content):
            start_pos = f"1.0+{match.start()}c"
            end_pos = f"1.0+{match.end()}c"
            self.text_editor.tag_add('json_keyword', start_pos, end_pos)
            
    def highlight_xml(self, content):
        # Simple XML syntax highlighting using regex
        import re
        
        # Highlight tags
        for match in re.finditer(r'<[^>]+>', content):
            start_pos = f"1.0+{match.start()}c"
            end_pos = f"1.0+{match.end()}c"
            self.text_editor.tag_add('xml_tag', start_pos, end_pos)
            
        # Highlight attributes
        for match in re.finditer(r'\w+="[^"]*"', content):
            start_pos = f"1.0+{match.start()}c"
            end_pos = f"1.0+{match.end()}c"
            self.text_editor.tag_add('xml_attribute', start_pos, end_pos)
            
    # File browser operations
    def browse_directory(self):
        directory = filedialog.askdirectory(initialdir=self.current_dir.get())
        if directory:
            self.current_dir.set(directory)
            self.refresh_file_browser()
            
    def refresh_file_browser(self):
        self.file_listbox.delete(0, tk.END)
        
        try:
            directory = self.current_dir.get()
            if not os.path.exists(directory):
                return
                
            # Add parent directory option
            if directory != os.path.dirname(directory):
                self.file_listbox.insert(tk.END, "..")
                
            # List directories first
            items = []
            for item in os.listdir(directory):
                path = os.path.join(directory, item)
                if os.path.isdir(path):
                    items.append(('dir', item))
                elif item.endswith(('.csv', '.json', '.xml', '.md', '.txt')):
                    items.append(('file', item))
                    
            # Sort items
            items.sort(key=lambda x: (x[0], x[1].lower()))
            
            for item_type, item_name in items:
                display_name = f"[{item_name}]" if item_type == 'dir' else item_name
                self.file_listbox.insert(tk.END, display_name)
                
        except PermissionError:
            messagebox.showerror("Error", "Permission denied accessing directory")
        except Exception as e:
            messagebox.showerror("Error", f"Error listing directory: {str(e)}")
            
    def open_from_browser(self, event):
        selection = self.file_listbox.curselection()
        if not selection:
            return
            
        item = self.file_listbox.get(selection[0])
        
        if item == "..":
            # Go to parent directory
            parent = os.path.dirname(self.current_dir.get())
            self.current_dir.set(parent)
            self.refresh_file_browser()
        elif item.startswith("[") and item.endswith("]"):
            # It's a directory
            dir_name = item[1:-1]
            new_path = os.path.join(self.current_dir.get(), dir_name)
            self.current_dir.set(new_path)
            self.refresh_file_browser()
        else:
            # It's a file
            file_path = os.path.join(self.current_dir.get(), item)
            if self.file_modified and not self.ask_save_changes():
                return
            self.load_file(file_path)
            
    # Bookmark operations
    def goto_bookmark(self):
        selection = self.bookmarks_listbox.curselection()
        if selection:
            bookmark = self.bookmarks_listbox.get(selection[0])
            line_num = bookmark.split()[1]  # Extract line number from "Line X"
            self.text_editor.mark_set(tk.INSERT, f"{line_num}.0")
            self.text_editor.see(tk.INSERT)
            self.update_cursor_position()
            
    def delete_bookmark(self):
        selection = self.bookmarks_listbox.curselection()
        if selection:
            bookmark = self.bookmarks_listbox.get(selection[0])
            self.bookmarks.remove(bookmark)
            self.bookmarks_listbox.delete(selection[0])
            
    # Recent files operations
    def add_to_recent_files(self, file_path):
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:10]  # Keep only 10 recent files
        self.update_recent_menu()
        
    def update_recent_menu(self):
        self.recent_menu.delete(0, tk.END)
        for file_path in self.recent_files:
            self.recent_menu.add_command(
                label=os.path.basename(file_path),
                command=lambda f=file_path: self.load_file(f)
            )
            
    def ask_save_changes(self):
        if self.file_modified:
            result = messagebox.askyesnocancel(
                "Save Changes",
                "Do you want to save changes to the current file?"
            )
            if result is True:
                self.save_file()
                return True
            elif result is False:
                return True
            else:
                return False
        return True
        
    def load_settings(self):
        # Load settings from file if it exists
        settings_file = "editor_settings.json"
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    self.font_family = settings.get('font_family', self.font_family)
                    self.font_size = settings.get('font_size', self.font_size)
                    self.show_line_numbers = settings.get('show_line_numbers', self.show_line_numbers)
                    self.word_wrap = settings.get('word_wrap', self.word_wrap)
                    self.syntax_highlighting = settings.get('syntax_highlighting', self.syntax_highlighting)
                    self.recent_files = settings.get('recent_files', [])
                    self.update_recent_menu()
        except Exception:
            pass  # Ignore errors loading settings
            
    def save_settings(self):
        # Save settings to file
        settings_file = "editor_settings.json"
        try:
            settings = {
                'font_family': self.font_family,
                'font_size': self.font_size,
                'show_line_numbers': self.show_line_numbers,
                'word_wrap': self.word_wrap,
                'syntax_highlighting': self.syntax_highlighting,
                'recent_files': self.recent_files
            }
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception:
            pass  # Ignore errors saving settings
            
    def exit_application(self):
        if self.ask_save_changes():
            self.save_settings()
            self.root.quit()


def main():
    root = tk.Tk()
    app = Win95FileEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()