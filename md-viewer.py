import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import webbrowser
import tempfile
import os
import re
from pathlib import Path

class SimpleMarkdownParser:
    """Simple Markdown parser using only regex"""
    
    def __init__(self):
        self.html_content = ""
        
    def parse(self, markdown_text):
        """Convert Markdown to simple HTML"""
        lines = markdown_text.split('\n')
        html_lines = []
        in_code_block = False
        in_list = False
        
        for line in lines:
            # Code blocks
            if line.strip().startswith('```'):
                if in_code_block:
                    html_lines.append('</pre>')
                    in_code_block = False
                else:
                    html_lines.append('<pre><code>')
                    in_code_block = True
                continue
                
            if in_code_block:
                html_lines.append(self.escape_html(line))
                continue
            
            # Headers
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                if level <= 6:
                    text = line.lstrip('#').strip()
                    html_lines.append(f'<h{level}>{self.parse_inline(text)}</h{level}>')
                    continue
            
            # Horizontal rule
            if re.match(r'^[-*_]{3,}$', line.strip()):
                html_lines.append('<hr>')
                continue
            
            # Lists
            if re.match(r'^\s*[-*+]\s+', line):
                if not in_list:
                    html_lines.append('<ul>')
                    in_list = True
                text = re.sub(r'^\s*[-*+]\s+', '', line)
                html_lines.append(f'<li>{self.parse_inline(text)}</li>')
                continue
            elif re.match(r'^\s*\d+\.\s+', line):
                if not in_list:
                    html_lines.append('<ol>')
                    in_list = True
                text = re.sub(r'^\s*\d+\.\s+', '', line)
                html_lines.append(f'<li>{self.parse_inline(text)}</li>')
                continue
            else:
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
            
            # Blockquotes
            if line.startswith('>'):
                text = line.lstrip('>').strip()
                html_lines.append(f'<blockquote>{self.parse_inline(text)}</blockquote>')
                continue
            
            # Empty lines
            if not line.strip():
                html_lines.append('<br>')
                continue
            
            # Regular paragraphs
            html_lines.append(f'<p>{self.parse_inline(line)}</p>')
        
        # Close any open lists
        if in_list:
            html_lines.append('</ul>')
        if in_code_block:
            html_lines.append('</code></pre>')
            
        return '\n'.join(html_lines)
    
    def parse_inline(self, text):
        """Parse inline formatting"""
        # Bold **text** or __text__
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.*?)__', r'<strong>\1</strong>', text)
        
        # Italic *text* or _text_
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        text = re.sub(r'_(.*?)_', r'<em>\1</em>', text)
        
        # Code `text`
        text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
        
        # Links [text](url)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        
        # Images ![alt](url)
        text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', text)
        
        return text
    
    def escape_html(self, text):
        """Escape HTML characters"""
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

