import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, font
from tkinter.scrolledtext import ScrolledText
import os
import re
import webbrowser
import pygments
from pygments.lexers import get_lexer_by_name, get_all_lexers
from pygments.styles import get_all_styles
from pygments.token import Token

class LineNumberedText(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent)
        self.text = ScrolledText(self, *args, **kwargs)
        self.line_numbers = tk.Text(self, width=4, padx=4, bg='#f0f0f0', bd=0,
                               highlightthickness=0, takefocus=0)
        self.line_numbers.tag_configure('line_numbers', justify='right')
        
        self.text.grid(row=0, column=1, sticky="nsew")
        self.line_numbers.grid(row=0, column=0, sticky="nsew")
        
        self.text.bind('<KeyRelease>', self.on_key_release)
        self.text.bind('<ButtonRelease-1>', self.on_key_release)
        self.text.bind('<MouseWheel>', self.on_key_release)
        self.text.bind('<Configure>', self.on_key_release)
        
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Initial line numbers update
        self.on_key_release()
        
    def on_key_release(self, event=None):
        self.update_line_numbers()
        
    def update_line_numbers(self):
        line_count = self.text.get('1.0', tk.END).count('\n')
        if line_count <= 0:
            line_count = 1
            
        line_number_content = '\n'.join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete('1.0', tk.END)
        self.line_numbers.insert('1.0', line_number_content)
        self.line_numbers.config(state=tk.DISABLED)
        
        # Sync scrolling
        self.line_numbers.yview_moveto(self.text.yview()[0])
        
    def highlight_line(self, line_number, bg_color='#e0e0e0'):
        self.text.tag_remove('active_line', '1.0', tk.END)
        self.text.tag_add('active_line', f'{line_number}.0', f'{line_number + 1}.0')
        self.text.tag_config('active_line', background=bg_color)

class SyntaxHighlighter:
    def __init__(self, text_widget):
        self.text = text_widget
        self.current_lexer = None
        self.current_style = 'default'
        self.token_tags = {}
        self._setup_tags()
        
    def _setup_tags(self):
        # Configure tags for different token types
        self.token_tags = {
            Token.Keyword: 'keyword',
            Token.String: 'string',
            Token.Name.Function: 'function',
            Token.Name.Class: 'class',
            Token.Comment: 'comment',
            Token.Number: 'number',
            Token.Operator: 'operator',
            Token.Name.Builtin: 'builtin',
            Token.Literal: 'literal',
            Token.String.Doc: 'docstring',
            Token.Name.Decorator: 'decorator',
        }
        
        # Default styling
        self.text.tag_configure('keyword', foreground='#0000FF', font=('Courier New', 10, 'bold'))
        self.text.tag_configure('string', foreground='#A31515')
        self.text.tag_configure('function', foreground='#795E26')
        self.text.tag_configure('class', foreground='#267f99', font=('Courier New', 10, 'bold'))
        self.text.tag_configure('comment', foreground='#008000', font=('Courier New', 10, 'italic'))
        self.text.tag_configure('number', foreground='#098658')
        self.text.tag_configure('operator', foreground='#000000')
        self.text.tag_configure('builtin', foreground='#0000FF')
        self.text.tag_configure('literal', foreground='#A31515')
        self.text.tag_configure('docstring', foreground='#008000', font=('Courier New', 10, 'italic'))
        self.text.tag_configure('decorator', foreground='#AF00DB')
    
    def set_lexer(self, language):
        try:
            self.current_lexer = get_lexer_by_name(language)
            return True
        except pygments.util.ClassNotFound:
            self.current_lexer = None
            return False
    
    def set_style(self, style_name):
        try:
            style = pygments.styles.get_style_by_name(style_name)
            self.current_style = style_name
            
            # Update tag configurations based on the style
            for token_type, tag_name in self.token_tags.items():
                if token_type in style:
                    style_attrs = style.style_for_token(token_type)
                    fg = style_attrs['color']
                    bg = style_attrs['bgcolor']
                    bold = style_attrs['bold']
                    italic = style_attrs['italic']
                    
                    kwargs = {}
                    if fg:
                        kwargs['foreground'] = f'#{fg}'
                    if bg:
                        kwargs['background'] = f'#{bg}'
                        
                    font_style = ('Courier New', 10)
                    if bold and italic:
                        font_style = ('Courier New', 10, 'bold italic')
                    elif bold:
                        font_style = ('Courier New', 10, 'bold')
                    elif italic:
                        font_style = ('Courier New', 10, 'italic')
                        
                    kwargs['font'] = font_style
                    self.text.tag_configure(tag_name, **kwargs)
            
            return True
        except pygments.util.ClassNotFound:
            return False
    
    def highlight(self):
        if not self.current_lexer:
            return
            
        # Remove all existing tags
        for tag in self.token_tags.values():
            self.text.tag_remove(tag, '1.0', tk.END)
            
        # Get text content
        content = self.text.get('1.0', tk.END)
        
        # Tokenize text using pygments
        tokens = pygments.lex(content, self.current_lexer)
        
        # Apply tags for each token
        pos = 0
        for token_type, value in tokens:
            # Find all token types that match
            for token_pattern, tag_name in self.token_tags.items():
                if token_type in token_pattern:
                    start_index = f"1.0+{pos}c"
                    end_index = f"1.0+{pos + len(value)}c"
                    self.text.tag_add(tag_name, start_index, end_index)
                    break
            pos += len(value)


