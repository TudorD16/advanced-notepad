import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
import re
import os
import subprocess
import threading
import platform
import json
import io
import sys
from datetime import datetime
import queue
import time
import uuid

class VSCodeEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("VS Code - Python Editor")
        self.root.geometry("1200x800")
        
        # Setare icon pentru aplicație (opțional)
        try:
            self.root.iconbitmap("vscode.ico")  # Necesită un fișier .ico în același folder
        except:
            pass
        
        # Tema dark colors - VS Code specific
        self.colors = {
            'bg': '#1e1e1e',
            'sidebar_bg': '#252526',
            'editor_bg': '#1e1e1e',
            'text': '#d4d4d4',
            'comment': '#6a9955',
            'keyword': '#569cd6',
            'string': '#ce9178',
            'number': '#b5cea8',
            'function': '#dcdcaa',
            'selection': '#264f78',
            'line_number': '#858585',
            'current_line': '#323232',
            'activity_bar': '#333333',
            'tab_active': '#1e1e1e',
            'tab_inactive': '#2d2d2d',
            'status_bar': '#007acc',
            'panel_bg': '#1e1e1e'
        }
        
        self.current_file = None
        self.modified = False
        self.files_opened = []
        self.current_tab_index = 0
        self.search_term = ""
        self.replace_term = ""
        self.terminal_visible = False
        self.explorer_visible = True
        self.current_search_index = 0
        self.search_results = []
        self.terminal_process = None
        
        # Variabile pentru terminalul interactiv
        self.process = None
        self.output_queue = queue.Queue()
        self.error_queue = queue.Queue()
        self.terminal_threads = []
        self.stop_threads = threading.Event()
        self.awaiting_input = False
        self.last_output_incomplete = False  # Urmărește dacă ultima linie de output se termină cu newline
        
        # Autocompletare pentru Python
        self.autocomplete_words = set([
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else',
            'except', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
            'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield',
            'True', 'False', 'None', 'self', 'cls', 'print', 'len', 'str', 'int', 'float', 'list',
            'dict', 'tuple', 'set', 'open', 'range', 'enumerate', 'zip', 'map', 'filter', 'sum',
            'min', 'max', 'sorted', 'reversed', 'any', 'all', 'isinstance', 'type', '__init__'
        ])
        
        # Inițializează UI
        self.setup_ui()
        self.setup_syntax_highlighting()
        
        # Configurează tema dark pentru all widgets
        self.apply_theme()
        
        self.last_output_time = time.time()
        
    def apply_theme(self):
        # Configurează stilul pentru ttk widgets
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurează stilul pentru butoane și alte widget-uri
        style.configure('TButton', background=self.colors['sidebar_bg'], foreground=self.colors['text'])
        style.configure('TEntry', fieldbackground=self.colors['editor_bg'], foreground=self.colors['text'])
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['text'])
        style.configure('TNotebook', background=self.colors['bg'])
        style.configure('TNotebook.Tab', background=self.colors['tab_inactive'], foreground=self.colors['text'], padding=[10, 2])
        style.map('TNotebook.Tab', background=[('selected', self.colors['tab_active'])])
        
        # Configurare specifică pentru Treeview (file explorer)
        style.configure("Treeview", 
                       background=self.colors['sidebar_bg'],
                       foreground=self.colors['text'],
                       fieldbackground=self.colors['sidebar_bg'])
        style.map('Treeview', background=[('selected', self.colors['selection'])])
        
    def setup_ui(self):
        # Configurează tema dark pentru root
        self.root.configure(bg=self.colors['bg'])
        
        # Menu bar
        menubar = tk.Menu(self.root, bg=self.colors['sidebar_bg'], fg=self.colors['text'])
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['sidebar_bg'], fg=self.colors['text'])
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New File", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open File...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Open Folder...", command=self.open_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_command(label="Save All", command=self.save_all_files)
        file_menu.add_separator()
        file_menu.add_command(label="Close Editor", command=self.close_current_file, accelerator="Ctrl+W")
        file_menu.add_command(label="Exit", command=self.exit_application, accelerator="Alt+F4")
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['sidebar_bg'], fg=self.colors['text'])
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut_text, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy_text, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste_text, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find", command=self.find_text, accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace", command=self.replace_text, accelerator="Ctrl+H")
        edit_menu.add_separator()
        edit_menu.add_command(label="Comment Line", command=self.comment_line, accelerator="Ctrl+/")
        edit_menu.add_command(label="Indent", command=self.indent, accelerator="Tab")
        edit_menu.add_command(label="Dedent", command=self.dedent, accelerator="Shift+Tab")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['sidebar_bg'], fg=self.colors['text'])
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Explorer", command=self.toggle_explorer, accelerator="Ctrl+B")
        view_menu.add_command(label="Terminal", command=self.toggle_terminal, accelerator="Ctrl+`")
        view_menu.add_separator()
        view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        
        # Run menu
        run_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['sidebar_bg'], fg=self.colors['text'])
        menubar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Run Python File", command=self.run_python_file, accelerator="F5")
        run_menu.add_command(label="Debug", command=self.debug_python_file, accelerator="Ctrl+F5")
        
        # Main layout with paned windows
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Activity bar (stânga de tot)
        self.activity_bar = tk.Frame(main_paned, bg=self.colors['activity_bar'], width=50)
        self.activity_bar.pack_propagate(False)
        main_paned.add(self.activity_bar)
        
        # Activity bar icons (simulare)
        explorer_icon = tk.Label(self.activity_bar, text="📁", bg=self.colors['activity_bar'], 
                               fg=self.colors['text'], font=('Segoe UI', 16))
        explorer_icon.pack(pady=(10, 5))
        explorer_icon.bind("<Button-1>", lambda e: self.toggle_explorer())
        
        search_icon = tk.Label(self.activity_bar, text="🔍", bg=self.colors['activity_bar'], 
                              fg=self.colors['text'], font=('Segoe UI', 16))
        search_icon.pack(pady=5)
        search_icon.bind("<Button-1>", lambda e: self.find_text())
        
        git_icon = tk.Label(self.activity_bar, text="⑂", bg=self.colors['activity_bar'], 
                           fg=self.colors['text'], font=('Segoe UI', 16))
        git_icon.pack(pady=5)
        
        debug_icon = tk.Label(self.activity_bar, text="⏵", bg=self.colors['activity_bar'], 
                             fg=self.colors['text'], font=('Segoe UI', 16))
        debug_icon.pack(pady=5)
        debug_icon.bind("<Button-1>", lambda e: self.run_python_file())
        
        extensions_icon = tk.Label(self.activity_bar, text="⊞", bg=self.colors['activity_bar'], 
                                  fg=self.colors['text'], font=('Segoe UI', 16))
        extensions_icon.pack(pady=5)
        
        # Sidebar container
        self.sidebar_container = tk.Frame(main_paned, bg=self.colors['sidebar_bg'], width=250)
        self.sidebar_container.pack_propagate(False)
        main_paned.add(self.sidebar_container)
        
        # Explorer sidebar
        self.setup_explorer_sidebar()
        
        # Editor area frame
        editor_container = ttk.Frame(main_paned)
        main_paned.add(editor_container)
        
        # Editor și terminal în PanedWindow vertical
        self.editor_terminal_paned = ttk.PanedWindow(editor_container, orient=tk.VERTICAL)
        self.editor_terminal_paned.pack(fill=tk.BOTH, expand=True)
        
        # Editor frame
        editor_frame = ttk.Frame(self.editor_terminal_paned)
        self.editor_terminal_paned.add(editor_frame, weight=3)
        
        # Tabs pentru fișiere multiple
        self.notebook = ttk.Notebook(editor_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Adaugă opțiunea de închidere tab cu buton X sau cu middle-click
        self.notebook.enable_traversal()
        
        # Primul tab (default)
        self.create_editor_tab("untitled")
        
        # Terminal
        self.terminal_frame = ttk.Frame(self.editor_terminal_paned, height=200)
        self.terminal_frame.pack_propagate(False)
        
        # Terminal header
        terminal_header = tk.Frame(self.terminal_frame, bg=self.colors['tab_inactive'], height=30)
        terminal_header.pack(fill=tk.X)
        
        terminal_label = tk.Label(terminal_header, text="TERMINAL", bg=self.colors['tab_inactive'],
                                 fg=self.colors['text'], font=('Consolas', 9, 'bold'))
        terminal_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        close_terminal_btn = tk.Label(terminal_header, text="✕", bg=self.colors['tab_inactive'],
                                     fg=self.colors['text'], cursor="hand2")
        close_terminal_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        close_terminal_btn.bind("<Button-1>", lambda e: self.toggle_terminal())
        
        # Terminal text cu suport pentru input
        self.terminal_output = tk.Text(self.terminal_frame, bg=self.colors['editor_bg'],
                                     fg=self.colors['text'], font=('Consolas', 10),
                                     wrap=tk.WORD)
        self.terminal_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Adaugă un prompt marker pentru input
        self.terminal_prompt = ">>> "
        self.terminal_output.tag_configure("prompt", foreground="#4EC9B0")
        self.terminal_output.tag_configure("input", foreground="#CE9178")
        self.terminal_output.tag_configure("error", foreground="red")
        self.terminal_output.tag_configure("input_prompt", foreground="#4EC9B0", font=('Consolas', 10, 'bold'))
        
        # Input field separat pentru terminal
        self.terminal_input = tk.Entry(self.terminal_frame, bg=self.colors['editor_bg'],
                                     fg=self.colors['text'], font=('Consolas', 10),
                                     insertbackground=self.colors['text'], state=tk.DISABLED)
        self.terminal_input.pack(fill=tk.X, padx=5, pady=(0, 5))

        # Binding pentru input field
        self.terminal_input.bind("<Return>", self.on_terminal_input_enter)
        
        # Binding pentru tastele din terminal
        #self.terminal_output.bind("<Return>", self.on_terminal_enter)
        
        # Terminal scrollbar (doar o singură dată)
        terminal_scrollbar = tk.Scrollbar(self.terminal_output, orient=tk.VERTICAL, 
                                         command=self.terminal_output.yview)
        terminal_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.terminal_output.config(yscrollcommand=terminal_scrollbar.set)
        
        interrupt_btn = tk.Label(terminal_header, text="⏹", bg=self.colors['tab_inactive'],
                       fg=self.colors['text'], cursor="hand2")
        interrupt_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        interrupt_btn.bind("<Button-1>", lambda e: self.interrupt_process())
        
        # Variabile pentru procesul în execuție
        self.process = None
        self.awaiting_input = False
        
        # Status bar
        status_container = tk.Frame(self.root, bg=self.colors['status_bar'], height=25)
        status_container.pack(side=tk.BOTTOM, fill=tk.X)
        status_container.pack_propagate(False)
        
        self.status_bar_left = tk.Label(status_container, text="Ready", bg=self.colors['status_bar'],
                                      fg=self.colors['text'], font=('Consolas', 9), anchor='w')
        self.status_bar_left.pack(side=tk.LEFT, padx=10)
        
        self.status_bar_right = tk.Label(status_container, text="Python", bg=self.colors['status_bar'],
                                       fg=self.colors['text'], font=('Consolas', 9), anchor='e')
        self.status_bar_right.pack(side=tk.RIGHT, padx=10)
        
        self.line_col_indicator = tk.Label(status_container, text="Ln 1, Col 1", bg=self.colors['status_bar'],
                                        fg=self.colors['text'], font=('Consolas', 9))
        self.line_col_indicator.pack(side=tk.RIGHT, padx=15)
        
        encoding_indicator = tk.Label(status_container, text="UTF-8", bg=self.colors['status_bar'],
                                    fg=self.colors['text'], font=('Consolas', 9))
        encoding_indicator.pack(side=tk.RIGHT, padx=15)
        
        # Keystroke bindings
        self.bind_keystrokes()
        
    def on_terminal_input_enter(self, event):
        """Gestionează input-ul din field-ul separat de terminal"""
        if not self.process or self.process.poll() is not None:
            return "break"
            
        # Obține input-ul utilizatorului
        user_input = self.terminal_input.get()
        
        # Afișează input-ul în terminal
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.insert(tk.END, f"{user_input}\n", "input")
        self.terminal_output.see(tk.END)
        self.terminal_output.config(state=tk.DISABLED)
        
        # Șterge input field-ul
        self.terminal_input.delete(0, tk.END)
        
        # Trimite input-ul către proces (inclusiv "\n")
        try:
            # Adăugăm \n pentru a simula apăsarea Enter și flush imediat pentru a evita buffering
            input_to_send = user_input + '\n'
            self.process.stdin.write(input_to_send)
            self.process.stdin.flush()
            
            # Resetează starea de așteptare input
            self.awaiting_input = False
        except Exception as e:
            self.terminal_output.config(state=tk.NORMAL)
            self.terminal_output.insert(tk.END, f"Error sending input to process: {str(e)}\n", "error")
            self.terminal_output.see(tk.END)
            self.terminal_output.config(state=tk.DISABLED)
        
        return "break"

    
    '''
    def on_terminal_input_enter(self, event):
        """Gestionează input-ul din field-ul separat de terminal"""
        if not self.process or self.process.poll() is not None:
            return "break"
            
        # Obține input-ul utilizatorului
        user_input = self.terminal_input.get()
        
        # Afișează input-ul în terminal
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.insert(tk.END, f"{user_input}\n", "input")
        self.terminal_output.see(tk.END)
        self.terminal_output.config(state=tk.DISABLED)
        
        # Șterge input field-ul
        self.terminal_input.delete(0, tk.END)
        
        # Trimite input-ul către proces
        try:
            input_to_send = user_input + '\n'
            self.process.stdin.write(input_to_send)
            self.process.stdin.flush()
        except Exception as e:
            self.terminal_output.config(state=tk.NORMAL)
            self.terminal_output.insert(tk.END, f"Error sending input to process: {str(e)}\n", "error")
            self.terminal_output.see(tk.END)
            self.terminal_output.config(state=tk.DISABLED)
        
        return "break"
    '''
    
    def interrupt_process(self):
        """Întrerupe procesul curent"""
        if not self.process or self.process.poll() is not None:
            return
            
        # Dacă procesul rulează, îl întrerupem
        if platform.system() == "Windows":
            try:
                # Pe Windows, încearcă să trimită un CTRL+Break
                import ctypes
                ctypes.windll.kernel32.GenerateConsoleCtrlEvent(1, self.process.pid)
            except:
                # Alternativă: forțează închiderea
                self.process.terminate()
        else:
            try:
                # Pe Unix, trimite un SIGINT (echivalent CTRL+C)
                import signal
                self.process.send_signal(signal.SIGINT)
            except:
                # Alternativă: forțează închiderea
                self.process.terminate()
        
        # Resetează starea
        self.awaiting_input = False
        
    def setup_explorer_sidebar(self):
        # Curăță sidebar
        for widget in self.sidebar_container.winfo_children():
            widget.destroy()
        
        # Explorer header
        explorer_header = tk.Frame(self.sidebar_container, bg=self.colors['sidebar_bg'])
        explorer_header.pack(fill=tk.X)
        
        explorer_title = tk.Label(explorer_header, text="EXPLORER", bg=self.colors['sidebar_bg'], 
                                 fg=self.colors['text'], font=('Consolas', 9, 'bold'))
        explorer_title.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Butoane pentru Explorer
        new_file_btn = tk.Label(explorer_header, text="📄", bg=self.colors['sidebar_bg'],
                               fg=self.colors['text'], cursor="hand2")
        new_file_btn.pack(side=tk.RIGHT, padx=(0, 5))
        new_file_btn.bind("<Button-1>", lambda e: self.new_file())
        
        new_folder_btn = tk.Label(explorer_header, text="📁", bg=self.colors['sidebar_bg'],
                                fg=self.colors['text'], cursor="hand2")
        new_folder_btn.pack(side=tk.RIGHT, padx=(0, 5))
        
        refresh_btn = tk.Label(explorer_header, text="🔄", bg=self.colors['sidebar_bg'],
                              fg=self.colors['text'], cursor="hand2")
        refresh_btn.pack(side=tk.RIGHT, padx=(0, 5))
        refresh_btn.bind("<Button-1>", lambda e: self.refresh_file_explorer())
        
        collapse_btn = tk.Label(explorer_header, text="⤌", bg=self.colors['sidebar_bg'],
                               fg=self.colors['text'], cursor="hand2")
        collapse_btn.pack(side=tk.RIGHT, padx=(0, 5))
        
        # File tree with treeview
        self.file_tree = ttk.Treeview(self.sidebar_container, selectmode="browse", show="tree")
        self.file_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.file_tree.bind("<Double-1>", self.on_tree_double_click)
        
        # Scrollbar for file tree
        tree_scroll = ttk.Scrollbar(self.file_tree, orient="vertical", command=self.file_tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_tree.configure(yscrollcommand=tree_scroll.set)
        
        # Configurare treeview style
        style = ttk.Style()
        style.configure("Treeview", 
                       background=self.colors['sidebar_bg'],
                       foreground=self.colors['text'],
                       fieldbackground=self.colors['sidebar_bg'])
        style.map('Treeview', background=[('selected', self.colors['selection'])])
        
        # Open folder label if none is opened
        self.folder_label = tk.Label(self.sidebar_container, 
                                    text="No folder opened\nClick 'Open Folder' to open a project", 
                                    bg=self.colors['sidebar_bg'], fg=self.colors['text'],
                                    justify=tk.CENTER)
        self.folder_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.file_tree.pack_forget()  # Ascunde tree-ul până când se deschide un folder
        
    def create_editor_tab(self, title, content=""):
        # Creează un nou tab cu editor
        tab_frame = ttk.Frame(self.notebook)
        
        # Tab header cu buton de închidere
        tab_header = tk.Frame(tab_frame, bg=self.colors['tab_inactive'])
        tab_header.pack(fill=tk.X)
        
        # Buton de închidere
        close_btn = tk.Label(tab_header, text="✕", bg=self.colors['tab_inactive'],
                           fg=self.colors['text'], cursor="hand2", font=('Consolas', 9))
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        # Editor container
        editor_container = tk.Frame(tab_frame, bg=self.colors['editor_bg'])
        editor_container.pack(fill=tk.BOTH, expand=True)
        
        # Line numbers
        line_numbers = tk.Text(editor_container, width=4, bg=self.colors['editor_bg'],
                              fg=self.colors['line_number'], font=('Consolas', 11),
                              state=tk.DISABLED, wrap=tk.NONE, bd=0, padx=5)
        line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Text editor
        text_editor = tk.Text(editor_container, bg=self.colors['editor_bg'], 
                             fg=self.colors['text'], font=('Consolas', 11),
                             insertbackground=self.colors['text'], wrap=tk.NONE,
                             selectbackground=self.colors['selection'], bd=0,
                             undo=True, maxundo=100, padx=10, pady=5)
        text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Highlight line curentă
        text_editor.tag_configure("current_line", background=self.colors['current_line'])
        
        # Scrollbar vertical
        v_scrollbar = tk.Scrollbar(editor_container, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        v_scrollbar.config(command=lambda *args: self.on_scroll(*args))
        text_editor.config(yscrollcommand=v_scrollbar.set)
        line_numbers.config(yscrollcommand=v_scrollbar.set)
        
        # Scrollbar orizontal
        h_scrollbar = tk.Scrollbar(tab_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        h_scrollbar.config(command=text_editor.xview)
        text_editor.config(xscrollcommand=h_scrollbar.set)
        
        # Adaugă tag-uri pentru text editor
        text_editor.tag_configure('keyword', foreground=self.colors['keyword'])
        text_editor.tag_configure('string', foreground=self.colors['string'])
        text_editor.tag_configure('comment', foreground=self.colors['comment'])
        text_editor.tag_configure('number', foreground=self.colors['number'])
        text_editor.tag_configure('function', foreground=self.colors['function'])
        text_editor.tag_configure('bracket', background='#442e2e')
        
        # Inserează conținut dacă există
        if content:
            text_editor.insert('1.0', content)
        
        # Adaugă tab
        tab_id = self.notebook.add(tab_frame, text=title)
        self.notebook.select(len(self.notebook.tabs()) - 1)
        
        # Index pentru acest tab
        tab_index = len(self.files_opened)
        
        # Conectează butonul de închidere
        close_btn.bind("<Button-1>", lambda e, idx=tab_index: self.close_tab_by_index(idx))
        
        # Adaugă la lista de file-uri deschise
        self.files_opened.append({
            'title': title,
            'path': None,
            'editor': text_editor,
            'line_numbers': line_numbers,
            'modified': False,
            'tab_id': tab_id,
            'close_btn': close_btn
        })
        
        # Bind evenimente
        text_editor.bind('<KeyRelease>', lambda e, editor=text_editor, ln=line_numbers: 
                        self.on_text_change(e, editor, ln))
        text_editor.bind('<Button-1>', lambda e, editor=text_editor, ln=line_numbers: 
                        self.on_text_change(e, editor, ln))
        text_editor.bind("<<Modified>>", lambda e, index=len(self.files_opened)-1: 
                        self.on_content_modified(e, index))
        text_editor.bind('<KeyRelease-parenleft>', lambda e, editor=text_editor: 
                        self.auto_close_bracket(e, editor, '(', ')'))
        text_editor.bind('<KeyRelease-bracketleft>', lambda e, editor=text_editor: 
                        self.auto_close_bracket(e, editor, '[', ']'))
        text_editor.bind('<KeyRelease-braceleft>', lambda e, editor=text_editor: 
                        self.auto_close_bracket(e, editor, '{', '}'))
        text_editor.bind('<KeyRelease-quotedbl>', lambda e, editor=text_editor: 
                        self.auto_close_bracket(e, editor, '"', '"'))
        text_editor.bind('<KeyRelease-quoteright>', lambda e, editor=text_editor: 
                        self.auto_close_bracket(e, editor, "'", "'"))
        text_editor.bind('<KeyRelease-colon>', lambda e, editor=text_editor: 
                        self.auto_indent_after_colon(e, editor))
        text_editor.bind('<KeyRelease-Return>', lambda e, editor=text_editor: 
                        self.auto_indent(e, editor))
        text_editor.bind('<Tab>', lambda e, editor=text_editor: 
                        self.handle_tab(e, editor))
        text_editor.bind('<KeyRelease-period>', lambda e, editor=text_editor: 
                        self.show_autocomplete(e, editor))
        text_editor.bind("<ButtonRelease-1>", lambda e, editor=text_editor, ln=line_numbers: 
                        self.on_editor_click(e, editor, ln))
        # Binding pentru mouse wheel
        text_editor.bind("<MouseWheel>", lambda e, editor=text_editor, ln=line_numbers: 
                        self.on_mousewheel(e, editor, ln))  # Windows
        text_editor.bind("<Button-4>", lambda e, editor=text_editor, ln=line_numbers: 
                        self.on_mousewheel(e, editor, ln))  # Linux scroll up
        text_editor.bind("<Button-5>", lambda e, editor=text_editor, ln=line_numbers: 
                        self.on_mousewheel(e, editor, ln))  # Linux scroll down
        
        # Bind middle-click pentru închidere tab
        self.notebook.bind("<Button-2>", self.on_tab_middle_click)
        
        # Update line numbers
        self.update_line_numbers(text_editor, line_numbers)
        
        # Focus pe editor
        text_editor.focus_set()
        
        return text_editor
        
    def on_mousewheel(self, event, editor, line_numbers):
        # Sincronizează line numbers la scroll cu mouse-ul
        if platform.system() == "Windows":
            # Pentru Windows, evenimentele au proprietatea delta
            editor.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif platform.system() == "Darwin":  # macOS
            editor.yview_scroll(int(-1 * event.delta), "units")
        else:  # Linux și alte sisteme
            if event.num == 4:  # Scroll up
                editor.yview_scroll(-1, "units")
            elif event.num == 5:  # Scroll down
                editor.yview_scroll(1, "units")
                
        # Sincronizează line numbers
        self.after_scroll_sync(editor, line_numbers)
        return "break"

    def after_scroll_sync(self, editor, line_numbers):
        # Funcție ajutătoare pentru a sincroniza după scroll
        line_numbers.yview_moveto(editor.yview()[0])
        self.root.after(10, lambda: line_numbers.yview_moveto(editor.yview()[0]))
    
    def on_editor_click(self, event, editor, line_numbers):
        # Salvează poziția de scroll actuală înainte de orice operație
        current_scroll_position = editor.yview()[0]
        
        # Procesează click-ul la poziția corectă
        try:
            click_pos = editor.index(f"@{event.x},{event.y}")
            editor.mark_set(tk.INSERT, click_pos)  # Setează cursorul la poziția exactă a click-ului
        except:
            pass
        
        # Highlight-ul liniei curente fără a afecta poziția de scroll
        self.highlight_current_line(editor)
        
        # Actualizează line numbers fără a schimba poziția de scroll a editorului
        self.update_line_numbers_without_scroll(editor, line_numbers)
        
        # Restaurează poziția de scroll a editorului
        editor.yview_moveto(current_scroll_position)
        
        # Sincronizează line_numbers cu poziția editorului (nu invers)
        line_numbers.yview_moveto(editor.yview()[0])
        
        # Update cursor position in status bar
        cursor_pos = editor.index(tk.INSERT)
        line, col = cursor_pos.split('.')
        self.line_col_indicator.config(text=f"Ln {line}, Col {int(col)+1}")
        
    def update_line_numbers_without_scroll(self, editor, line_numbers):
        content = editor.get('1.0', tk.END)
        lines = content.count('\n')
        if lines == 0:
            lines = 1
            
        line_numbers.config(state=tk.NORMAL)
        line_numbers.delete('1.0', tk.END)
        
        line_numbers_string = '\n'.join(str(i) for i in range(1, lines + 1))
        line_numbers.insert('1.0', line_numbers_string)
        line_numbers.config(state=tk.DISABLED)
        
        # Nu sincroniza scroll-ul editorului, doar păstrează poziția line_numbers sincronizată cu editorul
        line_numbers.yview_moveto(editor.yview()[0])
        
    def on_scroll(self, *args):
        # Sincronizează scroll-ul între editor și line numbers
        current_editor = self.get_current_editor()
        line_numbers = self.get_current_line_numbers()
        
        if current_editor and line_numbers:
            # Aplică scroll-ul la ambele widget-uri
            current_editor.yview(*args)
            line_numbers.yview(*args)
            
            # Forțează sincronizarea cu un mic delay pentru a asigura că poziția de scroll este aceeași
            self.root.after(10, lambda: line_numbers.yview_moveto(current_editor.yview()[0]))
    
    def close_tab_by_index(self, index):
        # Asigură-te că indexul este valid
        if index >= len(self.files_opened):
            # Poate indexul s-a schimbat din cauza închiderii altor tab-uri
            # Găsim tab-ul curent selectat
            index = self.notebook.index(self.notebook.select())
        
        # Salvăm indexul curent
        current_tab_index = self.current_tab_index
        
        # Selectăm tab-ul pe care vrem să-l închidem
        self.notebook.select(index)
        self.current_tab_index = index
        
        # Închidem tab-ul folosind metoda existentă
        self.close_current_file()
        
        # Dacă tab-ul curent era diferit și încă există, revenim la el
        if current_tab_index != index and current_tab_index < len(self.notebook.tabs()):
            self.notebook.select(current_tab_index)
    
    def on_tab_middle_click(self, event):
        # Obține tab-ul pe care s-a făcut click
        clicked_tab = self.notebook.tk.call(self.notebook._w, "identify", "tab", event.x, event.y)
        if clicked_tab != "":
            # Închide tab-ul
            self.close_tab_by_index(int(clicked_tab))
    
    def setup_syntax_highlighting(self):
        # Python keywords
        self.keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else',
            'except', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
            'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield',
            'True', 'False', 'None', 'self', 'cls', 'print', 'len', 'str', 'int', 'float', 'list',
            'dict', 'tuple', 'set', 'open', 'range', 'enumerate', 'zip', 'map', 'filter'
        ]
        
        # Builtin functions pentru autocompletare
        for func in dir(__builtins__):
            if not func.startswith('_'):
                self.autocomplete_words.add(func)
        
    def highlight_syntax(self, editor):
        # Elimină highlighting-ul anterior
        for tag in ['keyword', 'string', 'comment', 'number', 'function']:
            editor.tag_remove(tag, '1.0', tk.END)
        
        content = editor.get('1.0', tk.END)
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Highlight keywords
            for keyword in self.keywords:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                for match in re.finditer(pattern, line):
                    start = f"{line_num}.{match.start()}"
                    end = f"{line_num}.{match.end()}"
                    editor.tag_add('keyword', start, end)
            
            # Highlight strings
            string_patterns = [r'"[^"\\\n]*(?:\\.[^"\\\n]*)*"', r"'[^'\\\n]*(?:\\.[^'\\\n]*)*'", 
                             r'"""[\s\S]*?"""', r"'''[\s\S]*?'''"]
            for pattern in string_patterns:
                for match in re.finditer(pattern, line):
                    start = f"{line_num}.{match.start()}"
                    end = f"{line_num}.{match.end()}"
                    editor.tag_add('string', start, end)
            
            # Highlight comments
            comment_match = re.search(r'#.*$', line)
            if comment_match:
                start = f"{line_num}.{comment_match.start()}"
                end = f"{line_num}.{comment_match.end()}"
                editor.tag_add('comment', start, end)
            
            # Highlight numbers
            for match in re.finditer(r'\b\d+\.?\d*\b', line):
                start = f"{line_num}.{match.start()}"
                end = f"{line_num}.{match.end()}"
                editor.tag_add('number', start, end)
            
            # Highlight function definitions and calls
            func_def_match = re.search(r'def\s+(\w+)', line)
            if func_def_match:
                start = f"{line_num}.{func_def_match.start(1)}"
                end = f"{line_num}.{func_def_match.end(1)}"
                editor.tag_add('function', start, end)
                
                # Adaugă la lista de cuvinte pentru autocompletare
                self.autocomplete_words.add(func_def_match.group(1))
            
            # Highlight function calls
            for match in re.finditer(r'(\w+)\(', line):
                start = f"{line_num}.{match.start(1)}"
                end = f"{line_num}.{match.end(1)}"
                editor.tag_add('function', start, end)
                
                # Adaugă la lista de cuvinte pentru autocompletare
                self.autocomplete_words.add(match.group(1))
    
    def highlight_current_line(self, editor):
        editor.tag_remove("current_line", "1.0", tk.END)
        editor.tag_add("current_line", "insert linestart", "insert lineend+1c")
    
    def update_line_numbers(self, editor, line_numbers):
        # Salvează poziția de scroll curentă
        current_scroll = editor.yview()[0]
        
        content = editor.get('1.0', tk.END)
        lines = content.count('\n')
        if lines == 0:
            lines = 1
            
        line_numbers.config(state=tk.NORMAL)
        line_numbers.delete('1.0', tk.END)
        
        line_numbers_string = '\n'.join(str(i) for i in range(1, lines + 1))
        line_numbers.insert('1.0', line_numbers_string)
        line_numbers.config(state=tk.DISABLED)
        
        # Sincronizează line_numbers cu editorul fără a modifica poziția editorului
        line_numbers.yview_moveto(current_scroll)
        
        # Nu modificăm poziția de scroll a editorului
        # editor.yview_moveto(line_numbers.yview()[0]) - eliminat
    
    def on_text_change(self, event=None, editor=None, line_numbers=None):
        if not editor:
            editor = self.get_current_editor()
        if not line_numbers:
            line_numbers = self.get_current_line_numbers()
            
        self.update_line_numbers(editor, line_numbers)
        self.highlight_syntax(editor)
        self.highlight_current_line(editor)
        
        # Update cursor position in status bar
        cursor_pos = editor.index(tk.INSERT)
        line, col = cursor_pos.split('.')
        self.line_col_indicator.config(text=f"Ln {line}, Col {int(col)+1}")
    
    def on_content_modified(self, event, index):
        if index >= len(self.files_opened):
            # Poate a fost închis deja tab-ul
            return
            
        editor = self.files_opened[index]['editor']
        editor.edit_modified(False)  # Reset flag
        
        if not self.files_opened[index]['modified']:
            self.files_opened[index]['modified'] = True
            # Update tab name to show modified indicator
            title = self.files_opened[index]['title']
            if not title.endswith('*'):
                self.notebook.tab(index, text=title + '*')
    
    def on_tab_changed(self, event):
        # Update the current tab index
        self.current_tab_index = self.notebook.index("current")
        
        # Actualizează titlul ferestrei cu numele fișierului curent
        if len(self.files_opened) > 0 and self.current_tab_index < len(self.files_opened):
            current_file = self.files_opened[self.current_tab_index]
            if current_file['path']:
                self.root.title(f"{os.path.basename(current_file['path'])} - VS Code - Python Editor")
            else:
                self.root.title(f"{current_file['title']} - VS Code - Python Editor")
            
            # Actualizează statusbar
            self.status_bar_left.config(text="Ready")
            if current_file['path']:
                self.status_bar_right.config(text=f"Python {os.path.splitext(current_file['path'])[1]}")
            else:
                self.status_bar_right.config(text="Python")
            
            # Aplică highlight și update line numbers
            editor = current_file['editor']
            line_numbers = current_file['line_numbers']
            self.highlight_syntax(editor)
            self.update_line_numbers(editor, line_numbers)
            self.highlight_current_line(editor)
            
            # Update cursor position
            cursor_pos = editor.index(tk.INSERT)
            line, col = cursor_pos.split('.')
            self.line_col_indicator.config(text=f"Ln {line}, Col {int(col)+1}")
    
    def bind_keystrokes(self):
        # Key bindings pentru root
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-S>', lambda e: self.save_as_file())  # Ctrl+Shift+S
        self.root.bind('<Control-w>', lambda e: self.close_current_file())
        self.root.bind('<Control-f>', lambda e: self.find_text())
        self.root.bind('<Control-h>', lambda e: self.replace_text())
        self.root.bind('<Control-b>', lambda e: self.toggle_explorer())
        self.root.bind('<Control-grave>', lambda e: self.toggle_terminal())  # Ctrl+`
        self.root.bind('<F5>', lambda e: self.run_python_file())
        self.root.bind('<Control-F5>', lambda e: self.debug_python_file())
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())  # Ctrl++
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())  # Ctrl+-
    
    def new_file(self):
        # Creează un nou tab gol
        self.create_editor_tab("untitled")
    
    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Python files", "*.py"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            # Verifică dacă fișierul este deja deschis
            for i, file_info in enumerate(self.files_opened):
                if file_info['path'] == file_path:
                    self.notebook.select(i)  # Selectează tab-ul existent
                    return
            
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                    # Creează un nou tab cu conținutul fișierului
                    file_name = os.path.basename(file_path)
                    editor = self.create_editor_tab(file_name, content)
                    
                    # Actualizează calea pentru fișierul curent
                    current_index = len(self.files_opened) - 1
                    self.files_opened[current_index]['path'] = file_path
                    self.files_opened[current_index]['modified'] = False
                    
                    # Actualizează titlul ferestrei
                    self.root.title(f"{file_name} - VS Code - Python Editor")
                    
                    # Colectează cuvinte pentru autocompletare din fișier
                    self.collect_words_from_file(content)
                    
                    # Actualizează status bar
                    self.status_bar_left.config(text=f"Opened: {file_name}")
                    
                    # Adaugă la file tree dacă este în folder-ul deschis
                    self.refresh_file_explorer()
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")
    
    def open_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            # Schimbă directorul curent
            os.chdir(folder_path)
            
            # Actualizează title bar
            self.root.title(f"{os.path.basename(folder_path)} - VS Code - Python Editor")
            
            # Schimbă status bar
            self.status_bar_left.config(text=f"Folder: {os.path.basename(folder_path)}")
            
            # Ascunde label-ul și arată treeview
            self.folder_label.pack_forget()
            self.file_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Populează file explorer
            self.populate_file_explorer(folder_path)
    
    def populate_file_explorer(self, folder_path):
        # Șterge conținut anterior
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # Adaugă root folder
        root_name = os.path.basename(folder_path)
        root_id = self.file_tree.insert('', 'end', text=root_name, open=True, 
                                      values=(folder_path, "folder"))
        
        # Funcție recursivă pentru a adăuga fișiere și subfoldere
        def add_directory_contents(parent_id, parent_path):
            try:
                # Sortează: întâi foldere, apoi fișiere, ambele alfabetic
                items = os.listdir(parent_path)
                folders = [i for i in items if os.path.isdir(os.path.join(parent_path, i)) and not i.startswith('.')]
                files = [i for i in items if os.path.isfile(os.path.join(parent_path, i)) and not i.startswith('.')]
                
                folders.sort()
                files.sort()
                
                # Adaugă foldere
                for folder in folders:
                    folder_path = os.path.join(parent_path, folder)
                    folder_id = self.file_tree.insert(parent_id, 'end', text=folder, 
                                                   values=(folder_path, "folder"))
                    add_directory_contents(folder_id, folder_path)
                
                # Adaugă fișiere
                for file in files:
                    file_path = os.path.join(parent_path, file)
                    # Alege icon bazat pe extensie
                    file_icon = ""
                    if file.endswith('.py'):
                        file_icon = "🐍 "
                    elif file.endswith(('.txt', '.md')):
                        file_icon = "📄 "
                    elif file.endswith(('.jpg', '.png', '.gif')):
                        file_icon = "🖼️ "
                    elif file.endswith(('.html', '.css', '.js')):
                        file_icon = "🌐 "
                    elif file.endswith('.json'):
                        file_icon = "📋 "
                    
                    self.file_tree.insert(parent_id, 'end', text=f"{file_icon}{file}", 
                                        values=(file_path, "file"))
            except Exception as e:
                print(f"Error accessing {parent_path}: {e}")
        
        # Populează tree-ul
        add_directory_contents(root_id, folder_path)
    
    def refresh_file_explorer(self):
        # Reîmprospătează file explorer dacă există un folder deschis
        root_items = self.file_tree.get_children()
        if root_items:
            root_id = root_items[0]
            folder_path = self.file_tree.item(root_id, "values")[0]
            self.populate_file_explorer(folder_path)
    
    def on_tree_double_click(self, event):
        # Deschide fișier la dublu click
        selection = self.file_tree.selection()
        if not selection:
            return
            
        item_id = selection[0]
        item_values = self.file_tree.item(item_id, "values")
        if item_values and item_values[1] == "file":
            file_path = item_values[0]
            # Verifică dacă fișierul este deja deschis
            for i, file_info in enumerate(self.files_opened):
                if file_info['path'] == file_path:
                    self.notebook.select(i)  # Selectează tab-ul existent
                    return
            
            # Deschide fișierul
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                    # Creează un nou tab cu conținutul fișierului
                    file_name = os.path.basename(file_path)
                    editor = self.create_editor_tab(file_name, content)
                    
                    # Actualizează calea pentru fișierul curent
                    current_index = len(self.files_opened) - 1
                    self.files_opened[current_index]['path'] = file_path
                    self.files_opened[current_index]['modified'] = False
                    
                    # Actualizează titlul ferestrei
                    self.root.title(f"{file_name} - VS Code - Python Editor")
                    
                    # Colectează cuvinte pentru autocompletare din fișier
                    self.collect_words_from_file(content)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")
    
    def save_file(self):
        if len(self.files_opened) == 0 or self.current_tab_index >= len(self.files_opened):
            return
            
        current_file = self.files_opened[self.current_tab_index]
        
        if current_file['path']:
            self.save_to_file(current_file['path'])
        else:
            self.save_as_file()
    
    def save_as_file(self):
        if len(self.files_opened) == 0 or self.current_tab_index >= len(self.files_opened):
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python files", "*.py"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.save_to_file(file_path)
            
            # Actualizează informațiile despre fișier
            current_file = self.files_opened[self.current_tab_index]
            current_file['path'] = file_path
            current_file['title'] = os.path.basename(file_path)
            current_file['modified'] = False
            
            # Actualizează tab
            self.notebook.tab(self.current_tab_index, text=current_file['title'])
            
            # Actualizează title bar
            self.root.title(f"{current_file['title']} - VS Code - Python Editor")
            
            # Reîmprospătează file explorer
            self.refresh_file_explorer()
    
    def save_all_files(self):
        for i, file_info in enumerate(self.files_opened):
            if file_info['modified']:
                if file_info['path']:
                    self.save_to_file(file_info['path'], i)
                else:
                    # Salvează cu dialog doar prima dată
                    current_tab = self.current_tab_index
                    self.notebook.select(i)
                    self.save_as_file()
                    self.notebook.select(current_tab)
    
    def save_to_file(self, file_path, index=None):
        if index is None:
            index = self.current_tab_index
            
        if index >= len(self.files_opened):
            return False
            
        try:
            current_file = self.files_opened[index]
            content = current_file['editor'].get('1.0', tk.END + '-1c')
            
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
                
            # Actualizează starea modificată
            current_file['modified'] = False
            title = current_file['title'].rstrip('*')
            self.notebook.tab(index, text=title)
            
            # Actualizează status bar
            self.status_bar_left.config(text=f"Saved: {os.path.basename(file_path)}")
            
            # Actualizează timestamp in status bar
            now = datetime.now().strftime("%H:%M:%S")
            self.status_bar_right.config(text=f"Python {os.path.splitext(file_path)[1]} | {now}")
            
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {str(e)}")
            return False
    
    def close_current_file(self):
        if len(self.files_opened) == 0 or self.current_tab_index >= len(self.files_opened):
            return
            
        current_file = self.files_opened[self.current_tab_index]
        
        # Verifică dacă fișierul a fost modificat
        if current_file['modified']:
            title = current_file['title'].rstrip('*')
            response = messagebox.askyesnocancel("Save Changes", 
                                                f"Do you want to save changes to {title}?")
            if response is None:  # Cancel
                return
            elif response:  # Yes
                if not current_file['path']:
                    file_path = filedialog.asksaveasfilename(
                        defaultextension=".py",
                        filetypes=[("Python files", "*.py"), ("Text files", "*.txt"), ("All files", "*.*")]
                    )
                    if not file_path:
                        return  # Cancel save
                    saved = self.save_to_file(file_path)
                    if not saved:
                        return  # Save failed
                else:
                    saved = self.save_to_file(current_file['path'])
                    if not saved:
                        return  # Save failed
        
        # Închide tab-ul
        self.notebook.forget(self.current_tab_index)
        
        # Elimină din lista de fișiere deschise
        self.files_opened.pop(self.current_tab_index)
        
        # Actualizăm indexul pentru restul tab-urilor
        for i in range(self.current_tab_index, len(self.files_opened)):
            # Actualizează referința la butonul de închidere
            self.files_opened[i]['close_btn'].bind("<Button-1>", lambda e, idx=i: self.close_tab_by_index(idx))
        
        # Deschide un nou tab dacă nu mai există altele
        if len(self.notebook.tabs()) == 0:
            self.create_editor_tab("untitled")
            
        # Actualizează UI
        self.on_tab_changed(None)
    
    def exit_application(self):
        # Verifică fișiere modificate și oferă salvare
        unsaved_files = [f for f in self.files_opened if f['modified']]
        
        if unsaved_files:
            response = messagebox.askyesnocancel("Save Changes", 
                                               f"Save changes to {len(unsaved_files)} files before closing?")
            if response is None:  # Cancel
                return
            elif response:  # Yes
                self.save_all_files()
        
        # Curăță procesele terminalului
        self.cleanup_terminal_process()
        
        # Închide aplicația
        self.root.quit()
    
    def cut_text(self):
        editor = self.get_current_editor()
        if editor:
            if editor.tag_ranges(tk.SEL):
                editor.event_generate("<<Cut>>")
    
    def copy_text(self):
        editor = self.get_current_editor()
        if editor:
            if editor.tag_ranges(tk.SEL):
                editor.event_generate("<<Copy>>")
    
    def paste_text(self):
        editor = self.get_current_editor()
        if editor:
            editor.event_generate("<<Paste>>")
    
    def undo(self):
        editor = self.get_current_editor()
        if editor:
            try:
                editor.edit_undo()
                self.on_text_change(None, editor, self.get_current_line_numbers())
            except tk.TclError:
                pass  # Nu există nimic de undo
    
    def redo(self):
        editor = self.get_current_editor()
        if editor:
            try:
                editor.edit_redo()
                self.on_text_change(None, editor, self.get_current_line_numbers())
            except tk.TclError:
                pass  # Nu există nimic de redo
    
    def find_text(self):
        editor = self.get_current_editor()
        if not editor:
            return
            
        # Verifică dacă există text selectat
        try:
            selected_text = editor.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            selected_text = ""
        
        # Creează dialog de căutare
        find_dialog = tk.Toplevel(self.root)
        find_dialog.title("Find")
        find_dialog.geometry("400x150")
        find_dialog.transient(self.root)
        find_dialog.configure(bg=self.colors['bg'])
        find_dialog.resizable(False, False)
        
        # Variabile pentru căutare
        search_var = tk.StringVar(value=selected_text)
        case_sensitive = tk.BooleanVar(value=False)
        match_whole_word = tk.BooleanVar(value=False)
        use_regex = tk.BooleanVar(value=False)
        
        # Layout
        search_frame = tk.Frame(find_dialog, bg=self.colors['bg'])
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(search_frame, text="Find:", bg=self.colors['bg'], fg=self.colors['text']).pack(side=tk.LEFT, padx=(0, 5))
        search_entry = tk.Entry(search_frame, textvariable=search_var, bg=self.colors['editor_bg'],
                               fg=self.colors['text'], insertbackground=self.colors['text'], width=30)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search_entry.focus_set()
        
        # Opțiuni de căutare
        options_frame = tk.Frame(find_dialog, bg=self.colors['bg'])
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Checkbutton(options_frame, text="Case sensitive", variable=case_sensitive,
                      bg=self.colors['bg'], fg=self.colors['text'], selectcolor=self.colors['editor_bg'],
                      activebackground=self.colors['bg'], activeforeground=self.colors['text']).pack(side=tk.LEFT, padx=5)
        
        tk.Checkbutton(options_frame, text="Match whole word", variable=match_whole_word,
                      bg=self.colors['bg'], fg=self.colors['text'], selectcolor=self.colors['editor_bg'],
                      activebackground=self.colors['bg'], activeforeground=self.colors['text']).pack(side=tk.LEFT, padx=5)
        
        tk.Checkbutton(options_frame, text="Use regex", variable=use_regex,
                      bg=self.colors['bg'], fg=self.colors['text'], selectcolor=self.colors['editor_bg'],
                      activebackground=self.colors['bg'], activeforeground=self.colors['text']).pack(side=tk.LEFT, padx=5)
        
        # Status
        status_var = tk.StringVar()
        status_label = tk.Label(find_dialog, textvariable=status_var, bg=self.colors['bg'], fg=self.colors['text'])
        status_label.pack(fill=tk.X, padx=10, pady=5)
        
        # Butoane
        buttons_frame = tk.Frame(find_dialog, bg=self.colors['bg'])
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def find_next():
            search_term = search_var.get()
            if not search_term:
                status_var.set("Nothing to search for")
                return
                
            # Șterge highlight-uri anterioare
            editor.tag_remove('search', '1.0', tk.END)
            
            # Obține poziția curentă a cursorului
            current_pos = editor.index(tk.INSERT)
            
            # Caută după poziția curentă
            if use_regex.get():
                try:
                    pattern = re.compile(search_term, 0 if case_sensitive.get() else re.IGNORECASE)
                except re.error:
                    status_var.set("Invalid regex pattern")
                    return
                    
                content = editor.get(current_pos, tk.END)
                match = pattern.search(content)
                
                if match:
                    start_idx = editor.index(f"{current_pos}+{match.start()}c")
                    end_idx = editor.index(f"{current_pos}+{match.end()}c")
                    
                    # Verifică whole word dacă este necesar
                    if match_whole_word.get():
                        if (start_idx == "1.0" or not editor.get(f"{start_idx}-1c").isalnum()) and \
                           (end_idx == editor.index(tk.END) or not editor.get(f"{end_idx}").isalnum()):
                            found = True
                        else:
                            found = False
                            start_idx = editor.index(f"{end_idx}")
                    else:
                        found = True
                        
                    if found:
                        editor.tag_add('search', start_idx, end_idx)
                        editor.tag_configure('search', background='#555500', foreground='white')
                        editor.mark_set(tk.INSERT, end_idx)
                        editor.see(start_idx)
                        status_var.set(f"Found match at position {start_idx}")
                        return
                        
                # Nu s-a găsit nimic, începe de la început
                content = editor.get("1.0", current_pos)
                match = pattern.search(content)
                
                if match:
                    start_idx = editor.index(f"1.0+{match.start()}c")
                    end_idx = editor.index(f"1.0+{match.end()}c")
                    
                    # Verifică whole word dacă este necesar
                    if match_whole_word.get():
                        if (start_idx == "1.0" or not editor.get(f"{start_idx}-1c").isalnum()) and \
                           (end_idx == editor.index(tk.END) or not editor.get(f"{end_idx}").isalnum()):
                            found = True
                        else:
                            found = False
                    else:
                        found = True
                        
                    if found:
                        editor.tag_add('search', start_idx, end_idx)
                        editor.tag_configure('search', background='#555500', foreground='white')
                        editor.mark_set(tk.INSERT, end_idx)
                        editor.see(start_idx)
                        status_var.set(f"Found match at position {start_idx} (wrapped search)")
                        return
                        
                status_var.set("No matches found")
            else:
                # Căutare normală
                search_flags = "nocase" if not case_sensitive.get() else ""
                
                if match_whole_word.get():
                    # Adaugă \y pentru a potrivi doar cuvinte întregi
                    search_term = f"\\y{search_term}\\y"
                    
                found_pos = editor.search(search_term, current_pos, tk.END, regexp=match_whole_word.get(), nocase=not case_sensitive.get())
                
                if found_pos:
                    # Calculează poziția de sfârșit
                    if match_whole_word.get() or use_regex.get():
                        # Pentru regex trebuie să determinăm lungimea potrivirii
                        match_length = len(re.search(search_term, editor.get(found_pos, tk.END)).group(0))
                    else:
                        match_length = len(search_term)
                        
                    end_pos = f"{found_pos}+{match_length}c"
                    
                    # Highlight și setează cursor
                    editor.tag_add('search', found_pos, end_pos)
                    editor.tag_configure('search', background='#555500', foreground='white')
                    editor.mark_set(tk.INSERT, end_pos)
                    editor.see(found_pos)
                    status_var.set(f"Found match at position {found_pos}")
                else:
                    # Încearcă de la început
                    found_pos = editor.search(search_term, "1.0", current_pos, regexp=match_whole_word.get(), nocase=not case_sensitive.get())
                    
                    if found_pos:
                        # Calculează poziția de sfârșit
                        if match_whole_word.get() or use_regex.get():
                            # Pentru regex trebuie să determinăm lungimea potrivirii
                            match_length = len(re.search(search_term, editor.get(found_pos, tk.END)).group(0))
                        else:
                            match_length = len(search_term)
                            
                        end_pos = f"{found_pos}+{match_length}c"
                        
                        # Highlight și setează cursor
                        editor.tag_add('search', found_pos, end_pos)
                        editor.tag_configure('search', background='#555500', foreground='white')
                        editor.mark_set(tk.INSERT, end_pos)
                        editor.see(found_pos)
                        status_var.set(f"Found match at position {found_pos} (wrapped search)")
                    else:
                        status_var.set("No matches found")
        
        def find_all():
            search_term = search_var.get()
            if not search_term:
                status_var.set("Nothing to search for")
                return
                
            # Șterge highlight-uri anterioare
            editor.tag_remove('search', '1.0', tk.END)
            
            # Contorizare
            count = 0
            
            if use_regex.get():
                try:
                    pattern = re.compile(search_term, 0 if case_sensitive.get() else re.IGNORECASE)
                except re.error:
                    status_var.set("Invalid regex pattern")
                    return
                    
                content = editor.get("1.0", tk.END)
                
                for match in pattern.finditer(content):
                    start_idx = editor.index(f"1.0+{match.start()}c")
                    end_idx = editor.index(f"1.0+{match.end()}c")
                    
                    # Verifică whole word dacă este necesar
                    if match_whole_word.get():
                        if (start_idx == "1.0" or not editor.get(f"{start_idx}-1c").isalnum()) and \
                           (end_idx == editor.index(tk.END) or not editor.get(f"{end_idx}").isalnum()):
                            editor.tag_add('search', start_idx, end_idx)
                            count += 1
                    else:
                        editor.tag_add('search', start_idx, end_idx)
                        count += 1
            else:
                # Căutare normală
                start_pos = "1.0"
                
                while True:
                    search_flags = "nocase" if not case_sensitive.get() else ""
                    
                    if match_whole_word.get():
                        # Adaugă \y pentru a potrivi doar cuvinte întregi
                        pattern = f"\\y{search_term}\\y"
                        found_pos = editor.search(pattern, start_pos, tk.END, regexp=True, nocase=not case_sensitive.get())
                    else:
                        found_pos = editor.search(search_term, start_pos, tk.END, nocase=not case_sensitive.get())
                    
                    if not found_pos:
                        break
                        
                    # Calculează poziția de sfârșit
                    if match_whole_word.get():
                        # Pentru regex trebuie să determinăm lungimea potrivirii
                        match_length = len(re.search(pattern, editor.get(found_pos, tk.END)).group(0))
                    else:
                        match_length = len(search_term)
                        
                    end_pos = f"{found_pos}+{match_length}c"
                    
                    # Highlight
                    editor.tag_add('search', found_pos, end_pos)
                    count += 1
                    
                    # Actualizează poziția de început pentru următoarea căutare
                    start_pos = end_pos
            
            # Configurare highlight
            editor.tag_configure('search', background='#555500', foreground='white')
            
            # Actualizează status
            if count == 0:
                status_var.set("No matches found")
            else:
                status_var.set(f"Found {count} matches")
        
        # Butoane pentru acțiuni
        find_next_btn = tk.Button(buttons_frame, text="Find Next", command=find_next,
                                 bg=self.colors['sidebar_bg'], fg=self.colors['text'],
                                 activebackground=self.colors['selection'])
        find_next_btn.pack(side=tk.LEFT, padx=5)
        
        find_all_btn = tk.Button(buttons_frame, text="Find All", command=find_all,
                               bg=self.colors['sidebar_bg'], fg=self.colors['text'],
                               activebackground=self.colors['selection'])
        find_all_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = tk.Button(buttons_frame, text="Close", command=find_dialog.destroy,
                            bg=self.colors['sidebar_bg'], fg=self.colors['text'],
                            activebackground=self.colors['selection'])
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        # Key bindings pentru dialog
        find_dialog.bind('<Return>', lambda e: find_next())
        find_dialog.bind('<Escape>', lambda e: find_dialog.destroy())
        
        # Centrare dialog
        find_dialog.update_idletasks()
        width = find_dialog.winfo_width()
        height = find_dialog.winfo_height()
        x = (self.root.winfo_width() // 2) - (width // 2) + self.root.winfo_x()
        y = (self.root.winfo_height() // 2) - (height // 2) + self.root.winfo_y()
        find_dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def replace_text(self):
        editor = self.get_current_editor()
        if not editor:
            return
            
        # Verifică dacă există text selectat
        try:
            selected_text = editor.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            selected_text = ""
        
        # Creează dialog de căutare și înlocuire
        replace_dialog = tk.Toplevel(self.root)
        replace_dialog.title("Replace")
        replace_dialog.geometry("400x200")
        replace_dialog.transient(self.root)
        replace_dialog.configure(bg=self.colors['bg'])
        replace_dialog.resizable(False, False)
        
        # Variabile pentru căutare
        search_var = tk.StringVar(value=selected_text)
        replace_var = tk.StringVar()
        case_sensitive = tk.BooleanVar(value=False)
        match_whole_word = tk.BooleanVar(value=False)
        use_regex = tk.BooleanVar(value=False)
        
        # Layout
        search_frame = tk.Frame(replace_dialog, bg=self.colors['bg'])
        search_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        tk.Label(search_frame, text="Find:", bg=self.colors['bg'], fg=self.colors['text']).pack(side=tk.LEFT, padx=(0, 5))
        search_entry = tk.Entry(search_frame, textvariable=search_var, bg=self.colors['editor_bg'],
                               fg=self.colors['text'], insertbackground=self.colors['text'], width=30)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search_entry.focus_set()
        
        replace_frame = tk.Frame(replace_dialog, bg=self.colors['bg'])
        replace_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(replace_frame, text="Replace:", bg=self.colors['bg'], fg=self.colors['text']).pack(side=tk.LEFT, padx=(0, 5))
        replace_entry = tk.Entry(replace_frame, textvariable=replace_var, bg=self.colors['editor_bg'],
                                fg=self.colors['text'], insertbackground=self.colors['text'], width=30)
        replace_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Opțiuni de căutare
        options_frame = tk.Frame(replace_dialog, bg=self.colors['bg'])
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Checkbutton(options_frame, text="Case sensitive", variable=case_sensitive,
                      bg=self.colors['bg'], fg=self.colors['text'], selectcolor=self.colors['editor_bg'],
                      activebackground=self.colors['bg'], activeforeground=self.colors['text']).pack(side=tk.LEFT, padx=5)
        
        tk.Checkbutton(options_frame, text="Match whole word", variable=match_whole_word,
                      bg=self.colors['bg'], fg=self.colors['text'], selectcolor=self.colors['editor_bg'],
                      activebackground=self.colors['bg'], activeforeground=self.colors['text']).pack(side=tk.LEFT, padx=5)
        
        tk.Checkbutton(options_frame, text="Use regex", variable=use_regex,
                      bg=self.colors['bg'], fg=self.colors['text'], selectcolor=self.colors['editor_bg'],
                      activebackground=self.colors['bg'], activeforeground=self.colors['text']).pack(side=tk.LEFT, padx=5)
        
        # Status
        status_var = tk.StringVar()
        status_label = tk.Label(replace_dialog, textvariable=status_var, bg=self.colors['bg'], fg=self.colors['text'])
        status_label.pack(fill=tk.X, padx=10, pady=5)
        
        # Butoane
        buttons_frame = tk.Frame(replace_dialog, bg=self.colors['bg'])
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def find_next():
            search_term = search_var.get()
            if not search_term:
                status_var.set("Nothing to search for")
                return False
                
            # Șterge highlight-uri anterioare
            editor.tag_remove('search', '1.0', tk.END)
            
            # Obține poziția curentă a cursorului
            current_pos = editor.index(tk.INSERT)
            
            # Caută după poziția curentă
            if use_regex.get():
                try:
                    pattern = re.compile(search_term, 0 if case_sensitive.get() else re.IGNORECASE)
                except re.error:
                    status_var.set("Invalid regex pattern")
                    return False
                    
                content = editor.get(current_pos, tk.END)
                match = pattern.search(content)
                
                if match:
                    start_idx = editor.index(f"{current_pos}+{match.start()}c")
                    end_idx = editor.index(f"{current_pos}+{match.end()}c")
                    
                    # Verifică whole word dacă este necesar
                    if match_whole_word.get():
                        if (start_idx == "1.0" or not editor.get(f"{start_idx}-1c").isalnum()) and \
                           (end_idx == editor.index(tk.END) or not editor.get(f"{end_idx}").isalnum()):
                            found = True
                        else:
                            found = False
                            start_idx = editor.index(f"{end_idx}")
                    else:
                        found = True
                        
                    if found:
                        editor.tag_add('search', start_idx, end_idx)
                        editor.tag_configure('search', background='#555500', foreground='white')
                        editor.mark_set(tk.INSERT, end_idx)
                        editor.see(start_idx)
                        status_var.set(f"Found match at position {start_idx}")
                        return True
                        
                # Nu s-a găsit nimic, începe de la început
                content = editor.get("1.0", current_pos)
                match = pattern.search(content)
                
                if match:
                    start_idx = editor.index(f"1.0+{match.start()}c")
                    end_idx = editor.index(f"1.0+{match.end()}c")
                    
                    # Verifică whole word dacă este necesar
                    if match_whole_word.get():
                        if (start_idx == "1.0" or not editor.get(f"{start_idx}-1c").isalnum()) and \
                           (end_idx == editor.index(tk.END) or not editor.get(f"{end_idx}").isalnum()):
                            found = True
                        else:
                            found = False
                    else:
                        found = True
                        
                    if found:
                        editor.tag_add('search', start_idx, end_idx)
                        editor.tag_configure('search', background='#555500', foreground='white')
                        editor.mark_set(tk.INSERT, end_idx)
                        editor.see(start_idx)
                        status_var.set(f"Found match at position {start_idx} (wrapped search)")
                        return True
                        
                status_var.set("No matches found")
                return False
            else:
                # Căutare normală
                search_flags = "nocase" if not case_sensitive.get() else ""
                
                if match_whole_word.get():
                    # Adaugă \y pentru a potrivi doar cuvinte întregi
                    search_term = f"\\y{search_term}\\y"
                    
                found_pos = editor.search(search_term, current_pos, tk.END, regexp=match_whole_word.get(), nocase=not case_sensitive.get())
                
                if found_pos:
                    # Calculează poziția de sfârșit
                    if match_whole_word.get() or use_regex.get():
                        # Pentru regex trebuie să determinăm lungimea potrivirii
                        match_length = len(re.search(search_term, editor.get(found_pos, tk.END)).group(0))
                    else:
                        match_length = len(search_term)
                        
                    end_pos = f"{found_pos}+{match_length}c"
                    
                    # Highlight și setează cursor
                    editor.tag_add('search', found_pos, end_pos)
                    editor.tag_configure('search', background='#555500', foreground='white')
                    editor.mark_set(tk.INSERT, end_pos)
                    editor.see(found_pos)
                    status_var.set(f"Found match at position {found_pos}")
                    return True
                else:
                    # Încearcă de la început
                    found_pos = editor.search(search_term, "1.0", current_pos, regexp=match_whole_word.get(), nocase=not case_sensitive.get())
                    
                    if found_pos:
                        # Calculează poziția de sfârșit
                        if match_whole_word.get() or use_regex.get():
                            # Pentru regex trebuie să determinăm lungimea potrivirii
                            match_length = len(re.search(search_term, editor.get(found_pos, tk.END)).group(0))
                        else:
                            match_length = len(search_term)
                            
                        end_pos = f"{found_pos}+{match_length}c"
                        
                        # Highlight și setează cursor
                        editor.tag_add('search', found_pos, end_pos)
                        editor.tag_configure('search', background='#555500', foreground='white')
                        editor.mark_set(tk.INSERT, end_pos)
                        editor.see(found_pos)
                        status_var.set(f"Found match at position {found_pos} (wrapped search)")
                        return True
                    else:
                        status_var.set("No matches found")
                        return False
        
        def replace():
            # Înlocuiește textul selectat curent
            try:
                # Verifică dacă există o selecție activă (de la căutarea anterioară)
                if editor.tag_ranges('search'):
                    start = editor.tag_ranges('search')[0]
                    end = editor.tag_ranges('search')[1]
                    
                    # Înlocuiește textul
                    editor.delete(start, end)
                    editor.insert(start, replace_var.get())
                    
                    # Șterge highlight
                    editor.tag_remove('search', '1.0', tk.END)
                    
                    # Găsește următoarea potrivire
                    find_next()
                    
                    status_var.set(f"Replaced text at {start}")
                else:
                    # Dacă nu există o selecție activă, caută prima potrivire
                    if find_next():
                        # Apelează din nou replace pentru a înlocui ce tocmai a fost găsit
                        replace()
            except tk.TclError:
                status_var.set("No text is currently selected")
        
        def replace_all():
            search_term = search_var.get()
            replace_text = replace_var.get()
            
            if not search_term:
                status_var.set("Nothing to search for")
                return
                
            # Șterge highlight-uri anterioare
            editor.tag_remove('search', '1.0', tk.END)
            
            # Contorizare
            count = 0
            
            # Dezactivează undo temporar pentru a grupa toate înlocuirile ca o singură acțiune
            editor.config(autoseparators=False)
            editor.edit_separator()
            
            if use_regex.get():
                try:
                    pattern = re.compile(search_term, 0 if case_sensitive.get() else re.IGNORECASE)
                except re.error:
                    status_var.set("Invalid regex pattern")
                    return
                    
                content = editor.get("1.0", tk.END)
                
                # Dacă este regex, folosește o abordare diferită pentru înlocuire
                if match_whole_word.get():
                    # Cod pentru regex cu match whole word
                    new_content = ""
                    last_end = 0
                    
                    for match in pattern.finditer(content):
                        start, end = match.span()
                        
                        # Verifică dacă e un cuvânt întreg
                        is_word_boundary_start = start == 0 or not content[start-1].isalnum()
                        is_word_boundary_end = end == len(content) or not content[end].isalnum()
                        
                        if is_word_boundary_start and is_word_boundary_end:
                            new_content += content[last_end:start] + replace_text
                            last_end = end
                            count += 1
                    
                    new_content += content[last_end:]
                    
                    # Actualizează conținut
                    editor.delete("1.0", tk.END)
                    editor.insert("1.0", new_content)
                else:
                    # Regex normal fără constrângere de cuvânt întreg
                    new_content = pattern.sub(replace_text, content)
                    
                    # Calculează numărul de înlocuiri
                    count = len(re.findall(pattern, content))
                    
                    # Actualizează conținut
                    editor.delete("1.0", tk.END)
                    editor.insert("1.0", new_content)
            else:
                # Înlocuire normală
                start_pos = "1.0"
                
                while True:
                    if match_whole_word.get():
                        # Adaugă \y pentru a potrivi doar cuvinte întregi
                        pattern = f"\\y{search_term}\\y"
                        found_pos = editor.search(pattern, start_pos, tk.END, regexp=True, nocase=not case_sensitive.get())
                    else:
                        found_pos = editor.search(search_term, start_pos, tk.END, nocase=not case_sensitive.get())
                    
                    if not found_pos:
                        break
                        
                    # Calculează poziția de sfârșit
                    if match_whole_word.get():
                        # Pentru regex trebuie să determinăm lungimea potrivirii
                        match_length = len(re.search(pattern, editor.get(found_pos, tk.END)).group(0))
                    else:
                        match_length = len(search_term)
                        
                    end_pos = f"{found_pos}+{match_length}c"
                    
                    # Înlocuiește text
                    editor.delete(found_pos, end_pos)
                    editor.insert(found_pos, replace_text)
                    count += 1
                    
                    # Actualizează poziția de început pentru următoarea căutare
                    start_pos = f"{found_pos}+{len(replace_text)}c"
            
            # Reactivează undo
            editor.edit_separator()
            editor.config(autoseparators=True)
            
            # Actualizează status
            if count == 0:
                status_var.set("No matches found")
            else:
                status_var.set(f"Replaced {count} occurrences")
                
            # Revalidează highlight syntax după înlocuiri
            self.highlight_syntax(editor)
        
        # Butoane pentru acțiuni
        find_next_btn = tk.Button(buttons_frame, text="Find Next", command=find_next,
                                 bg=self.colors['sidebar_bg'], fg=self.colors['text'],
                                 activebackground=self.colors['selection'])
        find_next_btn.pack(side=tk.LEFT, padx=5)
        
        replace_btn = tk.Button(buttons_frame, text="Replace", command=replace,
                              bg=self.colors['sidebar_bg'], fg=self.colors['text'],
                              activebackground=self.colors['selection'])
        replace_btn.pack(side=tk.LEFT, padx=5)
        
        replace_all_btn = tk.Button(buttons_frame, text="Replace All", command=replace_all,
                                   bg=self.colors['sidebar_bg'], fg=self.colors['text'],
                                   activebackground=self.colors['selection'])
        replace_all_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = tk.Button(buttons_frame, text="Close", command=replace_dialog.destroy,
                            bg=self.colors['sidebar_bg'], fg=self.colors['text'],
                            activebackground=self.colors['selection'])
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        # Key bindings pentru dialog
        replace_dialog.bind('<Return>', lambda e: find_next())
        replace_dialog.bind('<Escape>', lambda e: replace_dialog.destroy())
        
        # Centrare dialog
        replace_dialog.update_idletasks()
        width = replace_dialog.winfo_width()
        height = replace_dialog.winfo_height()
        x = (self.root.winfo_width() // 2) - (width // 2) + self.root.winfo_x()
        y = (self.root.winfo_height() // 2) - (height // 2) + self.root.winfo_y()
        replace_dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def toggle_explorer(self):
        if self.explorer_visible:
            self.sidebar_container.pack_forget()
            self.explorer_visible = False
        else:
            self.sidebar_container.pack(side=tk.LEFT, fill=tk.Y)
            self.explorer_visible = True
    
    def toggle_terminal(self):
        if self.terminal_visible:
            # Dacă închidem terminalul și există un proces rulând, oferă opțiunea de a-l opri
            if self.process is not None and self.process.poll() is None:
                response = messagebox.askyesno("Process Running", 
                                             "There is a process running in the terminal. Stop it?")
                if response:
                    self.cleanup_terminal_process()
            
            self.editor_terminal_paned.forget(self.terminal_frame)
            self.terminal_visible = False
        else:
            self.editor_terminal_paned.add(self.terminal_frame, weight=1)
            self.terminal_visible = True
            
            # Actualizează separatorul
            self.editor_terminal_paned.update_idletasks()
            total_height = self.editor_terminal_paned.winfo_height()
            self.editor_terminal_paned.sashpos(0, int(total_height * 0.7))
            
    def get_current_editor(self):
        if len(self.files_opened) == 0 or self.current_tab_index >= len(self.files_opened):
            return None
        return self.files_opened[self.current_tab_index]['editor']
    
    def get_current_line_numbers(self):
        if len(self.files_opened) == 0 or self.current_tab_index >= len(self.files_opened):
            return None
        return self.files_opened[self.current_tab_index]['line_numbers']
    
    def collect_words_from_file(self, content):
        # Colectează toate cuvintele unice pentru autocompletare
        words = re.findall(r'\b\w+\b', content)
        self.autocomplete_words.update(words)
        
        # Adaugă funcții și clase
        for match in re.finditer(r'def\s+(\w+)', content):
            self.autocomplete_words.add(match.group(1))
        
        for match in re.finditer(r'class\s+(\w+)', content):
            self.autocomplete_words.add(match.group(1))
    
    def show_autocomplete(self, event, editor):
        # Verifică dacă s-a tastat "."
        cursor_pos = editor.index(tk.INSERT)
        line, column = map(int, cursor_pos.split('.'))
        
        # Obține cuvântul înainte de "."
        line_content = editor.get(f"{line}.0", f"{line}.{column}")
        match = re.search(r'(\w+)\.', line_content)
        
        if match:
            obj_name = match.group(1)
            # Aici ar trebui să determinăm membrii obiectului, pentru simplitate
            # vom oferi câteva metode comune pentru tipurile de bază Python
            
            if obj_name in ['str', 'list', 'dict', 'set', 'int', 'float']:
                methods = self.get_type_methods(obj_name)
            else:
                # Pentru alte obiecte, oferă sugestii generale
                methods = ['__init__', '__str__', '__repr__', 'append', 'extend', 'insert', 'remove',
                         'pop', 'clear', 'index', 'count', 'sort', 'reverse', 'copy', 'keys', 
                         'values', 'items', 'get', 'update', 'add', 'lower', 'upper', 'strip', 
                         'split', 'join', 'replace', 'find', 'format']
            
            # Creează lista de sugestii
            self.show_completion_window(editor, methods)
    
    def get_type_methods(self, obj_type):
        # Dicționar cu metode comune pentru tipurile de bază Python
        type_methods = {
            'str': ['capitalize', 'casefold', 'center', 'count', 'encode', 'endswith', 'expandtabs',
                   'find', 'format', 'format_map', 'index', 'isalnum', 'isalpha', 'isascii',
                   'isdecimal', 'isdigit', 'isidentifier', 'islower', 'isnumeric', 'isprintable',
                   'isspace', 'istitle', 'isupper', 'join', 'ljust', 'lower', 'lstrip', 'maketrans',
                   'partition', 'replace', 'rfind', 'rindex', 'rjust', 'rpartition', 'rsplit',
                   'rstrip', 'split', 'splitlines', 'startswith', 'strip', 'swapcase', 'title',
                   'translate', 'upper', 'zfill'],
            'list': ['append', 'clear', 'copy', 'count', 'extend', 'index', 'insert', 'pop', 'remove',
                    'reverse', 'sort'],
            'dict': ['clear', 'copy', 'fromkeys', 'get', 'items', 'keys', 'pop', 'popitem',
                    'setdefault', 'update', 'values'],
            'set': ['add', 'clear', 'copy', 'difference', 'difference_update', 'discard',
                   'intersection', 'intersection_update', 'isdisjoint', 'issubset', 'issuperset',
                   'pop', 'remove', 'symmetric_difference', 'symmetric_difference_update', 'union',
                   'update'],
            'int': ['as_integer_ratio', 'bit_length', 'conjugate', 'from_bytes', 'to_bytes'],
            'float': ['as_integer_ratio', 'conjugate', 'fromhex', 'hex', 'is_integer']
        }
        
        return type_methods.get(obj_type, [])
    
    def show_completion_window(self, editor, suggestions):
        # Obține poziția cursor
        cursor_pos = editor.index(tk.INSERT)
        x, y, width, height = editor.bbox(cursor_pos)
        
        # Coordonate absolute
        x += editor.winfo_rootx()
        y += editor.winfo_rooty() + height
        
        # Creează fereastra de completare
        completion_window = tk.Toplevel(self.root)
        completion_window.wm_overrideredirect(True)
        completion_window.wm_geometry(f"+{x}+{y}")
        completion_window.configure(bg=self.colors['bg'])
        
        # Creează un frame pentru conținut
        frame = tk.Frame(completion_window, bg=self.colors['bg'], bd=1, relief=tk.SOLID)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Listbox pentru sugestii
        listbox = tk.Listbox(frame, bg=self.colors['editor_bg'], fg=self.colors['text'],
                            font=('Consolas', 10), height=min(10, len(suggestions)),
                            selectbackground=self.colors['selection'], bd=0)
        listbox.pack(fill=tk.BOTH, expand=True)
        
        # Adaugă sugestiile sortate alfabetic
        for item in sorted(suggestions):
            listbox.insert(tk.END, item)
        
        # Selectează primul item
        if listbox.size() > 0:
            listbox.selection_set(0)
            listbox.activate(0)
        
        # Funcție pentru a insera textul selectat
        def insert_selection(event=None):
            if listbox.curselection():
                selected_item = listbox.get(listbox.curselection())
                editor.insert(tk.INSERT, selected_item)
                completion_window.destroy()
                return "break"  # Previne procesarea ulterioară a evenimentului
        
        # Funcție pentru a naviga prin listă
        def navigate(event):
            selection = listbox.curselection()
            if selection:
                index = selection[0]
                if event.keysym == 'Up' and index > 0:
                    listbox.selection_clear(0, tk.END)
                    listbox.selection_set(index - 1)
                    listbox.activate(index - 1)
                    listbox.see(index - 1)
                elif event.keysym == 'Down' and index < listbox.size() - 1:
                    listbox.selection_clear(0, tk.END)
                    listbox.selection_set(index + 1)
                    listbox.activate(index + 1)
                    listbox.see(index + 1)
            return "break"  # Previne procesarea ulterioară a evenimentului
        
        # Binding-uri pentru taste
        listbox.bind('<Return>', insert_selection)
        listbox.bind('<Double-Button-1>', insert_selection)
        listbox.bind('<Escape>', lambda e: completion_window.destroy())
        listbox.bind('<Up>', navigate)
        listbox.bind('<Down>', navigate)
        
        # Binding pentru a închide fereastra când se pierde focus-ul
        def on_focus_out(event):
            completion_window.destroy()
        
        completion_window.bind('<FocusOut>', on_focus_out)
        
        # Focus pe listbox
        listbox.focus_set()
    
    def comment_line(self):
        editor = self.get_current_editor()
        if not editor:
            return
            
        # Verifică dacă există selecție
        try:
            start_line = int(editor.index(tk.SEL_FIRST).split('.')[0])
            end_line = int(editor.index(tk.SEL_LAST).split('.')[0])
            has_selection = True
        except tk.TclError:
            # Nu există selecție, folosește linia curentă
            cursor_pos = editor.index(tk.INSERT)
            start_line = end_line = int(cursor_pos.split('.')[0])
            has_selection = False
        
        # Verifică dacă liniile sunt deja comentate
        all_commented = True
        for line in range(start_line, end_line + 1):
            line_content = editor.get(f"{line}.0", f"{line}.end")
            if line_content.strip() and not line_content.lstrip().startswith('#'):
                all_commented = False
                break
        
        # Comentează sau decomentează liniile
        for line in range(start_line, end_line + 1):
            line_content = editor.get(f"{line}.0", f"{line}.end")
            if not line_content.strip():
                continue  # Sari liniile goale
                
            if all_commented:
                # Decomentează
                if line_content.lstrip().startswith('#'):
                    # Găsește poziția primului #
                    hash_pos = line_content.find('#')
                    # Verifică dacă este urmat de un spațiu
                    if hash_pos + 1 < len(line_content) and line_content[hash_pos + 1] == ' ':
                        editor.delete(f"{line}.{hash_pos}", f"{line}.{hash_pos + 2}")
                    else:
                        editor.delete(f"{line}.{hash_pos}", f"{line}.{hash_pos + 1}")
            else:
                # Comentează
                indent = len(line_content) - len(line_content.lstrip())
                editor.insert(f"{line}.{indent}", "# ")
        
        # Actualizează highlight
        self.highlight_syntax(editor)
    
    def indent(self):
        editor = self.get_current_editor()
        if not editor:
            return
            
        # Verifică dacă există selecție
        try:
            start_line = int(editor.index(tk.SEL_FIRST).split('.')[0])
            end_line = int(editor.index(tk.SEL_LAST).split('.')[0])
            has_selection = True
        except tk.TclError:
            # Nu există selecție, folosește linia curentă
            cursor_pos = editor.index(tk.INSERT)
            start_line = end_line = int(cursor_pos.split('.')[0])
            has_selection = False
        
        # Adaugă indentare la fiecare linie
        editor.config(autoseparators=False)
        editor.edit_separator()
        
        for line in range(start_line, end_line + 1):
            editor.insert(f"{line}.0", "    ")
        
        editor.edit_separator()
        editor.config(autoseparators=True)
        
        # Actualizează highlight
        self.highlight_syntax(editor)
    
    def dedent(self):
        editor = self.get_current_editor()
        if not editor:
            return
            
        # Verifică dacă există selecție
        try:
            start_line = int(editor.index(tk.SEL_FIRST).split('.')[0])
            end_line = int(editor.index(tk.SEL_LAST).split('.')[0])
            has_selection = True
        except tk.TclError:
            # Nu există selecție, folosește linia curentă
            cursor_pos = editor.index(tk.INSERT)
            start_line = end_line = int(cursor_pos.split('.')[0])
            has_selection = False
        
        # Dedentează fiecare linie
        editor.config(autoseparators=False)
        editor.edit_separator()
        
        for line in range(start_line, end_line + 1):
            line_content = editor.get(f"{line}.0", f"{line}.end")
            
            # Verifică dacă există cel puțin 4 spații (sau 1 tab) la începutul liniei
            if line_content.startswith('    '):
                editor.delete(f"{line}.0", f"{line}.4")
            elif line_content.startswith('\t'):
                editor.delete(f"{line}.0", f"{line}.1")
            elif line_content.startswith(' '):
                # Dedentează cu numărul de spații disponibile (maxim 4)
                spaces = len(line_content) - len(line_content.lstrip(' '))
                if spaces > 0:
                    editor.delete(f"{line}.0", f"{line}.{min(spaces, 4)}")
        
        editor.edit_separator()
        editor.config(autoseparators=True)
        
        # Actualizează highlight
        self.highlight_syntax(editor)
    
    def handle_tab(self, event, editor):
        try:
            # Verifică dacă există o selecție
            sel_start = editor.index(tk.SEL_FIRST)
            sel_end = editor.index(tk.SEL_LAST)
            
            # Există selecție, aplică indentare pe mai multe linii
            start_line = int(sel_start.split('.')[0])
            end_line = int(sel_end.split('.')[0])
            
            # Verifică dacă selecția se întinde pe mai multe linii
            if start_line != end_line:
                self.indent()
                return "break"
        except tk.TclError:
            # Nu există selecție, folosește comportamentul normal (inserează un tab/spații)
            editor.insert(tk.INSERT, "    ")
            return "break"
    
    def auto_close_bracket(self, event, editor, opening, closing):
        # Adaugă automat închiderea parantezei, ghilimelei etc.
        editor.insert(tk.INSERT, closing)
        editor.mark_set(tk.INSERT, "insert-1c")  # Mută cursorul înapoi cu o poziție
        return "break"
    
    def auto_indent_after_colon(self, event, editor):
        # Auto-indentare după ":" în Python
        cursor_pos = editor.index(tk.INSERT)
        line, col = cursor_pos.split('.')
        
        # Verifică dacă ":" este la sfârșitul unei linii care conține cuvinte cheie Python
        line_content = editor.get(f"{line}.0", f"{line}.{col}")
        
        # Verifică dacă linia conține un keyword care ar trebui să ducă la indentare
        contains_indent_keyword = any(kw in line_content for kw in 
                                     ['if ', 'else:', 'elif ', 'for ', 'while ', 'def ', 'class ', 'try:', 'except ', 'finally:'])
        
        if contains_indent_keyword and line_content.rstrip().endswith(':'):
            # Verifică dacă cursorul este la sfârșitul liniei
            is_end_of_line = editor.get(cursor_pos, f"{line}.end").strip() == ""
            
            if is_end_of_line:
                # Adaugă o nouă linie indentată automat
                current_indent = len(line_content) - len(line_content.lstrip())
                new_indent = current_indent + 4
                editor.insert(cursor_pos, f"\n{' ' * new_indent}")
                return "break"
    
    def auto_indent(self, event, editor):
        # Auto-indentare după Enter
        cursor_pos = editor.index(tk.INSERT)
        line, col = cursor_pos.split('.')
        prev_line = int(line) - 1
        
        if prev_line > 0:
            # Obține indentarea liniei anterioare
            prev_line_content = editor.get(f"{prev_line}.0", f"{prev_line}.end")
            indent = len(prev_line_content) - len(prev_line_content.lstrip())
            
            # Verifică dacă linia anterioară se termină cu ":"
            if prev_line_content.rstrip().endswith(':'):
                # Adaugă indentare suplimentară pentru blocuri noi
                indent += 4
            
            # Adaugă indentarea
            editor.insert(cursor_pos, ' ' * indent)
    
    def zoom_in(self):
        # Mărire font
        editor = self.get_current_editor()
        if not editor:
            return
            
        font_obj = font.Font(font=editor['font'])
        current_size = font_obj.actual('size')
        
        if current_size < 36:  # Limită superioară pentru font
            new_size = current_size + 1
            new_font = (font_obj.actual('family'), new_size)
            
            # Actualizează font pentru toți editorii
            for file_info in self.files_opened:
                file_info['editor'].configure(font=new_font)
                file_info['line_numbers'].configure(font=new_font)
    
    def zoom_out(self):
        # Micșorare font
        editor = self.get_current_editor()
        if not editor:
            return
            
        font_obj = font.Font(font=editor['font'])
        current_size = font_obj.actual('size')
        
        if current_size > 6:  # Limită inferioară pentru font
            new_size = current_size - 1
            new_font = (font_obj.actual('family'), new_size)
            
            # Actualizează font pentru toți editorii
            for file_info in self.files_opened:
                file_info['editor'].configure(font=new_font)
                file_info['line_numbers'].configure(font=new_font)
    
    '''
    def run_python_file(self):
        # Rulează fișierul Python curent
        if len(self.files_opened) == 0 or self.current_tab_index >= len(self.files_opened):
            return
            
        current_file = self.files_opened[self.current_tab_index]
        
        # Dacă fișierul nu a fost salvat, încearcă să-l salvezi mai întâi
        if current_file['modified'] or not current_file['path']:
            if not current_file['path']:
                # Solicită salvarea fișierului
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".py",
                    filetypes=[("Python files", "*.py"), ("All files", "*.*")]
                )
                if not file_path:
                    messagebox.showwarning("Run Error", "Cannot run unsaved file. Please save the file first.")
                    return
                
                self.save_to_file(file_path)
                current_file['path'] = file_path
                current_file['title'] = os.path.basename(file_path)
                current_file['modified'] = False
                self.notebook.tab(self.current_tab_index, text=current_file['title'])
            else:
                # Salvează fișierul existent
                self.save_file()
        
        # Asigură-te că terminalul este vizibil
        if not self.terminal_visible:
            self.toggle_terminal()
        
        # Oprește orice proces anterior
        self.cleanup_terminal_process()
        
        # Curăță terminalul
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.delete('1.0', tk.END)
        self.terminal_output.insert(tk.END, f"Running {os.path.basename(current_file['path'])}...\n")
        self.terminal_output.insert(tk.END, "=" * 50 + "\n\n")
        self.terminal_output.see(tk.END)
        self.terminal_output.config(state=tk.DISABLED)
        
        # Activează input field-ul
        self.terminal_input.config(state=tk.NORMAL)
        
        # Determină comanda Python
        python_cmd = "python" if platform.system() == "Windows" else "python3"
        
        try:
            # Creează procesul ca un cmd pe Windows sau un terminal pe Unix
            if platform.system() == "Windows":
                # Folosește cmd.exe pentru a rula Python interactiv
                cmd = f'cmd.exe /c {python_cmd} "{current_file["path"]}"'
                
                # Folosește STARTUPINFO pentru a ascunde fereastra cmd
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                # Creează procesul cu toate fluxurile conectate și fără buffering
                self.process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    shell=True,
                    universal_newlines=True,
                    startupinfo=startupinfo,
                    bufsize=0,
                    encoding='utf-8',
                    errors='replace',
                    env=dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONUNBUFFERED='1')
                )
            else:
                # Pe Unix, folosim direct comanda Python
                self.process = subprocess.Popen(
                    [python_cmd, current_file['path']],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=0,
                    encoding='utf-8',
                    errors='replace',
                    env=dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONUNBUFFERED='1')
                )
            
            # Thread pentru a citi stdout
            def read_stdout():
                while self.process and self.process.poll() is None:
                    try:
                        # Citim un singur caracter pentru a evita blocarea
                        char = self.process.stdout.read(1)
                        if char:
                            self.terminal_output.config(state=tk.NORMAL)
                            self.terminal_output.insert(tk.END, char)
                            self.terminal_output.see(tk.END)
                            self.terminal_output.config(state=tk.DISABLED)
                            self.root.update_idletasks()
                    except (IOError, OSError):
                        break
                    except Exception as e:
                        print(f"Stdout error: {e}")
                        break
            
            # Thread pentru a citi stderr
            def read_stderr():
                while self.process and self.process.poll() is None:
                    try:
                        # Citim un singur caracter pentru a evita blocarea
                        char = self.process.stderr.read(1)
                        if char:
                            self.terminal_output.config(state=tk.NORMAL)
                            self.terminal_output.insert(tk.END, char, "error")
                            self.terminal_output.see(tk.END)
                            self.terminal_output.config(state=tk.DISABLED)
                            self.root.update_idletasks()
                    except (IOError, OSError):
                        break
                    except Exception as e:
                        print(f"Stderr error: {e}")
                        break
            
            # Thread pentru a monitoriza terminarea procesului
            def monitor_process():
                if self.process:
                    return_code = self.process.wait()
                    
                    # Dacă thread-urile au fost oprite, nu mai continua
                    if self.stop_threads.is_set():
                        return
                    
                    self.terminal_output.config(state=tk.NORMAL)
                    self.terminal_output.insert(tk.END, f"\n\n{'='*50}\n")
                    self.terminal_output.insert(tk.END, f"[Process completed with exit code {return_code}]")
                    if return_code == 0:
                        self.terminal_output.insert(tk.END, "\n[Program finished successfully]")
                    else:
                        self.terminal_output.insert(tk.END, f"\n[Program finished with errors]", "error")
                        
                    self.terminal_output.insert(tk.END, "\n[Terminal input disabled. Run another program to continue.]\n")
                    self.terminal_output.see(tk.END)
                    self.terminal_output.config(state=tk.DISABLED)
                    
                    # Dezactivează input field-ul
                    self.terminal_input.config(state=tk.DISABLED)
                    
                    # Actualizează statusbar
                    self.status_bar_left.config(text="Ready")
            
            # Pornește thread-urile
            stdout_thread = threading.Thread(target=read_stdout, daemon=True)
            stderr_thread = threading.Thread(target=read_stderr, daemon=True)
            monitor_thread = threading.Thread(target=monitor_process, daemon=True)
            
            stdout_thread.start()
            stderr_thread.start()
            monitor_thread.start()
            
            self.terminal_threads = [stdout_thread, stderr_thread, monitor_thread]
            
            # Focalizează pe input
            self.terminal_input.focus_set()
            
        except Exception as e:
            self.terminal_output.config(state=tk.NORMAL)
            self.terminal_output.insert(tk.END, f"Error running program: {str(e)}\n", "error")
            self.terminal_output.see(tk.END)
            self.terminal_output.config(state=tk.DISABLED)
        
        # Actualizează statusbar
        self.status_bar_left.config(text=f"Running: {os.path.basename(current_file['path'])}")
    '''
    
    def run_python_file(self):
        # Rulează fișierul Python curent
        if len(self.files_opened) == 0 or self.current_tab_index >= len(self.files_opened):
            return
            
        current_file = self.files_opened[self.current_tab_index]
        
        # Dacă fișierul nu a fost salvat, încearcă să-l salvezi mai întâi
        if current_file['modified'] or not current_file['path']:
            if not current_file['path']:
                # Solicită salvarea fișierului
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".py",
                    filetypes=[("Python files", "*.py"), ("All files", "*.*")]
                )
                if not file_path:
                    messagebox.showwarning("Run Error", "Cannot run unsaved file. Please save the file first.")
                    return
                
                self.save_to_file(file_path)
                current_file['path'] = file_path
                current_file['title'] = os.path.basename(file_path)
                current_file['modified'] = False
                self.notebook.tab(self.current_tab_index, text=current_file['title'])
            else:
                # Salvează fișierul existent
                self.save_file()
        
        # Asigură-te că terminalul este vizibil
        if not self.terminal_visible:
            self.toggle_terminal()
        
        # Oprește orice proces anterior
        self.cleanup_terminal_process()
        
        # Curăță terminalul
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.delete('1.0', tk.END)
        self.terminal_output.insert(tk.END, f"Running {os.path.basename(current_file['path'])}...\n")
        self.terminal_output.insert(tk.END, f"Type input in the field below whenever the program waits for input.\n")
        self.terminal_output.insert(tk.END, "=" * 50 + "\n\n")
        self.terminal_output.see(tk.END)
        self.terminal_output.config(state=tk.DISABLED)
        
        # Activează input field-ul
        self.terminal_input.config(state=tk.NORMAL)
        self.terminal_input.focus_set()
        
        # Resetează starea
        self.awaiting_input = False
        
        try:
            # Determină comanda Python corectă utilizând executabilul Python actual
            python_cmd = sys.executable
            
            # Creează procesul ca un cmd pe Windows sau un terminal pe Unix cu suport pentru input interactiv
            if platform.system() == "Windows":
                # Setăm variabile de mediu pentru a asigura comportamentul corect Python
                env_vars = dict(os.environ)
                env_vars['PYTHONIOENCODING'] = 'utf-8'
                env_vars['PYTHONUNBUFFERED'] = '1'
                
                # Folosește cmd.exe pentru a rula Python interactiv
                cmd = f'cmd.exe /c {python_cmd} "{current_file["path"]}"'
                
                # Folosește STARTUPINFO pentru a ascunde fereastra cmd
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                # Creează procesul cu toate fluxurile conectate și fără buffering
                self.process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    shell=True,
                    universal_newlines=True,
                    startupinfo=startupinfo,
                    bufsize=0,  # Fără buffering
                    encoding='utf-8',
                    errors='replace',
                    env=env_vars
                )
            else:
                # Pe Unix, folosim direct comanda Python
                env_vars = dict(os.environ)
                env_vars['PYTHONIOENCODING'] = 'utf-8'
                env_vars['PYTHONUNBUFFERED'] = '1'
                
                self.process = subprocess.Popen(
                    [python_cmd, current_file['path']],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=0,  # Fără buffering
                    encoding='utf-8',
                    errors='replace',
                    env=env_vars
                )
            
            # Thread pentru a citi stdout caracter cu caracter
            def read_stdout():
                while self.process and self.process.poll() is None and not self.stop_threads.is_set():
                    try:
                        # Citim un singur caracter pentru a evita blocarea și a detecta mai repede prompturile de input
                        char = self.process.stdout.read(1)
                        if char:
                            self.terminal_output.config(state=tk.NORMAL)
                            self.terminal_output.insert(tk.END, char)
                            self.terminal_output.see(tk.END)
                            self.terminal_output.config(state=tk.DISABLED)
                            self.root.update_idletasks()
                            
                            # Detectează prompt-urile de input specifice 
                            # (verifică dacă ultimul caracter sau ultimele caractere sugerează un prompt de input)
                            last_line = self.terminal_output.get("end-2l", "end-1c")
                            if last_line.rstrip().endswith((':', '?', '>>>')) or "input" in last_line.lower():
                                self.terminal_input.focus_set()
                                self.awaiting_input = True
                    except (IOError, OSError):
                        break
                    except Exception as e:
                        print(f"Stdout error: {e}")
                        break
                    
                    # Mică pauză pentru a evita consumul excesiv de CPU
                    time.sleep(0.001)
            
            # Thread pentru a citi stderr caracter cu caracter
            def read_stderr():
                while self.process and self.process.poll() is None and not self.stop_threads.is_set():
                    try:
                        # Citim un singur caracter pentru a evita blocarea
                        char = self.process.stderr.read(1)
                        if char:
                            self.terminal_output.config(state=tk.NORMAL)
                            self.terminal_output.insert(tk.END, char, "error")
                            self.terminal_output.see(tk.END)
                            self.terminal_output.config(state=tk.DISABLED)
                            self.root.update_idletasks()
                    except (IOError, OSError):
                        break
                    except Exception as e:
                        print(f"Stderr error: {e}")
                        break
                    
                    # Mică pauză pentru a evita consumul excesiv de CPU
                    time.sleep(0.001)
            
            # Thread pentru a monitoriza terminarea procesului
            def monitor_process():
                if self.process:
                    return_code = self.process.wait()
                    
                    # Dacă thread-urile au fost oprite, nu mai continua
                    if self.stop_threads.is_set():
                        return
                    
                    # Așteaptă puțin pentru a se asigura că tot output-ul a fost procesat
                    time.sleep(0.2)
                    
                    # Afișează mesajul de finalizare
                    self.terminal_output.config(state=tk.NORMAL)
                    self.terminal_output.insert(tk.END, f"\n\n{'='*50}\n")
                    self.terminal_output.insert(tk.END, f"[Process completed with exit code {return_code}]")
                    if return_code == 0:
                        self.terminal_output.insert(tk.END, "\n[Program finished successfully]")
                    else:
                        self.terminal_output.insert(tk.END, f"\n[Program finished with errors]", "error")
                        
                    self.terminal_output.insert(tk.END, "\n[Terminal input disabled. Run another program to continue.]\n")
                    self.terminal_output.see(tk.END)
                    self.terminal_output.config(state=tk.DISABLED)
                    
                    # Dezactivează input field-ul
                    self.terminal_input.config(state=tk.DISABLED)
                    
                    # Actualizează statusbar
                    self.status_bar_left.config(text="Ready")
                    
                    # Resetează starea procesului
                    self.process = None
                    self.awaiting_input = False
            
            # Pornește thread-urile
            stdout_thread = threading.Thread(target=read_stdout, daemon=True)
            stderr_thread = threading.Thread(target=read_stderr, daemon=True)
            monitor_thread = threading.Thread(target=monitor_process, daemon=True)
            
            stdout_thread.start()
            stderr_thread.start()
            monitor_thread.start()
            
            self.terminal_threads = [stdout_thread, stderr_thread, monitor_thread]
            
        except Exception as e:
            self.terminal_output.config(state=tk.NORMAL)
            self.terminal_output.insert(tk.END, f"Error running program: {str(e)}\n", "error")
            self.terminal_output.see(tk.END)
            self.terminal_output.config(state=tk.DISABLED)
        
        # Actualizează statusbar
        self.status_bar_left.config(text=f"Running: {os.path.basename(current_file['path'])}")
    
    def cleanup_terminal_process(self):
        """Oprește procesul curent și thread-urile asociate"""
        # Semnalează thread-urilor să se oprească
        self.stop_threads.set()
        
        # Oprește procesul
        if self.process is not None:
            try:
                # Închide stdin înainte de a termina procesul pentru a evita erori EOF
                if hasattr(self.process, 'stdin') and self.process.stdin:
                    try:
                        self.process.stdin.close()
                    except:
                        pass
                    
                # Așteaptă puțin înainte de a termina procesul
                time.sleep(0.1)
                
                # Încearcă să termine procesul normal
                self.process.terminate()
                
                # Așteaptă puțin pentru terminare normală
                for _ in range(5):  # Încearcă de 5 ori cu un mic delay
                    if self.process.poll() is not None:
                        break  # Procesul s-a terminat
                    time.sleep(0.1)
                    
                # Dacă procesul încă rulează, forțează închiderea
                if self.process.poll() is None:
                    self.process.kill()
            except:
                pass
            finally:
                self.process = None
        
        # Așteaptă oprirea thread-urilor (dar nu prea mult)
        for thread in self.terminal_threads:
            if thread.is_alive():
                thread.join(timeout=0.5)
        
        # Curăță lista de thread-uri
        self.terminal_threads.clear()
        
        # Resetează flag-ul pentru thread-uri
        self.stop_threads.clear()
        
        # Resetează starea
        self.awaiting_input = False
        self.last_output_incomplete = False
        
        # Dezactivează input field-ul
        self.terminal_input.config(state=tk.DISABLED)
        self.terminal_input.delete(0, tk.END)
    
    def read_output_to_queue(self, pipe, output_queue):
        """Citește output-ul din pipe și îl pune într-o coadă"""
        for line in iter(pipe.readline, ''):
            if self.stop_threads.is_set():
                break
            output_queue.put(line)
        
        try:
            pipe.close()
        except:
            pass

    def update_terminal_from_queue(self):
        """Actualizează terminalul din cozile de output - versiune simplificată"""
        while not self.stop_threads.is_set():
            output_processed = False
            
            # Procesează output-ul standard
            try:
                while not self.output_queue.empty():
                    line = self.output_queue.get_nowait()
                    self.terminal_output.config(state=tk.NORMAL)
                    self.terminal_output.insert(tk.END, line)
                    self.terminal_output.see(tk.END)
                    self.terminal_output.config(state=tk.DISABLED)
                    self.root.update_idletasks()
                    output_processed = True
            except queue.Empty:
                pass
            
            # Procesează erorile
            try:
                while not self.error_queue.empty():
                    line = self.error_queue.get_nowait()
                    self.terminal_output.config(state=tk.NORMAL)
                    self.terminal_output.insert(tk.END, line, "error")
                    self.terminal_output.see(tk.END)
                    self.terminal_output.config(state=tk.DISABLED)
                    self.root.update_idletasks()
                    output_processed = True
            except queue.Empty:
                pass
            
            # Scurtă pauză pentru a nu supraîncărca CPU
            time.sleep(0.05)
            
    def check_for_input_state(self):
        """Verifică dacă procesul așteaptă input de la utilizator"""
        if not self.process or self.process.poll() is not None:
            return
            
        # Verifică dacă avem output nou
        if not self.output_queue.empty() or not self.error_queue.empty():
            return
            
        # Verifică dacă procesul este blocat așteptând input
        # (Nu avem output nou și procesul încă rulează)
        current_time = time.time()
        if hasattr(self, 'last_output_time') and (current_time - self.last_output_time) > 0.5:
            # Procesul probabil așteaptă input
            if not self.awaiting_input:
                self.awaiting_input = True
                self.terminal_input.config(state=tk.NORMAL)
                self.terminal_input.focus_set()
            
    def monitor_process_completion(self):
        """Monitorizează finalizarea procesului"""
        if not self.process:
            return
            
        # Așteaptă finalizarea procesului
        return_code = self.process.wait()
        
        # Dacă thread-urile au fost oprite, nu mai continua
        if self.stop_threads.is_set():
            return
        
        # Așteaptă puțin să se proceseze toate output-urile
        time.sleep(0.2)
        
        # Afișează un mesaj despre terminarea procesului
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.insert(tk.END, f"\n{'='*50}\n")
        self.terminal_output.insert(tk.END, f"[Process completed with exit code {return_code}]")
        if return_code == 0:
            self.terminal_output.insert(tk.END, "\n[Program finished successfully]")
        else:
            self.terminal_output.insert(tk.END, f"\n[Program finished with errors]", "error")
            
        self.terminal_output.insert(tk.END, "\n[Terminal input disabled. Run another program to continue.]\n")
        self.terminal_output.see(tk.END)
        self.terminal_output.config(state=tk.DISABLED)
        
        # Dezactivează input field-ul
        self.terminal_input.config(state=tk.DISABLED)
        self.terminal_input.delete(0, tk.END)
        
        self.root.update_idletasks()
        
        # Actualizează statusbar
        self.status_bar_left.config(text="Ready")
        
        # Curăță starea complet
        self.process = None
        self.awaiting_input = False
        self.last_output_incomplete = False

        # Asigură-te că terminalul este vizibil
        if not self.terminal_visible:
            self.toggle_terminal()
        
        # Oprește orice proces anterior
        self.cleanup_terminal_process()
        
        # Curăță terminalul
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.delete('1.0', tk.END)
        self.terminal_output.insert(tk.END, f"Running {os.path.basename(current_file['path'])}...\n")
        self.terminal_output.insert(tk.END, "=" * 50 + "\n\n")
        self.terminal_output.see(tk.END)
        self.terminal_output.config(state=tk.DISABLED)
        
        # Activează input field-ul
        self.terminal_input.config(state=tk.NORMAL)
        
        # Determină comanda Python
        python_cmd = "python" if platform.system() == "Windows" else "python3"
        
        try:
            # Folosește PIPE pentru stdin, stdout și stderr
            self.process = subprocess.Popen(
                [python_cmd, current_file['path']],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=0,
                encoding='utf-8',
                errors='replace',
                env=dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONUNBUFFERED='1')
            )
            
            # Setează flag-ul pentru a indica că procesul rulează
            self.process_running = True
            
            # Thread pentru a citi output-ul
            def read_output():
                # Folosim un buffer pentru a colecta caractere până la o linie completă
                stdout_buffer = ""
                stderr_buffer = ""
                
                while self.process_running and self.process and self.process.poll() is None:
                    # Verifică dacă există date disponibile pentru citire
                    r_list = []
                    if self.process.stdout:
                        r_list.append(self.process.stdout)
                    if self.process.stderr:
                        r_list.append(self.process.stderr)
                    
                    if not r_list:
                        time.sleep(0.05)
                        continue
                    
                    # Folosim select pentru a verifica care stream are date disponibile
                    # Timeout de 0.1 secunde pentru a nu bloca thread-ul
                    try:
                        ready, _, _ = select.select(r_list, [], [], 0.1)
                        
                        for stream in ready:
                            if stream == self.process.stdout:
                                # Citim o linie sau bucăți din stdout
                                char = stream.read(1)
                                if char:
                                    # Afișează caracterul imediat
                                    self.terminal_output.config(state=tk.NORMAL)
                                    self.terminal_output.insert(tk.END, char)
                                    self.terminal_output.see(tk.END)
                                    self.terminal_output.config(state=tk.DISABLED)
                                    self.root.update_idletasks()
                            
                            elif stream == self.process.stderr:
                                # Citim o linie sau bucăți din stderr
                                char = stream.read(1)
                                if char:
                                    # Afișează caracterul imediat ca eroare
                                    self.terminal_output.config(state=tk.NORMAL)
                                    self.terminal_output.insert(tk.END, char, "error")
                                    self.terminal_output.see(tk.END)
                                    self.terminal_output.config(state=tk.DISABLED)
                                    self.root.update_idletasks()
                    except (OSError, IOError, ValueError) as e:
                        # Eroare la select sau stream închis
                        break
                    except Exception as e:
                        # Afișăm eroarea și continuăm
                        print(f"Error reading output: {e}")
                        time.sleep(0.1)
                
                # Procesul s-a terminat sau a fost oprit
                if self.process:
                    # Încercăm să citim orice output rămas
                    try:
                        # Dăm un timeout scurt pentru communicate pentru a evita blocarea
                        stdout, stderr = self.process.communicate(timeout=0.5)
                        
                        if stdout:
                            self.terminal_output.config(state=tk.NORMAL)
                            self.terminal_output.insert(tk.END, stdout)
                            self.terminal_output.config(state=tk.DISABLED)
                        
                        if stderr:
                            self.terminal_output.config(state=tk.NORMAL)
                            self.terminal_output.insert(tk.END, stderr, "error")
                            self.terminal_output.config(state=tk.DISABLED)
                    except subprocess.TimeoutExpired:
                        # Dacă timeout expiră, continuăm oricum
                        pass
                    except Exception as e:
                        print(f"Error collecting remaining output: {e}")
            
            # Thread pentru a monitoriza terminarea procesului
            def monitor_process():
                if self.process:
                    return_code = self.process.wait()
                    
                    # Setează flag-ul pentru a opri citirea output-ului
                    self.process_running = False
                    
                    # Dacă thread-urile au fost oprite, nu mai continua
                    if self.stop_threads.is_set():
                        return
                    
                    # Așteaptă puțin să se proceseze tot output-ul rămas
                    time.sleep(0.2)
                    
                    # Afișează mesajul de finalizare
                    self.terminal_output.config(state=tk.NORMAL)
                    self.terminal_output.insert(tk.END, f"\n\n{'='*50}\n")
                    self.terminal_output.insert(tk.END, f"[Process completed with exit code {return_code}]")
                    if return_code == 0:
                        self.terminal_output.insert(tk.END, "\n[Program finished successfully]")
                    else:
                        self.terminal_output.insert(tk.END, f"\n[Program finished with errors]", "error")
                        
                    self.terminal_output.insert(tk.END, "\n[Terminal input disabled. Run another program to continue.]\n")
                    self.terminal_output.see(tk.END)
                    self.terminal_output.config(state=tk.DISABLED)
                    
                    # Dezactivează input field-ul
                    self.terminal_input.config(state=tk.DISABLED)
                    
                    # Actualizează statusbar
                    self.status_bar_left.config(text="Ready")
            
            # Import necesar pentru select
            import select
            
            # Inițializează flag-ul pentru procesul care rulează
            self.process_running = True
            
            # Pornește thread-urile
            output_thread = threading.Thread(target=read_output, daemon=True)
            monitor_thread = threading.Thread(target=monitor_process, daemon=True)
            
            output_thread.start()
            monitor_thread.start()
            
            self.terminal_threads = [output_thread, monitor_thread]
            
            # Focalizează pe input
            self.terminal_input.focus_set()
            
        except Exception as e:
            self.terminal_output.config(state=tk.NORMAL)
            self.terminal_output.insert(tk.END, f"Error running program: {str(e)}\n", "error")
            self.terminal_output.see(tk.END)
            self.terminal_output.config(state=tk.DISABLED)
        
        # Actualizează statusbar
        self.status_bar_left.config(text=f"Running: {os.path.basename(current_file['path'])}")
    
    def debug_python_file(self):
        # Simulare debug pentru fișierul Python curent
        if len(self.files_opened) == 0 or self.current_tab_index >= len(self.files_opened):
            return
            
        current_file = self.files_opened[self.current_tab_index]
        
        # Dacă fișierul nu a fost salvat, încearcă să-l salvezi mai întâi
        if current_file['modified'] or not current_file['path']:
            if not current_file['path']:
                messagebox.showwarning("Debug Error", "Cannot debug unsaved file. Please save the file first.")
                return
            else:
                self.save_file()
        
        # Afișează un dialog pentru simularea debugging
        debug_dialog = tk.Toplevel(self.root)
        debug_dialog.title("Debug Mode")
        debug_dialog.geometry("400x300")
        debug_dialog.transient(self.root)
        debug_dialog.configure(bg=self.colors['bg'])
        
        # Mesaj informativ
        tk.Label(debug_dialog, text=f"Debugging {os.path.basename(current_file['path'])}", 
               bg=self.colors['bg'], fg=self.colors['text'], font=('Consolas', 12, 'bold')).pack(pady=10)
        
        tk.Label(debug_dialog, text="Debug features:\n\n• Breakpoints\n• Variable inspection\n• Step-by-step execution\n• Call stack viewing", 
               bg=self.colors['bg'], fg=self.colors['text'], justify=tk.LEFT).pack(pady=10, padx=20, anchor='w')
        
        tk.Label(debug_dialog, text="This is a simulated debug interface.\nIn a full implementation, this would launch pdb or a visual debugger.", 
               bg=self.colors['bg'], fg=self.colors['text']).pack(pady=10)
        
        # Buton pentru închidere
        tk.Button(debug_dialog, text="Close", command=debug_dialog.destroy,
                bg=self.colors['sidebar_bg'], fg=self.colors['text'],
                activebackground=self.colors['selection']).pack(pady=20)
    
    def run(self):
        # Adaugă conținut de demonstrație în primul editor
        demo_content = '''# VS Code Python Editor
# Tema Dark activată!

def hello_world():
    """Funcție de demonstrație cu highlight de sintaxă"""
    name = "Python Developer"
    age = 25
    print(f"Hello, {name}! You are {age} years old.")
    
    # Aceasta este o listă
    languages = ["Python", "JavaScript", "C++", "Java"]
    
    for lang in languages:
        print(f"I love {lang}!")
    
    return True

class ExampleClass:
    """O clasă de exemplu pentru demonstrație"""
    
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        """Metoda de salut"""
        return f"Hello from {self.name}!"

if __name__ == "__main__":
    # Punct de intrare pentru program
    result = hello_world()
    print(f"Function returned: {result}")
    
    # Creăm o instanță a clasei
    example = ExampleClass("VS Code Editor")
    print(example.greet())
'''
        # Actualizează conținutul primului editor
        current_editor = self.get_current_editor()
        if current_editor:
            current_editor.delete('1.0', tk.END)
            current_editor.insert('1.0', demo_content)
            self.on_text_change(None, current_editor, self.get_current_line_numbers())
            
            # Colectează cuvinte pentru autocompletare din conținutul demo
            self.collect_words_from_file(demo_content)
        
        # Actualizează statusbar
        self.status_bar_left.config(text="Ready")
        
        # Afișează terminalul inițial și apoi îl ascunde pentru mai mult spațiu
        self.toggle_terminal()
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.delete('1.0', tk.END)
        self.terminal_output.insert(tk.END, "Terminal ready. Run your Python script using F5 or the Run menu.\n")
        self.terminal_output.insert(tk.END, "Input is disabled until you run a program.\n")
        self.terminal_output.config(state=tk.DISABLED)
        # Dezactivează input field-ul inițial
        self.terminal_input.config(state=tk.DISABLED)
        # Ascunde terminalul inițial pentru a avea mai mult spațiu pentru editor
        self.toggle_terminal()
        
        # Configurare pentru a reține dimensiunea ferestrei
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        self.root.minsize(800, 600)
        
        # Centrează fereastra pe ecran
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Pornește mainloop
        self.root.mainloop()

if __name__ == "__main__":
    editor = VSCodeEditor()
    editor.run()