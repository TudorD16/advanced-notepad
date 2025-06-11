import tkinter as tk
from tkinter import messagebox, colorchooser, filedialog
import json
import math
import random

class Node:
    def __init__(self, x, y, text="New Node", color="#C0C0C0"):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.width = 120
        self.height = 40
        self.connections = []  # List of connected node IDs
        self.id = None
        
    def contains_point(self, x, y):
        return (self.x - self.width//2 <= x <= self.x + self.width//2 and
                self.y - self.height//2 <= y <= self.y + self.height//2)
    
    def get_connection_point(self, target_node):
        """Get the best connection point on the edge of this node towards target"""
        dx = target_node.x - self.x
        dy = target_node.y - self.y
        
        # Calculate intersection with rectangle
        if dx == 0:
            return (self.x, self.y + (self.height//2 if dy > 0 else -self.height//2))
        if dy == 0:
            return (self.x + (self.width//2 if dx > 0 else -self.width//2), self.y)
        
        # General case
        slope = dy / dx
        
        # Check intersection with vertical edges
        if dx > 0:
            x_edge = self.x + self.width//2
        else:
            x_edge = self.x - self.width//2
        y_at_edge = self.y + slope * (x_edge - self.x)
        
        if abs(y_at_edge - self.y) <= self.height//2:
            return (x_edge, y_at_edge)
        
        # Check intersection with horizontal edges
        if dy > 0:
            y_edge = self.y + self.height//2
        else:
            y_edge = self.y - self.height//2
        x_at_edge = self.x + (y_edge - self.y) / slope
        
        return (x_at_edge, y_edge)

class Win95Button(tk.Frame):
    def __init__(self, parent, text, command=None, width=10, **kwargs):
        super().__init__(parent, **kwargs)
        self.command = command
        self.pressed = False
        
        # Windows 95 button colors
        self.bg_normal = "#C0C0C0"
        self.bg_pressed = "#C0C0C0"
        
        self.configure(bg=self.bg_normal, relief="raised", bd=2)
        
        self.label = tk.Label(self, text=text, bg=self.bg_normal, 
                             font=("MS Sans Serif", 8), width=width)
        self.label.pack(padx=2, pady=2)
        
        # Bind events
        self.bind("<Button-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.label.bind("<Button-1>", self.on_press)
        self.label.bind("<ButtonRelease-1>", self.on_release)
        
    def on_press(self, event):
        self.configure(relief="sunken", bd=2)
        self.pressed = True
        
    def on_release(self, event):
        self.configure(relief="raised", bd=2)
        if self.pressed and self.command:
            self.command()
        self.pressed = False

class MindMapTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Mind Mapper - Windows 95 Edition")
        self.root.geometry("1024x768")
        
        # Windows 95 color scheme
        self.bg_color = "#C0C0C0"
        self.canvas_color = "#FFFFFF"
        self.text_color = "#000000"
        
        # Configure root window
        self.root.configure(bg=self.bg_color)
        
        # Set Windows 95 style icon (if available)
        try:
            self.root.iconbitmap("brain.ico")  # Optional - add your own icon
        except:
            pass
        
        self.nodes = {}
        self.selected_node = None
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.connecting_mode = False
        self.connect_start_node = None
        self.node_counter = 0
        
        self.setup_ui()
        self.setup_bindings()
        
    def setup_ui(self):
        # Menu bar (Windows 95 style)
        menubar = tk.Menu(self.root, bg=self.bg_color, font=("MS Sans Serif", 8))
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color, font=("MS Sans Serif", 8))
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.clear_all, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.load_mindmap, accelerator="Ctrl+O")
        file_menu.add_command(label="Save...", command=self.save_mindmap, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Alt+F4")
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color, font=("MS Sans Serif", 8))
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Add Node", command=self.add_node_dialog)
        edit_menu.add_command(label="Delete Node", command=self.delete_selected_node)
        edit_menu.add_command(label="Edit Node", command=self.edit_selected_node)
        edit_menu.add_separator()
        edit_menu.add_command(label="Connect Nodes", command=self.toggle_connect_mode)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color, font=("MS Sans Serif", 8))
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Auto Layout", command=self.auto_layout)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color, font=("MS Sans Serif", 8))
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About...", command=self.show_about)
        
        # Main container with Windows 95 styling
        main_frame = tk.Frame(self.root, bg=self.bg_color, relief="sunken", bd=1)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Toolbar with Windows 95 styling
        toolbar_frame = tk.Frame(main_frame, bg=self.bg_color, relief="raised", bd=1)
        toolbar_frame.pack(fill=tk.X, padx=2, pady=2)
        
        # Create Windows 95 style buttons
        btn_frame = tk.Frame(toolbar_frame, bg=self.bg_color)
        btn_frame.pack(side=tk.LEFT, padx=5, pady=3)
        
        Win95Button(btn_frame, "Add Node", self.add_node_dialog, width=8).pack(side=tk.LEFT, padx=1)
        Win95Button(btn_frame, "Delete", self.delete_selected_node, width=8).pack(side=tk.LEFT, padx=1)
        Win95Button(btn_frame, "Connect", self.toggle_connect_mode, width=8).pack(side=tk.LEFT, padx=1)
        Win95Button(btn_frame, "Edit", self.edit_selected_node, width=8).pack(side=tk.LEFT, padx=1)
        Win95Button(btn_frame, "Color", self.change_node_color, width=8).pack(side=tk.LEFT, padx=1)
        
        # Separator
        sep_frame = tk.Frame(toolbar_frame, bg="#808080", width=2, height=25)
        sep_frame.pack(side=tk.LEFT, padx=5, pady=3)
        
        btn_frame2 = tk.Frame(toolbar_frame, bg=self.bg_color)
        btn_frame2.pack(side=tk.LEFT, padx=5, pady=3)
        
        Win95Button(btn_frame2, "Save", self.save_mindmap, width=8).pack(side=tk.LEFT, padx=1)
        Win95Button(btn_frame2, "Load", self.load_mindmap, width=8).pack(side=tk.LEFT, padx=1)
        Win95Button(btn_frame2, "Clear", self.clear_all, width=8).pack(side=tk.LEFT, padx=1)
        Win95Button(btn_frame2, "Layout", self.auto_layout, width=8).pack(side=tk.LEFT, padx=1)
        
        # Status bar
        status_frame = tk.Frame(main_frame, bg=self.bg_color, relief="sunken", bd=1)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=2, pady=2)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Double-click to add node, click to select, drag to move")
        self.status_label = tk.Label(status_frame, textvariable=self.status_var, 
                                   bg=self.bg_color, font=("MS Sans Serif", 8), 
                                   anchor="w", relief="sunken", bd=1)
        self.status_label.pack(fill=tk.X, padx=2, pady=2)
        
        # Canvas area with Windows 95 styling
        canvas_container = tk.Frame(main_frame, bg=self.bg_color, relief="sunken", bd=2)
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Canvas with scrollbars
        self.canvas = tk.Canvas(canvas_container, bg=self.canvas_color, 
                               scrollregion=(0, 0, 2000, 2000),
                               relief="sunken", bd=1)
        
        # Windows 95 style scrollbars
        v_scrollbar = tk.Scrollbar(canvas_container, orient=tk.VERTICAL, 
                                 command=self.canvas.yview, bg=self.bg_color,
                                 relief="raised", bd=1)
        h_scrollbar = tk.Scrollbar(canvas_container, orient=tk.HORIZONTAL, 
                                 command=self.canvas.xview, bg=self.bg_color,
                                 relief="raised", bd=1)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add some initial instructions
        self.canvas.create_text(400, 100, text="Mind Mapper - Windows 95 Edition", 
                              font=("MS Sans Serif", 16, "bold"), fill="#000080")
        self.canvas.create_text(400, 130, text="Double-click to create your first node!", 
                              font=("MS Sans Serif", 10), fill="#800000")
        
    def setup_bindings(self):
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.on_right_click)
        
        # Keyboard shortcuts
        self.root.bind("<Control-n>", lambda e: self.clear_all())
        self.root.bind("<Control-o>", lambda e: self.load_mindmap())
        self.root.bind("<Control-s>", lambda e: self.save_mindmap())
        
    def show_about(self):
        messagebox.showinfo("About Mind Mapper", 
                          "Mind Mapper - Windows 95 Edition\n\n"
                          "Create mind maps with that classic 90s feel!\n\n"
                          "Features:\n"
                          "• Drag & drop nodes\n"
                          "• Connect ideas with arrows\n"
                          "• Save and load your work\n"
                          "• Authentic Windows 95 interface\n\n"
                          "© 1995 Nostalgia Software Inc.")
        
    def add_node_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Node")
        dialog.geometry("320x160")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Windows 95 dialog styling
        main_frame = tk.Frame(dialog, bg=self.bg_color, relief="raised", bd=2)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Label(main_frame, text="Node Text:", bg=self.bg_color, 
                font=("MS Sans Serif", 8)).pack(pady=(10, 5))
        
        text_entry = tk.Entry(main_frame, width=30, font=("MS Sans Serif", 8),
                            relief="sunken", bd=2)
        text_entry.pack(pady=5)
        text_entry.focus()
        
        # Button frame
        btn_frame = tk.Frame(main_frame, bg=self.bg_color)
        btn_frame.pack(pady=15)
        
        def create_node():
            text = text_entry.get().strip()
            if text:
                x = random.randint(100, 500)
                y = random.randint(100, 400)
                self.create_node(x, y, text)
                dialog.destroy()
            else:
                messagebox.showwarning("Warning", "Please enter some text for the node!")
        
        def cancel():
            dialog.destroy()
        
        Win95Button(btn_frame, "OK", create_node, width=10).pack(side=tk.LEFT, padx=5)
        Win95Button(btn_frame, "Cancel", cancel, width=10).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter and Escape
        text_entry.bind("<Return>", lambda e: create_node())
        dialog.bind("<Escape>", lambda e: cancel())
        
    def create_node(self, x, y, text="New Node", color="#E0E0E0"):
        node = Node(x, y, text, color)
        node_id = f"node_{self.node_counter}"
        node.id = node_id
        self.node_counter += 1
        self.nodes[node_id] = node
        self.draw_node(node)
        
        # Clear instruction text if this is the first node
        if len(self.nodes) == 1:
            self.canvas.delete("instruction")
            
        return node_id
        
    def draw_node(self, node):
        # Clear previous drawings for this node
        self.canvas.delete(f"node_{node.id}")
        
        # Draw Windows 95 style node
        x1 = node.x - node.width // 2
        y1 = node.y - node.height // 2
        x2 = node.x + node.width // 2
        y2 = node.y + node.height // 2
        
        # Main rectangle with Windows 95 3D effect
        if self.selected_node == node.id:
            # Selected node - sunken effect
            self.canvas.create_rectangle(x1, y1, x2, y2, 
                                       fill=node.color, outline="#808080",
                                       width=2, tags=f"node_{node.id}")
            # Inner highlight
            self.canvas.create_line(x1+1, y1+1, x2-1, y1+1, fill="#FFFFFF", width=1, tags=f"node_{node.id}")
            self.canvas.create_line(x1+1, y1+1, x1+1, y2-1, fill="#FFFFFF", width=1, tags=f"node_{node.id}")
            # Inner shadow
            self.canvas.create_line(x2-1, y1+1, x2-1, y2-1, fill="#808080", width=1, tags=f"node_{node.id}")
            self.canvas.create_line(x1+1, y2-1, x2-1, y2-1, fill="#808080", width=1, tags=f"node_{node.id}")
        else:
            # Normal node - raised effect
            self.canvas.create_rectangle(x1, y1, x2, y2, 
                                       fill=node.color, outline="#000000",
                                       width=1, tags=f"node_{node.id}")
            # Highlight
            self.canvas.create_line(x1, y1, x2-1, y1, fill="#FFFFFF", width=1, tags=f"node_{node.id}")
            self.canvas.create_line(x1, y1, x1, y2-1, fill="#FFFFFF", width=1, tags=f"node_{node.id}")
            # Shadow
            self.canvas.create_line(x2, y1, x2, y2, fill="#808080", width=1, tags=f"node_{node.id}")
            self.canvas.create_line(x1, y2, x2, y2, fill="#808080", width=1, tags=f"node_{node.id}")
        
        # Draw text
        self.canvas.create_text(node.x, node.y, 
                              text=node.text, 
                              font=("MS Sans Serif", 9, "bold"),
                              fill="#000000",
                              tags=f"node_{node.id}")
        
    def draw_connections(self):
        # Clear all connection lines
        self.canvas.delete("connection")
        
        # Draw all connections
        for node_id, node in self.nodes.items():
            for connected_id in node.connections:
                if connected_id in self.nodes:
                    target_node = self.nodes[connected_id]
                    
                    # Get connection points on edges
                    start_point = node.get_connection_point(target_node)
                    end_point = target_node.get_connection_point(node)
                    
                    # Draw arrow with Windows 95 style
                    self.canvas.create_line(start_point[0], start_point[1],
                                          end_point[0], end_point[1],
                                          width=2, fill="#000080",
                                          arrow=tk.LAST, arrowshape=(10, 12, 3),
                                          tags="connection")
        
        # Ensure nodes are drawn on top
        for node in self.nodes.values():
            self.draw_node(node)
    
    def on_double_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        # Check if clicked on existing node
        clicked_node = self.get_node_at_position(x, y)
        if not clicked_node:
            # Create new node
            text = f"Node {len(self.nodes) + 1}"
            self.create_node(x, y, text)
            self.draw_connections()
            
    def on_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        clicked_node = self.get_node_at_position(x, y)
        
        if self.connecting_mode:
            if clicked_node:
                if self.connect_start_node is None:
                    self.connect_start_node = clicked_node
                    self.status_var.set(f"Now click on the second node to connect...")
                else:
                    if clicked_node != self.connect_start_node:
                        self.connect_nodes(self.connect_start_node, clicked_node)
                    self.connect_start_node = None
                    self.connecting_mode = False
                    self.status_var.set("Ready")
            return
        
        if clicked_node:
            self.selected_node = clicked_node
            self.dragging = True
            self.drag_start_x = x
            self.drag_start_y = y
            self.draw_connections()
            self.status_var.set(f"Selected: {self.nodes[clicked_node].text}")
        else:
            self.selected_node = None
            self.draw_connections()
            self.status_var.set("Ready")
            
    def on_drag(self, event):
        if self.dragging and self.selected_node:
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            
            dx = x - self.drag_start_x
            dy = y - self.drag_start_y
            
            node = self.nodes[self.selected_node]
            node.x += dx
            node.y += dy
            
            self.drag_start_x = x
            self.drag_start_y = y
            
            self.draw_connections()
            
    def on_release(self, event):
        self.dragging = False
        
    def on_right_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        clicked_node = self.get_node_at_position(x, y)
        if clicked_node:
            self.selected_node = clicked_node
            self.show_context_menu(event, clicked_node)
            
    def show_context_menu(self, event, node_id):
        context_menu = tk.Menu(self.root, tearoff=0, bg=self.bg_color, 
                             font=("MS Sans Serif", 8))
        context_menu.add_command(label="Edit Text...", command=lambda: self.edit_node(node_id))
        context_menu.add_command(label="Change Color...", command=lambda: self.change_color(node_id))
        context_menu.add_separator()
        context_menu.add_command(label="Delete Node", command=lambda: self.delete_node(node_id))
        context_menu.add_command(label="Disconnect All", command=lambda: self.disconnect_all(node_id))
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
            
    def get_node_at_position(self, x, y):
        for node_id, node in self.nodes.items():
            if node.contains_point(x, y):
                return node_id
        return None
        
    def toggle_connect_mode(self):
        self.connecting_mode = not self.connecting_mode
        if self.connecting_mode:
            self.status_var.set("Connection mode: Click on the first node...")
            self.connect_start_node = None
        else:
            self.status_var.set("Ready")
            
    def connect_nodes(self, node1_id, node2_id):
        if node1_id in self.nodes and node2_id in self.nodes:
            node1 = self.nodes[node1_id]
            node2 = self.nodes[node2_id]
            
            if node2_id not in node1.connections:
                node1.connections.append(node2_id)
            if node1_id not in node2.connections:
                node2.connections.append(node1_id)
                
            self.draw_connections()
            self.status_var.set(f"Connected '{node1.text}' to '{node2.text}'")
            
    def edit_selected_node(self):
        if self.selected_node:
            self.edit_node(self.selected_node)
        else:
            messagebox.showinfo("Information", "Please select a node first!")
            
    def edit_node(self, node_id):
        if node_id not in self.nodes:
            return
            
        node = self.nodes[node_id]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Node")
        dialog.geometry("320x160")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        main_frame = tk.Frame(dialog, bg=self.bg_color, relief="raised", bd=2)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Label(main_frame, text="Node Text:", bg=self.bg_color, 
                font=("MS Sans Serif", 8)).pack(pady=(10, 5))
        
        text_entry = tk.Entry(main_frame, width=30, font=("MS Sans Serif", 8),
                            relief="sunken", bd=2)
        text_entry.insert(0, node.text)
        text_entry.pack(pady=5)
        text_entry.focus()
        text_entry.select_range(0, tk.END)
        
        btn_frame = tk.Frame(main_frame, bg=self.bg_color)
        btn_frame.pack(pady=15)
        
        def save_changes():
            new_text = text_entry.get().strip()
            if new_text:
                node.text = new_text
                self.draw_connections()
                dialog.destroy()
                self.status_var.set(f"Updated node text")
            else:
                messagebox.showwarning("Warning", "Please enter some text!")
                
        def cancel():
            dialog.destroy()
                
        Win95Button(btn_frame, "OK", save_changes, width=10).pack(side=tk.LEFT, padx=5)
        Win95Button(btn_frame, "Cancel", cancel, width=10).pack(side=tk.LEFT, padx=5)
        
        text_entry.bind("<Return>", lambda e: save_changes())
        dialog.bind("<Escape>", lambda e: cancel())
        
    def change_node_color(self):
        if self.selected_node:
            self.change_color(self.selected_node)
        else:
            messagebox.showinfo("Information", "Please select a node first!")
            
    def change_color(self, node_id):
        if node_id not in self.nodes:
            return
            
        # Windows 95 style color chooser
        colors = [
            "#FFFFFF", "#C0C0C0", "#808080", "#000000",
            "#FF0000", "#800000", "#FFFF00", "#808000",
            "#00FF00", "#008000", "#00FFFF", "#008080",
            "#0000FF", "#000080", "#FF00FF", "#800080"
        ]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Choose Color")
        dialog.geometry("240x200")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        main_frame = tk.Frame(dialog, bg=self.bg_color, relief="raised", bd=2)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Label(main_frame, text="Select a color:", bg=self.bg_color, 
                font=("MS Sans Serif", 8)).pack(pady=10)
        
        color_frame = tk.Frame(main_frame, bg=self.bg_color)
        color_frame.pack(pady=10)
        
        selected_color = [self.nodes[node_id].color]
        
        def select_color(color):
            selected_color[0] = color
            self.nodes[node_id].color = color
            self.draw_connections()
            dialog.destroy()
            self.status_var.set(f"Changed node color")
        
        # Create color buttons in a 4x4 grid
        for i, color in enumerate(colors):
            row = i // 4
            col = i % 4
            
            color_btn = tk.Button(color_frame, bg=color, width=3, height=1,
                                relief="raised", bd=2,
                                command=lambda c=color: select_color(c))
            color_btn.grid(row=row, column=col, padx=2, pady=2)
        
        # Custom color button
        btn_frame = tk.Frame(main_frame, bg=self.bg_color)
        btn_frame.pack(pady=10)
        
        def custom_color():
            color = colorchooser.askcolor(title="Choose custom color")
            if color[1]:
                select_color(color[1])
        
        Win95Button(btn_frame, "Custom...", custom_color, width=10).pack(side=tk.LEFT, padx=5)
        Win95Button(btn_frame, "Cancel", dialog.destroy, width=10).pack(side=tk.LEFT, padx=5)
        
    def delete_selected_node(self):
        if self.selected_node:
            result = messagebox.askyesno("Confirm Delete", 
                                       f"Delete node '{self.nodes[self.selected_node].text}'?")
            if result:
                self.delete_node(self.selected_node)
        else:
            messagebox.showinfo("Information", "Please select a node first!")
            
    def delete_node(self, node_id):
        if node_id not in self.nodes:
            return
            
        # Remove connections to this node
        for other_node in self.nodes.values():
            if node_id in other_node.connections:
                other_node.connections.remove(node_id)
                
        # Remove the node
        del self.nodes[node_id]
        self.selected_node = None
        
        # Clear and redraw
        self.canvas.delete("all")
        self.draw_connections()
        self.status_var.set(f"Deleted node")
        
    def disconnect_all(self, node_id):
        if node_id not in self.nodes:
            return
            
        node = self.nodes[node_id]
        
        # Remove this node from other nodes' connections
        for other_node in self.nodes.values():
            if node_id in other_node.connections:
                other_node.connections.remove(node_id)
                
        # Clear this node's connections
        node.connections.clear()
        
        self.draw_connections()
        self.status_var.set(f"Disconnected all connections from '{node.text}'")
        
    def auto_layout(self):
        if len(self.nodes) < 2:
            messagebox.showinfo("Information", "Need at least 2 nodes for auto layout!")
            return
            
        # Simple circular layout
        center_x, center_y = 400, 300
        radius = min(200, max(100, len(self.nodes) * 20))
        
        nodes_list = list(self.nodes.values())
        angle_step = 2 * math.pi / len(nodes_list)
        
        for i, node in enumerate(nodes_list):
            angle = i * angle_step
            node.x = center_x + radius * math.cos(angle)
            node.y = center_y + radius * math.sin(angle)
            
        self.draw_connections()
        self.status_var.set("Applied auto layout")
        
    def clear_all(self):
        if self.nodes:
            result = messagebox.askyesno("Confirm Clear", 
                                       "This will delete all nodes and connections. Continue?")
            if not result:
                return
                
        self.nodes.clear()
        self.selected_node = None
        self.connecting_mode = False
        self.connect_start_node = None
        self.node_counter = 0
        
        self.canvas.delete("all")
        
        # Add back instruction text
        self.canvas.create_text(400, 100, text="Mind Mapper - Windows 95 Edition", 
                              font=("MS Sans Serif", 16, "bold"), fill="#000080",
                              tags="instruction")
        self.canvas.create_text(400, 130, text="Double-click to create your first node!", 
                              font=("MS Sans Serif", 10), fill="#800000",
                              tags="instruction")
        
        self.status_var.set("Ready - All nodes cleared")
        
    def save_mindmap(self):
        if not self.nodes:
            messagebox.showinfo("Information", "No nodes to save!")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Save Mind Map",
            defaultextension=".json",
            filetypes=[("Mind Map files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                # Prepare data for saving
                save_data = {
                    "nodes": {},
                    "node_counter": self.node_counter
                }
                
                for node_id, node in self.nodes.items():
                    save_data["nodes"][node_id] = {
                        "x": node.x,
                        "y": node.y,
                        "text": node.text,
                        "color": node.color,
                        "connections": node.connections
                    }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, indent=2, ensure_ascii=False)
                
                self.status_var.set(f"Saved to {filename}")
                messagebox.showinfo("Success", f"Mind map saved successfully!\n\n{filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
                
    def load_mindmap(self):
        filename = filedialog.askopenfilename(
            title="Load Mind Map",
            filetypes=[("Mind Map files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    save_data = json.load(f)
                
                # Clear existing data
                self.nodes.clear()
                self.selected_node = None
                self.connecting_mode = False
                self.connect_start_node = None
                self.canvas.delete("all")
                
                # Load nodes
                if "nodes" in save_data:
                    for node_id, node_data in save_data["nodes"].items():
                        node = Node(
                            node_data["x"], 
                            node_data["y"], 
                            node_data["text"], 
                            node_data["color"]
                        )
                        node.id = node_id
                        node.connections = node_data.get("connections", [])
                        self.nodes[node_id] = node
                
                # Restore counter
                if "node_counter" in save_data:
                    self.node_counter = save_data["node_counter"]
                
                # Redraw everything
                self.draw_connections()
                
                self.status_var.set(f"Loaded from {filename}")
                messagebox.showinfo("Success", f"Mind map loaded successfully!\n\n{filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")

def main():
    root = tk.Tk()
    
    # Set Windows 95 theme
    try:
        root.tk.call("source", "azure.tcl")
        root.tk.call("set_theme", "light")
    except:
        pass  # Theme not available, use default
    
    app = MindMapTool(root)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()