class FindReplaceDialog(tk.Toplevel):
    def __init__(self, parent, text_widget):
        super().__init__(parent)
        self.text = text_widget
        self.title("Find & Replace")
        self.geometry("400x150")
        self.resizable(False, False)
        
        # Variables
        self.find_var = tk.StringVar()
        self.replace_var = tk.StringVar()
        self.case_sensitive_var = tk.BooleanVar()
        self.whole_word_var = tk.BooleanVar()
        self.regex_var = tk.BooleanVar()
        
        # Create UI
        ttk.Label(self, text="Find:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self, textvariable=self.find_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self, text="Replace:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self, textvariable=self.replace_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        options_frame = ttk.Frame(self)
        options_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        ttk.Checkbutton(options_frame, text="Case sensitive", variable=self.case_sensitive_var).pack(side=tk.LEFT)
        ttk.Checkbutton(options_frame, text="Whole word", variable=self.whole_word_var).pack(side=tk.LEFT)
        ttk.Checkbutton(options_frame, text="Regular expression", variable=self.regex_var).pack(side=tk.LEFT)
        
        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Find Next", command=self.find_next).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Replace", command=self.replace).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Replace All", command=self.replace_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=self.destroy).pack(side=tk.LEFT, padx=5)
        
        self.last_search_pos = "1.0"
        self.found_items = []
        self.current_match = -1
        
    def find_next(self):
        search_str = self.find_var.get()
        if not search_str:
            return
            
        start_pos = self.text.index(tk.INSERT)
        
        # Remove previous highlights
        self.text.tag_remove('search_highlight', '1.0', tk.END)
        
        search_kwargs = {"nocase": not self.case_sensitive_var.get()}
        
        if self.regex_var.get():
            # Use regex search
            content = self.text.get('1.0', tk.END)
            flags = 0 if self.case_sensitive_var.get() else re.IGNORECASE
            try:
                pattern = re.compile(search_str, flags)
                matches = list(pattern.finditer(content))
                
                if not matches:
                    messagebox.showinfo("Find", "No match found")
                    return
                
                self.found_items = []
                for match in matches:
                    start_idx = f"1.0+{match.start()}c"
                    end_idx = f"1.0+{match.end()}c"
                    self.found_items.append((start_idx, end_idx))
                    self.text.tag_add('search_highlight', start_idx, end_idx)
                
                self.current_match = (self.current_match + 1) % len(self.found_items)
                self.text.tag_config('search_highlight', background='yellow')
                self.text.see(self.found_items[self.current_match][0])
                self.text.mark_set(tk.INSERT, self.found_items[self.current_match][0])
                
            except re.error as e:
                messagebox.showerror("Regex Error", f"Invalid regular expression: {e}")
        else:
            # Use normal search
            found_pos = self.text.search(search_str, start_pos, **search_kwargs)
            if not found_pos:
                # Try from the beginning if not found
                found_pos = self.text.search(search_str, '1.0', **search_kwargs)
                
            if not found_pos:
                messagebox.showinfo("Find", "No match found")
                return
                
            end_pos = f"{found_pos}+{len(search_str)}c"
            self.text.tag_add('search_highlight', found_pos, end_pos)
            self.text.tag_config('search_highlight', background='yellow')
            self.text.see(found_pos)
            self.text.mark_set(tk.INSERT, found_pos)
            self.last_search_pos = end_pos
    
    def replace(self):
        search_str = self.find_var.get()
        replace_str = self.replace_var.get()
        
        if not search_str:
            return
            
        # First find the current occurrence
        self.find_next()
        
        # Then replace if found
        try:
            sel_start = self.text.index(tk.SEL_FIRST)
            sel_end = self.text.index(tk.SEL_LAST)
            self.text.delete(sel_start, sel_end)
            self.text.insert(sel_start, replace_str)
        except tk.TclError:
            # No selection, do nothing
            pass
    
    def replace_all(self):
        search_str = self.find_var.get()
        replace_str = self.replace_var.get()
        
        if not search_str:
            return
            
        # Start from the beginning
        self.text.mark_set(tk.INSERT, '1.0')
        count = 0
        
        if self.regex_var.get():
            # Use regex replace all
            content = self.text.get('1.0', tk.END)
            flags = 0 if self.case_sensitive_var.get() else re.IGNORECASE
            try:
                pattern = re.compile(search_str, flags)
                new_content, count = pattern.subn(replace_str, content)
                if count > 0:
                    self.text.delete('1.0', tk.END)
                    self.text.insert('1.0', new_content)
                messagebox.showinfo("Replace All", f"{count} occurrences replaced")
            except re.error as e:
                messagebox.showerror("Regex Error", f"Invalid regular expression: {e}")
        else:
            # Use normal search and replace
            search_kwargs = {"nocase": not self.case_sensitive_var.get()}
            current_pos = '1.0'
            
            while True:
                found_pos = self.text.search(search_str, current_pos, tk.END, **search_kwargs)
                if not found_pos:
                    break
                    
                end_pos = f"{found_pos}+{len(search_str)}c"
                self.text.delete(found_pos, end_pos)
                self.text.insert(found_pos, replace_str)
                current_pos = f"{found_pos}+{len(replace_str)}c"
                count += 1
                
            messagebox.showinfo("Replace All", f"{count} occurrences replaced")


