import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from collections import deque
import threading
import time

from bfs import BFS
from dfs import DFS
from dijkstra import CUS1
from gbfs import GBFS
from astar import AS
from idastar import CUS2


class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Search Algorithm Visualizer - Step by Step")
        self.root.geometry("1600x900")
        
        self.graph = None
        self.search_tree = []
        self.solution_path = None
        self.is_running = False
        self.is_paused = False
        self.node_counter = 0
        self.node_ids = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        # Top control panel
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        
        # File selection
        ttk.Label(control_frame, text="File:").grid(row=0, column=0, padx=5)
        self.file_entry = ttk.Entry(control_frame, width=40)
        self.file_entry.grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=5)
        
        # Algorithm selection
        ttk.Label(control_frame, text="Algorithm:").grid(row=0, column=3, padx=5)
        self.algorithm_var = tk.StringVar(value="bfs")
        algorithms = ["bfs", "dfs", "dijkstra", "gbfs", "astar", "idastar"]
        algo_menu = ttk.Combobox(control_frame, textvariable=self.algorithm_var, 
                                 values=algorithms, state="readonly", width=15)
        algo_menu.grid(row=0, column=4, padx=5)
        
        # Speed control
        ttk.Label(control_frame, text="Speed (s):").grid(row=0, column=5, padx=5)
        self.speed_var = tk.DoubleVar(value=0.5)
        speed_scale = ttk.Scale(control_frame, from_=0.1, to=2.0, variable=self.speed_var, 
                               orient=tk.HORIZONTAL, length=100)
        speed_scale.grid(row=0, column=6, padx=5)
        self.speed_label = ttk.Label(control_frame, text="0.5")
        self.speed_label.grid(row=0, column=7, padx=5)
        self.speed_var.trace_add('write', lambda *args: self.speed_label.config(text=f"{self.speed_var.get():.2f}"))
        
        # Control buttons
        self.run_button = ttk.Button(control_frame, text="▶ Run", command=self.run_search)
        self.run_button.grid(row=0, column=8, padx=5)
        
        self.pause_button = ttk.Button(control_frame, text="⏸ Pause", command=self.toggle_pause, state=tk.DISABLED)
        self.pause_button.grid(row=0, column=9, padx=5)
        
        self.reset_button = ttk.Button(control_frame, text="↺ Reset", command=self.reset_visualization, state=tk.DISABLED)
        self.reset_button.grid(row=0, column=10, padx=5)
        
        # Main content area
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - Graph visualization
        left_frame = ttk.LabelFrame(content_frame, text="Graph Visualization", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.graph_canvas = tk.Canvas(left_frame, bg="white", width=600, height=600)
        self.graph_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Right side - Search tree and info
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Search tree
        tree_frame = ttk.LabelFrame(right_frame, text="Search Tree", padding="10")
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Add scrollbars
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        self.tree_canvas = tk.Canvas(tree_frame, bg="white", 
                                     yscrollcommand=tree_scroll_y.set,
                                     xscrollcommand=tree_scroll_x.set)
        tree_scroll_y.config(command=self.tree_canvas.yview)
        tree_scroll_x.config(command=self.tree_canvas.xview)
        
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Status panel
        status_frame = ttk.LabelFrame(right_frame, text="Status", padding="10")
        status_frame.pack(fill=tk.X, pady=(5, 5))
        
        self.status_text = tk.Text(status_frame, height=6, width=50, wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Results panel
        results_frame = ttk.LabelFrame(right_frame, text="Results", padding="10")
        results_frame.pack(fill=tk.X)
        
        self.results_text = tk.Text(results_frame, height=8, width=50, wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True)
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select graph file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)
            self.load_graph(filename)
    
    def load_graph(self, filename):
        try:
            self.graph = self.open_file(filename)
            self.draw_graph()
            messagebox.showinfo("Success", "Graph loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load graph: {str(e)}")
    
    def open_file(self, fname):
        graph = {
            'nodes': {},
            'adjacency_list': {},
            'origin': None,
            'destinations': []
        }
        
        with open(fname, 'r') as file:
            lines = file.readlines()
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line == "Nodes:":
                current_section = "nodes"
                continue
            elif line == "Edges:":
                current_section = "edges"
                continue
            elif line == "Origin:":
                current_section = "origin"
                continue
            elif line == "Destinations:":
                current_section = "destinations"
                continue
            
            if current_section == "nodes":
                parts = line.split(': ')
                node_id = int(parts[0])
                coords = parts[1].strip('()').split(',')
                x, y = int(coords[0]), int(coords[1])
                graph['nodes'][node_id] = (x, y)
                graph['adjacency_list'][node_id] = []
            
            elif current_section == "edges":
                parts = line.split(': ')
                edge = parts[0].strip('()').split(',')
                from_node = int(edge[0])
                to_node = int(edge[1])
                cost = int(parts[1])
                
                if from_node not in graph['adjacency_list']:
                    graph['adjacency_list'][from_node] = []
                graph['adjacency_list'][from_node].append((to_node, cost))
            
            elif current_section == "origin":
                graph['origin'] = int(line)
            
            elif current_section == "destinations":
                dest_list = line.split(';')
                graph['destinations'] = [int(d.strip()) for d in dest_list]
        
        for node in graph['adjacency_list']:
            graph['adjacency_list'][node].sort(key=lambda x: x[0])
        
        return graph
    
    def draw_graph(self, highlight_current=None, highlight_frontier=None, highlight_path=None, highlighted_visited=None):
        if not self.graph:
            return
        
        self.graph_canvas.delete("all")
        
        nodes = self.graph['nodes']
        if not nodes:
            return
        
        xs = [coord[0] for coord in nodes.values()]
        ys = [coord[1] for coord in nodes.values()]
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        padding = 60
        canvas_width = self.graph_canvas.winfo_width() or 600
        canvas_height = self.graph_canvas.winfo_height() or 600
        
        scale_x = (canvas_width - 2 * padding) / (max_x - min_x) if max_x != min_x else 1
        scale_y = (canvas_height - 2 * padding) / (max_y - min_y) if max_y != min_y else 1
        scale = min(scale_x, scale_y)
        
        def transform(x, y):
            tx = padding + (x - min_x) * scale
            ty = canvas_height - (padding + (y - min_y) * scale)
            return tx, ty
        
        # Draw solution path edges first (if available)
        if highlight_path:
            for i in range(len(highlight_path) - 1):
                from_node = highlight_path[i]
                to_node = highlight_path[i + 1]
                x1, y1 = transform(*nodes[from_node])
                x2, y2 = transform(*nodes[to_node])
                self.graph_canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST,
                                             fill="yellow", width=4)
  
        
        # Draw edges
        for from_node, neighbors in self.graph['adjacency_list'].items():
            x1, y1 = transform(*nodes[from_node])
            for to_node, cost in neighbors:
                x2, y2 = transform(*nodes[to_node])
                self.graph_canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, 
                                              fill="gray", width=2)
                mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                self.graph_canvas.create_text(mid_x, mid_y, text=str(cost), 
                                             fill="blue", font=("Arial", 9, "bold"))
        
        # Draw nodes
        for node_id, (x, y) in nodes.items():
            tx, ty = transform(x, y)
            
            # Determine color
            if highlight_current and node_id == highlight_current:
                color = "orange"
                outline_width = 4
            elif highlight_path and node_id in highlight_path:
                color = "yellow"
                outline_width = 3
            elif highlight_frontier and node_id in highlight_frontier:
                color = "lightyellow"
                outline_width = 3
            elif highlighted_visited and node_id in highlighted_visited:
                color = "lightblue"
                outline_width = 2
            elif node_id == self.graph['origin']:
                color = "green"
                outline_width = 2
            elif node_id in self.graph['destinations']:
                color = "red"
                outline_width = 2
            else:
                color = "white"
                outline_width = 2
            
            r = 22
            self.graph_canvas.create_oval(tx - r, ty - r, tx + r, ty + r, 
                                         fill=color, outline="black", width=outline_width)
            self.graph_canvas.create_text(tx, ty, text=str(node_id), 
                                         font=("Arial", 12, "bold"))
        
        # Draw legend
        legend_x, legend_y = 10, 10
        self.graph_canvas.create_rectangle(legend_x, legend_y, legend_x + 180, legend_y + 120, 
                                          fill="white", outline="black", width=2)
        
        items = [
            ("green", "Origin"),
            ("red", "Destination"),
            ("lightblue", "Visited"),
            ("orange", "Current"),
            ("lightyellow", "Frontier")
        ]
        
        for i, (color, label) in enumerate(items):
            y_offset = legend_y + 10 + i * 22
            self.graph_canvas.create_oval(legend_x + 10, y_offset, legend_x + 28, y_offset + 18, 
                                          fill=color, outline="black")
            self.graph_canvas.create_text(legend_x + 95, y_offset + 9, text=label, anchor=tk.W,
                                         font=("Arial", 9))
    
    def run_search(self):
        if not self.graph:
            messagebox.showwarning("Warning", "Please load a graph file first!")
            return
        
        if self.is_running:
            return
        
        self.is_running = True
        self.is_paused = False
        self.run_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)
        
        # Reset tree tracking
        self.search_tree = []
        self.node_counter = 0
        self.node_ids = {}
        
        # Run search in separate thread
        thread = threading.Thread(target=self.execute_search)
        thread.daemon = True
        thread.start()
    
    def execute_search(self):
        algorithm = self.algorithm_var.get()
        
        algorithm_map = {
            'bfs': BFS,
            'dfs': DFS,
            'dijkstra': CUS1,
            'gbfs': GBFS,
            'astar': AS,
            'idastar': CUS2
        }
        
        try:
            if algorithm in algorithm_map:
                searcher = algorithm_map[algorithm](self.graph)
                
                # Run with callback
                number_of_nodes, path, goal = searcher.search(step_callback=self.step_callback)
                
                self.solution_path = path
                
                # Display final results
                self.root.after(0, self.display_results, algorithm, number_of_nodes, path, goal)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.root.after(0, messagebox.showerror, "Error", f"Search failed: {str(e)}")
        finally:
            self.is_running = False
            self.root.after(0, self.run_button.config, {"state": tk.NORMAL})
            self.root.after(0, self.pause_button.config, {"state": tk.DISABLED})
    
    def step_callback(self, current_node, path, frontier, visited, is_goal):
        """Called by search algorithm at each step"""
        # Wait if paused
        while self.is_paused and self.is_running:
            time.sleep(0.1)
        
        if not self.is_running:
            return
        
        # For IDAstar reset step
        if current_node is None and not path:
            # reset internal tree state
            self.search_tree = []
            self.node_counter = 0
            self.node_ids = {}

            # prepare empty step data to update GUI (clears tree_canvas and redraws graph)
            step_data = {
                'current_node': None,
                'path': [],
                'frontier': frontier or [],
                'visited': visited or set(),
                'is_goal': False,
                'tree_data': []
            }
            # update GUI on main thread
            self.root.after(0, self.update_visualization_step, step_data)
            return
        
        # Build tree structure
        self.build_tree_from_path(path, current_node, is_goal)
        

   
        # Create step data
        step_data = {
            'current_node': current_node,
            'path': path,
            'frontier': frontier,
            'visited': visited,
            'is_goal': is_goal,
            'tree_data': [node.copy() for node in self.search_tree]
        }

        
        # Update GUI in main thread
        self.root.after(0, self.update_visualization_step, step_data)
        
        # Delay for visualization
        time.sleep(self.speed_var.get())
    
    # ...existing code...

    def build_tree_from_path(self, path, current_node, is_goal):
        """Build/update search tree from current path"""
        
        # First, update all previous 'current' nodes to 'visited' (after expansion)
        if not is_goal:
            for tree_node in self.search_tree:
                if tree_node['state'] == 'current':
                    tree_node['state'] = 'visited'
        
        # Add nodes in path if not already added
        for i, node in enumerate(path):
            node_key = (node, i)
            
            if node_key not in self.node_ids:
                node_id = self.node_counter
                self.node_counter += 1
                self.node_ids[node_key] = node_id
                
                parent_id = None
                if i > 0:
                    parent_key = (path[i-1], i-1)
                    parent_id = self.node_ids.get(parent_key)
                
                # Determine initial state
                if is_goal and node == current_node:
                    state = 'solution'
                elif node == current_node:
                    state = 'current'  # Currently being expanded
                elif i < len(path) - 1:  # Nodes before current in path
                    state = 'visited'
                else:
                    state = 'frontier'
                
                self.search_tree.append({
                    'id': node_id,
                    'node': node,
                    'parent': parent_id,
                    'cost': i,
                    'state': state
                })
            else:
                # Update state of existing node
                node_id = self.node_ids[node_key]
                for tree_node in self.search_tree:
                    if tree_node['id'] == node_id:
                        if is_goal and node in path:
                            tree_node['state'] = 'solution'
                        elif node == current_node:
                            tree_node['state'] = 'current'  # Currently being expanded
                        # If this node was previously 'current', it will be changed to 'visited' at the start
                        break
        
        # Mark all nodes in solution path when goal is found
        if is_goal:
            for node_data in self.search_tree:
                if node_data['node'] in path:
                    node_data['state'] = 'solution'

