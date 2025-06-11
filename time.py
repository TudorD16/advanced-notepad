import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, filedialog
import json
import math
import random

class Node:
    def __init__(self, x, y, text="New Node", color="#87CEEB"):
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

class MindMapTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Mind Mapping Tool")
        self.root.geometry("1200x800")
        
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
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Toolbar
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="Add Node", command=self.add_node_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Delete Node", command=self.delete_selected_node).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Connect Nodes", command=self.toggle_connect_mode).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Edit Node", command=self.edit_selected_node).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Change Color", command=self.change_node_color).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        ttk.Button(toolbar, text="Save", command=self.save_mindmap).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Load", command=self.load_mindmap).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        ttk.Button(toolbar, text="Auto Layout", command=self.auto_layout).pack(side=tk.LEFT, padx=2)
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Double-click to add node, click to select, drag to move")
        self.status_label = ttk.Label(toolbar, textvariable=self.status_var)
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        # Canvas with scrollbars
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg="white", scrollregion=(0, 0, 2000, 2000))
        
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
    def setup_bindings(self):
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.on_right_click)  # Right-click menu
        
    def add_node_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Node")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Node Text:").pack(pady=5)
        text_entry = ttk.Entry(dialog, width=30)
        text_entry.pack(pady=5)
        text_entry.focus()
        
        def create_node():
            text = text_entry.get().strip()
            if text:
                x = random.randint(100, 500)
                y = random.randint(100, 400)
                self.create_node(x, y, text)
                dialog.destroy()
        
        ttk.Button(dialog, text="Create", command=create_node).pack(pady=10)
        
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
        
    def draw_node(self, node):
        # Clear previous drawings for this node
        self.canvas.delete(f"node_{node.id}")
        
        # Draw node rectangle
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
                    
                    # Draw arrow
                    self.canvas.create_line(start_point[0], start_point[1],
                                          end_point[0], end_point[1],
                                          width=2, fill="#666666",
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
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Edit Text", command=lambda: self.edit_node(node_id))
        context_menu.add_command(label="Change Color", command=lambda: self.change_color(node_id))
        context_menu.add_command(label="Delete", command=lambda: self.delete_node(node_id))
        context_menu.add_separator()
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
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Node")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Node Text:").pack(pady=5)
        text_entry = ttk.Entry(dialog, width=30)
        text_entry.insert(0, node.text)
        text_entry.pack(pady=5)
        text_entry.focus()
        text_entry.select_range(0, tk.END)
        
        def save_changes():
            new_text = text_entry.get().strip()
            if new_text:
                node.text = new_text
                self.draw_connections()
                dialog.destroy()
                
        ttk.Button(dialog, text="Save", command=save_changes).pack(pady=10)
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
        
    def auto_layout(self):
        if not self.nodes:
            return
            
        # Simple circular layout
        center_x, center_y = 400, 300
        radius = 200
        
        node_list = list(self.nodes.values())
        angle_step = 2 * math.pi / len(node_list)
        
        for i, node in enumerate(node_list):
            angle = i * angle_step
            node.x = center_x + radius * math.cos(angle)
            node.y = center_y + radius * math.sin(angle)
            
        self.draw_connections()
        
    def save_mindmap(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            data = {
                "nodes": {
                    node_id: {
                        "x": node.x,
                        "y": node.y,
                        "text": node.text,
                        "color": node.color,
                        "connections": node.connections
                    }
                    for node_id, node in self.nodes.items()
                }
            }
            
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                self.status_var.set(f"Saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")
                
    def load_mindmap(self):
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Clear current mindmap
                self.clear_all()
                
                # Load nodes
                for node_id, node_data in data["nodes"].items():
                    node = Node(
                        node_data["x"],
                        node_data["y"],
                        node_data["text"],
                        node_data["color"]
                    )
                    node.id = node_id
                    node.connections = node_data["connections"]
                    self.nodes[node_id] = node
                    
                # Update counter
                if self.nodes:
                    max_num = max([int(nid.split('_')[1]) for nid in self.nodes.keys()])
                    self.node_counter = max_num + 1
                    
                self.draw_connections()
                self.status_var.set(f"Loaded from {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load: {str(e)}")
                
    def clear_all(self):
        result = messagebox.askyesno("Confirm", "Are you sure you want to clear all nodes?")
        if result:
            self.nodes.clear()
            self.selected_node = None
            self.canvas.delete("all")
            self.node_counter = 0
            self.status_var.set("Cleared all nodes")

if __name__ == "__main__":
    root = tk.Tk()
    app = MindMapTool(root)
    root.mainloop()