class ThemeManager:
    def __init__(self, editor):
        self.editor = editor
        self.current_theme = "default"
        
        # Define themes
        self.themes = {
            "default": {
                "background": "#FFFFFF",
                "foreground": "#000000",
                "line_numbers_bg": "#F0F0F0",
                "line_numbers_fg": "#000000",
                "cursor": "#000000",
                "selection_bg": "#ADD6FF",
                "active_line_bg": "#E8F2FE",
                "font": ("Courier New", 10),
            },
            "dark": {
                "background": "#1E1E1E",
                "foreground": "#D4D4D4",
                "line_numbers_bg": "#252526",
                "line_numbers_fg": "#858585",
                "cursor": "#AEAFAD",
                "selection_bg": "#264F78",
                "active_line_bg": "#282828",
                "font": ("Courier New", 10),
            },
            "monokai": {
                "background": "#272822",
                "foreground": "#F8F8F2",
                "line_numbers_bg": "#3E3D32",
                "line_numbers_fg": "#90908A",
                "cursor": "#F8F8F0",
                "selection_bg": "#49483E",
                "active_line_bg": "#3E3D32",
                "font": ("Courier New", 10),
            },
            "solarized_light": {
                "background": "#FDF6E3",
                "foreground": "#657B83",
                "line_numbers_bg": "#EEE8D5",
                "line_numbers_fg": "#839496",
                "cursor": "#586E75",
                "selection_bg": "#EEE8D5",
                "active_line_bg": "#EEE8D5",
                "font": ("Courier New", 10),
            },
            "solarized_dark": {
                "background": "#002B36",
                "foreground": "#839496",
                "line_numbers_bg": "#073642",
                "line_numbers_fg": "#586E75",
                "cursor": "#93A1A1",
                "selection_bg": "#073642",
                "active_line_bg": "#073642",
                "font": ("Courier New", 10),
            }
        }
    
    def apply_theme(self, theme_name):
        if theme_name not in self.themes:
            return False
            
        theme = self.themes[theme_name]
        self.current_theme = theme_name
        
        # Apply theme to text editor
        self.editor.text.config(
            background=theme["background"],
            foreground=theme["foreground"],
            insertbackground=theme["cursor"],
            selectbackground=theme["selection_bg"],
            font=theme["font"]
        )
        
        # Apply theme to line numbers
        self.editor.line_numbers.config(
            background=theme["line_numbers_bg"],
            foreground=theme["line_numbers_fg"],
            font=theme["font"]
        )
        
        # Apply theme to active line highlighting
        self.editor.text.tag_config('active_line', background=theme["active_line_bg"])
        
        return True
    
    def add_custom_theme(self, name, settings):
        self.themes[name] = settings
        
    def get_theme_names(self):
        return list(self.themes.keys())


