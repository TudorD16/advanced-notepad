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
    def __init__(self, parent, text, command=None, width=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.command = command
        self.pressed = False
        
        # Configure frame
        self.configure(relief="raised", bd=2, bg="#C0C0C0")
        
        # Create label
        self.label = tk.Label(self, text=text, font=("MS Sans Serif", 8),
                             bg="#C0C0C0", fg="black")
        if width:
            self.label.configure(width=width)
        self.label.pack(padx=4, pady=2)
        
        # Bind events
        self.bind("<Button-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.label.bind("<Button-1>", self.on_press)
        self.label.bind("<ButtonRelease-1>", self.on_release)
        
    def on_press(self, event):
        self.configure(relief="sunken")
        self.pressed = True
        
    def on_release(self, event):
        if self.pressed:
            self.configure(relief="raised")
            self.pressed = False
            if self.command:
                self.command()

class MindMapTool:
    def __init__(self, root_MIND):
        self.root_MIND = root_MIND
        self.root_MIND.title("Mind Mapping Tool - Windows 95 Style")
        self.root_MIND.geometry("1200x800")
        self.root_MIND.configure(bg="#C0C0C0")
        
        # Windows 95 color scheme
        self.colors = {
            'bg': '#C0C0C0',
            'button_face': '#C0C0C0',
            'button_highlight': '#FFFFFF',
            'button_shadow': '#808080',
            'button_dark_shadow': '#404040',
            'window_frame': '#404040',
            'active_title': '#000080',
            'inactive_title': '#808080',
            'text': '#000000'
        }
        
        self.nodes = {}
        self.selected_node = None
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.connecting_mode = False
        self.connect_start_node = None
        self.node_counter = 0
        
        # Display mode: True for 3D, False for 2D
        self.display_3d = True
        
        self.setup_ui()
        self.setup_bindings()
        
    def setup_ui(self):
        # Configure root_MIND window style
        self.root_MIND.configure(bg=self.colors['bg'])
        
        # Create title bar frame (simulated)
        title_frame = tk.Frame(self.root_MIND, bg=self.colors['active_title'], height=25)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="Mind Mapping Tool", 
                              font=("MS Sans Serif", 8, "bold"),
                              bg=self.colors['active_title'], fg="white")
        title_label.pack(side=tk.LEFT, padx=5, pady=3)
        
        # Create main frame with border
        main_frame = tk.Frame(self.root_MIND, bg=self.colors['bg'], relief="raised", bd=2)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Menu bar (simulated)
        menubar_frame = tk.Frame(main_frame, bg=self.colors['bg'], relief="raised", bd=1)
        menubar_frame.pack(fill=tk.X)
        
        # File menu
        file_menu = tk.Label(menubar_frame, text="File", font=("MS Sans Serif", 8),
                           bg=self.colors['bg'], fg=self.colors['text'], padx=8, pady=2)
        file_menu.pack(side=tk.LEFT)
        
        edit_menu = tk.Label(menubar_frame, text="Edit", font=("MS Sans Serif", 8),
                           bg=self.colors['bg'], fg=self.colors['text'], padx=8, pady=2)
        edit_menu.pack(side=tk.LEFT)
        
        view_menu = tk.Label(menubar_frame, text="View", font=("MS Sans Serif", 8),
                           bg=self.colors['bg'], fg=self.colors['text'], padx=8, pady=2)
        view_menu.pack(side=tk.LEFT)
        
        # Toolbar with Win95 style buttons
        toolbar = tk.Frame(main_frame, bg=self.colors['bg'], relief="raised", bd=1)
        toolbar.pack(fill=tk.X, pady=2)
        
        # Left toolbar
        left_toolbar = tk.Frame(toolbar, bg=self.colors['bg'])
        left_toolbar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)
        
        # Create Win95 style buttons
        Win95Button(left_toolbar, "Add Node", self.add_node_dialog, width=10).pack(side=tk.LEFT, padx=1)
        Win95Button(left_toolbar, "Delete", self.delete_selected_node, width=8).pack(side=tk.LEFT, padx=1)
        Win95Button(left_toolbar, "Connect", self.toggle_connect_mode, width=8).pack(side=tk.LEFT, padx=1)
        Win95Button(left_toolbar, "Edit", self.edit_selected_node, width=6).pack(side=tk.LEFT, padx=1)
        Win95Button(left_toolbar, "Color", self.change_node_color, width=6).pack(side=tk.LEFT, padx=1)
        
        # Separator
        sep1 = tk.Frame(left_toolbar, width=2, bg=self.colors['button_shadow'], relief="sunken", bd=1)
        sep1.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        Win95Button(left_toolbar, "Save", self.save_mindmap, width=6).pack(side=tk.LEFT, padx=1)
        Win95Button(left_toolbar, "Load", self.load_mindmap, width=6).pack(side=tk.LEFT, padx=1)
        Win95Button(left_toolbar, "Clear", self.clear_all, width=6).pack(side=tk.LEFT, padx=1)
        
        # Separator
        sep2 = tk.Frame(left_toolbar, width=2, bg=self.colors['button_shadow'], relief="sunken", bd=1)
        sep2.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        Win95Button(left_toolbar, "Auto Layout", self.auto_layout, width=10).pack(side=tk.LEFT, padx=1)
        
        # Separator
        sep3 = tk.Frame(left_toolbar, width=2, bg=self.colors['button_shadow'], relief="sunken", bd=1)
        sep3.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # 2D/3D Toggle button
        self.display_button = Win95Button(left_toolbar, "3D View", self.toggle_display_mode, width=8)
        self.display_button.pack(side=tk.LEFT, padx=1)
        
        # Status bar frame
        status_frame = tk.Frame(main_frame, bg=self.colors['bg'], relief="sunken", bd=2)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Double-click to add node, click to select, drag to move")
        self.status_label = tk.Label(status_frame, textvariable=self.status_var,
                                   font=("MS Sans Serif", 8), bg=self.colors['bg'],
                                   fg=self.colors['text'], anchor="w")
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2, fill=tk.X, expand=True)
        
        # Canvas frame with Win95 style borders
        canvas_frame = tk.Frame(main_frame, bg=self.colors['bg'], relief="sunken", bd=2)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create canvas with Win95 colors
        self.canvas = tk.Canvas(canvas_frame, bg="#FFFFFF", scrollregion=(0, 0, 2000, 2000),
                               highlightthickness=0, relief="flat")
        
        # Scrollbars with Win95 style
        v_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview,
                                  bg=self.colors['bg'], troughcolor=self.colors['bg'],
                                  relief="raised", bd=1)
        h_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview,
                                  bg=self.colors['bg'], troughcolor=self.colors['bg'],
                                  relief="raised", bd=1)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and canvas
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
    def toggle_display_mode(self):
        """Toggle between 2D and 3D display modes"""
        self.display_3d = not self.display_3d
        
        # Update button text
        if self.display_3d:
            self.display_button.label.configure(text="3D View")
            self.status_var.set("Switched to 3D display mode")
        else:
            self.display_button.label.configure(text="2D View")
            self.status_var.set("Switched to 2D display mode")
        
        # Redraw all nodes with new display mode
        self.draw_connections()
        
    def draw_node(self, node):
        """Draw node using current display mode"""
        if self.display_3d:
            self.draw_node_3d(node)
        else:
            self.draw_node_2d(node)
    
    def create_win95_dialog(self, title, width=300, height=150):
        """Create a Windows 95 style dialog"""
        dialog = tk.Toplevel(self.root_MIND)
        dialog.title(title)
        dialog.geometry(f"{width}x{height}")
        dialog.transient(self.root_MIND)
        dialog.grab_set()
        dialog.configure(bg=self.colors['bg'])
        dialog.resizable(False, False)
        
        # Title bar simulation
        title_frame = tk.Frame(dialog, bg=self.colors['active_title'], height=20)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text=title, font=("MS Sans Serif", 8, "bold"),
                              bg=self.colors['active_title'], fg="white")
        title_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Main content frame
        content_frame = tk.Frame(dialog, bg=self.colors['bg'], relief="raised", bd=2)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        return dialog, content_frame
        
    def setup_bindings(self):
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.on_right_click)  # Right-click menu
        
    def add_node_dialog(self):
        dialog, content_frame = self.create_win95_dialog("Add Node", 320, 180)
        
        # Label
        label = tk.Label(content_frame, text="Node Text:", font=("MS Sans Serif", 8),
                        bg=self.colors['bg'], fg=self.colors['text'])
        label.pack(pady=(15, 5))
        
        # Entry with Win95 style
        entry_frame = tk.Frame(content_frame, relief="sunken", bd=2, bg="white")
        entry_frame.pack(pady=5, padx=20, fill=tk.X)
        
        text_entry = tk.Entry(entry_frame, font=("MS Sans Serif", 8), bg="white",
                             fg="black", relief="flat", bd=0)
        text_entry.pack(padx=2, pady=2, fill=tk.X)
        text_entry.focus()
        
        # Button frame
        button_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        button_frame.pack(pady=15)
        
        def create_node():
            text = text_entry.get().strip()
            if text:
                x = random.randint(100, 500)
                y = random.randint(100, 400)
                self.create_node(x, y, text)
                dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        Win95Button(button_frame, "OK", create_node, width=8).pack(side=tk.LEFT, padx=5)
        Win95Button(button_frame, "Cancel", cancel, width=8).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        text_entry.bind("<Return>", lambda e: create_node())
        
    def create_node(self, x, y, text="New Node", color="#87CEEB"):
        node = Node(x, y, text, color)
        node_id = f"node_{self.node_counter}"
        node.id = node_id
        self.node_counter += 1
        self.nodes[node_id] = node
        self.draw_node(node)
        return node_id
    
    def draw_node_3d(self, node):
        # Clear previous drawings for this node
        self.canvas.delete(f"node_{node.id}")
        
        # Calculate coordinates
        x1 = node.x - node.width // 2
        y1 = node.y - node.height // 2
        x2 = node.x + node.width // 2
        y2 = node.y + node.height // 2
        
        # Highlight selected node
        outline_color = "#FF0000" if self.selected_node == node.id else "#000000"
        outline_width = 3 if self.selected_node == node.id else 1
        
        # Draw Win95 style button (raised/sunken effect)
        if self.selected_node == node.id:
            # Selected node - sunken appearance
            # Dark shadow (bottom-right)
            self.canvas.create_line(x2-1, y1+1, x2-1, y2-1, x1+1, y2-1,
                                  fill=self.colors['button_dark_shadow'], width=1,
                                  tags=f"node_{node.id}")
            # Shadow (inner bottom-right)
            self.canvas.create_line(x2-2, y1+2, x2-2, y2-2, x1+2, y2-2,
                                  fill=self.colors['button_shadow'], width=1,
                                  tags=f"node_{node.id}")
            # Highlight (top-left)
            self.canvas.create_line(x1+1, y2-2, x1+1, y1+1, x2-2, y1+1,
                                  fill=self.colors['button_highlight'], width=1,
                                  tags=f"node_{node.id}")
        else:
            # Normal node - raised appearance
            # Highlight (top-left)
            self.canvas.create_line(x1, y2-1, x1, y1, x2-1, y1,
                                  fill=self.colors['button_highlight'], width=1,
                                  tags=f"node_{node.id}")
            # Shadow (bottom-right)
            self.canvas.create_line(x2-1, y1+1, x2-1, y2-1, x1+1, y2-1,
                                  fill=self.colors['button_shadow'], width=1,
                                  tags=f"node_{node.id}")
            # Dark shadow (outer bottom-right)
            self.canvas.create_line(x2, y1, x2, y2, x1, y2,
                                  fill=self.colors['button_dark_shadow'], width=1,
                                  tags=f"node_{node.id}")
        
        # Fill the button face
        self.canvas.create_rectangle(x1+1, y1+1, x2-1, y2-1,
                                   fill=node.color, outline="",
                                   tags=f"node_{node.id}")
        
        # Add selection border if selected
        if self.selected_node == node.id:
            self.canvas.create_rectangle(x1, y1, x2, y2,
                                       fill="", outline=outline_color, width=outline_width,
                                       tags=f"node_{node.id}")
        
        # Draw text
        self.canvas.create_text(node.x, node.y,
                              text=node.text,
                              font=("MS Sans Serif", 8, "bold"),
                              fill="black",
                              tags=f"node_{node.id}")

    def draw_node_2d(self, node):
        # Clear previous drawings for this node
        self.canvas.delete(f"node_{node.id}")
        
        # Calculate coordinates
        x1 = node.x - node.width // 2
        y1 = node.y - node.height // 2
        x2 = node.x + node.width // 2
        y2 = node.y + node.height // 2
        
        # Highlight selected node
        outline_color = "#FF0000" if self.selected_node == node.id else "#000000"
        outline_width = 3 if self.selected_node == node.id else 1
        
        self.canvas.create_rectangle(x1, y1, x2, y2, 
                                   fill=node.color, 
                                   outline=outline_color,
                                   width=outline_width,
                                   tags=f"node_{node.id}")
        
        # Draw text
        self.canvas.create_text(node.x, node.y, 
                              text=node.text, 
                              font=("Arial", 10, "bold"),
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
                    
                    # Draw arrow with Win95 style
                    self.canvas.create_line(start_point[0], start_point[1],
                                          end_point[0], end_point[1],
                                          width=2, fill="black",
                                          arrow=tk.LAST, arrowshape=(8, 10, 3),
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
                    self.status_var.set(f"Select second node to connect to {self.nodes[clicked_node].text}")
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
            self.draw_connections()  # Redraw to show selection
        else:
            self.selected_node = None
            self.draw_connections()  # Redraw to remove selection
            
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
        context_menu = tk.Menu(self.root_MIND, tearoff=0, font=("MS Sans Serif", 8),
                              bg=self.colors['bg'], fg=self.colors['text'],
                              activebackground=self.colors['active_title'],
                              activeforeground="white")
        context_menu.add_command(label="Edit Text", command=lambda: self.edit_node(node_id))
        context_menu.add_command(label="Change Color", command=lambda: self.change_color(node_id))
        context_menu.add_command(label="Delete", command=lambda: self.delete_node(node_id))
        context_menu.add_separator()
        context_menu.add_command(label="Disconnect All", command=lambda: self.disconnect_all(node_id))
        
        try:
            context_menu.tk_popup(event.x_root_MIND, event.y_root_MIND)
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
            self.status_var.set("Connection mode: Click first node, then second node")
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
            self.status_var.set(f"Connected {node1.text} to {node2.text}")
            
    def edit_selected_node(self):
        if self.selected_node:
            self.edit_node(self.selected_node)
            
    def edit_node(self, node_id):
        if node_id not in self.nodes:
            return
            
        node = self.nodes[node_id]
        
        dialog, content_frame = self.create_win95_dialog("Edit Node", 320, 180)
        
        # Label
        label = tk.Label(content_frame, text="Node Text:", font=("MS Sans Serif", 8),
                        bg=self.colors['bg'], fg=self.colors['text'])
        label.pack(pady=(15, 5))
        
        # Entry with Win95 style
        entry_frame = tk.Frame(content_frame, relief="sunken", bd=2, bg="white")
        entry_frame.pack(pady=5, padx=20, fill=tk.X)
        
        text_entry = tk.Entry(entry_frame, font=("MS Sans Serif", 8), bg="white",
                             fg="black", relief="flat", bd=0)
        text_entry.insert(0, node.text)
        text_entry.pack(padx=2, pady=2, fill=tk.X)
        text_entry.focus()
        text_entry.select_range(0, tk.END)
        
        # Button frame
        button_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        button_frame.pack(pady=15)
        
        def save_changes():
            new_text = text_entry.get().strip()
            if new_text:
                node.text = new_text
                self.draw_connections()
                dialog.destroy()
                
        def cancel():
            dialog.destroy()
                
        Win95Button(button_frame, "OK", save_changes, width=8).pack(side=tk.LEFT, padx=5)
        Win95Button(button_frame, "Cancel", cancel, width=8).pack(side=tk.LEFT, padx=5)
        
        text_entry.bind("<Return>", lambda e: save_changes())
        
    def change_node_color(self):
        if self.selected_node:
            self.change_color(self.selected_node)
            
    def change_color(self, node_id):
        if node_id not in self.nodes:
            return
            
        color = colorchooser.askcolor(title="Choose node color")
        if color[1]:  # If user didn't cancel
            self.nodes[node_id].color = color[1]
            self.draw_connections()
            
    def delete_selected_node(self):
        if self.selected_node:
            self.delete_node(self.selected_node)
            
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
        self.canvas.delete(f"node_{node_id}")
        self.draw_connections()
        
    def disconnect_all(self, node_id):
        if node_id not in self.nodes:
            return
            
        node = self.nodes[node_id]
        # Remove this node from other nodes' connection lists
        for connected_id in node.connections:
            if connected_id in self.nodes:
                other_node = self.nodes[connected_id]
                if node_id in other_node.connections:
                    other_node.connections.remove(node_id)
        
        # Clear this node's connections
        node.connections.clear()
        self.draw_connections()
        
    def clear_all(self):
        result = messagebox.askyesno("Clear All", "Are you sure you want to clear all nodes?",
                                   icon="warning")
        if result:
            self.nodes.clear()
            self.selected_node = None
            self.canvas.delete("all")
            self.status_var.set("All nodes cleared")
            
    def auto_layout(self):
        if not self.nodes:
            return
            
        # Simple circular layout
        center_x = 400
        center_y = 300
        radius = 200
        
        nodes_list = list(self.nodes.values())
        angle_step = 2 * math.pi / len(nodes_list)
        
        for i, node in enumerate(nodes_list):
            angle = i * angle_step
            node.x = center_x + radius * math.cos(angle)
            node.y = center_y + radius * math.sin(angle)
            
        self.draw_connections()
        self.status_var.set("Auto layout applied")
        
    def save_mindmap(self):
        if not self.nodes:
            messagebox.showwarning("Save", "No nodes to save!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Mind Map"
        )
        
        if filename:
            try:
                data = {
                    'nodes': {
                        node_id: {
                            'x': node.x,
                            'y': node.y,
                            'text': node.text,
                            'color': node.color,
                            'connections': node.connections
                        }
                        for node_id, node in self.nodes.items()
                    },
                    'display_3d': self.display_3d
                }
                
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                
                self.status_var.set(f"Mind map saved to {filename}")
                messagebox.showinfo("Save", "Mind map saved successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
                
    def load_mindmap(self):
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Mind Map"
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                # Clear existing nodes
                self.nodes.clear()
                self.canvas.delete("all")
                
                # Load nodes
                for node_id, node_data in data['nodes'].items():
                    node = Node(
                        node_data['x'],
                        node_data['y'],
                        node_data['text'],
                        node_data['color']
                    )
                    node.id = node_id
                    node.connections = node_data.get('connections', [])
                    self.nodes[node_id] = node
                
                # Load display mode if available
                if 'display_3d' in data:
                    self.display_3d = data['display_3d']
                    if self.display_3d:
                        self.display_button.label.configure(text="3D View")
                    else:
                        self.display_button.label.configure(text="2D View")
                
                # Update node counter
                self.node_counter = len(self.nodes)
                
                self.draw_connections()
                self.status_var.set(f"Mind map loaded from {filename}")
                messagebox.showinfo("Load", "Mind map loaded successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")

def main():
    root_MIND = tk.Tk()
    app = MindMapTool(root_MIND)
    
    # Set window icon (optional)
    try:
        # You can add an icon file here if you have one
        # root_MIND.iconbitmap("mindmap.ico")
        pass
    except:
        pass
    
    # Center the window
    root_MIND.update_idletasks()
    width = root_MIND.winfo_width()
    height = root_MIND.winfo_height()
    x = (root_MIND.winfo_screenwidth() // 2) - (width // 2)
    y = (root_MIND.winfo_screenheight() // 2) - (height // 2)
    root_MIND.geometry(f"{width}x{height}+{x}+{y}")
    
    root_MIND.mainloop()

if __name__ == "__main__":
    main()