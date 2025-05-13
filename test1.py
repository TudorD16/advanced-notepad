import tkinter as tk
from tkinter import ttk, font, filedialog, colorchooser, messagebox
import json
import os

class Win95KnowledgeBase:
    def __init__(self, root):
        self.root = root
        self.root.title("Retro Knowledge Base")
        self.root.geometry("800x600")
        
        # Culorile Windows 95
        self.win95_bg = "#c0c0c0"
        self.win95_button = "#c0c0c0"
        self.win95_text_bg = "#ffffff"
        self.win95_text_fg = "#000000"
        self.win95_active = "#000080"
        self.win95_highlight = "#0000ff"
        
        # Fonturi
        self.default_font = font.Font(family="MS Sans Serif", size=10)
        
        # Configurare stil Windows 95
        self.root.configure(bg=self.win95_bg)
        
        # Variabile pentru fișierul curent
        self.current_file = None
        self.procedures = {}
        self.current_procedure = None
        
        # Crearea interfeței
        self.create_ui()
        
        # Crearea primei proceduri implicite
        self.new_procedure()
    
    def create_ui(self):
        # Cadru principal
        main_frame = tk.Frame(self.root, bg=self.win95_bg, bd=1, relief=tk.RAISED)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Meniu
        self.create_menu()
        
        # Cadru pentru toolbar
        toolbar_frame = tk.Frame(main_frame, bg=self.win95_bg, bd=1, relief=tk.RAISED)
        toolbar_frame.pack(fill=tk.X, padx=2, pady=2)
        
        # Butoane toolbar
        new_btn = tk.Button(toolbar_frame, text="New", bg=self.win95_button, 
                          relief=tk.RAISED, bd=2, font=self.default_font,
                          command=self.new_procedure)
        new_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        save_btn = tk.Button(toolbar_frame, text="Save", bg=self.win95_button, 
                           relief=tk.RAISED, bd=2, font=self.default_font,
                           command=self.save_procedure)
        save_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        bold_btn = tk.Button(toolbar_frame, text="B", bg=self.win95_button, 
                          relief=tk.RAISED, bd=2, font=font.Font(family="MS Sans Serif", size=10, weight="bold"),
                          command=self.toggle_bold)
        bold_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        italic_btn = tk.Button(toolbar_frame, text="I", bg=self.win95_button, 
                            relief=tk.RAISED, bd=2, font=font.Font(family="MS Sans Serif", size=10, slant="italic"),
                            command=self.toggle_italic)
        italic_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        text_color_btn = tk.Button(toolbar_frame, text="Text Color", bg=self.win95_button, 
                                 relief=tk.RAISED, bd=2, font=self.default_font,
                                 command=self.choose_text_color)
        text_color_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        bg_color_btn = tk.Button(toolbar_frame, text="BG Color", bg=self.win95_button, 
                               relief=tk.RAISED, bd=2, font=self.default_font,
                               command=self.choose_bg_color)
        bg_color_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Combobox pentru mărime font
        font_size_label = tk.Label(toolbar_frame, text="Font:", bg=self.win95_bg, font=self.default_font)
        font_size_label.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.font_size_var = tk.StringVar(value="10")
        font_sizes = ["8", "9", "10", "11", "12", "14", "16", "18", "20", "22", "24", "26", "28", "36", "48", "72"]
        self.font_size_combo = ttk.Combobox(toolbar_frame, textvariable=self.font_size_var, values=font_sizes, width=3)
        self.font_size_combo.pack(side=tk.LEFT, padx=2, pady=2)
        self.font_size_combo.bind("<<ComboboxSelected>>", self.change_font_size)
        
        # Cadru pentru conținut
        content_frame = tk.Frame(main_frame, bg=self.win95_bg)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Cadru stânga pentru lista de proceduri
        left_frame = tk.Frame(content_frame, bg=self.win95_bg, bd=1, relief=tk.SUNKEN, width=200)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=2, pady=2)
        left_frame.pack_propagate(False)
        
        # Lista de proceduri
        procedure_label = tk.Label(left_frame, text="Procedures:", bg=self.win95_bg, font=self.default_font)
        procedure_label.pack(anchor=tk.W, padx=5, pady=5)
        
        self.procedure_listbox = tk.Listbox(left_frame, bg=self.win95_text_bg, relief=tk.SUNKEN, bd=2,
                                         selectbackground=self.win95_active, font=self.default_font)
        self.procedure_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.procedure_listbox.bind("<<ListboxSelect>>", self.load_selected_procedure)
        
        # Cadru pentru adăugarea unei noi proceduri
        add_procedure_frame = tk.Frame(left_frame, bg=self.win95_bg)
        add_procedure_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.new_procedure_name = tk.Entry(add_procedure_frame, bg=self.win95_text_bg, 
                                        relief=tk.SUNKEN, bd=2, font=self.default_font)
        self.new_procedure_name.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        
        add_btn = tk.Button(add_procedure_frame, text="+", bg=self.win95_button, 
                          relief=tk.RAISED, bd=2, font=self.default_font,
                          command=self.add_new_procedure)
        add_btn.pack(side=tk.RIGHT)
        
        # Cadru dreapta pentru editor text
        right_frame = tk.Frame(content_frame, bg=self.win95_bg, bd=1, relief=tk.SUNKEN)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Titlu procedură
        title_frame = tk.Frame(right_frame, bg=self.win95_bg)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        
        title_label = tk.Label(title_frame, text="Title:", bg=self.win95_bg, font=self.default_font)
        title_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.title_entry = tk.Entry(title_frame, bg=self.win95_text_bg, 
                                 relief=tk.SUNKEN, bd=2, font=self.default_font)
        self.title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Editor text
        self.text_editor = tk.Text(right_frame, bg=self.win95_text_bg, fg=self.win95_text_fg,
                                relief=tk.SUNKEN, bd=2, font=self.default_font,
                                wrap=tk.WORD, undo=True)
        self.text_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar pentru editor
        scrollbar = tk.Scrollbar(self.text_editor, command=self.text_editor.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_editor.config(yscrollcommand=scrollbar.set)
        
        # Status bar
        self.status_bar = tk.Label(main_frame, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                font=font.Font(family="MS Sans Serif", size=8), bg=self.win95_bg)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # Meniu Fișier
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_kb)
        file_menu.add_command(label="Open", command=self.open_kb)
        file_menu.add_command(label="Save", command=self.save_kb)
        file_menu.add_command(label="Save as", command=self.save_kb_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Meniu Editare
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Cut", command=lambda: self.text_editor.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", command=lambda: self.text_editor.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", command=lambda: self.text_editor.event_generate("<<Paste>>"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Bold", command=self.toggle_bold)
        edit_menu.add_command(label="Italic", command=self.toggle_italic)
        edit_menu.add_command(label="Text color", command=self.choose_text_color)
        edit_menu.add_command(label="BG color", command=self.choose_bg_color)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # Meniu Ajutor
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def add_tag_with_config(self, tag_name, **kwargs):
        """Adaugă un tag cu configurație pentru formatare text"""
        self.text_editor.tag_configure(tag_name, **kwargs)
    
    def toggle_tag(self, tag_name):
        """Comută un tag la selecția curentă"""
        try:
            # Verifică dacă există text selectat
            selected_text = self.text_editor.tag_ranges(tk.SEL)
            if selected_text:
                start, end = selected_text
                # Verifică dacă tag-ul există deja în selecție
                tags = self.text_editor.tag_names(start)
                if tag_name in tags:
                    self.text_editor.tag_remove(tag_name, start, end)
                else:
                    self.text_editor.tag_add(tag_name, start, end)
            else:
                self.status_bar.config(text="Select text to apply formatting.")
        except:
            self.status_bar.config(text="Error applying formatting.")
    
    def toggle_bold(self):
        """Comută textul îngroșat"""
        bold_font = font.Font(family="MS Sans Serif", size=int(self.font_size_var.get()), weight="bold")
        self.add_tag_with_config("bold", font=bold_font)
        self.toggle_tag("bold")
    
    def toggle_italic(self):
        """Comută textul înclinat"""
        italic_font = font.Font(family="MS Sans Serif", size=int(self.font_size_var.get()), slant="italic")
        self.add_tag_with_config("italic", font=italic_font)
        self.toggle_tag("italic")
    
    def choose_text_color(self):
        """Alege culoarea textului"""
        color = colorchooser.askcolor(title="Choose text color.")[1]
        if color:
            self.add_tag_with_config(f"color_{color}", foreground=color)
            self.toggle_tag(f"color_{color}")
    
    def choose_bg_color(self):
        """Alege culoarea de fundal"""
        color = colorchooser.askcolor(title="Choose background color.")[1]
        if color:
            self.add_tag_with_config(f"bg_{color}", background=color)
            self.toggle_tag(f"bg_{color}")
    
    def change_font_size(self, event=None):
        """Schimbă dimensiunea fontului"""
        try:
            size = int(self.font_size_var.get())
            size_font = font.Font(family="MS Sans Serif", size=size)
            tag_name = f"size_{size}"
            self.add_tag_with_config(tag_name, font=size_font)
            
            # Aplică tag-ul la selecție
            selected_text = self.text_editor.tag_ranges(tk.SEL)
            if selected_text:
                start, end = selected_text
                # Elimină alte tag-uri de dimensiune
                for tag in self.text_editor.tag_names(start):
                    if tag.startswith("size_"):
                        self.text_editor.tag_remove(tag, start, end)
                # Adaugă noul tag
                self.text_editor.tag_add(tag_name, start, end)
            else:
                self.status_bar.config(text="Select text to change font size.")
        except:
            self.status_bar.config(text="Error changing font size.")
    
    def new_procedure(self):
        """Creează o nouă procedură"""
        self.current_procedure = f"Procedure {len(self.procedures) + 1}"
        self.procedures[self.current_procedure] = {
            "title": self.current_procedure,
            "content": "",
            "tags": []
        }
        self.update_procedure_list()
        self.clear_editor()
        self.title_entry.insert(0, self.current_procedure)
    
    def add_new_procedure(self):
        """Adaugă o nouă procedură din câmpul de intrare"""
        name = self.new_procedure_name.get().strip()
        if name:
            self.current_procedure = name
            self.procedures[name] = {
                "title": name,
                "content": "",
                "tags": []
            }
            self.update_procedure_list()
            self.clear_editor()
            self.title_entry.insert(0, name)
            self.new_procedure_name.delete(0, tk.END)
        else:
            self.status_bar.config(text="Enter a name for the new procedure.")
    
    def update_procedure_list(self):
        """Actualizează lista de proceduri"""
        self.procedure_listbox.delete(0, tk.END)
        for proc in self.procedures:
            self.procedure_listbox.insert(tk.END, proc)
        # Selectează procedura curentă
        if self.current_procedure:
            for i, proc in enumerate(self.procedures):
                if proc == self.current_procedure:
                    self.procedure_listbox.selection_set(i)
                    break
    
    def load_selected_procedure(self, event=None):
        """Încarcă procedura selectată"""
        selection = self.procedure_listbox.curselection()
        if selection:
            index = selection[0]
            procedure_name = self.procedure_listbox.get(index)
            
            # Salvează procedura curentă înainte de a o schimba
            if self.current_procedure:
                self.save_procedure()
            
            # Încarcă noua procedură
            self.current_procedure = procedure_name
            self.load_procedure(procedure_name)
    
    def load_procedure(self, procedure_name):
        """Încarcă o procedură în editor"""
        if procedure_name in self.procedures:
            procedure = self.procedures[procedure_name]
            
            # Curăță editorul
            self.clear_editor()
            
            # Setează titlul
            self.title_entry.insert(0, procedure["title"])
            
            # Setează conținutul
            self.text_editor.insert("1.0", procedure["content"])
            
            # Aplică tag-urile
            for tag_info in procedure["tags"]:
                tag_name = tag_info["name"]
                start = tag_info["start"]
                end = tag_info["end"]
                config = tag_info["config"]
                
                # Creează tag-ul cu configurația sa
                self.text_editor.tag_configure(tag_name, **config)
                
                # Aplică tag-ul
                self.text_editor.tag_add(tag_name, start, end)
            
            self.status_bar.config(text=f"Procedure '{procedure_name}' loaded")
    
    def save_procedure(self):
        """Salvează procedura curentă"""
        if self.current_procedure:
            # Actualizează titlul
            new_title = self.title_entry.get().strip()
            if new_title and new_title != self.current_procedure:
                # Dacă titlul s-a schimbat, trebuie să redenumim procedura
                procedure_data = self.procedures[self.current_procedure]
                del self.procedures[self.current_procedure]
                self.current_procedure = new_title
                self.procedures[new_title] = procedure_data
            
            # Salvează conținutul
            content = self.text_editor.get("1.0", tk.END)
            self.procedures[self.current_procedure]["content"] = content
            self.procedures[self.current_procedure]["title"] = new_title
            
            # Salvează tag-urile
            tags = []
            for tag_name in self.text_editor.tag_names():
                if tag_name == "sel":  # Ignoră tag-ul de selecție
                    continue
                
                # Obține configurația tag-ului
                config = {}
                for key in ["font", "foreground", "background"]:
                    value = self.text_editor.tag_cget(tag_name, key)
                    if value:
                        config[key] = value
                
                # Obține toate intervalele care au acest tag
                ranges = self.text_editor.tag_ranges(tag_name)
                for i in range(0, len(ranges), 2):
                    start = ranges[i]
                    end = ranges[i + 1]
                    tags.append({
                        "name": tag_name,
                        "start": str(start),
                        "end": str(end),
                        "config": config
                    })
            
            self.procedures[self.current_procedure]["tags"] = tags
            
            self.update_procedure_list()
            self.status_bar.config(text=f"Procedure '{self.current_procedure}' saved")
    
    def clear_editor(self):
        """Curăță editorul"""
        self.text_editor.delete("1.0", tk.END)
        self.title_entry.delete(0, tk.END)
        
        # Elimină toate tag-urile
        for tag in self.text_editor.tag_names():
            if tag != "sel":  # Păstrează tag-ul de selecție
                self.text_editor.tag_delete(tag)
    
    def new_kb(self):
        """Creează o nouă bază de cunoștințe"""
        if self.procedures and messagebox.askyesno("Saving", "Do you want to save the current knowledge base before creating a new one?"):
            self.save_kb()
        
        self.procedures = {}
        self.current_procedure = None
        self.current_file = None
        self.update_procedure_list()
        self.clear_editor()
        self.new_procedure()
        self.status_bar.config(text="Nouă bază de cunoștințe creată")
    
    def open_kb(self):
        """Deschide o bază de cunoștințe"""
        if self.procedures and messagebox.askyesno("Saving", "Do you want to save the current knowledge base before creating a new one?"):
            self.save_kb()
        
        file_path = filedialog.askopenfilename(
            defaultextension=".kb95",
            filetypes=[("Knowledge Base for Multiapp 95", "*.kb95"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    self.procedures = data.get("procedures", {})
                    self.current_file = file_path
                    
                    # Încarcă prima procedură dacă există
                    if self.procedures:
                        self.current_procedure = list(self.procedures.keys())[0]
                        self.update_procedure_list()
                        self.load_procedure(self.current_procedure)
                    else:
                        self.new_procedure()
                    
                    self.status_bar.config(text=f"Knowledge base '{os.path.basename(file_path)}' open")
            except Exception as e:
                messagebox.showerror("Error", f"The file could not be opened: {str(e)}")
    
    def save_kb(self):
        """Salvează baza de cunoștințe"""
        if self.current_procedure:
            self.save_procedure()
        
        if self.current_file:
            self.save_kb_to_file(self.current_file)
        else:
            self.save_kb_as()
    
    def save_kb_as(self):
        """Salvează baza de cunoștințe ca un nou fișier"""
        if self.current_procedure:
            self.save_procedure()
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".kb95",
            filetypes=[("Knowledge Base for Multiapp 95", "*.kb95"), ("All files", "*.*")]
        )
        
        if file_path:
            self.save_kb_to_file(file_path)
            self.current_file = file_path
    
    def save_kb_to_file(self, file_path):
        """Salvează baza de cunoștințe în fișier"""
        try:
            data = {
                "procedures": self.procedures
            }
            
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            
            self.status_bar.config(text=f"Knowledge base saved in '{os.path.basename(file_path)}'")
        except Exception as e:
            messagebox.showerror("Error", f"The file could not be saved: {str(e)}")
    
    def show_about(self):
        """Afișează informații despre aplicație"""
        messagebox.showinfo(
            "About Knowledge Base",
            "Version 1.0\n\n"
            "A knowledge/procedure management system."
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = Win95KnowledgeBase(root)
    root.mainloop()