# ...existing code...
    
    def update_visualization_step(self, step_data):
        """Update GUI with current step"""
        # Update graph
        highlight_path = step_data['path'] if step_data['is_goal'] else None
        self.draw_graph(
            highlight_current=step_data['current_node'],
            highlight_frontier=step_data['frontier'],
            highlight_path=highlight_path,
            highlighted_visited=step_data['visited']
        )
        
        # Update search tree
        self.search_tree = step_data['tree_data']
        self.draw_search_tree()
        
        # Update status
        self.update_status(step_data)
    
    def update_status(self, step_data):
        self.status_text.delete(1.0, tk.END)
        
        status = f"Current Node: {step_data['current_node']}\n"
        status += f"Current Path: {' → '.join(map(str, step_data['path']))}\n"
        status += f"Visited Nodes: {len(step_data['visited'])}\n"
        status += f"Frontier Size: {len(step_data['frontier'])}\n"
        status += f"Frontier: {step_data['frontier'][:10]}"
        if len(step_data['frontier']) > 10:
            status += f"... (+{len(step_data['frontier']) - 10} more)"
        status += f"\nTree Nodes: {len(step_data['tree_data'])}\n"
        
        self.status_text.insert(1.0, status)
    
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_button.config(text="▶ Resume")
        else:
            self.pause_button.config(text="⏸ Pause")
    
    def reset_visualization(self):
        self.is_running = False
        self.is_paused = False
        self.search_tree = []
        self.solution_path = None
        self.node_counter = 0
        self.node_ids = {}
        
        self.tree_canvas.delete("all")
        self.status_text.delete(1.0, tk.END)
        self.results_text.delete(1.0, tk.END)
        
        if self.graph:
            self.draw_graph()
        
        self.run_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED, text="⏸ Pause")
        self.reset_button.config(state=tk.DISABLED)
    
    def display_results(self, algorithm, num_nodes, path, goal):
        self.results_text.delete(1.0, tk.END)
        
        result_text = f"Algorithm: {algorithm.upper()}\n"
        result_text += f"Goal Reached: {goal}\n"
        result_text += f"Nodes Created: {num_nodes}\n"
        result_text += f"Path: {' → '.join(map(str, path)) if path else 'Not found'}\n"
        
        if path:
            cost = 0
            for i in range(len(path) - 1):
                from_node = path[i]
                to_node = path[i + 1]
                for neighbor, edge_cost in self.graph['adjacency_list'].get(from_node, []):
                    if neighbor == to_node:
                        cost += edge_cost
                        break
            result_text += f"Path Cost: {cost}\n"
            result_text += f"Path Length: {len(path)} nodes\n"
        
        self.results_text.insert(1.0, result_text)
    
    def draw_search_tree(self):
        if not self.search_tree:
            return
        
        self.tree_canvas.delete("all")
        
        levels = self.organize_tree_by_levels()
        
        if not levels:
            return
        
        level_height = 70
        node_spacing = 55
        start_y = 30
        
        max_width = max(len(level) for level in levels) * node_spacing
        canvas_width = max(800, max_width + 100)
        canvas_height = len(levels) * level_height + 100
        
        self.tree_canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))
        
        node_positions = {}
        
        # Draw tree level by level
        for level_idx, level_nodes in enumerate(levels):
            y = start_y + level_idx * level_height
            num_nodes = len(level_nodes)
            total_width = num_nodes * node_spacing
            start_x = (canvas_width - total_width) / 2
            
            for idx, node_data in enumerate(level_nodes):
                x = start_x + idx * node_spacing
                node_positions[node_data['id']] = (x, y)
                
                # Draw edge to parent
                if node_data['parent'] is not None and node_data['parent'] in node_positions:
                    px, py = node_positions[node_data['parent']]
                    edge_color = "yellow" if node_data['state'] == 'solution' else "gray"
                    edge_width = 3 if node_data['state'] == 'solution' else 2
                    self.tree_canvas.create_line(px, py, x, y, fill=edge_color, width=edge_width)
                
                # Determine node color based on state
                state = node_data.get('state', 'frontier')
                if state == 'solution':
                    color = "yellow"
                elif state == 'visited':
                    color = "lightblue"
                elif state == 'frontier':
                    color = "lightyellow"
                elif state == 'current':
                    color = "orange"
                elif node_data['node'] == self.graph['origin']:
                    color = "green"
                elif node_data['node'] in self.graph['destinations']:
                    color = "red"
                else:
                    color = "white"
                
                # Draw node
                r = 16
                self.tree_canvas.create_oval(x - r, y - r, x + r, y + r, 
                                            fill=color, outline="black", width=2)
                self.tree_canvas.create_text(x, y, text=str(node_data['node']), 
                                            font=("Arial", 9, "bold"))
                
                # Draw depth
                if node_data.get('cost') is not None:
                    self.tree_canvas.create_text(x, y + r + 12, 
                                                text=f"d={node_data['cost']}", 
                                                font=("Arial", 7), fill="blue")
    
    def organize_tree_by_levels(self):
        if not self.search_tree:
            return []
        
        levels = []
        visited = set()
        queue = deque()
        
        # Find root
        root = None
        for node in self.search_tree:
            if node['parent'] is None:
                root = node
                break
        
        if not root:
            return []
        
        queue.append((root, 0))
        visited.add(root['id'])
        
        while queue:
            node, level = queue.popleft()
            
            if level >= len(levels):
                levels.append([])
            
            levels[level].append(node)
            
            # Find children
            for child in self.search_tree:
                if child['parent'] == node['id'] and child['id'] not in visited:
                    queue.append((child, level + 1))
                    visited.add(child['id'])
        
        return levels


