import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import webbrowser
import tempfile
import os
import re
from pathlib import Path

class SimpleMarkdownParser:
    """Parser simplu pentru Markdown folosind doar regex"""
    
    def __init__(self):
        self.html_content = ""
        
    def parse(self, markdown_text):
        """Convertește Markdown în HTML simplu"""
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
        """Parsează formatarea inline"""
        # Bold **text** sau __text__
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.*?)__', r'<strong>\1</strong>', text)
        
        # Italic *text* sau _text_
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
        """Escape caractere HTML"""
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

class MarkdownViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Markdown Viewer")
        self.root.geometry("1000x700")
        
        # Variabile pentru fișier
        self.current_file = None
        self.markdown_content = ""
        self.parser = SimpleMarkdownParser()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fișier", menu=file_menu)
        file_menu.add_command(label="Deschide...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Reîncarcă", command=self.reload_file, accelerator="F5")
        file_menu.add_separator()
        file_menu.add_command(label="Export HTML...", command=self.export_html)
        file_menu.add_separator()
        file_menu.add_command(label="Ieșire", command=self.root.quit)
        
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Vizualizare", menu=view_menu)
        view_menu.add_command(label="Preview în browser", command=self.preview_in_browser)
        
        # Toolbar
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(toolbar, text="Deschide", command=self.open_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Reîncarcă", command=self.reload_file).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        ttk.Button(toolbar, text="Preview Browser", command=self.preview_in_browser).pack(side=tk.LEFT, padx=2)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Gata - Selectează un fișier Markdown pentru a începe")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Main content area
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Notebook pentru taburi
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab pentru markdown source
        self.source_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.source_frame, text="📝 Markdown Source")
        
        self.source_text = scrolledtext.ScrolledText(
            self.source_frame, 
            wrap=tk.WORD, 
            font=("Consolas", 10),
            state=tk.DISABLED,
            bg="#f8f8f8"
        )
        self.source_text.pack(fill=tk.BOTH, expand=True)
        
        # Tab pentru preview formatat
        self.preview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.preview_frame, text="👁️ Preview Formatat")
        
        self.preview_text = scrolledtext.ScrolledText(
            self.preview_frame, 
            wrap=tk.WORD,
            font=("Arial", 10),
            state=tk.DISABLED,
            bg="white"
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        
        # Tab pentru HTML generat
        self.html_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.html_frame, text="🔧 HTML Generat")
        
        self.html_text = scrolledtext.ScrolledText(
            self.html_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            state=tk.DISABLED,
            bg="#f0f0f0"
        )
        self.html_text.pack(fill=tk.BOTH, expand=True)
        
        # Binding pentru keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<F5>', lambda e: self.reload_file())
        
        # Configurare tag-uri pentru preview formatat
        self.setup_preview_tags()
        
    def setup_preview_tags(self):
        """Configurează tag-uri pentru formatare în preview"""
        self.preview_text.tag_configure("h1", font=("Arial", 18, "bold"), spacing1=15, spacing3=10)
        self.preview_text.tag_configure("h2", font=("Arial", 16, "bold"), spacing1=12, spacing3=8)
        self.preview_text.tag_configure("h3", font=("Arial", 14, "bold"), spacing1=10, spacing3=6)
        self.preview_text.tag_configure("h4", font=("Arial", 12, "bold"), spacing1=8, spacing3=4)
        self.preview_text.tag_configure("bold", font=("Arial", 10, "bold"))
        self.preview_text.tag_configure("italic", font=("Arial", 10, "italic"))
        self.preview_text.tag_configure("code", font=("Consolas", 9), background="#e8e8e8", relief="solid", borderwidth=1)
        self.preview_text.tag_configure("blockquote", lmargin1=20, lmargin2=20, background="#f0f8ff", font=("Arial", 10, "italic"))
        self.preview_text.tag_configure("link", foreground="blue", underline=True)
        
    def open_file(self):
        """Deschide un fișier Markdown"""
        file_path = filedialog.askopenfilename(
            title="Selectează fișier Markdown",
            filetypes=[
                ("Fișiere Markdown", "*.md *.markdown *.mdown *.mkd *.txt"),
                ("Toate fișierele", "*.*")
            ]
        )
        
        if file_path:
            self.load_file(file_path)
            
    def load_file(self, file_path):
        """Încarcă conținutul unui fișier"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.current_file = file_path
            self.markdown_content = content
            
            # Actualizează titlul ferestrei
            filename = os.path.basename(file_path)
            self.root.title(f"Markdown Viewer - {filename}")
            
            # Actualizează conținutul
            self.update_source_view()
            self.update_preview()
            self.update_html_view()
            
            self.status_var.set(f"Încărcat: {file_path} ({len(content)} caractere)")
            
        except Exception as e:
            messagebox.showerror("Eroare", f"Nu s-a putut încărca fișierul:\n{str(e)}")
            
    def update_source_view(self):
        """Actualizează tab-ul cu sursa Markdown"""
        self.source_text.config(state=tk.NORMAL)
        self.source_text.delete(1.0, tk.END)
        self.source_text.insert(1.0, self.markdown_content)
        self.source_text.config(state=tk.DISABLED)
        
    def update_preview(self):
        """Actualizează preview-ul formatat"""
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
                        self.preview_text.insert(tk.END, text + '\n', f"h{level}")
                        continue
                
                # Bold și italic (simplu)
                formatted_line = line
                
                # Înlocuiește **bold** cu formatare
                parts = re.split(r'(\*\*.*?\*\*)', formatted_line)
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
                    elif part.startswith('>'):
                        text = part.lstrip('>').strip()
                        self.preview_text.insert(tk.END, "  " + text, "blockquote")
                    else:
                        self.preview_text.insert(tk.END, part)
                
                self.preview_text.insert(tk.END, '\n')
            
            self.preview_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Eroare Preview", f"Eroare la generarea preview-ului:\n{str(e)}")
    
    def update_html_view(self):
        """Actualizează tab-ul cu HTML-ul generat"""
        if not self.markdown_content:
            return
            
        try:
            html = self.parser.parse(self.markdown_content)
            
            self.html_text.config(state=tk.NORMAL)
            self.html_text.delete(1.0, tk.END)
            self.html_text.insert(1.0, html)
            self.html_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Eroare HTML", f"Eroare la generarea HTML-ului:\n{str(e)}")
            
    def reload_file(self):
        """Reîncarcă fișierul curent"""
        if self.current_file and os.path.exists(self.current_file):
            self.load_file(self.current_file)
        else:
            messagebox.showwarning("Avertisment", "Nu există fișier încărcat pentru reîncărcare.")
            
    def preview_in_browser(self):
        """Deschide preview-ul în browser"""
        if not self.markdown_content:
            messagebox.showwarning("Avertisment", "Nu există conținut pentru preview.")
            return
            
        try:
            # Convertește în HTML
            html = self.parser.parse(self.markdown_content)
            
            # Creează un fișier HTML temporar
            html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Markdown Preview</title>
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
{html}
</body>
</html>"""
            
            # Salvează fișierul temporar
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_template)
                temp_file = f.name
            
            # Deschide în browser
            webbrowser.open(f'file://{temp_file}')
            
            self.status_var.set("Preview deschis în browser")
            
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la deschiderea preview-ului:\n{str(e)}")
            
    def export_html(self):
        """Exportă conținutul ca fișier HTML"""
        if not self.markdown_content:
            messagebox.showwarning("Avertisment", "Nu există conținut pentru export.")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Salvează ca HTML",
            defaultextension=".html",
            filetypes=[("Fișiere HTML", "*.html"), ("Toate fișierele", "*.*")]
        )
        
        if file_path:
            try:
                html = self.parser.parse(self.markdown_content)
                
                html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Markdown Export</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 0 auto; padding: 40px 20px; line-height: 1.6; color: #333; }}
        h1, h2, h3, h4, h5, h6 {{ margin-top: 30px; margin-bottom: 15px; color: #2c3e50; }}
        h1 {{ font-size: 2em; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        h2 {{ font-size: 1.5em; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
        pre {{ background: #f8f9fa; padding: 15px; border-radius: 6px; overflow-x: auto; border-left: 4px solid #007acc; }}
        code {{ background: #f1f3f4; padding: 2px 6px; border-radius: 3px; font-family: 'Consolas', 'Monaco', monospace; font-size: 0.9em; }}
        blockquote {{ border-left: 4px solid #dfe2e5; margin: 0; padding-left: 20px; color: #6a737d; font-style: italic; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #dfe2e5; padding: 12px; text-align: left; }}
        th {{ background-color: #f6f8fa; font-weight: 600; }}
        ul, ol {{ padding-left: 30px; }}
        li {{ margin: 5px 0; }}
        a {{ color: #0366d6; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        hr {{ border: none; height: 1px; background: #e1e4e8; margin: 30px 0; }}
        img {{ max-width: 100%; height: auto; }}
    </style>
</head>
<body>
{html}
</body>
</html>"""
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_template)
                
                self.status_var.set(f"Exportat: {file_path}")
                messagebox.showinfo("Succes", f"Fișierul a fost exportat cu succes în:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Eroare", f"Eroare la export:\n{str(e)}")

def main():
    root = tk.Tk()
    app = MarkdownViewer(root)
    
    # Mesaj de bun venit
    welcome_text = """# Bun venit la Markdown Viewer! 🎉

Acest viewer Markdown nu necesită module externe și folosește doar Python standard.

## Funcționalități disponibile:

- **📝 Markdown Source**: Vezi codul Markdown original
- **👁️ Preview Formatat**: Vezi preview-ul formatat în aplicație  
- **🔧 HTML Generat**: Vezi HTML-ul generat din Markdown
- **🌐 Preview în Browser**: Deschide preview-ul în browser web
- **💾 Export HTML**: Salvează ca fișier HTML

## Formatare suportată:

### Headers
# H1
## H2
### H3

### Text formatting
**Bold text** și *italic text*

### Code
`inline code` și blocuri de cod:

```
cod pe mai multe linii
```

### Lists
- Element listă
- Alt element

### Blockquotes
> Acesta este un blockquote

### Links și Images
[Link text](http://example.com)
![Alt text](image.jpg)

---

**Începe prin a deschide un fișier Markdown din meniu sau toolbar!**
"""
    
    app.markdown_content = welcome_text
    app.update_source_view()
    app.update_preview()
    app.update_html_view()
    
    root.mainloop()

if __name__ == "__main__":
    main()