class AdvancedNotepad:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Advanced Notepad")
        self.root.geometry("1000x600")
        
        # Set application icon
        try:
            self.root.iconbitmap("notepad.ico")  # Replace with your icon file
        except:
            pass  # Ignore if icon file is not found
            
        # Initialize variables
        self.current_file = None
        self.modified = False
        
        # Create main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the editor with line numbers
        self.editor = LineNumberedText(self.main_frame)
        self.editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Set font
        default_font = font.Font(family="Courier New", size=10)
        self.editor.text.configure(font=default_font, wrap=tk.NONE, undo=True)
        
        # Initialize syntax highlighter
        self.syntax_highlighter = SyntaxHighlighter(self.editor.text)
        self.syntax_highlighter.set_lexer("python")  # Default to Python syntax
        
        # Initialize theme manager
        self.theme_manager = ThemeManager(self.editor)
        self.theme_manager.apply_theme("default")
        
        # Create menu bar - moved after theme_manager initialization
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create status bar
        self.status_bar = ttk.Frame(root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_text = ttk.Label(self.status_bar, text="Line: 1, Col: 0")
        self.status_text.pack(side=tk.LEFT, padx=5)
        
        self.language_label = ttk.Label(self.status_bar, text="Python")
        self.language_label.pack(side=tk.RIGHT, padx=5)
        
        # Bind events
        self.editor.text.bind("<KeyRelease>", self.on_key_release)
        self.editor.text.bind("<ButtonRelease-1>", self.update_status_bar)
        self.editor.text.bind("<Control-f>", self.show_find_dialog)
        self.editor.text.bind("<Control-h>", self.show_find_dialog)
        self.editor.text.bind("<Control-s>", self.save_file)
        self.editor.text.bind("<Control-o>", self.open_file)
        self.editor.text.bind("<Control-n>", self.new_file)
        self.editor.text.bind("<Control-w>", self.close_file)
        
        # Initial status bar update
        self.update_status_bar()
        
        # Set focus to the editor
        self.editor.text.focus_set()
        
    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", accelerator="Ctrl+N", command=self.new_file)
        file_menu.add_command(label="Open", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=lambda: self.editor.text.event_generate("<<Undo>>"))
        edit_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=lambda: self.editor.text.event_generate("<<Redo>>"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", accelerator="Ctrl+X", command=lambda: self.editor.text.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", accelerator="Ctrl+C", command=lambda: self.editor.text.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", accelerator="Ctrl+V", command=lambda: self.editor.text.event_generate("<<Paste>>"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Find/Replace", accelerator="Ctrl+F", command=self.show_find_dialog)
        edit_menu.add_command(label="Select All", accelerator="Ctrl+A", command=lambda: self.editor.text.tag_add(tk.SEL, "1.0", tk.END))
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        
        # Language submenu
        language_menu = tk.Menu(view_menu, tearoff=0)
        languages = sorted([lexer[0] for lexer in get_all_lexers()])
        
        # Add common languages first
        common_languages = ['Python', 'Java', 'JavaScript', 'HTML', 'CSS', 'C', 'C++', 'C#', 'PHP', 'Ruby', 'SQL', 'XML']
        for lang in common_languages:
            language_menu.add_command(label=lang, command=lambda l=lang: self.set_language(l))
            
        language_menu.add_separator()
        
        # Add all other languages
        for lang in languages:
            if lang not in common_languages:
                language_menu.add_command(label=lang, command=lambda l=lang: self.set_language(l))
        
        view_menu.add_cascade(label="Language", menu=language_menu)
        
        # Theme submenu
        theme_menu = tk.Menu(view_menu, tearoff=0)
        for theme in self.theme_manager.get_theme_names():
            theme_menu.add_command(label=theme.replace('_', ' ').title(), 
                                 command=lambda t=theme: self.set_theme(t))
        
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        view_menu.add_separator()
        
        # Font submenu
        font_menu = tk.Menu(view_menu, tearoff=0)
        font_menu.add_command(label="Font Settings", command=self.change_font)
        view_menu.add_cascade(label="Font", menu=font_menu)
        
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Word Count", command=self.word_count)
        tools_menu.add_command(label="Character Count", command=self.character_count)
        tools_menu.add_separator()
        tools_menu.add_command(label="Convert to Uppercase", command=self.convert_to_uppercase)
        tools_menu.add_command(label="Convert to Lowercase", command=self.convert_to_lowercase)
        tools_menu.add_command(label="Convert Tabs to Spaces", command=self.convert_tabs_to_spaces)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_toolbar(self):
        toolbar_frame = ttk.Frame(self.root)
        toolbar_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(toolbar_frame, text="New", command=self.new_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Open", command=self.open_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Save", command=self.save_file).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        ttk.Button(toolbar_frame, text="Cut", command=lambda: self.editor.text.event_generate("<<Cut>>")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Copy", command=lambda: self.editor.text.event_generate("<<Copy>>")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Paste", command=lambda: self.editor.text.event_generate("<<Paste>>")).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        ttk.Button(toolbar_frame, text="Find", command=self.show_find_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Word Count", command=self.word_count).pack(side=tk.LEFT, padx=2)
    
    def on_key_release(self, event=None):
        self.update_status_bar()
        self.highlight_current_line()
        
        # Apply syntax highlighting
        if hasattr(self, 'syntax_highlighter') and self.syntax_highlighter.current_lexer:
            self.syntax_highlighter.highlight()
            
        # Mark as modified
        if not self.modified and event and event.char:
            self.modified = True
            self.update_title()
    
    def update_status_bar(self, event=None):
        cursor_position = self.editor.text.index(tk.INSERT)
        line, col = cursor_position.split('.')
        self.status_text.config(text=f"Line: {line}, Col: {col}")
    
    def highlight_current_line(self):
        cursor_position = self.editor.text.index(tk.INSERT)
        line = cursor_position.split('.')[0]
        self.editor.highlight_line(int(line))
    
    def update_title(self):
        filename = os.path.basename(self.current_file) if self.current_file else "Untitled"
        modified_indicator = "*" if self.modified else ""
        self.root.title(f"{filename}{modified_indicator} - Python Advanced Notepad")
    
    def new_file(self, event=None):
        if self.modified:
            if not messagebox.askyesno("Unsaved Changes", "You have unsaved changes. Do you want to continue?"):
                return
                
        self.editor.text.delete('1.0', tk.END)
        self.current_file = None
        self.modified = False
        self.update_title()
        return "break"  # Prevent default behavior
    
    def open_file(self, event=None):
        if self.modified:
            if not messagebox.askyesno("Unsaved Changes", "You have unsaved changes. Do you want to continue?"):
                return "break"
                
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("All Files", "*.*"),
                ("Text Files", "*.txt"),
                ("Python Files", "*.py"),
                ("HTML Files", "*.html"),
                ("CSS Files", "*.css"),
                ("JavaScript Files", "*.js"),
                ("XML Files", "*.xml"),
                ("JSON Files", "*.json"),
                ("Markdown Files", "*.md"),
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                self.editor.text.delete('1.0', tk.END)
                self.editor.text.insert('1.0', content)
                self.current_file = file_path
                self.modified = False
                self.update_title()
                
                # Detect language based on file extension
                extension = os.path.splitext(file_path)[1].lower()
                if extension == '.py':
                    self.set_language('Python')
                elif extension == '.html':
                    self.set_language('HTML')
                elif extension == '.css':
                    self.set_language('CSS')
                elif extension == '.js':
                    self.set_language('JavaScript')
                elif extension == '.xml':
                    self.set_language('XML')
                elif extension == '.json':
                    self.set_language('JSON')
                elif extension == '.md':
                    self.set_language('Markdown')
                    
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")
                
        return "break"  # Prevent default behavior
    
    def save_file(self, event=None):
        if not self.current_file:
            return self.save_as_file()
            
        try:
            with open(self.current_file, 'w', encoding='utf-8') as file:
                file.write(self.editor.text.get('1.0', tk.END))
            self.modified = False
            self.update_title()
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")
            
        return "break"  # Prevent default behavior
    
    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("All Files", "*.*"),
                ("Text Files", "*.txt"),
                ("Python Files", "*.py"),
                ("HTML Files", "*.html"),
                ("CSS Files", "*.css"),
                ("JavaScript Files", "*.js"),
                ("XML Files", "*.xml"),
                ("JSON Files", "*.json"),
                ("Markdown Files", "*.md"),
            ]
        )
        
        if file_path:
            self.current_file = file_path
            self.save_file()
            
            # Detect language based on file extension
            extension = os.path.splitext(file_path)[1].lower()
            if extension == '.py':
                self.set_language('Python')
            elif extension == '.html':
                self.set_language('HTML')
            elif extension == '.css':
                self.set_language('CSS')
            elif extension == '.js':
                self.set_language('JavaScript')
            elif extension == '.xml':
                self.set_language('XML')
            elif extension == '.json':
                self.set_language('JSON')
            elif extension == '.md':
                self.set_language('Markdown')
                
        return "break"  # Prevent default behavior
    
    def close_file(self, event=None):
        if self.modified:
            if not messagebox.askyesno("Unsaved Changes", "You have unsaved changes. Do you want to continue?"):
                return "break"
                
        self.editor.text.delete('1.0', tk.END)
        self.current_file = None
        self.modified = False
        self.update_title()
        return "break"  # Prevent default behavior
    
    def exit_app(self):
        if self.modified:
            if not messagebox.askyesno("Unsaved Changes", "You have unsaved changes. Do you want to exit?"):
                return
        self.root.destroy()
    
    def show_find_dialog(self, event=None):
        FindReplaceDialog(self.root, self.editor.text)
        return "break"  # Prevent default behavior
    
    def set_language(self, language):
        language_map = {
            'Python': 'python',
            'Java': 'java',
            'JavaScript': 'javascript',
            'HTML': 'html',
            'CSS': 'css',
            'C': 'c',
            'C++': 'cpp',
            'C#': 'csharp',
            'PHP': 'php',
            'Ruby': 'ruby',
            'SQL': 'sql',
            'XML': 'xml',
            'JSON': 'json',
            'Markdown': 'markdown',
        }
        
        lexer_name = language_map.get(language, language.lower())
        
        if self.syntax_highlighter.set_lexer(lexer_name):
            self.language_label.config(text=language)
            self.syntax_highlighter.highlight()
        else:
            messagebox.showwarning("Language Support", f"Syntax highlighting for {language} is not available.")
    
    def set_theme(self, theme_name):
        self.theme_manager.apply_theme(theme_name)
        # Re-apply syntax highlighting
        self.syntax_highlighter.highlight()
    
    def change_font(self):
        current_font = font.Font(font=self.editor.text['font'])
        font_dialog = tk.Toplevel(self.root)
        font_dialog.title("Font Settings")
        font_dialog.geometry("300x200")
        font_dialog.resizable(False, False)
        
        ttk.Label(font_dialog, text="Family:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Get system fonts
        font_families = sorted(list(font.families()))
        family_var = tk.StringVar(value=current_font.actual()['family'])
        family_combo = ttk.Combobox(font_dialog, textvariable=family_var, values=font_families, width=20)
        family_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(font_dialog, text="Size:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        size_var = tk.IntVar(value=current_font.actual()['size'])
        size_combo = ttk.Combobox(font_dialog, textvariable=size_var, values=list(range(8, 25)), width=5)
        size_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Bold and italic checkboxes
        bold_var = tk.BooleanVar(value='bold' in current_font.actual()['weight'])
        italic_var = tk.BooleanVar(value='italic' in current_font.actual()['slant'])
        
        ttk.Checkbutton(font_dialog, text="Bold", variable=bold_var).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Checkbutton(font_dialog, text="Italic", variable=italic_var).grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # Preview
        preview_frame = ttk.LabelFrame(font_dialog, text="Preview")
        preview_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        preview_text = tk.Text(preview_frame, height=3, width=30)
        preview_text.insert('1.0', "AaBbCcXxYyZz 123456")
        preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        def update_preview():
            weight = 'bold' if bold_var.get() else 'normal'
            slant = 'italic' if italic_var.get() else 'roman'
            preview_font = font.Font(family=family_var.get(), size=size_var.get(), weight=weight, slant=slant)
            preview_text.configure(font=preview_font)
            
        family_combo.bind("<<ComboboxSelected>>", lambda e: update_preview())
        size_combo.bind("<<ComboboxSelected>>", lambda e: update_preview())
        bold_var.trace_add("write", lambda *args: update_preview())
        italic_var.trace_add("write", lambda *args: update_preview())
        
        update_preview()  # Initial preview update
        
        def apply_font():
            weight = 'bold' if bold_var.get() else 'normal'
            slant = 'italic' if italic_var.get() else 'roman'
            new_font = font.Font(family=family_var.get(), size=size_var.get(), weight=weight, slant=slant)
            self.editor.text.configure(font=new_font)
            self.editor.line_numbers.configure(font=new_font)
            font_dialog.destroy()
            
        button_frame = ttk.Frame(font_dialog)
        button_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Apply", command=apply_font).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=font_dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def word_count(self):
        text = self.editor.text.get('1.0', tk.END)
        words = len(text.split())
        lines = len(text.splitlines())
        chars = len(text)
        messagebox.showinfo("Statistics", f"Words: {words}\nLines: {lines}\nCharacters: {chars}")
    
    def character_count(self):
        text = self.editor.text.get('1.0', tk.END)
        chars = len(text) - 1  # Subtract one for the final newline
        chars_no_spaces = len(text.replace(" ", "").replace("\n", "").replace("\t", ""))
        messagebox.showinfo("Character Count", f"Characters (with spaces): {chars}\nCharacters (without spaces): {chars_no_spaces}")
    
    def convert_to_uppercase(self):
        try:
            if self.editor.text.tag_ranges(tk.SEL):
                selected_text = self.editor.text.get(tk.SEL_FIRST, tk.SEL_LAST)
                self.editor.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
                self.editor.text.insert(tk.INSERT, selected_text.upper())
        except tk.TclError:
            # No selection, convert all text
            text = self.editor.text.get('1.0', tk.END)
            self.editor.text.delete('1.0', tk.END)
            self.editor.text.insert('1.0', text.upper())
    
    def convert_to_lowercase(self):
        try:
            if self.editor.text.tag_ranges(tk.SEL):
                selected_text = self.editor.text.get(tk.SEL_FIRST, tk.SEL_LAST)
                self.editor.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
                self.editor.text.insert(tk.INSERT, selected_text.lower())
        except tk.TclError:
            # No selection, convert all text
            text = self.editor.text.get('1.0', tk.END)
            self.editor.text.delete('1.0', tk.END)
            self.editor.text.insert('1.0', text.lower())
    
    def convert_tabs_to_spaces(self):
        text = self.editor.text.get('1.0', tk.END)
        text = text.replace("\t", "    ")  # Replace tabs with 4 spaces
        self.editor.text.delete('1.0', tk.END)
        self.editor.text.insert('1.0', text)
    
    def show_about(self):
        about_dialog = tk.Toplevel(self.root)
        about_dialog.title("About Python Advanced Notepad")
        about_dialog.geometry("400x300")
        about_dialog.resizable(False, False)
        
        about_text = """Python Advanced Notepad

Version 1.0

A feature-rich text editor built with Python and tkinter.
Inspired by Notepad++ functionality.

Features:
- Syntax highlighting for multiple languages
- Line numbering
- Multiple themes
- Find and replace with regex support
- Code folding
- And more!

"""
        
        ttk.Label(about_dialog, text=about_text, justify=tk.CENTER, wraplength=380).pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        ttk.Button(about_dialog, text="Close", command=about_dialog.destroy).pack(pady=10)
    
    def show_shortcuts(self):
        shortcuts_dialog = tk.Toplevel(self.root)
        shortcuts_dialog.title("Keyboard Shortcuts")
        shortcuts_dialog.geometry("400x400")
        
        shortcuts_text = """
Keyboard Shortcuts:

File Operations:
  Ctrl+N     New File
  Ctrl+O     Open File
  Ctrl+S     Save File
  Ctrl+W     Close File

Edit Operations:
  Ctrl+Z     Undo
  Ctrl+Y     Redo
  Ctrl+X     Cut
  Ctrl+C     Copy
  Ctrl+V     Paste
  Ctrl+A     Select All
  Ctrl+F     Find/Replace

Navigation:
  Home       Start of Line
  End        End of Line
  Ctrl+Home  Start of Document
  Ctrl+End   End of Document
  Ctrl+G     Go to Line
"""
        
        shortcuts_frame = ttk.Frame(shortcuts_dialog)
        shortcuts_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        shortcuts_text_widget = tk.Text(shortcuts_frame, wrap=tk.WORD, height=20, width=40)
        shortcuts_text_widget.insert('1.0', shortcuts_text)
        shortcuts_text_widget.config(state=tk.DISABLED)
        shortcuts_text_widget.pack(expand=True, fill=tk.BOTH)
        
        ttk.Button(shortcuts_dialog, text="Close", command=shortcuts_dialog.destroy).pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedNotepad(root)
    root.mainloop()