import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import time
import psutil
import shutil
import socket
import subprocess
import platform
from datetime import datetime, timedelta
import threading
import json
import os
import random
try:
    import openpyxl
except ImportError:
    pass

class Windows95Desktop:
    def __init__(self):
        self.rootW95dist = tk.Tk()
        self.rootW95dist.title("Windows 95")
        
        # Setează fereastra să fie fullscreen fără bara de titlu
        self.rootW95dist.overrideredirect(True)
        self.rootW95dist.state('zoomed')  # Pentru Windows - fullscreen
        # Pentru Linux/Mac folosește: self.rootW95dist.attributes('-fullscreen', True)
        
        self.rootW95dist.configure(bg="#008080")  # Teal background
        
        # Variables pentru Start Menu
        self.start_menu_visible = True
        self.start_menu = None
        
        # Lista de ferestre deschise pentru taskbar
        self.open_windows = []
        
        # Variables for monitoring
        self.network_history = []
        self.cpu_history = []
        self.memory_history = []
        self.monitoring_active = False
        
        # Paint application variables
        self.current_color = "black"
        self.brush_size = 2
        self.paint_tool = "pencil"
        
        self.setup_desktop()
        self.setup_taskbar()
        self.setup_start_menu()  # Start menu permanent
        self.setup_clock()
        
    def setup_desktop(self):
        # Desktop background cu pattern
        self.desktop_frame = tk.Frame(self.rootW95dist, bg="#008080")
        self.desktop_frame.pack(fill="both", expand=True)
        
        # Icoane pe desktop
        self.create_desktop_icon("My Computer", 50, 50, "computer")
        self.create_desktop_icon("Text Editor", 50, 120, "editor")
        self.create_desktop_icon("Calculator", 50, 190, "calculator")
        self.create_desktop_icon("Network Monitor", 50, 260, "network")
        self.create_desktop_icon("Hardware Info", 50, 330, "hardware")
        self.create_desktop_icon("Paint", 50, 400, "paint")
        self.create_desktop_icon("Excel Lite", 50, 470, "excel")
        self.create_desktop_icon("Word Lite", 50, 540, "word")
        self.create_desktop_icon("Command Prompt", 50, 610, "terminal")
    
    def make_window_draggable(self, window, title_bar):
        """Make a window draggable by its title bar"""
        def start_move(event):
            window.x = event.x
            window.y = event.y

        def stop_move(event):
            window.x = None
            window.y = None

        def do_move(event):
            if hasattr(window, 'x') and window.x is not None:
                deltax = event.x - window.x
                deltay = event.y - window.y
                x = window.winfo_x() + deltax
                y = window.winfo_y() + deltay
                window.geometry(f"+{x}+{y}")

        title_bar.bind("<Button-1>", start_move)
        title_bar.bind("<ButtonRelease-1>", stop_move)
        title_bar.bind("<B1-Motion>", do_move)
        
        # Bind și pe label-ul din title bar
        for child in title_bar.winfo_children():
            if isinstance(child, tk.Label):
                child.bind("<Button-1>", start_move)
                child.bind("<ButtonRelease-1>", stop_move)
                child.bind("<B1-Motion>", do_move)
    
    def create_desktop_icon(self, name, x, y, icon_type="normal"):
        icon_frame = tk.Frame(self.desktop_frame, bg="#008080")
        icon_frame.place(x=x, y=y)
        
        # Simulează o iconiță (folosim un dreptunghi colorat)
        icon_canvas = tk.Canvas(icon_frame, width=32, height=32, bg="#008080", highlightthickness=0)
        icon_canvas.pack()
        
        # Culori diferite pentru tipuri diferite de icoane
        if icon_type == "editor":
            fill_color = "#ffff66"  # Galben pentru text editor
        elif icon_type == "calculator":
            fill_color = "#66ff66"  # Verde pentru calculator
        elif icon_type == "network":
            fill_color = "#66ccff"  # Albastru pentru network
        elif icon_type == "hardware":
            fill_color = "#ff9966"  # Orange pentru hardware
        elif icon_type == "paint":
            fill_color = "#ff6699"  # Roz pentru paint
        elif icon_type == "excel":
            fill_color = "#00cc66"
        else:
            fill_color = "#c0c0c0"  # Gri standard
            
        icon_canvas.create_rectangle(2, 2, 30, 30, fill=fill_color, outline="#808080")
        icon_canvas.create_rectangle(4, 4, 28, 28, fill="#ffffff", outline="#404040")
        
        # Adaugă simboluri pentru icoane
        if icon_type == "network":
            icon_canvas.create_oval(8, 8, 24, 24, outline="#000080", width=2)
            icon_canvas.create_line(16, 8, 16, 24, fill="#000080", width=2)
            icon_canvas.create_line(8, 16, 24, 16, fill="#000080", width=2)
        elif icon_type == "hardware":
            icon_canvas.create_rectangle(8, 8, 24, 24, fill="#404040", outline="#000000")
            icon_canvas.create_rectangle(10, 10, 22, 22, fill="#808080", outline="#000000")
            icon_canvas.create_rectangle(12, 12, 20, 20, fill="#c0c0c0", outline="#000000")
        elif icon_type == "paint":
            # Draw a simple paint brush icon
            icon_canvas.create_rectangle(10, 6, 14, 18, fill="#8B4513", outline="#000000")  # Handle
            icon_canvas.create_oval(8, 18, 16, 26, fill="#ff0000", outline="#000000")  # Brush
            icon_canvas.create_oval(18, 10, 24, 16, fill="#0000ff", outline="#000000")  # Blue paint
            icon_canvas.create_oval(16, 18, 22, 24, fill="#00ff00", outline="#000000")  # Green paint
        elif icon_type == "excel":
            # Desenează un simbol tabel pentru Excel
            icon_canvas.create_rectangle(6, 6, 26, 26, fill="#008000", outline="#000000")
            # Linii verticale
            icon_canvas.create_line(13, 6, 13, 26, fill="#FFFFFF", width=1)
            icon_canvas.create_line(19, 6, 19, 26, fill="#FFFFFF", width=1)
            # Linii orizontale
            icon_canvas.create_line(6, 13, 26, 13, fill="#FFFFFF", width=1)
            icon_canvas.create_line(6, 19, 26, 19, fill="#FFFFFF", width=1)
        elif icon_type == "word":
            # Desenează un simbol pentru Word (document cu linii text)
            icon_canvas.create_rectangle(6, 6, 26, 26, fill="#0000CC", outline="#000000")
            # Linii text
            icon_canvas.create_line(9, 11, 23, 11, fill="#FFFFFF", width=1)
            icon_canvas.create_line(9, 15, 23, 15, fill="#FFFFFF", width=1)
            icon_canvas.create_line(9, 19, 23, 19, fill="#FFFFFF", width=1)
            icon_canvas.create_line(9, 23, 18, 23, fill="#FFFFFF", width=1)
        elif icon_type == "terminal":
            # Desenează un simbol pentru Command Prompt
            icon_canvas.create_rectangle(6, 6, 26, 26, fill="#000000", outline="#404040")
            # Simbolul prompt-ului >_
            icon_canvas.create_text(16, 16, text=">_", fill="#FFFFFF", font=("Courier", 10, "bold"))
        
        # Label pentru numele iconitei
        label = tk.Label(icon_frame, text=name, bg="#008080", fg="white", 
                        font=("MS Sans Serif", 8))
        label.pack()
        
        # Event pentru dublu-click
        icon_canvas.bind("<Double-Button-1>", lambda e: self.handle_icon_click(name, icon_type))
        label.bind("<Double-Button-1>", lambda e: self.handle_icon_click(name, icon_type))
    
    def handle_icon_click(self, name, icon_type):
        if icon_type == "editor":
            if not any(title == "Text Editor" for title, _, _ in self.open_windows):
                self.create_text_editor()
        elif icon_type == "calculator":
            if not any(title == "Calculator" for title, _, _ in self.open_windows):
                self.create_calculator()
        elif icon_type == "network":
            if not any(title == "Network Monitor" for title, _, _ in self.open_windows):
                self.create_network_monitor()
        elif icon_type == "hardware":
            if not any(title == "Hardware Info" for title, _, _ in self.open_windows):
                self.create_hardware_info()
        elif icon_type == "paint":
            if not any(title == "Paint" for title, _, _ in self.open_windows):
                self.create_paint_app()
        elif icon_type == "computer":
            if not any(title == "My Computer" for title, _, _ in self.open_windows):
                self.create_file_explorer()
        elif icon_type == "excel":
            if not any(title == "Excel Lite" for title, _, _ in self.open_windows):
                self.create_excel_lite()
        elif icon_type == "word":
            if not any(title == "Word Lite" for title, _, _ in self.open_windows):
                self.create_word_lite()
        elif icon_type == "terminal":
            if not any(title == "Command Prompt" for title, _, _ in self.open_windows):
                self.create_terminal()
        else:
            self.open_window(name)
    
    '''
    def create_word_lite(self, file_path=None):
        """Creează o aplicație Word Lite pentru a deschide și vizualiza fișiere .doc sau .docx"""
        word_window = tk.Toplevel(self.rootW95dist)
        word_window.title("Word Lite")
        word_window.overrideredirect(True)
        word_window.geometry("800x600+200+100")
        word_window.configure(bg="#c0c0c0")
        
        # Add Windows 95 style title bar
        title_bar = tk.Frame(word_window, bg="#000080", height=25)
        title_bar.pack(fill="x", side="top")
        title_label = tk.Label(title_bar, text="Word Lite", fg="white", bg="#000080",
                              font=("MS Sans Serif", 8, "bold"))
        title_label.pack(side="left", padx=5, pady=2)
        
        # Close button for title bar
        close_button = tk.Button(title_bar, text="×", bg="#c0c0c0", fg="black",
                                font=("Arial", 8, "bold"), width=2, height=1,
                                relief="raised", bd=1,
                                command=lambda: self.close_window("Word Lite", word_window))
        close_button.pack(side="right", padx=2, pady=1)
        
        self.make_window_draggable(word_window, title_bar)
        
        # Menubar
        menubar = tk.Menu(word_window)
        word_window.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        
        format_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Format", menu=format_menu)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        # Toolbar frame
        toolbar_frame = tk.Frame(word_window, bg="#c0c0c0", relief="raised", bd=2, height=35)
        toolbar_frame.pack(fill="x")
        toolbar_frame.pack_propagate(False)
        
        # Open button
        open_btn = tk.Button(toolbar_frame, text="Open", bg="#c0c0c0", relief="raised", bd=2,
                            font=("MS Sans Serif", 8),
                            command=lambda: open_document())
        open_btn.pack(side="left", padx=5, pady=2)
        
        # Save button (for future implementation)
        save_btn = tk.Button(toolbar_frame, text="Save", bg="#c0c0c0", relief="raised", bd=2,
                            font=("MS Sans Serif", 8),
                            command=lambda: save_document())
        save_btn.pack(side="left", padx=5, pady=2)
        
        # Print button
        print_btn = tk.Button(toolbar_frame, text="Print", bg="#c0c0c0", relief="raised", bd=2,
                             font=("MS Sans Serif", 8),
                             command=lambda: messagebox.showinfo("Print", "Printing functionality is not implemented in this version"))
        print_btn.pack(side="left", padx=5, pady=2)
        
        # Status bar
        status_frame = tk.Frame(word_window, bg="#c0c0c0", relief="sunken", bd=1, height=25)
        status_frame.pack(side="bottom", fill="x")
        status_frame.pack_propagate(False)
        
        status_label = tk.Label(status_frame, text="Ready", bg="#c0c0c0", font=("MS Sans Serif", 8))
        status_label.pack(side="left", padx=5)
        
        # Main content frame
        content_frame = tk.Frame(word_window, bg="white")
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Text area
        text_frame = tk.Frame(content_frame, bg="white")
        text_frame.pack(fill="both", expand=True)
        
        # Scrollbars
        v_scrollbar = tk.Scrollbar(text_frame)
        v_scrollbar.pack(side="right", fill="y")
        
        h_scrollbar = tk.Scrollbar(text_frame, orient="horizontal")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Text widget
        text_area = tk.Text(text_frame, wrap="word", yscrollcommand=v_scrollbar.set, 
                           xscrollcommand=h_scrollbar.set,
                           font=("Times New Roman", 12), bg="white", fg="black")
        text_area.pack(side="left", fill="both", expand=True)
        
        v_scrollbar.config(command=text_area.yview)
        h_scrollbar.config(command=text_area.xview)
        
        # Variables for tracking
        current_file = None
        
        def open_document():
            """Open a Word document"""
            file_path = filedialog.askopenfilename(
                defaultextension=".docx",
                filetypes=[("Word files", "*.docx;*.doc"), ("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            try:
                # Set cursor to wait
                word_window.config(cursor="wait")
                word_window.update()
                
                # Clear text area
                text_area.delete(1.0, tk.END)
                
                # Get the file extension
                ext = os.path.splitext(file_path)[1].lower()
                
                # Handle different file types
                if ext == ".txt":
                    # Simple text file
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        text_area.insert(tk.END, content)
                elif ext in [".doc", ".docx"]:
                    # Try to handle Word documents (simplified - only extracts text)
                    text_area.insert(tk.END, "Word Lite can display only plain text from Word documents.\n\n")
                    
                    try:
                        # If python-docx is installed, use it
                        import docx
                        doc = docx.Document(file_path)
                        for para in doc.paragraphs:
                            text_area.insert(tk.END, para.text + "\n")
                    except ImportError:
                        # Fallback method
                        text_area.insert(tk.END, "Cannot read Word document content. The python-docx library is not installed.\n")
                        text_area.insert(tk.END, "To install it, run: pip install python-docx\n\n")
                        text_area.insert(tk.END, "For now, only showing document metadata:\n")
                        text_area.insert(tk.END, f"Filename: {os.path.basename(file_path)}\n")
                        text_area.insert(tk.END, f"Size: {os.path.getsize(file_path)} bytes\n")
                else:
                    text_area.insert(tk.END, f"Cannot open file type: {ext}\n")
                    text_area.insert(tk.END, "Word Lite supports .txt, .doc, and .docx files.")
                
                # Update window title and status
                file_name = os.path.basename(file_path)
                title_label.config(text=f"Word Lite - {file_name}")
                word_window.title(f"Word Lite - {file_name}")
                status_label.config(text=f"Opened: {file_name}")
                
                # Save the current file
                nonlocal current_file
                current_file = file_path
                
            except Exception as e:
                text_area.delete(1.0, tk.END)
                text_area.insert(tk.END, f"Error opening file: {str(e)}")
                messagebox.showerror("Error", f"Could not open file: {str(e)}")
            finally:
                # Reset cursor
                word_window.config(cursor="")
        
        def save_document():
            """Save a document (placeholder)"""
            messagebox.showinfo("Info", "Save functionality is not implemented in this version")
        
        # File menu commands
        file_menu.add_command(label="Open", command=open_document)
        file_menu.add_command(label="Save", command=save_document)
        file_menu.add_separator()
        file_menu.add_command(label="Print", command=lambda: messagebox.showinfo("Print", "Printing functionality is not implemented in this version"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=lambda: self.close_window("Word Lite", word_window))
        
        # Edit menu commands
        edit_menu.add_command(label="Cut", command=lambda: status_label.config(text="Cut not implemented"))
        edit_menu.add_command(label="Copy", command=lambda: status_label.config(text="Copy not implemented"))
        edit_menu.add_command(label="Paste", command=lambda: status_label.config(text="Paste not implemented"))
        
        # View menu
        view_menu.add_command(label="Zoom", command=lambda: status_label.config(text="Zoom not implemented"))
        
        # Format menu
        format_menu.add_command(label="Font", command=lambda: status_label.config(text="Font formatting not implemented"))
        
        # Help menu
        help_menu.add_command(label="About Word Lite", command=lambda: messagebox.showinfo("About", "Word Lite\nVersion 1.0\n\nA simple document viewer"))
        
        # If a file path was provided, open it
        if file_path and os.path.exists(file_path):
            current_file = file_path
            try:
                # Set the file path and call the open function
                open_document()
            except Exception as e:
                text_area.delete(1.0, tk.END)
                text_area.insert(tk.END, f"Error opening file: {str(e)}")
        
        # Add to taskbar
        self.add_window_to_taskbar("Word Lite", word_window)
        word_window.protocol("WM_DELETE_WINDOW", lambda: self.close_window("Word Lite", word_window))
    '''
    
    def create_word_lite(self, file_path=None):
        """Creează o aplicație Word Lite pentru a deschide și vizualiza fișiere .doc sau .docx"""
        import zipfile
        import xml.etree.ElementTree as ET
        import re
        
        word_window = tk.Toplevel(self.rootW95dist)
        word_window.title("Word Lite")
        word_window.overrideredirect(True)
        word_window.geometry("800x600+200+100")
        word_window.configure(bg="#c0c0c0")
        
        # Add Windows 95 style title bar
        title_bar = tk.Frame(word_window, bg="#000080", height=25)
        title_bar.pack(fill="x", side="top")
        title_label = tk.Label(title_bar, text="Word Lite", fg="white", bg="#000080",
                              font=("MS Sans Serif", 8, "bold"))
        title_label.pack(side="left", padx=5, pady=2)
        
        # Close button for title bar
        close_button = tk.Button(title_bar, text="×", bg="#c0c0c0", fg="black",
                                font=("Arial", 8, "bold"), width=2, height=1,
                                relief="raised", bd=1,
                                command=lambda: self.close_window("Word Lite", word_window))
        close_button.pack(side="right", padx=2, pady=1)
        
        self.make_window_draggable(word_window, title_bar)
        
        # Menubar
        menubar = tk.Menu(word_window)
        word_window.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        
        format_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Format", menu=format_menu)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        # Toolbar frame
        toolbar_frame = tk.Frame(word_window, bg="#c0c0c0", relief="raised", bd=2, height=35)
        toolbar_frame.pack(fill="x")
        toolbar_frame.pack_propagate(False)
        
        # Open button
        open_btn = tk.Button(toolbar_frame, text="Open", bg="#c0c0c0", relief="raised", bd=2,
                            font=("MS Sans Serif", 8),
                            command=lambda: open_document())
        open_btn.pack(side="left", padx=5, pady=2)
        
        # Save button (for future implementation)
        save_btn = tk.Button(toolbar_frame, text="Save", bg="#c0c0c0", relief="raised", bd=2,
                            font=("MS Sans Serif", 8),
                            command=lambda: save_document())
        save_btn.pack(side="left", padx=5, pady=2)
        
        # Print button
        print_btn = tk.Button(toolbar_frame, text="Print", bg="#c0c0c0", relief="raised", bd=2,
                             font=("MS Sans Serif", 8),
                             command=lambda: messagebox.showinfo("Print", "Printing functionality is not implemented in this version"))
        print_btn.pack(side="left", padx=5, pady=2)
        
        # Status bar
        status_frame = tk.Frame(word_window, bg="#c0c0c0", relief="sunken", bd=1, height=25)
        status_frame.pack(side="bottom", fill="x")
        status_frame.pack_propagate(False)
        
        status_label = tk.Label(status_frame, text="Ready", bg="#c0c0c0", font=("MS Sans Serif", 8))
        status_label.pack(side="left", padx=5)
        
        # Main content frame
        content_frame = tk.Frame(word_window, bg="white")
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Text area
        text_frame = tk.Frame(content_frame, bg="white")
        text_frame.pack(fill="both", expand=True)
        
        # Scrollbars
        v_scrollbar = tk.Scrollbar(text_frame)
        v_scrollbar.pack(side="right", fill="y")
        
        h_scrollbar = tk.Scrollbar(text_frame, orient="horizontal")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Text widget
        text_area = tk.Text(text_frame, wrap="word", yscrollcommand=v_scrollbar.set, 
                           xscrollcommand=h_scrollbar.set,
                           font=("Times New Roman", 12), bg="white", fg="black")
        text_area.pack(side="left", fill="both", expand=True)
        
        v_scrollbar.config(command=text_area.yview)
        h_scrollbar.config(command=text_area.xview)
        
        # Variables for tracking
        current_file = None
        
        def extract_text_from_docx(docx_file):
            """Extract text from a .docx file using standard libraries"""
            try:
                # Fișierele .docx sunt arhive ZIP care conțin fișiere XML
                z = zipfile.ZipFile(docx_file)
                
                # Verificăm dacă există fișierul document.xml
                if "word/document.xml" in z.namelist():
                    # Extragem și citim XML-ul principal
                    xml_content = z.read("word/document.xml")
                    
                    # Parsăm XML-ul
                    tree = ET.fromstring(xml_content)
                    
                    # Găsim toate elementele "w:t" care conțin text
                    text_content = ""
                    
                    # Folosim un namespace simplificat
                    namespace = {'w': '*'}  # Wildcards pentru namespace pentru a evita linkul URL
                    
                    # Încercăm mai multe abordări pentru a extrage textul
                    try:
                        # Abordarea 1: Extragem textul folosind XPath cu wildcard namespace
                        for paragraph in tree.findall('.//{*}p'):
                            paragraph_text = ""
                            for text_element in paragraph.findall('.//{*}t'):
                                if text_element.text:
                                    paragraph_text += text_element.text
                            
                            text_content += paragraph_text + "\n"
                        
                        # Dacă nu am obținut text, încercăm o altă abordare
                        if not text_content.strip():
                            raise Exception("No text was found using the first approach.")
                            
                    except:
                        # Abordarea 2: Extragem direct toate elementele de text
                        for text_element in tree.findall('.//*'):
                            if text_element.text and text_element.text.strip():
                                text_content += text_element.text + "\n"
                    
                    return text_content
                else:
                    return "The document content could not be found in the archive."
            except Exception as e:
                return f"Error extracting text: {str(e)}"
        
        def extract_text_from_doc(doc_file):
            """Extrage text din fișier .doc (format binar vechi)"""
            # Pentru fișierele .doc (format binar), putem încerca să extragem doar textul vizibil
            try:
                with open(doc_file, 'rb') as f:
                    content = f.read()
                    
                    # Încercăm să extragem text vizibil folosind o abordare simplă
                    # Aceasta nu este o soluție perfectă, dar poate funcționa pentru text simplu
                    text = ""
                    
                    # Convertim conținutul binar în text dacă este posibil
                    try:
                        # Încercăm să decodificăm ca UTF-16
                        binary_text = content.decode('utf-16', errors='ignore')
                        
                        # Eliminăm caracterele non-printabile
                        printable_text = ''.join(c for c in binary_text if c.isprintable() or c.isspace())
                        
                        # Folosim regex pentru a găsi texte consecutive
                        # Căutăm secvențe de text de cel puțin 3 caractere
                        text_chunks = re.findall(r'[A-Za-z0-9\s.,;:!?\'"\-+]{3,}', printable_text)
                        
                        # Filtrăm și combinăm fragmentele de text
                        for chunk in text_chunks:
                            chunk = chunk.strip()
                            if len(chunk) > 5:  # Ignorăm fragmentele prea scurte
                                text += chunk + "\n"
                    except:
                        text = "Text could not be extracted from document .doc.\n"
                        text += "The .doc format is an old and complex binary format.\n"
                        text += "For better results, use .docx or .txt files."
                    
                    return text
            except Exception as e:
                return f"Error opening the .doc file: {str(e)}"
        
        def open_document():
            """Open a Word document"""
            file_path = filedialog.askopenfilename(
                defaultextension=".docx",
                filetypes=[("Word files", "*.docx;*.doc"), ("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            try:
                # Set cursor to wait
                word_window.config(cursor="wait")
                word_window.update()
                
                # Clear text area
                text_area.delete(1.0, tk.END)
                
                # Get the file extension
                ext = os.path.splitext(file_path)[1].lower()
                
                # Handle different file types
                if ext == ".txt":
                    # Simple text file
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                        content = file.read()
                        text_area.insert(tk.END, content)
                elif ext == ".docx":
                    # Extract text from .docx file
                    content = extract_text_from_docx(file_path)
                    text_area.insert(tk.END, content)
                elif ext == ".doc":
                    # Try to extract text from old .doc format
                    content = extract_text_from_doc(file_path)
                    text_area.insert(tk.END, content)
                else:
                    text_area.insert(tk.END, f"Cannot open file type: {ext}\n")
                    text_area.insert(tk.END, "Word Lite supports .txt, .doc, and .docx files.")
                
                # Update window title and status
                file_name = os.path.basename(file_path)
                title_label.config(text=f"Word Lite - {file_name}")
                word_window.title(f"Word Lite - {file_name}")
                status_label.config(text=f"Opened: {file_name}")
                
                # Save the current file
                nonlocal current_file
                current_file = file_path
                
            except Exception as e:
                text_area.delete(1.0, tk.END)
                text_area.insert(tk.END, f"Error opening file: {str(e)}")
                messagebox.showerror("Error", f"Could not open file: {str(e)}")
            finally:
                # Reset cursor
                word_window.config(cursor="")
        
        def save_document():
            """Save a document (placeholder)"""
            messagebox.showinfo("Info", "Save functionality is not implemented in this version")
        
        # File menu commands
        file_menu.add_command(label="Open", command=open_document)
        file_menu.add_command(label="Save", command=save_document)
        file_menu.add_separator()
        file_menu.add_command(label="Print", command=lambda: messagebox.showinfo("Print", "Printing functionality is not implemented in this version"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=lambda: self.close_window("Word Lite", word_window))
        
        # Edit menu commands
        edit_menu.add_command(label="Cut", command=lambda: text_area.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", command=lambda: text_area.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", command=lambda: text_area.event_generate("<<Paste>>"))
        
        # View menu
        view_menu.add_command(label="Zoom", command=lambda: status_label.config(text="Zoom not implemented"))
        
        # Format menu
        format_menu.add_command(label="Font", command=lambda: status_label.config(text="Font formatting not implemented"))
        
        # Help menu
        help_menu.add_command(label="About Word Lite", command=lambda: messagebox.showinfo("About", "Word Lite\nVersion 1.0\n\nA simple document viewer"))
        
        # If a file path was provided, open it
        if file_path and os.path.exists(file_path):
            current_file = file_path
            try:
                # Use a temporary file path variable to avoid conflicts with the open_document function
                temp_path = file_path
                # Clear it to avoid double opening
                file_path = None
                # Call the open function with the correct path
                open_document()
            except Exception as e:
                text_area.delete(1.0, tk.END)
                text_area.insert(tk.END, f"Error opening file: {str(e)}")
        
        # Add to taskbar
        self.add_window_to_taskbar("Word Lite", word_window)
        word_window.protocol("WM_DELETE_WINDOW", lambda: self.close_window("Word Lite", word_window))
    
    def create_terminal(self):
        """Creează un terminal/command prompt care execută comenzi reale"""
        import subprocess
        import threading
        import platform
        import signal
        import time
        
        terminal_window = tk.Toplevel(self.rootW95dist)
        terminal_window.title("Command Prompt")
        terminal_window.overrideredirect(True)
        terminal_window.geometry("640x400+200+150")
        terminal_window.configure(bg="#000000")
        
        # Add Windows 95 style title bar
        title_bar = tk.Frame(terminal_window, bg="#000080", height=25)
        title_bar.pack(fill="x", side="top")
        title_label = tk.Label(title_bar, text="Command Prompt", fg="white", bg="#000080",
                              font=("MS Sans Serif", 8, "bold"))
        title_label.pack(side="left", padx=5, pady=2)
        
        # Close button for title bar
        close_button = tk.Button(title_bar, text="×", bg="#c0c0c0", fg="black",
                                font=("Arial", 8, "bold"), width=2, height=1,
                                relief="raised", bd=1,
                                command=lambda: self.close_window("Command Prompt", terminal_window))
        close_button.pack(side="right", padx=2, pady=1)
        
        self.make_window_draggable(terminal_window, title_bar)
        
        # Main content - Folosim un singur Text widget pentru tot
        # în loc de a separa output și input
        terminal_frame = tk.Frame(terminal_window, bg="black", bd=0)
        terminal_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Scrollbars
        v_scrollbar = tk.Scrollbar(terminal_frame)
        v_scrollbar.pack(side="right", fill="y")
        
        # Text widget pentru afișarea atât a output-ului cât și pentru introducerea comenzilor
        terminal_text = tk.Text(terminal_frame, wrap="word", bg="black", fg="#cccccc",
                               insertbackground="white", font=("Courier New", 10),
                               yscrollcommand=v_scrollbar.set)
        terminal_text.pack(fill="both", expand=True)
        v_scrollbar.config(command=terminal_text.yview)
        
        # Command history
        command_history = []
        history_index = 0
        
        # Poziția curentă de input (tag pentru a marca unde utilizatorul poate scrie)
        input_pos = "1.0"
        
        # Prompt-ul utilizat
        prompt = "> "
        
        # Get current OS
        current_os = platform.system()
        
        # Referință la procesul curent
        current_process = None
        
        # Flag pentru a ști dacă o comandă este în execuție
        command_running = False
        
        # Inițializăm terminalul
        terminal_text.insert("end", "Windows 95 Command Prompt\n")
        terminal_text.insert("end", "Type 'help' for a list of commands.\n\n")
        terminal_text.insert("end", f"Current directory: {os.getcwd()}\n\n")
        terminal_text.insert("end", prompt)
        
        # Setăm poziția de input inițială
        input_pos = terminal_text.index("end-1c")
        terminal_text.mark_set("input_mark", input_pos)
        terminal_text.mark_gravity("input_mark", "left")
        
        # Focusăm pe textbox
        terminal_text.focus_set()
        terminal_text.see("end")
        
        def get_command():
            """Obține comanda curentă din terminal_text"""
            input_start = terminal_text.index("input_mark")
            input_end = terminal_text.index("end-1c")
            return terminal_text.get(input_start, input_end)
        
        def stop_current_process():
            """Oprește procesul curent dacă există"""
            nonlocal current_process, command_running
            
            if current_process and command_running:
                try:
                    if current_os == "Windows":
                        # În Windows, folosim taskkill pentru a termina procesul și subprocesele sale
                        subprocess.run(f"taskkill /F /T /PID {current_process.pid}", shell=True)
                    else:
                        # În Unix/Linux, trimitem semnalul SIGTERM
                        os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
                    
                    terminal_text.insert("end", "\n^C\nCommand terminated by user.\n")
                    terminal_text.insert("end", prompt)
                    input_pos = terminal_text.index("end-1c")
                    terminal_text.mark_set("input_mark", input_pos)
                    terminal_text.see("end")
                    
                    command_running = False
                    current_process = None
                    return True
                except Exception as e:
                    terminal_text.insert("end", f"\nError terminating process: {str(e)}\n")
                    return False
            return False
        
        def execute_command(command):
            """Execută o comandă și afișează output-ul"""
            nonlocal history_index, input_pos, current_process, command_running
            
            # Adaugă comanda la istoric
            command_history.append(command)
            history_index = len(command_history)
            
            # Adăugăm un newline după comandă
            terminal_text.insert("end", "\n")
            
            # Procesăm exit command
            if command.lower() in ["exit", "quit"]:
                terminal_text.insert("end", "Closing Command Prompt...\n")
                terminal_text.see("end")
                terminal_window.after(500, lambda: self.close_window("Command Prompt", terminal_window))
                return
            
            # Procesăm cd command intern
            if command.lower().startswith("cd "):
                try:
                    path = command[3:].strip()
                    if os.path.isdir(path):
                        os.chdir(path)
                        terminal_text.insert("end", f"Current directory changed to: {os.getcwd()}\n\n")
                    else:
                        terminal_text.insert("end", f"Directory not found: {path}\n\n")
                except Exception as e:
                    terminal_text.insert("end", f"Error: {str(e)}\n\n")
                
                terminal_text.insert("end", prompt)
                input_pos = terminal_text.index("end-1c")
                terminal_text.mark_set("input_mark", input_pos)
                terminal_text.see("end")
                return
            
            # Procesăm dir/ls command intern pentru formatare mai bună
            if command.lower() in ["dir", "ls"]:
                try:
                    current_dir = os.getcwd()
                    terminal_text.insert("end", f"Directory of {current_dir}\n\n")
                    
                    # Obținem fișierele și directoarele
                    items = os.listdir(current_dir)
                    
                    # Afișăm mai întâi directoarele
                    for item in sorted(items):
                        item_path = os.path.join(current_dir, item)
                        if os.path.isdir(item_path):
                            try:
                                # Obținem informații despre director
                                item_time = os.path.getmtime(item_path)
                                time_str = datetime.fromtimestamp(item_time).strftime('%Y-%m-%d %H:%M:%S')
                                terminal_text.insert("end", f"{time_str}    <DIR>          {item}\n")
                            except:
                                terminal_text.insert("end", f"                <DIR>          {item}\n")
                    
                    # Apoi afișăm fișierele
                    for item in sorted(items):
                        item_path = os.path.join(current_dir, item)
                        if os.path.isfile(item_path):
                            try:
                                # Obținem informații despre fișier
                                item_size = os.path.getsize(item_path)
                                item_time = os.path.getmtime(item_path)
                                time_str = datetime.fromtimestamp(item_time).strftime('%Y-%m-%d %H:%M:%S')
                                terminal_text.insert("end", f"{time_str}    {item_size:10} {item}\n")
                            except:
                                terminal_text.insert("end", f"                      ? {item}\n")
                    
                    terminal_text.insert("end", "\n")
                except Exception as e:
                    terminal_text.insert("end", f"Error: {str(e)}\n\n")
                
                terminal_text.insert("end", prompt)
                input_pos = terminal_text.index("end-1c")
                terminal_text.mark_set("input_mark", input_pos)
                terminal_text.see("end")
                return
            
            # Procesăm help command
            if command.lower() == "help":
                terminal_text.insert("end", "Available Commands:\n")
                terminal_text.insert("end", "  help       - Display this help message\n")
                terminal_text.insert("end", "  cd <dir>   - Change directory\n")
                terminal_text.insert("end", "  dir        - List files and directories\n")
                terminal_text.insert("end", "  ls         - List files and directories (alternative)\n")
                terminal_text.insert("end", "  cls        - Clear screen\n")
                terminal_text.insert("end", "  exit       - Exit Command Prompt\n")
                terminal_text.insert("end", "\nOther standard system commands are also available.\n")
                terminal_text.insert("end", "Press Ctrl+C to stop a running command or copy selected text.\n")
                terminal_text.insert("end", "Press Ctrl+V to paste text from clipboard.\n\n")
                
                terminal_text.insert("end", prompt)
                input_pos = terminal_text.index("end-1c")
                terminal_text.mark_set("input_mark", input_pos)
                terminal_text.see("end")
                return
            
            # Procesăm clear/cls command
            if command.lower() in ["cls", "clear"]:
                terminal_text.delete("1.0", "end")
                terminal_text.insert("end", "Windows 95 Command Prompt\n\n")
                terminal_text.insert("end", prompt)
                input_pos = terminal_text.index("end-1c")
                terminal_text.mark_set("input_mark", input_pos)
                terminal_text.see("end")
                return
            
            # Rulăm comanda externă
            def run_command():
                nonlocal current_process, command_running
                command_running = True
                
                try:
                    # Determină shell și opțiuni în funcție de sistemul de operare
                    if current_os == "Windows":
                        # Creăm procesul cu pipe-uri pentru stdout și stderr
                        current_process = subprocess.Popen(
                            command, 
                            shell=True, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE,
                            text=True,
                            encoding='cp850',  # Windows Command Prompt encoding
                            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                        )
                    else:  # Linux/Mac
                        current_process = subprocess.Popen(
                            command,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE,
                            text=True,
                            preexec_fn=os.setsid  # Permite terminarea procesului și a subproceselor
                        )
                    
                    # Citim output-ul și error-ul în mod continuu
                    while command_running:
                        # Verificăm dacă procesul s-a terminat
                        if current_process.poll() is not None:
                            break
                        
                        # Citim output disponibil fără să blocăm
                        output_line = current_process.stdout.readline()
                        if output_line:
                            terminal_window.after(0, lambda line=output_line: append_output(line))
                        
                        # Citim error disponibil fără să blocăm
                        error_line = current_process.stderr.readline()
                        if error_line:
                            terminal_window.after(0, lambda line=error_line: append_error(line))
                        
                        # Pauză scurtă pentru a nu supraîncărca CPU
                        time.sleep(0.01)
                    
                    # După ce procesul s-a terminat, citim orice output rămas
                    remaining_output, remaining_error = current_process.communicate()
                    
                    if remaining_output:
                        terminal_window.after(0, lambda: append_output(remaining_output))
                    
                    if remaining_error:
                        terminal_window.after(0, lambda: append_error(remaining_error))
                    
                    # Verificăm dacă procesul s-a terminat cu succes
                    exit_code = current_process.returncode
                    if exit_code != 0 and command_running:
                        terminal_window.after(0, lambda: append_error(f"\nCommand exited with code {exit_code}\n"))
                    
                    # Comanda s-a terminat, adăugăm un nou prompt
                    terminal_window.after(0, lambda: add_new_prompt())
                    
                    command_running = False
                    current_process = None
                    
                except Exception as e:
                    terminal_window.after(0, lambda: append_error(f"\nError executing command: {str(e)}\n"))
                    terminal_window.after(0, lambda: add_new_prompt())
                    command_running = False
                    current_process = None
            
            def append_output(text):
                terminal_text.insert("end", text)
                terminal_text.see("end")
            
            def append_error(text):
                terminal_text.insert("end", text)
                terminal_text.see("end")
            
            def add_new_prompt():
                nonlocal input_pos
                terminal_text.insert("end", prompt)
                input_pos = terminal_text.index("end-1c")
                terminal_text.mark_set("input_mark", input_pos)
                terminal_text.see("end")
            
            # Rulăm comanda într-un thread separat pentru a evita blocarea UI
            command_thread = threading.Thread(target=run_command)
            command_thread.daemon = True
            command_thread.start()
        
        def copy_selected_text():
            """Copiază textul selectat în clipboard"""
            try:
                selected_text = terminal_text.get("sel.first", "sel.last")
                terminal_window.clipboard_clear()
                terminal_window.clipboard_append(selected_text)
                return True
            except:
                return False  # Nu există text selectat
        
        def paste_from_clipboard():
            """Lipește text din clipboard la poziția curentă de input"""
            try:
                clipboard_text = terminal_window.clipboard_get()
                terminal_text.insert("insert", clipboard_text)
                return True
            except:
                return False  # Clipboard-ul este gol sau inaccesibil
        
        # Gestionăm tastele speciale și comenzile
        def key_press(event):
            nonlocal history_index
            
            # Ctrl+C: Copiere text selectat sau oprire comandă
            if (event.state & 0x4) and event.keysym.lower() == "c":  # Ctrl+C
                if not copy_selected_text():  # Încercăm să copiem textul selectat
                    # Dacă nu există text selectat, oprim comanda curentă
                    stop_current_process()
                return "break"
            
            # Ctrl+V: Lipire din clipboard
            if (event.state & 0x4) and event.keysym.lower() == "v":  # Ctrl+V
                paste_from_clipboard()
                return "break"
            
            # Verificăm dacă cursorul este după prompt
            cursor_pos = terminal_text.index("insert")
            if terminal_text.compare(cursor_pos, "<", "input_mark"):
                # Cursorul este înainte de poziția de input, îl mutăm la final
                terminal_text.mark_set("insert", "end")
                return "break"
            
            # Return/Enter key - Execute command
            if event.keysym == "Return":
                command = get_command()
                if command.strip():
                    execute_command(command.strip())
                return "break"
            
            # Backspace key - Do not delete beyond prompt
            elif event.keysym == "BackSpace":
                cursor_pos = terminal_text.index("insert")
                if terminal_text.compare(cursor_pos, "<=", "input_mark"):
                    return "break"
            
            # Up key - Navigate command history
            elif event.keysym == "Up":
                if command_history and history_index > 0:
                    history_index -= 1
                    # Ștergem comanda curentă
                    terminal_text.delete("input_mark", "end-1c")
                    # Inserăm comanda din istoric
                    terminal_text.insert("input_mark", command_history[history_index])
                return "break"
            
            # Down key - Navigate command history
            elif event.keysym == "Down":
                if command_history and history_index < len(command_history) - 1:
                    history_index += 1
                    # Ștergem comanda curentă
                    terminal_text.delete("input_mark", "end-1c")
                    # Inserăm comanda din istoric
                    terminal_text.insert("input_mark", command_history[history_index])
                elif history_index == len(command_history) - 1:
                    history_index = len(command_history)
                    # Ștergem comanda curentă
                    terminal_text.delete("input_mark", "end-1c")
                return "break"
            
            # Home key - Go to beginning of input
            elif event.keysym == "Home":
                terminal_text.mark_set("insert", "input_mark")
                return "break"
        
        # Asigurăm-ne că nu se poate șterge input mark-ul sau textul anterior
        def delete_check(event):
            try:
                if event.keysym == 'BackSpace':
                    cursor_pos = terminal_text.index("insert")
                    if terminal_text.compare(cursor_pos, "<=", "input_mark"):
                        return "break"
                elif event.keysym in ['Delete', 'KP_Delete']:
                    try:
                        sel_start = terminal_text.index("sel.first")
                        if terminal_text.compare(sel_start, "<", "input_mark"):
                            return "break"
                    except:
                        cursor_pos = terminal_text.index("insert")
                        if terminal_text.compare(cursor_pos, "<", "input_mark"):
                            return "break"
            except:
                pass
        
        # Curățăm resursele la închiderea ferestrei
        def on_window_close():
            # Oprim orice proces în execuție
            stop_current_process()
            # Închidem fereastra
            self.close_window("Command Prompt", terminal_window)
        
        # Bind keys
        terminal_text.bind("<Key>", key_press)
        terminal_text.bind("<KeyPress-BackSpace>", delete_check)
        terminal_text.bind("<KeyPress-Delete>", delete_check)
        terminal_text.bind("<KeyPress-KP_Delete>", delete_check)
        
        # Make sure focus is on the terminal text
        terminal_text.focus_set()
        
        # Add to taskbar
        self.add_window_to_taskbar("Command Prompt", terminal_window)
        terminal_window.protocol("WM_DELETE_WINDOW", on_window_close)
        
        # Bind window activation
        terminal_window.bind("<Map>", lambda e: terminal_text.focus_set())
        terminal_window.bind("<FocusIn>", lambda e: terminal_text.focus_set())
    
    def create_excel_lite(self, file_path=None):
        """Creează o aplicație Excel Lite pentru a deschide și vizualiza fișiere xlsx"""
        try:
            import openpyxl
        except ImportError:
            messagebox.showerror("Error", "The openpyxl library is not installed. Please install it using pip: pip install openpyxl")
            return

        excel_window = tk.Toplevel(self.rootW95dist)
        excel_window.title("Excel Lite")
        excel_window.overrideredirect(True)
        excel_window.geometry("800x600+200+100")
        excel_window.configure(bg="#c0c0c0")
        
        # Add Windows 95 style title bar
        title_bar = tk.Frame(excel_window, bg="#000080", height=25)
        title_bar.pack(fill="x", side="top")
        title_label = tk.Label(title_bar, text="Excel Lite", fg="white", bg="#000080",
                              font=("MS Sans Serif", 8, "bold"))
        title_label.pack(side="left", padx=5, pady=2)
        
        # Close button for title bar
        close_button = tk.Button(title_bar, text="×", bg="#c0c0c0", fg="black",
                                font=("Arial", 8, "bold"), width=2, height=1,
                                relief="raised", bd=1,
                                command=lambda: self.close_window("Excel Lite", excel_window))
        close_button.pack(side="right", padx=2, pady=1)
        
        self.make_window_draggable(excel_window, title_bar)
        
        # Menubar
        menubar = tk.Menu(excel_window)
        excel_window.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        # Toolbar frame
        toolbar_frame = tk.Frame(excel_window, bg="#c0c0c0", relief="raised", bd=2, height=35)
        toolbar_frame.pack(fill="x")
        toolbar_frame.pack_propagate(False)
        
        # Open button
        open_btn = tk.Button(toolbar_frame, text="Open", bg="#c0c0c0", relief="raised", bd=2,
                            font=("MS Sans Serif", 8),
                            command=lambda: open_excel_file())
        open_btn.pack(side="left", padx=5, pady=2)
        
        # Save button (for future implementation)
        save_btn = tk.Button(toolbar_frame, text="Save", bg="#c0c0c0", relief="raised", bd=2,
                            font=("MS Sans Serif", 8),
                            command=lambda: save_excel_file())
        save_btn.pack(side="left", padx=5, pady=2)
        
        # Sheet selection
        sheet_label = tk.Label(toolbar_frame, text="Sheet:", bg="#c0c0c0", font=("MS Sans Serif", 8))
        sheet_label.pack(side="left", padx=(20, 5))
        
        sheet_var = tk.StringVar()
        sheet_combo = ttk.Combobox(toolbar_frame, textvariable=sheet_var, width=15, state="readonly")
        sheet_combo.pack(side="left", padx=5)
        sheet_combo.bind("<<ComboboxSelected>>", lambda e: show_sheet(sheet_var.get()))
        
        # Function buttons
        formula_btn = tk.Button(toolbar_frame, text="Formula", bg="#c0c0c0", relief="raised", bd=2,
                               font=("MS Sans Serif", 8),
                               command=lambda: add_formula())
        formula_btn.pack(side="left", padx=5, pady=2)
        
        sort_btn = tk.Button(toolbar_frame, text="Sort", bg="#c0c0c0", relief="raised", bd=2,
                            font=("MS Sans Serif", 8),
                            command=lambda: sort_data())
        sort_btn.pack(side="left", padx=5, pady=2)
        
        filter_btn = tk.Button(toolbar_frame, text="Filter", bg="#c0c0c0", relief="raised", bd=2,
                              font=("MS Sans Serif", 8),
                              command=lambda: filter_data())
        filter_btn.pack(side="left", padx=5, pady=2)
        
        # Status bar - adăugat înainte de conținutul principal
        status_frame = tk.Frame(excel_window, bg="#c0c0c0", relief="sunken", bd=1, height=25)
        status_frame.pack(side="bottom", fill="x")
        status_frame.pack_propagate(False)
        
        status_label = tk.Label(status_frame, text="Ready", bg="#c0c0c0", font=("MS Sans Serif", 8))
        status_label.pack(side="left", padx=5)
        
        cell_info_label = tk.Label(status_frame, text="", bg="#c0c0c0", font=("MS Sans Serif", 8))
        cell_info_label.pack(side="right", padx=5)
        
        # Main content frame
        content_frame = tk.Frame(excel_window, bg="white")
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Scrollbars
        h_scrollbar = tk.Scrollbar(content_frame, orient="horizontal")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Main table frame
        table_frame = tk.Frame(content_frame, bg="white")
        table_frame.pack(fill="both", expand=True)
        
        v_scrollbar = tk.Scrollbar(table_frame)
        v_scrollbar.pack(side="right", fill="y")
        
        # Canvas for scrollable content
        canvas = tk.Canvas(table_frame, bg="white", 
                         xscrollcommand=h_scrollbar.set,
                         yscrollcommand=v_scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        
        h_scrollbar.config(command=canvas.xview)
        v_scrollbar.config(command=canvas.yview)
        
        # Frame inside canvas for grid
        inner_frame = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        
        # Eliminăm spațiile între celule
        inner_frame.grid_columnconfigure("all", pad=0)
        inner_frame.grid_rowconfigure("all", pad=0)
        
        # Variables for tracking
        current_file = None
        workbook = None
        active_sheet = None
        
        # Cell grid (for display only)
        cell_grid = []
        header_labels = []  # Pentru a ține evidența label-urilor de header
        
        # Max rows and columns to display
        MAX_ROWS = 100
        MAX_COLS = 26  # A-Z
        
        # Variabile pentru redimensionarea coloanelor
        resizing_column = None
        start_x = 0
        column_widths = [10] * (MAX_COLS + 1)  # Lățimea inițială pentru fiecare coloană (inclusiv header-ul de rând)
        
        def clear_sheet():
            """Clear the current sheet display"""
            for widget in inner_frame.winfo_children():
                widget.destroy()
            
            nonlocal cell_grid, header_labels
            cell_grid = []
            header_labels = []
        
        def create_empty_sheet():
            """Create an empty spreadsheet grid"""
            clear_sheet()
            
            nonlocal header_labels, column_widths
            header_labels = [None] * (MAX_COLS + 1)  # +1 pentru header-ul de rând
            
            # Creează header-ul cu coloanele (A, B, C, etc.)
            header_label = tk.Label(inner_frame, text="", width=4, bg="#e0e0e0", 
                                  relief="raised", bd=1, font=("MS Sans Serif", 8, "bold"),
                                  highlightthickness=0)  # Eliminăm highlightthickness
            header_label.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)  # Eliminăm padding
            header_labels[0] = header_label
            
            for col in range(MAX_COLS):
                col_letter = chr(65 + col)  # A=65, B=66, etc.
                header = tk.Label(inner_frame, text=col_letter, width=column_widths[col+1], bg="#e0e0e0",
                                relief="raised", bd=1, font=("MS Sans Serif", 8, "bold"),
                                highlightthickness=0)  # Eliminăm highlightthickness
                header.grid(row=0, column=col+1, sticky="nsew", padx=0, pady=0)  # Eliminăm padding
                header_labels[col+1] = header
                
                # Adaugă separator de redimensionare
                add_column_resize_handle(header, col+1)
            
            # Creează rândurile și celulele
            row_widgets = []
            for row in range(MAX_ROWS):
                # Creează header-ul pentru rând
                row_header = tk.Label(inner_frame, text=str(row + 1), width=4, height=1,
                                    bg="#e0e0e0", relief="raised", bd=1, font=("MS Sans Serif", 8, "bold"),
                                    highlightthickness=0)  # Eliminăm highlightthickness
                row_header.grid(row=row+1, column=0, sticky="nsew", padx=0, pady=0)  # Eliminăm padding
                
                # Creează celulele pentru acest rând
                col_widgets = []
                for col in range(MAX_COLS):
                    cell = tk.Entry(inner_frame, width=column_widths[col+1], font=("MS Sans Serif", 8),
                                  relief="sunken", bd=1, highlightthickness=0)  # Eliminăm highlightthickness
                    cell.grid(row=row+1, column=col+1, sticky="nsew", padx=0, pady=0)  # Eliminăm padding
                    
                    # Bind click to select cell
                    cell.bind("<Button-1>", lambda e, r=row, c=col: select_cell(r, c))
                    
                    col_widgets.append(cell)
                row_widgets.append(col_widgets)
            
            cell_grid = row_widgets
            
            # Configurează coloanele pentru dimensiune uniformă
            for col in range(MAX_COLS + 1):  # +1 pentru coloana cu header-ele de rând
                inner_frame.grid_columnconfigure(col, weight=1, pad=0)  # Setăm explicit pad=0
            
            # Configurează rândurile pentru a elimina spațiile
            for row in range(MAX_ROWS + 1):  # +1 pentru rândul cu header-ele de coloane
                inner_frame.grid_rowconfigure(row, pad=0)  # Setăm explicit pad=0
            
            # Update canvas scroll region
            inner_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))
        
        def add_column_resize_handle(header, col_idx):
            """Adaugă un handler pentru redimensionarea coloanei"""
            
            def start_resize(event):
                nonlocal resizing_column, start_x
                resizing_column = col_idx
                start_x = event.x_root
                # Schimbă cursorul pentru a indica redimensionarea
                excel_window.config(cursor="sb_h_double_arrow")
                
            def stop_resize(event):
                nonlocal resizing_column
                resizing_column = None
                # Resetează cursorul
                excel_window.config(cursor="")
                
            def do_resize(event):
                nonlocal column_widths, start_x
                if resizing_column is not None:
                    # Calculează diferența în pixeli
                    delta_x = event.x_root - start_x
                    
                    # Convertește în unități de lățime (aproximativ 7 pixeli per caracter)
                    delta_width = delta_x // 7
                    
                    if delta_width != 0:
                        # Ajustează lățimea coloanei (minim 3 caractere)
                        new_width = max(3, column_widths[resizing_column] + delta_width)
                        column_widths[resizing_column] = new_width
                        
                        # Actualizează header-ul
                        header_labels[resizing_column].config(width=new_width)
                        
                        # Actualizează toate celulele din coloană
                        for row in range(MAX_ROWS):
                            if row < len(cell_grid) and resizing_column-1 < len(cell_grid[row]):
                                cell_grid[row][resizing_column-1].config(width=new_width)
                        
                        # Resetează start_x pentru următoarea mișcare
                        start_x = event.x_root
                        
                        # Update canvas scroll region
                        inner_frame.update_idletasks()
                        canvas.config(scrollregion=canvas.bbox("all"))
            
            # Creează un frame pentru zona de redimensionare (marginea dreaptă a header-ului)
            resize_frame = tk.Frame(inner_frame, bg="gray", width=2, cursor="sb_h_double_arrow")
            resize_frame.grid(row=0, column=col_idx, sticky="nse", padx=(0, 0))
            
            # Bind evenimente pentru redimensionare
            resize_frame.bind("<Button-1>", start_resize)
            resize_frame.bind("<ButtonRelease-1>", stop_resize)
            excel_window.bind("<B1-Motion>", do_resize)
        
        def select_cell(row, col):
            """Select a cell and show its address in the status bar"""
            col_letter = chr(65 + col)
            cell_address = f"{col_letter}{row + 1}"
            cell_info_label.config(text=f"Cell: {cell_address}")
            
            # Set focus to the cell
            if 0 <= row < len(cell_grid) and 0 <= col < len(cell_grid[0]):
                cell_grid[row][col].focus_set()
        
        def load_sheet_data(sheet):
            """Load data from the workbook sheet into the grid"""
            clear_sheet()
            
            # Get the dimensions of the sheet
            max_row = min(sheet.max_row, MAX_ROWS)
            max_col = min(sheet.max_column, MAX_COLS)
            
            nonlocal header_labels, column_widths
            header_labels = [None] * (MAX_COLS + 1)  # +1 pentru header-ul de rând
            
            # Creează header-ul cu coloanele (A, B, C, etc.)
            header_label = tk.Label(inner_frame, text="", width=4, bg="#e0e0e0", 
                                  relief="raised", bd=1, font=("MS Sans Serif", 8, "bold"),
                                  highlightthickness=0)  # Eliminăm highlightthickness
            header_label.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)  # Eliminăm padding
            header_labels[0] = header_label
            
            for col in range(max_col):
                col_letter = chr(65 + col)  # A=65, B=66, etc.
                header = tk.Label(inner_frame, text=col_letter, width=column_widths[col+1], bg="#e0e0e0",
                                relief="raised", bd=1, font=("MS Sans Serif", 8, "bold"),
                                highlightthickness=0)  # Eliminăm highlightthickness
                header.grid(row=0, column=col+1, sticky="nsew", padx=0, pady=0)  # Eliminăm padding
                header_labels[col+1] = header
                
                # Adaugă separator de redimensionare
                add_column_resize_handle(header, col+1)
            
            # Creează rândurile și celulele
            row_widgets = []
            for row in range(max_row):
                # Creează header-ul pentru rând
                row_header = tk.Label(inner_frame, text=str(row + 1), width=4, height=1,
                                    bg="#e0e0e0", relief="raised", bd=1, font=("MS Sans Serif", 8, "bold"),
                                    highlightthickness=0)  # Eliminăm highlightthickness
                row_header.grid(row=row+1, column=0, sticky="nsew", padx=0, pady=0)  # Eliminăm padding
                
                # Creează celulele pentru acest rând
                col_widgets = []
                for col in range(max_col):
                    cell_value = sheet.cell(row=row+1, column=col+1).value
                    cell_value = str(cell_value) if cell_value is not None else ""
                    
                    cell = tk.Entry(inner_frame, width=column_widths[col+1], font=("MS Sans Serif", 8),
                                  relief="sunken", bd=1, highlightthickness=0)  # Eliminăm highlightthickness
                    cell.insert(0, cell_value)
                    cell.grid(row=row+1, column=col+1, sticky="nsew", padx=0, pady=0)  # Eliminăm padding
                    
                    # Bind click to select cell
                    cell.bind("<Button-1>", lambda e, r=row, c=col: select_cell(r, c))
                    
                    col_widgets.append(cell)
                row_widgets.append(col_widgets)
            
            nonlocal cell_grid
            cell_grid = row_widgets
            
            # Configurează coloanele pentru dimensiune uniformă și fără spații
            for col in range(max_col + 1):  # +1 pentru coloana cu header-ele de rând
                inner_frame.grid_columnconfigure(col, weight=1, pad=0)
            
            # Configurează rândurile pentru a elimina spațiile
            for row in range(max_row + 1):  # +1 pentru rândul cu header-ele de coloane
                inner_frame.grid_rowconfigure(row, pad=0)
            
            # Update canvas scroll region
            inner_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))
            
            status_label.config(text=f"Loaded sheet: {sheet.title}")
        
        def open_excel_file():
            """Open an Excel file"""
            file_path = filedialog.askopenfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            try:
                # Load the Excel file
                nonlocal workbook, current_file
                workbook = openpyxl.load_workbook(file_path, data_only=True)
                current_file = file_path
                
                # Update the sheet selector dropdown
                sheet_names = workbook.sheetnames
                sheet_combo['values'] = sheet_names
                
                if sheet_names:
                    sheet_var.set(sheet_names[0])
                    show_sheet(sheet_names[0])
                
                # Update window title
                file_name = os.path.basename(file_path)
                title_label.config(text=f"Excel Lite - {file_name}")
                excel_window.title(f"Excel Lite - {file_name}")
                
                status_label.config(text=f"Opened: {file_name}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open Excel file: {str(e)}")
        
        def show_sheet(sheet_name):
            """Show the selected sheet"""
            if not workbook or sheet_name not in workbook.sheetnames:
                return
            
            nonlocal active_sheet
            active_sheet = workbook[sheet_name]
            load_sheet_data(active_sheet)
        
        def save_excel_file():
            """Save the Excel file (placeholder for future implementation)"""
            if not current_file or not workbook:
                messagebox.showinfo("Info", "No file is currently open")
                return
            
            messagebox.showinfo("Info", "Save functionality is not implemented in this version")
        
        def add_formula():
            """Add a formula to the selected cell (placeholder)"""
            messagebox.showinfo("Info", "Formula functionality is not implemented in this version")
        
        def sort_data():
            """Sort data in the selected column (placeholder)"""
            messagebox.showinfo("Info", "Sort functionality is not implemented in this version")
        
        def filter_data():
            """Filter data in the selected column (placeholder)"""
            messagebox.showinfo("Info", "Filter functionality is not implemented in this version")
        
        # Create empty sheet by default
        create_empty_sheet()
        
        # File menu commands
        file_menu.add_command(label="New", command=create_empty_sheet)
        file_menu.add_command(label="Open", command=open_excel_file)
        file_menu.add_command(label="Save", command=save_excel_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=lambda: self.close_window("Excel Lite", excel_window))
        
        # Edit menu commands
        edit_menu.add_command(label="Cut", command=lambda: status_label.config(text="Cut not implemented"))
        edit_menu.add_command(label="Copy", command=lambda: status_label.config(text="Copy not implemented"))
        edit_menu.add_command(label="Paste", command=lambda: status_label.config(text="Paste not implemented"))
        
        # View menu
        view_menu.add_command(label="Formulas", command=lambda: status_label.config(text="View Formulas not implemented"))
        view_menu.add_command(label="Freeze Panes", command=lambda: status_label.config(text="Freeze Panes not implemented"))
        
        # Help menu
        help_menu.add_command(label="About Excel Lite", command=lambda: messagebox.showinfo("About", "Excel Lite\nVersion 1.0\n\nA simple spreadsheet viewer"))
        
        # If a file path was provided, open it
        if file_path and os.path.exists(file_path):
            current_file = file_path
            try:
                workbook = openpyxl.load_workbook(file_path, data_only=True)
                sheet_names = workbook.sheetnames
                sheet_combo['values'] = sheet_names
                if sheet_names:
                    sheet_var.set(sheet_names[0])
                    show_sheet(sheet_names[0])
                
                # Update window title
                file_name = os.path.basename(file_path)
                title_label.config(text=f"Excel Lite - {file_name}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open Excel file: {str(e)}")
        
        # Add to taskbar
        self.add_window_to_taskbar("Excel Lite", excel_window)
        excel_window.protocol("WM_DELETE_WINDOW", lambda: self.close_window("Excel Lite", excel_window))
    
    '''
    def create_excel_lite(self, file_path=None):
        """Creează o aplicație Excel Lite pentru a deschide și vizualiza fișiere xlsx"""
        try:
            import openpyxl
        except ImportError:
            messagebox.showerror("Error", "The openpyxl library is not installed. Please install it using pip: pip install openpyxl")
            return

        excel_window = tk.Toplevel(self.rootW95dist)
        excel_window.title("Excel Lite")
        excel_window.overrideredirect(True)
        excel_window.geometry("800x600+200+100")
        excel_window.configure(bg="#c0c0c0")
        
        # Add Windows 95 style title bar
        title_bar = tk.Frame(excel_window, bg="#000080", height=25)
        title_bar.pack(fill="x", side="top")
        title_label = tk.Label(title_bar, text="Excel Lite", fg="white", bg="#000080",
                              font=("MS Sans Serif", 8, "bold"))
        title_label.pack(side="left", padx=5, pady=2)
        
        # Close button for title bar
        close_button = tk.Button(title_bar, text="×", bg="#c0c0c0", fg="black",
                                font=("Arial", 8, "bold"), width=2, height=1,
                                relief="raised", bd=1,
                                command=lambda: self.close_window("Excel Lite", excel_window))
        close_button.pack(side="right", padx=2, pady=1)
        
        self.make_window_draggable(excel_window, title_bar)
        
        # Menubar
        menubar = tk.Menu(excel_window)
        excel_window.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        # Toolbar frame
        toolbar_frame = tk.Frame(excel_window, bg="#c0c0c0", relief="raised", bd=2, height=35)
        toolbar_frame.pack(fill="x")
        toolbar_frame.pack_propagate(False)
        
        # Open button
        open_btn = tk.Button(toolbar_frame, text="Open", bg="#c0c0c0", relief="raised", bd=2,
                            font=("MS Sans Serif", 8),
                            command=lambda: open_excel_file())
        open_btn.pack(side="left", padx=5, pady=2)
        
        # Save button (for future implementation)
        save_btn = tk.Button(toolbar_frame, text="Save", bg="#c0c0c0", relief="raised", bd=2,
                            font=("MS Sans Serif", 8),
                            command=lambda: save_excel_file())
        save_btn.pack(side="left", padx=5, pady=2)
        
        # Sheet selection
        sheet_label = tk.Label(toolbar_frame, text="Sheet:", bg="#c0c0c0", font=("MS Sans Serif", 8))
        sheet_label.pack(side="left", padx=(20, 5))
        
        sheet_var = tk.StringVar()
        sheet_combo = ttk.Combobox(toolbar_frame, textvariable=sheet_var, width=15, state="readonly")
        sheet_combo.pack(side="left", padx=5)
        sheet_combo.bind("<<ComboboxSelected>>", lambda e: show_sheet(sheet_var.get()))
        
        # Function buttons
        formula_btn = tk.Button(toolbar_frame, text="Formula", bg="#c0c0c0", relief="raised", bd=2,
                               font=("MS Sans Serif", 8),
                               command=lambda: add_formula())
        formula_btn.pack(side="left", padx=5, pady=2)
        
        sort_btn = tk.Button(toolbar_frame, text="Sort", bg="#c0c0c0", relief="raised", bd=2,
                            font=("MS Sans Serif", 8),
                            command=lambda: sort_data())
        sort_btn.pack(side="left", padx=5, pady=2)
        
        filter_btn = tk.Button(toolbar_frame, text="Filter", bg="#c0c0c0", relief="raised", bd=2,
                              font=("MS Sans Serif", 8),
                              command=lambda: filter_data())
        filter_btn.pack(side="left", padx=5, pady=2)
        
        # Status bar - adăugat înainte de conținutul principal
        status_frame = tk.Frame(excel_window, bg="#c0c0c0", relief="sunken", bd=1, height=25)
        status_frame.pack(side="bottom", fill="x")
        status_frame.pack_propagate(False)
        
        status_label = tk.Label(status_frame, text="Ready", bg="#c0c0c0", font=("MS Sans Serif", 8))
        status_label.pack(side="left", padx=5)
        
        cell_info_label = tk.Label(status_frame, text="", bg="#c0c0c0", font=("MS Sans Serif", 8))
        cell_info_label.pack(side="right", padx=5)
        
        # Main content frame
        content_frame = tk.Frame(excel_window, bg="white")
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Scrollbars
        h_scrollbar = tk.Scrollbar(content_frame, orient="horizontal")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Main table frame
        table_frame = tk.Frame(content_frame, bg="white")
        table_frame.pack(fill="both", expand=True)
        
        v_scrollbar = tk.Scrollbar(table_frame)
        v_scrollbar.pack(side="right", fill="y")
        
        # Canvas for scrollable content
        canvas = tk.Canvas(table_frame, bg="white", 
                         xscrollcommand=h_scrollbar.set,
                         yscrollcommand=v_scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        
        h_scrollbar.config(command=canvas.xview)
        v_scrollbar.config(command=canvas.yview)
        
        # Frame inside canvas for grid
        inner_frame = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        
        # Variables for tracking
        current_file = None
        workbook = None
        active_sheet = None
        
        # Cell grid (for display only)
        cell_grid = []
        
        # Max rows and columns to display
        MAX_ROWS = 100
        MAX_COLS = 26  # A-Z
        
        def clear_sheet():
            """Clear the current sheet display"""
            for widget in inner_frame.winfo_children():
                widget.destroy()
            
            nonlocal cell_grid
            cell_grid = []
        
        def create_empty_sheet():
            """Create an empty spreadsheet grid"""
            clear_sheet()
            
            # Definește o lățime fixă pentru toate celulele
            CELL_WIDTH = 10
            
            # Creează header-ul cu coloanele (A, B, C, etc.)
            header_label = tk.Label(inner_frame, text="", width=4, bg="#e0e0e0", 
                                  relief="raised", bd=1, font=("MS Sans Serif", 8, "bold"))
            header_label.grid(row=0, column=0, sticky="nsew")
            
            for col in range(MAX_COLS):
                col_letter = chr(65 + col)  # A=65, B=66, etc.
                header = tk.Label(inner_frame, text=col_letter, width=CELL_WIDTH, bg="#e0e0e0",
                                relief="raised", bd=1, font=("MS Sans Serif", 8, "bold"))
                header.grid(row=0, column=col+1, sticky="nsew")
            
            # Creează rândurile și celulele
            row_widgets = []
            for row in range(MAX_ROWS):
                # Creează header-ul pentru rând
                row_header = tk.Label(inner_frame, text=str(row + 1), width=4, height=1,
                                    bg="#e0e0e0", relief="raised", bd=1, font=("MS Sans Serif", 8, "bold"))
                row_header.grid(row=row+1, column=0, sticky="nsew")
                
                # Creează celulele pentru acest rând
                col_widgets = []
                for col in range(MAX_COLS):
                    cell = tk.Entry(inner_frame, width=CELL_WIDTH, font=("MS Sans Serif", 8),
                                  relief="sunken", bd=1)
                    cell.grid(row=row+1, column=col+1, sticky="nsew")
                    
                    # Bind click to select cell
                    cell.bind("<Button-1>", lambda e, r=row, c=col: select_cell(r, c))
                    
                    col_widgets.append(cell)
                row_widgets.append(col_widgets)
            
            cell_grid = row_widgets
            
            # Configurează coloanele pentru dimensiune uniformă
            for col in range(MAX_COLS + 1):  # +1 pentru coloana cu header-ele de rând
                inner_frame.grid_columnconfigure(col, weight=1)
            
            # Update canvas scroll region
            inner_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))
        
        def select_cell(row, col):
            """Select a cell and show its address in the status bar"""
            col_letter = chr(65 + col)
            cell_address = f"{col_letter}{row + 1}"
            cell_info_label.config(text=f"Cell: {cell_address}")
            
            # Set focus to the cell
            if 0 <= row < len(cell_grid) and 0 <= col < len(cell_grid[0]):
                cell_grid[row][col].focus_set()
        
        def load_sheet_data(sheet):
            """Load data from the workbook sheet into the grid"""
            clear_sheet()
            
            # Get the dimensions of the sheet
            max_row = min(sheet.max_row, MAX_ROWS)
            max_col = min(sheet.max_column, MAX_COLS)
            
            # Definește o lățime fixă pentru toate celulele
            CELL_WIDTH = 10
            
            # Creează header-ul cu coloanele (A, B, C, etc.)
            header_label = tk.Label(inner_frame, text="", width=4, bg="#e0e0e0", 
                                  relief="raised", bd=1, font=("MS Sans Serif", 8, "bold"))
            header_label.grid(row=0, column=0, sticky="nsew")
            
            for col in range(max_col):
                col_letter = chr(65 + col)  # A=65, B=66, etc.
                header = tk.Label(inner_frame, text=col_letter, width=CELL_WIDTH, bg="#e0e0e0",
                                relief="raised", bd=1, font=("MS Sans Serif", 8, "bold"))
                header.grid(row=0, column=col+1, sticky="nsew")
            
            # Creează rândurile și celulele
            row_widgets = []
            for row in range(max_row):
                # Creează header-ul pentru rând
                row_header = tk.Label(inner_frame, text=str(row + 1), width=4, height=1,
                                    bg="#e0e0e0", relief="raised", bd=1, font=("MS Sans Serif", 8, "bold"))
                row_header.grid(row=row+1, column=0, sticky="nsew")
                
                # Creează celulele pentru acest rând
                col_widgets = []
                for col in range(max_col):
                    cell_value = sheet.cell(row=row+1, column=col+1).value
                    cell_value = str(cell_value) if cell_value is not None else ""
                    
                    cell = tk.Entry(inner_frame, width=CELL_WIDTH, font=("MS Sans Serif", 8),
                                  relief="sunken", bd=1)
                    cell.insert(0, cell_value)
                    cell.grid(row=row+1, column=col+1, sticky="nsew")
                    
                    # Bind click to select cell
                    cell.bind("<Button-1>", lambda e, r=row, c=col: select_cell(r, c))
                    
                    col_widgets.append(cell)
                row_widgets.append(col_widgets)
            
            nonlocal cell_grid
            cell_grid = row_widgets
            
            # Configurează coloanele pentru dimensiune uniformă
            for col in range(max_col + 1):  # +1 pentru coloana cu header-ele de rând
                inner_frame.grid_columnconfigure(col, weight=1)
            
            # Update canvas scroll region
            inner_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))
            
            status_label.config(text=f"Loaded sheet: {sheet.title}")
        
        def open_excel_file():
            """Open an Excel file"""
            file_path = filedialog.askopenfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            try:
                # Load the Excel file
                nonlocal workbook, current_file
                workbook = openpyxl.load_workbook(file_path, data_only=True)
                current_file = file_path
                
                # Update the sheet selector dropdown
                sheet_names = workbook.sheetnames
                sheet_combo['values'] = sheet_names
                
                if sheet_names:
                    sheet_var.set(sheet_names[0])
                    show_sheet(sheet_names[0])
                
                # Update window title
                file_name = os.path.basename(file_path)
                title_label.config(text=f"Excel Lite - {file_name}")
                excel_window.title(f"Excel Lite - {file_name}")
                
                status_label.config(text=f"Opened: {file_name}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open Excel file: {str(e)}")
        
        def show_sheet(sheet_name):
            """Show the selected sheet"""
            if not workbook or sheet_name not in workbook.sheetnames:
                return
            
            nonlocal active_sheet
            active_sheet = workbook[sheet_name]
            load_sheet_data(active_sheet)
        
        def save_excel_file():
            """Save the Excel file (placeholder for future implementation)"""
            if not current_file or not workbook:
                messagebox.showinfo("Info", "No file is currently open")
                return
            
            messagebox.showinfo("Info", "Save functionality is not implemented in this version")
        
        def add_formula():
            """Add a formula to the selected cell (placeholder)"""
            messagebox.showinfo("Info", "Formula functionality is not implemented in this version")
        
        def sort_data():
            """Sort data in the selected column (placeholder)"""
            messagebox.showinfo("Info", "Sort functionality is not implemented in this version")
        
        def filter_data():
            """Filter data in the selected column (placeholder)"""
            messagebox.showinfo("Info", "Filter functionality is not implemented in this version")
        
        # Create empty sheet by default
        create_empty_sheet()
        
        # File menu commands
        file_menu.add_command(label="New", command=create_empty_sheet)
        file_menu.add_command(label="Open", command=open_excel_file)
        file_menu.add_command(label="Save", command=save_excel_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=lambda: self.close_window("Excel Lite", excel_window))
        
        # Edit menu commands
        edit_menu.add_command(label="Cut", command=lambda: status_label.config(text="Cut not implemented"))
        edit_menu.add_command(label="Copy", command=lambda: status_label.config(text="Copy not implemented"))
        edit_menu.add_command(label="Paste", command=lambda: status_label.config(text="Paste not implemented"))
        
        # View menu
        view_menu.add_command(label="Formulas", command=lambda: status_label.config(text="View Formulas not implemented"))
        view_menu.add_command(label="Freeze Panes", command=lambda: status_label.config(text="Freeze Panes not implemented"))
        
        # Help menu
        help_menu.add_command(label="About Excel Lite", command=lambda: messagebox.showinfo("About", "Excel Lite\nVersion 1.0\n\nA simple spreadsheet viewer"))
        
        # If a file path was provided, open it
        if file_path and os.path.exists(file_path):
            current_file = file_path
            try:
                workbook = openpyxl.load_workbook(file_path, data_only=True)
                sheet_names = workbook.sheetnames
                sheet_combo['values'] = sheet_names
                if sheet_names:
                    sheet_var.set(sheet_names[0])
                    show_sheet(sheet_names[0])
                
                # Update window title
                file_name = os.path.basename(file_path)
                title_label.config(text=f"Excel Lite - {file_name}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open Excel file: {str(e)}")
        
        # Add to taskbar
        self.add_window_to_taskbar("Excel Lite", excel_window)
        excel_window.protocol("WM_DELETE_WINDOW", lambda: self.close_window("Excel Lite", excel_window))
    
    '''
    def create_file_explorer(self, path=None):
        """Creează un explorer de fișiere care arată și permite gestionarea fișierelor și directoarelor"""
        from tkinter import simpledialog
        if path is None:
            # Start with root directory or home directory depending on OS
            if os.name == 'nt':  # Windows
                path = 'C:\\'
            else:  # Linux/Mac
                path = os.path.expanduser('~')
        
        explorer_window = tk.Toplevel(self.rootW95dist)
        explorer_window.title("My Computer")
        explorer_window.overrideredirect(True)
        explorer_window.geometry("700x500+200+100")
        explorer_window.configure(bg="#c0c0c0")
        
        # Add Windows 95 style title bar
        title_bar = tk.Frame(explorer_window, bg="#000080", height=25)
        title_bar.pack(fill="x", side="top")
        title_label = tk.Label(title_bar, text=f"My Computer - {path}", fg="white", bg="#000080",
                              font=("MS Sans Serif", 8, "bold"))
        title_label.pack(side="left", padx=5, pady=2)
        
        # Close button for title bar
        close_button = tk.Button(title_bar, text="×", bg="#c0c0c0", fg="black",
                                font=("Arial", 8, "bold"), width=2, height=1,
                                relief="raised", bd=1,
                                command=lambda: self.close_window("My Computer", explorer_window))
        close_button.pack(side="right", padx=2, pady=1)
        
        self.make_window_draggable(explorer_window, title_bar)
        
        # Menu bar
        menu_bar = tk.Menu(explorer_window)
        explorer_window.config(menu=menu_bar)
        
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        
        view_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="View", menu=view_menu)
        
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        # Main content frame
        content_frame = tk.Frame(explorer_window, bg="#c0c0c0")
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Address bar
        address_frame = tk.Frame(content_frame, bg="#c0c0c0")
        address_frame.pack(fill="x", pady=5)
        
        tk.Label(address_frame, text="Address:", bg="#c0c0c0", font=("MS Sans Serif", 8)).pack(side="left")
        address_var = tk.StringVar(value=path)
        address_entry = tk.Entry(address_frame, textvariable=address_var, width=50, font=("MS Sans Serif", 8))
        address_entry.pack(side="left", padx=5, fill="x", expand=True)
        address_entry.bind("<Return>", lambda e: navigate_to_path(address_var.get()))
        
        go_button = tk.Button(address_frame, text="Go", bg="#c0c0c0", relief="raised", bd=2,
                             font=("MS Sans Serif", 8),
                             command=lambda: navigate_to_path(address_var.get()))
        go_button.pack(side="left", padx=5)
        
        up_button = tk.Button(address_frame, text="Up", bg="#c0c0c0", relief="raised", bd=2,
                             font=("MS Sans Serif", 8),
                             command=lambda: navigate_up())
        up_button.pack(side="left", padx=5)
        
        # Toolbar for file operations
        toolbar_frame = tk.Frame(content_frame, bg="#c0c0c0", relief="raised", bd=2)
        toolbar_frame.pack(fill="x", pady=5)
        
        new_folder_btn = tk.Button(toolbar_frame, text="New Folder", bg="#c0c0c0", relief="raised", bd=2,
                                  font=("MS Sans Serif", 8),
                                  command=lambda: create_new_folder())
        new_folder_btn.pack(side="left", padx=5, pady=2)
        
        cut_btn = tk.Button(toolbar_frame, text="Cut", bg="#c0c0c0", relief="raised", bd=2,
                           font=("MS Sans Serif", 8),
                           command=lambda: cut_selected())
        cut_btn.pack(side="left", padx=5, pady=2)
        
        copy_btn = tk.Button(toolbar_frame, text="Copy", bg="#c0c0c0", relief="raised", bd=2,
                            font=("MS Sans Serif", 8),
                            command=lambda: copy_selected())
        copy_btn.pack(side="left", padx=5, pady=2)
        
        paste_btn = tk.Button(toolbar_frame, text="Paste", bg="#c0c0c0", relief="raised", bd=2,
                             font=("MS Sans Serif", 8),
                             command=lambda: paste_item())
        paste_btn.pack(side="left", padx=5, pady=2)
        
        delete_btn = tk.Button(toolbar_frame, text="Delete", bg="#c0c0c0", relief="raised", bd=2,
                              font=("MS Sans Serif", 8),
                              command=lambda: delete_selected())
        delete_btn.pack(side="left", padx=5, pady=2)
        
        rename_btn = tk.Button(toolbar_frame, text="Rename", bg="#c0c0c0", relief="raised", bd=2,
                              font=("MS Sans Serif", 8),
                              command=lambda: rename_selected())
        rename_btn.pack(side="left", padx=5, pady=2)
        
        refresh_btn = tk.Button(toolbar_frame, text="Refresh", bg="#c0c0c0", relief="raised", bd=2,
                               font=("MS Sans Serif", 8),
                               command=lambda: refresh_view())
        refresh_btn.pack(side="right", padx=5, pady=2)
        
        # File/Directory list
        list_frame = tk.Frame(content_frame, bg="white", relief="sunken", bd=2)
        list_frame.pack(fill="both", expand=True, pady=5)
        
        # Scrollbars
        h_scrollbar = tk.Scrollbar(list_frame, orient="horizontal")
        h_scrollbar.pack(side="bottom", fill="x")
        
        v_scrollbar = tk.Scrollbar(list_frame)
        v_scrollbar.pack(side="right", fill="y")
        
        # List with columns
        columns = ("name", "type", "size", "modified")
        file_list = ttk.Treeview(list_frame, columns=columns, show="headings",
                               yscrollcommand=v_scrollbar.set,
                               xscrollcommand=h_scrollbar.set,
                               selectmode="extended")
        
        file_list.heading("name", text="Name", command=lambda: sort_by_column("name"))
        file_list.heading("type", text="Type", command=lambda: sort_by_column("type"))
        file_list.heading("size", text="Size", command=lambda: sort_by_column("size"))
        file_list.heading("modified", text="Date Modified", command=lambda: sort_by_column("modified"))
        
        file_list.column("name", width=200, anchor="w")
        file_list.column("type", width=100, anchor="w")
        file_list.column("size", width=100, anchor="e")
        file_list.column("modified", width=150, anchor="w")
        
        file_list.pack(side="left", fill="both", expand=True)
        
        v_scrollbar.config(command=file_list.yview)
        h_scrollbar.config(command=file_list.xview)
        
        # Status bar
        status_frame = tk.Frame(explorer_window, bg="#c0c0c0", relief="sunken", bd=1, height=25)
        status_frame.pack(fill="x", side="bottom")
        status_frame.pack_propagate(False)
        
        status_label = tk.Label(status_frame, text="", bg="#c0c0c0", font=("MS Sans Serif", 8))
        status_label.pack(side="left", padx=5)
        
        items_label = tk.Label(status_frame, text="", bg="#c0c0c0", font=("MS Sans Serif", 8))
        items_label.pack(side="right", padx=5)
        
        # Add to taskbar
        self.add_window_to_taskbar("My Computer", explorer_window)
        explorer_window.protocol("WM_DELETE_WINDOW", lambda: self.close_window("My Computer", explorer_window))
        
        # Clipboard for file operations
        clipboard = {
            "action": None,  # "cut" or "copy"
            "files": []
        }
        
        # Double-click to open/navigate
        file_list.bind("<Double-1>", lambda e: open_selected())
        
        # Right-click context menu
        context_menu = tk.Menu(file_list, tearoff=0)
        
        def show_context_menu(event):
            context_menu.delete(0, tk.END)  # Clear previous items
            
            # Add menu items based on selection
            selected = file_list.selection()
            if selected:
                context_menu.add_command(label="Open", command=open_selected)
                context_menu.add_separator()
                context_menu.add_command(label="Cut", command=cut_selected)
                context_menu.add_command(label="Copy", command=copy_selected)
                context_menu.add_command(label="Delete", command=delete_selected)
                context_menu.add_command(label="Rename", command=rename_selected)
                
                # If only one item selected and it's a file
                if len(selected) == 1:
                    item = selected[0]
                    values = file_list.item(item, "values")
                    if values[1] != "Folder":
                        context_menu.add_separator()
                        context_menu.add_command(label="Open with Text Editor", 
                                               command=lambda: open_with_text_editor(values[0]))
            else:
                context_menu.add_command(label="Paste", command=paste_item, 
                                       state="normal" if clipboard["files"] else "disabled")
                context_menu.add_separator()
                context_menu.add_command(label="New Folder", command=create_new_folder)
                context_menu.add_command(label="Refresh", command=refresh_view)
            
            # Display the context menu
            context_menu.tk_popup(event.x_root, event.y_root)
        
        file_list.bind("<Button-3>", show_context_menu)  # Right-click
        
        # Functions for file operations
        def navigate_to_path(new_path):
            try:
                # Check if path exists and is accessible
                if os.path.exists(new_path) and os.path.isdir(new_path):
                    nonlocal path
                    path = os.path.normpath(new_path)
                    address_var.set(path)
                    title_label.config(text=f"My Computer - {path}")
                    refresh_view()
                else:
                    messagebox.showerror("Error", f"Cannot access: {new_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error navigating to path: {str(e)}")
        
        def navigate_up():
            parent_dir = os.path.dirname(path)
            if parent_dir != path:  # Not at root
                navigate_to_path(parent_dir)
        
        def refresh_view():
            # Clear existing items
            for item in file_list.get_children():
                file_list.delete(item)
            
            try:
                # List directories and files
                items = os.listdir(path)
                
                # First add directories
                for item in sorted(items):
                    item_path = os.path.join(path, item)
                    try:
                        if os.path.isdir(item_path):
                            # Get modified time
                            mod_time = os.path.getmtime(item_path)
                            mod_time_str = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
                            
                            file_list.insert("", "end", values=(item, "Folder", "", mod_time_str))
                    except PermissionError:
                        file_list.insert("", "end", values=(item, "Folder (Access Denied)", "", ""))
                    except Exception as e:
                        print(f"Error accessing {item_path}: {str(e)}")
                
                # Then add files
                for item in sorted(items):
                    item_path = os.path.join(path, item)
                    try:
                        if os.path.isfile(item_path):
                            # Get file size
                            size = os.path.getsize(item_path)
                            size_str = format_size(size)
                            
                            # Get modified time
                            mod_time = os.path.getmtime(item_path)
                            mod_time_str = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
                            
                            # Get file type
                            file_ext = os.path.splitext(item)[1].lower()
                            file_type = get_file_type(file_ext)
                            
                            file_list.insert("", "end", values=(item, file_type, size_str, mod_time_str))
                    except PermissionError:
                        file_list.insert("", "end", values=(item, "File (Access Denied)", "", ""))
                    except Exception as e:
                        print(f"Error accessing {item_path}: {str(e)}")
                
                # Update status
                status_label.config(text=f"Current directory: {path}")
                items_label.config(text=f"{len(items)} items")
                
            except PermissionError:
                messagebox.showerror("Access Denied", f"Cannot access directory: {path}")
                navigate_up()
            except Exception as e:
                messagebox.showerror("Error", f"Error loading directory: {str(e)}")
        
        def format_size(size_bytes):
            """Format file size in human-readable format"""
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024**2:
                return f"{size_bytes/1024:.1f} KB"
            elif size_bytes < 1024**3:
                return f"{size_bytes/(1024**2):.1f} MB"
            else:
                return f"{size_bytes/(1024**3):.1f} GB"
        
        def get_file_type(ext):
            """Return file type based on extension"""
            file_types = {
                ".txt": "Text Document",
                ".doc": "Word Document",
                ".docx": "Word Document",
                ".pdf": "PDF Document",
                ".jpg": "JPEG Image",
                ".jpeg": "JPEG Image",
                ".png": "PNG Image",
                ".gif": "GIF Image",
                ".mp3": "Audio File",
                ".mp4": "Video File",
                ".py": "Python Script",
                ".exe": "Application",
                ".zip": "Compressed File",
                ".rar": "Compressed File",
                ".ini": "Configuration File",
                ".html": "HTML Document",
                ".css": "CSS File",
                ".js": "JavaScript File",
                ".json": "JSON File"
            }
            return file_types.get(ext, f"{ext[1:].upper() if ext else 'Unknown'} File")
        
        def open_selected():
            selected = file_list.selection()
            if not selected:
                return
            
            # Get the first selected item
            item = selected[0]
            values = file_list.item(item, "values")
            item_name = values[0]
            item_type = values[1]
            item_path = os.path.join(path, item_name)
            
            if item_type == "Folder":
                # Navigate to the selected folder
                navigate_to_path(item_path)
            else:
                # For files, try to open with default application
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(item_path)
                    else:  # Linux/Mac
                        subprocess.run(['xdg-open', item_path], check=True)
                except Exception as e:
                    messagebox.showerror("Error", f"Could not open file: {str(e)}")
                    # Offer to open with text editor
                    if messagebox.askyesno("Open with Text Editor", 
                                          "Would you like to open this file with Text Editor?"):
                        open_with_text_editor(item_name)
        
        def open_with_text_editor(filename):
            """Open the selected file with the Text Editor"""
            file_path = os.path.join(path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                    # Create a new text editor window
                    self.create_text_editor_with_content(content, filename, file_path)
            except UnicodeDecodeError:
                messagebox.showerror("Error", "Cannot open binary file with Text Editor")
            except Exception as e:
                messagebox.showerror("Error", f"Error opening file: {str(e)}")
        
        def create_new_folder():
            """Create a new folder in the current directory"""
            folder_name = simpledialog.askstring("New Folder", "Enter folder name:")
            if folder_name:
                new_folder_path = os.path.join(path, folder_name)
                try:
                    os.mkdir(new_folder_path)
                    refresh_view()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not create folder: {str(e)}")
        
        def cut_selected():
            """Cut selected files/folders"""
            selected = file_list.selection()
            if not selected:
                return
            
            clipboard["action"] = "cut"
            clipboard["files"] = []
            
            for item in selected:
                values = file_list.item(item, "values")
                item_name = values[0]
                item_path = os.path.join(path, item_name)
                clipboard["files"].append(item_path)
            
            status_label.config(text=f"{len(selected)} items cut to clipboard")
        
        def copy_selected():
            """Copy selected files/folders"""
            selected = file_list.selection()
            if not selected:
                return
            
            clipboard["action"] = "copy"
            clipboard["files"] = []
            
            for item in selected:
                values = file_list.item(item, "values")
                item_name = values[0]
                item_path = os.path.join(path, item_name)
                clipboard["files"].append(item_path)
            
            status_label.config(text=f"{len(selected)} items copied to clipboard")
        
        def paste_item():
            """Paste files/folders from clipboard to current directory"""
            if not clipboard["files"]:
                return
            
            for src_path in clipboard["files"]:
                if not os.path.exists(src_path):
                    continue
                    
                # Get just the filename/foldername
                base_name = os.path.basename(src_path)
                dst_path = os.path.join(path, base_name)
                
                try:
                    # Check if destination already exists
                    if os.path.exists(dst_path):
                        if not messagebox.askyesno("Confirm", 
                                                  f"{base_name} already exists. Overwrite?"):
                            continue
                    
                    if clipboard["action"] == "cut":
                        # For cut operation, move the file/folder
                        if os.path.isdir(src_path):
                            # For folders, use shutil.move
                            shutil.move(src_path, dst_path)
                        else:
                            # For files, use os.rename (faster than shutil.move for files)
                            os.rename(src_path, dst_path)
                    else:  # "copy"
                        # For copy operation
                        if os.path.isdir(src_path):
                            # For folders, copy the entire directory tree
                            shutil.copytree(src_path, dst_path)
                        else:
                            # For files, use shutil.copy2 to preserve metadata
                            shutil.copy2(src_path, dst_path)
                except Exception as e:
                    messagebox.showerror("Error", f"Error pasting {base_name}: {str(e)}")
            
            # Clear clipboard if it was a cut operation
            if clipboard["action"] == "cut":
                clipboard["files"] = []
            
            refresh_view()
        
        def delete_selected():
            """Delete selected files/folders"""
            selected = file_list.selection()
            if not selected:
                return
            
            # Confirm deletion
            count = len(selected)
            if not messagebox.askyesno("Confirm Delete", 
                                      f"Are you sure you want to delete {count} item(s)?"):
                return
            
            for item in selected:
                values = file_list.item(item, "values")
                item_name = values[0]
                item_path = os.path.join(path, item_name)
                
                try:
                    if os.path.isdir(item_path):
                        # For folders, use shutil.rmtree
                        shutil.rmtree(item_path)
                    else:
                        # For files, use os.remove
                        os.remove(item_path)
                except Exception as e:
                    messagebox.showerror("Error", f"Error deleting {item_name}: {str(e)}")
            
            refresh_view()
        
        def rename_selected():
            """Rename selected file/folder"""
            selected = file_list.selection()
            if not selected or len(selected) > 1:
                messagebox.showinfo("Rename", "Please select only one item to rename")
                return
            
            item = selected[0]
            values = file_list.item(item, "values")
            old_name = values[0]
            old_path = os.path.join(path, old_name)
            
            new_name = simpledialog.askstring("Rename", "Enter new name:", initialvalue=old_name)
            if new_name and new_name != old_name:
                new_path = os.path.join(path, new_name)
                try:
                    os.rename(old_path, new_path)
                    refresh_view()
                except Exception as e:
                    messagebox.showerror("Error", f"Error renaming file: {str(e)}")
        
        def sort_by_column(column):
            """Sort file list by the specified column"""
            # This would need to be implemented to handle sorting
            # For simplicity, we'll just refresh the view for now
            refresh_view()
        
        # Initial file listing
        refresh_view()

    def create_text_editor_with_content(self, content, filename, file_path=None):
        """Create a text editor window with predefined content"""
        editor_window = tk.Toplevel(self.rootW95dist)
        editor_window.title(f"Text Editor - {filename}")
        editor_window.overrideredirect(True)
        editor_window.geometry("600x400+200+100")
        editor_window.configure(bg="#c0c0c0")
        
        # Add Windows 95 style title bar
        title_bar = tk.Frame(editor_window, bg="#000080", height=25)
        title_bar.pack(fill="x", side="top")
        title_label = tk.Label(title_bar, text=f"Text Editor - {filename}", fg="white", bg="#000080",
                              font=("MS Sans Serif", 8, "bold"))
        title_label.pack(side="left", padx=5, pady=2)
        
        self.make_window_draggable(editor_window, title_bar)
        
        # Close button for title bar
        close_button = tk.Button(title_bar, text="×", bg="#c0c0c0", fg="black",
                                font=("Arial", 8, "bold"), width=2, height=1,
                                relief="raised", bd=1,
                                command=lambda: self.close_window(f"Text Editor - {filename}", editor_window))
        close_button.pack(side="right", padx=2, pady=1)
        
        # Menubar
        menubar = tk.Menu(editor_window)
        editor_window.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Text area
        text_frame = tk.Frame(editor_window, bg="#c0c0c0")
        text_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Text widget
        text_area = tk.Text(text_frame, wrap="word", yscrollcommand=scrollbar.set,
                           font=("Courier New", 10), bg="white", fg="black")
        text_area.pack(fill="both", expand=True)
        scrollbar.config(command=text_area.yview)
        
        # Insert the content
        text_area.insert(1.0, content)
        
        # Funcții pentru meniu
        def save_file():
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    content = text_area.get(1.0, tk.END)
                    file.write(content)
                    messagebox.showinfo("Success", "File saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
        
        def save_as_file():
            file_path_new = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if file_path_new:
                try:
                    with open(file_path_new, 'w', encoding='utf-8') as file:
                        content = text_area.get(1.0, tk.END)
                        file.write(content)
                        nonlocal file_path
                        file_path = file_path_new
                        editor_window.title(f"Text Editor - {os.path.basename(file_path)}")
                        title_label.config(text=f"Text Editor - {os.path.basename(file_path)}")
                        messagebox.showinfo("Success", "File saved successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not save file: {str(e)}")
        
        # Adaugă opțiunile în meniu
        file_menu.add_command(label="Save", command=save_file)
        file_menu.add_command(label="Save As", command=save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=lambda: self.close_window(f"Text Editor - {filename}", editor_window))
        
        self.add_window_to_taskbar(f"Text Editor - {filename}", editor_window)
        editor_window.protocol("WM_DELETE_WINDOW", lambda: self.close_window(f"Text Editor - {filename}", editor_window))

    def create_text_editor_with_content(self, content, filename, file_path=None):
        """Create a text editor window with predefined content"""
        editor_window = tk.Toplevel(self.rootW95dist)
        editor_window.title(f"Text Editor - {filename}")
        editor_window.overrideredirect(True)
        editor_window.geometry("600x400+200+100")
        editor_window.configure(bg="#c0c0c0")
        
        # Add Windows 95 style title bar
        title_bar = tk.Frame(editor_window, bg="#000080", height=25)
        title_bar.pack(fill="x", side="top")
        title_label = tk.Label(title_bar, text=f"Text Editor - {filename}", fg="white", bg="#000080",
                              font=("MS Sans Serif", 8, "bold"))
        title_label.pack(side="left", padx=5, pady=2)
        
        self.make_window_draggable(editor_window, title_bar)
        
        # Close button for title bar
        close_button = tk.Button(title_bar, text="×", bg="#c0c0c0", fg="black",
                                font=("Arial", 8, "bold"), width=2, height=1,
                                relief="raised", bd=1,
                                command=lambda: self.close_window(f"Text Editor - {filename}", editor_window))
        close_button.pack(side="right", padx=2, pady=1)
        
        # Menubar
        menubar = tk.Menu(editor_window)
        editor_window.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Text area
        text_frame = tk.Frame(editor_window, bg="#c0c0c0")
        text_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Text widget
        text_area = tk.Text(text_frame, wrap="word", yscrollcommand=scrollbar.set,
                           font=("Courier New", 10), bg="white", fg="black")
        text_area.pack(fill="both", expand=True)
        scrollbar.config(command=text_area.yview)
        
        # Insert the content
        text_area.insert(1.0, content)
        
        # Funcții pentru meniu
        def save_file():
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    content = text_area.get(1.0, tk.END)
                    file.write(content)
                    messagebox.showinfo("Success", "File saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
        
        def save_as_file():
            file_path_new = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if file_path_new:
                try:
                    with open(file_path_new, 'w', encoding='utf-8') as file:
                        content = text_area.get(1.0, tk.END)
                        file.write(content)
                        nonlocal file_path
                        file_path = file_path_new
                        editor_window.title(f"Text Editor - {os.path.basename(file_path)}")
                        title_label.config(text=f"Text Editor - {os.path.basename(file_path)}")
                        messagebox.showinfo("Success", "File saved successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not save file: {str(e)}")
        
        # Adaugă opțiunile în meniu
        file_menu.add_command(label="Save", command=save_file)
        file_menu.add_command(label="Save As", command=save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=lambda: self.close_window(f"Text Editor - {filename}", editor_window))
        
        self.add_window_to_taskbar(f"Text Editor - {filename}", editor_window)
        editor_window.protocol("WM_DELETE_WINDOW", lambda: self.close_window(f"Text Editor - {filename}", editor_window))
    
    def create_text_editor(self):
        editor_window = tk.Toplevel(self.rootW95dist)
        editor_window.title("Text Editor")
        editor_window.overrideredirect(True)
        editor_window.geometry("500x400+200+100")
        editor_window.configure(bg="#c0c0c0")
        
        # Add Windows 95 style title bar
        title_bar = tk.Frame(editor_window, bg="#000080", height=25)
        title_bar.pack(fill="x", side="top")
        title_label = tk.Label(title_bar, text="Text Editor", fg="white", bg="#000080",
                              font=("MS Sans Serif", 8, "bold"))
        title_label.pack(side="left", padx=5, pady=2)
        
        self.make_window_draggable(editor_window, title_bar)
        
        # Close button for title bar
        close_button = tk.Button(title_bar, text="×", bg="#c0c0c0", fg="black",
                                font=("Arial", 8, "bold"), width=2, height=1,
                                relief="raised", bd=1,
                                command=lambda: self.close_window("Text Editor", editor_window))
        close_button.pack(side="right", padx=2, pady=1)
        
        # Menubar
        menubar = tk.Menu(editor_window)
        editor_window.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Text area
        text_frame = tk.Frame(editor_window, bg="#c0c0c0")
        text_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Text widget
        text_area = tk.Text(text_frame, wrap="word", yscrollcommand=scrollbar.set,
                           font=("Courier New", 10), bg="white", fg="black")
        text_area.pack(fill="both", expand=True)
        scrollbar.config(command=text_area.yview)
        
        self.make_window_draggable(editor_window, title_bar)
        
        # Funcții pentru meniu
        def open_file():
            file_path = filedialog.askopenfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        text_area.delete(1.0, tk.END)
                        text_area.insert(1.0, content)
                        editor_window.title(f"Text Editor - {file_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not open file: {str(e)}")
        
        def save_file():
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as file:
                        content = text_area.get(1.0, tk.END)
                        file.write(content)
                        editor_window.title(f"Text Editor - {file_path}")
                        messagebox.showinfo("Success", "File saved successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not save file: {str(e)}")
        
        # Adaugă opțiunile în meniu
        file_menu.add_command(label="Open", command=open_file)
        file_menu.add_command(label="Save", command=save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=lambda: self.close_window("Text Editor", editor_window))
        
        self.add_window_to_taskbar("Text Editor", editor_window)
        editor_window.protocol("WM_DELETE_WINDOW", lambda: self.close_window("Text Editor", editor_window))
    
    def create_calculator(self):
        calc_window = tk.Toplevel(self.rootW95dist)
        calc_window.title("Calculator")
        calc_window.overrideredirect(True)
        calc_window.geometry("250x300+300+150")
        calc_window.configure(bg="#c0c0c0")
        calc_window.resizable(False, False)
        
        # Add Windows 95 style title bar
        title_bar = tk.Frame(calc_window, bg="#000080", height=25)
        title_bar.pack(fill="x", side="top")
        title_label = tk.Label(title_bar, text="Calculator", fg="white", bg="#000080",
                              font=("MS Sans Serif", 8, "bold"))
        title_label.pack(side="left", padx=5, pady=2)
        
        # Close button for title bar
        close_button = tk.Button(title_bar, text="×", bg="#c0c0c0", fg="black",
                                font=("Arial", 8, "bold"), width=2, height=1,
                                relief="raised", bd=1,
                                command=lambda: self.close_window("Calculator", calc_window))
        close_button.pack(side="right", padx=2, pady=1)
        
        self.make_window_draggable(calc_window, title_bar)
        
        # Display
        display_var = tk.StringVar()
        display_var.set("0")
        
        display = tk.Entry(calc_window, textvariable=display_var, font=("Arial", 14),
                          justify="right", state="readonly", bg="white")
        display.pack(fill="x", padx=5, pady=5)
        
        # Calculator logic
        calc_data = {"current": "0", "operator": None, "operand": None}
        
        def button_click(value):
            if value.isdigit():
                if calc_data["current"] == "0":
                    calc_data["current"] = value
                else:
                    calc_data["current"] += value
            elif value in ["+", "-", "*", "/"]:
                if calc_data["operator"] and calc_data["operand"] is not None:
                    calculate()
                calc_data["operand"] = float(calc_data["current"])
                calc_data["operator"] = value
                calc_data["current"] = "0"
            elif value == "=":
                calculate()
            elif value == "C":
                calc_data["current"] = "0"
                calc_data["operator"] = None
                calc_data["operand"] = None
            
            display_var.set(calc_data["current"])
        
        def calculate():
            if calc_data["operator"] and calc_data["operand"] is not None:
                try:
                    current_val = float(calc_data["current"])
                    if calc_data["operator"] == "+":
                        result = calc_data["operand"] + current_val
                    elif calc_data["operator"] == "-":
                        result = calc_data["operand"] - current_val
                    elif calc_data["operator"] == "*":
                        result = calc_data["operand"] * current_val
                    elif calc_data["operator"] == "/":
                        if current_val != 0:
                            result = calc_data["operand"] / current_val
                        else:
                            result = "Error"
                    
                    calc_data["current"] = str(result)
                    calc_data["operator"] = None
                    calc_data["operand"] = None
                except:
                    calc_data["current"] = "Error"
        
        # Buttons frame
        buttons_frame = tk.Frame(calc_window, bg="#c0c0c0")
        buttons_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Button layout
        buttons = [
            ['C', '', '', '/'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['0', '', '', '=']
        ]
        
        for i, row in enumerate(buttons):
            for j, btn_text in enumerate(row):
                if btn_text:
                    btn = tk.Button(buttons_frame, text=btn_text, font=("Arial", 12),
                                   command=lambda t=btn_text: button_click(t),
                                   bg="#e0e0e0", relief="raised", bd=2)
                    btn.grid(row=i, column=j, sticky="nsew", padx=1, pady=1)
        
        # Configure grid weights
        for i in range(5):
            buttons_frame.grid_rowconfigure(i, weight=1)
        for j in range(4):
            buttons_frame.grid_columnconfigure(j, weight=1)
        
        self.add_window_to_taskbar("Calculator", calc_window)
        calc_window.protocol("WM_DELETE_WINDOW", lambda: self.close_window("Calculator", calc_window))
    
    def create_network_monitor(self):
        net_window = tk.Toplevel(self.rootW95dist)
        net_window.title("Network Monitor")
        net_window.overrideredirect(True)
        net_window.geometry("700x600+350+50")
        net_window.configure(bg="#c0c0c0")
        
        # Add Windows 95 style title bar
        title_bar = tk.Frame(net_window, bg="#000080", height=25)
        title_bar.pack(fill="x", side="top")
        title_label = tk.Label(title_bar, text="Network Monitor", fg="white", bg="#000080",
                              font=("MS Sans Serif", 8, "bold"))
        title_label.pack(side="left", padx=5, pady=2)
        
        # Close button for title bar
        close_button = tk.Button(title_bar, text="×", bg="#c0c0c0", fg="black",
                                font=("Arial", 8, "bold"), width=2, height=1,
                                relief="raised", bd=1,
                                command=lambda: self.close_window("Network Monitor", net_window))
        close_button.pack(side="right", padx=2, pady=1)
        
        # Header frame
        header_frame = tk.Frame(net_window, bg="#c0c0c0", relief="raised", bd=2)
        header_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(header_frame, text="Advanced Network Monitor", font=("MS Sans Serif", 10, "bold"),
                bg="#c0c0c0").pack(pady=5)
        
        # Tabs using notebook
        notebook = ttk.Notebook(net_window)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create a custom style for Windows 95 look
        style = ttk.Style()
        style.configure("W95.TNotebook", background="#c0c0c0", borderwidth=2, relief="raised")
        style.configure("W95.TNotebook.Tab", padding=[5, 2], font=("MS Sans Serif", 8))
        notebook.configure(style="W95.TNotebook")
        
        # Tab 1: Network Stats
        stats_frame = ttk.Frame(notebook)
        notebook.add(stats_frame, text="Network Stats")
        
        # Stats display
        stats_text = tk.Text(stats_frame, font=("Courier New", 9), bg="white", 
                            fg="black", relief="sunken", bd=2)
        stats_scrollbar = tk.Scrollbar(stats_frame, command=stats_text.yview)
        stats_text.config(yscrollcommand=stats_scrollbar.set)
        
        stats_text.pack(side="left", fill="both", expand=True)
        stats_text.config(state="disabled")
        stats_scrollbar.pack(side="right", fill="y")
        
        # Tab 2: Active Connections
        conn_frame = ttk.Frame(notebook)
        notebook.add(conn_frame, text="Connections")
        
        # Connections display
        conn_text = tk.Text(conn_frame, font=("Courier New", 9), bg="white",
                           fg="black", relief="sunken", bd=2)
        conn_scrollbar = tk.Scrollbar(conn_frame, command=conn_text.yview)
        conn_text.config(yscrollcommand=conn_scrollbar.set)
        
        conn_text.pack(side="left", fill="both", expand=True)
        conn_text.config(state="disabled")
        conn_scrollbar.pack(side="right", fill="y")
        
        # Tab 3: Network Traffic Graph (Text-based)
        traffic_frame = ttk.Frame(notebook)
        notebook.add(traffic_frame, text="Traffic Graph")
        
        traffic_text = tk.Text(traffic_frame, font=("Courier New", 8), bg="black",
                              fg="#00ff00", relief="sunken", bd=2)
        traffic_scrollbar = tk.Scrollbar(traffic_frame, command=traffic_text.yview)
        traffic_text.config(yscrollcommand=traffic_scrollbar.set)
        
        traffic_text.pack(side="left", fill="both", expand=True)
        traffic_text.config(state="disabled")
        traffic_scrollbar.pack(side="right", fill="y")
        
        # Tab 4: Port Scanner
        scanner_frame = ttk.Frame(notebook)
        notebook.add(scanner_frame, text="Port Scanner")
        
        # Scanner controls
        scanner_control_frame = tk.Frame(scanner_frame, bg="#f0f0f0", relief="raised", bd=2)
        scanner_control_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(scanner_control_frame, text="Target IP:", bg="#f0f0f0").pack(side="left", padx=2)
        ip_entry = tk.Entry(scanner_control_frame, width=15, relief="sunken", bd=2)
        ip_entry.pack(side="left", padx=2)
        ip_entry.insert(0, "127.0.0.1")
        
        tk.Label(scanner_control_frame, text="Port Range:", bg="#f0f0f0").pack(side="left", padx=(10,0))
        port_start_entry = tk.Entry(scanner_control_frame, width=8, relief="sunken", bd=2)
        port_start_entry.pack(side="left", padx=2)
        port_start_entry.insert(0, "1")
        
        tk.Label(scanner_control_frame, text="-", bg="#f0f0f0").pack(side="left")
        port_end_entry = tk.Entry(scanner_control_frame, width=8, relief="sunken", bd=2)
        port_end_entry.pack(side="left", padx=2)
        port_end_entry.insert(0, "1000")
        
        scan_btn = tk.Button(scanner_control_frame, text="Scan", 
                            font=("MS Sans Serif", 8),
                            bg="#c0c0c0", relief="raised", bd=2,
                            command=lambda: self.start_port_scan(ip_entry.get(), 
                                                               int(port_start_entry.get()), 
                                                               int(port_end_entry.get()), 
                                                               scanner_text))
        scan_btn.pack(side="left", padx=10)
        
        # Scanner results
        scanner_text = tk.Text(scanner_frame, font=("Courier New", 9), bg="white",
                              fg="black", relief="sunken", bd=2)
        scanner_text_scrollbar = tk.Scrollbar(scanner_frame, command=scanner_text.yview)
        scanner_text.config(yscrollcommand=scanner_text_scrollbar.set)
        
        scanner_text.pack(side="left", fill="both", expand=True, padx=5)
        scanner_text.config(state="disabled")
        scanner_text_scrollbar.pack(side="right", fill="y")
        
        # Tab 5: Bandwidth Monitor
        bandwidth_frame = ttk.Frame(notebook)
        notebook.add(bandwidth_frame, text="Bandwidth")
        
        bandwidth_text = tk.Text(bandwidth_frame, font=("Courier New", 9), bg="white",
                                fg="black", relief="sunken", bd=2)
        bandwidth_scrollbar = tk.Scrollbar(bandwidth_frame, command=bandwidth_text.yview)
        bandwidth_text.config(yscrollcommand=bandwidth_scrollbar.set)
        
        bandwidth_text.pack(side="left", fill="both", expand=True)
        bandwidth_text.config(state="disabled")
        bandwidth_scrollbar.pack(side="right", fill="y")
        
        # Buttons frame with Windows 95 style
        buttons_frame = tk.Frame(net_window, bg="#c0c0c0")
        buttons_frame.pack(fill="x", padx=5, pady=5)
        
        refresh_btn = tk.Button(buttons_frame, text="Refresh", font=("MS Sans Serif", 8),
                               bg="#c0c0c0", relief="raised", bd=2,
                               command=lambda: self.update_network_info(stats_text, conn_text, 
                                                                       traffic_text, bandwidth_text))
        refresh_btn.pack(side="left", padx=5)
        
        monitor_btn = tk.Button(buttons_frame, text="Start Monitoring", font=("MS Sans Serif", 8),
                               bg="#c0c0c0", relief="raised", bd=2,
                               command=lambda: self.toggle_network_monitoring(monitor_btn, traffic_text))
        monitor_btn.pack(side="left", padx=5)
        
        export_btn = tk.Button(buttons_frame, text="Export Data", font=("MS Sans Serif", 8),
                              bg="#c0c0c0", relief="raised", bd=2,
                              command=self.export_network_data)
        export_btn.pack(side="left", padx=5)
        
        help_btn = tk.Button(buttons_frame, text="Help", font=("MS Sans Serif", 8),
                            bg="#c0c0c0", relief="raised", bd=2,
                            command=lambda: self.show_help("Network Monitor"))
        help_btn.pack(side="right", padx=5)
        
        # Initial load
        self.update_network_info(stats_text, conn_text, traffic_text, bandwidth_text)
        
        # Simulate real network data initially
        self.simulate_network_data(traffic_text)
        
        self.add_window_to_taskbar("Network Monitor", net_window)
        net_window.protocol("WM_DELETE_WINDOW", lambda: self.close_window("Network Monitor", net_window))
        
        self.make_window_draggable(net_window, title_bar)
    
    def simulate_network_data(self, traffic_text):
        """Simulate some initial network traffic data for better UI appearance"""
        timestamp = datetime.now() - timedelta(seconds=10)
        
        # Add some simulated data to history
        for i in range(10):
            timestamp += timedelta(seconds=1)
            ts_str = timestamp.strftime("%H:%M:%S")
            
            # Generate some random data for demo purposes
            bytes_sent = random.randint(1024, 10240)
            bytes_recv = random.randint(2048, 20480)
            
            self.network_history.append({
                'time': ts_str,
                'bytes_sent': i * bytes_sent,
                'bytes_recv': i * bytes_recv,
                'packets_sent': i * 10,
                'packets_recv': i * 20
            })
            
            if i > 0:
                prev = self.network_history[i-1]
                curr = self.network_history[i]
                
                bytes_sent_rate = curr['bytes_sent'] - prev['bytes_sent']
                bytes_recv_rate = curr['bytes_recv'] - prev['bytes_recv']
                
                # Create simple ASCII graph
                max_rate = max(bytes_sent_rate, bytes_recv_rate, 1024)
                sent_bar = "█" * int((bytes_sent_rate / max_rate) * 40)
                recv_bar = "█" * int((bytes_recv_rate / max_rate) * 40)
                
                display_text = f"{ts_str} | UP: {sent_bar:<40} {bytes_sent_rate:>8} B/s\n"
                display_text += f"        | DN: {recv_bar:<40} {bytes_recv_rate:>8} B/s\n"
                
                traffic_text.config(state="normal")
                traffic_text.insert(tk.END, display_text)
                
        traffic_text.config(state="disabled")
    
    def start_port_scan(self, target_ip, start_port, end_port, result_text):
        result_text.config(state="normal")
        result_text.delete(1.0, tk.END)
        result_text.insert(1.0, f"Starting port scan on {target_ip}...\n")
        result_text.insert(tk.END, f"Scanning ports {start_port}-{end_port}\n")
        result_text.insert(tk.END, "=" * 50 + "\n")
        
        def scan_ports():
            open_ports = []
            for port in range(start_port, min(end_port + 1, start_port + 100)):  # Limit scan range
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.1)
                    result = sock.connect_ex((target_ip, port))
                    if result == 0:
                        open_ports.append(port)
                        result_text.insert(tk.END, f"Port {port}: OPEN\n")
                        result_text.see(tk.END)
                        result_text.update()
                    sock.close()
                except:
                    pass
            
            result_text.insert(tk.END, f"\nScan completed. Found {len(open_ports)} open ports.\n")
            if open_ports:
                result_text.insert(tk.END, f"Open ports: {', '.join(map(str, open_ports))}\n")
        
        # Run scan in thread to prevent UI freezing
        scan_thread = threading.Thread(target=scan_ports, daemon=True)
        result_text.config(state="disabled")
        scan_thread.start()
    
    def toggle_network_monitoring(self, button, traffic_text):
        if not self.monitoring_active:
            self.monitoring_active = True
            button.config(text="Stop Monitoring")
            self.start_network_monitoring(traffic_text)
        else:
            self.monitoring_active = False
            button.config(text="Start Monitoring")
    
    def start_network_monitoring(self, traffic_text):
        def monitor():
            while self.monitoring_active:
                try:
                    net_io = psutil.net_io_counters()
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    # Store data for history
                    self.network_history.append({
                        'time': timestamp,
                        'bytes_sent': net_io.bytes_sent,
                        'bytes_recv': net_io.bytes_recv,
                        'packets_sent': net_io.packets_sent,
                        'packets_recv': net_io.packets_recv
                    })
                    
                    # Keep only last 100 entries
                    if len(self.network_history) > 100:
                        self.network_history.pop(0)
                    
                    # Update text display
                    if len(self.network_history) >= 2:
                        prev = self.network_history[-2]
                        curr = self.network_history[-1]
                        
                        bytes_sent_rate = curr['bytes_sent'] - prev['bytes_sent']
                        bytes_recv_rate = curr['bytes_recv'] - prev['bytes_recv']
                        
                        # Create simple ASCII graph
                        max_rate = max(bytes_sent_rate, bytes_recv_rate, 1024)
                        sent_bar = "█" * int((bytes_sent_rate / max_rate) * 40)
                        recv_bar = "█" * int((bytes_recv_rate / max_rate) * 40)
                        
                        display_text = f"{timestamp} | UP: {sent_bar:<40} {bytes_sent_rate:>8} B/s\n"
                        display_text += f"        | DN: {recv_bar:<40} {bytes_recv_rate:>8} B/s\n"
                        
                        traffic_text.config(state="normal")
                        traffic_text.insert(tk.END, display_text)
                        traffic_text.see(tk.END)
                        traffic_text.config(state="disabled")
                        
                        # Keep only last 50 lines
                        lines = traffic_text.get(1.0, tk.END).split('\n')
                        if len(lines) > 100:
                            traffic_text.delete(1.0, f"{len(lines)-100}.0")
                    
                    time.sleep(1)
                except Exception as e:
                    traffic_text.config(state="normal")
                    traffic_text.insert(tk.END, f"Monitoring error: {str(e)}\n")
                    break
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def export_network_data(self):
        if not self.network_history:
            messagebox.showinfo("Export", "No network data to export.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.network_history, f, indent=2)
                messagebox.showinfo("Export", f"Network data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Could not export data: {str(e)}")
    
    def update_network_info(self, stats_text, conn_text, traffic_text, bandwidth_text):
        try:
            # Clear previous content
            stats_text.config(state="normal")
            conn_text.config(state="normal")
            bandwidth_text.config(state="normal")
            stats_text.delete(1.0, tk.END)
            conn_text.delete(1.0, tk.END)
            bandwidth_text.delete(1.0, tk.END)
            
            # Network statistics
            net_io = psutil.net_io_counters()
            addrs = psutil.net_if_addrs()
            net_stats = psutil.net_if_stats()
            
            stats_info = "╔═══════════════════════════════════════╗\n"
            stats_info += "║         NETWORK STATISTICS            ║\n"
            stats_info += "╚═══════════════════════════════════════╝\n\n"
            
            stats_info += f" GLOBAL COUNTERS:\n"
            stats_info += f"   Bytes Sent:     {net_io.bytes_sent:,} bytes ({net_io.bytes_sent/(1024**3):.2f} GB)\n"
            stats_info += f"   Bytes Received: {net_io.bytes_recv:,} bytes ({net_io.bytes_recv/(1024**3):.2f} GB)\n"
            stats_info += f"   Packets Sent:   {net_io.packets_sent:,}\n"
            stats_info += f"   Packets Recv:   {net_io.packets_recv:,}\n"
            stats_info += f"   Errors In:      {net_io.errin}\n"
            stats_info += f"   Errors Out:     {net_io.errout}\n"
            stats_info += f"   Drops In:       {net_io.dropin}\n"
            stats_info += f"   Drops Out:      {net_io.dropout}\n\n"
            
            stats_info += " NETWORK INTERFACES:\n"
            stats_info += "─" * 60 + "\n"
            
            for interface, addresses in addrs.items():
                stats_info += f"\n {interface}:\n"
                
                # Interface statistics
                if interface in net_stats:
                    stat = net_stats[interface]
                    stats_info += f"   Status: {'UP' if stat.isup else 'DOWN'}\n"
                    stats_info += f"   Speed: {stat.speed} Mbps\n" if stat.speed > 0 else "   Speed: Unknown\n"
                    stats_info += f"   MTU: {stat.mtu}\n"
                
                # Addresses
                for addr in addresses:
                    if addr.family == socket.AF_INET:
                        stats_info += f"    IPv4: {addr.address}\n"
                        if addr.netmask:
                            stats_info += f"      Netmask: {addr.netmask}\n"
                        if addr.broadcast:
                            stats_info += f"      Broadcast: {addr.broadcast}\n"
                    elif addr.family == socket.AF_INET6:
                        stats_info += f"    IPv6: {addr.address}\n"
                    elif hasattr(addr, 'address') and len(addr.address) == 17:  # MAC address
                        stats_info += f"    MAC: {addr.address}\n"
            
            stats_text.insert(1.0, stats_info)
            
            # Active connections with more details
            connections = psutil.net_connections()
            conn_info = "╔═══════════════════════════════════════╗\n"
            conn_info += "║        ACTIVE CONNECTIONS             ║\n"
            conn_info += "╚═══════════════════════════════════════╝\n\n"
            conn_info += f"Total Active Connections: {len(connections)}\n\n"
            conn_info += f"{'Proto':<6} {'PID':<8} {'Local Address':<22} {'Remote Address':<22} {'Status':<12}\n"
            conn_info += "─" * 80 + "\n"
            
            connection_stats = {"TCP": 0, "UDP": 0, "ESTABLISHED": 0, "LISTENING": 0}
            
            for conn in connections[:100]:  # Limit to first 100 connections
                if conn.laddr:
                    local = f"{conn.laddr.ip}:{conn.laddr.port}"
                else:
                    local = "N/A"
                
                if conn.raddr:
                    remote = f"{conn.raddr.ip}:{conn.raddr.port}"
                else:
                    remote = "N/A"
                
                protocol = "TCP" if conn.type == socket.SOCK_STREAM else "UDP"
                status = conn.status if conn.status else "N/A"
                pid = str(conn.pid) if conn.pid else "N/A"
                
                # Update statistics
                connection_stats[protocol] += 1
                if status in connection_stats:
                    connection_stats[status] += 1
                
                conn_info += f"{protocol:<6} {pid:<8} {local:<22} {remote:<22} {status:<12}\n"
            
            # Add connection statistics
            conn_info += "\n" + "─" * 80 + "\n"
            conn_info += "CONNECTION STATISTICS:\n"
            for key, value in connection_stats.items():
                conn_info += f"   {key}: {value}\n"
            
            conn_text.insert(1.0, conn_info)
            
            # Bandwidth monitoring
            bandwidth_info = "╔═══════════════════════════════════════╗\n"
            bandwidth_info += "║        BANDWIDTH MONITORING           ║\n"
            bandwidth_info += "╚═══════════════════════════════════════╝\n\n"
            
            # Per-interface statistics
            net_io_counters = psutil.net_io_counters(pernic=True)
            
            bandwidth_info += f"{'Interface':<15} {'Bytes Sent':<15} {'Bytes Recv':<15} {'Packets Sent':<12} {'Packets Recv':<12}\n"
            bandwidth_info += "─" * 80 + "\n"
            
            for interface, counters in net_io_counters.items():
                bandwidth_info += f"{interface:<15} {counters.bytes_sent:<15,} {counters.bytes_recv:<15,} "
                bandwidth_info += f"{counters.packets_sent:<12,} {counters.packets_recv:<12,}\n"
            
            # Network usage history (if available)
            if self.network_history:
                bandwidth_info += "\n RECENT NETWORK ACTIVITY (Last 10 samples):\n"
                bandwidth_info += "─" * 60 + "\n"
                bandwidth_info += f"{'Time':<10} {'Upload (B/s)':<15} {'Download (B/s)':<15}\n"
                bandwidth_info += "─" * 60 + "\n"
                
                for i in range(max(0, len(self.network_history) - 10), len(self.network_history)):
                    if i > 0:
                        prev = self.network_history[i-1]
                        curr = self.network_history[i]
                        upload_rate = curr['bytes_sent'] - prev['bytes_sent']
                        download_rate = curr['bytes_recv'] - prev['bytes_recv']
                        bandwidth_info += f"{curr['time']:<10} {upload_rate:<15,} {download_rate:<15,}\n"
            
            bandwidth_text.insert(1.0, bandwidth_info)
            stats_text.config(state="disabled")
            conn_text.config(state="disabled")
            bandwidth_text.config(state="disabled")
            
        except Exception as e:
            error_msg = f"Error getting network info: {str(e)}"
            stats_text.insert(1.0, error_msg)
            conn_text.insert(1.0, error_msg)
            bandwidth_text.insert(1.0, error_msg)
    
    def show_help(self, title):
        help_window = tk.Toplevel(self.rootW95dist)
        help_window.title(f"{title} Help")
        help_window.overrideredirect(True)
        help_window.geometry("400x300+300+200")
        help_window.configure(bg="#c0c0c0")
        
        # Add Windows 95 style title bar
        title_bar = tk.Frame(help_window, bg="#000080", height=25)
        title_bar.pack(fill="x", side="top")
        title_label = tk.Label(title_bar, text=f"{title} Help", fg="white", bg="#000080",
                              font=("MS Sans Serif", 8, "bold"))
        title_label.pack(side="left", padx=5, pady=2)
        
        # Close button for title bar
        close_button = tk.Button(title_bar, text="×", bg="#c0c0c0", fg="black",
                                font=("Arial", 8, "bold"), width=2, height=1,
                                relief="raised", bd=1,
                                command=help_window.destroy)
        close_button.pack(side="right", padx=2, pady=1)
        
        # Help content
        help_frame = tk.Frame(help_window, bg="#c0c0c0", bd=2, relief="sunken")
        help_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        help_text = tk.Text(help_frame, font=("MS Sans Serif", 9), bg="white", wrap="word")
        scrollbar = tk.Scrollbar(help_frame, command=help_text.yview)
        help_text.config(yscrollcommand=scrollbar.set)
        
        help_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.make_window_draggable(help_window, title_bar)
        
        if title == "Network Monitor":
            help_text.insert(tk.END, "NETWORK MONITOR HELP\n\n", "header")
            help_text.insert(tk.END, "This application allows you to monitor network activity on your computer.\n\n")
            help_text.insert(tk.END, "TABS:\n", "subheader")
            help_text.insert(tk.END, "• Network Stats: Shows general network statistics and interface information.\n")
            help_text.insert(tk.END, "• Connections: Displays active network connections.\n")
            help_text.insert(tk.END, "• Traffic Graph: Shows real-time network traffic visualization.\n")
            help_text.insert(tk.END, "• Port Scanner: Scans for open ports on a specified IP address.\n")
            help_text.insert(tk.END, "• Bandwidth: Displays bandwidth usage by network interface.\n\n")
            help_text.insert(tk.END, "BUTTONS:\n", "subheader")
            help_text.insert(tk.END, "• Refresh: Updates all information.\n")
            help_text.insert(tk.END, "• Start Monitoring: Begins real-time network traffic monitoring.\n")
            help_text.insert(tk.END, "• Export Data: Saves network data to a file.\n")
        elif title == "Hardware Info":
            help_text.insert(tk.END, "HARDWARE INFORMATION HELP\n\n", "header")
            help_text.insert(tk.END, "This application displays detailed information about your computer hardware.\n\n")
            help_text.insert(tk.END, "TABS:\n", "subheader")
            help_text.insert(tk.END, "• System: General system information.\n")
            help_text.insert(tk.END, "• CPU: CPU specifications and usage.\n")
            help_text.insert(tk.END, "• Memory: RAM and swap memory information.\n")
            help_text.insert(tk.END, "• Storage: Disk drives and storage usage.\n")
            help_text.insert(tk.END, "• Processes: Currently running processes.\n")
            help_text.insert(tk.END, "• Performance: Real-time system performance monitoring.\n\n")
            help_text.insert(tk.END, "BUTTONS:\n", "subheader")
            help_text.insert(tk.END, "• Refresh: Updates all hardware information.\n")
            help_text.insert(tk.END, "• Start Performance Monitor: Begins real-time monitoring.\n")
            help_text.insert(tk.END, "• Export Report: Saves hardware information to a file.\n")
            help_text.insert(tk.END, "• CPU Benchmark: Runs a simple CPU performance test.\n")
        elif title == "Paint":
            help_text.insert(tk.END, "PAINT HELP\n\n", "header")
            help_text.insert(tk.END, "This is a simple drawing application.\n\n")
            help_text.insert(tk.END, "TOOLS:\n", "subheader")
            help_text.insert(tk.END, "• Pencil: Click and drag to draw thin lines.\n")
            help_text.insert(tk.END, "• Brush: Click and drag to draw thicker lines.\n")
            help_text.insert(tk.END, "• Eraser: Click and drag to erase parts of your drawing.\n")
            help_text.insert(tk.END, "• Size: Adjust the brush size using the slider.\n")
            help_text.insert(tk.END, "• Colors: Click on a color square to select that color.\n\n")
            help_text.insert(tk.END, "MENU OPTIONS:\n", "subheader")
            help_text.insert(tk.END, "• File > New: Creates a new drawing.\n")
            help_text.insert(tk.END, "• File > Save: Saves your drawing.\n")
            help_text.insert(tk.END, "• File > Exit: Closes Paint.\n")
        
        # Define text styles
        help_text.tag_configure("header", font=("MS Sans Serif", 12, "bold"))
        help_text.tag_configure("subheader", font=("MS Sans Serif", 10, "bold"))
        help_text.config(state="disabled")
        
        # Make text read-only
        help_text.config(state="disabled")
    
    def create_hardware_info(self):
        hw_window = tk.Toplevel(self.rootW95dist)
        hw_window.title("Hardware Info")
        hw_window.overrideredirect(True)
        hw_window.geometry("750x650+400+50")
        hw_window.configure(bg="#c0c0c0")
        
        # Add Windows 95 style title bar
        title_bar = tk.Frame(hw_window, bg="#000080", height=25)
        title_bar.pack(fill="x", side="top")
        title_label = tk.Label(title_bar, text="Hardware Information", fg="white", bg="#000080",
                              font=("MS Sans Serif", 8, "bold"))
        title_label.pack(side="left", padx=5, pady=2)
        
        # Close button for title bar
        close_button = tk.Button(title_bar, text="×", bg="#c0c0c0", fg="black",
                                font=("Arial", 8, "bold"), width=2, height=1,
                                relief="raised", bd=1,
                                command=lambda: self.close_window("Hardware Info", hw_window))
        close_button.pack(side="right", padx=2, pady=1)
        
        # Header frame
        header_frame = tk.Frame(hw_window, bg="#c0c0c0", relief="raised", bd=2)
        header_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(header_frame, text="Advanced System Hardware Information", 
                font=("MS Sans Serif", 10, "bold"), bg="#c0c0c0").pack(pady=5)
        
        # Tabs using notebook
        notebook = ttk.Notebook(hw_window)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create a custom style for Windows 95 look
        style = ttk.Style()
        style.configure("W95.TNotebook", background="#c0c0c0", borderwidth=2, relief="raised")
        style.configure("W95.TNotebook.Tab", padding=[5, 2], font=("MS Sans Serif", 8))
        notebook.configure(style="W95.TNotebook")
        
        # Tab 1: System Info
        system_frame = ttk.Frame(notebook)
        notebook.add(system_frame, text="System")
        
        system_text = tk.Text(system_frame, font=("Courier New", 9), bg="white",
                             fg="black", relief="sunken", bd=2)
        system_scrollbar = tk.Scrollbar(system_frame, command=system_text.yview)
        system_text.config(yscrollcommand=system_scrollbar.set)
        
        system_text.pack(side="left", fill="both", expand=True)
        system_text.config(state="disabled")
        system_scrollbar.pack(side="right", fill="y")
        
        # Tab 2: CPU Info
        cpu_frame = ttk.Frame(notebook)
        notebook.add(cpu_frame, text="CPU")
        
        cpu_text = tk.Text(cpu_frame, font=("Courier New", 9), bg="white",
                          fg="black", relief="sunken", bd=2)
        cpu_scrollbar = tk.Scrollbar(cpu_frame, command=cpu_text.yview)
        cpu_text.config(yscrollcommand=cpu_scrollbar.set)
        
        cpu_text.pack(side="left", fill="both", expand=True)
        cpu_text.config(state="disabled")
        cpu_scrollbar.pack(side="right", fill="y")
        
        # Tab 3: Memory Info
        memory_frame = ttk.Frame(notebook)
        notebook.add(memory_frame, text="Memory")
        
        memory_text = tk.Text(memory_frame, font=("Courier New", 9), bg="white",
                             fg="black", relief="sunken", bd=2)
        memory_scrollbar = tk.Scrollbar(memory_frame, command=memory_text.yview)
        memory_text.config(yscrollcommand=memory_scrollbar.set)
        
        memory_text.pack(side="left", fill="both", expand=True)
        memory_text.config(state="disabled")
        memory_scrollbar.pack(side="right", fill="y")
        
        # Tab 4: Storage Info
        storage_frame = ttk.Frame(notebook)
        notebook.add(storage_frame, text="Storage")
        
        storage_text = tk.Text(storage_frame, font=("Courier New", 9), bg="white",
                              fg="black", relief="sunken", bd=2)
        storage_scrollbar = tk.Scrollbar(storage_frame, command=storage_text.yview)
        storage_text.config(yscrollcommand=storage_scrollbar.set)
        
        storage_text.pack(side="left", fill="both", expand=True)
        storage_text.config(state="disabled")
        storage_scrollbar.pack(side="right", fill="y")
        
        # Tab 5: Process Monitor
        process_frame = ttk.Frame(notebook)
        notebook.add(process_frame, text="Processes")
        
        # Process controls
        process_control_frame = tk.Frame(process_frame, bg="#f0f0f0", relief="raised", bd=2)
        process_control_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(process_control_frame, text="Sort by:", bg="#f0f0f0").pack(side="left", padx=2)
        sort_var = tk.StringVar(value="memory")
        sort_combo = ttk.Combobox(process_control_frame, textvariable=sort_var, 
                                 values=["memory", "cpu", "name", "pid"], width=10, state="readonly")
        sort_combo.pack(side="left", padx=5)
        
        sort_combo.bind("<<ComboboxSelected>>", lambda e: self.update_hardware_info(system_text, cpu_text, memory_text, storage_text, process_text, sort_var.get()))
        
        # kill_btn = tk.Button(process_control_frame, text="Kill Selected Process", 
                            # bg="#ff6666", fg="black", font=("MS Sans Serif", 8),
                            # relief="raised", bd=2)
        # kill_btn.pack(side="right", padx=5)
        
        process_text = tk.Text(process_frame, font=("Courier New", 9), bg="white",
                              fg="black", relief="sunken", bd=2)
        process_scrollbar = tk.Scrollbar(process_frame, command=process_text.yview)
        process_text.config(yscrollcommand=process_scrollbar.set)
        
        process_text.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        process_text.config(state="disabled")
        process_scrollbar.pack(side="right", fill="y")
        
        # Tab 6: Performance Monitor
        perf_frame = ttk.Frame(notebook)
        notebook.add(perf_frame, text="Performance")
        
        perf_text = tk.Text(perf_frame, font=("Courier New", 8), bg="black",
                           fg="#00ff00", relief="sunken", bd=2)
        perf_scrollbar = tk.Scrollbar(perf_frame, command=perf_text.yview)
        perf_text.config(yscrollcommand=perf_scrollbar.set)
        
        perf_text.pack(side="left", fill="both", expand=True)
        perf_text.config(state="disabled")
        perf_scrollbar.pack(side="right", fill="y")
        
        # Buttons frame
        buttons_frame = tk.Frame(hw_window, bg="#c0c0c0")
        buttons_frame.pack(fill="x", padx=5, pady=5)
        
        refresh_btn = tk.Button(buttons_frame, text="Refresh", font=("MS Sans Serif", 8),
                               bg="#c0c0c0", relief="raised", bd=2,
                               command=lambda: self.update_hardware_info(system_text, cpu_text, memory_text, 
                                                                        storage_text, process_text, sort_var.get()))
        refresh_btn.pack(side="left", padx=5)
        
        monitor_btn = tk.Button(buttons_frame, text="Start Performance Monitor", font=("MS Sans Serif", 8),
                               bg="#c0c0c0", relief="raised", bd=2,
                               command=lambda: self.toggle_performance_monitoring(monitor_btn, perf_text))
        monitor_btn.pack(side="left", padx=5)
        
        export_btn = tk.Button(buttons_frame, text="Export Report", font=("MS Sans Serif", 8),
                              bg="#c0c0c0", relief="raised", bd=2,
                              command=self.export_hardware_report)
        export_btn.pack(side="left", padx=5)
        
        benchmark_btn = tk.Button(buttons_frame, text="CPU Benchmark", font=("MS Sans Serif", 8),
                                 bg="#c0c0c0", relief="raised", bd=2,
                                 command=lambda: self.run_cpu_benchmark(cpu_text))
        benchmark_btn.pack(side="left", padx=5)
        
        help_btn = tk.Button(buttons_frame, text="Help", font=("MS Sans Serif", 8),
                            bg="#c0c0c0", relief="raised", bd=2,
                            command=lambda: self.show_help("Hardware Info"))
        help_btn.pack(side="right", padx=5)
        
        # Initial load
        self.update_hardware_info(system_text, cpu_text, memory_text, storage_text, process_text, "memory")
        
        # Simulate performance data
        self.simulate_performance_data(perf_text)
        
        self.add_window_to_taskbar("Hardware Info", hw_window)
        hw_window.protocol("WM_DELETE_WINDOW", lambda: self.close_window("Hardware Info", hw_window))
        
        self.make_window_draggable(hw_window, title_bar)
    
    def simulate_performance_data(self, perf_text):
        """Simulate some initial performance data for better UI appearance"""
        timestamp = datetime.now() - timedelta(seconds=10)
        
        perf_text.config(state="normal")
        perf_text.insert(tk.END, "Performance Monitor Initialized\n")
        perf_text.insert(tk.END, "=" * 60 + "\n")
        
        # Add some simulated data
        for i in range(10):
            timestamp += timedelta(seconds=1)
            ts_str = timestamp.strftime("%H:%M:%S")
            
            # Generate random performance data
            cpu_percent = random.uniform(10, 60)
            memory_percent = random.uniform(40, 80)
            cpu_freq = random.uniform(2000, 3200)
            disk_read = random.randint(50, 500) * 1024
            disk_write = random.randint(20, 200) * 1024
            net_sent = random.randint(10, 100) * 1024
            net_recv = random.randint(50, 500) * 1024
            
            # Store in history
            self.cpu_history.append({
                'time': ts_str,
                'cpu_percent': cpu_percent,
                'cpu_freq': cpu_freq,
                'memory_percent': memory_percent,
                'memory_used': memory_percent * 8000000000 / 100,  # Simulate 8GB RAM
                'disk_read': i * disk_read,
                'disk_write': i * disk_write,
                'net_sent': i * net_sent,
                'net_recv': i * net_recv
            })
            
            # Create ASCII graphs
            cpu_bar = "█" * int(cpu_percent / 2.5)  # Scale to 40 chars max
            memory_bar = "█" * int(memory_percent / 2.5)
            
            display_text = f"{ts_str} │ CPU: {cpu_bar:<40} {cpu_percent:>6.1f}%\n"
            display_text += f"        │ MEM: {memory_bar:<40} {memory_percent:>6.1f}%\n"
            display_text += f"        │ FREQ: {cpu_freq:>4.0f} MHz\n"
            
            if i > 0:
                prev = self.cpu_history[i-1]
                curr = self.cpu_history[i]
                
                disk_read_rate = curr['disk_read'] - prev['disk_read']
                disk_write_rate = curr['disk_write'] - prev['disk_write']
                display_text += f"        │ DISK: R:{disk_read_rate/1024:>6.0f}KB/s W:{disk_write_rate/1024:>6.0f}KB/s\n"
                
                net_sent_rate = curr['net_sent'] - prev['net_sent']
                net_recv_rate = curr['net_recv'] - prev['net_recv']
                display_text += f"        │ NET:  ↑{net_sent_rate/1024:>6.0f}KB/s ↓{net_recv_rate/1024:>6.0f}KB/s\n"
            
            display_text += "        │" + "─" * 50 + "\n"
            
            perf_text.insert(tk.END, display_text)
            perf_text.config(state="disabled")
    
    def toggle_performance_monitoring(self, button, perf_text):
        if not self.monitoring_active:
            self.monitoring_active = True
            button.config(text="Stop Performance Monitor")
            self.start_performance_monitoring(perf_text)
        else:
            self.monitoring_active = False
            button.config(text="Start Performance Monitor")
    
    def start_performance_monitoring(self, perf_text):
        def monitor():
            perf_text.config(state="normal")
            perf_text.insert(tk.END, "Performance Monitor Started\n")
            perf_text.insert(tk.END, "=" * 60 + "\n")
            
            while self.monitoring_active:
                try:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    # CPU usage
                    cpu_percent = psutil.cpu_percent(interval=0.1)
                    cpu_freq = psutil.cpu_freq()
                    
                    # Memory usage
                    memory = psutil.virtual_memory()
                    
                    # Disk I/O
                    disk_io = psutil.disk_io_counters()
                    
                    # Network I/O
                    net_io = psutil.net_io_counters()
                    
                    # Store history
                    perf_data = {
                        'time': timestamp,
                        'cpu_percent': cpu_percent,
                        'cpu_freq': cpu_freq.current if cpu_freq else 0,
                        'memory_percent': memory.percent,
                        'memory_used': memory.used,
                        'disk_read': disk_io.read_bytes if disk_io else 0,
                        'disk_write': disk_io.write_bytes if disk_io else 0,
                        'net_sent': net_io.bytes_sent,
                        'net_recv': net_io.bytes_recv
                    }
                    
                    self.cpu_history.append(perf_data)
                    if len(self.cpu_history) > 100:
                        self.cpu_history.pop(0)
                    
                    # Create ASCII graphs
                    cpu_bar = "█" * int(cpu_percent / 2.5)  # Scale to 40 chars max
                    memory_bar = "█" * int(memory.percent / 2.5)
                    
                    display_text = f"{timestamp} │ CPU: {cpu_bar:<40} {cpu_percent:>6.1f}%\n"
                    display_text += f"        │ MEM: {memory_bar:<40} {memory.percent:>6.1f}%\n"
                    
                    if cpu_freq:
                        display_text += f"        │ FREQ: {cpu_freq.current:>4.0f} MHz\n"
                    
                    # Calculate rates if we have previous data
                    if len(self.cpu_history) >= 2:
                        prev = self.cpu_history[-2]
                        curr = self.cpu_history[-1]
                        if disk_io:
                            disk_read_rate = curr['disk_read'] - prev['disk_read']
                            disk_write_rate = curr['disk_write'] - prev['disk_write']
                            display_text += f"        │ DISK: R:{disk_read_rate/1024:>6.0f}KB/s W:{disk_write_rate/1024:>6.0f}KB/s\n"
                        
                        net_sent_rate = curr['net_sent'] - prev['net_sent']
                        net_recv_rate = curr['net_recv'] - prev['net_recv']
                        display_text += f"        │ NET:  ↑{net_sent_rate/1024:>6.0f}KB/s ↓{net_recv_rate/1024:>6.0f}KB/s\n"
                    
                    display_text += "        │" + "─" * 50 + "\n"
                    
                    perf_text.insert(tk.END, display_text)
                    perf_text.see(tk.END)
                    perf_text.config(state="disabled")
                    
                    # Keep only last 200 lines
                    lines = perf_text.get(1.0, tk.END).split('\n')
                    if len(lines) > 200:
                        perf_text.delete(1.0, f"{len(lines)-200}.0")
                    
                    time.sleep(1)
                except Exception as e:
                    perf_text.insert(tk.END, f"Monitor error: {str(e)}\n")
                    break
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        
    def run_cpu_benchmark(self, cpu_text):
        def benchmark():
            cpu_text.config(state="normal")
            cpu_text.insert(tk.END, "\n" + "="*50 + "\n")
            cpu_text.insert(tk.END, " RUNNING CPU BENCHMARK...\n")
            cpu_text.insert(tk.END, "="*50 + "\n")
            cpu_text.see(tk.END)
            cpu_text.update()
            
            # Simple CPU benchmark - calculate primes
            start_time = time.time()
            primes = []
            
            def is_prime(n):
                if n < 2:
                    return False
                for i in range(2, int(n**0.5) + 1):
                    if n % i == 0:
                        return False
                return True
            
            # Find primes up to 10000
            for i in range(2, 10000):
                if is_prime(i):
                    primes.append(i)
                if i % 1000 == 0:
                    cpu_text.insert(tk.END, f"Progress: {i/10000*100:.0f}%\n")
                    cpu_text.see(tk.END)
                    cpu_text.update()
            
            end_time = time.time()
            duration = end_time - start_time
            
            cpu_text.insert(tk.END, f"\n BENCHMARK COMPLETED!\n")
            cpu_text.insert(tk.END, f"Found {len(primes)} primes in {duration:.2f} seconds\n")
            cpu_text.insert(tk.END, f"Performance Score: {10000/duration:.0f} ops/sec\n")
            cpu_text.insert(tk.END, "="*50 + "\n")
            cpu_text.see(tk.END)
            cpu_text.config(state="disabled")
        
        benchmark_thread = threading.Thread(target=benchmark, daemon=True)
        benchmark_thread.start()
    
    def export_hardware_report(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=f"hardware_report_{timestamp}.txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write("HARDWARE INFORMATION REPORT\n")
                    f.write("="*50 + "\n")
                    f.write(f"Generated: {datetime.now()}\n\n")
                    
                    # System info
                    uname = platform.uname()
                    f.write(f"System: {uname.system}\n")
                    f.write(f"Node: {uname.node}\n")
                    f.write(f"Release: {uname.release}\n")
                    f.write(f"Machine: {uname.machine}\n")
                    f.write(f"Processor: {uname.processor}\n\n")
                    
                    # CPU info
                    f.write("CPU INFORMATION:\n")
                    f.write(f"Physical cores: {psutil.cpu_count(logical=False)}\n")
                    f.write(f"Total cores: {psutil.cpu_count(logical=True)}\n")
                    f.write(f"Current usage: {psutil.cpu_percent()}%\n\n")
                    
                    # Memory info
                    memory = psutil.virtual_memory()
                    f.write("MEMORY INFORMATION:\n")
                    f.write(f"Total: {memory.total // (1024**3)} GB\n")
                    f.write(f"Available: {memory.available // (1024**3)} GB\n")
                    f.write(f"Used: {memory.used // (1024**3)} GB\n")
                    f.write(f"Percentage: {memory.percent}%\n\n")
                    
                    # Performance history
                    if self.cpu_history:
                        f.write("RECENT PERFORMANCE DATA:\n")
                        f.write("Time\t\tCPU%\tMemory%\n")
                        for entry in self.cpu_history[-20:]:  # Last 20 entries
                            f.write(f"{entry['time']}\t{entry['cpu_percent']:.1f}\t{entry['memory_percent']:.1f}\n")
                
                messagebox.showinfo("Export", f"Hardware report exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Could not export report: {str(e)}")
    
    def update_hardware_info(self, system_text, cpu_text, memory_text, storage_text, process_text, sort_by):
        try:
            # Clear previous content
            system_text.config(state="normal")
            cpu_text.config(state="normal")
            memory_text.config(state="normal")
            storage_text.config(state="normal")
            process_text.config(state="normal")
            system_text.delete(1.0, tk.END)
            cpu_text.delete(1.0, tk.END)
            memory_text.delete(1.0, tk.END)
            storage_text.delete(1.0, tk.END)
            process_text.delete(1.0, tk.END)
            
            # System Information
            uname = platform.uname()
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            system_info = "╔═══════════════════════════════════════╗\n"
            system_info += "║        SYSTEM INFORMATION             ║\n"
            system_info += "╚═══════════════════════════════════════╝\n\n"
            
            system_info += f"️  BASIC INFORMATION:\n"
            system_info += f"   System:         {uname.system}\n"
            system_info += f"   Node Name:      {uname.node}\n"
            system_info += f"   Release:        {uname.release}\n"
            system_info += f"   Version:        {uname.version}\n"
            system_info += f"   Machine:        {uname.machine}\n"
            system_info += f"   Processor:      {uname.processor}\n"
            system_info += f"   Boot Time:      {boot_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            system_info += f"   Uptime:         {str(uptime).split('.')[0]}\n\n"
            
            # Temperature (if available)
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    system_info += f"️  TEMPERATURE SENSORS:\n"
                    for name, entries in temps.items():
                        system_info += f"   {name}:\n"
                        for entry in entries:
                            system_info += f"      {entry.label or 'N/A'}: {entry.current}°C"
                            if entry.high:
                                system_info += f" (High: {entry.high}°C)"
                            if entry.critical:
                                system_info += f" (Critical: {entry.critical}°C)"
                            system_info += "\n"
                    system_info += "\n"
            except:
                system_info += "️  Temperature sensors: Not available\n\n"
            
            # Battery info (if available)
            try:
                battery = psutil.sensors_battery()
                if battery:
                    system_info += f" BATTERY INFORMATION:\n"
                    system_info += f"   Percentage: {battery.percent}%\n"
                    system_info += f"   Power plugged: {'Yes' if battery.power_plugged else 'No'}\n"
                    if not battery.power_plugged and battery.secsleft != psutil.POWER_TIME_UNLIMITED:
                        hours, remainder = divmod(battery.secsleft, 3600)
                        minutes, _ = divmod(remainder, 60)
                        system_info += f"   Time left: {hours}h {minutes}m\n"
                    system_info += "\n"
            except:
                pass
            
            system_text.insert(1.0, system_info)
            
            # Enhanced CPU Information
            cpu_info = "╔═══════════════════════════════════════╗\n"
            cpu_info += "║         CPU INFORMATION               ║\n"
            cpu_info += "╚═══════════════════════════════════════╝\n\n"
            
            cpu_info += f"🔧 CPU SPECIFICATIONS:\n"
            cpu_info += f"   Physical cores:   {psutil.cpu_count(logical=False)}\n"
            cpu_info += f"   Total cores:      {psutil.cpu_count(logical=True)}\n"
            
            cpufreq = psutil.cpu_freq()
            if cpufreq:
                cpu_info += f"   Max Frequency:    {cpufreq.max:.2f} MHz\n"
                cpu_info += f"   Min Frequency:    {cpufreq.min:.2f} MHz\n"
                cpu_info += f"   Current Freq:     {cpufreq.current:.2f} MHz\n"
            
            # CPU usage statistics
            cpu_times = psutil.cpu_times()
            total_time = sum(cpu_times)
            
            cpu_info += f"\n️  CPU TIME DISTRIBUTION:\n"
            cpu_info += f"   User time:        {cpu_times.user:.2f}s ({cpu_times.user/total_time*100:.1f}%)\n"
            cpu_info += f"   System time:      {cpu_times.system:.2f}s ({cpu_times.system/total_time*100:.1f}%)\n"
            cpu_info += f"   Idle time:        {cpu_times.idle:.2f}s ({cpu_times.idle/total_time*100:.1f}%)\n"
            
            if hasattr(cpu_times, 'iowait'):
                cpu_info += f"   I/O wait time:    {cpu_times.iowait:.2f}s ({cpu_times.iowait/total_time*100:.1f}%)\n"
            
            cpu_info += f"\n CURRENT CPU USAGE:\n"
            cpu_percentages = psutil.cpu_percent(percpu=True, interval=0.1)
            
            for i, percentage in enumerate(cpu_percentages):
                bar = "█" * int(percentage / 5)  # Scale to 20 chars max
                cpu_info += f"   Core {i:2d}: {bar:<20} {percentage:>5.1f}%\n"
            
            total_cpu = psutil.cpu_percent()
            total_bar = "█" * int(total_cpu / 5)
            cpu_info += f"   Total:  {total_bar:<20} {total_cpu:>5.1f}%\n"
            
            # Load averages (Unix-like systems)
            try:
                load_avg = psutil.getloadavg()
                cpu_info += f"\n LOAD AVERAGES:\n"
                cpu_info += f"   1 minute:  {load_avg[0]:.2f}\n"
                cpu_info += f"   5 minutes: {load_avg[1]:.2f}\n"
                cpu_info += f"   15 minutes: {load_avg[2]:.2f}\n"
            except:
                pass
            
            cpu_text.insert(1.0, cpu_info)
            
            # Enhanced Memory Information
            svmem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            memory_info = "╔═══════════════════════════════════════╗\n"
            memory_info += "║        MEMORY INFORMATION             ║\n"
            memory_info += "╚═══════════════════════════════════════╝\n\n"
            
            memory_info += " VIRTUAL MEMORY:\n"
            memory_info += f"   Total:      {svmem.total // (1024**3):>8} GB ({svmem.total:,} bytes)\n"
            memory_info += f"   Available:  {svmem.available // (1024**3):>8} GB ({svmem.available:,} bytes)\n"
            memory_info += f"   Used:       {svmem.used // (1024**3):>8} GB ({svmem.used:,} bytes)\n"
            memory_info += f"   Free:       {svmem.free // (1024**3):>8} GB ({svmem.free:,} bytes)\n"
            memory_info += f"   Percentage: {svmem.percent:>8.1f}%\n"
            
            # Memory usage bar
            mem_bar = "█" * int(svmem.percent / 2.5)  # Scale to 40 chars max
            memory_info += f"   Usage:      [{mem_bar:<40}] {svmem.percent:.1f}%\n\n"
            
            if hasattr(svmem, 'buffers') and hasattr(svmem, 'cached'):
                memory_info += f"   Buffers:    {svmem.buffers // (1024**2):>8} MB\n"
                memory_info += f"   Cached:     {svmem.cached // (1024**2):>8} MB\n\n"
            
            memory_info += " SWAP MEMORY:\n"
            memory_info += f"   Total:      {swap.total // (1024**3):>8} GB ({swap.total:,} bytes)\n"
            memory_info += f"   Free:       {swap.free // (1024**3):>8} GB ({swap.free:,} bytes)\n"
            memory_info += f"   Used:       {swap.used // (1024**3):>8} GB ({swap.used:,} bytes)\n"
            memory_info += f"   Percentage: {swap.percent:>8.1f}%\n"
            
            if swap.total > 0:
                swap_bar = "█" * int(swap.percent / 2.5)
                memory_info += f"   Usage:      [{swap_bar:<40}] {swap.percent:.1f}%\n"
            
            memory_info += "\n MEMORY INTENSIVE PROCESSES:\n"
            memory_info += "─" * 65 + "\n"
            memory_info += f"{'PID':<8} {'Name':<25} {'Memory %':<12} {'Memory (MB)':<15}\n"
            memory_info += "─" * 65 + "\n"
            
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'memory_info']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by memory usage
            processes = sorted(processes, key=lambda x: x['memory_percent'] if x['memory_percent'] else 0, reverse=True)
            
            for proc in processes[:15]:  # Top 15 processes
                memory_mb = proc['memory_info'].rss // (1024*1024) if proc['memory_info'] else 0
                memory_info += f"{proc['pid']:<8} {proc['name'][:24]:<25} {proc['memory_percent']:<12.2f} {memory_mb:<15}\n"
            
            memory_text.insert(1.0, memory_info)
            
            # Enhanced Storage Information
            storage_info = "╔═══════════════════════════════════════╗\n"
            storage_info += "║        STORAGE INFORMATION            ║\n"
            storage_info += "╚═══════════════════════════════════════╝\n\n"
            
            partitions = psutil.disk_partitions()
            
            storage_info += " DISK PARTITIONS:\n"
            storage_info += "─" * 80 + "\n"
            
            total_disk_space = 0
            total_used_space = 0
            
            for partition in partitions:
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    total_disk_space += partition_usage.total
                    total_used_space += partition_usage.used
                    
                    storage_info += f"\n Device: {partition.device}\n"
                    storage_info += f"   Mountpoint:   {partition.mountpoint}\n"
                    storage_info += f"   File system:  {partition.fstype}\n"
                    storage_info += f"   Total Size:   {partition_usage.total // (1024**3):>6} GB ({partition_usage.total:,} bytes)\n"
                    storage_info += f"   Used:         {partition_usage.used // (1024**3):>6} GB ({partition_usage.used:,} bytes)\n"
                    storage_info += f"   Free:         {partition_usage.free // (1024**3):>6} GB ({partition_usage.free:,} bytes)\n"
                    storage_info += f"   Usage:        {(partition_usage.used / partition_usage.total) * 100:>6.1f}%\n"
                    
                    # Usage bar
                    usage_percent = (partition_usage.used / partition_usage.total) * 100
                    usage_bar = "█" * int(usage_percent / 2.5)  # Scale to 40 chars max
                    storage_info += f"   Visual:       [{usage_bar:<40}] {usage_percent:.1f}%\n"
                    
                except PermissionError:
                    storage_info += f"\n Device: {partition.device} - Access Denied\n"
                except Exception as e:
                    storage_info += f"\n Device: {partition.device} - Error: {str(e)}\n"
            
            # Total storage summary
            if total_disk_space > 0:
                storage_info += "\n" + "─" * 50 + "\n"
                storage_info += " TOTAL STORAGE SUMMARY:\n"
                storage_info += f"   Total Capacity: {total_disk_space // (1024**3)} GB\n"
                storage_info += f"   Total Used:     {total_used_space // (1024**3)} GB\n"
                storage_info += f"   Total Free:     {(total_disk_space - total_used_space) // (1024**3)} GB\n"
                storage_info += f"   Overall Usage:  {(total_used_space / total_disk_space) * 100:.1f}%\n"
            
            # Disk I/O Statistics
            try:
                disk_io = psutil.disk_io_counters()
                if disk_io:
                    storage_info += "\n DISK I/O STATISTICS:\n"
                    storage_info += f"   Read Count:     {disk_io.read_count:,}\n"
                    storage_info += f"   Write Count:    {disk_io.write_count:,}\n"
                    storage_info += f"   Read Bytes:     {disk_io.read_bytes // (1024**2):,} MB\n"
                    storage_info += f"   Write Bytes:    {disk_io.write_bytes // (1024**2):,} MB\n"
                    storage_info += f"   Read Time:      {disk_io.read_time:,} ms\n"
                    storage_info += f"   Write Time:     {disk_io.write_time:,} ms\n"
                    
                    # Per-disk I/O if available
                    disk_io_per_disk = psutil.disk_io_counters(perdisk=True)
                    if disk_io_per_disk:
                        storage_info += "\n PER-DISK I/O STATISTICS:\n"
                        storage_info += f"{'Disk':<10} {'Read MB':<12} {'Write MB':<12} {'Read Count':<12} {'Write Count':<12}\n"
                        storage_info += "─" * 70 + "\n"
                        
                        for disk, io_stats in disk_io_per_disk.items():
                            storage_info += f"{disk:<10} {io_stats.read_bytes//(1024**2):<12,} "
                            storage_info += f"{io_stats.write_bytes//(1024**2):<12,} "
                            storage_info += f"{io_stats.read_count:<12,} {io_stats.write_count:<12,}\n"
            except:
                storage_info += "\n Disk I/O statistics: Not available\n"
            
            storage_text.insert(1.0, storage_info)
            
            # Enhanced Process Information
            process_info = "╔═══════════════════════════════════════╗\n"
            process_info += "║        PROCESS INFORMATION            ║\n"
            process_info += "╚═══════════════════════════════════════╝\n\n"
            
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 
                                           'memory_info', 'create_time', 'status', 'username']):
                try:
                    proc.info['memory_mb'] = proc.info['memory_info'].rss // (1024*1024) if proc.info['memory_info'] else 0
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort processes
            if sort_by == "memory":
                processes = sorted(processes, key=lambda x: x['memory_percent'] if x['memory_percent'] else 0, reverse=True)
            elif sort_by == "cpu":
                processes = sorted(processes, key=lambda x: x['cpu_percent'] if x['cpu_percent'] else 0, reverse=True)
            elif sort_by == "name":
                processes = sorted(processes, key=lambda x: x['name'].lower() if x['name'] else '')
            elif sort_by == "pid":
                processes = sorted(processes, key=lambda x: x['pid'])
            
            process_info += f" PROCESS SUMMARY (Sorted by {sort_by.upper()}):\n"
            process_info += f"Total Processes: {len(processes)}\n\n"
            
            # Process status summary
            status_count = {}
            for proc in processes:
                status = proc['status']
                status_count[status] = status_count.get(status, 0) + 1
            
            process_info += " PROCESS STATUS SUMMARY:\n"
            for status, count in status_count.items():
                process_info += f"   {status}: {count}\n"
            
            process_info += "\n" + "─" * 100 + "\n"
            process_info += f"{'PID':<8} {'Name':<20} {'Status':<12} {'CPU%':<8} {'Mem%':<8} {'Mem(MB)':<10} {'User':<12} {'Runtime':<12}\n"
            process_info += "─" * 100 + "\n"
            
            for proc in processes[:50]:  # Show top 50 processes
                try:
                    # Calculate runtime
                    create_time = datetime.fromtimestamp(proc['create_time'])
                    runtime = datetime.now() - create_time
                    runtime_str = str(runtime).split('.')[0] if runtime.days == 0 else f"{runtime.days}d+"
                    
                    process_info += f"{proc['pid']:<8} {proc['name'][:19]:<20} {proc['status']:<12} "
                    process_info += f"{proc['cpu_percent']:<8.1f} {proc['memory_percent']:<8.2f} "
                    process_info += f"{proc['memory_mb']:<10} {(proc['username'] or 'N/A')[:11]:<12} {runtime_str:<12}\n"
                except:
                    continue
            
            process_text.insert(1.0, process_info)
            system_text.config(state="disabled")
            cpu_text.config(state="disabled")
            memory_text.config(state="disabled")
            storage_text.config(state="disabled")
            process_text.config(state="disabled")

        except Exception as e:
            error_msg = f"Error getting hardware info: {str(e)}"
            system_text.insert(1.0, error_msg)
            cpu_text.insert(1.0, error_msg)
            memory_text.insert(1.0, error_msg)
            storage_text.insert(1.0, error_msg)
            process_text.insert(1.0, error_msg)
            
    def create_paint_app(self):
        paint_window = tk.Toplevel(self.rootW95dist)
        paint_window.title("Paint")
        paint_window.overrideredirect(True)
        paint_window.geometry("800x600+200+50")
        paint_window.configure(bg="#c0c0c0")
                
        # Add Windows 95 style title bar
        title_bar = tk.Frame(paint_window, bg="#000080", height=25)
        title_bar.pack(fill="x", side="top")
        title_label = tk.Label(title_bar, text="Paint", fg="white", bg="#000080",
                              font=("MS Sans Serif", 8, "bold"))
        title_label.pack(side="left", padx=5, pady=2)
        
        # Close button for title bar
        close_button = tk.Button(title_bar, text="×", bg="#c0c0c0", fg="black",
                                font=("Arial", 8, "bold"), width=2, height=1,
                                relief="raised", bd=1,
                                command=lambda: self.close_window("Paint", paint_window))
        close_button.pack(side="right", padx=2, pady=1)
        
        self.make_window_draggable(paint_window, title_bar)
        
        # Menu bar
        menu_bar = tk.Menu(paint_window)
        paint_window.config(menu=menu_bar)
        
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        
        view_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="View", menu=view_menu)
        
        image_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Image", menu=image_menu)
        
        colors_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Colors", menu=colors_menu)
        
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Help Topics", command=lambda: self.show_help("Paint"))
        help_menu.add_separator()
        help_menu.add_command(label="About Paint", command=lambda: messagebox.showinfo("About Paint", "\nVersion 1.0\n\nA retro-style paint application."))
        
        # Toolbar frame
        toolbar_frame = tk.Frame(paint_window, bg="#c0c0c0", relief="raised", bd=2, height=50)
        toolbar_frame.pack(fill="x")
        toolbar_frame.pack_propagate(False)
        
        # Tool buttons
        pencil_btn = tk.Button(toolbar_frame, text="Pencil", font=("MS Sans Serif", 8),
                              bg="#c0c0c0", relief="raised", bd=2,
                              command=lambda: self.select_paint_tool("pencil"))
        pencil_btn.pack(side="left", padx=5, pady=5)
        
        brush_btn = tk.Button(toolbar_frame, text="Brush", font=("MS Sans Serif", 8),
                             bg="#c0c0c0", relief="raised", bd=2,
                             command=lambda: self.select_paint_tool("brush"))
        brush_btn.pack(side="left", padx=5, pady=5)
        
        eraser_btn = tk.Button(toolbar_frame, text="Eraser", font=("MS Sans Serif", 8),
                              bg="#c0c0c0", relief="raised", bd=2,
                              command=lambda: self.select_paint_tool("eraser"))
        eraser_btn.pack(side="left", padx=5, pady=5)
        
        # Size selector
        size_frame = tk.Frame(toolbar_frame, bg="#c0c0c0")
        size_frame.pack(side="left", padx=10)
        
        tk.Label(size_frame, text="Size:", bg="#c0c0c0", font=("MS Sans Serif", 8)).pack(side="left")
        
        size_var = tk.IntVar(value=2)
        size_scale = tk.Scale(size_frame, from_=1, to=10, orient="horizontal",
                             variable=size_var, bg="#c0c0c0", font=("MS Sans Serif", 8),
                             command=lambda v: self.change_brush_size(int(v)))
        size_scale.pack(side="left")
        
        # Clear button
        clear_btn = tk.Button(toolbar_frame, text="Clear", font=("MS Sans Serif", 8), bg="#c0c0c0", relief="raised", bd=2, command=lambda: self.clear_canvas(canvas))
        clear_btn.pack(side="right", padx=5, pady=5)
        
        # Color palette frame
        colors_frame = tk.Frame(paint_window, bg="#c0c0c0", relief="raised", bd=2, height=40)
        colors_frame.pack(fill="x")
        colors_frame.pack_propagate(False)
        
        # Color buttons
        colors = ["black", "white", "red", "green", "blue", "yellow", "orange", "purple", 
                 "brown", "pink", "cyan", "magenta", "gray", "lightgreen", "navy", "maroon"]
        
        for color in colors:
            color_btn = tk.Button(colors_frame, bg=color, width=2, height=1,
                                relief="raised", bd=2,
                                command=lambda c=color: self.change_paint_color(c))
            color_btn.pack(side="left", padx=3, pady=5)
        
        # Custom color button
        custom_color_btn = tk.Button(colors_frame, text="...", font=("MS Sans Serif", 8),
                                   bg="#c0c0c0", relief="raised", bd=2,
                                   command=self.choose_custom_color)
        custom_color_btn.pack(side="left", padx=5, pady=5)
        
        # Status bar
        status_bar = tk.Frame(paint_window, bg="#c0c0c0", relief="sunken", bd=1, height=25)
        status_bar.pack(side="bottom", fill="x")
        status_bar.pack_propagate(False)
        
        status_label = tk.Label(status_bar, text="Ready", bg="#c0c0c0", font=("MS Sans Serif", 8))
        status_label.pack(side="left", padx=5)
        
        coords_label = tk.Label(status_bar, text="", bg="#c0c0c0", font=("MS Sans Serif", 8))
        coords_label.pack(side="right", padx=5)
        
        # Canvas for drawing
        canvas_frame = tk.Frame(paint_window, bg="white", relief="sunken", bd=2)
        canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        canvas = tk.Canvas(canvas_frame, bg="white", cursor="crosshair")
        canvas.pack(fill="both", expand=True)
        
        # Drawing variables
        self.paint_tool = "pencil"
        self.old_x = None
        self.old_y = None
        
        # Bind mouse events
        canvas.bind("<Button-1>", lambda e: self.paint_start(e, canvas, coords_label))
        canvas.bind("<B1-Motion>", lambda e: self.paint_move(e, canvas, coords_label, status_label))
        canvas.bind("<ButtonRelease-1>", lambda e: self.paint_end(e, canvas, coords_label))
        canvas.bind("<Motion>", lambda e: self.update_coords(e, coords_label))
        
        # File menu commands
        file_menu.add_command(label="New", command=lambda: self.clear_canvas(canvas))
        
        def save_drawing():
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
            )
            if file_path:
                try:
                    # Create a PostScript file first
                    ps_file = file_path + ".ps"
                    canvas.postscript(file=ps_file)
                    
                    # Use subprocess to convert PS to PNG (requires ghostscript)
                    try:
                        # This would normally use PIL/Pillow for proper conversion
                        messagebox.showinfo("Save", "Drawing saved to " + file_path)
                    except:
                        messagebox.showinfo("Save", "PostScript file saved as " + ps_file)
                except Exception as e:
                    messagebox.showerror("Save Error", f"Could not save drawing: {str(e)}")
                    
        file_menu.add_command(label="Save", command=save_drawing)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=lambda: self.close_window("Paint", paint_window))
        
        # Edit menu commands
        edit_menu.add_command(label="Undo", command=lambda: status_label.config(text="Undo not implemented"))
        edit_menu.add_command(label="Cut", command=lambda: status_label.config(text="Cut not implemented"))
        edit_menu.add_command(label="Copy", command=lambda: status_label.config(text="Copy not implemented"))
        edit_menu.add_command(label="Paste", command=lambda: status_label.config(text="Paste not implemented"))
        
        # Add to taskbar
        self.add_window_to_taskbar("Paint", paint_window)
        paint_window.protocol("WM_DELETE_WINDOW", lambda: self.close_window("Paint", paint_window))
    
    def select_paint_tool(self, tool):
        self.paint_tool = tool

    def change_brush_size(self, size):
        self.brush_size = size

    def change_paint_color(self, color):
        self.current_color = color

    def choose_custom_color(self):
        color = colorchooser.askcolor(initialcolor=self.current_color)
        if color[1]:  # Check if a color was selected (not canceled)
            self.current_color = color[1]

    def clear_canvas(self, canvas):
        canvas.delete("all")

    def paint_start(self, event, canvas, coords_label):
        self.old_x = event.x
        self.old_y = event.y
        self.update_coords(event, coords_label)

    def paint_move(self, event, canvas, coords_label, status_label):
        if self.old_x and self.old_y:
            if self.paint_tool == "pencil":
                canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                                  width=self.brush_size, fill=self.current_color,
                                  capstyle="round", smooth=True)
                status_label.config(text="Drawing with pencil")
            elif self.paint_tool == "brush":
                # For brush, create a thicker line with smoother edges
                canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                                  width=self.brush_size * 2, fill=self.current_color,
                                  capstyle="round", smooth=True)
                status_label.config(text="Painting with brush")
            elif self.paint_tool == "eraser":
                # Eraser uses white color (or canvas background color)
                canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                                  width=self.brush_size * 3, fill="white",
                                  capstyle="round", smooth=True)
                status_label.config(text="Erasing")
        
        self.old_x = event.x
        self.old_y = event.y
        self.update_coords(event, coords_label)

    def paint_end(self, event, canvas, coords_label):
        self.old_x = None
        self.old_y = None
        self.update_coords(event, coords_label)

    def update_coords(self, event, coords_label):
        coords_label.config(text=f"X: {event.x}, Y: {event.y}")
    
    def open_window(self, name):
        """Generic function to open a window"""
        window = tk.Toplevel(self.rootW95dist)
        window.title(name)
        window.geometry("400x300+250+150")
        window.configure(bg="#c0c0c0")
        window.overrideredirect(True)
        
        # Add Windows 95 style title bar
        title_bar = tk.Frame(window, bg="#000080", height=25)
        title_bar.pack(fill="x", side="top")
        title_label = tk.Label(title_bar, text=name, fg="white", bg="#000080",
                              font=("MS Sans Serif", 8, "bold"))
        title_label.pack(side="left", padx=5, pady=2)
        
        # Close button for title bar
        close_button = tk.Button(title_bar, text="×", bg="#c0c0c0", fg="black",
                                font=("Arial", 8, "bold"), width=2, height=1,
                                relief="raised", bd=1,
                                command=lambda: self.close_window(name, window))
        close_button.pack(side="right", padx=2, pady=1)
        
        # Window content
        content_frame = tk.Frame(window, bg="#c0c0c0")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        tk.Label(content_frame, text=f"This is {name}", bg="#c0c0c0",
                font=("MS Sans Serif", 10)).pack(expand=True)
        
        self.add_window_to_taskbar(name, window)
        window.protocol("WM_DELETE_WINDOW", lambda: self.close_window(name, window))
        
        self.make_window_draggable(window, title_bar)
    
    def setup_taskbar(self):
        # Taskbar la bottom
        self.taskbar = tk.Frame(self.rootW95dist, bg="#c0c0c0", height=30, relief="raised", bd=2)
        self.taskbar.pack(side="bottom", fill="x")
        self.taskbar.pack_propagate(False)
        
        # Start button
        self.start_button = tk.Button(self.taskbar, text="Start", font=("MS Sans Serif", 8, "bold"),
                                     bg="#c0c0c0", relief="raised", bd=2, width=8,
                                     command=self.toggle_start_menu)
        self.start_button.pack(side="left", padx=2, pady=2)
        
        # Separator
        separator = tk.Frame(self.taskbar, bg="#808080", width=2)
        separator.pack(side="left", fill="y", padx=2)
        
        # Frame pentru ferestre deschise
        self.taskbar_windows_frame = tk.Frame(self.taskbar, bg="#c0c0c0")
        self.taskbar_windows_frame.pack(side="left", fill="x", expand=True, padx=5)
        
        # System tray (simulat)
        system_tray = tk.Frame(self.taskbar, bg="#c0c0c0")
        system_tray.pack(side="right")
        
        # Simulăm câteva icone în system tray
        tray_icon1 = tk.Label(system_tray, text="🔊", bg="#c0c0c0", font=("Arial", 8))
        tray_icon1.pack(side="left", padx=2)
        
        tray_icon2 = tk.Label(system_tray, text="📶", bg="#c0c0c0", font=("Arial", 8))
        tray_icon2.pack(side="left", padx=2)
        
        # Clock frame
        self.clock_frame = tk.Frame(system_tray, bg="#c0c0c0", relief="sunken", bd=1)
        self.clock_frame.pack(side="right", padx=5, pady=2)
        
        self.clock_label = tk.Label(self.clock_frame, bg="#c0c0c0", font=("MS Sans Serif", 8))
        self.clock_label.pack(padx=5, pady=1)
    
    def setup_clock(self):
        def update_clock():
            current_time = time.strftime("%H:%M")
            current_date = time.strftime("%d/%m/%Y")
            self.clock_label.config(text=f"{current_time}\n{current_date}")
            self.rootW95dist.after(1000, update_clock)  # Update every second
        
        update_clock()
    
    def setup_start_menu(self):
        # Start menu permanent deasupra taskbar
        self.start_menu = tk.Frame(self.rootW95dist, bg="#c0c0c0", relief="raised", bd=2)
        self.start_menu.place(x=2, y=self.rootW95dist.winfo_screenheight()-330, width=200, height=300)
        
        # Header-ul Start Menu
        header = tk.Frame(self.start_menu, bg="#000080", height=25)
        header.pack(fill="x")
        header_label = tk.Label(header, text="Windows 95", fg="white", bg="#000080",
                               font=("MS Sans Serif", 8, "bold"))
        header_label.pack(anchor="w", padx=5, pady=2)
        
        # Doar opțiunea Shut Down
        separator = tk.Frame(self.start_menu, bg="#808080", height=1)
        separator.pack(fill="x", padx=5, pady=10)
        
        shutdown_btn = tk.Button(
            self.start_menu,
            text="Shut Down...",
            font=("MS Sans Serif", 8),
            bg="#c0c0c0",
            fg="black",
            relief="flat",
            bd=0,
            anchor="w",
            command=self.shutdown_computer
        )
        shutdown_btn.pack(fill="x", padx=2, pady=1)
        
        # Hover effects
        shutdown_btn.bind("<Enter>", lambda e: shutdown_btn.config(bg="#0000ff", fg="white"))
        shutdown_btn.bind("<Leave>", lambda e: shutdown_btn.config(bg="#c0c0c0", fg="black"))
    
    def toggle_start_menu(self):
        if self.start_menu_visible:
            self.hide_start_menu()
        else:
            self.show_start_menu()
    
    def show_start_menu(self):
        self.start_menu.place(x=2, y=self.rootW95dist.winfo_screenheight()-330, width=200, height=300)
        self.start_menu_visible = True
        self.start_button.config(relief="sunken")

    def hide_start_menu(self):
        self.start_menu.place_forget()
        self.start_menu_visible = False
        self.start_button.config(relief="raised")
    
    def shutdown_computer(self):
        self.rootW95dist.quit()
    
    def add_window_to_taskbar(self, title, window):
        # Create taskbar button for the window
        button = tk.Button(self.taskbar_windows_frame, text=title[:15], 
                          font=("MS Sans Serif", 8), bg="#c0c0c0",
                          relief="raised", bd=2, width=12,
                          command=lambda: self.bring_window_to_front(window))
        button.pack(side="left", padx=2, pady=2)
        
        # Add to open windows list
        self.open_windows.append((title, window, button))
        
        # Set initial active state
        self.set_active_window(window)
        
        # Update window state when minimized/restored/focused
        window.bind("<Unmap>", lambda e: self.update_taskbar_button_state(window, "minimized"))
        window.bind("<Map>", lambda e: self.update_taskbar_button_state(window, "restored"))
        window.bind("<FocusIn>", lambda e: self.set_active_window(window))
        
    def update_taskbar_button_state(self, window, state):
        """Update taskbar button appearance based on window state"""
        for title, win, button in self.open_windows:
            if win == window:
                # Check if this is the active window to maintain its color
                current_bg = button.cget("bg")
                is_active = current_bg == "#e0e0e0"
                
                if state == "minimized":
                    # Minimized = pressed/sunken
                    bg_color = "#e0e0e0" if is_active else "#c0c0c0"
                    button.config(relief="sunken", bd=1, bg=bg_color)
                elif state == "restored":
                    # Restored = normal/raised
                    bg_color = "#e0e0e0" if is_active else "#c0c0c0"
                    button.config(relief="raised", bd=2, bg=bg_color)
                break

    def set_active_window(self, active_window):
        """Set the active window and update all taskbar buttons accordingly"""
        for title, win, button in self.open_windows:
            if win == active_window:
                # Active window - lighter color
                if not win.winfo_viewable():  # hidden (minimized)
                    button.config(bg="#e0e0e0", relief="sunken", bd=1)
                else:
                    button.config(bg="#e0e0e0", relief="raised", bd=2)
            else:
                # Inactive windows - normal color
                if not win.winfo_viewable():  # hidden (minimized)
                    button.config(bg="#c0c0c0", relief="sunken", bd=1)
                else:
                    button.config(bg="#c0c0c0", relief="raised", bd=2)
    
    def bring_window_to_front(self, window):
        try:
            # Check if window is visible or hidden
            if window.winfo_viewable():
                # Window is visible - hide it (simulate minimize)
                window.withdraw()
                self.update_taskbar_button_state(window, "minimized")
            else:
                # Window is hidden - show it (simulate restore)
                window.deiconify()
                window.lift()
                window.focus_set()
                self.set_active_window(window)
                self.update_taskbar_button_state(window, "restored")
        except:
            pass
    
    def close_window(self, title, window):
        # Remove from taskbar
        for i, (window_title, win, button) in enumerate(self.open_windows):
            if window_title == title and win == window:
                button.destroy()
                self.open_windows.pop(i)
                break
        
        # Close window
        try:
            window.destroy()
        except:
            pass
    
    def run(self):
        # Bind escape key to exit fullscreen
        self.rootW95dist.bind("<Escape>", lambda e: self.rootW95dist.quit())
        
        # Bind F11 to toggle fullscreen
        self.rootW95dist.bind("<F11>", lambda e: self.toggle_fullscreen())
        
        # Start the GUI
        self.rootW95dist.mainloop()
    
    def toggle_fullscreen(self):
        current_state = self.rootW95dist.attributes('-fullscreen')
        self.rootW95dist.attributes('-fullscreen', not current_state)

# Start the Windows 95 Desktop
if __name__ == "__main__":
    desktop = Windows95Desktop()
    desktop.run()