class MarkdownViewer:
    def __init__(self, rootMDDD):
        self.rootMDDD = rootMDDD
        self.rootMDDD.title("Markdown Viewer 95")
        self.rootMDDD.geometry("800x600")
        
        # Windows 95 color scheme
        self.bg_color = "#c0c0c0"
        self.button_color = "#c0c0c0"
        self.text_bg = "white"
        self.dark_edge = "#808080"
        self.light_edge = "#ffffff"
        
        # Configure rootMDDD window
        self.rootMDDD.configure(bg=self.bg_color)
        
        # Variables
        self.current_file = None
        self.markdown_content = ""
        self.parser = SimpleMarkdownParser()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Menu bar with Windows 95 style
        menubar = tk.Menu(self.rootMDDD, bg=self.bg_color, fg="black", 
                         activebackground="#316AC5", activeforeground="white")
        self.rootMDDD.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color, fg="black",
                           activebackground="#316AC5", activeforeground="white")
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Reload", command=self.reload_file, accelerator="F5")
        file_menu.add_separator()
        file_menu.add_command(label="Export HTML...", command=self.export_html)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.rootMDDD.quit)
        
        view_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color, fg="black",
                           activebackground="#316AC5", activeforeground="white")
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Preview in Browser", command=self.preview_in_browser)
        
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color, fg="black",
                           activebackground="#316AC5", activeforeground="white")
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Toolbar with Windows 95 style
        toolbar = tk.Frame(self.rootMDDD, bg=self.bg_color, relief=tk.RAISED, bd=1)
        toolbar.pack(fill=tk.X, padx=2, pady=2)
        
        # Windows 95 style buttons
        self.create_button(toolbar, "Open", self.open_file).pack(side=tk.LEFT, padx=1)
        self.create_button(toolbar, "Reload", self.reload_file).pack(side=tk.LEFT, padx=1)
        
        # Separator
        separator = tk.Frame(toolbar, width=2, bg=self.dark_edge, relief=tk.SUNKEN, bd=1)
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)
        
        self.create_button(toolbar, "Browser Preview", self.preview_in_browser).pack(side=tk.LEFT, padx=1)
        self.create_button(toolbar, "Export HTML", self.export_html).pack(side=tk.LEFT, padx=1)
        
        # Main content area with Windows 95 styling
        main_frame = tk.Frame(self.rootMDDD, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Notebook-style tabs (manual implementation for Win95 feel)
        self.tab_frame = tk.Frame(main_frame, bg=self.bg_color)
        self.tab_frame.pack(fill=tk.X)
        
        self.tabs = {}
        self.active_tab = "source"
        
        # Create tab buttons
        self.create_tab_button("source", "Markdown Source").pack(side=tk.LEFT)
        self.create_tab_button("preview", "Formatted Preview").pack(side=tk.LEFT)
        self.create_tab_button("html", "Generated HTML").pack(side=tk.LEFT)
        
        # Content frame with sunken border
        content_frame = tk.Frame(main_frame, bg=self.bg_color, relief=tk.SUNKEN, bd=2)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Source text area
        self.source_text = scrolledtext.ScrolledText(
            content_frame,
            wrap=tk.WORD,
            font=("Courier New", 9),
            bg=self.text_bg,
            fg="black",
            relief=tk.SUNKEN,
            bd=1,
            state=tk.DISABLED
        )
        self.source_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Preview text area (hidden initially)
        self.preview_text = scrolledtext.ScrolledText(
            content_frame,
            wrap=tk.WORD,
            font=("MS Sans Serif", 8),
            bg=self.text_bg,
            fg="black",
            relief=tk.SUNKEN,
            bd=1,
            state=tk.DISABLED
        )
        
        # HTML text area (hidden initially)
        self.html_text = scrolledtext.ScrolledText(
            content_frame,
            wrap=tk.WORD,
            font=("Courier New", 8),
            bg="#f0f0f0",
            fg="black",
            relief=tk.SUNKEN,
            bd=1,
            state=tk.DISABLED
        )
        
        # Status bar with Windows 95 style
        status_frame = tk.Frame(self.rootMDDD, bg=self.bg_color, relief=tk.SUNKEN, bd=1)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Select a Markdown file to begin")
        status_label = tk.Label(status_frame, textvariable=self.status_var, 
                               bg=self.bg_color, fg="black", anchor=tk.W, 
                               font=("MS Sans Serif", 8))
        status_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Keyboard bindings
        self.rootMDDD.bind('<Control-o>', lambda e: self.open_file())
        self.rootMDDD.bind('<F5>', lambda e: self.reload_file())
        
        # Configure text formatting
        self.setup_preview_tags()
        
        # Show welcome message
        self.show_welcome()
        
    def create_button(self, parent, text, command):
        """Create a Windows 95 style button"""
        btn = tk.Button(parent, text=text, command=command,
                       bg=self.button_color, fg="black",
                       relief=tk.RAISED, bd=2,
                       font=("MS Sans Serif", 8),
                       padx=8, pady=2)
        return btn
    
    def create_tab_button(self, tab_id, text):
        """Create a tab button"""
        btn = tk.Button(self.tab_frame, text=text,
                       command=lambda: self.switch_tab(tab_id),
                       bg=self.button_color if tab_id != self.active_tab else "white",
                       fg="black",
                       relief=tk.RAISED if tab_id != self.active_tab else tk.SUNKEN,
                       bd=2,
                       font=("MS Sans Serif", 8),
                       padx=10, pady=2)
        self.tabs[tab_id] = btn
        return btn
    
    def switch_tab(self, tab_id):
        """Switch between tabs"""
        # Update button states
        for tid, btn in self.tabs.items():
            if tid == tab_id:
                btn.config(relief=tk.SUNKEN, bg="white")
            else:
                btn.config(relief=tk.RAISED, bg=self.button_color)
        
        # Hide all text widgets
        self.source_text.pack_forget()
        self.preview_text.pack_forget()
        self.html_text.pack_forget()
        
        # Show selected tab content
        if tab_id == "source":
            self.source_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        elif tab_id == "preview":
            self.preview_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        elif tab_id == "html":
            self.html_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        self.active_tab = tab_id
        
    def setup_preview_tags(self):
        """Configure text formatting tags"""
        self.preview_text.tag_configure("h1", font=("MS Sans Serif", 14, "bold"), spacing1=12, spacing3=8)
        self.preview_text.tag_configure("h2", font=("MS Sans Serif", 12, "bold"), spacing1=10, spacing3=6)
        self.preview_text.tag_configure("h3", font=("MS Sans Serif", 10, "bold"), spacing1=8, spacing3=4)
        self.preview_text.tag_configure("bold", font=("MS Sans Serif", 8, "bold"))
        self.preview_text.tag_configure("italic", font=("MS Sans Serif", 8, "italic"))
        self.preview_text.tag_configure("code", font=("Courier New", 8), background="#e0e0e0")
        self.preview_text.tag_configure("blockquote", lmargin1=20, lmargin2=20, background="#f0f0f0")
        
    def show_welcome(self):
        """Show welcome message"""
        welcome_text = """# Welcome to Markdown Viewer 95!

This retro Markdown viewer brings you back to the Windows 95 era.
No external dependencies required - pure Python standard library.

## Features Available:

- **Markdown Source**: View the original Markdown code
- **Formatted Preview**: See formatted preview in the application
- **Generated HTML**: View the HTML generated from Markdown
- **Browser Preview**: Open preview in your web browser
- **HTML Export**: Save as standalone HTML file

## Supported Markdown:

### Headers
# H1 Header
## H2 Header
### H3 Header

### Text Formatting
**Bold text** and *italic text*

### Code
`inline code` and code blocks:

```
multi-line code
block example
```

### Lists
- Bullet list item
- Another item

1. Numbered list
2. Second item

### Blockquotes
> This is a blockquote
> It can span multiple lines

### Links and Images
[Link text](http://example.com)
![Alt text](image.jpg)

---

**Get started by opening a Markdown file from the File menu or toolbar!**

*Experience the nostalgia of Windows 95 while viewing your modern Markdown files.*
"""
        
        self.markdown_content = welcome_text
        self.update_all_views()
        
    def show_about(self):
        """Show about dialog"""
        about_text = """Markdown Viewer 95
Version 1.0

A retro-style Markdown viewer inspired by Windows 95.

Built with Python and Tkinter
No external dependencies required

© 2025 - Retro Computing Division"""
        
        messagebox.showinfo("About Markdown Viewer 95", about_text)
        
    def open_file(self):
        """Open a Markdown file"""
        file_path = filedialog.askopenfilename(
            title="Open Markdown File",
            filetypes=[
                ("Markdown files", "*.md *.markdown *.mdown *.mkd *.txt"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.load_file(file_path)
            
    def load_file(self, file_path):
        """Load file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.current_file = file_path
            self.markdown_content = content
            
            # Update window title
            filename = os.path.basename(file_path)
            self.rootMDDD.title(f"Markdown Viewer 95 - {filename}")
            
            # Update content
            self.update_all_views()
            
            self.status_var.set(f"Loaded: {file_path} ({len(content)} characters)")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not load file:\n{str(e)}")
            
    def update_all_views(self):
        """Update all views"""
        self.update_source_view()
        self.update_preview()
        self.update_html_view()
        
    def update_source_view(self):
        """Update the Markdown source view"""
        self.source_text.config(state=tk.NORMAL)
        self.source_text.delete(1.0, tk.END)
        self.source_text.insert(1.0, self.markdown_content)
        self.source_text.config(state=tk.DISABLED)
        
    def update_preview(self):
        """Update the formatted preview"""
        if not self.markdown_content:
            return
            
        try:
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            
            lines = self.markdown_content.split('\n')
            
            for line in lines:
                # Headers
                if line.startswith('#'):
                    level = len(line) - len(line.lstrip('#'))
                    if level <= 6:
                        text = line.lstrip('#').strip()
                        self.preview_text.insert(tk.END, text + '\n', f"h{min(level, 3)}")
                        continue
                
                # Process inline formatting
                self.process_line_formatting(line)
                self.preview_text.insert(tk.END, '\n')
            
            self.preview_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Preview Error", f"Error generating preview:\n{str(e)}")
    
    def process_line_formatting(self, line):
        """Process inline formatting for a line"""
        if line.startswith('>'):
            text = line.lstrip('>').strip()
            self.preview_text.insert(tk.END, "  " + text, "blockquote")
            return
            
        # Simple bold/italic/code processing
        parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)', line)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                text = part[2:-2]
                self.preview_text.insert(tk.END, text, "bold")
            elif part.startswith('*') and part.endswith('*'):
                text = part[1:-1]
                self.preview_text.insert(tk.END, text, "italic")
            elif part.startswith('`') and part.endswith('`'):
                text = part[1:-1]
                self.preview_text.insert(tk.END, text, "code")
            else:
                self.preview_text.insert(tk.END, part)
    
    def update_html_view(self):
        """Update the HTML view"""
        if not self.markdown_content:
            return
            
        try:
            html = self.parser.parse(self.markdown_content)
            
            self.html_text.config(state=tk.NORMAL)
            self.html_text.delete(1.0, tk.END)
            self.html_text.insert(1.0, html)
            self.html_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("HTML Error", f"Error generating HTML:\n{str(e)}")
            
    def reload_file(self):
        """Reload current file"""
        if self.current_file and os.path.exists(self.current_file):
            self.load_file(self.current_file)
        else:
            messagebox.showwarning("Warning", "No file loaded to reload.")
            
    def preview_in_browser(self):
        """Open preview in browser"""
        if not self.markdown_content:
            messagebox.showwarning("Warning", "No content to preview.")
            return
            
        try:
            html = self.parser.parse(self.markdown_content)
            
            # Create HTML template with retro styling
            html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Markdown Preview - Windows 95 Style</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            line-height: 1.6;
            color: #333;
        }}
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 30px;
            margin-bottom: 15px;
            color: #2c3e50;
        }}
        h1 {{ font-size: 2em; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        h2 {{ font-size: 1.5em; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
        pre {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
            border-left: 4px solid #007acc;
        }}
        code {{
            background: #f1f3f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9em;
        }}
        blockquote {{
            border-left: 4px solid #dfe2e5;
            margin: 0;
            padding-left: 20px;
            color: #6a737d;
            font-style: italic;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #dfe2e5;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #f6f8fa;
            font-weight: 600;
        }}
        ul, ol {{ padding-left: 30px; }}
        li {{ margin: 5px 0; }}
        a {{ color: #0366d6; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        hr {{ border: none; height: 1px; background: #e1e4e8; margin: 30px 0; }}
        img {{ max-width: 100%; height: auto; }}
    </style>
</head>
<body>
    <div class="window">
        <h1 style="color: #000080; border-bottom: 1px solid #808080; padding-bottom: 5px;">
            Markdown Preview - Windows 95 Style
        </h1>
        {html}
    </div>
</body>
</html>"""
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_template)
                temp_file = f.name
            
            webbrowser.open(f'file://{temp_file}')
            self.status_var.set("Preview opened in browser")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error opening preview:\n{str(e)}")
            
    def export_html(self):
        """Export content as HTML file"""
        if not self.markdown_content:
            messagebox.showwarning("Warning", "No content to export.")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save as HTML",
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                html = self.parser.parse(self.markdown_content)
                
                html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Markdown Export</title>
    
</head>
<body>
    <div class="window">
        {html}
    </div>
</body>
</html>"""
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_template)
                
                self.status_var.set(f"Exported: {file_path}")
                messagebox.showinfo("Success", f"File exported successfully to:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Export error:\n{str(e)}")

def main():
    rootMDDD = tk.Tk()
    app = MarkdownViewer(rootMDDD)
    rootMDDD.mainloop()

if __name__ == "__main__":
    main()
